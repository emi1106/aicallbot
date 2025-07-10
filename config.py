import os
from dotenv import load_dotenv
from vocode.streaming.models.agent import ChatGPTAgentConfig
from vocode.streaming.models.transcriber import DeepgramTranscriberConfig
from vocode.streaming.models.synthesizer import ElevenLabsSynthesizerConfig
from vocode.streaming.telephony.config_manager.redis_config_manager import RedisConfigManager
from vocode.streaming.telephony.server.base import TelephonyServer
from vocode.streaming.telephony.conversation.call import Call
from vocode.streaming.models.telephony import TwilioConfig
from prompt import LOVITURA_DE_GRATIE_PROMPT


class ConfigManager:
    """Configuration manager for the Stefan AI phone bot"""
    
    def __init__(self):
        load_dotenv()
        self._validate_env_vars()
        self._setup_configs()
    
    def _validate_env_vars(self):
        """Validate that all required environment variables are set"""
        required_vars = [
            'OPENAI_API_KEY',
            'ELEVENLABS_API_KEY',
            'ELEVENLABS_VOICE_ID',
            'DEEPGRAM_API_KEY',
            'TWILIO_ACCOUNT_SID',
            'TWILIO_AUTH_TOKEN',
            'TWILIO_PHONE_NUMBER',
            'N8N_WEBHOOK_URL',
            'BASE_URL',
            'PORT'
        ]
        
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    def _setup_configs(self):
        """Setup all Vocode configuration objects"""
        # ChatGPT Agent Configuration
        self.agent_config = ChatGPTAgentConfig(
            model_name="gpt-4-turbo",
            prompt_preamble=LOVITURA_DE_GRATIE_PROMPT,
            temperature=0.7,
            max_tokens=1000,
            openai_api_key=os.getenv('OPENAI_API_KEY')
        )
        
        # Deepgram Transcriber Configuration
        self.transcriber_config = DeepgramTranscriberConfig(
            model="nova-2",
            language="ro",
            api_key=os.getenv('DEEPGRAM_API_KEY')
        )
        
        # ElevenLabs Synthesizer Configuration
        self.synthesizer_config = ElevenLabsSynthesizerConfig(
            voice_id=os.getenv('ELEVENLABS_VOICE_ID'),
            api_key=os.getenv('ELEVENLABS_API_KEY'),
            model_id="eleven_multilingual_v2"
        )
        
        # Twilio Configuration
        self.twilio_config = TwilioConfig(
            account_sid=os.getenv('TWILIO_ACCOUNT_SID'),
            auth_token=os.getenv('TWILIO_AUTH_TOKEN'),
            phone_number=os.getenv('TWILIO_PHONE_NUMBER')
        )
    
    @property
    def webhook_url(self):
        """Get the N8N webhook URL"""
        return os.getenv('N8N_WEBHOOK_URL')
    
    @property
    def base_url(self):
        """Get the base URL for the application"""
        return os.getenv('BASE_URL')
    
    @property
    def port(self):
        """Get the port for the application"""
        return int(os.getenv('PORT', 8000))
    
    @property
    def openai_api_key(self):
        """Get the OpenAI API key"""
        return os.getenv('OPENAI_API_KEY')
