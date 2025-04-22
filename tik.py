import os
import uuid
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from gtts import gTTS
from moviepy import ImageClip, AudioFileClip

app = FastAPI()
GEMINI_API_KEY = "Put in your API key here"

class Prompt(BaseModel):
    topic: str

def generationoffscriptswithgemini(topic, api_key):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"  
    headers = {"Content-Type": "application/json"}

    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": f"Create a fun and educational video script on the topic: {topic}."
                    }
                ]
            }
        ]
    }

    response = requests.post(url, headers=headers, json=data, timeout=30)
    if response.status_code == 200:
        return response.json()["candidates"][0]["content"]["parts"][0]["text"]
    else:
        raise Exception(f"Error from Gemini API: {response.text}")

@app.get("/")
async def root():
    return {"message": "Welcome to the TikTok Video Generator API!"}

@app.post("/generate-tiktok-video")
async def generate_tiktok_video(prompt: Prompt):
    audio_file = None
    output_path = None

    try:
        script = generationoffscriptswithgemini(prompt.topic, GEMINI_API_KEY)
        tts = gTTS(text=script)
        os.makedirs("videos", exist_ok=True)
        audio_file = os.path.join("videos", f"audio_{uuid.uuid4()}.mp3")
        tts.save(audio_file)

        bg_image = ("background.jpg")
        if not os.path.exists(bg_image):
            raise Exception("Missing background image: background.jpg")

      
        image = ImageClip(bg_image, duration=60)  
        
        audio = AudioFileClip(audio_file)
    
        video = image.with_audio(audio)
        
    
        os.makedirs("videos", exist_ok=True)
        video_id = str(uuid.uuid4())[:8]
        output_path = f"videos/{video_id}.mp4"
        
      
        video.write_videofile(output_path, fps=24)
        video.close()
        

        

        return {
            "status": "success",
            "script": script,
            "video_path": output_path,
        }  
           
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

