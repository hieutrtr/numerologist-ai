"""
Manual Test Script for Pipecat Voice AI Bot

This script creates a Daily.co room and spawns the Pipecat bot for manual testing
of the voice conversation pipeline.

Prerequisites:
    - All voice service API keys configured in backend/.env:
      * DAILY_API_KEY (Daily.co WebRTC)
      * DEEPGRAM_API_KEY (speech-to-text)
      * AZURE_OPENAI_API_KEY (language model)
      * AZURE_OPENAI_ENDPOINT (Azure endpoint URL)
      * ELEVENLABS_API_KEY (text-to-speech)

Usage:
    1. Ensure backend/.env has all required API keys
    2. Run from backend directory: python scripts/test_pipecat_bot.py
    3. Script will print a Daily.co room URL
    4. Open URL in Chrome/Firefox (enable microphone when prompted)
    5. Speak into microphone: "Hello"
    6. Bot should respond with greeting via audio
    7. Press Ctrl+C to stop bot and exit

Testing Checklist:
    [ ] Bot joins room automatically
    [ ] User speech is transcribed (observable in pipeline logs)
    [ ] AI generates relevant response
    [ ] Response is spoken naturally
    [ ] End-to-end latency < 1 second
    [ ] Bot handles multiple conversation turns
    [ ] Bot recovers gracefully from audio interruptions

Troubleshooting:
    - If bot doesn't join: Check DAILY_API_KEY is correct
    - If no transcription: Check DEEPGRAM_API_KEY and microphone permissions
    - If no AI response: Check AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT
    - If no audio output: Check ELEVENLABS_API_KEY
    - If high latency: Check network connection and service status
"""

import asyncio
import sys
import os

# Add backend to path for imports
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

from src.services import daily_service
from src.voice_pipeline import pipecat_bot


async def test_pipecat_bot():
    """
    Create Daily.co room and run Pipecat bot for manual testing.

    Steps:
        1. Clean up any existing test room from previous runs
        2. Create Daily.co room with test conversation ID
        3. Print room URL for manual browser access
        4. Spawn bot in room
        5. Bot runs until Ctrl+C or room closes
        6. Clean up room on exit

    Returns:
        None

    Raises:
        ValueError: If API keys are not configured
        Exception: If room creation or bot initialization fails
    """
    room_info = None

    try:
        print("=" * 70)
        print("🤖 Pipecat Voice AI Bot - Manual Test")
        print("=" * 70)
        print()

        # Clean up any existing test room from previous runs
        print("🧹 Cleaning up any existing test rooms...")
        conversation_id = "manual-test-pipecat-bot-1"
        room_name = f"numerologist-{conversation_id}"
        await daily_service.delete_room(room_name)
        print("✅ Cleanup completed")
        print()

        # Create Daily.co room
        print("📞 Creating Daily.co room...")
        room_info = await daily_service.create_room(conversation_id)

        print("✅ Room created successfully!")
        print()
        print("=" * 70)
        print("📍 Room Details:")
        print("=" * 70)
        print(f"Room URL:  {room_info['room_url']}")
        print(f"Room Name: {room_info['room_name']}")
        print()
        print("🌐 Open the Room URL in your browser to test:")
        print(f"   {room_info['room_url']}")
        print()
        print("=" * 70)
        print("🎤 Testing Instructions:")
        print("=" * 70)
        print("1. Click the Room URL above to open in browser")
        print("2. Allow microphone access when prompted")
        print("3. Wait for bot to join (you'll see 'Numerology AI Bot' in participants)")
        print("4. Speak clearly into your microphone: 'Hello'")
        print("5. Listen for bot's audio response")
        print("6. Try a few conversation turns")
        print("7. Press Ctrl+C here to stop the bot")
        print()
        print("=" * 70)
        print()

        # Start bot
        print("🚀 Starting Pipecat bot...")
        print("   (Bot is now joining the room and initializing services)")
        print()

        # Run bot (blocking call until stopped)
        await pipecat_bot.run_bot(room_info["room_url"], room_info["meeting_token"])

    except ValueError as e:
        # Configuration error (missing API keys)
        print()
        print("=" * 70)
        print("❌ Configuration Error")
        print("=" * 70)
        print(str(e))
        print()
        return 1

    except KeyboardInterrupt:
        # User pressed Ctrl+C
        print()
        print("=" * 70)
        print("🛑 Test stopped by user (Ctrl+C)")
        print("=" * 70)
        print()

    except Exception as e:
        # Other errors
        print()
        print("=" * 70)
        print(f"❌ Error: {type(e).__name__}")
        print("=" * 70)
        print(str(e))
        print()
        import traceback
        traceback.print_exc()
        return 1

    finally:
        # Always clean up the room on exit (success, error, or Ctrl+C)
        if room_info:
            print()
            print("🧹 Cleaning up test room...")
            deleted = await daily_service.delete_room(room_info["room_name"])
            if deleted:
                print("✅ Room deleted successfully")
            else:
                print("⚠️  Room cleanup failed or already deleted")
        print()

    print()
    print("=" * 70)
    print("✅ Test completed successfully")
    print("=" * 70)
    return 0


def main():
    """
    Main entry point for test script.

    Runs async test function and returns exit code.
    """
    try:
        exit_code = asyncio.run(test_pipecat_bot())
        sys.exit(exit_code)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
