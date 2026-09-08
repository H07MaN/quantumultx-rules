"""GeQ1an/Rules native rewrite supplement; GPL-3.0 builder code.
Source rule attribution: GeQ1an, DivineEngine and upstream contributors.
"""
import re
import hashlib
from urllib.parse import urlsplit
from re import _parser as parser

def normalize(pattern):
    return pattern.replace(r'\/', '/')

def expand(tokens):
    values = ['']
    for op, arg in tokens:
        if op == parser.LITERAL:
            parts = [chr(arg)]
        elif op == parser.SUBPATTERN:
            parts = expand(arg[-1])
        elif op == parser.BRANCH:
            parts = [v for branch in arg[1] for v in expand(branch)]
        elif op == parser.IN and all(x == parser.LITERAL for x, _ in arg):
            parts = [chr(v) for _, v in arg]
        elif op == parser.MAX_REPEAT and arg[0] == 0 and arg[1] == 1:
            parts = [''] + expand(arg[2])
        else:
            raise ValueError('Non-finite hostname expression')
        values = [a+b for a in values for b in parts]
        if len(values) > 64:
            raise ValueError('Too many hostname variants')
    return values

def finite_hosts(pattern):
    host = pattern.split('://', 1)[1].split('/', 1)[0]
    # Source occasionally uses unescaped dots, including (www.)?.
    host = re.sub(r'(?<!\\)\.', r'\\.', host)
    return expand(parser.parse(host, 0))

def merge_rewrites(path, result, hosts, seen):
    raw = path.read_bytes()
    source = raw.decode('utf-8-sig')
    if len(raw) < 10000 or '<html' in source[:500].lower():
        raise ValueError('Invalid rewrite supplement')
    existing = {normalize(x.split(' url ', 1)[0]) for x in result if ' url ' in x}
    source_hosts = set()
    for line in source.splitlines():
        if line.startswith('hostname ='):
            source_hosts.update(h.strip() for h in line.split('=', 1)[1].split(','))
    source_hosts -= {'app.biliintl.com', 'passport.biliintl.com'}
    report = {'source': 'https://raw.githubusercontent.com/GeQ1an/Rules/master/QuantumultX/Rewrite/Rewrite.list',
              'sha256': hashlib.sha256(raw).hexdigest(), 'added_reject': 0,
              'added_redirect': 0, 'skipped': [], 'loop_guards': [], 'redirect_tests': []}
    additions = []
    redirects_seen = set()
    for line in source.splitlines():
        if not line or line.startswith(('#', ';')) or ' url ' not in line:
            continue
        pattern, action = line.split(' url ', 1)
        pattern = normalize(pattern)
        if 'biliintl' in pattern:
            report['skipped'].append({'rule': line, 'reason': 'separate_optional_region_resource'})
            continue
        if action.startswith('response-body '):
            report['skipped'].append({'rule': line, 'reason': 'existing_wechat_response_rule_preferred'})
            continue
        if pattern in existing:
            report['skipped'].append({'rule': line, 'reason': 'existing_pattern_preferred'})
            continue
        if action.startswith('302 '):
            dest = action[4:]
            if '$' in dest or not dest.startswith(('http://', 'https://')):
                raise ValueError('Unreviewed dynamic redirect')
            host_expr = pattern.split('://', 1)[1].split('/', 1)[0]
            fixed_expr = re.sub(r'(?<!\\)\.', r'\\.', host_expr)
            pattern = pattern.replace(host_expr, fixed_expr, 1)
            if pattern in redirects_seen:
                report['skipped'].append({'rule': line, 'reason': 'duplicate_redirect_first_target_retained'})
                continue
            redirects_seen.add(pattern)
            hostnames = finite_hosts(pattern)
            hosts.update(hostnames)
            target = urlsplit(dest)
            # Never redirect an already-canonical destination origin.
            if re.search(pattern, dest):
                guard = re.escape(target.scheme + '://' + target.netloc)
                pattern = '^(?!' + guard + r'(?:[/:?#]|$))' + pattern.lstrip('^')
                report['loop_guards'].append(dest)
            assert not re.search(pattern, dest), 'Redirect loop: '+dest
            report['redirect_tests'].append({'pattern': pattern, 'target': dest})
            report['added_redirect'] += 1
        elif action in {'reject', 'reject-200', 'reject-dict', 'reject-img', 'reject-array'}:
            # Apple lookup is an app-update check, not an advertisement endpoint.
            if 'itunes\\.apple\\.com/lookup' in pattern:
                report['skipped'].append({'rule': line, 'reason': 'app_update_lookup_not_advertising'})
                continue
            report['added_reject'] += 1
        else:
            raise ValueError('Unsupported action: '+action)
        re.compile(pattern)
        existing.add(pattern)
        seen.add(pattern)
        additions.append(pattern+' url '+action)
    # Preserve upstream enabled host scope for ad rules; no wildcard-all MITM.
    hosts.update(source_hosts)
    result.extend(['', '# GeQ1an/Rules supplement: native advertising + redirect rules.', *additions])
    report['added_total'] = len(additions)
    return report

def optional_region():
    prefix = r'https?://(?:app\.biliintl\.com/(?:x/)?(?:intl|dm|reply|history|v\d/(?:fav|msgfeed))[^?#]*|passport\.biliintl\.com/x/intl/passport-login/[^?#]*)'
    rules = []
    for key, value in [('s_locale', 'zh-Hans_PH'), ('sim_code', '51503')]:
        pattern = '^(' + prefix + r'\?(?:[^#]*&)?' + key + ')=(' + '(?!' + value + r'(?:&|$))[^&#]*)([^#]*)$'
        rules.append(pattern+' url 302 $1='+value+'$3')
    return '\n'.join(['# OPTIONAL: Bili international PH parameters; not enabled by main subscriptions.',
        '# Derived intent from GeQ1an/Rules. Rebuilt captures; preserve query parameters and avoid self-loops.',
        '# May affect request methods/login; service compatibility not device-tested. Opt in only.',
        *rules, 'hostname = app.biliintl.com, passport.biliintl.com', ''])
