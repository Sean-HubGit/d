import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
import uvicorn
# Optionnel : pip install python-dotenv pour le test local
from dotenv import load_dotenv 

# Charge le fichier .env si présent (utile uniquement en local)
load_dotenv()

app = FastAPI()

# Récupère la clé depuis l'environnement
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("❌ Erreur : La variable d'environnement OPENAI_API_KEY n'est pas définie.")

class QuestionRequest(BaseModel):
    question: str

@app.post("/ask")
async def ask(request_data: QuestionRequest):
    url = "https://api.openai.com/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": request_data.question}]
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, headers=headers, json=payload, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)
