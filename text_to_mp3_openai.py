"""
OpenAI Text-to-Speech with Voice Support
Usage:
  cat my_text.txt | python text_to_mp3_openai.py                    # Auto-numbering
  cat my_text.txt | python text_to_mp3_openai.py --out custom.mp3   # Custom filename
  cat my_text.txt | python text_to_mp3_openai.py --voice nova       # Specific voice

.env file:
  OPENAI_API_KEY=sk_...
  OPENAI_TTS_MODEL=tts-1          # optional, defaults to "tts-1" (use "tts-1-hd" for higher quality)

Voices:
  - alloy (neutral, balanced)
  - echo (warm, expressive)
  - fable (engaging, storytelling)
  - onyx (deep, confident)
  - nova (bright, energetic)
  - shimmer (clear, professional)
"""

import os, sys, argparse, re
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")
MODEL   = os.getenv("OPENAI_TTS_MODEL", "tts-1")

if not API_KEY:
    sys.exit("❌  OPENAI_API_KEY not set. Add it to your .env file.")

VOICE_PROFILES = {
    "calm": "alloy",           # Neutral and balanced
    "energetic": "nova",       # Bright and energetic
    "warm": "echo",            # Warm and expressive
    "professional": "shimmer", # Clear and professional
}

def get_next_output_number():
    """Auto-increment output number if using default naming."""
    outputs_dir = Path("outputs")
    outputs_dir.mkdir(exist_ok=True)
    existing = list(outputs_dir.glob("output_*.mp3"))
    numbers = [int(re.search(r'output_(\d+)', f.name).group(1)) for f in existing]
    return max(numbers) + 1 if numbers else 1

def convert(text: str, out_path: str, voice: str = "shimmer"):
    client = OpenAI(api_key=API_KEY)

    # Map emotion to voice, or use voice directly if it's a valid voice name
    voice_name = VOICE_PROFILES.get(voice, voice)

    valid_voices = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
    if voice_name not in valid_voices:
        sys.exit(f"❌  Invalid voice: {voice}. Must be one of: {', '.join(valid_voices)}")

    try:
        response = client.audio.speech.create(
            model=MODEL,
            voice=voice_name,
            input=text,
        )

        audio_bytes = response.content
        Path(out_path).write_bytes(audio_bytes)
        print(f"✅  Saved → {out_path}  ({len(audio_bytes):,} bytes)")
        print(f"🎤 Voice: {voice_name.capitalize()}")
        print(f"🎵 Model: {MODEL}")
    except Exception as e:
        sys.exit(f"❌  Error: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert text to speech via OpenAI")
    parser.add_argument("text", nargs="?", help="Text to convert (or pipe via stdin)")
    parser.add_argument("--out", default=None, help="Output file (default: outputs/output_N.mp3)")
    parser.add_argument("--voice", default="professional",
                       choices=list(VOICE_PROFILES.keys()) + list(VOICE_PROFILES.values()),
                       help="Voice/emotion to use")
    args = parser.parse_args()

    text = args.text or (sys.stdin.read().strip() if not sys.stdin.isatty() else None)
    if not text:
        sys.exit("❌  No text provided. Pass it as an argument or pipe it in.")

    if args.out:
        out_path = args.out
    else:
        num = get_next_output_number()
        out_path = f"outputs/output_{num}.mp3"

    convert(text, out_path, args.voice)
