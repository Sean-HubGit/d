import os
import httpx
import uvicorn
from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel
from dotenv import load_dotenv

# Charge le .env pour le local, ignoré sur Render
load_dotenv()

app = FastAPI(title="Mon API OpenAI Sécurisée")

# --- CONFIGURATION DES CLÉS ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# C'est cette clé que tu devras ajouter dans Render (ex: "mon_secret_123")
MY_INTERNAL_KEY = os.getenv("MY_INTERNAL_KEY") 

if not OPENAI_API_KEY:
    raise ValueError("❌ Erreur : OPENAI_API_KEY manquante.")
if not MY_INTERNAL_KEY:
    print("⚠️ Attention : MY_INTERNAL_KEY n'est pas définie. L'API est ouverte au public !")

# --- SYSTÈME DE VÉRIFICATION ---
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def verify_api_key(api_key: str = Security(api_key_header)):
    """Vérifie si la clé envoyée dans le header correspond à celle de Render."""
    if api_key == MY_INTERNAL_KEY:
        return api_key
    raise HTTPException(
        status_code=403, 
        detail="Accès refusé : Clé API interne invalide ou manquante."
    )

# --- MODÈLES DE DONNÉES ---
class QuestionRequest(BaseModel):
    question: str

# --- ROUTES ---
@app.get("/")
def home():
    return {"status": "L'API est en ligne. Utilisez le endpoint /ask en POST avec authentification."}

@app.post("/ask", dependencies=[Depends(verify_api_key)])
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
    # Render utilise souvent le port 10000 par défaut, mais uvicorn lira le port $PORT de Render
    port = int(os.environ.get("PORT", 5000))
    uvicorn.run(app, host="0.0.0.0", port=port)
