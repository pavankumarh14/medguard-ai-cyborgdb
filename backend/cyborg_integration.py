import asyncio
import psycopg2
from psycopg2.extras import RealDictCursor
from cryptography.fernet import Fernet
import json
import logging
from typing import Dict, List, Optional
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

class CyborgDBClient:
    """
    Integration layer for CyborgDB - handles encrypted vector storage
    for sensitive healthcare data with HIPAA compliance
    """
    
    def __init__(self, host: str, port: int, db_name: str, master_key: str):
        self.host = host
        self.port = port
        self.db_name = db_name
        self.master_key = master_key.encode() if master_key else Fernet.generate_key()
        self.cipher = Fernet(self.master_key)
        self.connection_pool = []
        self.init_connection()
    
    def init_connection(self):
        """Initialize PostgreSQL connection for CyborgDB"""
        try:
            self.conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.db_name,
                user="postgres",
                password="postgres"
            )
            logger.info(f"Connected to CyborgDB at {self.host}:{self.port}")
            self._create_tables()
        except Exception as e:
            logger.error(f"Failed to connect to CyborgDB: {str(e)}")
            raise
    
    def _create_tables(self):
        """Create encrypted vector storage tables"""
        cursor = self.conn.cursor()
        try:
            # Main encrypted records table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS encrypted_records (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    patient_id VARCHAR(255) NOT NULL,
                    record_type VARCHAR(50) NOT NULL,
                    encrypted_data BYTEA NOT NULL,
                    data_hash VARCHAR(64),
                    role_based_access JSONB DEFAULT '{}',
                    audit_log JSONB DEFAULT '[]',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_patient_id (patient_id),
                    INDEX idx_record_type (record_type)
                )
            """)
            
            # Vector embeddings table for semantic search
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS vector_embeddings (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    record_id UUID REFERENCES encrypted_records(id),
                    embedding_vector FLOAT8[],
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Audit trail for HIPAA compliance
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS audit_trail (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    patient_id VARCHAR(255),
                    action VARCHAR(100),
                    user_role VARCHAR(50),
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    details JSONB
                )
            """)
            
            self.conn.commit()
            logger.info("CyborgDB tables created successfully")
        except Exception as e:
            logger.error(f"Error creating tables: {str(e)}")
            self.conn.rollback()
    
    async def store_encrypted_record(self, record_type: str, data: dict, patient_id: str):
        """
        Store encrypted record in CyborgDB
        """
        try:
            # Encrypt data
            json_data = json.dumps(data).encode()
            encrypted_data = self.cipher.encrypt(json_data)
            
            cursor = self.conn.cursor()
            record_id = str(uuid.uuid4())
            
            cursor.execute("""
                INSERT INTO encrypted_records 
                (id, patient_id, record_type, encrypted_data, role_based_access)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                record_id,
                patient_id,
                record_type,
                encrypted_data,
                json.dumps({"doctor": True, "patient": True})
            ))
            
            # Log audit trail
            self._log_audit(patient_id, "STORE", "SYSTEM", {
                "record_id": record_id,
                "record_type": record_type
            })
            
            self.conn.commit()
            logger.info(f"Stored encrypted {record_type} for patient {patient_id}")
            
            return {
                "record_id": record_id,
                "encrypted": True,
                "storage": "CyborgDB"
            }
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Error storing encrypted record: {str(e)}")
            raise
    
    async def query_encrypted_records(self, patient_id: str, record_type: Optional[str] = None, limit: int = 10):
        """
        Query and decrypt records from CyborgDB
        """
        try:
            cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            
            if record_type:
                cursor.execute("""
                    SELECT * FROM encrypted_records 
                    WHERE patient_id = %s AND record_type = %s
                    ORDER BY created_at DESC
                    LIMIT %s
                """, (patient_id, record_type, limit))
            else:
                cursor.execute("""
                    SELECT * FROM encrypted_records 
                    WHERE patient_id = %s
                    ORDER BY created_at DESC
                    LIMIT %s
                """, (patient_id, limit))
            
            results = []
            for row in cursor.fetchall():
                # Decrypt data
                decrypted_data = self.cipher.decrypt(row['encrypted_data'])
                results.append({
                    "id": str(row['id']),
                    "record_type": row['record_type'],
                    "data": json.loads(decrypted_data),
                    "created_at": row['created_at'].isoformat(),
                    "role_based_access": row['role_based_access']
                })
            
            logger.info(f"Retrieved {len(results)} encrypted records for patient {patient_id}")
            return results
        except Exception as e:
            logger.error(f"Error querying records: {str(e)}")
            raise
    
    async def get_unified_records(self, patient_id: str):
        """
        Get all unified records for a patient
        """
        try:
            appointments = await self.query_encrypted_records(patient_id, "appointment")
            labs = await self.query_encrypted_records(patient_id, "lab_order")
            prescriptions = await self.query_encrypted_records(patient_id, "prescription")
            billing = await self.query_encrypted_records(patient_id, "billing")
            
            return {
                "appointments": appointments,
                "labs": labs,
                "prescriptions": prescriptions,
                "billing": billing
            }
        except Exception as e:
            logger.error(f"Error getting unified records: {str(e)}")
            raise
    
    def _log_audit(self, patient_id: str, action: str, user_role: str, details: dict):
        """
        Log audit trail for HIPAA compliance
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO audit_trail (patient_id, action, user_role, details)
                VALUES (%s, %s, %s, %s)
            """, (patient_id, action, user_role, json.dumps(details)))
            self.conn.commit()
        except Exception as e:
            logger.error(f"Error logging audit: {str(e)}")
    
    def check_connection(self) -> bool:
        """
        Check if database connection is active
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT 1")
            return True
        except:
            return False
