"""
ElevenLabs History Cleanup via REST API
Displays and deletes all items from your ElevenLabs history simultaneously.

Usage:
  python cleanup_history.py              # Delete all history (no confirmation)
  python cleanup_history.py --preview    # See what would be deleted
  python cleanup_history.py --confirm    # Require confirmation before deleting
"""

import os, sys, argparse
from dotenv import load_dotenv
import requests

load_dotenv()

API_KEY = os.getenv("ELEVENLABS_API_KEY")

if not API_KEY:
    sys.exit("❌  ELEVENLABS_API_KEY not set. Add it to your .env file.")

BASE_URL = "https://api.elevenlabs.io/v1"
HEADERS = {"xi-api-key": API_KEY}

def get_text_preview(text, max_length=50):
    """Safely get text preview, handling None values."""
    if text is None:
        return "[No text]"
    text_str = str(text).strip()
    if len(text_str) > max_length:
        return text_str[:max_length] + "..."
    return text_str

def cleanup_history(preview=False, confirm=False):
    try:
        # Get history
        response = requests.get(f"{BASE_URL}/history", headers=HEADERS)
        response.raise_for_status()
        items = response.json().get("history", [])

        if not items:
            print("ℹ️  No history items to delete")
            return

        print(f"Found {len(items)} history items:")
        print("-" * 60)

        for i, item in enumerate(items, 1):
            text_preview = get_text_preview(item.get("text"))
            print(f"{i}. {text_preview}")

        print("-" * 60)

        if preview:
            print(f"\n📋 Preview mode: Would delete {len(items)} items")
            return

        # Confirm before deleting if requested
        if confirm:
            response_input = input(f"\n⚠️  Delete all {len(items)} items? (yes/no): ").strip().lower()
            if response_input != "yes":
                print("Cancelled.")
                return

        # Delete all while displaying progress
        print("\n🗑️  Deleting items...")
        deleted = 0
        failed = 0
        for i, item in enumerate(items, 1):
            try:
                history_item_id = item.get("history_item_id")
                text_preview = get_text_preview(item.get("text"), max_length=40)

                delete_response = requests.delete(f"{BASE_URL}/history/{history_item_id}", headers=HEADERS)
                delete_response.raise_for_status()

                deleted += 1
                print(f"  [{i}/{len(items)}] ✓ {text_preview}")
            except Exception as e:
                failed += 1
                print(f"  [{i}/{len(items)}] ✗ Failed: {text_preview} - {str(e)[:50]}")

        print(f"\n✅ Deleted {deleted}/{len(items)} items from ElevenLabs history")
        if failed > 0:
            print(f"⚠️  {failed} items failed to delete")

    except Exception as e:
        sys.exit(f"❌  Error: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Clean up ElevenLabs history")
    parser.add_argument("--preview", action="store_true", help="Preview items without deleting")
    parser.add_argument("--confirm", action="store_true", help="Require confirmation before deleting (default: delete without confirmation)")
    args = parser.parse_args()

    cleanup_history(preview=args.preview, confirm=args.confirm)
