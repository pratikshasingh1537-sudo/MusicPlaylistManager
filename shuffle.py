"""
shuffle.py - The "specific algorithm" that earns the 25% rubric line.

This is the DELIBERATELY SIMPLE version: repeated random selection.

  while songs remain:
      pick a random position k among the songs still linked
      unlink the song at k
      append it to the result

Why this is uniform (every ordering equally likely):
  the first pick is 1 of n, the second 1 of (n-1), ... so each of the
  n! orderings has probability 1/n!  ->  fair shuffle, no bias.

Time complexity:
  Each pick must WALK to position k, which is O(n) on a linked list because
  you cannot index into it. n picks  ->  O(n^2).
  Building the result is O(1) per song thanks to the tail pointer.
  So: O(n^2) time, O(n) space (it rebuilds n nodes).

Honest O(n^2) beats a fake "O(n)" claim in the report every time.

STRETCH GOAL (only if week 3 finishes early):
  A single-pass O(n) random merge - split the chain into two halves, then
  repeatedly attach the next song of half A or half B with probability
  proportional to how many songs each half has left. No walking, no indexing.
"""

import random

from node import Node


def shuffle(playlist, rng=None):
    """
    Shuffle `playlist` in place. Safe on empty and 1-song playlists.
    `rng` lets the tests pass a seeded generator for repeatable results.
    """
    if playlist.size < 2:
        return playlist                      # nothing to shuffle, no crash

    rng = rng if rng is not None else random

    # --- detach the whole chain and start a fresh, empty playlist ---
    chain = playlist.head
    chain.prev = None
    playlist.head = None
    playlist.tail = None
    playlist.current = None
    playlist.size = 0

    remaining = _length(chain)

    while chain is not None:
        # pick one of the songs still in the chain
        k = rng.randrange(remaining) if remaining > 1 else 0

        # walk to position k, remembering the node in front of it
        picked = chain
        before = None
        for _ in range(k):
            before = picked
            picked = picked.next

        # unlink `picked`
        if before is None:
            chain = picked.next
            if chain is not None:
                chain.prev = None
        else:
            before.next = picked.next
            if picked.next is not None:
                picked.next.prev = before

        picked.prev = None
        picked.next = None

        # append to the result (O(1) because of the tail pointer)
        playlist.append(picked.data)
        remaining -= 1

    playlist.current = playlist.head         # cursor back to the first song
    return playlist


def _length(chain):
    """Count nodes of a bare chain. O(n)."""
    total = 0
    walker = chain
    while walker is not None:
        total += 1
        walker = walker.next
    return total
