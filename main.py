import asyncio
import logging
from fastapi import FastAPI, Request, Response
from fastapi.responses import PlainTextResponse
import uvicorn
from twilio.twiml.voice_response import VoiceResponse
from config import ConfigManager
from agent import StefanAgentActions

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Stefan AI Phone Bot")

# Global variables
config = None
agent_actions = None

@app.on_event("startup")
async def startup_event():
    """Initialize configuration and agent on startup"""
    global config, agent_actions
    try:
        config = ConfigManager()
        agent_actions = StefanAgentActions(config)
        logger.info("Stefan AI Phone Bot initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize: {str(e)}")
        raise

@app.get("/")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Stefan AI Phone Bot is running"}

@app.post("/webhook/call")
async def handle_incoming_call(request: Request):
    """Handle incoming Twilio calls"""
    try:
        # Get form data from Twilio
        form_data = await request.form()
        call_sid = form_data.get("CallSid")
        from_number = form_data.get("From")
        to_number = form_data.get("To")
        
        logger.info(f"Incoming call: {call_sid} from {from_number} to {to_number}")
        
        # Create TwiML response
        response = VoiceResponse()
        
        # Start the conversation
        response.say(
            "Bună ziua! Sunt Ștefan de la WEMI. Vă mulțumesc că ați răspuns. Cu cine vorbesc?",
            voice="alice",
            language="ro-RO"
        )
        
        # Set up recording and continue to conversation handler
        response.record(
            action="/webhook/recording",
            method="POST",
            max_length=300,  # 5 minutes max
            play_beep=False,
            transcribe=True,
            transcribe_callback="/webhook/transcription"
        )
        
        return PlainTextResponse(str(response), media_type="application/xml")
        
    except Exception as e:
        logger.error(f"Error handling incoming call: {str(e)}")
        # Return a simple error response
        response = VoiceResponse()
        response.say("Ne pare rău, a apărut o problemă tehnică. Vă rugăm să sunați din nou.", 
                    voice="alice", language="ro-RO")
        return PlainTextResponse(str(response), media_type="application/xml")

@app.post("/webhook/recording")
async def handle_recording(request: Request):
    """Handle call recording completion"""
    try:
        form_data = await request.form()
        call_sid = form_data.get("CallSid")
        recording_url = form_data.get("RecordingUrl")
        
        logger.info(f"Recording completed for call {call_sid}: {recording_url}")
        
        # Simple response to end the call
        response = VoiceResponse()
        response.say("Mulțumesc pentru timpul acordat. O zi frumoasă!", 
                    voice="alice", language="ro-RO")
        response.hangup()
        
        return PlainTextResponse(str(response), media_type="application/xml")
        
    except Exception as e:
        logger.error(f"Error handling recording: {str(e)}")
        response = VoiceResponse()
        response.hangup()
        return PlainTextResponse(str(response), media_type="application/xml")

@app.post("/webhook/transcription")
async def handle_transcription(request: Request):
    """Handle call transcription from Twilio"""
    try:
        form_data = await request.form()
        call_sid = form_data.get("CallSid")
        transcription_text = form_data.get("TranscriptionText", "")
        
        logger.info(f"Transcription received for call {call_sid}")
        
        if transcription_text and agent_actions:
            # Process the transcription
            await agent_actions.handle_call_end(
                call_id=call_sid,
                transcript=transcription_text,
                call_details={
                    "timestamp": form_data.get("DateCreated"),
                    "phone_number": form_data.get("From"),
                    "duration": form_data.get("CallDuration")
                }
            )
        
        return {"status": "processed"}
        
    except Exception as e:
        logger.error(f"Error handling transcription: {str(e)}")
        return {"status": "error", "message": str(e)}

@app.post("/webhook/status")
async def handle_call_status(request: Request):
    """Handle call status updates from Twilio"""
    try:
        form_data = await request.form()
        call_sid = form_data.get("CallSid")
        call_status = form_data.get("CallStatus")
        
        logger.info(f"Call {call_sid} status: {call_status}")
        
        if call_status == "completed":
            logger.info(f"Call {call_sid} completed")
        
        return {"status": "received"}
        
    except Exception as e:
        logger.error(f"Error handling call status: {str(e)}")
        return {"status": "error"}

if __name__ == "__main__":
    port = int(config.port if config else 8000)
    logger.info(f"Starting Stefan AI Phone Bot on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
