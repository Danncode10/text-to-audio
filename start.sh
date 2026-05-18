#!/bin/bash

# Start script: Generate audio output + clear history simultaneously
#
# Usage:
#   ./start.sh                    # Uses my_text.txt (default emotion: professional)
#   ./start.sh --emotion warm     # Specify emotion
#   ./start.sh --out custom.mp3   # Custom output filename
#   ./start.sh --emotion energetic --out my_audio.mp3

set -e

# Load environment variables from .env if it exists
if [ -f .env ]; then
    export $(cat .env | grep -E "ELEVENLABS|ELEVENLABS_VOICE_ID|ELEVENLABS_MODEL" | xargs)
fi

API_KEY="${ELEVENLABS_API_KEY}"

if [ -z "$API_KEY" ]; then
    echo "❌ ELEVENLABS_API_KEY not set. Add it to your .env file."
    exit 1
fi

BASE_URL="https://api.elevenlabs.io/v1"
TEXT_FILE="my_text.txt"
EMOTION="professional"
OUT_FILE=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --emotion)
            EMOTION="$2"
            shift 2
            ;;
        --out)
            OUT_FILE="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Check if text file exists
if [ ! -f "$TEXT_FILE" ]; then
    echo "❌ $TEXT_FILE not found"
    exit 1
fi

echo "🚀 Starting text-to-speech conversion and history cleanup..."
echo ""

# Function to clear history in background
clear_history_async() {
    echo "[Background] 🗑️  Clearing ElevenLabs history..."

    HISTORY_RESPONSE=$(curl -s -X GET \
        "$BASE_URL/history" \
        -H "xi-api-key: $API_KEY")

    ITEMS=$(echo "$HISTORY_RESPONSE" | jq -r '.history[]? | @json' 2>/dev/null)
    ITEM_COUNT=$(echo "$HISTORY_RESPONSE" | jq '.history | length' 2>/dev/null)

    if [ -z "$ITEM_COUNT" ] || [ "$ITEM_COUNT" -eq 0 ]; then
        echo "[Background] ℹ️  No history items to clear"
        return
    fi

    DELETED=0
    i=1

    while IFS= read -r item; do
        if [ -z "$item" ]; then
            continue
        fi

        HISTORY_ID=$(echo "$item" | jq -r '.history_item_id // ""' 2>/dev/null)

        if [ -z "$HISTORY_ID" ]; then
            ((i++))
            continue
        fi

        # Delete the item
        curl -s -X DELETE \
            "$BASE_URL/history/$HISTORY_ID" \
            -H "xi-api-key: $API_KEY" > /dev/null 2>&1

        ((DELETED++))
        ((i++))
    done <<< "$ITEMS"

    echo "[Background] ✅ Cleared $DELETED history items"
}

# Start history cleanup in background
clear_history_async &
HISTORY_PID=$!

# Generate audio from text file
echo "[Main] 📝 Converting text to speech..."
if [ -z "$OUT_FILE" ]; then
    cat "$TEXT_FILE" | python text_to_mp3.py --emotion "$EMOTION"
else
    cat "$TEXT_FILE" | python text_to_mp3.py --emotion "$EMOTION" --out "$OUT_FILE"
fi

# Wait for history cleanup to complete
wait $HISTORY_PID
echo ""
echo "✨ Done! Audio generated and history cleared."
