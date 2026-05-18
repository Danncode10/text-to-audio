# Text to Audio Converter

Convert text to speech using either **ElevenLabs** or **OpenAI** APIs with support for different voices and emotions.

## Features

- 🎤 Multiple TTS providers (ElevenLabs & OpenAI)
- 🎭 Emotion/tone customization
- 📁 Auto-numbered output files
- 🔄 Pipe text directly from files or stdin
- 🎵 High-quality MP3 output

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

Or manually install:
```bash
pip install elevenlabs openai python-dotenv
```

### 2. Get API Keys

#### ElevenLabs Setup

1. Sign up at [elevenlabs.io](https://elevenlabs.io)
2. Go to Account → API Key
3. Copy your API key (free tier available)
4. (Optional) Note your preferred voice ID from the Voices section

#### OpenAI Setup

1. Visit [platform.openai.com](https://platform.openai.com/account/api-keys)
2. Create an API key
3. Copy it to your `.env` file

### 3. Configure `.env` File

Create a `.env` file in the project root:

```env
# ElevenLabs Configuration
ELEVENLABS_API_KEY=sk_your_elevenlabs_api_key_here
ELEVENLABS_VOICE_ID=IKne3meq5aSn9XLyUdCD  # Optional: defaults to Rachel
ELEVENLABS_MODEL=eleven_multilingual_v2

# OpenAI Configuration
OPENAI_API_KEY=sk_your_openai_api_key_here
OPENAI_TTS_MODEL=tts-1  # Use "tts-1-hd" for higher quality
```

## Usage

### Using ElevenLabs

```bash
# Auto-numbered output
cat my_text.txt | python text_to_mp3.py

# Custom output filename
cat my_text.txt | python text_to_mp3.py --out custom.mp3

# With emotion/tone
cat my_text.txt | python text_to_mp3.py --emotion energetic

# Direct text input
python text_to_mp3.py "Hello, this is a test!" --out test.mp3
```

**Available emotions:**
- `calm` - Stable, relaxed
- `energetic` - Upbeat, enthusiastic
- `warm` - Friendly, expressive
- `professional` - Formal, clear

### Using OpenAI

```bash
# Auto-numbered output
cat my_text.txt | python text_to_mp3_openai.py

# Custom output filename
cat my_text.txt | python text_to_mp3_openai.py --out custom.mp3

# With voice preference
cat my_text.txt | python text_to_mp3_openai.py --voice nova

# Direct text input
python text_to_mp3_openai.py "Hello, world!" --out test.mp3
```

**Available voices:**
- `alloy` - Neutral, balanced
- `echo` - Warm, expressive
- `fable` - Engaging, storytelling
- `onyx` - Deep, confident
- `nova` - Bright, energetic
- `shimmer` - Clear, professional

## Configuration Files

### `prompt.txt` (Optional)

Add custom emotion/tone instructions for voice customization. The script will read this automatically if it exists.

Example:
```
Speak with enthusiasm and energy, as if you're excited about the topic.
Use natural pauses between sentences.
```

## Output

Files are saved to the `outputs/` directory with auto-numbered names:
- `output_1.mp3`
- `output_2.mp3`
- etc.

Or use a custom filename with the `--out` flag.

## Troubleshooting

**"ELEVENLABS_API_KEY not set"**
- Ensure your `.env` file exists in the project root
- Check that the API key is correctly copied
- Load the environment: `export $(cat .env | xargs)`

**"No text provided"**
- Pipe text via stdin: `echo "Hello" | python text_to_mp3.py`
- Or pass as argument: `python text_to_mp3.py "Your text here"`

**Rate limiting errors**
- ElevenLabs free tier has character limits
- OpenAI's TTS has usage quotas
- Check your API dashboard for usage details

## Project Structure

```
.
├── text_to_mp3.py              # ElevenLabs converter
├── text_to_mp3_openai.py       # OpenAI converter
├── prompt.txt                  # Optional emotion instructions
├── .env                        # API keys (don't commit!)
├── .gitignore                  # Ignore output/ folder
├── outputs/                    # Generated MP3 files
└── README.md                   # This file
```

## Notes

- Never commit your `.env` file (it contains API keys)
- The `outputs/` folder is ignored by git
- Both providers support multiple languages
- ElevenLabs offers more voice customization; OpenAI offers faster processing
