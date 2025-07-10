# Stefan AI Phone Bot

A sophisticated AI-powered phone bot for WEMI that conducts sales conversations in Romanian and analyzes call outcomes.

## Features

- **AI-Powered Conversations**: Uses GPT-4 Turbo for natural Romanian conversations
- **Voice Processing**: Integrates with ElevenLabs for speech synthesis and Deepgram for transcription
- **Call Analysis**: Automatically analyzes call outcomes and lead quality
- **Webhook Integration**: Sends structured data to N8N workflows
- **Telephony Integration**: Uses Twilio for phone system integration

## Project Structure

```
aibot/
├── prompt.py           # AI prompts for conversation and analysis
├── config.py           # Configuration management
├── agent.py            # AI agent actions and post-call processing
├── main.py             # Main application server
├── test_setup.py       # Test script for setup verification
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variables template
├── nixpacks.toml       # Railway deployment configuration
└── README.md           # This file
```

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Environment Configuration

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Fill in all required environment variables:
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `ELEVENLABS_API_KEY`: ElevenLabs API key
   - `ELEVENLABS_VOICE_ID`: Voice ID for Romanian speech
   - `DEEPGRAM_API_KEY`: Deepgram API key for transcription
   - `TWILIO_ACCOUNT_SID`: Twilio account SID
   - `TWILIO_AUTH_TOKEN`: Twilio auth token
   - `TWILIO_PHONE_NUMBER`: Your Twilio phone number
   - `N8N_WEBHOOK_URL`: N8N webhook URL for data processing
   - `BASE_URL`: Your application's base URL
   - `PORT`: Server port (default: 8000)

### 3. Test Setup

Run the test script to verify everything is configured correctly:

```bash
python test_setup.py
```

### 4. Start the Server

```bash
python main.py
```

The server will start on `0.0.0.0:8000` (or your configured port).

## How It Works

1. **Incoming Calls**: Twilio forwards calls to the application
2. **Conversation**: Stefan (AI agent) conducts the conversation in Romanian
3. **Analysis**: After the call ends, the transcript is analyzed using GPT-4
4. **Data Processing**: Results are sent to N8N webhook for further processing

## Call Flow

Stefan follows this conversation pattern:

1. **Opening**: Greets caller and identifies decision-maker
2. **Qualification**: Confirms company and services
3. **Pitch**: Presents WEMI's web development offer (€300 package)
4. **Closing**: Asks for either a 10-minute call or WhatsApp portfolio delivery

## Analysis Output

The system analyzes each call and provides:

- **Outcome**: appointment_booked, whatsapp_sent_agreement, callback_requested, etc.
- **Lead Quality**: high, medium, low
- **Decision Maker**: Name of the person contacted
- **Summary**: Brief call summary
- **Next Steps**: Recommended follow-up actions

## Deployment

### Railway Deployment

The project includes `nixpacks.toml` for Railway deployment:

1. Connect your GitHub repository to Railway
2. Set environment variables in Railway dashboard
3. Deploy automatically

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
python test_setup.py

# Start server
python main.py
```

## API Endpoints

The application automatically sets up Twilio webhook endpoints for:
- Incoming calls
- Call status updates
- Call recordings (if enabled)

## Monitoring

The application includes comprehensive logging for:
- Call events
- Analysis results
- Webhook delivery status
- Error tracking

## Support

For issues or questions about the Stefan AI Phone Bot, please check:
1. Environment variables are correctly set
2. All API keys are valid and have sufficient credits
3. Network connectivity for webhook delivery
4. Twilio phone number configuration

## License

This project is proprietary software for WEMI.
