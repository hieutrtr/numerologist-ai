"""
Voice Pipeline Package

This package contains voice AI bot components for the Numerologist AI application.
It integrates Pipecat-ai framework with Daily.co WebRTC for real-time voice conversations.

Components:
    - pipecat_bot: Main bot implementation with Pipecat pipeline
"""

from . import pipecat_bot

__all__ = ["pipecat_bot"]
