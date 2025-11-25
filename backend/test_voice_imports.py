#!/usr/bin/env python3
"""
Voice Pipeline Import Verification Script
==========================================

This script verifies that all voice pipeline dependencies can be imported successfully.
It ensures that Pipecat-ai and all required voice service SDKs are properly installed
and accessible in the Python environment.

Run with: uv run python test_voice_imports.py
"""


def test_pipecat_core_imports():
    """Test core Pipecat-ai framework imports"""
    try:
        from pipecat.pipeline.pipeline import Pipeline
        from pipecat.pipeline.runner import PipelineRunner
        print("✓ Pipecat-ai core imports successful")
        return True
    except ImportError as e:
        print(f"✗ Pipecat-ai core import failed: {e}")
        return False


def test_pipecat_transport_imports():
    """Test Pipecat-ai transport (Daily.co) imports"""
    try:
        from pipecat.transports.daily.transport import DailyTransport
        print("✓ Pipecat-ai Daily transport import successful")
        return True
    except ImportError as e:
        print(f"✗ Pipecat-ai Daily transport import failed: {e}")
        return False


def test_pipecat_stt_imports():
    """Test Pipecat-ai speech-to-text (Azure Speech) imports"""
    try:
        from pipecat.services.azure.stt import AzureSTTService
        print("✓ Pipecat-ai Azure Speech STT import successful")
        return True
    except ImportError as e:
        print(f"✗ Pipecat-ai Azure Speech STT import failed: {e}")
        return False


def test_pipecat_tts_imports():
    """Test Pipecat-ai text-to-speech (ElevenLabs) imports"""
    try:
        from pipecat.services.elevenlabs.tts import ElevenLabsTTSService
        print("✓ Pipecat-ai ElevenLabs TTS import successful")
        return True
    except ImportError as e:
        print(f"✗ Pipecat-ai ElevenLabs TTS import failed: {e}")
        return False


def test_voice_service_sdk_imports():
    """Test individual voice service SDK imports"""
    try:
        from daily import Daily
        from azure.cognitiveservices.speech import SpeechConfig
        from elevenlabs import ElevenLabs
        from openai import AzureOpenAI
        print("✓ Voice service SDKs import successful")
        print("  - Daily.co SDK")
        print("  - Azure Speech SDK")
        print("  - ElevenLabs SDK")
        print("  - Azure OpenAI SDK")
        return True
    except ImportError as e:
        print(f"✗ Voice service SDK import failed: {e}")
        return False


def main():
    """Run all import verification tests"""
    print("=" * 70)
    print("Voice Pipeline Import Verification")
    print("=" * 70)
    print()

    tests = [
        test_pipecat_core_imports,
        test_pipecat_transport_imports,
        test_pipecat_stt_imports,
        test_pipecat_tts_imports,
        test_voice_service_sdk_imports,
    ]

    results = []
    for test in tests:
        results.append(test())
        print()

    print("=" * 70)
    if all(results):
        print("✅ All voice pipeline dependencies installed correctly!")
        print()
        print("Ready to build Pipecat-ai voice bot in Story 3.3")
        return 0
    else:
        print("❌ Some imports failed. Check the errors above.")
        return 1


if __name__ == "__main__":
    exit(main())
