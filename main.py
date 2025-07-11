# main.py (Final Robust Version)

import logging
import os
from vocode.streaming.telephony.server.base import TelephonyServer
from vocode.streaming.models.events import EventType
from config import ConfigManager
from agent import StefanAgentActions

# Configure basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Main function to setup and run the telephony server."""
    try:
        config_manager = ConfigManager()
        agent_actions = StefanAgentActions(config_manager)

        telephony_server = TelephonyServer(
            base_url=config_manager.base_url,
            inbound_call_configs=[
                {
                    "url": "/inbound_call",
                    "agent_config": config_manager.agent_config,
                    "twilio_config": config_manager.twilio_config,
                    "transcriber_config": config_manager.transcriber_config,
                    "synthesizer_config": config_manager.synthesizer_config,
                }
            ],
            config_manager=config_manager,
        )

        telephony_server.events_manager.register_handler(
            EventType.CALL_ENDED, agent_actions.handle_call_end
        )

        port = int(os.getenv("PORT", 8000))
        
        logger.info(f"Starting Stefan AI Agent Server on port {port}...")

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