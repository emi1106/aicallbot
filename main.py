# main.py

import logging
import os
from vocode.streaming.telephony.server.base import TelephonyServer
from vocode.streaming.models.events import EventType
from vocode.streaming.models.telephony import TwilioCallConfig
from config import ConfigManager
from agent import StefanAgentActions

# Configure basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Main function to setup and run the telephony server."""
    try:
        # Initialize configurations and agent actions
        config_manager = ConfigManager()
        agent_actions = StefanAgentActions(config_manager)

        # Create a single, pre-configured call config to speed up connections
        call_config = TwilioCallConfig(
            twilio_config=config_manager.twilio_config,
            agent_config=config_manager.agent_config,
            transcriber_config=config_manager.transcriber_config,
            synthesizer_config=config_manager.synthesizer_config,
            inbound_url="/inbound_call",
        )

        # Create the Telephony Server with the pre-configured config
        telephony_server = TelephonyServer(
            base_url=config_manager.base_url,
            inbound_call_config=call_config,
        )

        # Register the event handler for when a call ends
        telephony_server.events_manager.register_handler(
            EventType.CALL_ENDED, agent_actions.handle_call_end
        )

        # Get the port from environment variables or default to 8000
        port = int(os.getenv("PORT", 8080))
        
        logger.info(f"Starting Stefan AI Agent Server on port {port}...")
        logger.info(f"Public URL should be configured as: {config_manager.base_url}")
        logger.info(f"Webhook URL for n8n: {config_manager.n8n_webhook_url}")

        # Run the server with proxy headers enabled for correct Twilio validation on Railway
        telephony_server.run(
            host="0.0.0.0",
            port=port,
            proxy_headers=True,
            forwarded_allow_ips="*"
        )

    except Exception as e:
        logger.error(f"Failed to start server: {e}", exc_info=True)

if __name__ == "__main__":
    main()