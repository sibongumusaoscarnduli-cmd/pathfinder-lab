# Validation — 25 October 2026

## Automated

`python3 -m unittest discover -s tests -v`: 13 tests passed. Includes 150 deterministic random maps checked with both search algorithms against an independent relaxation oracle, input errors, unreachable and same-endpoint cases, route integrity and CLI exit codes.

## Browser checks

- Pinned Pyodide 0.27.7 successfully initialized in a worker.
- Expensive shortcut: both route costs 23; Dijkstra settled 206 cells and A* settled 74.
- Blocked scenario: no route reported by both algorithms.
- Paint a clear cell through the barrier: old results cleared; rerun found cost 15.
- Switch to Dijkstra, move exploration slider to beginning: zero settled cells displayed.
- JSON download completed as pathfinder-comparison.json.
- Desktop layout inspected visually.

These are synthetic scenarios and do not establish performance on real transport networks. Public deployment verification is recorded in the portfolio PLAN after publishing.
