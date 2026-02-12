from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
import uvicorn

app = FastAPI()

# ⚠️ Remplace par ta vraie clé ou utilise une variable d'environnement
OPENAI_API_KEY = "sk-proj-..."

# Définition de la structure attendue pour la requête (Validation Pydantic)
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
        "messages": [
            {"role": "user", "content": request_data.question}
        ]
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, headers=headers, json=payload, timeout=30.0)
            response.raise_for_status() # Lève une erreur si le code HTTP est 4xx ou 5xx
            return response.json()
        
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    # Lancement du serveur sur le port 5000
    uvicorn.run(app, host="0.0.0.0", port=5000)
