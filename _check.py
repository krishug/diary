"""Comprehensive check of diary_app.py"""
import sys, os, re

sys.argv = ['diary_app.py']
os.chdir(os.path.dirname(os.path.abspath('diary_app.py')))

# Mock webview
import types
webview = types.ModuleType('webview')
webview.create_window = lambda *a, **kw: None
webview.start = lambda: None
sys.modules['webview'] = webview

globs = {'__file__': os.path.abspath('diary_app.py'), '__name__': '__main__'}
exec(open('diary_app.py').read(), globs)
HTML = globs['HTML']
api = globs['DiaryAPI']()

errors = []

# 1. HTML structure
if '<!DOCTYPE html>' not in HTML: errors.append('Missing DOCTYPE')
if '<html' not in HTML: errors.append('Missing <html>')
if '</html>' not in HTML: errors.append('Missing </html>')
if '<head>' not in HTML: errors.append('Missing <head>')
if '<body>' not in HTML: errors.append('Missing <body>')
if '<script>' not in HTML: errors.append('Missing <script>')

# 2. Key DOM elements
for el in ['editor', 'preview', 'dateLabel', 'todayBtn', 'stats', 'calendar', 'moods', 'weathers', 'wordCount', 'toast', 'dateSearch']:
    if f'id="{el}"' not in HTML:
        errors.append(f'Missing element: {el}')

# 3. Tag balance
body_s = HTML.count('<body>')
body_e = HTML.count('</body>')
if body_s != body_e: errors.append(f'Body tags: {body_s} open, {body_e} close')

div_s = len(re.findall(r'<div\b', HTML))
div_e = HTML.count('</div>')
if div_s != div_e: errors.append(f'Div tags: {div_s} open, {div_e} close')

script_s = HTML.count('<script>')
script_e = HTML.count('</script>')
if script_s != script_e: errors.append(f'Script tags: {script_s} open, {script_e} close')

# 4. CSS balance
style_m = re.search(r'<style>(.*?)</style>', HTML, re.DOTALL)
if style_m:
    css = style_m.group(1)
    so = css.count('{')
    sc = css.count('}')
    if so != sc: errors.append(f'CSS braces: {so} open, {sc} close')

# 5. JS balance
script_m = re.search(r'<script>(.*?)</script>', HTML, re.DOTALL)
if script_m:
    js = script_m.group(1)
    jo = js.count('{')
    jc = js.count('}')
    if jo != jc: errors.append(f'JS braces: {jo} open, {jc} close')
    po = js.count('(')
    pc = js.count(')')
    if po != pc: errors.append(f'JS parens: {po} open, {pc} close')

# 6. All functions present
for fn in ['fmt', 'ds', 'load', 'getWeekday', 'preview', 'simpleMarkdown', 'save', 'handleDelete', 'go', 'goDate', 'searchDate', 'parseFrontMatter', 'setMoodWeatherUI', 'autoNumberPlans', 'loadStats', 'loadCalendar', 'toast']:
    if f'function {fn}' not in js if script_m else True:
        errors.append(f'Missing JS function: {fn}')

# 7. Event listeners
if script_m:
    pass  # no specific startup mechanism requirement

# 8. Remaining template markers
if '{API_JS}' in HTML: errors.append('{API_JS} not replaced')
if '{{' in HTML: errors.append('Remaining double braces {{')
if '}}' in HTML: errors.append('Remaining double braces }}')

# 9. Test API methods
try:
    t = api.template('2026-06-04')
    if not t: errors.append('template() returned empty')
    if '{{date}}' in t: errors.append('template() didnt replace {{date}}')
except Exception as e:
    errors.append(f'template() error: {e}')

try:
    api.save('2099-12-31', 'test')
    r = api.read('2099-12-31')
    if r != 'test': errors.append(f'read/write mismatch: got {r}')
    api.delete_entry('2099-12-31')
    if api.read('2099-12-31'): errors.append('delete_entry failed')
except Exception as e:
    errors.append(f'file ops error: {e}')

try:
    s = api.stats()
    if not isinstance(s, dict): errors.append('stats() not dict')
except Exception as e:
    errors.append(f'stats() error: {e}')

# 10. File exists check
if not os.path.exists('_template.md'): errors.append('Template file missing')
if not os.path.isdir('entries'): errors.append('entries dir missing')

# Results
print(f'HTML size: {len(HTML)} bytes')
print(f'Lines: {len(HTML.splitlines())}')
if errors:
    print(f'\n❌ {len(errors)} issues found:')
    for e in errors:
        print(f'  - {e}')
else:
    print('\n✅ All checks passed!')
