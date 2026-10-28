#!/usr/bin/env python3
"""Compile tag-selected outputs; --watch rebuilds affected targets on changes."""
from tools.tag_project import main

if __name__ == '__main__':
    raise SystemExit(main())
