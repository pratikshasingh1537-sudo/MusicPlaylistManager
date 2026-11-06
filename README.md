# Music Playlist Manager - Doubly Linked List

DSA mini-project (B.Tech CSE Sem 3). A command-line music playlist built on a
**hand-written doubly linked list**. No built-in list/dict/deque stores the
playlist; every song is a `Node` with `prev` and `next` links.

## Run it

```bash
python3 main.py
```

## Run the tests

```bash
python3 tests/test_core.py      # 60+ assertions, no pytest needed
python3 tools/benchmark.py      # timing table for the report
```

## Files

| File | Role | Rubric line it earns |
|---|---|---|
| `node.py` | `Song` (data + validation) and `Node` (`prev`/`next`) | Core DS 30% |
| `core.py` | `Playlist`: insert, delete, search, traverse, reorder, navigate | Core DS 30% |
| `shuffle.py` | The shuffle algorithm (random selection, O(n^2)) | Algorithm 25% |
| `storage.py` | Save/load as plain `id\|title\|artist\|seconds` text | Core DS + interface |
| `main.py` | CLI menu, all input validation, error messages | Interface & testing 15% |
| `tests/test_core.py` | Automated tests incl. every edge case | Interface & testing 15% |
| `tools/benchmark.py` | Measured timings vs predicted Big-O | Documentation 15% |

## Complexity

| Operation | Time | Note |
|---|---|---|
| `append` / `prepend` | O(1) | `tail` pointer |
| `insert_at` | O(n) | must walk to the position |
| `find` / `find_by_id` | O(n) | linear scan |
| `remove_node` | O(1) | pure pointer surgery |
| `next_song` / `prev_song` | O(1) | `prev` link removes the backward search |
| `move_up` / `move_down` | O(n) locate, O(1) relink | 6 pointer assignments |
| `shuffle` | O(n^2) | stated honestly; O(n) merge is the stretch goal |
| `save` / `load` | O(n) | one pass |
| Space (whole list) | O(n) | 2 pointers per node |

## Design rules to keep

1. `core.py` never calls `print()` or `input()`.
2. All user-facing validation happens in `main.py`; data validation in `node.py`.
3. Every `PlaylistError` becomes one friendly CLI line, never a traceback.
4. Nothing in `core.py` stores songs in a Python list.

## Run the web app locally

The original CLI is still available with `python3 main.py`. To run the browser UI:

```bash
python -m venv .venv
# Windows PowerShell: .venv\\Scripts\\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Streamlit opens the app at `http://localhost:8501`.

## Deploy free with Streamlit Community Cloud

1. Push this project folder (including `app.py` and `requirements.txt`) to your GitHub repository.
2. Sign in at https://share.streamlit.io/ using GitHub and authorize access to the repository.
3. Select **Create app**, choose `pratikshasingh1537-sudo/MusicPlaylistManager`, branch `main`, and main file path `app.py`.
4. Click **Deploy**. Streamlit will install the packages from `requirements.txt` and provide a public URL.

The current app keeps playlist state in the active browser session. It does not provide a shared database or permanent cloud storage; downloading the playlist saves a text backup. For persistent multi-user accounts/storage, add a database in a later version.
