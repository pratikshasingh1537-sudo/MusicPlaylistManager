"""Streamlit web interface for the existing MusicPlaylistManager DSA project."""
import io
import random
import streamlit as st

from core import Playlist, PlaylistError
from node import Song
import shuffle as shuffle_module

st.set_page_config(page_title="Music Playlist Manager", page_icon="🎵", layout="wide")

if "playlist" not in st.session_state:
    st.session_state.playlist = Playlist()

playlist = st.session_state.playlist


def songs_in_order(reverse=False):
    node = playlist.tail if reverse else playlist.head
    step = "prev" if reverse else "next"
    while node is not None:
        yield node
        node = getattr(node, step)


def playlist_as_text():
    lines = []
    for node in songs_in_order():
        song = node.data
        lines.append(song.to_record())
    return "\n".join(lines) + ("\n" if lines else "")


def show_message(kind, message):
    getattr(st, kind)(message)

st.title("🎵 Music Playlist Manager")
st.caption("A browser-based interface powered by your hand-built doubly linked list.")

# Summary
count = len(playlist)
total_seconds = playlist.total_duration()
current = playlist.now_playing()
a, b, c = st.columns(3)
a.metric("Songs", count)
b.metric("Total duration", f"{total_seconds // 60}:{total_seconds % 60:02d}")
c.metric("Now playing", current.title if current else "—")

st.divider()
left, right = st.columns([1, 1.7], gap="large")

with left:
    st.subheader("Add a song")
    with st.form("add_song_form", clear_on_submit=True):
        title = st.text_input("Song title")
        artist = st.text_input("Artist")
        duration = st.number_input("Duration (seconds)", min_value=0, step=1, value=180)
        submitted = st.form_submit_button("Add to playlist", type="primary", use_container_width=True)
        if submitted:
            try:
                song = Song(playlist.next_free_id(), title, artist, int(duration))
                playlist.append(song)
                st.success(f"Added **{song.title}**.")
                st.rerun()
            except (ValueError, PlaylistError) as error:
                st.error(str(error))

    st.subheader("Playback controls")
    wrap = st.checkbox("Loop playlist", value=False)
    p1, p2 = st.columns(2)
    if p1.button("⏮ Previous", use_container_width=True, disabled=count == 0):
        result = playlist.prev_song(wrap=wrap)
        if result is None:
            st.info("Already at the first song.")
        st.rerun()
    if p2.button("Next ⏭", use_container_width=True, disabled=count == 0):
        result = playlist.next_song(wrap=wrap)
        if result is None:
            st.info("Already at the last song.")
        st.rerun()

    if st.button("🔀 Shuffle playlist", use_container_width=True, disabled=count < 2):
        shuffle_module.shuffle(playlist, rng=random)
        st.success("Playlist shuffled.")
        st.rerun()

    st.subheader("Save / load")
    st.download_button(
        "⬇ Download playlist (.txt)",
        data=playlist_as_text(),
        file_name="music_playlist.txt",
        mime="text/plain",
        use_container_width=True,
    )
    uploaded = st.file_uploader("Load a playlist text file", type=["txt"])
    if uploaded is not None and st.button("Load uploaded playlist", use_container_width=True):
        try:
            new_playlist = Playlist()
            for line_number, raw in enumerate(io.StringIO(uploaded.getvalue().decode("utf-8")), 1):
                line = raw.strip()
                if not line or line.startswith("#"):
                    continue
                parts = line.split("|")
                if len(parts) != 4:
                    raise ValueError(f"Line {line_number}: expected id|title|artist|seconds")
                song_id, song_title, song_artist, seconds = parts
                new_playlist.append(Song(int(song_id), song_title, song_artist, int(seconds)))
            st.session_state.playlist = new_playlist
            st.success(f"Loaded {len(new_playlist)} songs.")
            st.rerun()
        except (UnicodeDecodeError, ValueError) as error:
            st.error(f"Could not load file: {error}")

with right:
    st.subheader("Your playlist")
    query = st.text_input("Search by title or artist", placeholder="Type to filter songs...")
    reverse = st.toggle("Show in reverse order", value=False)
    visible_nodes = list(songs_in_order(reverse=reverse))
    if query.strip():
        q = query.casefold()
        visible_nodes = [n for n in visible_nodes if q in n.data.title.casefold() or q in n.data.artist.casefold()]

    if not visible_nodes:
        st.info("No matching songs. Add a song to get started." if count == 0 else "No songs match your search.")
    else:
        for position, node in enumerate(visible_nodes):
            song = node.data
            is_current = node is playlist.current
            row = st.container(border=True)
            with row:
                info, up_col, down_col, del_col = st.columns([5, 1, 1, 1])
                marker = "▶️ " if is_current else ""
                info.markdown(f"**{marker}{song.title}**  \n{song.artist or 'Unknown artist'} · {song.duration_text()}")
                # Reordering uses the actual linked-list node; filtered/reverse views do not change its identity.
                if up_col.button("↑", key=f"up_{song.song_id}", disabled=node.prev is None, help="Move up"):
                    playlist.move_up(node)
                    st.rerun()
                if down_col.button("↓", key=f"down_{song.song_id}", disabled=node.next is None, help="Move down"):
                    playlist.move_down(node)
                    st.rerun()
                if del_col.button("✕", key=f"del_{song.song_id}", help="Remove song"):
                    playlist.remove_node(node)
                    st.rerun()

    st.caption("The playlist is still stored in your original doubly linked list (head/tail/prev/next). The web UI is a separate layer.")

st.divider()
with st.expander("About this project"):
    st.write("This app reuses `core.py`, `node.py`, and `shuffle.py` from the original CLI project. Streamlit only provides the browser interface; playlist operations continue to use the custom doubly linked list.")
    st.write("**Complexities:** append O(1), search O(n), next/previous O(1), shuffle O(n²) for the current algorithm.")
