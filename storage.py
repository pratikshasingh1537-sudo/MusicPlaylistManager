"""
storage.py - Save / load the playlist as a plain text file. O(n) each.

File format: one song per line, four fields, pipe separated.

    1|Kesariya|Aritjit Singh|268
    2|Believer|Imagine Dragons|204|

Why plain text and not JSON/CSV?
  json.load() would hand back Python dicts and lists for the data we are
  supposed to be storing in a hand-built structure - awkward to defend
  against the "no built-in structures" rule. A hand-written parser keeps
  the whole project honest and is ~20 lines.
  (Also gives you real error handling to demo: missing file, bad field count,
   non-numeric duration.)
"""

from node import Song, SEP
from core import Playlist


class StorageError(Exception):
    """Raised for any file problem, always with a helpful message."""
    pass


def save_playlist(playlist, path):
    """Write every song, head to tail. Returns how many were written. O(n)."""
    records = []                              # scratch text buffer, not storage
    walker = playlist.head
    while walker is not None:
        records.append(walker.data.to_record())
        walker = walker.next

    try:
        handle = open(path, "w", encoding="utf-8")
    except OSError as error:
        raise StorageError("could not open '%s' for writing (%s)" % (path, error))

    with handle:
        for record in records:
            handle.write(record + "\n")

    return len(records)


def load_playlist(path):
    """
    Read the file and rebuild the linked list. O(n).
    Raises StorageError with the offending line number on bad data.
    The caller's existing playlist is left untouched if this raises.
    """
    try:
        handle = open(path, "r", encoding="utf-8")
    except FileNotFoundError:
        raise StorageError("no saved playlist at '%s'" % path)
    except OSError as error:
        raise StorageError("could not read '%s' (%s)" % (path, error))

    playlist = Playlist()
    line_number = 0

    with handle:
        for raw in handle:
            line_number += 1
            line = raw.strip()

            if not line or line.startswith("#"):     # blank lines / comments
                continue

            parts = line.split(SEP)
            if len(parts) != 4:
                raise StorageError(
                    "line %d: expected 4 fields (id|title|artist|seconds), got %d"
                    % (line_number, len(parts)))

            id_text, title, artist, duration_text = parts

            try:
                song_id = int(id_text.strip())
                duration = int(duration_text.strip())
            except ValueError:
                raise StorageError(
                    "line %d: id and duration must be whole numbers" % line_number)

            try:
                song = Song(song_id, title, artist, duration)
            except ValueError as error:
                raise StorageError("line %d: %s" % (line_number, error))

            playlist.append(song)

    return playlist
