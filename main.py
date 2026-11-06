"""
main.py - The command line interface. This is the ONLY file that talks to
the user. It never manipulates pointers directly; it only calls core.Playlist.

Run it with:   python3 main.py
"""

import sys

from core import Playlist, PlaylistError
import shuffle as shuffle_module
import storage
from node import Song, SEP

DEFAULT_FILE = "data/sample.txt"

MENU = """
=========================  MUSIC PLAYLIST MANAGER  =========================
 1. Add song at end            7. Move song up
 2. Insert song at position    8. Move song down
 3. Show playlist              9. Delete song by title
 4. Show playlist in reverse  10. Shuffle
 5. Next song                 11. Save playlist
 6. Previous song             12. Load playlist
13. Playlist stats             0. Exit
============================================================================
"""


# ----------------------------------------------------------------------
# Input helpers - every user mistake is caught here, never deeper down
# ----------------------------------------------------------------------
def ask_int(prompt, low=None, high=None):
    """Keep asking until the user types a whole number in range."""
    while True:
        raw = input(prompt).strip()
        if raw == "":
            print("  ! nothing typed, try again")
            continue
        try:
            value = int(raw)
        except ValueError:
            print("  ! '%s' is not a whole number" % raw)
            continue
        if low is not None and value < low:
            print("  ! must be %d or more" % low)
            continue
        if high is not None and value > high:
            print("  ! must be %d or less" % high)
            continue
        return value


def ask_text(prompt, allow_blank=False):
    while True:
        raw = input(prompt).strip()
        if raw:
            if SEP in raw:
                print("  ! '%s' is not allowed in text fields" % SEP)
                continue
            return raw
        if allow_blank:
            return ""
        print("  ! this cannot be empty")


def read_song(playlist):
    """Collect the four fields of one song, validating as we go."""
    song_id = playlist.next_free_id()
    title = ask_text("  Title: ")
    artist = ask_text("  Artist: ")
    duration = ask_int("  Duration in seconds (e.g. 268): ", low=0)
    try:
        return Song(song_id, title, artist, duration)
    except ValueError as error:
        print("  ! %s" % error)
        return None


# ----------------------------------------------------------------------
# Display helpers
# ----------------------------------------------------------------------
def show_playlist(playlist):
    if playlist.is_empty():
        print("  (the playlist is empty)")
        return
    print()
    for line in playlist.to_lines(mark_current=True):
        print("  " + line)
    print("  ('>' marks the song that is currently playing)")
    print()


def show_reverse(playlist):
    if playlist.is_empty():
        print("  (the playlist is empty)")
        return
    print("\n  --- walked backwards, tail to head (proves prev links) ---")
    for line in playlist.to_lines_reverse():
        print("  " + line)
    print()


def show_stats(playlist):
    total = playlist.total_duration()
    count = len(playlist)
    average = (total / count) if count else 0
    print("\n  songs      : %d" % count)
    print("  total time : %d:%02d" % (total // 60, total % 60))
    print("  average    : %d:%02d" % (int(average) // 60, int(average) % 60))
    print("  memory note: %d nodes x 2 pointers = %d links to keep in sync\n"
          % (count, count * 2))


# ----------------------------------------------------------------------
# Menu actions
# ----------------------------------------------------------------------
def action_add(playlist):
    song = read_song(playlist)
    if song is not None:
        playlist.append(song)
        print("  + added '%s' at the end" % song.title)


def action_insert(playlist):
    song = read_song(playlist)
    if song is None:
        return
    position = ask_int("  Position (0 = first, %d = last): " % len(playlist),
                       low=0, high=len(playlist))
    playlist.insert_at(position, song)
    print("  + inserted '%s' at position %d" % (song.title, position))


def action_delete(playlist):
    if playlist.is_empty():
        print("  ! nothing to delete, the playlist is empty")
        return
    title = ask_text("  Title to delete: ")
    removed = playlist.remove_by_title(title)
    print("  - removed '%s'" % removed.title)


def action_move(playlist, direction):
    if playlist.is_empty():
        print("  ! the playlist is empty")
        return
    title = ask_text("  Title to move: ")
    node = playlist.find(title)
    if node is None:
        print("  ! no song titled '%s'" % title)
        return
    before = playlist.index_of(node)
    moved = playlist.move_up(node) if direction == "up" else playlist.move_down(node)
    if not moved:
        print("  ! '%s' is already at the %s" % (node.data.title,
              "top" if direction == "up" else "bottom"))
        return
    print("  ~ '%s' moved from position %d to %d"
          % (node.data.title, before, playlist.index_of(node)))


def action_next(playlist, wrap_choice):
    if playlist.is_empty():
        print("  ! the playlist is empty, nothing to play")
        return
    song = playlist.next_song(wrap=wrap_choice)
    if song is None:
        print("  ! '%s' is the last song - end of playlist"
              % playlist.now_playing().title)
        return
    print("  > now playing: %s - %s (%s)"
          % (song.title, song.artist, song.duration_text()))


def action_prev(playlist, wrap_choice):
    if playlist.is_empty():
        print("  ! the playlist is empty, nothing to play")
        return
    song = playlist.prev_song(wrap=wrap_choice)
    if song is None:
        print("  ! '%s' is the first song - start of playlist"
              % playlist.now_playing().title)
        return
    print("  > now playing: %s - %s (%s)"
          % (song.title, song.artist, song.duration_text()))


def action_shuffle(playlist):
    if playlist.size < 2:
        print("  ! need at least 2 songs to shuffle")
        return
    shuffle_module.shuffle(playlist)
    print("  ~ shuffled %d songs. New order:" % playlist.size)
    show_playlist(playlist)


def action_save(playlist, state):
    path = state["file"]
    typed = input("  File to save to [%s]: " % path).strip()
    if typed:
        path = typed
        state["file"] = path
    count = storage.save_playlist(playlist, path)
    print("  v saved %d songs to '%s'" % (count, path))


def action_load(playlist, state):
    path = state["file"]
    typed = input("  File to load from [%s]: " % path).strip()
    if typed:
        path = typed
        state["file"] = path
    try:
        loaded = storage.load_playlist(path)
    except storage.StorageError as error:
        print("  ! could not load: %s" % error)
        print("    (your current playlist was not changed)")
        return
    state["playlist"] = loaded
    print("  v loaded %d songs from '%s'" % (len(loaded), path))
    show_playlist(loaded)


# ----------------------------------------------------------------------
# Main loop
# ----------------------------------------------------------------------
def main():
    state = {"playlist": Playlist(), "file": DEFAULT_FILE}
    wrap_choice = False

    print("\nWelcome to the Music Playlist Manager (doubly linked list demo).")

    while True:
        playlist = state["playlist"]
        print(MENU)
        print("  %d song(s) loaded" % len(playlist))
        choice = ask_int("  Choose an option: ", low=0, high=13)

        try:
            if choice == 1:
                action_add(playlist)
            elif choice == 2:
                action_insert(playlist)
            elif choice == 3:
                show_playlist(playlist)
            elif choice == 4:
                show_reverse(playlist)
            elif choice == 5:
                action_next(playlist, wrap_choice)
            elif choice == 6:
                action_prev(playlist, wrap_choice)
            elif choice == 7:
                action_move(playlist, "up")
            elif choice == 8:
                action_move(playlist, "down")
            elif choice == 9:
                action_delete(playlist)
            elif choice == 10:
                action_shuffle(playlist)
            elif choice == 11:
                action_save(playlist, state)
            elif choice == 12:
                action_load(playlist, state)
            elif choice == 13:
                show_stats(playlist)
            elif choice == 0:
                print("\n  bye.\n")
                return 0
        except PlaylistError as error:
            # every rule violation surfaces as one clean line, never a traceback
            print("  ! %s" % error)
        except KeyboardInterrupt:
            print("\n\n  interrupted. bye.\n")
            return 0
        except EOFError:
            print("\n  bye.\n")
            return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n  bye.\n")
        sys.exit(0)
