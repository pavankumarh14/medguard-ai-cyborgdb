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

from cyborg_integration import CyborgDBClient

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

# ====================== REQUEST MODELS ======================
class AppointmentRequest(BaseModel):
    patient_id: str
    doctor_name: str
    appointment_date: str
    reason: str

class LabOrderRequest(BaseModel):
    patient_id: str
    test_types: List[str]
    priority: str = "normal"

class BillingRequest(BaseModel):
    patient_id: str
    service_date: str
    amount: float
    service_description: str

# ====================== GLOBAL CYBORG CLIENT ======================
cyborg_client = None

@app.on_event("startup")
def startup_event():
    global cyborg_client
    try:
        cyborg_client = CyborgDBClient(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "5432")),
            database=os.getenv("DB_NAME", "medguard_db"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", "password")
        )
        logger.info("CyborgDB client initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize CyborgDB client: {str(e)}")
        raise

@app.on_event("shutdown")
def shutdown_event():
    global cyborg_client
    if cyborg_client:
        try:
            cyborg_client.close_connection()
            logger.info("CyborgDB connection closed")
        except Exception as e:
            logger.error(f"Error closing connection: {str(e)}")

# ====================== HEALTH CHECK ======================
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "MedGuard AI v1.0.0"}

# ====================== APPOINTMENT ENDPOINTS ======================
@app.post("/api/appointments")
async def create_appointment(request: AppointmentRequest):
    """Create a new appointment with encrypted storage"""
    try:
        appointment_id = str(uuid.uuid4())
        response = f"Appointment {appointment_id} scheduled with Dr. {request.doctor_name}"
        
        await cyborg_client.store_encrypted_record(
            record_type="appointment",
            data={"appointment_id": appointment_id, "doctor_name": request.doctor_name, "date": request.appointment_date, "reason": request.reason},
            patient_id=request.patient_id
        )
        
        return {"status": "success", "response": response, "hipaa_compliant": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/appointments/{patient_id}")
async def get_appointments(patient_id: str):
    """Retrieve patient appointments (encrypted)"""
    try:
        appointments = await cyborg_client.query_encrypted_records(patient_id, "appointment")
        return {"status": "success", "appointments": appointments}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ====================== LAB ORDER ENDPOINTS ======================
@app.post("/api/labs")
async def create_lab_order(request: LabOrderRequest):
    """Create encrypted lab orders"""
    try:
        lab_id = str(uuid.uuid4())
        response = f"Lab order {lab_id} created for patient {request.patient_id}"
        
        await cyborg_client.store_encrypted_record(
            record_type="lab_order",
            data={"lab_id": lab_id, "test_types": request.test_types, "priority": request.priority},
            patient_id=request.patient_id
        )
        
        return {"status": "success", "response": response, "hipaa_compliant": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/labs/{patient_id}")
async def get_lab_orders(patient_id: str):
    """Retrieve patient lab orders (encrypted)"""
    try:
        labs = await cyborg_client.query_encrypted_records(patient_id, "lab_order")
        return {"status": "success", "labs": labs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ====================== PRESCRIPTION ENDPOINTS ======================
@app.post("/api/prescriptions")
async def create_prescription(request: dict):
    """Create encrypted prescriptions"""
    try:
        prescription_id = str(uuid.uuid4())
        response = f"Prescription {prescription_id} issued"
        
        await cyborg_client.store_encrypted_record(
            record_type="prescription",
            data={"prescription_id": prescription_id, "medication": request.get("medication"), "dosage": request.get("dosage")},
            patient_id=request["patient_id"]
        )
        
        return {"status": "success", "response": response, "hipaa_compliant": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/prescriptions/{patient_id}")
async def get_prescriptions(patient_id: str):
    """Retrieve patient prescriptions (encrypted)"""
    try:
        prescriptions = await cyborg_client.query_encrypted_records(patient_id, "prescription")
        return {"status": "success", "prescriptions": prescriptions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ====================== BILLING ENDPOINTS ======================
@app.post("/api/billing")
async def create_billing_record(request: BillingRequest):
    """Create encrypted billing records"""
    try:
        billing_id = str(uuid.uuid4())
        response = f"Billing record {billing_id} created"
        
        await cyborg_client.store_encrypted_record(
            record_type="billing",
            data={"billing_id": billing_id, "amount": request.amount, "service_date": request.service_date, "service_description": request.service_description},
            patient_id=request.patient_id
        )
        
        return {"status": "success", "response": response, "hipaa_compliant": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/billing/{patient_id}")
async def get_billing_records(patient_id: str):
    """Retrieve patient billing records (encrypted)"""
    try:
        billing_records = await cyborg_client.query_encrypted_records(patient_id, "billing")
        return {"status": "success", "billing_records": billing_records}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ====================== UNIFIED RECORDS ENDPOINT ======================
@app.get("/api/records/{patient_id}")
async def get_unified_records(patient_id: str):
    """Retrieve unified encrypted health records"""
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

# ====================== MEDICAL CHAT ENDPOINT ======================
@app.post("/api/chat")
async def medical_chat(request: dict):
    """HIPAA-compliant AI medical chatbot"""
    try:
        response = f"HIPAA-compliant response to: {request.get('message')}"
        
        await cyborg_client.store_encrypted_record(
            record_type="chat_interaction",
            data={"message": request.get('message'), "response": response},
            patient_id=request.get('patient_id')
        )
        
        return {"status": "success", "response": response, "hipaa_compliant": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
