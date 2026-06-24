import json
import threading
import requests
import speech_recognition as sr
import pyttsx3
import paho.mqtt.client as mqtt
from deep_translator import GoogleTranslator

# Configuration 
MQTT_BROKER = "broker.emqx.io" # Replace with your device B's IP address if on a different machine
MQTT_PORT = 1883
MQTT_TOPIC = "smarttimer/deviceB"
LOCAL_API_URL = "http://localhost:7071/parse_time"

mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_id="DeviceA")
mqtt_client.connect(MQTT_BROKER, MQTT_PORT)
mqtt_client.loop_start()

# Text-to-Speech
engine = pyttsx3.init()
engine.setProperty('rate', 150) 

def say(text):
    print(f"Device A Speaking: {text}")
    engine.say(text)
    engine.runAndWait()

# Translate function
def translate_text(text):
    try:
        return GoogleTranslator(source='en', target='vi').translate(text)
    except Exception as e:
        print(f"Translation error: {e}")
        return text

def send_to_device_b(text_fr, seconds=0):
    payload = {"speech": text_fr, "seconds": seconds}
    mqtt_client.publish(MQTT_TOPIC, json.dumps(payload))
    print(f"Sent payload to Device B via MQTT")

def get_timer_time(text):
    keywords = ['second', 'seconds', 'minute', 'minutes', 'hour', 'hours']
    if not any(k in text.lower() for k in keywords):
        return 0
    try:
        response = requests.post(LOCAL_API_URL, json={"text": text}, timeout=5)
        return response.json().get("seconds", 0)
    except Exception as e:
        print(f"API Error: {e}")
        return 0

def announce_timer(minutes, seconds):
    say(f"Time's up on your timer.")

def create_timer(duration_seconds):
    minutes, seconds = divmod(duration_seconds, 60)
    threading.Timer(duration_seconds, announce_timer, args=[minutes, seconds]).start()
    say(f"Timer started.")

def process_text(text):
    if not text.strip(): 
        return
    print(f"\n[+] Recognized: {text}")
    
    translated = translate_text(text)
    print(f"[+] Translated: {translated}")
    
    seconds = get_timer_time(text)
    send_to_device_b(translated, seconds)
    
    if seconds > 0:
        create_timer(seconds)

r = sr.Recognizer()
mic = sr.Microphone()

print("Device A is Listening... Speak an English command.")
with mic as source:
    r.adjust_for_ambient_noise(source)
    while True:
        try:
            audio = r.listen(source, phrase_time_limit=5)
            print("Processing audio...")
            text = r.recognize_google(audio) 
            threading.Thread(target=process_text, args=(text,), daemon=True).start()
        except sr.UnknownValueError:
            pass 
        except KeyboardInterrupt:
            print("\nShutting down Device A.")
            break
        except Exception as e:
            print(f"Error: {e}")