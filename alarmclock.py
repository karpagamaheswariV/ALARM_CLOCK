import streamlit as st
import datetime
import time
import winsound
from threading import Thread
import json
import os

# File to save alarm settings
settings_file = "alarm_settings.json"

# Load settings from file
def load_settings():
    if os.path.exists(settings_file):
        with open(settings_file, 'r') as f:
            return json.load(f)
    return {
        "alarm_times": {
            "General": None,
            "Breakfast": "08:00:00",
            "Lunch": "12:30:00",
            "Dinner": "19:30:00"
        },
        "alarm_labels": {
            "General": "",
            "Breakfast": "Breakfast Time",
            "Lunch": "Lunch Time",
            "Dinner": "Dinner Time"
        },
        "alarm_days": {
            "General": [],
            "Breakfast": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
            "Lunch": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
            "Dinner": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        },
        "snooze_duration": 5
    }

# Save settings to file
def save_settings():
    with open(settings_file, 'w') as f:
        json.dump(settings, f)

settings = load_settings()
snooze_time = None
sound_file = "default_sound.wav"

# Choose sound file
def choose_sound():
    global sound_file
    uploaded_file = st.file_uploader("Choose Sound File", type=["wav"], label_visibility="collapsed")
    if uploaded_file:
        sound_file = f"uploaded_{uploaded_file.name}"
        with open(sound_file, 'wb') as f:
            f.write(uploaded_file.getbuffer())
    else:
        sound_file = "default_sound.wav"

# Alarm function
def alarm(alarm_type):
    global snooze_time
    while True:
        set_alarm_time = settings["alarm_times"].get(alarm_type)
        if not set_alarm_time:
            continue

        time.sleep(1)
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        current_day = datetime.datetime.now().strftime("%A")

        if (current_time == set_alarm_time and current_day in settings["alarm_days"][alarm_type]) or \
           (snooze_time and current_time == snooze_time.strftime("%H:%M:%S")):
            st.toast(f"Time for {alarm_type}: {settings['alarm_labels'][alarm_type]}")
            winsound.PlaySound(os.path.abspath(sound_file), winsound.SND_ASYNC)
            break

# Reminder function
def reminder(alarm_type):
    while True:
        set_alarm_time = settings["alarm_times"].get(alarm_type)
        if not set_alarm_time:
            return

        alarm_datetime = datetime.datetime.strptime(set_alarm_time, "%H:%M:%S")
        reminder_time = (alarm_datetime - datetime.timedelta(minutes=5)).strftime("%H:%M:%S")
        
        time.sleep(1)
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        current_day = datetime.datetime.now().strftime("%A")

        if current_time == reminder_time and current_day in settings["alarm_days"][alarm_type]:
            st.toast(f"Reminder: {settings['alarm_labels'][alarm_type]} in 5 minutes")
            break

# Stop alarm
def stop_alarm():
    winsound.PlaySound(None, winsound.SND_ASYNC)
    st.toast("Alarm stopped")

# Snooze function
def snooze():
    global snooze_time
    snooze_time = datetime.datetime.now() + datetime.timedelta(minutes=settings["snooze_duration"])
    winsound.PlaySound(None, winsound.SND_ASYNC)
    st.toast(f"Alarm snoozed for {settings['snooze_duration']} minutes")

# Set alarm function
def set_alarm(alarm_type, label, hour, minute, second, days):
    settings["alarm_times"][alarm_type] = f"{hour}:{minute}:{second}"
    settings["alarm_labels"][alarm_type] = label
    settings["alarm_days"][alarm_type] = days
    save_settings()
    Thread(target=alarm, args=(alarm_type,), daemon=True).start()
    Thread(target=reminder, args=(alarm_type,), daemon=True).start()

# Streamlit UI setup
st.title("Wake Me Up 🕰️")

# Add some space for a cleaner look
st.markdown("<br>", unsafe_allow_html=True)

choose_sound()

st.markdown("<h3>Set Your Alarm Time 🕰️</h3>", unsafe_allow_html=True)

# Alarm label input with padding for aesthetics
alarm_label = st.text_input("Enter Alarm Label:", placeholder="E.g., Breakfast Time", label_visibility="collapsed")

# Time picker controls with some layout styling
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    hour = st.selectbox("Hour", [f"{i:02d}" for i in range(24)], label_visibility="collapsed")

with col2:
    minute = st.selectbox("Minute", [f"{i:02d}" for i in range(60)], label_visibility="collapsed")

with col3:
    second = st.selectbox("Second", [f"{i:02d}" for i in range(60)], label_visibility="collapsed")

# Days of the week with checkboxes and some padding
st.markdown("<h4>Choose Days for the Alarm 🗓️</h4>", unsafe_allow_html=True)
days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
selected_days = [day for day in days_of_week if st.checkbox(day, value=True)]

# Adjust snooze duration
st.markdown("<h4>Snooze Duration (in minutes) ⏲️</h4>", unsafe_allow_html=True)
settings["snooze_duration"] = st.slider("Snooze Duration", 1, 30, settings["snooze_duration"], label_visibility="collapsed")
save_settings()

# Buttons for alarm management
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Set General Alarm", key="general"):
        set_alarm("General", alarm_label, hour, minute, second, selected_days)

with col2:
    if st.button("Enable Breakfast Alarm", key="breakfast"):
        Thread(target=alarm, args=("Breakfast",), daemon=True).start()

with col3:
    if st.button("Enable Lunch Alarm", key="lunch"):
        Thread(target=alarm, args=("Lunch",), daemon=True).start()

if st.button("Enable Dinner Alarm"):
    Thread(target=alarm, args=("Dinner",), daemon=True).start()

# Stop Alarm Button
st.markdown("<br><br>", unsafe_allow_html=True)
col1, col2 = st.columns(2)

with col1:
    if st.button("Stop Alarm"):
        stop_alarm()

# Snooze Button
with col2:
    if st.button("Snooze"):
        snooze()

# Show live clock with styling
time_display = st.empty()
while True:
    time_display.markdown(f"<h4 style='text-align:center;'>Current Time: {datetime.datetime.now().strftime('%H:%M:%S')}</h4>", unsafe_allow_html=True)
    time.sleep(1)
