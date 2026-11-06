"""
node.py - The two smallest pieces of the project.

Nothing in this file knows about lists, menus or files.
It only defines what ONE song looks like and what ONE link looks like.
"""

SEP = "|"   # field separator used by storage.py


class Song:
    """A single song's data. No links here - just values."""

    def __init__(self, song_id, title, artist, duration_sec):
        # --- validation: reject bad data right where it enters the program ---
        if not isinstance(song_id, int) or song_id <= 0:
            raise ValueError("song id must be a positive whole number")

        if not isinstance(title, str) or not title.strip():
            raise ValueError("title cannot be empty")

        if SEP in title or "\n" in title:
            raise ValueError("title cannot contain '%s' or a line break" % SEP)

        if not isinstance(duration_sec, int) or duration_sec < 0:
            raise ValueError("duration must be a whole number of seconds, 0 or more")

        self.song_id = song_id
        self.title = title.strip()
        self.artist = artist.strip() if isinstance(artist, str) else ""
        self.duration_sec = duration_sec

    def duration_text(self):
        """268 -> '4:28'. Keeps the CLI tidy."""
        minutes = self.duration_sec // 60
        seconds = self.duration_sec % 60
        return "%d:%02d" % (minutes, seconds)

    def to_record(self):
        """One line of the save file."""
        return SEP.join([
            str(self.song_id),
            self.title,
            self.artist,
            str(self.duration_sec),
        ])

    def __repr__(self):
        return "Song(%d, %r, %r, %d)" % (
            self.song_id, self.title, self.artist, self.duration_sec)


class Node:
    """
    One link of the doubly linked list.

    data  -> the Song
    prev  -> the node before this one (None at the head)
    next  -> the node after this one  (None at the tail)

    Having BOTH directions is the whole reason 'previous song' is O(1)
    instead of O(n). Say exactly that in your viva.
    """

    def __init__(self, data, prev=None, next=None):
        self.data = data
        self.prev = prev
        self.next = next

    def __repr__(self):
        return "Node(%r)" % (self.data,)
