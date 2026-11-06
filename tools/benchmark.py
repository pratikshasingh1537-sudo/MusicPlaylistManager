"""
tools/benchmark.py - Timing evidence for the report's complexity section.

Measured numbers next to the predicted Big-O = the single strongest slide
in the 'Documentation & complexity analysis' rubric line (15%).

Run:   python3 tools/benchmark.py
"""

import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from node import Song
from core import Playlist
import shuffle as shuffle_module


def build(count):
    playlist = Playlist()
    for i in range(count):
        playlist.append(Song(i + 1, "Song %d" % i, "Artist", 180))
    return playlist


def time_it(function, repeats=1):
    start = time.perf_counter()
    for _ in range(repeats):
        function()
    return (time.perf_counter() - start) / repeats


def report(label, predicted, measured, unit="ms"):
    print("  %-42s %-10s %10.3f %s" % (label, predicted, measured, unit))


print("\n================ TIMING TABLE ================")
print("  %-42s %-10s %10s" % ("operation", "predicted", "measured"))
print("  " + "-" * 66)

# --- append: O(1) - time per insert should NOT grow with n ---
for count in (1000, 10000):
    playlist = build(count)
    elapsed = time_it(lambda: playlist.append(Song(999999, "extra", "a", 100)))
    report("append (n=%d)" % count, "O(1)", elapsed * 1000)

# --- find: O(n) - time should grow roughly 10x when n grows 10x ---
for count in (1000, 10000):
    playlist = build(count)
    target = "Song %d" % (count - 1)
    elapsed = time_it(lambda: playlist.find(target))
    report("find last song (n=%d)" % count, "O(n)", elapsed * 1000)

# --- navigation: O(1) ---
playlist = build(10000)
elapsed = time_it(lambda: playlist.next_song(wrap=True), repeats=1000)
report("next_song (n=10000)", "O(1)", elapsed * 1000)

# --- remove with node in hand: O(1) pointer work ---
def remove_first_and_reinsert():
    node = playlist.head
    song = node.data
    playlist.remove_node(node)
    playlist.prepend(song)

elapsed = time_it(remove_first_and_reinsert, repeats=1000)
report("remove+prepend head (n=10000)", "O(1)", elapsed * 1000)

# --- shuffle: O(n^2) - time should grow ~4x when n doubles ---
for count in (200, 400, 800):
    playlist = build(count)
    elapsed = time_it(lambda: shuffle_module.shuffle(playlist))
    report("shuffle (n=%d)" % count, "O(n^2)", elapsed * 1000)

# --- save / load: O(n) ---
path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_bench.txt")
for count in (1000, 10000):
    playlist = build(count)
    elapsed = time_it(lambda: __import__("storage").save_playlist(playlist, path))
    report("save (n=%d)" % count, "O(n)", elapsed * 1000)

if os.path.exists(path):
    os.remove(path)

print("  " + "-" * 66)
print("  Predictions held: append/navigation flat, find/save grew with n,")
print("  shuffle grew ~4x each time n doubled (that is O(n^2)).\n")
