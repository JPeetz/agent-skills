import os, subprocess, json, glob

root = '/tmp/agent-skills-audit'
skills = []
for dp, _, fs in os.walk(root):
    if '.git' in dp: continue
    if 'SKILL.md' in fs:
        rel = os.path.relpath(dp, root)
        skills.append((rel, dp))

results = []
for rel, dp in skills:
    r = subprocess.run(['/usr/local/bin/python3','scripts/validate_skill.py', dp],
                       capture_output=True, text=True, cwd=root)
    try:
        j = json.loads(r.stdout)
    except:
        j = {'valid': False, 'issues': [{'type':'run_err','message':r.stderr[:100]}]}
    # completeness beyond the validator
    has_evals = os.path.isdir(os.path.join(dp,'evals'))
    has_corrections = os.path.exists(os.path.join(dp,'references','corrections.md')) or \
                      any('correction' in f for f in os.listdir(os.path.join(dp,'references')) if os.path.isdir(os.path.join(dp,'references'))) if os.path.isdir(os.path.join(dp,'references')) else False
    has_changelog = os.path.exists(os.path.join(dp,'CHANGELOG.md'))
    has_scripts = os.path.isdir(os.path.join(dp,'scripts'))
    # desc style
    import re
    desc = ''
    m = re.match(r'^---\s*\n(.*?)\n---', open(os.path.join(dp,'SKILL.md'),encoding='utf-8',errors='replace').read(), re.S)
    if m:
        try:
            import yaml; desc = (yaml.safe_load(m.group(1)) or {}).get('description','')
        except: pass
    desc_style = desc.startswith('Use this skill when') or desc.startswith('Use when')
    results.append({
        'rel': rel, 'valid': j.get('valid', False),
        'issues': [i.get('type') for i in j.get('issues',[])],
        'warnings': [w.get('type') for w in j.get('warnings',[])],
        'evals': has_evals, 'corrections': has_corrections, 'changelog': has_changelog,
        'scripts': has_scripts, 'desc_chars': len(desc), 'desc_style': desc_style,
    })

# summary
from collections import Counter
issues = Counter()
for r in results:
    for i in r['issues']: issues[i]+=1
print("=== VALIDATOR ISSUES ===")
for i,n in issues.most_common(): print(f"  {i}: {n}")

nvalid = sum(1 for r in results if r['valid'])
print(f"\nValid per repo validator: {nvalid}/{len(results)}")

print("\n=== QUALITY BAR (evals/corrections/changelog) — these are what the README promises ===")
for field in ['evals','corrections','changelog','scripts']:
    n = sum(1 for r in results if r[field])
    print(f"  has_{field}: {n}/{len(results)}")

print("\n=== desc style ('Use this skill when'/'Use when') ===")
print(f"  compliant: {sum(1 for r in results if r['desc_style'])}/{len(results)}")

print("\n=== SKILLS MISSING evals (README promises eval suites) ===")
for r in results:
    if not r['evals']:
        print(f"  {r['rel']}")
