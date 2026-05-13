#!/usr/bin/env python3
"""
generate_webapp.py — Genereer statische webapp (Belastingdienst-stijl) uit project-data.

Gebruik:
    tools/.venv/bin/python tools/generate_webapp.py [--project-dir .] [--out webapp]

Delegates naar sitegen.cli.main().
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from sitegen.cli import main

if __name__ == "__main__":
    main()
