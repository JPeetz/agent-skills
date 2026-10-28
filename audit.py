import os, re, yaml, json
from collections import Counter

root = '/tmp/agent-skills-audit'
skills = []
for dp, _, fs in os.walk(root):
    if '.git' in dp: continue
    if 'SKILL.md' in fs:
        rel = os.path.relpath(dp, root)
        skills.append((rel, os.path.join(dp, 'SKILL.md')))

marketing = ['powerful','comprehensive','seamless','advanced','cutting-edge','state-of-the-art',
             'best-in-class','robust','lightning','unparalleled','revolutionary','cutting-edge']

def parse(path):
    txt = open(path, encoding='utf-8', errors='replace').read()
    issues = []
    m = re.match(r'^---\s*\n(.*?)\n---\s*\n', txt, re.S)
    data = {}
    if not m:
        return issues, data, txt, len(txt)
    try:
        data = yaml.safe_load(m.group(1)) or {}
    except Exception as e:
        issues.append(f"YAML_ERR:{str(e)[:40]}")
    body = txt[m.end():]
    return issues, data, body, len(body)

def audit(rel, path):
    issues, data, body, blen = parse(path)
    desc = data.get('description', '') or ''
    if not desc: issues.append("NO_DESC")
    elif len(desc) > 60: issues.append(f"DESC>{60}({len(desc)})")
    if desc and not desc.rstrip().endswith('.'): issues.append("DESC_NO_PERIOD")
    dl = desc.lower()
    for w in marketing:
        if w in dl: issues.append(f"MARKETING:{w}")
    for f in ['version','author','license','platforms']:
        if f not in data: issues.append(f"NO_{f.upper()}")
    if re.search(r'(/Users/|/home/|/root/|C:\\|/Users/[a-z])', body): issues.append("MACHINE_LOCAL_PATH")
    lb = body.lower()
    for sec in ['when to use','pitfalls','verification']:
        if sec not in lb: issues.append(f"NO_SECTION:{sec.replace(' ','-')}")
    if blen < 800: issues.append(f"THIN_BODY({blen})")
    return issues, data, len(desc)

report = []
for rel, path in skills:
    issues, data, dlen = audit(rel, path)
    report.append({'rel': rel, 'name': data.get('name',''), 'desc_len': dlen, 'issues': issues})

all_issues = Counter()
for r in report:
    for i in r['issues']: all_issues[i] += 1

print("=== ISSUE FREQUENCY (all %d skills) ===" % len(report))
for issue, n in all_issues.most_common():
    print(f"  {issue}: {n}")

clean = [r for r in report if not r['issues']]
print("\n=== CLEAN (%d) ===" % len(clean))
for r in clean: print(f"  {r['rel']}")

print("\n=== SKILLS WITH ISSUES (%d) ===" % (len(report)-len(clean)))
for r in report:
    if r['issues']:
        print(f"\n  {r['rel']}")
        for i in r['issues']: print(f"    - {i}")

json.dump(report, open('/tmp/agent-skills-audit/report.json','w'), indent=2)
print("\nreport saved to /tmp/agent-skills-audit/report.json")
