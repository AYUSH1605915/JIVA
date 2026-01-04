from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from groq import Groq
import uvicorn
import os

# 1. Initialize the FastAPI app FIRST (This fixes the NameError)
app = FastAPI()

# 2. Setup your Groq Client
# Replace with your key from https://console.groq.com/keys
import os
from dotenv import load_dotenv

load_dotenv() # This loads the variables from your .env file
api_key = os.getenv("GROQ_API_KEY")

# 3. Define file paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
html_path = os.path.join(BASE_DIR, "index.html")

SYSTEM_PROMPT = "You are JIVA, a helpful AI Voice Agent. Respond concisely (1-2 sentences)."

# 4. Route to serve the webpage
@app.get("/", response_class=HTMLResponse)
async def get_index():
    try:
        with open(html_path, "r") as f:
            return f.read()
    except FileNotFoundError:
        return "<h1>Error: index.html not found!</h1>"

# 5. Route to handle AI Chat
@app.post("/chat")
async def chat(request: Request):
    try:
        data = await request.json()
        user_message = data.get("message")

        # Calling Groq API
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message}
            ]
        )
        return {"reply": completion.choices[0].message.content}
    except Exception as e:
        print(f"Error: {e}")
        return {"reply": "I am having trouble processing that right now."}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5051)