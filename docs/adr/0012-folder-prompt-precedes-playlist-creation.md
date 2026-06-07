# Folder prompt precedes playlist creation

Before creating any Album Playlists for an artist, the script pauses and prompts the user to create and position the Artist Folder in Spotify. Playlist creation begins only after the user confirms.

The reason: the user drags newly created playlists into the folder immediately after they appear in the library. For this to work naturally, the folder must already be positioned just below where the new playlists will land — which is only possible if the folder exists before creation starts.

The prompt for each subsequent artist doubles as the wait for the previous artist: the user drags the previous batch into its folder, then creates the next folder, then presses Enter. After the final artist there is no blocking wait — the script prints the last batch and exits.

The previous behaviour prompted after creation, which required the user to create the folder after the playlists were already scattered through the library.
