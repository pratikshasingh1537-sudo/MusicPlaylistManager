"""
tests/test_core.py - Automated tests for the data structure.

No pytest needed: plain asserts and a tiny runner, so it works anywhere.

Run:    python3 tests/test_core.py
If any line prints FAIL, that test is broken. All PASS = the 30% is solid.
"""

import os
import sys
import random

# let the tests import the modules in the parent folder
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from node import Song, Node
from core import Playlist, PlaylistError
import shuffle as shuffle_module
import storage

PASSED = 0
FAILED = 0


def check(label, condition):
    global PASSED, FAILED
    if condition:
        PASSED += 1
        print("  PASS  %s" % label)
    else:
        FAILED += 1
        print("  FAIL  %s" % label)


def expect_error(label, function, error_type=PlaylistError):
    global PASSED, FAILED
    try:
        function()
    except error_type:
        PASSED += 1
        print("  PASS  %s (rejected correctly)" % label)
    except Exception as other:
        FAILED += 1
        print("  FAIL  %s (wrong error: %r)" % (label, other))
    else:
        FAILED += 1
        print("  FAIL  %s (did not reject bad input)" % label)


def make_song(song_id, title, seconds=200):
    return Song(song_id, title, "Artist %d" % song_id, seconds)


def build(names):
    playlist = Playlist()
    for i, name in enumerate(names):
        playlist.append(make_song(i + 1, name))
    return playlist


def titles(playlist):
    """Read the list into a plain list of strings - test-only convenience."""
    return [line.split(". ", 1)[1][:28].strip() for line in playlist.to_lines()]


def check_links(playlist):
    """Re-walk both directions and confirm every link agrees."""
    forward = 0
    walker = playlist.head
    last = None
    while walker is not None:
        if walker.prev is not last:
            return False
        last = walker
        walker = walker.next
        forward += 1
    if last is not playlist.tail:
        return False
    if forward != playlist.size:
        return False
    backward = 0
    walker = playlist.tail
    while walker is not None:
        walker = walker.prev
        backward += 1
    return backward == playlist.size


# ----------------------------------------------------------------------
print("\n--- empty playlist ---")
empty = Playlist()
check("fresh playlist is empty", empty.is_empty())
check("size is 0", len(empty) == 0)
check("head/tail/current are None",
      empty.head is None and empty.tail is None and empty.current is None)
check("next_song() on empty returns None", empty.next_song() is None)
check("prev_song() on empty returns None", empty.prev_song() is None)
check("now_playing() on empty returns None", empty.now_playing() is None)
check("shuffle on empty does not crash", shuffle_module.shuffle(empty) is empty)
check("to_lines() on empty is empty", empty.to_lines() == [])
expect_error("remove_at on empty", lambda: empty.remove_at(0))

# ----------------------------------------------------------------------
print("\n--- insert: append / prepend / insert_at ---")
p = build(["A"])
check("one song: head is tail", p.head is p.tail)
check("first appended song becomes current", p.now_playing().title == "A")

p = build(["A", "B", "C", "D"])
check("append keeps order", titles(p) == ["A", "B", "C", "D"])
check("size is 4", len(p) == 4)
check("tail is D", p.tail.data.title == "D")
check("links all consistent after appends", check_links(p))

p.prepend(make_song(9, "Z"))
check("prepend puts song first", titles(p) == ["Z", "A", "B", "C", "D"])
check("links consistent after prepend", check_links(p))

p.insert_at(2, make_song(10, "M"))
check("insert_at middle", titles(p) == ["Z", "A", "M", "B", "C", "D"])
p.insert_at(0, make_song(11, "Q"))
check("insert_at index 0", titles(p)[0] == "Q")
p.insert_at(len(p), make_song(12, "END"))
check("insert_at index == size appends", titles(p)[-1] == "END")
check("links consistent after inserts", check_links(p))
expect_error("insert_at beyond size", lambda: p.insert_at(99, make_song(13, "X")))
expect_error("insert_at negative", lambda: p.insert_at(-1, make_song(13, "X")))

# ----------------------------------------------------------------------
print("\n--- search ---")
p = build(["Kesariya", "Believer", "Thunder"])
check("find exact", p.find("Believer").data.title == "Believer")
check("find is case-insensitive", p.find("believer").data.title == "Believer")
check("find missing returns None", p.find("Nope") is None)
check("index_of head is 0", p.index_of(p.head) == 0)
check("index_of tail is size-1", p.index_of(p.tail) == len(p) - 1)

# ----------------------------------------------------------------------
print("\n--- delete ---")
p = build(["A", "B", "C"])
p.remove_by_title("A")
check("delete head", titles(p) == ["B", "C"] and p.head.data.title == "B")
check("links consistent after head delete", check_links(p))
p = build(["A", "B", "C"])
p.remove_by_title("C")
check("delete tail", titles(p) == ["A", "B"] and p.tail.data.title == "B")
check("links consistent after tail delete", check_links(p))
p = build(["A", "B", "C"])
p.remove_by_title("B")
check("delete middle", titles(p) == ["A", "C"])
check("links consistent after middle delete", check_links(p))
check("middle delete repaired prev link",
      p.head.next.prev is p.head and p.tail.prev is p.head)

p = build(["only"])
p.remove_by_title("only")
check("delete the only song empties the list",
      p.is_empty() and p.head is None and p.tail is None and p.current is None)
expect_error("delete a title that is not there", lambda: p.remove_by_title("ghost"))

p = build(["A", "B", "C"])
p.next_song(); p.next_song()             # current is now C
p.remove_by_title("C")
check("deleting the current song moves the cursor back",
      p.now_playing().title == "B")
p = build(["A", "B", "C"])
p.remove_by_title("A")                   # A was current
check("deleting the current head moves cursor forward",
      p.now_playing().title == "B")

# ----------------------------------------------------------------------
print("\n--- navigation ---")
p = build(["A", "B", "C"])
check("starts on the first song", p.now_playing().title == "A")
check("next moves forward", p.next_song().title == "B")
check("prev moves back", p.prev_song().title == "A")
check("prev at head without wrap returns None", p.prev_song() is None)
p.current = p.tail
check("next at tail without wrap returns None", p.next_song() is None)
check("next at tail WITH wrap goes to head", p.next_song(wrap=True).title == "A")
check("prev at head WITH wrap goes to tail", p.prev_song(wrap=True).title == "C")

# ----------------------------------------------------------------------
print("\n--- reorder ---")
p = build(["A", "B", "C", "D"])
p.move_up(p.find("C"))
check("move_up middle", titles(p) == ["A", "C", "B", "D"])
check("links consistent after move_up", check_links(p))

p = build(["A", "B", "C", "D"])
p.move_down(p.find("B"))
check("move_down middle", titles(p) == ["A", "C", "B", "D"])
check("links consistent after move_down", check_links(p))

p = build(["A", "B", "C"])
check("move_up on first is refused", p.move_up(p.head) is False)
p.move_down(p.head)
check("move_down on first works", titles(p) == ["B", "A", "C"])
p = build(["A", "B", "C"])
check("move_down on last is refused", p.move_down(p.tail) is False)
p.move_up(p.tail)
check("move_up on last works", titles(p) == ["A", "C", "B"])
check("links consistent after end moves", check_links(p))

p = build(["A", "B"])
p.move_up(p.find("B"))
check("swap on a 2-song list", titles(p) == ["B", "A"])
check("links consistent after 2-song swap", check_links(p))

p = build(["A", "B", "C"])
kept = p.find("B")
p.move_up(kept); p.move_up(kept)
check("same node can be moved twice", titles(p) == ["B", "A", "C"])

# ----------------------------------------------------------------------
print("\n--- shuffle ---")
p = build(["A", "B", "C", "D", "E"])
before = titles(p)
shuffle_module.shuffle(p)
check("shuffle keeps exactly the same songs", sorted(titles(p)) == sorted(before))
check("shuffle keeps size", len(p) == 5)
check("shuffle keeps links consistent", check_links(p))
check("shuffle resets current to head", p.current is p.head)
single = build(["solo"])
shuffle_module.shuffle(single)
check("shuffle on a 1-song list is a no-op", titles(single) == ["solo"])

print("  (uniformity check - 6000 shuffles of 4 songs)")
counts = {}
order = build(["A", "B", "C", "D"])
rng = random.Random(1234)
for _ in range(6000):
    shuffle_module.shuffle(order, rng)
    key = "-".join(titles(order))
    counts[key] = counts.get(key, 0) + 1
check("all 24 orderings of 4 songs appear", len(counts) == 24)
spread = (max(counts.values()) - min(counts.values())) / 250.0
check("no ordering is wildly over/under-represented (spread %.2f%%)" % (spread * 100),
      spread < 0.30)

# ----------------------------------------------------------------------
print("\n--- save / load ---")
here = os.path.dirname(os.path.abspath(__file__))
temp_path = os.path.join(here, "_temp_playlist.txt")
p = build(["Kesariya", "Believer"])
p.append(Song(3, "Song With Spaces", "", 95))

saved = storage.save_playlist(p, temp_path)
check("save reports 3 records", saved == 3)
check("file was created", os.path.exists(temp_path))
load_back = storage.load_playlist(temp_path)
check("load restores the count", len(load_back) == 3)
check("load restores order", titles(load_back) == titles(p))
check("load restores empty artist", load_back.tail.data.artist == "")
check("load restores duration", load_back.tail.data.duration_sec == 95)
check("loaded list has consistent links", check_links(load_back))

expect_error("load a missing file",
             lambda: storage.load_playlist(os.path.join(here, "no_such_file.txt")),
             storage.StorageError)

bad_path = os.path.join(here, "_temp_bad.txt")
with open(bad_path, "w") as handle:
    handle.write("1|Fine|Someone|180\n2|Broken|Someone\n")
expect_error("load a file with a missing field",
             lambda: storage.load_playlist(bad_path), storage.StorageError)

with open(bad_path, "w") as handle:
    handle.write("1|Fine|Someone|not_a_number\n")
expect_error("load a file with a non-numeric duration",
             lambda: storage.load_playlist(bad_path), storage.StorageError)

with open(bad_path, "w") as handle:
    handle.write("\n\n# a comment line\n1|Ok|Someone|100\n\n")
check("load skips blanks and comments",
      len(storage.load_playlist(bad_path)) == 1)

for path in (temp_path, bad_path):
    if os.path.exists(path):
        os.remove(path)

# ----------------------------------------------------------------------
print("\n--- validation at the door ---")
expect_error("Song with empty title",
             lambda: Song(1, "   ", "x", 100), ValueError)
expect_error("Song with negative duration",
             lambda: Song(1, "x", "y", -5), ValueError)
expect_error("Song with zero/negative id",
             lambda: Song(0, "x", "y", 100), ValueError)
expect_error("Song with pipe in title (would break the save file)",
             lambda: Song(1, "bad|title", "y", 100), ValueError)

# ----------------------------------------------------------------------
print("\n--- scale: 1000 songs ---")
big = Playlist()
for i in range(1000):
    big.append(make_song(i + 1, "Song %d" % i, 180))
check("1000 appended", len(big) == 1000)
check("links consistent at 1000", check_links(big))
big.move_up(big.find("Song 999"))
check("reorder works at 1000", big.find("Song 999").prev is not None)
big.remove_node(big.head)
check("delete works at 1000", len(big) == 999)
check("links consistent after delete at 1000", check_links(big))

# ----------------------------------------------------------------------
print("\n==============================================")
print("  passed: %d    failed: %d" % (PASSED, FAILED))
print("==============================================\n")
sys.exit(1 if FAILED else 0)
