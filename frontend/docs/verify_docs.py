#!/usr/bin/env python3
"""Validate frontend document structure. This does not verify semantic truth."""

from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit

FRONTEND = Path(__file__).resolve().parents[1]
REQUIRED = {
    'AGENTS.md': ('Scope', 'Startup order', 'Completion procedure'),
    'README.md': ('Current status', 'Commands', 'Environment'),
    'docs/README.md': ('Canonical owners', 'Startup routing'),
    'docs/FRONTEND_ARCHITECTURE.md': ('API transport and contracts', 'Authentication and privacy'),
    'docs/WORKFLOW.md': ('Route map', 'Guest creation and generated result'),
    'docs/DESIGN_SYSTEM.md': ('Tokens and typography', 'Motion and accessibility'),
    'docs/TESTING_AND_QUALITY.md': ('Test selection', 'Production and performance gate'),
    'docs/BUILD_CHECKLIST.md': ('Status contract', 'Implementation queue', 'Next task'),
    'docs/SOURCE_LEDGER.md': ('Decision rules', 'Adopted component source'),
    'docs/HANDOFF.md': ('Current objective', 'Verified checks', 'Blockers and cross-boundary dependencies', 'Exact next task', 'Scope protections'),
}
STATUSES = {'TODO', 'IN_PROGRESS', 'PARTIAL', 'BLOCKED_BACKEND', 'BLOCKED_CONTRACT', 'BLOCKED_DECISION', 'BLOCKED_EXTERNAL', 'DEFERRED', 'DONE_VERIFIED'}
ERRORS: list[str] = []


def prose(text: str) -> str:
    return re.sub(r'^```[^\n]*\n.*?^```\s*$', '', text, flags=re.M | re.S)


def anchors(text: str) -> set[str]:
    counts: dict[str, int] = {}
    found = set(re.findall(r'<(?:a|[a-z]+)\b[^>]*\bid=["\']([^"\']+)', text))
    for heading in re.findall(r'^#{1,6}\s+(.+?)\s*#*$', prose(text), flags=re.M):
        heading = re.sub(r'\[([^]]+)\]\([^)]*\)', r'\1', heading)
        slug = re.sub(r'[^\w\- ]', '', heading.lower()).replace(' ', '-')
        count = counts.get(slug, 0)
        found.add(slug if not count else f'{slug}-{count}')
        counts[slug] = count + 1
    return found


owners: dict[str, str] = {}
texts: dict[str, str] = {}
for name, sections in REQUIRED.items():
    path = FRONTEND / name
    if not path.is_file() or not path.read_text().strip():
        ERRORS.append(f'{name}: required non-empty document missing')
        continue
    text = path.read_text()
    texts[name] = text
    labels = re.findall(r'^\*\*Owner:\*\* (.+)$', text, flags=re.M)
    if len(labels) != 1:
        ERRORS.append(f'{name}: exactly one owner header required')
    else:
        label = labels[0].strip().lower()
        if label in owners:
            ERRORS.append(f'{name}: duplicate owner claim with {owners[label]}')
        owners[label] = name
    for section in sections:
        if f'## {section}\n' not in text:
            ERRORS.append(f'{name}: missing section {section}')
    if name not in {'docs/BUILD_CHECKLIST.md', 'docs/HANDOFF.md'}:
        for line in prose(text).splitlines():
            if re.search(r'\b(?:TODO|TBD|FIXME|INSERT_HERE)\b|<placeholder>', line):
                if not re.search(r'\b(?:PLANNED|BLOCKED|DEFERRED|REFERENCE_ONLY|EVALUATED_DEFERRED)\b', line):
                    ERRORS.append(f'{name}: unclassified placeholder: {line.strip()}')

# Check maintained Markdown, including notices; skip installed skills and artifacts.
documents = [FRONTEND / name for name in texts]
documents.append(FRONTEND / 'THIRD_PARTY_NOTICES.md')
for path in documents:
    if not path.is_file():
        ERRORS.append(f'{path.relative_to(FRONTEND)}: notice file missing')
        continue
    for target in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)', prose(path.read_text())):
        target = target.strip().strip('<>')
        parts = urlsplit(target)
        if parts.scheme or parts.netloc:
            continue
        local = (path.parent / unquote(parts.path)).resolve() if parts.path else path
        if not local.exists():
            ERRORS.append(f'{path.relative_to(FRONTEND)}: broken local link {target}')
        elif parts.fragment and local.suffix == '.md':
            if unquote(parts.fragment) not in anchors(local.read_text()):
                ERRORS.append(f'{path.relative_to(FRONTEND)}: missing local anchor {target}')

tasks: dict[str, list[str]] = {}
for line in texts.get('docs/BUILD_CHECKLIST.md', '').splitlines():
    if not re.match(r'^\|\s*FE-\d+', line):
        continue
    row = [part.strip().strip('`') for part in line.strip().strip('|').split('|')]
    if len(row) != 8 or not all(row):
        ERRORS.append(f'BUILD_CHECKLIST: eight populated cells required: {line}')
        continue
    task_id = row[0]
    if not re.fullmatch(r'FE-\d{3}', task_id) or task_id in tasks:
        ERRORS.append(f'BUILD_CHECKLIST: invalid or duplicate ID {task_id}')
    tasks[task_id] = row
    if row[6] not in STATUSES:
        ERRORS.append(f'{task_id}: invalid status {row[6]}')
    if row[6].startswith('BLOCKED_') and row[7] == 'None':
        ERRORS.append(f'{task_id}: blocked task needs a blocker')
if not tasks:
    ERRORS.append('BUILD_CHECKLIST: no structured tasks found')
for task_id, row in tasks.items():
    for dependency in re.findall(r'FE-\d{3}', row[2]):
        if dependency not in tasks or dependency == task_id:
            ERRORS.append(f'{task_id}: invalid dependency {dependency}')

if ERRORS:
    print('\n'.join(ERRORS), file=sys.stderr)
    sys.exit(1)
print(f'Document structure passed: {len(texts)} canonical owners, {len(tasks)} unique tasks, local links and anchors.')
