# Pathfinder Lab

An interactive weighted-route explorer built in **Python**. Paint obstacles and expensive terrain, then compare Dijkstra with A*. The live app runs the actual Python engine via Pyodide in a Web Worker; JavaScript handles controls and rendering only.

**Live app:** https://sibongumusaoscarnduli-cmd.github.io/pathfinder-lab/

## What this demonstrates

- Data structures and algorithms: adjacency generation, heap-based priority queues, predecessor maps, shortest paths and consistent heuristics.
- Software engineering: one reusable engine shared between CLI and browser, input validation, deterministic tests and explicit failure states.
- Testing: 150 seeded random maps checked against an independent Bellman-Ford-style oracle, plus route integrity and edge cases.
- UI development: interactive editing, algorithm comparison, exploration slider, accessible cell labels and JSON export.

This is an original learning project created with AI assistance. It demonstrates concepts from Computer Science coursework; it is not represented as a university assignment or independently authored student work.

## Run locally

Python 3.9+; no pip packages needed for the CLI or tests.

```sh
python3 -m unittest discover -s tests -v
python3 cli.py example.json
python3 -m http.server 8087 --bind 127.0.0.1 --directory docs
```

Open http://127.0.0.1:8087/. Browser mode requires internet for the pinned Pyodide runtime from jsDelivr. There is no backend, account, API key or paid hosting. Python CLI works offline.

## Map contract

```json
{"grid": [[1, 5, 1], [1, null, 1], [1, 1, 1]], "start": [0, 0], "goal": [0, 2]}
```

Coordinates are zero-based `[row, column]`. Cells have integer cost 1–9, or `null` for walls. Grids must be rectangular and at most 60×60. Movement is orthogonal, not diagonal. Entering a cell pays its cost; the starting cell is free. Endpoints must be traversable and may coincide in the engine. The UI keeps them distinct for easier editing.

Results contain `found`, `cost`, `path`, `expanded` and `algorithm`. Unreachable routes have `cost: null` and an empty path. `expanded` records settled nodes, including the start and goal when reached. The CLI exits 2 for malformed input or file errors, and 0 for a valid search including an unreachable route.

## Architecture

```text
Grid controls → worker → Python engine → JSON results → map / trace / export
                              ↑
                        CLI and tests
```

`docs/engine.py` is the single source of truth. The worker loads that file and calls `compare_json`; user input is passed as JSON data, never interpolated as Python code. Search runs off the UI thread. Editing invalidates stale results and editing is disabled while a comparison is in flight.

Dijkstra orders the frontier by accumulated cost. A* orders by cost plus Manhattan distance multiplied by the minimum traversable cell cost. This heuristic is admissible and consistent for positive-cost four-way grids. Both algorithms therefore find a minimum-cost route. Equal-priority A* entries prefer a smaller heuristic, then cost and coordinates. This is deterministic but may choose a different optimal route from Dijkstra.

For V cells and E ≤ 4V directed moves, search takes O((V+E) log V) time and O(V+E) space using a heap with stale entries. Each settled cell appears once in the trace. A* can settle fewer cells on suitable maps, but this is not a universal performance guarantee. No wall-clock benchmark claims are made.

## Test and review notes

See [VALIDATION.md](VALIDATION.md) for recorded checks and [REVIEW.md](REVIEW.md) for the local code review. No remote automated-review pass or CI badge is claimed. The Code Review connector available during creation supplies PR check diagnostics, not a standalone source reviewer.

## Deployment

GitHub Pages serves `main:/docs`. The Python process runs in each visitor's browser, not on GitHub's servers. `.nojekyll` keeps static assets untouched. No private documents, credentials or real map data are included. Only synthetic grid scenarios are bundled.

Pyodide is pinned to 0.27.7 using the official documented CDN. The CDN receives normal runtime-download requests (such as IP and browser metadata); map contents are not uploaded. Runtime download can be slow or blocked: the interface reports loading/errors rather than showing fake results. The local CLI remains available. This is not production routing, accessibility guidance or navigation software.

## Interview walkthrough

1. Run the expensive-shortcut scenario and explain why the cheapest route is not necessarily the fewest moves.
2. Change to the blocked scenario. Explain why an empty route is a valid result.
3. Show the two expansion counts. Derive Manhattan distance and explain why diagonal movement would require changing the heuristic.
4. Explain stale heap entries, parent reconstruction, tie-breaking and the positive-weight restriction.
5. Open the independent oracle test and explain why a second algorithm is stronger evidence than testing only known outputs.
6. Make and test your own enhancement before claiming personal authorship: add diagonal movement with a proven heuristic, a map import validator, or a bidirectional search.

## References and licence

Original implementation; no third-party repository source copied. Algorithm background: [Dijkstra's original shortest-path paper](https://doi.org/10.1007/BF01386390) and [A* original paper](https://doi.org/10.1109/TSSC.1968.300136). Runtime integration follows [Pyodide's official quickstart](https://pyodide.org/en/stable/usage/quickstart.html). Pyodide and its bundled Python runtime retain their upstream licences; they are loaded from the CDN, not vendored here. Project code is MIT licensed; see LICENSE.
