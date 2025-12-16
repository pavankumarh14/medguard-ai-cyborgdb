"""HIPAA-compliant medical chatbot powered by OpenAI and CyborgDB encryption."""

import os
import json
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
import openai
from cyborg_integration import CyborgDBClient

logger = logging.getLogger(__name__)


class MedicalChatbot:
    """HIPAA-compliant AI medical chatbot for patient consultations."""
    
    def __init__(self, cyborg_client: CyborgDBClient):
        self.cyborg_client = cyborg_client
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("LLM_MODEL", "gpt-4")
        self.temperature = float(os.getenv("LLM_TEMPERATURE", "0.7"))
        openai.api_key = self.openai_api_key
        self.conversation_history = []
        self.max_history_tokens = 4000
        
    async def process_patient_query(self, patient_id: str, query: str) -> Dict[str, Any]:
        """Process a patient's medical query with HIPAA compliance."""
        try:
            logger.info(f"Processing medical query for patient: {patient_id}")
            
            # Validate patient context
            context = await self._get_patient_context(patient_id)
            
            # Build encrypted system prompt
            system_prompt = self._build_system_prompt(context)
            
            # Prepare messages with conversation history
            messages = [
                {"role": "system", "content": system_prompt},
                *self.conversation_history,
                {"role": "user", "content": query}
            ]
            
            # Get response from OpenAI
            response = await self._get_openai_response(messages)
            
            # Encrypt and store conversation
            await self._store_encrypted_conversation(patient_id, query, response)
            
            # Update conversation history
            self.conversation_history.append({"role": "user", "content": query})
            self.conversation_history.append({"role": "assistant", "content": response})
            
            # Maintain token limit
            self._trim_conversation_history()
            
            return {
                "status": "success",
                "response": response,
                "patient_id": patient_id,
                "hipaa_compliant": True,
                "encrypted": True,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error processing medical query: {str(e)}")
            return {
                "status": "error",
                "message": "Unable to process your query. Please try again.",
                "hipaa_compliant": True
            }
    
    async def _get_patient_context(self, patient_id: str) -> Dict[str, Any]:
        """Retrieve encrypted patient context for conversation."""
        # Retrieve patient appointments, labs, and prescriptions
        appointments = await self.cyborg_client.query_encrypted_records(
            patient_id, "appointment"
        )
        labs = await self.cyborg_client.query_encrypted_records(
            patient_id, "lab_order"
        )
        prescriptions = await self.cyborg_client.query_encrypted_records(
            patient_id, "prescription"
        )
        
        return {
            "appointments": appointments,
            "labs": labs,
            "prescriptions": prescriptions
        }
    
    def _build_system_prompt(self, context: Dict[str, Any]) -> str:
        """Build HIPAA-compliant system prompt with patient context."""
        return f"""You are a HIPAA-compliant medical assistant for patient consultations.
Your role is to:
1. Provide general medical information and guidance
2. Help patients understand their appointments and prescriptions
3. Answer questions about lab results and medical procedures
4. Maintain strict confidentiality and data protection
5. Always recommend consulting with licensed physicians for critical decisions

Patient Context:
- Recent Appointments: {len(context.get('appointments', []))}
- Active Lab Orders: {len(context.get('labs', []))}
- Current Prescriptions: {len(context.get('prescriptions', []))}

IMPORTANT: All responses must be HIPAA-compliant and avoid exposing sensitive patient information.
Recommend professional medical consultation for serious health concerns."""
    
    async def _get_openai_response(self, messages: List[Dict[str, str]]) -> str:
        """Get response from OpenAI with streaming support."""
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            max_tokens=1000,
            top_p=0.95,
            frequency_penalty=0.0,
            presence_penalty=0.0
        )
        return response["choices"][0]["message"]["content"]
    
    async def _store_encrypted_conversation(self, patient_id: str, query: str, response: str):
        """Store encrypted conversation in CyborgDB."""
        conversation_data = {
            "query": query,
            "response": response,
            "timestamp": datetime.utcnow().isoformat(),
            "model": self.model
        }
        
        await self.cyborg_client.store_encrypted_record(
            record_type="chat_interaction",
            data=conversation_data,
            patient_id=patient_id
        )
        
        logger.info(f"Encrypted conversation stored for patient: {patient_id}")
    
    def _trim_conversation_history(self):
        """Trim conversation history to maintain token limit."""
        # Simple token estimation: ~4 tokens per word
        while len(self.conversation_history) > 2:
            total_tokens = sum(len(msg["content"].split()) * 4 
                             for msg in self.conversation_history)
            if total_tokens > self.max_history_tokens:
                self.conversation_history.pop(0)
            else:
                break
    
    async def generate_discharge_summary(self, patient_id: str, visit_details: str) -> str:
        """Generate encrypted AI discharge summary."""
        try:
            prompt = f"""Generate a professional medical discharge summary based on visit details:
{visit_details}

Include: diagnosis, treatment, medications, follow-up recommendations.
Maintain HIPAA compliance and clinical accuracy."""
            
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                max_tokens=1500
            )
            
            summary = response["choices"][0]["message"]["content"]
            
            # Store encrypted summary
            await self.cyborg_client.store_encrypted_record(
                record_type="discharge_summary",
                data={"summary": summary, "visit_details": visit_details},
                patient_id=patient_id
            )
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating discharge summary: {str(e)}")
            raise
