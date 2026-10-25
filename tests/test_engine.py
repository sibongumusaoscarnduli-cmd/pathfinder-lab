import json
import random
import subprocess
import sys
import unittest
from math import inf
from docs.engine import search, compare_json


def oracle(grid, start, goal):
    """Bellman-Ford-style relaxation; deliberately no heap or heuristic."""
    h,w=len(grid),len(grid[0]); dist={start:0}
    for _ in range(h*w):
        changed=False
        for r in range(h):
            for c in range(w):
                if grid[r][c] is None: continue
                for nr,nc in ((r-1,c),(r+1,c),(r,c-1),(r,c+1)):
                    if 0<=nr<h and 0<=nc<w and grid[nr][nc] is not None:
                        value=dist.get((r,c),inf)+grid[nr][nc]
                        if value<dist.get((nr,nc),inf):
                            dist[nr,nc]=value;changed=True
        if not changed: break
    return dist.get(goal)


class SearchTests(unittest.TestCase):
    def check_path(self,grid,start,goal,result):
        self.assertEqual(len(result['expanded']),len(set(map(tuple,result['expanded']))))
        if not result['found']:
            self.assertIsNone(result['cost']);self.assertEqual(result['path'],[]);return
        path=result['path'];self.assertEqual(path[0],list(start));self.assertEqual(path[-1],list(goal))
        self.assertEqual(result['cost'],sum(grid[r][c] for r,c in path[1:]))
        for a,b in zip(path,path[1:]): self.assertEqual(abs(a[0]-b[0])+abs(a[1]-b[1]),1)

    def test_weighted_detour(self):
        grid=[[1,1,1],[1,9,1],[1,1,1]]
        for algo in ('astar','dijkstra'):
            s=search(grid,[1,0],[1,2],algo);self.assertEqual(s['cost'],4);self.assertEqual(len(s['path']),5)

    def test_disconnected(self):
        for algo in ('astar','dijkstra'):
            s=search([[1,None,1]],[0,0],[0,2],algo);self.assertFalse(s['found']);self.assertIsNone(s['cost'])

    def test_same_endpoint(self):
        s=search([[9]],[0,0],[0,0]);self.assertEqual(s['cost'],0);self.assertEqual(s['path'],[[0,0]])

    def test_cost_of_entering_not_leaving(self):
        self.assertEqual(search([[9,2]],[0,0],[0,1])['cost'],2)

    def test_minimum_above_one(self):
        self.assertEqual(search([[3,4],[2,5]],[0,0],[1,1])['cost'],7)

    def test_single_column(self):
        self.assertEqual(search([[1],[2],[3]],[0,0],[2,0])['cost'],5)

    def test_invalid_grids(self):
        for grid in ([],[[]],[[1],[1,2]],[[True]],[[0]],[[-1]],[[1.5]],[[float('inf')]],[[10]],['x'],[[1]*61]):
            with self.subTest(grid=grid),self.assertRaises(ValueError): search(grid,[0,0],[0,0])

    def test_invalid_endpoints(self):
        for p in ([-1,0],[0,2],[True,0],[0],None,'00'):
            with self.subTest(p=p),self.assertRaises(ValueError): search([[1,1]],p,[0,0])
        with self.assertRaises(ValueError):search([[None,1]],[0,0],[0,1])

    def test_invalid_algorithm(self):
        with self.assertRaises(ValueError):search([[1]],[0,0],[0,0],'greedy')

    def test_json_errors(self):
        for payload in ('[]','{}','not json'):
            with self.assertRaises(ValueError):compare_json(payload)

    def test_random_maps_against_independent_oracle(self):
        rng=random.Random(2048)
        for index in range(150):
            grid=[[None if rng.random()<.25 else rng.randint(1,9) for _ in range(6)] for _ in range(5)]
            grid[0][0]=grid[-1][-1]=1
            optimum=oracle(grid,(0,0),(4,5))
            for algo in ('astar','dijkstra'):
                with self.subTest(index=index,algorithm=algo):
                    s=search(grid,[0,0],[4,5],algo);self.assertEqual(s['cost'],optimum);self.check_path(grid,(0,0),(4,5),s)

    def test_open_grid_heuristic(self):
        grid=[[1]*18 for _ in range(12)]
        a=search(grid,[0,0],[11,17]);d=search(grid,[0,0],[11,17],'dijkstra')
        self.assertEqual(a['cost'],28);self.assertEqual(a['cost'],d['cost']);self.assertLess(len(a['expanded']),len(d['expanded']))

    def test_cli(self):
        p=subprocess.run([sys.executable,'cli.py','example.json'],capture_output=True,text=True)
        self.assertEqual(p.returncode,0);self.assertEqual(json.loads(p.stdout)['astar']['cost'],6)
        p=subprocess.run([sys.executable,'cli.py','missing-map.json'],capture_output=True,text=True)
        self.assertEqual(p.returncode,2);self.assertIn('Invalid map',p.stderr)

if __name__=='__main__':unittest.main()
