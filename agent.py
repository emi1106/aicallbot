import json
import asyncio
import aiohttp
from openai import AsyncOpenAI
from prompt import ANALYSIS_PROMPT


class StefanAgentActions:
    """Stefan AI Agent Actions for handling post-call logic"""
    
    def __init__(self, config_manager):
        """Initialize with config manager"""
        self.config = config_manager
        self.openai_client = AsyncOpenAI(api_key=self.config.openai_api_key)
    
    async def summarize_and_analyze_transcript(self, transcript: str) -> dict:
        """
        Analyze the call transcript using OpenAI GPT-4 Turbo
        
        Args:
            transcript: The conversation transcript to analyze
            
        Returns:
            dict: Structured analysis with outcome, lead quality, etc.
        """
        try:
            prompt = ANALYSIS_PROMPT.format(transcript=transcript)
            
            response = await self.openai_client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[
                    {"role": "system", "content": "You are a sales call analyst. Respond only with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.3,
                max_tokens=500
            )
            
            analysis = json.loads(response.choices[0].message.content)
            
            # Validate required keys
            required_keys = ["outcome", "decision_maker_name", "lead_quality", "summary", "next_steps"]
            for key in required_keys:
                if key not in analysis:
                    analysis[key] = "unknown"
            
            return analysis
            
        except Exception as e:
            print(f"Error analyzing transcript: {str(e)}")
            return {
                "outcome": "inconclusive",
                "decision_maker_name": "unknown",
                "lead_quality": "low",
                "summary": "Analysis failed due to technical error",
                "next_steps": "Manual review required"
            }
    
    async def send_to_webhook(self, payload: dict) -> bool:
        """
        Send the analyzed call data to N8N webhook
        
        Args:
            payload: The data to send to the webhook
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.config.webhook_url,
                    json=payload,
                    headers={"Content-Type": "application/json"},
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        print(f"Successfully sent webhook: {response.status}")
                        return True
                    else:
                        print(f"Webhook failed with status: {response.status}")
                        return False
                        
        except Exception as e:
            print(f"Error sending webhook: {str(e)}")
            return False
    
    async def handle_call_end(self, call_id: str, transcript: str, call_details: dict = None) -> None:
        """
        Main orchestration method for handling call end events
        
        Args:
            call_id: Unique identifier for the call
            transcript: The full conversation transcript
            call_details: Additional call metadata
        """
        try:
            print(f"Processing call end for call ID: {call_id}")
            
            # Step 1: Analyze the transcript
            analysis = await self.summarize_and_analyze_transcript(transcript)
            
            # Step 2: Build the webhook payload
            payload = {
                "call_id": call_id,
                "timestamp": call_details.get("timestamp") if call_details else None,
                "phone_number": call_details.get("phone_number") if call_details else None,
                "duration": call_details.get("duration") if call_details else None,
                "transcript": transcript,
                "analysis": analysis
            }
            
            # Step 3: Send to webhook
            webhook_success = await self.send_to_webhook(payload)
            
            if webhook_success:
                print(f"Call {call_id} processed successfully")
            else:
                print(f"Failed to send webhook for call {call_id}")
                
        except Exception as e:
            print(f"Error handling call end for {call_id}: {str(e)}")
    
    def extract_call_details(self, call_object) -> dict:
        """
        Extract relevant details from the call object
        
        Args:
            call_object: The Vocode call object
            
        Returns:
            dict: Extracted call details
        """
        try:
            return {
                "timestamp": getattr(call_object, 'created_at', None),
                "phone_number": getattr(call_object, 'from_phone', None),
                "duration": getattr(call_object, 'duration', None),
                "status": getattr(call_object, 'status', None)
            }
        except Exception as e:
            print(f"Error extracting call details: {str(e)}")
            return {}
