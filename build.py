"""Build a native Quantumult X subset from local fmz200 source snapshots.
Usage: python3 build.py SOURCE_DIRECTORY
Source files: upstream-rewrite.snippet, upstream-filter.list, upstream-LICENSE.
GPL-3.0; retains upstream authorship. No network requests or remote scripts.
"""
from pathlib import Path
import sys, re, json, hashlib, fnmatch

src = Path(sys.argv[1])
out = Path(__file__).resolve().parent
rewrite = (src / 'upstream-rewrite.snippet').read_text()
filters = (src / 'upstream-filter.list').read_text()
allowed = {'reject', 'reject-200', 'reject-img', 'reject-dict', 'reject-array'}
global_hosts = set()
for line in rewrite.splitlines():
    if line.startswith('hostname ='):
        global_hosts.update(h.strip() for h in line.split('=', 1)[1].split(','))

blocks, block = [], []
for line in rewrite.splitlines():
    if line.startswith('# > ') and not line.startswith('# >>>'):
        blocks.append(block)
        block = []
    block.append(line)
blocks.append(block)
result, hosts, seen, skipped, sections = [], set(), set(), [], []
body_paths = (r'mp\.weixin\.qq\.com\/mp\/getappmsgad',
              r'api\.m\.jd\.com\/client\.action\?functionId=lite_advertising')
for block in blocks:
    chosen = []
    declared = set()
    title = next((x for x in block if x.startswith('# > ')), '# > General')
    for line in block:
        if line.startswith('# hostname ='):
            declared.update(h.strip() for h in line.split('=', 1)[1].split(','))
        if not line.startswith('^') or ' url ' not in line:
            continue
        pattern, action = re.split(r'\s+url\s+', line, maxsplit=1)
        keep = action.lower() in allowed
        keep_body = action.startswith('response-body ') and any(p in pattern for p in body_paths)
        if not (keep or keep_body):
            continue
        # Repair an invalid escape in upstream's KFC advertisement path.
        pattern = pattern.replace(r'res\.kfc\.com.\cn', r'res\.kfc\.com\.cn')
        try:
            re.compile(pattern)
        except re.error:
            skipped.append({'reason': 'invalid_regex', 'rule': line})
            continue
        canonical = pattern + ' url ' + (action.lower() if keep else action)
        if pattern in seen:
            continue
        seen.add(pattern)
        chosen.append(canonical)
    if chosen:
        result.extend([title, *chosen, ''])
        sections.append(title[4:])
        # Never enable hostnames that upstream deliberately leaves disabled.
        hosts.update(declared & global_hosts)

hosts = {h for h in hosts if h and h not in {'*', '*.*'} and not h.startswith('-')}
header = ['# Quantumult X 国内广告拦截：HTTPS 重写',
          '# Derived from fmz200/wool_scripts; author: 奶思 and upstream contributors.',
          '# Source: https://github.com/fmz200/wool_scripts',
          '# License: GPL-3.0 (see LICENSE). Modified: 2026-09-07.',
          '# Native reject rules + two selected response replacements; no external JavaScript.',
          '# Enable Rewrite and MitM, generate/install/trust your own CA on your device.',
          '# Snapshot. Not all ads or App versions are supported. No claim of device testing.',
          '# Modifications: native subset, deduplication, KFC regex repair, scoped hostname list.',
          '# Source SHA256: ' + hashlib.sha256(rewrite.encode()).hexdigest(), '']
(out / 'china-adblock.snippet').write_text('\n'.join(header + result + ['hostname = ' + ', '.join(sorted(hosts))]) + '\n')

fresult, fseen, overlaps = [], set(), []
for line in filters.splitlines():
    p = [v.strip() for v in line.split(',')]
    if len(p) != 3 or p[0] not in {'host', 'host-suffix'} or p[2].lower() not in allowed:
        continue
    typ, domain, action = p
    if not re.fullmatch(r'[a-z0-9_-]+(?:\.[a-z0-9_-]+)+', domain):
        continue
    # Preserve shared service hosts used by the HTTPS resource.
    if any(fnmatch.fnmatchcase(domain, h) or (typ == 'host-suffix' and (h == domain or h.endswith('.' + domain))) for h in hosts):
        overlaps.append(domain)
        continue
    rule = f'{typ}, {domain}, {action.lower()}'
    if (typ, domain) not in fseen:
        fseen.add((typ, domain))
        fresult.append(rule)
# User-tested together: banner disappeared on 2026-09-08.
# Keep exact hosts only; individual necessity has not been isolated.
for domain in ('83876gc.ezze0ct.com', '0812gc.18tmnxt.com'):
    if ('host', domain) not in fseen:
        fseen.add(('host', domain))
        fresult.append(f'host, {domain}, reject')
(out / 'china-adblock.list').write_text('\n'.join([
    '# Quantumult X 国内广告域名拦截',
    '# Derived from fmz200/wool_scripts; author: 奶思 and upstream contributors.',
    '# Source: https://github.com/fmz200/wool_scripts; GPL-3.0 (see LICENSE).',
    '# Modified: 2026-09-07. Domain-only subset; no IP or keyword rules.',
    '# Import as filter resource; leave force-policy unset.',
    '# Source SHA256: ' + hashlib.sha256(filters.encode()).hexdigest(), *fresult]) + '\n')
(out / 'LICENSE').write_text((src / 'upstream-LICENSE').read_text())
stats = {'rewrite_rules': len(seen), 'mitm_hostnames': len(hosts),
         'source_sections_with_selected_rules': len(sections), 'filter_rules': len(fseen),
         'skipped_invalid_regex': skipped, 'removed_filter_overlap': sorted(set(overlaps)),
         'source_sections': sections,
         'validation': 'static syntax and deduplication only; no on-device test',
         'update_mode': 'manual snapshot, no automatic upstream sync'}
(out / 'build-report.json').write_text(json.dumps(stats, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({k:v for k,v in stats.items() if k not in {'source_sections', 'removed_filter_overlap'}}, ensure_ascii=False))
