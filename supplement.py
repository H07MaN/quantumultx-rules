"""Screen the user-selected GeQ1an domain supplement; preserve base rules.

Source: https://github.com/GeQ1an/Rules/blob/master/QuantumultX/Filter/AdBlock.list
Original rule attribution: GeQ1an/Rules and its contributors.
This module is GPL-3.0 like the builder. Source data retain their authorship.
"""
import hashlib
import re
import fnmatch
from collections import Counter

# Only applied to NEW supplement entries, never silently changes base rules.
PROTECTED = ('apple.com', 'icloud.com', 'mzstatic.com', 'tiktok.com',
             'tiktokv.com', 'tiktokcdn.com', 'shopee.com', 'shopee.tw',
             'shopee.sg', 'shopee.com.my', 'shopeemobile.com', 'alipay.com',
             'tenpay.com', 'paypal.com', 'github.com', 'githubusercontent.com')
BUSINESS_LABELS = {'login', 'passport', 'auth', 'oauth', 'payment', 'pay',
                   'checkout', 'captcha', 'verify', 'account', 'accounts'}

def within(host, suffix):
    return host == suffix or host.endswith('.' + suffix)

def conflicts(domain, typ, hosts):
    for h in hosts:
        if fnmatch.fnmatchcase(domain, h):
            return True
        if typ == 'host-suffix':
            if within(h, domain):
                return True
            # Conservative intersection with wildcard hostname patterns.
            if '*' in h or '?' in h:
                dl, hl = domain.split('.'), h.split('.')
                if len(dl) <= len(hl) and all(fnmatch.fnmatchcase(a, b) for a, b in zip(dl, hl[-len(dl):])):
                    return True
    return False

def merge_geq(path, rules, seen, mitm_hosts):
    raw = path.read_bytes()  # Missing source must fail, not erase the supplement.
    source = raw.decode('utf-8-sig')
    if len(raw) < 10000 or '<html' in source[:500].lower():
        raise ValueError('Invalid GeQ1an source; publication must stop')
    reasons, omitted, added = Counter(), [], []
    suffixes = {d for t, d in seen if t == 'host-suffix'}
    for line in source.splitlines():
        line = line.strip()
        if not line or line.startswith(('#', ';', '//')):
            continue
        p = [x.strip().lower() for x in line.split(',')]
        reason = None
        if len(p) != 3 or p[0] not in {'host', 'host-suffix'}:
            reason = 'non_domain_rule'
        elif p[2] != 'adblock':
            reason = 'unexpected_policy'
        elif len(p[1].split('.')) < 2 or not all(re.fullmatch(r'[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?', v) for v in p[1].split('.')):
            reason = 'invalid_domain'
        else:
            typ, d, _ = p
            if (typ, d) in seen or any('.'.join(d.split('.')[i:]) in suffixes for i in range(len(d.split('.')))):
                reason = 'already_covered'
            elif any(within(d, x) or within(x, d) for x in PROTECTED) or set(d.split('.')) & BUSINESS_LABELS:
                reason = 'protected_service_or_business_label'
            elif conflicts(d, typ, mitm_hosts):
                reason = 'mitm_overlap'
        if reason:
            reasons[reason] += 1
            if reason != 'already_covered':
                omitted.append({'rule': line, 'reason': reason})
            continue
        seen.add((typ, d))
        if typ == 'host-suffix':
            suffixes.add(d)
        rules.append(f'{typ}, {d}, reject')
        added.append(f'{typ}, {d}, reject')
    return {'source': 'https://raw.githubusercontent.com/GeQ1an/Rules/master/QuantumultX/Filter/AdBlock.list',
            'sha256': hashlib.sha256(raw).hexdigest(), 'added': len(added),
            'skipped_counts': dict(reasons), 'skipped_details': omitted,
            'validation': 'static screening; added domains are not individually device-tested'}
