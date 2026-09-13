import asyncio
import logging
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Ensure UTF-8 output on Windows console to prevent charmap encoding errors
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Load env variables from root .env.local or .env
root_dir = Path(__file__).parent.parent
load_dotenv(root_dir / ".env.local")
load_dotenv(root_dir / ".env")

import edge_tts
from livekit.agents import (
    AutoSubscribe,
    JobContext,
    WorkerOptions,
    cli,
    tts,
)
from livekit.agents.voice import Agent, AgentSession
from livekit.plugins import groq, silero
try:
    from agent.pc_control import LAPTOP_CONTROL_TOOLS
except (ModuleNotFoundError, ImportError):
    from pc_control import LAPTOP_CONTROL_TOOLS

logger = logging.getLogger("voice-agent")
logger.setLevel(logging.INFO)

# High-fidelity Edge Neural TTS Adapter for LiveKit
class EdgeTTS(tts.TTS):
    def __init__(self, voice: str = "en-US-JennyNeural"):
        super().__init__(
            capabilities=tts.TTSCapabilities(streaming=False),
            sample_rate=24000,
            num_channels=1,
        )
        self.voice = voice

    def synthesize(self, text: str, *, conn_options=None) -> tts.ChunkedStream:
        return EdgeChunkedStream(
            tts=self,
            input_text=text,
            conn_options=conn_options or tts.DEFAULT_API_CONNECT_OPTIONS,
        )

class EdgeChunkedStream(tts.ChunkedStream):
    async def _run(self, output_emitter: tts.AudioEmitter) -> None:
        communicate = edge_tts.Communicate(self.input_text, self._tts.voice)
        output_emitter.initialize(
            request_id="edge_tts",
            sample_rate=24000,
            num_channels=1,
            mime_type="audio/mp3",
        )
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                output_emitter.push(chunk["data"])
        output_emitter.flush()

SYSTEM_PROMPT = """You are an intelligent, friendly AI voice assistant built with LiveKit Agents that has voice control capabilities over the user's Windows laptop.
You communicate naturally through voice.

DYNAMIC COMMAND CREATION & EXECUTION (VERY IMPORTANT):
You have the ability to automatically create and execute Windows PowerShell commands to fulfill any task requested by the user.
Whenever the user asks you to:
- Run a command, execute a script, or perform any command-line task
- Create, modify, delete, find, or list files or folders (e.g. "create a folder on my desktop called projects", "list files in my downloads")
- Check disk space, drive usage, or system storage (e.g. "check free space on drive C")
- Check networking, WiFi details, ping websites, or find IP address (e.g. "what is my IP address?", "ping google.com")
- Query active processes, hardware stats, or system info (e.g. "what apps are using the most RAM?")
- Any other PC action not covered by built-in tools
👉 IMMEDIATELY formulate the safe Windows PowerShell command and call `run_terminal_command(command=..., description=...)`!
When you receive the command output, summarize the result into 1 or 2 spoken sentences for the user.

BUILT-IN TOOLS:
- Open an application (notepad, chrome, calculator, vs code, settings, etc.) -> call `open_application`
- Close an app -> call `close_application`
- Open a website (YouTube, GitHub, etc.) -> call `open_website`
- Search something -> call `search_web`
- Write or take a note -> call `write_note` (saves the note and opens it in Notepad)
- Adjust volume (up, down, mute) -> call `volume_control`
- Control media (play, pause, next) -> call `media_control`
- Take a screenshot -> call `take_screenshot`
- Check battery / system specs -> call `get_system_status`
- Lock laptop -> call `lock_laptop`

VOICE RESPONSE RULES:
- Always call the tool FIRST to perform the action.
- Keep your spoken responses concise, conversational, and direct (1 to 2 sentences).
- Avoid long lists, markdown formatting, or bullet points in spoken responses—speak plain conversational English.
"""

async def entrypoint(ctx: JobContext):
    logger.info(f"Connecting to room: {ctx.room.name}")
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    # Initialize VAD (Voice Activity Detection)
    vad = silero.VAD.load()

    # Initialize Groq STT and LLM
    stt = groq.STT(
        model="whisper-large-v3-turbo",
        language="en",
    )
    llm = groq.LLM(
        model="openai/gpt-oss-120b",
    )

    # Configure TTS: Use OpenAI if available, else Edge Neural TTS
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key and len(openai_key.strip()) > 10:
        from livekit.plugins import openai
        logger.info("Using OpenAI TTS")
        agent_tts = openai.TTS(voice="alloy")
    else:
        logger.info("Using Microsoft Edge Neural TTS (en-US-JennyNeural)")
        agent_tts = EdgeTTS(voice="en-US-JennyNeural")

    # Create Agent instance with Laptop Control tools
    agent = Agent(
        instructions=SYSTEM_PROMPT,
        tools=LAPTOP_CONTROL_TOOLS,
    )

    # Create Agent Session
    session = AgentSession(
        stt=stt,
        llm=llm,
        tts=agent_tts,
        vad=vad,
    )

    # Real-time Terminal Logging Listeners
    @session.on("user_input_transcribed")
    def on_user_input(ev):
        if ev.is_final and ev.transcript.strip():
            print(f"\n🗣️  [USER SPOKE]: \"{ev.transcript.strip()}\"", flush=True)

    @session.on("conversation_item_added")
    def on_conv_item(ev):
        item = ev.item
        role = getattr(item, "role", "")
        text = getattr(item, "text_content", "") or ""
        if str(role).lower() == "assistant" and text.strip():
            print(f"🤖 [AGENT REPLIED]: \"{text.strip()}\"\n", flush=True)

    # Start the agent session attached to the room
    banner = """
=================================================================
  🎙️  LIVEKIT AI VOICE AGENT WORKER IS ACTIVE & READY!
  💻 Laptop Voice Control & Dynamic Command Engine Loaded:
     • Dynamic PowerShell Command Generation & Execution (Auto)
     • Open / Close Apps (Notepad, Chrome, Calc, VS Code, etc.)
     • Write Notes (Auto-saves & opens in Notepad)
     • Open Websites & Search Web / YouTube
     • Volume Control & Media Playback
     • Screenshots & System / Battery Status
     • Workstation Lock
=================================================================
"""
    print(banner, flush=True)
    logger.info("Starting voice agent session with laptop control tools...")
    await session.start(agent, room=ctx.room)

    # Send initial greeting once user joins
    await asyncio.sleep(1)
    try:
        await session.say("Hi there! I am your AI voice assistant with full laptop control. You can ask me to open apps, write notes, check system stats, or automatically create and run any command on your laptop. What would you like me to do?")
    except Exception as e:
        logger.warning(f"Initial greeting notice: {e}")

if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
