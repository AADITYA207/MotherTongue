import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import mysql.connector
from datetime import datetime
import uvicorn

app = FastAPI()

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to your frontend's URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MySQL connection config (use env vars if set)
db_config = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'user': os.getenv('MYSQL_USER', 'admin'),
    'password': os.getenv('MYSQL_PASSWORD', 'admin'),
    'database': os.getenv('MYSQL_DATABASE', 'mothertongue')
}

class TherapyResponse(BaseModel):
    person: List[str]
    therapy: List[str]
    language: List[str]
    phone: str
    timestamp: Optional[str] = None

@app.post("/api/submit")
async def submit_form(response: TherapyResponse):
    timestamp = response.timestamp or datetime.now().isoformat()
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO therapy_responses (person, therapy, language, phone, timestamp) VALUES (%s, %s, %s, %s, %s)",
            (
                str(response.person),
                str(response.therapy),
                str(response.language),
                response.phone,
                timestamp
            )
        )
        conn.commit()
        cursor.close()
        conn.close()
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/health")
def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
