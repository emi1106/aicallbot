import os
from dotenv import load_dotenv
from prompt import LOVITURA_DE_GRATIE_PROMPT


class ConfigManager:
    """Configuration manager for the Stefan AI phone bot"""
    
    def __init__(self):
        load_dotenv()
        self._validate_env_vars()
    
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
    
    @property
    def openai_api_key(self):
        """Get the OpenAI API key"""
        return os.getenv('OPENAI_API_KEY')
    
    @property
    def elevenlabs_api_key(self):
        """Get the ElevenLabs API key"""
        return os.getenv('ELEVENLABS_API_KEY')
    
    @property
    def elevenlabs_voice_id(self):
        """Get the ElevenLabs voice ID"""
        return os.getenv('ELEVENLABS_VOICE_ID')
    
    @property
    def deepgram_api_key(self):
        """Get the Deepgram API key"""
        return os.getenv('DEEPGRAM_API_KEY')
    
    @property
    def twilio_account_sid(self):
        """Get the Twilio Account SID"""
        return os.getenv('TWILIO_ACCOUNT_SID')
    
    @property
    def twilio_auth_token(self):
        """Get the Twilio Auth Token"""
        return os.getenv('TWILIO_AUTH_TOKEN')
    
    @property
    def twilio_phone_number(self):
        """Get the Twilio Phone Number"""
        return os.getenv('TWILIO_PHONE_NUMBER')
    
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
    def agent_prompt(self):
        """Get the agent prompt"""
        return LOVITURA_DE_GRATIE_PROMPT
