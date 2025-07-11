import asyncio
import logging
from fastapi import FastAPI, Request, Response
from fastapi.responses import PlainTextResponse
import uvicorn
from twilio.twiml.voice_response import VoiceResponse, Gather
from twilio.rest import Client as TwilioClient
import aiohttp
import json
from openai import AsyncOpenAI
from elevenlabs import ElevenLabs
import tempfile
import os
from config import ConfigManager
from agent import StefanAgentActions
from prompt import LOVITURA_DE_GRATIE_PROMPT

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Stefan AI Phone Bot")

# Global variables
config = None
agent_actions = None
openai_client = None
elevenlabs_client = None
twilio_client = None

@app.on_event("startup")
async def startup_event():
    """Initialize configuration and services on startup"""
    global config, agent_actions, openai_client, elevenlabs_client, twilio_client
    try:
        config = ConfigManager()
        agent_actions = StefanAgentActions(config)
        openai_client = AsyncOpenAI(api_key=config.openai_api_key)
        elevenlabs_client = ElevenLabs(api_key=config.elevenlabs_api_key)
        twilio_client = TwilioClient(config.twilio_account_sid, config.twilio_auth_token)
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
        
        # Generate AI greeting using OpenAI
        ai_greeting = await generate_ai_response(
            "Start the conversation with a Romanian greeting as Stefan from WEMI.",
            conversation_history=[]
        )
        
        # Convert AI response to speech using ElevenLabs
        audio_url = await text_to_speech(ai_greeting)
        
        if audio_url:
            response.play(audio_url)
        else:
            # Fallback to Twilio TTS
            response.say(ai_greeting, voice="alice", language="ro-RO")
        
        # Gather user input
        gather = Gather(
            input="speech",
            action="/webhook/process_speech",
            method="POST",
            speech_timeout="3",
            language="ro-RO",
            enhanced=True
        )
        gather.say("", voice="alice", language="ro-RO")  # Silent pause for input
        response.append(gather)
        
        # Fallback if no input
        response.say("Nu v-am auzit. Vă rog să încercați din nou.", voice="alice", language="ro-RO")
        response.redirect("/webhook/call")
        
        return PlainTextResponse(str(response), media_type="application/xml")
        
    except Exception as e:
        logger.error(f"Error handling incoming call: {str(e)}")
        response = VoiceResponse()
        response.say("Ne pare rău, a apărut o problemă tehnică. Vă rugăm să sunați din nou.", 
                    voice="alice", language="ro-RO")
        return PlainTextResponse(str(response), media_type="application/xml")

@app.post("/webhook/process_speech")
async def process_speech(request: Request):
    """Process speech input from user"""
    try:
        form_data = await request.form()
        call_sid = form_data.get("CallSid")
        speech_result = form_data.get("SpeechResult", "")
        
        logger.info(f"Speech received for call {call_sid}: {speech_result}")
        
        if not speech_result:
            response = VoiceResponse()
            response.say("Nu v-am înțeles. Puteți repeta, vă rog?", voice="alice", language="ro-RO")
            response.redirect("/webhook/call")
            return PlainTextResponse(str(response), media_type="application/xml")
        
        # Get conversation history (you might want to store this in Redis/database)
        conversation_history = get_conversation_history(call_sid)
        conversation_history.append({"role": "user", "content": speech_result})
        
        # Generate AI response
        ai_response = await generate_ai_response(speech_result, conversation_history)
        
        # Update conversation history
        conversation_history.append({"role": "assistant", "content": ai_response})
        store_conversation_history(call_sid, conversation_history)
        
        # Convert to speech
        audio_url = await text_to_speech(ai_response)
        
        response = VoiceResponse()
        
        if audio_url:
            response.play(audio_url)
        else:
            response.say(ai_response, voice="alice", language="ro-RO")
        
        # Check if conversation should continue
        if should_end_conversation(ai_response):
            response.say("Mulțumesc pentru timpul acordat. O zi frumoasă!", voice="alice", language="ro-RO")
            response.hangup()
        else:
            # Continue conversation
            gather = Gather(
                input="speech",
                action="/webhook/process_speech",
                method="POST",
                speech_timeout="3",
                language="ro-RO",
                enhanced=True
            )
            gather.say("", voice="alice", language="ro-RO")
            response.append(gather)
            
            response.say("Nu v-am auzit. Continuăm?", voice="alice", language="ro-RO")
            response.redirect("/webhook/process_speech")
        
        return PlainTextResponse(str(response), media_type="application/xml")
        
    except Exception as e:
        logger.error(f"Error processing speech: {str(e)}")
        response = VoiceResponse()
        response.say("Ne pare rău, a apărut o problemă. Vom încheia convorbirea.", voice="alice", language="ro-RO")
        response.hangup()
        return PlainTextResponse(str(response), media_type="application/xml")

@app.post("/webhook/call_ended")
async def handle_call_ended(request: Request):
    """Handle call completion"""
    try:
        form_data = await request.form()
        call_sid = form_data.get("CallSid")
        call_duration = form_data.get("CallDuration")
        from_number = form_data.get("From")
        
        logger.info(f"Call ended: {call_sid}, duration: {call_duration}")
        
        # Get full conversation
        conversation_history = get_conversation_history(call_sid)
        full_transcript = "\n".join([
            f"{'Stefan' if msg['role'] == 'assistant' else 'Caller'}: {msg['content']}"
            for msg in conversation_history
        ])
        
        # Process with agent actions
        if agent_actions and full_transcript:
            await agent_actions.handle_call_end(
                call_id=call_sid,
                transcript=full_transcript,
                call_details={
                    "timestamp": form_data.get("Timestamp"),
                    "phone_number": from_number,
                    "duration": call_duration
                }
            )
        
        # Clean up conversation history
        cleanup_conversation_history(call_sid)
        
        return {"status": "processed"}
        
    except Exception as e:
        logger.error(f"Error handling call end: {str(e)}")
        return {"status": "error"}

async def generate_ai_response(user_input: str, conversation_history: list) -> str:
    """Generate AI response using OpenAI"""
    try:
        messages = [
            {"role": "system", "content": LOVITURA_DE_GRATIE_PROMPT},
        ]
        messages.extend(conversation_history[-10:])  # Keep last 10 messages for context
        
        if user_input:
            messages.append({"role": "user", "content": user_input})
        
        response = await openai_client.chat.completions.create(
            model="gpt-4-turbo",
            messages=messages,
            temperature=0.7,
            max_tokens=200  # Keep responses concise for phone calls
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        logger.error(f"Error generating AI response: {str(e)}")
        return "Ne pare rău, am o problemă tehnică. Putem continua?"

async def text_to_speech(text: str) -> str:
    """Convert text to speech using ElevenLabs"""
    try:
        # Generate speech
        audio = elevenlabs_client.generate(
            text=text,
            voice=config.elevenlabs_voice_id,
            model="eleven_multilingual_v2"
        )
        
        # Save to temporary file and upload to accessible URL
        # Note: In production, you'd want to use cloud storage
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        for chunk in audio:
            temp_file.write(chunk)
        temp_file.close()
        
        # For now, return None to use Twilio TTS as fallback
        # In production, upload temp_file.name to cloud storage and return URL
        os.unlink(temp_file.name)
        return None
        
    except Exception as e:
        logger.error(f"Error with text-to-speech: {str(e)}")
        return None

def get_conversation_history(call_sid: str) -> list:
    """Get conversation history for a call (in-memory for now)"""
    # In production, use Redis or database
    if not hasattr(app.state, 'conversations'):
        app.state.conversations = {}
    return app.state.conversations.get(call_sid, [])

def store_conversation_history(call_sid: str, history: list):
    """Store conversation history for a call"""
    if not hasattr(app.state, 'conversations'):
        app.state.conversations = {}
    app.state.conversations[call_sid] = history

def cleanup_conversation_history(call_sid: str):
    """Clean up conversation history after call ends"""
    if hasattr(app.state, 'conversations') and call_sid in app.state.conversations:
        del app.state.conversations[call_sid]

def should_end_conversation(response: str) -> bool:
    """Determine if conversation should end based on AI response"""
    end_keywords = ["mulțumesc", "la revedere", "o zi", "pa pa", "tchau"]
    return any(keyword in response.lower() for keyword in end_keywords)

if __name__ == "__main__":
    port = int(os.getenv('PORT', 8000))
    logger.info(f"Starting Stefan AI Phone Bot on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
