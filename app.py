import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# Constants
LAT = 20.93
LONG = 77.75
LOCATION_NAME = "Amravati"

# 1. The "Key-Free" Weather Engine
def get_weather():
    """Fetches real-time weather from Open-Meteo API."""
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": LAT,
        "longitude": LONG,
        "current_weather": "true"
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        return data.get('current_weather')
    except Exception as e:
        st.error(f"Error fetching weather data: {e}")
        return None

# 2. The Event Simulator (Mock Data)
def get_local_events():
    """Generates random realistic events based on the day of the week."""
    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    today = datetime.now().strftime("%A")

    events_db = {
        "Monday": ["Weekday Business Mixer", "Quiet Reading Hour"],
        "Tuesday": ["Taco Tuesday", "Business Networking"],
        "Wednesday": ["Wine Down Wednesday", "Mid-week Yoga"],
        "Thursday": ["Thirsty Thursday Happy Hour", "Live Acoustic Music"],
        "Friday": ["Friday Night Fever", "Cocktail Workshop"],
        "Saturday": ["Saturday Night Jazz", "Pool Party"],
        "Sunday": ["Sunday Morning Yoga", "Brunch Special"]
    }

    # Return the day and the list of events for that day
    return today, events_db.get(today, ["General Relaxation"])

# 3. The Logic Brain (Merging Real Weather + Mock Events)
def get_recommendations(weather, events, guest_prefs):
    """Generates recommendations based on weather, events, and guest preferences."""
    recommendations = []

    if not weather:
        return [("System Error", "Could not retrieve weather data for recommendations.")]

    # Weather Logic
    temp = weather['temperature']
    code = weather['weathercode']
    # is_day is available in Open-Meteo current_weather

    # Real-time Rain: If Open-Meteo says it is raining (Weather Code > 50)
    if code > 50:
        recommendations.append(("Indoor Spa", "It's raining outside. Perfect for a relaxing spa day."))
        recommendations.append(("Warm Tea", "Stay cozy with our signature herbal tea."))

    # Real-time Heat: If Temp > 30°C
    if temp > 30:
        recommendations.append(("Poolside Cooler", "It's hot! Enjoy a refreshing drink by the pool."))
        recommendations.append(("AC Room Upgrade", "Stay cool with a premium AC room."))

    # Event Match: If "Saturday Jazz" is active AND Guest likes Music
    # We check if any event contains "Jazz" and guest likes "Music"
    # The requirement specifically mentions "Saturday Jazz" and "Music" -> "VIP Jazz Table"

    for event in events:
        if "Saturday Night Jazz" in event and "Music" in guest_prefs:
             recommendations.append(("VIP Jazz Table", "Since you love music, we saved you a spot for the Jazz night!"))

    # Additional generic logic to make it more robust (optional but good for "Senior Developer" persona)
    # If no specific logic triggered, maybe suggest something generic based on preferences
    if not recommendations:
        if "Food" in guest_prefs:
            recommendations.append(("Chef's Special", "Try our local delicacies at the restaurant."))
        else:
            recommendations.append(("Lounge Access", "Relax in our exclusive lounge area."))

    return recommendations

# Guest Profiles for the Sidebar
GUESTS = {
    "Alice (Business Traveler)": ["Business", "Quiet"],
    "Bob (Music Lover)": ["Music", "Party"],
    "Charlie (Wellness Guru)": ["Wellness", "Nature"],
    "Diana (Foodie)": ["Food", "Drinks"]
}

# Main App
def main():
    st.set_page_config(page_title="Perfect Stay Predictor", page_icon="🏨")

    # UI Layout: Header
    st.title("🏨 Perfect Stay Predictor")

    # UI Layout: Guest Selector (Sidebar)
    st.sidebar.header("Guest Selector")
    selected_guest_name = st.sidebar.selectbox("Choose a Guest", list(GUESTS.keys()))
    guest_prefs = GUESTS[selected_guest_name]
    st.sidebar.write(f"**Preferences:** {', '.join(guest_prefs)}")

    # Fetch Data
    with st.spinner("Fetching live weather from Amravati..."):
        weather = get_weather()

    day, events = get_local_events()

    if weather:
        # Header continued: "Live from Amravati" (Displaying the Real Temp)
        st.subheader(f"Live from {LOCATION_NAME}")

        col1, col2, col3 = st.columns(3)
        col1.metric("Temperature", f"{weather['temperature']}°C")

        # Determine condition string based on code
        condition = "Clear/Cloudy"
        if weather['weathercode'] > 50:
            condition = "Raining"
        elif weather['weathercode'] <= 3:
            condition = "Clear"

        col2.metric("Condition", condition)
        col3.metric("Wind Speed", f"{weather['windspeed']} km/h")

        # Display Events
        st.info(f"📅 **Today is {day}**. Local Events: {', '.join(events)}")

        # UI Layout: Blueprint Card
        st.markdown("---")
        st.subheader("📋 Your Personalized Blueprint")

        recs = get_recommendations(weather, events, guest_prefs)

        if recs:
            for title, desc in recs:
                st.success(f"**{title}**: {desc}")
        else:
             st.info("No specific recommendations for now. Enjoy your stay!")

    else:
        st.error("Could not load weather data. Please try again later.")

if __name__ == "__main__":
    main()
