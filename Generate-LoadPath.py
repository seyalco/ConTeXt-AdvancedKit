#!/usr/bin/env python3
"""Prepare tag-selected snapshots and PathList.ctx without compiling."""
from tools.tag_project import main

if __name__ == '__main__':
    raise SystemExit(main(prepare_only=True))
