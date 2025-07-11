# AI Phone Bot - "Ștefan"

This project is a sophisticated AI phone bot designed to make outbound calls to businesses based on a provided list. It uses a variety of modern AI and communication technologies to hold a natural, low-latency conversation.

## Core Technologies
- **Framework:** Vocode (for real-time streaming telephony)
- **Telephony:** Twilio
- **AI Brain:** OpenAI (GPT-4o)
- **Speech-to-Text:** Deepgram
- **Text-to-Speech:** ElevenLabs
- **Orchestration:** n8n.io
- **Hosting:** Railway.app

## How it Works
1.  An **n8n** workflow reads a list of leads from a Google Sheet.
2.  It triggers **Twilio** to place an outbound call.
3.  Twilio connects the call to this Python application, which is hosted on **Railway**.
4.  The application uses **Vocode** to manage the real-time audio stream, converting speech to text with **Deepgram**, getting intelligent responses from **OpenAI**, and converting the responses back to speech with **ElevenLabs**.
5.  After the call ends, the application analyzes the transcript and sends a summary to a second **n8n** workflow via a webhook.
6.  The second n8n workflow updates the Google Sheet with the call results.

## Setup
1.  Clone this repository.
2.  Install dependencies: `pip install -r requirements.txt`.
3.  Create a `.env` file by copying `.env.example` and fill in all the required API keys and URLs.
4.  Deploy the application to a service like Railway.
5.  Set up the two required n8n workflows.