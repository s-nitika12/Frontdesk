"""
Voice AI Agent with LiveKit integration for real-time voice conversations.
Handles speech-to-text, AI processing, and text-to-speech.
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from livekit import agents, rtc
from livekit.agents import AutoSubscribe, JobContext, WorkerOptions, cli, llm
from livekit.agents.voice_assistant import VoiceAssistant
from livekit.plugins import deepgram, openai, silero

from .ai_agent import AIAgent
from .config import Config

logger = logging.getLogger("voice_ai_agent")


class VoiceAIAgent:
    """
    LiveKit-based Voice AI Agent that handles real-time voice conversations.
    Integrates with the existing AIAgent for knowledge base lookups and escalations.
    """

    def __init__(self):
        self.ai_agent = AIAgent()
        self.logger = logger

    async def entrypoint(self, ctx: JobContext):
        """
        Main entrypoint for LiveKit agent sessions.
        Called when a new participant joins the room.
        """
        self.logger.info(f"Starting voice AI session for room: {ctx.room.name}")

        # Wait for the first participant
        async def on_participant_connected(participant: rtc.Participant):
            self.logger.info(f"Participant connected: {participant.identity}")
            await self._start_voice_assistant(ctx, participant)

        ctx.room.on("participant_connected", on_participant_connected)

        # If participant is already in room
        if len(ctx.room.participants) > 0:
            participant = list(ctx.room.participants.values())[0]
            await self._start_voice_assistant(ctx, participant)

    async def _start_voice_assistant(self, ctx: JobContext, participant: rtc.Participant):
        """Initialize and start the voice assistant for a participant."""
        
        # Configure the AI model with business context
        initial_ctx = self._build_initial_context()

        # Create assistant with STT, LLM, and TTS
        assistant = VoiceAssistant(
            vad=silero.VAD.load(),  # Voice Activity Detection
            stt=deepgram.STT(),      # Speech-to-Text
            llm=openai.LLM(
                model="gpt-4-turbo-preview",
                temperature=0.7,
            ),
            tts=openai.TTS(voice="nova"),  # Text-to-Speech
            chat_ctx=initial_ctx,
        )

        # Hook into the assistant's chat flow
        assistant.on("function_calls_finished", self._on_function_calls_finished)
        
        # Start the assistant
        await assistant.start(ctx.room, participant)

        self.logger.info(f"Voice assistant started for {participant.identity}")

    def _build_initial_context(self) -> llm.ChatContext:
        """Build the initial chat context with business information."""
        import json
        
        # Load business info
        with open(self.ai_agent.business_info, "r") as f:
            business_data = json.load(f)

        system_prompt = f"""You are a professional AI receptionist for {business_data['name']}.

Business Information:
- Address: {business_data['address']}
- Phone: {business_data['phone']}
- Hours: {business_data['hours']}

Services and Pricing:
{json.dumps(business_data['services'], indent=2)}

Policies:
{json.dumps(business_data['policies'], indent=2)}

Your role:
1. Answer customer questions politely and professionally
2. Use the provided business information
3. If you're unsure or the question requires human expertise, politely escalate to a supervisor
4. Keep responses concise and natural for voice conversation
5. Offer helpful follow-up suggestions

When you need to check the knowledge base or escalate, use the available functions.
"""

        return llm.ChatContext(
            messages=[
                llm.ChatMessage(role="system", content=system_prompt)
            ]
        )

    async def _on_function_calls_finished(self, ctx: Any):
        """Handle custom function calls from the LLM."""
        # This can be extended to handle custom functions like KB lookup
        pass

    def handle_voice_query(self, caller: Dict[str, str], audio_data: bytes) -> Dict[str, Any]:
        """
        Handle a voice query (for REST API integration).
        This is a synchronous wrapper for async voice processing.
        """
        # For REST API, we can transcribe and process
        # In production, use LiveKit rooms instead
        return {
            "status": "voice_processing_requires_livekit_room",
            "message": "Please use LiveKit room for real-time voice processing"
        }


class VoiceCallHandler:
    """
    Handler for incoming voice calls that integrates with the main AI agent.
    Bridges voice input/output with the existing help request system.
    """

    def __init__(self):
        self.ai_agent = AIAgent()
        self.logger = logger

    async def process_voice_input(
        self,
        caller: Dict[str, str],
        transcript: str,
        audio_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process transcribed voice input and generate response.
        
        Args:
            caller: Caller information (name, phone)
            transcript: Transcribed text from speech
            audio_metadata: Optional metadata about the audio
            
        Returns:
            Response with action taken and reply text/audio
        """
        self.logger.info(f"Processing voice input from {caller.get('phone')}: {transcript}")

        # Use existing AI agent logic
        result = self.ai_agent.handle_incoming(caller, transcript)

        # Enhance with voice-specific metadata
        result["voice_metadata"] = audio_metadata or {}
        result["response_format"] = "voice"

        return result

    def generate_voice_response(self, text: str) -> Dict[str, Any]:
        """
        Generate voice response from text.
        In production, this would call TTS service.
        """
        return {
            "text": text,
            "audio_url": None,  # Would be generated by TTS service
            "format": "mp3",
            "duration_ms": len(text) * 50,  # Rough estimate
        }


# Worker configuration for LiveKit
def create_worker_options() -> WorkerOptions:
    """Create worker options for LiveKit agent."""
    return WorkerOptions(
        entrypoint_fnc=lambda ctx: VoiceAIAgent().entrypoint(ctx),
        request_fnc=None,  # Optional: handle custom requests
    )


# For running as standalone LiveKit worker
if __name__ == "__main__":
    cli.run_app(create_worker_options())
