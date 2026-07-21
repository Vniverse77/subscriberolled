# YouTube Subscriber Watcher

A lightweight Python script that monitors a YouTube channel's subscriber count
and triggers a browser-based prank (opens a Rickroll video) whenever a new
subscriber is detected.

## How It Works

The script polls the YouTube Data API v3 at a configurable interval, compares
the current subscriber count against the last recorded value, and opens a
video in the default browser whenever the count increases. State is persisted
locally so the script can be restarted without re-triggering on the same
subscriber count.

## Requirements

- Python 3.10 or later
- A Google Cloud project with the YouTube Data API v3 enabled
- An API key for that project
- The target channel's ID

## Installation

Clone the repository and install dependencies:

```bash
pip install requests python-dotenv --break-system-packages
```

## Configuration

Copy the example environment file and fill in your own values:

```bash
cp .env.example .env
```

Edit `.env`:

```
YOUTUBE_API_KEY=your_api_key_here
YOUTUBE_CHANNEL_ID=your_channel_id_here
```

The `.env` file is excluded from version control via `.gitignore` and should
never be committed. Only `.env.example` is safe to share publicly.

## Usage

Run the watcher with default settings (checks every 300 seconds):

```bash
python3 youtube_watcher.py
```

Specify a custom check interval, in seconds:

```bash
python3 youtube_watcher.py --interval 60
```

Override credentials via command-line flags instead of `.env`:

```bash
python3 youtube_watcher.py --api-key YOUR_KEY --channel-id YOUR_CHANNEL_ID
```

Test the prank mechanism without waiting for a real subscriber or calling
the API:

```bash
python3 youtube_watcher.py --test-rickroll
```

## Security Notes

- Never commit API keys or `.env` files to version control.
- If a key is ever exposed (for example, pushed to a public repository),
  revoke it immediately from the Google Cloud Console and generate a new
  one. Removing the commit from git history does not, by itself,
  invalidate an already-exposed key.
- Restrict the API key's scope to the YouTube Data API v3 where possible.

## License

This project is provided as GPL3.2 License.
