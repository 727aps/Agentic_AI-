import streamlit as st
import requests
from typing import TypedDict

# ----- Data structure -----
class ReviewState(TypedDict):
    pr_diff: str
    review: str

# ----- Function to fetch PR diff -----
def fetch_pr_diff(repo: str, pr_number: int, token: str) -> str:
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3.diff"
    }
    url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.text
    else:
        st.error(f"GitHub error: {response.status_code} - {response.text}")
        return ""

# ----- Function to call Ollama -----
def review_with_ollama(diff_text: str) -> str:
    payload = {
        "model": "tinyllama",
        "prompt": f"You're a code reviewer. Please review the following code diff and provide suggestions:\n\n{diff_text}",
        "stream": False
    }
    response = requests.post("http://localhost:11434/api/generate", json=payload)

    if response.status_code == 200:
        return response.json()["response"]
    else:
        return f"❌ Error from Ollama: {response.text}"

# ----- Streamlit UI -----
st.title("🧠 CODE REVIEWS WITH PR AGENT")

with st.form("review_form"):
    github_token = st.text_input("🔐 GitHub Token", type="password")
    repo = st.text_input("📘 Repository (owner/repo)", value="mega6105raj/nmap")
    pr_number = st.number_input("🔢 Pull Request Number", min_value=1, value=1)
    submitted = st.form_submit_button("Review PR")

if submitted:
    with st.spinner("Fetching pull request diff..."):
        diff_text = fetch_pr_diff(repo, pr_number, github_token)

    if diff_text:
        st.success("✅ Diff fetched successfully!")

        with st.spinner("Sending diff to TinyLLM via Ollama..."):
            review = review_with_ollama(diff_text)

        st.markdown("### 📄 PR Diff")
        st.code(diff_text, language="diff")

        st.markdown("### 🧠 AI Review")
        st.success(review)
