"""Compatibility launcher for the Fukuoka historical design sample."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent / 'scripts'))
from context import load_context
import layout
root, temporary, output, plan, trip = load_context('fukuoka-2026')
layout.configure(root, output, temporary, trip, plan['fonts'])
sys.path.insert(0, str(root))
from sample import make_sample
make_sample()
