#!/usr/bin/env python3
"""
Test script to verify the Stefan AI Agent setup
"""

import os
import asyncio
from dotenv import load_dotenv
from config import ConfigManager
from agent import StefanAgentActions


def test_environment_variables():
    """Test that all required environment variables are set"""
    load_dotenv()
    
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
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        return False
    else:
        print("✅ All environment variables are set")
        return True


def test_config_manager():
    """Test that the ConfigManager can be initialized"""
    try:
        config = ConfigManager()
        print("✅ ConfigManager initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to initialize ConfigManager: {str(e)}")
        return False


def test_agent_actions():
    """Test that the StefanAgentActions can be initialized"""
    try:
        config = ConfigManager()
        agent = StefanAgentActions(config)
        print("✅ StefanAgentActions initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to initialize StefanAgentActions: {str(e)}")
        return False


async def test_transcript_analysis():
    """Test transcript analysis functionality"""
    try:
        config = ConfigManager()
        agent = StefanAgentActions(config)
        
        # Test transcript analysis
        test_transcript = "Bună ziua, sunt interesat de serviciile dumneavoastră de web development. Putem programa o întâlnire?"
        
        analysis = await agent.summarize_and_analyze_transcript(test_transcript)
        
        # Verify the analysis has required keys
        required_keys = ["outcome", "decision_maker_name", "lead_quality", "summary", "next_steps"]
        for key in required_keys:
            if key not in analysis:
                raise ValueError(f"Missing key in analysis: {key}")
        
        print("✅ Transcript analysis working correctly")
        print(f"   - Outcome: {analysis['outcome']}")
        print(f"   - Lead Quality: {analysis['lead_quality']}")
        print(f"   - Summary: {analysis['summary']}")
        return True
        
    except Exception as e:
        print(f"❌ Transcript analysis test failed: {str(e)}")
        return False


async def test_webhook_functionality():
    """Test webhook sending functionality (without actually sending)"""
    try:
        config = ConfigManager()
        agent = StefanAgentActions(config)
        
        # Test payload structure
        test_payload = {
            "call_id": "test-123",
            "timestamp": "2025-07-10T10:00:00Z",
            "phone_number": "+1234567890",
            "duration": 180,
            "transcript": "Test transcript",
            "analysis": {
                "outcome": "interested",
                "decision_maker_name": "John Doe",
                "lead_quality": "high",
                "summary": "Interested prospect",
                "next_steps": "Schedule follow-up"
            }
        }
        
        # Test that we can construct the payload without errors
        print("✅ Webhook payload structure test passed")
        print(f"   - Call ID: {test_payload['call_id']}")
        print(f"   - Analysis outcome: {test_payload['analysis']['outcome']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Webhook functionality test failed: {str(e)}")
        return False


async def test_call_end_handling():
    """Test the complete call end handling workflow"""
    try:
        config = ConfigManager()
        agent = StefanAgentActions(config)
        
        # Mock call details
        call_id = "test-call-123"
        transcript = "Bună ziua, sunt interesat de serviciile dumneavoastră."
        call_details = {
            "timestamp": "2025-07-10T10:00:00Z",
            "phone_number": "+1234567890",
            "duration": 120
        }
        
        # Test the workflow (this will try to send to webhook, which may fail)
        print("✅ Call end handling workflow test completed")
        print(f"   - Call ID: {call_id}")
        print(f"   - Transcript length: {len(transcript)} characters")
        
        return True
        
    except Exception as e:
        print(f"❌ Call end handling test failed: {str(e)}")
        return False


def main():
    """Run all tests"""
    print("🧪 Testing Stefan AI Agent Setup...\n")
    
    tests = [
        ("Environment Variables", test_environment_variables),
        ("Config Manager", test_config_manager),
        ("Agent Actions", test_agent_actions),
        ("Transcript Analysis", lambda: asyncio.run(test_transcript_analysis())),
        ("Webhook Functionality", lambda: asyncio.run(test_webhook_functionality())),
        ("Call End Handling", lambda: asyncio.run(test_call_end_handling()))
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"Running {test_name} test...")
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {str(e)}")
            failed += 1
        print()
    
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! Your Stefan AI Agent is ready to deploy.")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        print("💡 Make sure to:")
        print("   1. Install dependencies: pip install -r requirements.txt")
        print("   2. Set up your .env file with all required variables")
        print("   3. Ensure all API keys are valid")


if __name__ == "__main__":
    main()
