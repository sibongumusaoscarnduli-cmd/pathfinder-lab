"""Weighted grid search. Entering a cell pays its positive integer cost."""
import heapq
import json
from math import inf


def validate(grid, start, goal):
    if not isinstance(grid, list) or not 1 <= len(grid) <= 60:
        raise ValueError('Grid must contain 1–60 rows.')
    if not isinstance(grid[0], list) or not 1 <= len(grid[0]) <= 60:
        raise ValueError('Grid must contain 1–60 columns.')
    width = len(grid[0])
    for row in grid:
        if not isinstance(row, list) or len(row) != width:
            raise ValueError('Grid must be rectangular.')
        for cost in row:
            if cost is not None and (type(cost) is not int or not 1 <= cost <= 9):
                raise ValueError('Costs must be integers 1–9; null represents a wall.')
    for point in (start, goal):
        if not isinstance(point, (list, tuple)) or len(point) != 2 or any(type(x) is not int for x in point):
            raise ValueError('Endpoints must be [row, column] integer pairs.')
        r, c = point
        if not (0 <= r < len(grid) and 0 <= c < width) or grid[r][c] is None:
            raise ValueError('Endpoints must lie on traversable cells.')


def search(grid, start, goal, algorithm='astar'):
    """Return an optimal path, total cost and expansion trace (four-way moves).

    A* uses Manhattan distance times minimum traversable cost: a consistent
    heuristic. Ties prefer smaller remaining distance, then row and column.
    Both algorithms settle each cell at most once; stale heap entries are skipped.
    """
    validate(grid, start, goal)
    if algorithm not in ('astar', 'dijkstra'):
        raise ValueError('Algorithm must be astar or dijkstra.')
    start, goal = tuple(start), tuple(goal)
    minimum = min(v for row in grid for v in row if v is not None)

    def heuristic(p):
        return minimum * (abs(p[0] - goal[0]) + abs(p[1] - goal[1])) if algorithm == 'astar' else 0

    distance, parent, settled, trace = {start: 0}, {}, set(), []
    queue = [(heuristic(start), heuristic(start), 0, start)]
    while queue:
        _, _, cost, here = heapq.heappop(queue)
        if here in settled or cost != distance[here]:
            continue
        settled.add(here)
        trace.append(list(here))
        if here == goal:
            path = [goal]
            while path[-1] != start:
                path.append(parent[path[-1]])
            return dict(algorithm=algorithm, found=True, cost=cost,
                        path=[list(p) for p in reversed(path)], expanded=trace)
        r, c = here
        for nxt in ((r-1, c), (r, c+1), (r+1, c), (r, c-1)):
            nr, nc = nxt
            if not (0 <= nr < len(grid) and 0 <= nc < len(grid[0])) or grid[nr][nc] is None:
                continue
            candidate = cost + grid[nr][nc]
            if candidate < distance.get(nxt, inf):
                distance[nxt], parent[nxt] = candidate, here
                h = heuristic(nxt)
                heapq.heappush(queue, (candidate + h, h, candidate, nxt))
    return dict(algorithm=algorithm, found=False, cost=None, path=[], expanded=trace)


def compare_json(payload):
    request = json.loads(payload)
    if not isinstance(request, dict):
        raise ValueError('Request must be an object.')
    try:
        grid, start, goal = request['grid'], request['start'], request['goal']
    except KeyError as exc:
        raise ValueError('Request requires grid, start and goal.') from exc
    return json.dumps({name: search(grid, start, goal, name) for name in ('dijkstra', 'astar')})
