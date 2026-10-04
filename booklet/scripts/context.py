"""Resolve one trip's reviewed plan and public snapshot without website data."""
import argparse
import json
import re
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[2]


def load_context(slug):
    if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', slug):
        raise ValueError('Invalid trip slug')
    root = PROJECT / 'booklet' / 'trips' / slug
    temporary = PROJECT / 'booklet' / 'tmp' / slug
    output = PROJECT / 'output' / 'pdf' / slug
    plan = json.loads((root / 'book-plan.json').read_text(encoding='utf8'))
    trip = json.loads((temporary / 'trip.json').read_text(encoding='utf8'))
    if trip['slug'] != slug or plan['slug'] != slug:
        raise ValueError('Trip/plan slug mismatch')
    if plan['reviewedSourceHash'] != trip['sourceHash']:
        raise ValueError('Source changed: review curated text before updating reviewedSourceHash.')
    if [trip['start'], trip['end']] != plan['dates']:
        raise ValueError('Reviewed date range changed')
    for filename in plan['outputs'].values():
        if Path(filename).name != filename or not filename.endswith('.pdf'):
            raise ValueError('Output names must be PDF basenames')
    return root, temporary, output, plan, trip


def slug_argument():
    parser = argparse.ArgumentParser()
    parser.add_argument('--slug', required=True, help='Trip slug from the note')
    return parser.parse_args().slug
