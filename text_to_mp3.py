"""
ElevenLabs Text-to-Speech with Emotion Support
Usage:
  cat my_text.txt | python text_to_mp3.py                    # Auto-numbering
  cat my_text.txt | python text_to_mp3.py --out custom.mp3   # Custom filename
  cat my_text.txt | python text_to_mp3.py --emotion energetic

.env file:
  ELEVENLABS_API_KEY=sk_...
  ELEVENLABS_VOICE_ID=EXA...          # optional, defaults to "Rachel"
  ELEVENLABS_MODEL=eleven_multilingual_v2   # optional

prompt.txt:
  Optional emotion/tone instructions for voice customization
"""


"""
Terminal code

# Pipe from text file:
cat my_text.txt | python text_to_mp3.py

# Or with specific emotion:
cat my_text.txt | python text_to_mp3.py --emotion warm

# Or pass text directly:
python text_to_mp3.py "Your text here" --out custom.mp3
"""

import os, sys, argparse, re
from pathlib import Path
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs

load_dotenv()

API_KEY  = os.getenv("ELEVENLABS_API_KEY")
VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")  # Rachel (default)
MODEL    = os.getenv("ELEVENLABS_MODEL", "eleven_multilingual_v2")

if not API_KEY:
    sys.exit("❌  ELEVENLABS_API_KEY not set. Add it to your .env file.")

EMOTION_PROFILES = {
    "calm": {"stability": 0.6, "similarity_boost": 0.7},
    "energetic": {"stability": 0.8, "similarity_boost": 0.9},
    "warm": {"stability": 0.7, "similarity_boost": 0.85},
    "professional": {"stability": 0.75, "similarity_boost": 0.8},
}

def get_next_output_number():
    """Auto-increment output number if using default naming."""
    outputs_dir = Path("outputs")
    outputs_dir.mkdir(exist_ok=True)
    existing = list(outputs_dir.glob("output_*.mp3"))
    numbers = [int(re.search(r'output_(\d+)', f.name).group(1)) for f in existing]
    return max(numbers) + 1 if numbers else 1

def read_prompt():
    """Read emotion instructions from prompt.txt if it exists."""
    prompt_file = Path("prompt.txt")
    if prompt_file.exists():
        return prompt_file.read_text()
    return None

def convert(text: str, out_path: str, emotion: str = "professional"):
    client = ElevenLabs(api_key=API_KEY)

    voice_settings = EMOTION_PROFILES.get(emotion, EMOTION_PROFILES["professional"])

    audio = client.text_to_speech.convert(
        text=text,
        voice_id=VOICE_ID,
        model_id=MODEL,
        output_format="mp3_44100_128",
        voice_settings={
            "stability": voice_settings["stability"],
            "similarity_boost": voice_settings["similarity_boost"],
        }
    )
    audio_bytes = b"".join(audio)
    Path(out_path).write_bytes(audio_bytes)
    print(f"✅  Saved → {out_path}  ({len(audio_bytes):,} bytes)")
    print(f"📝 Emotion: {emotion.capitalize()}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert text to speech via ElevenLabs with emotion support")
    parser.add_argument("text", nargs="?", help="Text to convert (or pipe via stdin)")
    parser.add_argument("--out", default=None, help="Output file (default: outputs/output_N.mp3)")
    parser.add_argument("--emotion", default="professional",
                       choices=list(EMOTION_PROFILES.keys()),
                       help="Voice emotion/tone")
    args = parser.parse_args()

    text = args.text or (sys.stdin.read().strip() if not sys.stdin.isatty() else None)
    if not text:
        sys.exit("❌  No text provided. Pass it as an argument or pipe it in.")

    if args.out:
        out_path = args.out
    else:
        num = get_next_output_number()
        out_path = f"outputs/output_{num}.mp3"

    convert(text, out_path, args.emotion)
