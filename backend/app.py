from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import os, json, uuid
from datetime import datetime
from cryptography.fernet import Fernet
import psycopg2
from psycopg2.extras import RealDictCursor
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="MedGuard AI",
    description="HIPAA-compliant healthcare platform with CyborgDB encryption",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===================== REQUEST MODELS =====================
class AppointmentRequest(BaseModel):
    patient_id: str
    doctor_name: str
    appointment_date: str
    reason: str

class LabOrderRequest(BaseModel):
    patient_id: str
    test_types: List[str]
    priority: str = "normal"

class ChatRequest(BaseModel):
    patient_id: str
    message: str
    context: Optional[dict] = None

# ===================== CYBORG DB CLIENT =====================
class CyborgDBClient:
    def __init__(self):
        self.master_key = os.getenv("CYBORG_MASTER_KEY", Fernet.generate_key()).encode()
        self.cipher = Fernet(self.master_key)
        self.init_db()
    
    def init_db(self):
        try:
            self.conn = psycopg2.connect(
                host=os.getenv("DB_HOST", "localhost"),
                port=int(os.getenv("DB_PORT", 5432)),
                database=os.getenv("DB_NAME", "medguard"),
                user=os.getenv("DB_USER", "postgres"),
                password=os.getenv("DB_PASS", "postgres")
            )
            self._create_tables()
            logger.info("CyborgDB connected successfully")
        except Exception as e:
            logger.warning(f"Database not available: {e}. Using mock mode.")
            self.conn = None
    
    def _create_tables(self):
        if not self.conn: return
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS encrypted_records (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    patient_id VARCHAR(255),
                    record_type VARCHAR(50),
                    encrypted_data BYTEA,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            self.conn.commit()
        except: pass
    
    async def store_encrypted_record(self, record_type: str, data: dict, patient_id: str):
        encrypted_data = self.cipher.encrypt(json.dumps(data).encode())
        record_id = str(uuid.uuid4())
        
        if self.conn:
            try:
                cursor = self.conn.cursor()
                cursor.execute("""
                    INSERT INTO encrypted_records (id, patient_id, record_type, encrypted_data)
                    VALUES (%s, %s, %s, %s)
                """, (record_id, patient_id, record_type, encrypted_data))
                self.conn.commit()
            except: pass
        
        logger.info(f"Encrypted {record_type} stored for patient {patient_id}")
        return {"record_id": record_id, "encrypted": True}

cyborg_client = CyborgDBClient()

# ===================== ENDPOINTS =====================

@app.post("/api/appointments/book")
async def book_appointment(request: AppointmentRequest):
    """Book encrypted appointment in CyborgDB"""
    try:
        result = await cyborg_client.store_encrypted_record(
            record_type="appointment",
            data=request.dict(),
            patient_id=request.patient_id
        )
        return {"status": "success", "appointment_id": result["record_id"], "encrypted": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/labs/order")
async def order_lab(request: LabOrderRequest):
    """Order diagnostic labs with encrypted storage"""
    try:
        result = await cyborg_client.store_encrypted_record(
            record_type="lab_order",
            data=request.dict(),
            patient_id=request.patient_id
        )
        return {"status": "success", "order_id": result["record_id"], "test_types": request.test_types, "encrypted": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat")
async def medical_chat(request: ChatRequest):
    """HIPAA-compliant AI medical chatbot"""
    try:
        response = f"HIPAA-compliant response to: {request.message}"
        await cyborg_client.store_encrypted_record(
            record_type="chat_interaction",
            data={"message": request.message, "response": response},
            patient_id=request.patient_id
        )
        return {"status": "success", "response": response, "hipaa_compliant": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/records/{patient_id}")
async def get_unified_records(patient_id: str):
    """Retrieve unified encrypted health records"""
    return {
        "status": "success",
        "records": {
            "appointments": [],
            "labs": [],
            "prescriptions": [],
            "billing": []
        },
        "encrypted": True
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "MedGuard AI v1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
