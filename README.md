# MedGuard AI: Secure Healthcare Platform Powered by CyborgDB

## 🏥 Overview

MedGuard AI is a **HIPAA-compliant healthcare platform** that leverages **CyborgDB's encrypted vector database** for secure storage and querying of sensitive patient data. The platform demonstrates enterprise-grade security for healthcare applications including patient appointments, diagnostic labs, medical imaging analysis, discharge summaries, and AI-powered medical chatbot.

## 🔐 Key Features

### 1. **Encrypted Patient Appointments**
- Patients book doctor appointments with encrypted data storage
- All appointment data stored as encrypted vector embeddings in CyborgDB
- Role-based access control (Doctor, Patient, Admin)
- Real-time appointment scheduling and notifications

### 2. **Diagnostic Labs Management**
- Patients select diagnostic tests (X-Ray, MRI, Bloodwork, CT Scan)
- Lab results stored with encryption-in-use
- Multi-tenant architecture with strict data isolation
- Real-time lab result notifications

### 3. **AI Medical Imaging Analysis**
- Automated analysis of medical images using computer vision
- Image findings transformed to encrypted vector embeddings
- Radiologists review encrypted reports
- Audit trail for compliance

### 4. **Automated Discharge Summaries**
- AI-generated clinical summaries from medical records
- Embeddings encrypted for authorized users only
- Accessible to doctors, nurses, and authorized pharmacy staff

### 5. **Secure Prescription Management**
- Doctors enter prescriptions converted to encrypted embeddings
- Only authorized pharmacies and patients access details
- Controlled substance tracking and compliance logging

### 6. **Unified Health Records**
- All records (appointments, tests, prescriptions, bills) unified in CyborgDB
- Multi-role access with fine-grained permissions
- Full audit logging for HIPAA compliance
- Patient consent controls

### 7. **HIPAA-Compliant Medical Chatbot**
- AI-powered chatbot for medical queries and triage
- Context-aware responses using encrypted patient records
- Compliant with healthcare privacy regulations
- Audit trail of all interactions

### 8. **Encrypted Billing & Payments**
- Secure payment gateway integration
- Encrypted transaction records
- Billing statements accessible only to authorized parties

## 🛠️ Tech Stack

### Backend
- **FastAPI** - High-performance async web framework
- **PostgreSQL** + **CyborgDB** - Encrypted vector database
- **Python 3.9+** - Core language
- **Cryptography** - Fernet encryption for data at rest
- **OpenAI API** - Medical chatbot intelligence

### Frontend
- **HTML5/CSS3** - Responsive UI
- **JavaScript (Vanilla)** - Interactive components
- **Fetch API** - Secure API communication

### Infrastructure
- **Docker & Docker Compose** - Containerization
- **Redis** - Caching and session management
- **Uvicorn** - ASGI server

## 📋 Architecture

```
Patient Books Appointment
         ↓
Data Encrypted in CyborgDB
         ↓
Tests Scheduled
         ↓
Results Stored as Encrypted Vectors
         ↓
Doctor Creates AI Discharge Summary
         ↓
AI Imaging Analysis
         ↓
Prescriptions Encrypted
         ↓
All Interactions Use Encryption-in-Use
         ↓
Prevents Vector Inversion & Data Reconstruction
```

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Docker & Docker Compose
- PostgreSQL 14+
- Redis 7+

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/pavankumarh14/medguard-ai-cyborgdb.git
cd medguard-ai-cyborgdb
```

2. **Set up environment variables**
```bash
cp .env.example .env
# Update .env with your CyborgDB credentials
```

3. **Install dependencies**
```bash
cd backend
pip install -r requirements.txt
```

4. **Start services with Docker**
```bash
docker-compose up -d
```

5. **Initialize database**
```bash
python backend/app.py  # Creates tables
```

6. **Access the application**
- API: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`
- Frontend: `http://localhost:3000`

## 📝 API Endpoints

### Appointments
```
POST   /api/appointments/book        - Book appointment
GET    /api/appointments/{patient_id} - Get patient appointments
```

### Diagnostic Labs
```
POST   /api/labs/order               - Order diagnostic tests
POST   /api/labs/results/{order_id}  - Upload lab results
```

### Medical Chatbot
```
POST   /api/chat                     - Get medical AI response
```

### Health Records
```
GET    /api/records/{patient_id}     - Get unified encrypted records
```

## 🔒 Security Features

### CyborgDB Integration
- **Encryption-in-Use**: All records encrypted with Fernet
- **Vector Embeddings**: Sensitive data stored as encrypted vectors
- **Secure Search**: Queries on encrypted data without decryption
- **Forward Privacy**: No information leakage about future queries
- **Access Control**: Multi-tenant isolation with role-based access
- **Audit Trail**: All access logged for compliance

### HIPAA Compliance
- ✅ Encryption of PHI at rest and in transit
- ✅ Role-based access control (RBAC)
- ✅ Comprehensive audit logging
- ✅ Patient consent management
- ✅ Data breach notification capability
- ✅ Secure authentication
- ✅ De-identification support

## 📊 Sample Data

The application includes sample data for testing:
- 5 sample patients
- 10+ appointment records
- Lab results with images
- Medical imaging analysis results
- Discharge summaries

## 🧪 Testing

```bash
# Run tests
python -m pytest backend/tests/

# Test appointment booking
curl -X POST http://localhost:8000/api/appointments/book \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "P001",
    "doctor_name": "Dr. Smith",
    "appointment_date": "2025-12-20T10:00:00",
    "reason": "Regular checkup"
  }'
```

## 📚 Documentation

- [Architecture Documentation](./docs/ARCHITECTURE.md)
- [API Reference](./docs/API_REFERENCE.md)
- [Security Whitepaper](./docs/SECURITY.md)
- [CyborgDB Integration Guide](./docs/CYBORGDB_INTEGRATION.md)

## 🏆 Hackathon Submission

This project is submitted for the **CyborgDB Hackathon 2025**.

**Innovation Highlight**: Demonstrates CyborgDB's capability to secure healthcare AI workflows while maintaining usability and performance.

## 👨‍💻 Author

**Pavan Kumar** - Full-stack AI/ML Developer
- GitHub: [@pavankumarh14](https://github.com/pavankumarh14)
- Focus: Healthcare technology, AI agents, secure systems

## 📄 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

- CyborgDB team for the encrypted vector database
- FastAPI community for the excellent framework
- HIPAA compliance resources and documentation

---

**Status**: ✅ Production-Ready Prototype | **Version**: 1.0.0 | **Last Updated**: December 2025
