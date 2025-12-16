"""Database models for MedGuard AI healthcare platform."""

from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any


class RecordType(str, Enum):
    """Types of healthcare records that can be encrypted and stored."""
    APPOINTMENT = "appointment"
    LAB_ORDER = "lab_order"
    PRESCRIPTION = "prescription"
    BILLING = "billing"
    CHAT_INTERACTION = "chat_interaction"
    PATIENT_INFO = "patient_info"


class EncryptedRecord:
    """Represents an encrypted healthcare record in CyborgDB."""
    
    def __init__(
        self,
        patient_id: str,
        record_type: RecordType,
        data: Dict[str, Any],
        encrypted_data: str,
        encryption_key_id: str,
        timestamp: datetime = None,
        record_id: Optional[str] = None
    ):
        self.record_id = record_id
        self.patient_id = patient_id
        self.record_type = record_type
        self.data = data
        self.encrypted_data = encrypted_data
        self.encryption_key_id = encryption_key_id
        self.timestamp = timestamp or datetime.utcnow()
        self.is_encrypted = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert record to dictionary representation."""
        return {
            "record_id": self.record_id,
            "patient_id": self.patient_id,
            "record_type": self.record_type.value,
            "data": self.data,
            "encrypted_data": self.encrypted_data,
            "encryption_key_id": self.encryption_key_id,
            "timestamp": self.timestamp.isoformat(),
            "is_encrypted": self.is_encrypted
        }


class AuditLog:
    """Represents an audit log entry for HIPAA compliance."""
    
    def __init__(
        self,
        patient_id: str,
        action: str,
        user_role: str,
        details: Dict[str, Any],
        timestamp: datetime = None,
        status: str = "success"
    ):
        self.patient_id = patient_id
        self.action = action
        self.user_role = user_role
        self.details = details
        self.timestamp = timestamp or datetime.utcnow()
        self.status = status

    def to_dict(self) -> Dict[str, Any]:
        """Convert audit log to dictionary representation."""
        return {
            "patient_id": self.patient_id,
            "action": self.action,
            "user_role": self.user_role,
            "details": self.details,
            "timestamp": self.timestamp.isoformat(),
            "status": self.status
        }


class Patient:
    """Represents a patient in the MedGuard system."""
    
    def __init__(
        self,
        patient_id: str,
        name: str,
        date_of_birth: str,
        ssn_encrypted: str,
        email: str,
        phone: str,
        address: str
    ):
        self.patient_id = patient_id
        self.name = name
        self.date_of_birth = date_of_birth
        self.ssn_encrypted = ssn_encrypted
        self.email = email
        self.phone = phone
        self.address = address
        self.created_at = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """Convert patient to dictionary representation."""
        return {
            "patient_id": self.patient_id,
            "name": self.name,
            "date_of_birth": self.date_of_birth,
            "ssn_encrypted": self.ssn_encrypted,
            "email": self.email,
            "phone": self.phone,
            "address": self.address,
            "created_at": self.created_at.isoformat()
        }
