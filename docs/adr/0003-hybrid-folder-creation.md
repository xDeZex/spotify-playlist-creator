# Hybrid folder creation — script creates playlists, user creates folders

Spotify's official Web API has no endpoints for creating or managing playlist folders. The only programmatic alternative is Spotify's internal spclient API (`spclient.wg.spotify.com`), which is undocumented, likely violates Spotify's developer ToS, and requires a separate client token obtained by scraping a versioned JS bundle — meaning it can silently break on any Spotify deployment.

Instead, the script creates Album Playlists via the official API and then pauses, printing the artist name and the newly created playlist names. The user creates the Artist Folder manually in the Spotify app and places the playlists inside it before signalling the script to continue.

## Considered Options

- **spclient private API** — works today but ToS risk, no stability guarantee, and requires a hardcoded client ID extracted from Spotify's JS bundle that changes on each deploy.
- **Naming convention** (prefix playlists with artist name, no real folders) — fully stable but abandons the visual folder structure that motivates the project.
- **Hybrid** — chosen. Keeps real Spotify folders, stays entirely on the official API, and trades full automation for a brief manual step per artist.
