import re
import os

root = os.path.join(os.getcwd(), '..') if os.getcwd().endswith('Backend') else os.path.join(os.getcwd(), 'Backend')
models_dir = os.path.join(root, 'auth_app', 'models')  # we'll scan all apps under Backend
# Collect all model files under Backend/*/models/*.py
files = []
for app in os.listdir(root):
    app_path = os.path.join(root, app)
    models_path = os.path.join(app_path, 'models')
    if os.path.isdir(models_path):
        for f in os.listdir(models_path):
            if f.endswith('.py'):
                files.append(os.path.join(models_path, f))

report = []
field_re = re.compile(r'^\s*(\w+)\s*=\s*models\.(\w+Field)\b')
class_re = re.compile(r'^class\s+(\w+)\s*\(models.Model')
json_re = re.compile(r'models\.JSONField|JSONField')
plural_suspects = set(['skills','tags','addresses','phones','emails','roles','members','skills_relevance','work_histories','workhistory','work_histories'])

for filepath in files:
    with open(filepath, 'r', encoding='utf-8') as fh:
        lines = fh.readlines()
    current_class = None
    for i, line in enumerate(lines):
        mclass = class_re.search(line)
        if mclass:
            current_class = mclass.group(1)
        m = field_re.search(line)
        if m and current_class:
            field_name = m.group(1)
            field_type = m.group(2)
            # look ahead a few chars to capture full field line
            extra = '\n'.join(lines[i:i+3])
            is_json = bool(json_re.search(extra))
            if field_name.endswith('s') and field_type in ('TextField','CharField','JSONField') or field_name in plural_suspects or is_json:
                report.append((os.path.relpath(filepath, root), current_class, field_name, field_type, i+1, is_json))

# Also search for common patterns in models (split(','), json.dumps)
pattern_report = []
patterns = [r"split\('\,'\)", r"split\(\'\,\'\)", r"json\.dumps", r"json\.loads", r",\s*'.*' in "]
for filepath in files:
    with open(filepath, 'r', encoding='utf-8') as fh:
        txt = fh.read()
    for p in patterns:
        if re.search(p, txt):
            pattern_report.append((os.path.relpath(filepath, root), p))

print('Normalization scan report')
print('=========================')
if not report:
    print('No obvious plural/text/json field issues found.')
else:
    print('Potential denormalized fields:')
    for f in report:
        print(f'- File: {f[0]} | Model: {f[1]} | Field: {f[2]} | Type: {f[3]} | Line: {f[4]} | JSON-like: {f[5]}')

if pattern_report:
    print('\nPatterns indicating serialized arrays/strings found:')
    for p in pattern_report:
        print(f'- File: {p[0]} | Pattern: {p[1]}')

print('\nScan complete.')
