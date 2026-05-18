#!/bin/bash

# ElevenLabs History Cleanup Script
# Displays and deletes all items from your ElevenLabs history simultaneously.
#
# Usage:
#   ./cleanup_history.sh              # Delete all history (no confirmation)
#   ./cleanup_history.sh --preview    # See what would be deleted
#   ./cleanup_history.sh --confirm    # Require confirmation before deleting

set -e

# Load environment variables from .env if it exists
if [ -f .env ]; then
    export $(cat .env | grep ELEVENLABS_API_KEY | xargs)
fi

API_KEY="${ELEVENLABS_API_KEY}"

if [ -z "$API_KEY" ]; then
    echo "❌ ELEVENLABS_API_KEY not set. Add it to your .env file or set it as an environment variable."
    exit 1
fi

BASE_URL="https://api.elevenlabs.io/v1"
PREVIEW=false
CONFIRM=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --preview)
            PREVIEW=true
            shift
            ;;
        --confirm)
            CONFIRM=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Function to safely get text preview
get_text_preview() {
    local text="$1"
    local max_length="${2:-50}"

    if [ -z "$text" ]; then
        echo "[No text]"
    elif [ ${#text} -gt $max_length ]; then
        echo "${text:0:$max_length}..."
    else
        echo "$text"
    fi
}

# Fetch history
echo "🔍 Fetching history from ElevenLabs..."
HISTORY_RESPONSE=$(curl -s -X GET \
    "$BASE_URL/history" \
    -H "xi-api-key: $API_KEY")

# Parse history items
ITEMS=$(echo "$HISTORY_RESPONSE" | jq -r '.history[]? | @json' 2>/dev/null)

if [ -z "$ITEMS" ]; then
    echo "ℹ️  No history items found"
    exit 0
fi

# Count items
ITEM_COUNT=$(echo "$HISTORY_RESPONSE" | jq '.history | length' 2>/dev/null)
echo "Found $ITEM_COUNT history items:"
echo "------------------------------------------------------------"

# Display items
i=1
while IFS= read -r item; do
    if [ -z "$item" ]; then
        continue
    fi
    TEXT=$(echo "$item" | jq -r '.text // ""' 2>/dev/null | sed 's/^"//;s/"$//')
    PREVIEW=$(get_text_preview "$TEXT" 50)
    echo "$i. $PREVIEW"
    ((i++))
done <<< "$ITEMS"

echo "------------------------------------------------------------"

if [ "$PREVIEW" = true ]; then
    echo ""
    echo "📋 Preview mode: Would delete $ITEM_COUNT items"
    exit 0
fi

# Confirm before deleting if requested
if [ "$CONFIRM" = true ]; then
    echo ""
    read -p "⚠️  Delete all $ITEM_COUNT items? (yes/no): " RESPONSE
    if [ "$RESPONSE" != "yes" ]; then
        echo "Cancelled."
        exit 0
    fi
fi

# Delete all items
echo ""
echo "🗑️  Deleting items..."

DELETED=0
FAILED=0
i=1

while IFS= read -r item; do
    if [ -z "$item" ]; then
        continue
    fi

    HISTORY_ID=$(echo "$item" | jq -r '.history_item_id // ""' 2>/dev/null)
    TEXT=$(echo "$item" | jq -r '.text // ""' 2>/dev/null | sed 's/^"//;s/"$//')
    PREVIEW=$(get_text_preview "$TEXT" 40)

    if [ -z "$HISTORY_ID" ]; then
        echo "  [$i/$ITEM_COUNT] ✗ Skipped: $PREVIEW (no ID)"
        ((FAILED++))
        ((i++))
        continue
    fi

    # Delete the item
    DELETE_RESPONSE=$(curl -s -w "\n%{http_code}" -X DELETE \
        "$BASE_URL/history/$HISTORY_ID" \
        -H "xi-api-key: $API_KEY")

    HTTP_CODE=$(echo "$DELETE_RESPONSE" | tail -n1)

    if [ "$HTTP_CODE" = "204" ] || [ "$HTTP_CODE" = "200" ]; then
        echo "  [$i/$ITEM_COUNT] ✓ $PREVIEW"
        ((DELETED++))
    else
        echo "  [$i/$ITEM_COUNT] ✗ Failed: $PREVIEW (HTTP $HTTP_CODE)"
        ((FAILED++))
    fi

    ((i++))
done <<< "$ITEMS"

echo ""
echo "✅ Deleted $DELETED/$ITEM_COUNT items from ElevenLabs history"
if [ $FAILED -gt 0 ]; then
    echo "⚠️  $FAILED items failed to delete"
fi
