import asyncio
import logging
from vocode.streaming.telephony.server.base import TelephonyServer
from vocode.streaming.models.events import EventType
from config import ConfigManager
from agent import StefanAgentActions

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StefanTelephonyServer:
    """Main telephony server for Stefan AI phone bot"""
    
    def __init__(self):
        """Initialize the server with configuration and agent actions"""
        self.config = ConfigManager()
        self.agent_actions = StefanAgentActions(self.config)
        self.server = self._create_server()
    
    def _create_server(self) -> TelephonyServer:
        """Create and configure the TelephonyServer"""
        server = TelephonyServer(
            agent_config=self.config.agent_config,
            transcriber_config=self.config.transcriber_config,
            synthesizer_config=self.config.synthesizer_config,
            twilio_config=self.config.twilio_config,
            base_url=self.config.base_url,
            port=self.config.port
        )
        
        # Register event handlers
        server.register_event_handler(
            EventType.CALL_ENDED,
            self._handle_call_ended
        )
        
        return server
    
    async def _handle_call_ended(self, call):
        """
        Handle call ended events
        
        Args:
            call: The Vocode call object
        """
        try:
            logger.info(f"Call ended: {call.id}")
            
            # Extract call details
            call_details = self.agent_actions.extract_call_details(call)
            
            # Get transcript
            transcript = getattr(call, 'transcript', '') or ''
            
            if not transcript:
                logger.warning(f"No transcript available for call {call.id}")
                transcript = "No transcript available"
            
            # Handle the call end processing
            await self.agent_actions.handle_call_end(
                call_id=call.id,
                transcript=transcript,
                call_details=call_details
            )
            
        except Exception as e:
            logger.error(f"Error handling call ended event: {str(e)}")
    
    async def start(self):
        """Start the telephony server"""
        logger.info("Starting Stefan AI Telephony Server...")
        logger.info(f"Server will listen on 0.0.0.0:{self.config.port}")
        
        try:
            await self.server.run(host="0.0.0.0", port=self.config.port)
        except Exception as e:
            logger.error(f"Error starting server: {str(e)}")
            raise


async def main():
    """Main application entry point"""
    try:
        server = StefanTelephonyServer()
        await server.start()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
