"""
core.py - The heart of the project: the doubly linked list itself.

House rules for this file (they protect your 30%):
  1. No print() and no input() anywhere in here.
     The CLI lives in main.py, the tests live in tests/. This file is pure logic.
  2. No Python list / dict / deque is used to STORE the playlist.
     head -> node -> node -> ... -> tail  is the only storage.
     (Lists appear only as throwaway text containers for printing / saving,
      which is clearly marked each time.)
"""

from node import Node, Song


class PlaylistError(Exception):
    """Any playlist-level rule violation (bad index, empty list, ...)."""
    pass


class Playlist:
    """
    A doubly linked list of songs with a 'now playing' cursor.

    head    -> first node      (None when empty)
    tail    -> last node       (None when empty)
    current -> the now-playing node (None when empty)
    size    -> number of songs, kept as a counter so len() is O(1)
    """

    def __init__(self):
        self.head = None
        self.tail = None
        self.current = None
        self.size = 0

    # ------------------------------------------------------------------
    # Basic state
    # ------------------------------------------------------------------
    def is_empty(self):
        return self.size == 0

    def __len__(self):
        return self.size

    def clear(self):
        self.head = None
        self.tail = None
        self.current = None
        self.size = 0

    # ------------------------------------------------------------------
    # INSERT  - three cases: empty list, at an end, in the middle
    # ------------------------------------------------------------------
    def append(self, song):
        """Add at the tail. O(1) because we keep a tail pointer."""
        node = Node(song)
        if self.tail is None:                 # empty list
            self.head = node
            self.tail = node
            self.current = node               # first song becomes 'now playing'
        else:
            node.prev = self.tail
            self.tail.next = node
            self.tail = node
        self.size += 1
        return node

    def prepend(self, song):
        """Add at the head. O(1)."""
        node = Node(song)
        if self.head is None:
            self.head = node
            self.tail = node
            self.current = node
        else:
            node.next = self.head
            self.head.prev = node
            self.head = node
        self.size += 1
        return node

    def insert_at(self, index, song):
        """Add so the new song ends up at position `index`. O(n) - we must walk."""
        if index < 0 or index > self.size:
            raise PlaylistError(
                "position %d is out of range (valid: 0 to %d)" % (index, self.size))
        if index == 0:
            return self.prepend(song)
        if index == self.size:
            return self.append(song)

        after = self._node_at(index)          # new node goes just before this one
        before = after.prev
        node = Node(song, prev=before, next=after)
        before.next = node
        after.prev = node
        self.size += 1
        return node

    # ------------------------------------------------------------------
    # LOOKUP - O(n)
    # ------------------------------------------------------------------
    def _node_at(self, index):
        """Walk to the node at `index`. O(n). Private helper."""
        if index < 0 or index >= self.size:
            raise PlaylistError(
                "position %d is out of range (valid: 0 to %d)" % (index, self.size - 1))
        node = self.head
        for _ in range(index):
            node = node.next
        return node

    def index_of(self, node):
        """Position of a node, or -1. O(n)."""
        i = 0
        walker = self.head
        while walker is not None:
            if walker is node:
                return i
            walker = walker.next
            i += 1
        return -1

    def find(self, title):
        """First node whose title matches (case-insensitive), else None. O(n)."""
        wanted = title.strip().lower()
        walker = self.head
        while walker is not None:
            if walker.data.title.lower() == wanted:
                return walker
            walker = walker.next
        return None

    def find_by_id(self, song_id):
        walker = self.head
        while walker is not None:
            if walker.data.song_id == song_id:
                return walker
            walker = walker.next
        return None

    # ------------------------------------------------------------------
    # DELETE - pure pointer surgery, O(1) once you hold the node
    # ------------------------------------------------------------------
    def remove_node(self, node):
        """Unlink one node. O(1). Returns the Song it held."""
        if node is None:
            raise PlaylistError("cannot remove: song not found")

        before = node.prev
        after = node.next

        if before is not None:                # not the head
            before.next = after
        else:
            self.head = after

        if after is not None:                 # not the tail
            after.prev = before
        else:
            self.tail = before

        # If we deleted the song that was playing, move the cursor sensibly:
        # prefer the next song, fall back to the previous one.
        if self.current is node:
            self.current = after if after is not None else before

        node.prev = None
        node.next = None
        self.size -= 1

        if self.size == 0:                    # deleting the very last song
            self.head = None
            self.tail = None
            self.current = None

        return node.data

    def remove_at(self, index):
        return self.remove_node(self._node_at(index))

    def remove_by_title(self, title):
        node = self.find(title)
        if node is None:
            raise PlaylistError("no song titled '%s' in this playlist" % title)
        return self.remove_node(node)

    # ------------------------------------------------------------------
    # REORDER - the adjacency-swap case students usually get wrong
    # ------------------------------------------------------------------
    def _swap_with_prev(self, node):
        """Swap `node` with the node before it, touching only 6 pointers. O(1)."""
        before = node.prev
        if before is None:
            return False
        top = before.prev
        after = node.next

        # detach the pair from the rest of the chain
        before.next = after
        if after is not None:
            after.prev = before
        else:
            self.tail = before                # 'before' became the last node

        node.prev = top
        if top is not None:
            top.next = node
        else:
            self.head = node                  # 'node' became the first node

        before.prev = node
        node.next = before
        return True

    def move_up(self, node):
        """Move a song one place earlier. O(1) relink (+ O(n) to locate)."""
        return self._swap_with_prev(node)

    def move_down(self, node):
        """Move a song one place later. O(1) relink (+ O(n) to locate)."""
        if node is None or node.next is None:
            return False
        return self._swap_with_prev(node.next)

    # ------------------------------------------------------------------
    # NAVIGATION - the O(1) win that justifies the doubly linked list
    # ------------------------------------------------------------------
    def next_song(self, wrap=False):
        """Play the next song. O(1). Returns None if already at the end."""
        if self.current is None:
            return None
        if self.current.next is None:
            if wrap:
                self.current = self.head
                return self.current.data
            return None
        self.current = self.current.next
        return self.current.data

    def prev_song(self, wrap=False):
        """Play the previous song. O(1) thanks to the prev link."""
        if self.current is None:
            return None
        if self.current.prev is None:
            if wrap:
                self.current = self.tail
                return self.current.data
            return None
        self.current = self.current.prev
        return self.current.data

    def now_playing(self):
        return self.current.data if self.current is not None else None

    # ------------------------------------------------------------------
    # TRAVERSAL / REPORTING
    # ------------------------------------------------------------------
    def to_lines(self, mark_current=False):
        """
        Walk head -> tail and build printable lines. O(n).
        NOTE: the Python list here is only a text container for the caller.
              The playlist itself is still the linked list, not this list.
        """
        lines = []
        walker = self.head
        position = 0
        while walker is not None:
            marker = "> " if (mark_current and walker is self.current) else "  "
            lines.append("%s%2d. %-28s %-20s %s" % (
                marker, position, walker.data.title,
                walker.data.artist, walker.data.duration_text()))
            walker = walker.next
            position += 1
        return lines

    def to_lines_reverse(self):
        """
        Walk tail -> head. O(n).
        This is the cheapest way to PROVE the prev links are correct:
        if any prev is wrong, the reverse walk breaks or prints garbage.
        """
        lines = []
        walker = self.tail
        while walker is not None:
            lines.append("%-28s %s" % (walker.data.title, walker.data.duration_text()))
            walker = walker.prev
        return lines

    def total_duration(self):
        """Sum of all durations. O(n)."""
        total = 0
        walker = self.head
        while walker is not None:
            total += walker.data.duration_sec
            walker = walker.next
        return total

    def next_free_id(self):
        """Smallest unused positive song id. O(n)."""
        highest = 0
        walker = self.head
        while walker is not None:
            if walker.data.song_id > highest:
                highest = walker.data.song_id
            walker = walker.next
        return highest + 1
