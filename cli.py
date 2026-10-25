"""Run: python3 cli.py map.json"""
import argparse
from pathlib import Path
from docs.engine import compare_json

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Compare optimal weighted-grid routes.')
    parser.add_argument('map', type=Path, help='JSON with grid, start and goal')
    args = parser.parse_args()
    try:
        if args.map.stat().st_size > 100_000:
            raise ValueError('Input must be at most 100 KB.')
        print(compare_json(args.map.read_text(encoding='utf-8')))
    except (OSError, ValueError, TypeError) as exc:
        parser.exit(2, f'Invalid map: {exc}\n')
