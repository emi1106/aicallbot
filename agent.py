# agent.py

import logging
import json
import aiohttp
from openai import AsyncOpenAI
from config import ConfigManager
from prompt import ANALYSIS_PROMPT

logger = logging.getLogger(__name__)

class StefanAgentActions:
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.openai_client = AsyncOpenAI(api_key=self.config_manager.openai_api_key)

    async def summarize_and_analyze_transcript(self, transcript: str) -> dict:
        """Uses GPT-4-Turbo to analyze the transcript and return structured data."""
        if not transcript:
            return {"error": "Transcript was empty."}
        
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[
                    {"role": "system", "content": ANALYSIS_PROMPT.format(transcript=transcript)},
                ],
                response_format={"type": "json_object"},
                temperature=0.2,
            )
            analysis_text = response.choices[0].message.content
            return json.loads(analysis_text)
        except Exception as e:
            logger.error(f"Error during GPT-4 analysis: {e}")
            return {"error": "Failed to analyze transcript with AI."}

    async def send_to_webhook(self, payload: dict):
        """Sends data to the n8n webhook asynchronously."""
        webhook_url = self.config_manager.n8n_webhook_url
        if not webhook_url:
            logger.warning("N8N_WEBHOOK_URL not set. Skipping webhook send.")
            return

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(webhook_url, json=payload, timeout=15) as response:
                    if response.status == 200:
                        logger.info(f"Successfully sent data to webhook for conv_id: {payload.get('conversation_id')}")
                    else:
                        logger.error(f"Webhook error: {response.status} - {await response.text()}")
            except Exception as e:
                logger.error(f"Failed to send to webhook: {e}")

    async def handle_call_end(self, call_ended_event):
        """Main handler for when a call is finished."""
        logger.info(f"Handling end of call: {call_ended_event.conversation_id}")
        
        transcript_text = "\n".join([
            f"{turn.sender}: {turn.text}" for turn in call_ended_event.transcript.events
        ])
        
        # Get AI-powered analysis
        analysis_result = await self.summarize_and_analyze_transcript(transcript_text)
        
        # Prepare the final payload for n8n
        webhook_payload = {
            "conversation_id": call_ended_event.conversation_id,
            "to_number": call_ended_event.to_phone,
            "from_number": call_ended_event.from_phone,
            "call_duration_seconds": call_ended_event.transcript.duration_seconds,
            "transcript": transcript_text,
            **analysis_result # Merge the AI analysis directly
        }

        # Send the comprehensive data to n8n
        await self.send_to_webhook(webhook_payload)