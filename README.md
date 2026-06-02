# Spotify Playlist Creator

Automatically organize your Spotify saved albums into curated album playlists, grouped by artist.

This script reads your Spotify Saved Albums, discovers the artists in your library, fetches their complete discographies, and creates one **Album Playlist** per album—then guides you through organizing them into **Artist Folders** in your Spotify library.

## Features

- **Discover artists from your library** — reads your Saved Albums to identify which artists to organize
- **Fetch complete discographies** — automatically retrieves all albums and EPs by each artist
- **Smart EP detection** — uses Spotify's track count and duration rules to distinguish EPs from singles
- **Create album playlists** — one playlist per album, pre-filled with all tracks
- **Additive sync** — safe to run repeatedly; only creates what's missing, never deletes
- **Dry-run mode** — preview what would be created without making changes
- **Artist limit** — process artists in batches to stay within your time budget

## Installation

### Requirements

- Python 3.10+
- A Spotify account
- Spotify API credentials (see [Setup](#setup) below)

### 1. Clone the repository

```bash
git clone <repository-url>
cd spotify-playlist-creator
```

### 2. Install dependencies

```bash
pip install -e .
```

Or if you prefer `poetry` or `pipx`:

```bash
poetry install
```

### 3. Set up Spotify API credentials

Create a Spotify Developer application at [developer.spotify.com](https://developer.spotify.com/dashboard):

1. Log in with your Spotify account (or create one)
2. Accept the terms and create an app
3. You'll receive a **Client ID** and **Client Secret**
4. Add `http://127.0.0.1:8888/callback` as a Redirect URI in your app settings

### 4. Configure environment variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Then edit `.env` and add your credentials:

```
SPOTIFY_CLIENT_ID=your_client_id_here
SPOTIFY_CLIENT_SECRET=your_client_secret_here
```

Alternatively, set these as shell environment variables before running the script.

## Usage

### Basic sync

Organize all artists in your library:

```bash
python main.py
```

For each artist with new album playlists, the script will:
1. Fetch their albums
2. Create playlists for albums you don't have yet
3. Print the new playlist names
4. Pause and prompt you to create an Artist Folder in Spotify and drag the playlists into it
5. Continue to the next artist once you press Enter

### Dry run

Preview what would be created without making changes:

```bash
python main.py --dry-run
```

Shows the same information as a normal sync, but skips all Spotify API writes and doesn't pause for input.

### Limit artists per run

Process only N artists at a time (useful if your library is large):

```bash
python main.py --limit 5
```

The N artists are selected by age: the artists whose albums you saved longest ago are processed first. Running with the same limit twice processes the same set of artists.

Combine with `--dry-run`:

```bash
python main.py --limit 5 --dry-run
```

## How it works

1. **Authenticate** — opens your browser to authorize access to your Spotify account
2. **Fetch Saved Albums** — reads the albums you've saved to discover which artists to include
3. **Derive artists** — extracts the primary artist from each saved album
4. **Fetch discographies** — for each artist, retrieves their full album catalog from Spotify
5. **Classify releases** — filters albums using EP detection logic (full albums only, plus qualifying EPs)
6. **Check existing playlists** — scans your current playlists to find which albums you've already organized
7. **Create missing playlists** — for each artist, creates playlists for any albums you haven't yet organized
8. **Prompt for folder placement** — pauses for you to manually organize new playlists into Artist Folders (unless in dry-run mode)

### What counts as an Album?

Albums include:
- Full studio albums (Spotify type `album`)
- EPs that meet Spotify's classification rules:
  - **4–6 tracks** with total duration ≤30 minutes
  - **1–3 tracks** where at least one track exceeds 10 minutes AND total duration exceeds 30 minutes

Singles and other releases do not qualify.

### Terminology

See [CONTEXT.md](CONTEXT.md) for the complete domain vocabulary and additional examples.

## Running tests

```bash
python -m pytest
```

Run a specific test:

```bash
python -m pytest tests/test_foo.py::test_specific_test
```

## Development

### Code quality

Format code:

```bash
ruff format .
```

Check for lint issues:

```bash
ruff check .
```

Type check:

```bash
mypy spotify_playlist_creator tests
```

Run all checks and tests:

```bash
pre-commit run --all-files
python -m pytest
```

### One-time setup for pre-commit hooks

```bash
pre-commit install
```

This ensures lint, format, and type checks run on every `git commit`.

## Architecture & Design

Key architectural decisions are documented in [docs/adr/](docs/adr/):

- [ADR-0001](docs/adr/0001-ep-classification-via-track-count-and-duration.md) — EP detection via track count and duration rules
- [ADR-0002](docs/adr/0002-sync-is-additive-only.md) — Sync is additive only; playlists are never deleted
- [ADR-0003](docs/adr/0003-hybrid-folder-creation.md) — Manual Artist Folder creation with guided placement
- [ADR-0004](docs/adr/0004-album-playlist-detection-via-first-track-fingerprint.md) — Album identity determined by first track
- [ADR-0005](docs/adr/0005-split-create-album-playlists-for-dry-sync.md) — Dry-run support via split create logic
- [ADR-0006](docs/adr/0006-429-retry-requires-retry-after-header.md) — Rate limit handling with Retry-After header

## Troubleshooting

### "Missing environment variable: SPOTIFY_CLIENT_ID"

Ensure your `.env` file is in the project root with your credentials, or set the environment variables in your shell before running.

### "Invalid client ID"

Double-check that your Client ID and Client Secret are correct in your `.env` file (or environment). Verify them in your Spotify Developer dashboard.

### "OAuth error" or browser won't open

Ensure `http://127.0.0.1:8888/callback` is registered as a Redirect URI in your Spotify app settings. Clear your browser cookies for `accounts.spotify.com` and try again.

### Script exits before creating playlists

This is normal if you've already organized all your albums. Run with `--dry-run` to confirm the script is working and has found your albums.

## Contributing

See [CONTEXT.md](CONTEXT.md) for domain terminology and [CLAUDE.md](CLAUDE.md) for development workflow guidance.

## License

This project is provided as-is for personal use. Ensure you comply with Spotify's API terms of service when using this tool.
