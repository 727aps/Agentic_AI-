import requests
import json
from langgraph.graph import StateGraph, END
from typing import TypedDict

# ------------------- GITHUB PR FETCH -------------------

# Replace with your own API key: os.getenv('GITHUB_TOKEN')
GITHUB_TOKEN = "add_your_api_key"
REPO = "mega6105raj/nmap"
PR_NUMBER = 1

headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3.diff"
}

url = f"https://api.github.com/repos/{REPO}/pulls/{PR_NUMBER}"
response = requests.get(url, headers=headers)

with open("diff.patch", "w") as f:
    f.write(response.text)

print("✅ PR diff saved to diff.patch")

# ------------------- LANGGRAPH FLOW -------------------

class ReviewState(TypedDict):
    pr_diff: str
    review: str


def load_code_diff(state: ReviewState) -> ReviewState:
    with open("diff.patch", "r") as f:
        diff = f.read()
    return {"pr_diff": diff, "review": ""}


def review_diff(state: ReviewState) -> ReviewState:
    print("🔄 Sending diff to local Ollama model...")
    payload = {
        "model": "tinyllama",
        "prompt": f"You're a code reviewer. Please review the following code diff and provide suggestions:\n\n{state['pr_diff']}",
        "stream": False
    }

    response = requests.post("http://localhost:11434/api/generate", json=payload)

    if response.status_code == 200:
        result = response.json()["response"]
    else:
        result = f"❌ Error from Ollama: {response.text}"

    return {"pr_diff": state["pr_diff"], "review": result}


def display_review(state: ReviewState) -> ReviewState:
    print("\n🧠 AI Code Review:\n")
    print(state["review"])
    return state


builder = StateGraph(ReviewState)
builder.add_node("load_diff", load_code_diff)
builder.add_node("review_node", review_diff)
builder.add_node("display", display_review)

builder.set_entry_point("load_diff")
builder.add_edge("load_diff", "review_node")
builder.add_edge("review_node", "display")
builder.add_edge("display", END)

graph = builder.compile()
graph.invoke({})
