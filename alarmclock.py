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
    else:
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

# Initialize settings
settings = load_settings()
snooze_time = None
sound_file = "default_sound.wav"

# Function to choose sound file
def choose_sound():
    global sound_file
    uploaded_file = st.file_uploader("Choose Sound File", type=["wav"])
    if uploaded_file is not None:
        sound_file = f"uploaded_{uploaded_file.name}"
        with open(sound_file, 'wb') as f:
            f.write(uploaded_file.getbuffer())
    else:
        sound_file = "default_sound.wav"

# Alarm function
def alarm(alarm_type):
    global snooze_time
    while True:
        set_alarm_time = settings["alarm_times"][alarm_type]
        time.sleep(1)
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        current_day = datetime.datetime.now().strftime("%A")

        if (current_time == set_alarm_time and current_day in settings["alarm_days"][alarm_type]) or \
           (snooze_time and current_time == snooze_time.strftime("%H:%M:%S")):
            st.warning(f"Time for {alarm_type}: {settings['alarm_labels'][alarm_type]}")
            winsound.PlaySound(sound_file, winsound.SND_ASYNC)
            if st.button("Snooze"):
                snooze()
            stop_alarm()
            break

# Reminder function to notify 15 minutes before the alarm
def reminder(alarm_type):
    while True:
        set_alarm_time = settings["alarm_times"][alarm_type]
        if set_alarm_time:
            alarm_datetime = datetime.datetime.strptime(set_alarm_time, "%H:%M:%S")
            reminder_time = (alarm_datetime - datetime.timedelta(minutes=5)).strftime("%H:%M:%S")
            time.sleep(1)
            current_time = datetime.datetime.now().strftime("%H:%M:%S")
            current_day = datetime.datetime.now().strftime("%A")

            if current_time == reminder_time and current_day in settings["alarm_days"][alarm_type]:
                st.info(f"Reminder: {settings['alarm_labels'][alarm_type]} in 5 minutes")
                break

# Stop alarm function
def stop_alarm():
    time.sleep(10)
    winsound.PlaySound(None, winsound.SND_ASYNC)
    st.write("Alarm stopped")

# Snooze function
def snooze():
    global snooze_time
    snooze_duration = settings["snooze_duration"]
    snooze_time = datetime.datetime.now() + datetime.timedelta(minutes=snooze_duration)
    winsound.PlaySound(None, winsound.SND_ASYNC)

# Set alarm function
def set_alarm(alarm_type, label, hour, minute, second, days):
    settings["alarm_times"][alarm_type] = f"{hour}:{minute}:{second}"
    settings["alarm_labels"][alarm_type] = label
    settings["alarm_days"][alarm_type] = days
    save_settings()
    Thread(target=alarm, args=(alarm_type,)).start()
    Thread(target=reminder, args=(alarm_type,)).start()

# Streamlit UI setup
st.title("Wake Me Up")
choose_sound()

# Customizable snooze duration
settings["snooze_duration"] = st.slider("Snooze Duration (minutes)", 1, 30, settings["snooze_duration"])
save_settings()

# Input for custom alarm label
alarm_label = st.text_input("Alarm Label:")

# Dropdowns for setting alarm time
hour = st.selectbox("Hour", [f"{i:02d}" for i in range(24)])
minute = st.selectbox("Minute", [f"{i:02d}" for i in range(60)])
second = st.selectbox("Second", [f"{i:02d}" for i in range(60)])

# Days of the week checkboxes
days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
day_vars = {day: st.checkbox(day) for day in days_of_week}

# Function to get selected days
def get_selected_days():
    return [day for day, selected in day_vars.items() if selected]

# Columns for better layout
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Set General Alarm"):
        set_alarm("General", alarm_label, hour, minute, second, get_selected_days())

with col2:
    if st.button("Enable Breakfast Alarm"):
        Thread(target=alarm, args=("Breakfast",)).start()
        Thread(target=reminder, args=("Breakfast",)).start()

with col3:
    if st.button("Enable Lunch Alarm"):
        Thread(target=alarm, args=("Lunch",)).start()
        Thread(target=reminder, args=("Lunch",)).start()

if st.button("Enable Dinner Alarm"):
    Thread(target=alarm, args=("Dinner",)).start()
    Thread(target=reminder, args=("Dinner",)).start()

# Function to update the current time display
def update_time():
    while True:
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        st.write(f"Current Time: {current_time}")
        time.sleep(1)

# Start the current time update thread
Thread(target=update_time, daemon=True).start()
