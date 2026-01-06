import os
import time
import speech_recognition as sr
from gtts import gTTS
from groq import Groq
from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import HTMLResponse

app = FastAPI()

# --- JIVA CONFIGURATION ---
# Replace with your actual Groq Key
client = Groq(api_key="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")
recognizer = sr.Recognizer()

def speak(text, lang='en'):
    """Converts text to human voice and plays it clearly on Mac."""
    print(f"JIVA ({lang}): {text}")
    try:
        # Generate the speech file
        tts = gTTS(text=text, lang=lang, slow=False)
        tts.save("response.mp3")
        # 'afplay' is the best way to play audio on Mac without conflicts
        os.system("afplay response.mp3")
    except Exception as e:
        print(f"Voice Error: {e}")

def get_jiva_response(user_input):
    """JIVA's multilingual brain."""
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "Your name is JIVA. You are a professional, helpful female AI agent. You MUST respond in the same language the user speaks (Hindi, English, etc). Keep answers brief and human-like."},
                {"role": "user", "content": user_input}
            ]
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"Groq Error: {e}")
        return "I am having a connection issue."

def start_jiva_loop():
    """Fixed loop to avoid Mac Audio Unit context errors."""
    # Custom JIVA Greeting
    speak("Hey welcome, I am jiva. I am ready to help you.", lang='en')
    
    # We open the microphone once and keep it open
    with sr.Microphone() as source:
        print("Calibrating for room noise...")
        recognizer.adjust_for_ambient_noise(source, duration=1.5)
        
        while True:
            try:
                print("\nJIVA is listening...")
                # phrase_time_limit helps JIVA not get 'stuck' listening
                audio = recognizer.listen(source, timeout=None, phrase_time_limit=8)
                
                print("Thinking...")
                # Google recognition handles multiple languages automatically
                user_text = recognizer.recognize_google(audio)
                print(f"You: {user_text}")

                if any(word in user_text.lower() for word in ["stop", "exit", "bye"]):
                    speak("Goodbye! JIVA is signing off.", lang='en')
                    break

                response = get_jiva_response(user_text)
                speak(response)
                
            except sr.UnknownValueError:
                # Just loop back if it didn't hear clear words
                continue
            except Exception as e:
                print(f"Loop Error: {e}")
                time.sleep(1) # Wait a second before trying again
                continue

# --- WEB ROUTES ---
@app.get("/")
async def get_index():
    with open("index.html", "r") as f:
        return HTMLResponse(content=f.read())

@app.post("/start-jiva")
async def start_agent(background_tasks: BackgroundTasks):
    background_tasks.add_task(start_jiva_loop)
    return {"status": "JIVA activated"}

if __name__ == "__main__":
    import uvicorn
    # Using 127.0.0.1 for better Mac stability
    uvicorn.run(app, host="127.0.0.1", port=8000)