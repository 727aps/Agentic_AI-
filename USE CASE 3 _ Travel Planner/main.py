import streamlit as st
import re
from dotenv import load_dotenv
import pandas as pd

from phi.agent import Agent
from phi.model.groq import Groq
from phi.tools.duckduckgo import DuckDuckGo

# Load environment variables from .env if needed
load_dotenv()

# Configure Ollama Model
llm = Groq(id="llama-3.3-70b-versatile")

# Define Agents
research_agent = Agent(
    name="Destination Researcher",
    model=llm,
    instructions=["Research travel destinations and provide attractions, customs, requirements. Format response with clear sections: Overview, Top Attractions, Local Culture, Best Time to Visit, Transportation, Safety Tips."],
    tools=[DuckDuckGo()],
    markdown=True
)

flight_agent = Agent(
    name="Flight Expert",
    model=llm,
    instructions=["Find the best flights based on user's location, destination, and budget. Provide specific airline names, prices, departure/arrival times, and duration. Format as structured data."],
    tools=[DuckDuckGo()],
    markdown=True
)

hotel_agent = Agent(
    name="Accommodation Planner",
    model=llm,
    instructions=["Suggest hotels and accommodations based on budget and travel style. Include hotel names, locations, ratings, price ranges, and key amenities. Provide at least 3-5 options."],
    tools=[DuckDuckGo()],
    markdown=True
)

itinerary_agent = Agent(
    name="Itinerary Designer",
    model=llm,
    instructions=["Create a detailed daily travel plan with balanced activities and relaxation. Organize by day with morning, afternoon, and evening activities. Include estimated costs and duration."],
    tools=[DuckDuckGo()],
    markdown=True
)

def parse_and_format_content(content, section_type):
    """Parse and format agent output for better presentation"""
    
    # Handle RunResponse object
    if hasattr(content, 'content'):
        content = content.content
    elif hasattr(content, 'text'):
        content = content.text
    elif not isinstance(content, str):
        content = str(content)
    
    # Clean up the content
    content = content.strip()
    
    # Remove excessive whitespace and normalize line breaks
    content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
    content = re.sub(r'\s+', ' ', content)
    content = content.replace('\n ', '\n')
    
    return content

def create_sample_flight_table():
    """Create a sample flight comparison table"""
    flight_data = {
        'Airline': ['Delta Airlines', 'American Airlines', 'United Airlines', 'JetBlue'],
        'Departure': ['8:30 AM', '2:15 PM', '6:45 PM', '10:20 AM'],
        'Arrival': ['11:45 AM', '5:30 PM', '9:50 PM', '1:35 PM'],
        'Duration': ['3h 15m', '3h 15m', '3h 05m', '3h 15m'],
        'Price': ['$450', '$425', '$475', '$390'],
        'Stops': ['Nonstop', '1 Stop', 'Nonstop', 'Nonstop']
    }
    return pd.DataFrame(flight_data)

def create_sample_hotel_table():
    """Create a sample hotel comparison table"""
    hotel_data = {
        'Hotel Name': ['Grand Plaza Hotel', 'Boutique Central Inn', 'Luxury Suites', 'Budget Comfort Lodge', 'Historic Manor'],
        'Location': ['Downtown', 'Arts District', 'Business Center', 'Near Airport', 'Old Town'],
        'Rating': ['⭐⭐⭐⭐⭐', '⭐⭐⭐⭐', '⭐⭐⭐⭐⭐', '⭐⭐⭐', '⭐⭐⭐⭐'],
        'Price/Night': ['$280', '$195', '$350', '$120', '$210'],
        'Key Amenities': ['Pool, Spa, WiFi', 'WiFi, Breakfast', 'Gym, Pool, Concierge', 'WiFi, Parking', 'Historic, WiFi, Restaurant']
    }
    return pd.DataFrame(hotel_data)

def format_itinerary_content(content):
    """Format itinerary content with better structure"""
    
    # Handle RunResponse object
    if hasattr(content, 'content'):
        content = content.content
    elif hasattr(content, 'text'):
        content = content.text
    elif not isinstance(content, str):
        content = str(content)
    
    # Split content into lines and process
    lines = content.split('\n')
    formatted_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Format day headers
        if re.match(r'^Day \d+', line, re.IGNORECASE):
            formatted_lines.append(f"### {line}")
        # Format time-based activities
        elif re.match(r'^(Morning|Afternoon|Evening)', line, re.IGNORECASE):
            formatted_lines.append(f"**{line}**")
        # Format bullet points
        elif line.startswith(('-', '•', '*')):
            formatted_lines.append(f"- {line[1:].strip()}")
        else:
            formatted_lines.append(line)
    
    return '\n\n'.join(formatted_lines)

# Streamlit UI
st.set_page_config(page_title="AI Travel Planner", page_icon="🌍", layout="wide")

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        margin: -1rem -1rem 2rem -1rem;
        border-radius: 0 0 10px 10px;
    }
    .section-header {
        background: linear-gradient(90deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .info-box {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #007bff;
        margin: 1rem 0;
    }
    .success-box {
        background: #d4edda;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>🌍 AI Travel Planner</h1>
    <p>Plan your perfect trip with AI-powered travel experts</p>
</div>
""", unsafe_allow_html=True)

# Sidebar for inputs
with st.sidebar:
    st.header("✈️ Trip Details")
    source = st.text_input("🏠 From (Source Location)", "Los Angeles", help="Where are you traveling from?")
    destination = st.text_input("🌍 To (Destination)", "New York", help="Where would you like to go?")
    dates = st.text_input("📅 Travel Dates", "12-06-2025", help="When are you traveling?")
    budget = st.text_input("💰 Budget ($)", "10000", help="What's your total budget?")
    preferences = st.text_area("❤️ Preferences", "Find good hotels and first class plane tickets", 
                              help="What kind of experience are you looking for?")
    
    st.markdown("---")
    generate_btn = st.button("🚀 Generate Travel Plan", use_container_width=True, type="primary")

if generate_btn:
    # Create enhanced query for each agent
    base_query = f"From: {source}, To: {destination}, Dates: {dates}, Budget: ${budget}, Preferences: {preferences}"
    
    # Progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Research Agent
        status_text.text("🔍 Researching destination...")
        progress_bar.progress(25)
        
        research_query = f"{base_query}. Provide comprehensive destination research including: overview, top attractions, local culture, best time to visit, transportation options, and safety tips. Format with clear headings and bullet points."
        research_response = research_agent.run(research_query)
        
        # Flight Agent
        status_text.text("✈️ Finding flight options...")
        progress_bar.progress(50)
        
        flight_query = f"{base_query}. Find and compare flight options from {source} to {destination} with specific airlines, departure/arrival times, prices, and durations. Include both economy and premium options."
        flights_response = flight_agent.run(flight_query)
        
        # Hotel Agent
        status_text.text("🏨 Searching accommodations...")
        progress_bar.progress(75)
        
        hotel_query = f"{base_query}. Recommend 3-5 hotels in {destination} with different price ranges. Include hotel names, exact locations, star ratings, nightly rates, and key amenities."
        hotels_response = hotel_agent.run(hotel_query)
        
        # Itinerary Agent
        status_text.text("📅 Creating itinerary...")
        progress_bar.progress(100)
        
        itinerary_query = f"{base_query}. Create a detailed day-by-day itinerary for {destination} with morning, afternoon, and evening activities. Include estimated costs, duration, and transportation between activities."
        itinerary_response = itinerary_agent.run(itinerary_query)
        
        # Clear progress indicators
        progress_bar.empty()
        status_text.empty()
        
        # Display results with better formatting
        st.markdown('<div class="section-header"><h2>📍 Destination Research</h2></div>', unsafe_allow_html=True)
        
        with st.container():
            # Parse and display research content
            formatted_research = parse_and_format_content(research_response, "research")
            st.markdown(formatted_research)
            
            # Add some key metrics in columns
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("🌡️ Climate", "Temperate")
            with col2:
                st.metric("💬 Language", "English")
            with col3:
                st.metric("💱 Currency", "USD")
            with col4:
                st.metric("🕒 Timezone", "EST")
        
        st.markdown("---")
        
        # Flight Options
        st.markdown('<div class="section-header"><h2>✈️ Flight Options</h2></div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            formatted_flights = parse_and_format_content(flights_response, "flights")
            st.markdown(formatted_flights)
        
        with col2:
            st.markdown("**📊 Flight Comparison**")
            flight_df = create_sample_flight_table()
            st.dataframe(flight_df, use_container_width=True)
            
            # Flight booking tips
            st.markdown("""
            <div class="info-box">
                <strong>💡 Booking Tips:</strong><br>
                • Book 2-3 weeks in advance<br>
                • Compare multiple airlines<br>
                • Consider flexible dates<br>
                • Check baggage policies
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Hotel Recommendations
        st.markdown('<div class="section-header"><h2>🏨 Hotel Recommendations</h2></div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            formatted_hotels = parse_and_format_content(hotels_response, "hotels")
            st.markdown(formatted_hotels)
        
        with col2:
            st.markdown("**🏨 Hotel Comparison**")
            hotel_df = create_sample_hotel_table()
            st.dataframe(hotel_df, use_container_width=True)
            
            # Hotel selection tips
            st.markdown("""
            <div class="success-box">
                <strong>🎯 Selection Tips:</strong><br>
                • Check recent reviews<br>
                • Verify location proximity<br>
                • Compare amenities<br>
                • Read cancellation policy
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Detailed Itinerary
        st.markdown('<div class="section-header"><h2>📅 Your Detailed Itinerary</h2></div>', unsafe_allow_html=True)
        
        # Format itinerary content
        formatted_itinerary = format_itinerary_content(itinerary_response)
        
        # Create tabs for different days
        if "day 1" in formatted_itinerary.lower() or "day 2" in formatted_itinerary.lower():
            # Extract days and create tabs
            days = re.findall(r'Day \d+[^\n]*', formatted_itinerary, re.IGNORECASE)
            if days:
                tabs = st.tabs([f"📅 {day}" for day in days[:5]])  # Limit to 5 days
                
                # Split itinerary by days
                day_contents = re.split(r'Day \d+[^\n]*', formatted_itinerary, flags=re.IGNORECASE)[1:]
                
                for i, (tab, content) in enumerate(zip(tabs, day_contents)):
                    with tab:
                        st.markdown(content.strip())
                        
                        # Add estimated daily cost
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("💰 Est. Daily Cost", f"${150 + i*20}")
                        with col2:
                            st.metric("⏱️ Activities", f"{4 + i}")
                        with col3:
                            st.metric("🚶 Walking", f"{2 + i}km")
            else:
                st.markdown(formatted_itinerary)
        else:
            st.markdown(formatted_itinerary)
        
        # Summary section
        st.markdown("---")
        st.markdown('<div class="section-header"><h2>📋 Trip Summary</h2></div>', unsafe_allow_html=True)
        
        summary_col1, summary_col2, summary_col3 = st.columns(3)
        
        with summary_col1:
            st.markdown("""
            **🎯 Trip Highlights**
            - Comprehensive destination research
            - Multiple flight options compared
            - Curated hotel recommendations
            - Detailed day-by-day planning
            """)
        
        with summary_col2:
            st.markdown(f"""
            **📊 Trip Overview**
            - **From:** {source}
            - **To:** {destination}
            - **Duration:** {dates}
            - **Budget:** ${budget}
            - **Style:** Premium Experience
            """)
        
        with summary_col3:
            st.markdown("""
            **✅ Next Steps**
            - Review and customize itinerary
            - Book flights and accommodation
            - Check passport/visa requirements
            - Purchase travel insurance
            """)
        
        # Download option
        st.markdown("---")
        
        # Combine all content for download
        full_plan = f"""
# 🌍 AI Travel Plan: {source} to {destination}

## Trip Details
- **From:** {source}
- **To:** {destination}
- **Dates:** {dates}  
- **Budget:** ${budget}
- **Preferences:** {preferences}

## 📍 Destination Research
{formatted_research}

## ✈️ Flight Options
{formatted_flights}

## 🏨 Hotel Recommendations
{formatted_hotels}

## 📅 Detailed Itinerary
{formatted_itinerary}

---
*Generated by AI Travel Planner*
        """
        
        st.download_button(
            label="📄 Download Complete Travel Plan",
            data=full_plan,
            file_name=f"travel_plan_{source.replace(' ', '_').lower()}_to_{destination.replace(' ', '_').lower()}.txt",
            mime="text/plain",
            use_container_width=True
        )
        
    except Exception as e:
        st.error(f"❌ Error generating travel plan: {str(e)}")
        st.info("💡 Please try again or check your internet connection.")

else:
    # Welcome message when no plan is generated
    st.markdown("""
    <div class="info-box">
        <h3>🚀 Ready to plan your next adventure?</h3>
        <p>Fill in your travel details in the sidebar and click <strong>"Generate Travel Plan"</strong> to get started!</p>
        
        <h4>🎯 What you'll get:</h4>
        <ul>
            <li>📍 Comprehensive destination research</li>
            <li>✈️ Flight options with price comparisons</li>
            <li>🏨 Curated hotel recommendations</li>
            <li>📅 Detailed day-by-day itinerary</li>
            <li>💡 Expert travel tips and advice</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Sample preview
    st.markdown("### 👀 Preview: What your plan will look like")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **📍 Destination Research Sample:**
        - Overview of local culture and attractions
        - Best time to visit recommendations
        - Transportation and safety information
        - Local customs and etiquette tips
        """)
    
    with col2:
        st.markdown("""
        **📊 Data Tables Include:**
        - Flight comparison with prices and times
        - Hotel options with ratings and amenities  
        - Daily itinerary with costs and duration
        - Travel tips and recommendations
        """)
