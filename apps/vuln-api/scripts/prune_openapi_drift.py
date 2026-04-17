#!/usr/bin/env python3
"""Prune stale operations from docs/openapi.yaml.

Walks the live Flask app (the union of routes during the Flask->Starlette
migration, since register_flask_compat_routes mirrors ported Starlette
routers back into Flask) and removes any (path, method) pair from
docs/openapi.yaml that does not correspond to a live route. Path blocks
left without any HTTP method operations are removed entirely.

The prune operates on the raw YAML text (not a parse/re-emit round-trip)
so existing formatting, key ordering, and inline flow styles like
`tags: [Admin]` are preserved.

Exit codes:
  0 - prune ran (may be a no-op)
  2 - failed to load live routes or spec
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
REPO_DIR = SCRIPTS_DIR.parent
sys.path.insert(0, str(SCRIPTS_DIR))

from check_openapi_drift import (  # type: ignore[import]
    DOCUMENTED_METHODS,
    load_live_routes,
    _normalize_oas,
)

_PATH_LINE = re.compile(r'^(\s{2})(/\S*):\s*$')
# Any 2-indent map key — used to detect malformed non-'/' entries that
# earlier manual edits accidentally dropped at the paths level.
_PATHS_CHILD_KEY = re.compile(r'^(\s{2})([^\s:][^:]*):\s*$')
_METHOD_LINE = re.compile(r'^(\s{4})([a-z]+):\s*$')


def _leading_spaces(line: str) -> int:
    count = 0
    for ch in line:
        if ch == ' ':
            count += 1
        else:
            break
    return count


def collect_spec_keys(text: str) -> set[tuple[str, str]]:
    """Scan the spec text for every (normalized_path, METHOD) pair.

    Using the same text we will later mutate guarantees the key set matches
    what the surgical prune walks.
    """
    results: set[tuple[str, str]] = set()
    in_paths = False
    current: str | None = None
    for line in text.splitlines():
        if not in_paths:
            if line.rstrip() == 'paths:':
                in_paths = True
            continue
        if line.strip() and _leading_spaces(line) == 0:
            in_paths = False
            current = None
            continue
        path_match = _PATH_LINE.match(line)
        if path_match:
            current = _normalize_oas(path_match.group(2))
            continue
        method_match = _METHOD_LINE.match(line)
        if method_match and current is not None:
            method = method_match.group(2).upper()
            if method in DOCUMENTED_METHODS:
                results.add((current, method))
    return results


def _process_path_block(
    body: list[str],
    normalized_path: str,
    stale: set[tuple[str, str]],
) -> tuple[list[str], int, bool, bool]:
    """For one path block body, drop stale methods and report what's left.

    Returns (kept_lines, removed_ops, has_remaining_methods, has_other_content).
    """
    kept: list[str] = []
    removed = 0
    has_methods = False
    has_other = False

    i = 0
    n = len(body)
    while i < n:
        line = body[i]
        method_match = _METHOD_LINE.match(line)
        if method_match:
            name = method_match.group(2).upper()
            start = i
            i += 1
            while i < n and (body[i].strip() == '' or _leading_spaces(body[i]) > 4):
                i += 1
            if name in DOCUMENTED_METHODS:
                if (normalized_path, name) in stale:
                    removed += 1
                    continue
                has_methods = True
            else:
                has_other = True
            kept.extend(body[start:i])
        else:
            if line.strip():
                has_other = True
            kept.append(line)
            i += 1

    return kept, removed, has_methods, has_other


def prune(text: str, stale: set[tuple[str, str]]) -> tuple[str, int, int, int]:
    """Return (new_text, removed_ops, removed_empty_paths, removed_bogus_keys)."""
    lines = text.splitlines(keepends=True)
    out: list[str] = []
    removed_ops = 0
    removed_paths = 0
    removed_bogus = 0
    in_paths = False

    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]

        if not in_paths:
            out.append(line)
            if line.rstrip() == 'paths:':
                in_paths = True
            i += 1
            continue

        path_match = _PATH_LINE.match(line)
        if path_match:
            declared = path_match.group(2)
            normalized = _normalize_oas(declared)

            start = i
            i += 1
            while i < n and (lines[i].strip() == '' or _leading_spaces(lines[i]) >= 4):
                i += 1
            body = lines[start + 1 : i]

            kept, dropped, has_methods, has_other = _process_path_block(
                body, normalized, stale
            )
            removed_ops += dropped

            if not has_methods and not has_other:
                removed_paths += 1
                continue

            out.append(line)
            out.extend(kept)
            continue

        bogus_match = _PATHS_CHILD_KEY.match(line)
        if bogus_match:
            # Non-'/' key at the paths level — malformed entry. Drop the
            # key and its entire indented block.
            i += 1
            while i < n and (lines[i].strip() == '' or _leading_spaces(lines[i]) >= 4):
                i += 1
            removed_bogus += 1
            continue

        if line.strip() and _leading_spaces(line) == 0:
            in_paths = False

        out.append(line)
        i += 1

    return ''.join(out), removed_ops, removed_paths, removed_bogus


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--spec', default=str(REPO_DIR / 'docs' / 'openapi.yaml'))
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()

    spec_file = Path(args.spec)
    if not spec_file.is_file():
        print(f'openapi spec not found: {spec_file}', file=sys.stderr)
        return 2

    try:
        live = load_live_routes()
    except Exception as exc:
        print(f'failed to load live routes: {exc}', file=sys.stderr)
        return 2

    text = spec_file.read_text()
    spec_keys = collect_spec_keys(text)
    stale = spec_keys - set(live)

    new_text, removed_ops, removed_paths, removed_bogus = prune(text, stale)

    if not removed_ops and not removed_paths and not removed_bogus:
        print('Nothing to prune.')
        return 0

    action = 'Would remove' if args.dry_run else 'Removed'
    print(
        f'{action} {removed_ops} stale operation(s), '
        f'{removed_paths} now-empty path block(s), and '
        f'{removed_bogus} malformed non-path key(s).'
    )

    if args.dry_run:
        return 0

    spec_file.write_text(new_text)
    return 0


if __name__ == '__main__':
    sys.exit(main())
