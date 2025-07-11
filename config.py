# config.py

import os
from dotenv import load_dotenv
from vocode.streaming.models.agent import ChatGPTAgentConfig
from vocode.streaming.models.synthesizer import ElevenLabsSynthesizerConfig
from vocode.streaming.models.transcriber import DeepgramTranscriberConfig
from vocode.streaming.models.telephony import TwilioConfig
from vocode.streaming.models.message import BaseMessage
from prompt import LOVITURA_DE_GRATIE_PROMPT

class ConfigManager:
    def __init__(self):
        load_dotenv()
        
        # Base URLs and Keys
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.n8n_webhook_url = os.getenv("N8N_WEBHOOK_URL")
        self.base_url = os.getenv("BASE_URL")

        # Agent Config (The "Brain")
        self.agent_config = ChatGPTAgentConfig(
        initial_message=BaseMessage(text="Bună ziua, numele meu este Ștefania de la WEMI, ne ocupam cu dezvoltarea web. Cu cine vorbesc?"),
        prompt_preamble=LOVITURA_DE_GRATIE_PROMPT,
            generate_responses=True,
            model_name="gpt-4o", # Use the fast and smart "omni" model
            temperature=0.7,
            end_conversation_on_goodbye=True,
            send_filler_audio=True,
            allowed_idle_time_seconds=30,
        )

        # Transcriber Config (The "Ears")
        self.transcriber_config = DeepgramTranscriberConfig(
            language="ro",
            model="nova-2",
            api_key=os.getenv("DEEPGRAM_API_KEY"),
            # Add the following required parameters for telephony
            sampling_rate=8000,
            audio_encoding="mulaw",
            chunk_size=2048,
        )

        # Synthesizer Config (The "Mouth")
        self.synthesizer_config = ElevenLabsSynthesizerConfig(
            api_key=os.getenv("ELEVENLABS_API_KEY"),
            voice_id=os.getenv("ELEVENLABS_VOICE_ID"),
            stability=0.7,
            similarity_boost=0.75,
            model_id="eleven_multilingual_v2",
            optimize_streaming_latency=1,
        )

        # Twilio Config (The "Phone Line")
        self.twilio_config = TwilioConfig(
            account_sid=os.getenv("TWILIO_ACCOUNT_SID"),
            auth_token=os.getenv("TWILIO_AUTH_TOKEN"),
            phone_number=os.getenv("TWILIO_PHONE_NUMBER"),
        )