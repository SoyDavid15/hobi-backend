# ai.py
import os
import json
from google import genai
from google.genai import types
from dotenv import load_dotenv


load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API"))



def verificacion_IA(imagen_pil, texto_reto:str):
    
    prompt = f"{texto_reto}. Analiza si la foto cumple con el reto."
    imagen_pil.thumbnail((1024, 1024))
    response = client.models.generate_content(
        model='gemini-2.0-flash',
        contents=[imagen_pil, prompt]
    )
    return response.text