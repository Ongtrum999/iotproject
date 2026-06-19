import json
import threading
import paho.mqtt.client as mqtt
from gtts import gTTS
import os
import platform

# Configuration
MQTT_BROKER = "127.0.0.1"
MQTT_PORT = 1883
MQTT_TOPIC = "smarttimer/deviceB"

# Speak function 
def say_vietnamese(text):
    print(f"Device B Speaking (VI): {text}")
    try:
        tts = gTTS(text=text, lang='vi')
        filename = "temp_vi.mp3"
        tts.save(filename)

        sys_os = platform.system()
        if sys_os == "Windows":
            os.system(f"start {filename}")
        elif sys_os == "Darwin": 
            os.system(f"afplay {filename}")
        else: 
            os.system(f"mpg321 {filename} || mplayer {filename}")
    except Exception as e:
        print(f"TTS Error: {e}")

def announce_timer_vi():
    say_vietnamese("Thời gian của bạn đã hết.")

# MQTT Callback
def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        text_vi = payload.get("speech", "")
        seconds = payload.get("seconds", 0)

        if text_vi:
            say_vietnamese(text_vi)

        if seconds > 0:
            threading.Timer(seconds, announce_timer_vi).start()
            print(f"Timer set for {seconds} seconds on Device B.")
            
    except Exception as e:
        print(f"Message parsing error: {e}")

# Initialize MQTT Client
mqtt_client = mqtt.Client(client_id="DeviceB")
mqtt_client.on_message = on_message

try:
    mqtt_client.connect(MQTT_BROKER, MQTT_PORT)
    mqtt_client.subscribe(MQTT_TOPIC)
    print("Device B is running. Waiting for messages from Device A...")
    mqtt_client.loop_forever()
except Exception as e:
    print(f"Failed to connect to MQTT broker. Is Mosquitto running? Error: {e}")