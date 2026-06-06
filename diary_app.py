#!/usr/bin/env python3
"""Diary App - 原生 macOS 窗口 (WebKit)"""
import webview
from pathlib import Path
from datetime import datetime, date, timedelta
import json, sys, os, re

PROJ = Path(__file__).parent
BASE = PROJ / 'entries'
TPL = PROJ / '_template.md'
WEEKDAYS = ['星期一','星期二','星期三','星期四','星期五','星期六','星期日']

API_JS = """
window.saveEntry = function(d, txt) { return pywebview.api.save(d, txt); };
window.readEntry = function(d) { return pywebview.api.read(d); };
window.delEntry  = function(d) { return pywebview.api.delete_entry(d); };
window.getDates  = function()  { return pywebview.api.list_dates(); };
window.getStats  = function()  { return pywebview.api.stats(); };
window.getTmpl   = function(d) { return pywebview.api.template(d); };
"""

HTML = """<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>日记</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        background: #f5f3f0; color: #1f2937; height: 100vh; overflow: hidden; }}
.container {{ max-width: 800px; margin: 0 auto; padding: 20px; height: 100vh; display: flex; flex-direction: column; }}
.header {{ display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px; }}
.header h1 {{ font-size: 22px; font-weight: 700; }}
.header h1 span {{ background: linear-gradient(135deg, #8b5cf6, #ec4899); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
.stats {{ display: flex; gap: 8px; }}
.stat {{ font-size: 12px; color: #6b7280; }}
.stat b {{ color: #8b5cf6; font-size: 14px; }}
.nav {{ display: flex; align-items: center; gap: 8px; margin-bottom: 12px; }}
.nav button {{ padding: 6px 16px; border: 1px solid #e5e7eb; border-radius: 8px;
               background: #fff; cursor: pointer; font-size: 13px; transition: all .15s; }}
.nav button:hover {{ border-color: #8b5cf6; color: #8b5cf6; }}
.nav button.active {{ background: #8b5cf6; color: #fff; border-color: #8b5cf6; }}
.nav .date {{ font-size: 16px; font-weight: 600; margin-left: 8px; }}
.search-area {{ margin-left: auto; display: flex; gap: 4px; align-items: center; }}
.search-area input {{ padding: 4px 8px; border: 1px solid #e5e7eb; border-radius: 6px; font-size: 12px; background: #fff; outline: none; }}
.search-area input:focus {{ border-color: #8b5cf6; }}
.search-area button {{ padding: 4px 10px; border: 1px solid #e5e7eb; border-radius: 6px; background: #fff; cursor: pointer; font-size: 13px; transition: all .15s; }}
.search-area button:hover {{ border-color: #8b5cf6; }}
.toolbar {{ display: flex; align-items: center; gap: 8px; margin-bottom: 8px; flex-wrap: wrap; }}
.toolbar label {{ font-size: 13px; color: #6b7280; }}
.mood-btn, .weather-btn {{ font-size: 18px; padding: 2px 6px; border: 2px solid transparent;
                          border-radius: 8px; cursor: pointer; background: none; transition: all .15s; }}
.mood-btn:hover, .weather-btn:hover {{ transform: scale(1.2); }}
.mood-btn.sel, .weather-btn.sel {{ border-color: #8b5cf6; background: #ede9fe; }}
.editor {{ flex: 1; display: flex; gap: 12px; min-height: 0; }}
.editor textarea {{ flex: 1; padding: 16px; border: 1px solid #e5e7eb; border-radius: 12px;
                    font-family: 'SF Mono', Menlo, monospace; font-size: 14px; line-height: 1.7;
                    resize: none; outline: none; background: #fafaf9; }}
.editor textarea:focus {{ border-color: #8b5cf6; box-shadow: 0 0 0 3px #ede9fe; }}
.preview {{ flex: 1; padding: 16px; border: 1px solid #e5e7eb; border-radius: 12px;
            overflow-y: auto; background: #fff; font-size: 14px; line-height: 1.8; }}
.preview h1 {{ font-size: 20px; margin-bottom: 8px; }}
.preview h2 {{ font-size: 16px; margin: 16px 0 6px; padding-bottom: 4px; border-bottom: 1px solid #eee; }}
.preview ul {{ padding-left: 20px; }}
.preview li {{ margin: 4px 0; }}
.footer {{ display: flex; align-items: center; justify-content: space-between; margin-top: 8px; }}
.footer .info {{ font-size: 12px; color: #6b7280; }}
.actions {{ display: flex; gap: 8px; }}
.actions button {{ padding: 8px 20px; border: none; border-radius: 10px; font-size: 13px;
                   font-weight: 600; cursor: pointer; transition: all .15s; }}
.btn-save {{ background: #8b5cf6; color: #fff; }}
.btn-save:hover {{ background: #7c3aed; }}
.btn-del {{ background: #fff; color: #6b7280; border: 1px solid #e5e7eb !important; }}
.btn-del:hover {{ background: #fef2f2; color: #ef4444; border-color: #fca5a5 !important; }}
.calendar {{ display: flex; gap: 4px; flex-wrap: wrap; margin-bottom: 8px; }}
.cal-item {{ padding: 3px 10px; border-radius: 6px; font-size: 11px; background: #fff;
             border: 1px solid #e5e7eb; cursor: pointer; transition: all .15s; }}
.cal-item:hover {{ border-color: #8b5cf6; transform: translateY(-1px); }}
.cal-item.done {{ background: #ede9fe; border-color: #8b5cf6; color: #8b5cf6; font-weight: 500; }}
.cal-item.today {{ border-color: #f59e0b; color: #d97706; font-weight: 700; background: #fffbeb; }}
.cal-item.active {{ border-color: #3b82f6; color: #2563eb; font-weight: 600; background: #eff6ff; }}
.cal-item.empty {{ opacity: .4; }}
.toast {{ position: fixed; bottom: 20px; right: 20px; padding: 10px 20px; border-radius: 10px;
          color: #fff; font-size: 13px; animation: slideIn .3s; z-index: 999; }}
@keyframes slideIn {{ from {{ opacity: 0; transform: translateY(20px); }} to {{ opacity: 1; transform: translateY(0); }} }}
@media (prefers-color-scheme: dark) {{
  body {{ background: #1c1917; color: #e5e7eb; }}
  .nav button, .cal-item, .preview {{ background: #292524; border-color: #44403c; color: #e5e7eb; }}
  .nav button:hover {{ border-color: #8b5cf6; }}
  .editor textarea {{ background: #292524; color: #e5e7eb; border-color: #44403c; }}
  .editor textarea:focus {{ border-color: #8b5cf6; }}
  .mood-btn.sel, .weather-btn.sel {{ background: #4c1d95; }}
  .cal-item.done {{ background: #4c1d95; border-color: #8b5cf6; }}
  .cal-item.today {{ border-color: #f59e0b; color: #fbbf24; background: #451a03; }}
  .cal-item.active {{ border-color: #3b82f6; color: #60a5fa; background: #1e3a5f; }}
  .btn-del {{ background: #292524; color: #a8a29e; border-color: #44403c !important; }}
  .header h1, .nav .date {{ color: #e5e7eb; }}
}}
</style>
</head>
<body>
<div class="container" id="app">
  <div class="header">
    <h1>📔 <span>日记</span></h1>
    <div class="stats" id="stats"></div>
  </div>
  <div class="calendar" id="calendar"></div>
  <div class="nav">
    <button onclick="go(-1)">‹ 前一天</button>
    <button onclick="go(0)" id="todayBtn" class="active">📅 今天</button>
    <button onclick="go(1)">后一天 ›</button>
    <span class="date" id="dateLabel"></span>
    <span class="search-area">
      <input type="date" id="dateSearch">
      <button onclick="searchDate()">🔍</button>
    </span>
  </div>
  <div class="toolbar">
    <label>心情:</label>
    <span id="moods">😊 😐 😔 😤 🥳</span>
    <label style="margin-left:12px">天气:</label>
    <span id="weathers">☀️ ⛅ ☁️ 🌧 ❄️</span>
  </div>
  <div class="editor">
    <textarea id="editor" placeholder="今天发生了什么？写下你的想法..."></textarea>
    <div class="preview" id="preview"></div>
  </div>
  <div class="footer">
    <div class="info" id="wordCount"></div>
    <div class="actions">
      <button class="btn-del" onclick="handleDelete()">🗑 删除</button>
      <button class="btn-save" onclick="save()">💾 保存</button>
    </div>
  </div>
</div>
<div class="toast" id="toast" style="display:none"></div>
<script>
{API_JS}
let cur = new Date();
let mood = '😊', weather = '☀️';

function fmt(d) {{
  return d.getFullYear() + '-' + String(d.getMonth()+1).padStart(2,'0') + '-' + String(d.getDate()).padStart(2,'0');
}}
function ds(d) {{ return fmt(d); }}
function parseFrontMatter(txt) {{
  let mood = '😊', weather = '☀️', body = txt;
  if (txt.startsWith('---\\n')) {{
    let end = txt.indexOf('\\n---\\n', 4);
    if (end > 0) {{
      let fm = txt.slice(4, end);
      for (let line of fm.split('\\n')) {{
        if (line.startsWith('mood: ')) mood = line.slice(6).trim();
        if (line.startsWith('weather: ')) weather = line.slice(9).trim();
      }}
      body = txt.slice(end + 5);
    }}
  }}
  return {{mood, weather, body}};
}}

function setMoodWeatherUI(m, w) {{
  mood = m; weather = w;
  document.querySelectorAll('#moods .mood-btn').forEach(el => {{
    el.classList.toggle('sel', el.textContent === m);
  }});
  document.querySelectorAll('#weathers .weather-btn').forEach(el => {{
    el.classList.toggle('sel', el.textContent === w);
  }});
}}

function load() {{
  let d = ds(cur);
  if (!window.pywebview || !window.pywebview.api) {{
    setTimeout(load, 50);
    return;
  }}
  readEntry(d).then(txt => {{
    if (txt) {{
      let fm = parseFrontMatter(txt);
      setMoodWeatherUI(fm.mood, fm.weather);
      document.getElementById('editor').value = fm.body;
      preview();
    }} else {{
      getTmpl(d).then(t => {{
        let now = new Date();
        let timeStr = String(now.getHours()).padStart(2,'0') + ':' + String(now.getMinutes()).padStart(2,'0') + ':' + String(now.getSeconds()).padStart(2,'0');
        let content = t || '# ' + d + ' ' + getWeekday(cur) + '\\n\\n⏰ ' + timeStr + '\\n\\n## 📝 今天做了什么？\\n\\n\\n## 💡 收获与思考\\n\\n\\n## ✅ 昨日计划完成情况\\n\\n\\n## 📋 明日计划\\n\\n';
        setMoodWeatherUI('😊', '☀️');
        document.getElementById('editor').value = content;
        preview();
      }});
    }}
  }});
  document.getElementById('dateLabel').textContent = d + '  ' + getWeekday(cur);
  document.getElementById('todayBtn').className = ds(cur)===ds(new Date()) ? 'active' : '';
  loadStats();
  loadCalendar();
}}
function getWeekday(d) {{ return ['星期日','星期一','星期二','星期三','星期四','星期五','星期六'][d.getDay()]; }}
function preview() {{
  let t = document.getElementById('editor').value;
  let p = document.getElementById('preview');
  p.innerHTML = simpleMarkdown(t);
  let wc = t.trim() ? t.split(/\\s+/).length : 0;
  document.getElementById('wordCount').textContent = wc + ' 字 | ' + t.length + ' 字符';
  // Attach interactive checkbox handlers
  p.querySelectorAll('input[type=checkbox]').forEach(cb => {{
    cb.addEventListener('change', function() {{
      let lines = document.getElementById('editor').value.split('\\n');
      let cbIdx = parseInt(this.dataset.cb);
      // Find matching checkbox line in editor
      let editorCbNum = 0, found = -1;
      for (let i = 0; i < lines.length; i++) {{
        if (lines[i].match(/^- \[/)) {{
          if (editorCbNum === cbIdx) {{ found = i; break; }}
          editorCbNum++;
        }}
      }}
      if (found >= 0) {{
        lines[found] = this.checked ? lines[found].replace(/^- \[ \]/, '- [x]') : lines[found].replace(/^- \[x\]/, '- [ ]');
        document.getElementById('editor').value = lines.join('\\n');
        preview();
      }}
    }});
  }});
}}
function simpleMarkdown(t) {{
  if (!t) return '<p style="color:#999">暂无内容</p>';
  let lines = t.split('\\n');
  let out = [], inList = false, cbCnt = 0;
  let curSection = '', secNum = 0;
  for (let line of lines) {{
    let m;
    if (m = line.match(/^### (.+)/)) {{
      if (inList) {{ out.push('</ul>'); inList = false; }}
      out.push('<h3>' + m[1] + '</h3>');
    }}
    else if (m = line.match(/^## (.+)/)) {{
      if (inList) {{ out.push('</ul>'); inList = false; }}
      curSection = m[1]; secNum = 0;
      out.push('<h2>' + curSection + '</h2>');
    }}
    else if (m = line.match(/^# (.+)/)) {{
      if (inList) {{ out.push('</ul>'); inList = false; }}
      curSection = ''; secNum = 0;
      out.push('<h1>' + m[1] + '</h1>');
    }}
    else if (m = line.match(/^- \[x\] (.+)/i)) {{ out.push((inList?'':'<ul>') + '<li><input type=checkbox checked data-cb="' + (cbCnt++) + '">' + m[1] + '</li>'); inList = true; }}
    else if (m = line.match(/^- \[ \] (.+)/)) {{ out.push((inList?'':'<ul>') + '<li><input type=checkbox data-cb="' + (cbCnt++) + '">' + m[1] + '</li>'); inList = true; }}
    else if (m = line.match(/^- (.+)/)) {{ out.push((inList?'':'<ul>') + '<li>' + m[1] + '</li>'); inList = true; }}
    else if (m = line.match(/^\\d+\\. (.+)/)) {{ out.push((inList?'':'<ul>') + '<li>' + m[1] + '</li>'); inList = true; }}
    else {{
      if (inList) {{ out.push('</ul>'); inList = false; }}
      if (line.trim() === '') {{ out.push(''); }}
      else {{
        line = line.replace(/\\*\\*(.+?)\\*\\*/g, '<strong>$1</strong>').replace(/\\*(.+?)\\*/g, '<em>$1</em>');
        if (curSection.includes('📝') || curSection.includes('💡')) {{
          out.push('<p><b>' + (++secNum) + '.</b> ' + line + '</p>');
        }} else {{
          out.push('<p>' + line + '</p>');
        }}
      }}
    }}
  }}
  if (inList) out.push('</ul>');
  return out.join('\\n');
}}
function save() {{
  let txt = document.getElementById('editor').value;
  let fm = '---\\nmood: ' + mood + '\\nweather: ' + weather + '\\n---\\n';
  saveEntry(ds(cur), fm + txt).then(() => {{
    toast('✅ 已保存', '#10b981');
    loadCalendar();
    loadStats();
  }});
}}
function handleDelete() {{
  if (ds(cur) === ds(new Date())) {{ toast('⚠️ 不能删除今天', '#ef4444'); return; }}
  if (!confirm('确定删除 ' + ds(cur) + ' 的记录？')) return;
  window.delEntry(ds(cur)).then(() => {{
    toast('🗑 已删除', '#ef4444');
    load();
  }});
}}
function go(n) {{
  if (n === 0) {{ cur = new Date(); }}
  else {{ cur.setDate(cur.getDate() + n); }}
  load();
}}
function goDate(dStr) {{
  let p = dStr.split('-');
  cur = new Date(parseInt(p[0]), parseInt(p[1])-1, parseInt(p[2]));
  load();
}}
function searchDate() {{
  let val = document.getElementById('dateSearch').value;
  if (val) goDate(val);
}}
document.getElementById('dateSearch').addEventListener('keydown', function(e) {{
  if (e.key === 'Enter') searchDate();
}});
function autoNumberPlans() {{
  let el = document.getElementById('editor');
  let val = el.value;
  let m = val.match(/## 📋 明日计划\\n([\\s\\S]*?)(\\n## |$)/);
  if (!m) return;
  let lines = m[1].split('\\n');
  let num = 1;
  let newLines = lines.map(l => {{
    if (l.trim() === '') return l;
    return num++ + '. ' + l.replace(/^\\d+\\.\\s*/, '').trim();
  }});
  let newSection = newLines.join('\\n');
  el.value = val.slice(0, m.index + '## 📋 明日计划\\n'.length) + newSection + val.slice(m.index + m[0].length);
}}

document.getElementById('editor').addEventListener('input', function(e) {{
  autoNumberPlans();
  preview();
}});

// Mood & Weather (per-day, stored in front matter)
document.getElementById('moods').addEventListener('click', function(e) {{
  if (e.target.tagName === 'SPAN') {{
    this.querySelectorAll('.sel').forEach(el => el.classList.remove('sel'));
    e.target.classList.add('sel');
    mood = e.target.textContent;
  }}
}});
document.getElementById('weathers').addEventListener('click', function(e) {{
  if (e.target.tagName === 'SPAN') {{
    this.querySelectorAll('.sel').forEach(el => el.classList.remove('sel'));
    e.target.classList.add('sel');
    weather = e.target.textContent;
  }}
}});

// Set mood/weather buttons
document.getElementById('moods').innerHTML = ['😊','😐','😔','😤','🥳'].map(m => `<span class="mood-btn sel">${{m}}</span>`).join('');
document.getElementById('weathers').innerHTML = ['☀️','⛅','☁️','🌧','❄️'].map(w => `<span class="weather-btn">${{w}}</span>`).join('');
document.querySelector('#weathers span:first-child').classList.add('sel');

function loadStats() {{
  getStats().then(s => {{
    document.getElementById('stats').innerHTML =
      '<span class="stat">总 <b>' + s.total + '</b></span>' +
      '<span class="stat">今年 <b>' + s.this_year + '</b></span>' +
      '<span class="stat">本月 <b>' + s.this_month + '</b></span>' +
      '<span class="stat">连续 <b>' + s.streak + '</b>天</span>';
  }});
}}
function loadCalendar() {{
  getDates().then(dates => {{
    let html = dates.map(ds2 => {{
      let p = ds2.split('-');
      let d = new Date(parseInt(p[0]), parseInt(p[1])-1, parseInt(p[2]));
      let isToday = ds2 === ds(new Date());
      let isViewing = ds2 === ds(cur);
      let cls = 'cal-item done';
      if (isToday) cls += ' today';
      if (isViewing) cls += ' active';
      let label = (d.getMonth()+1) + '/' + d.getDate();
      return '<span class="' + cls + '" data-date="' + ds2 + '">' + label + '</span>';
    }}).join('');
    let cal = document.getElementById('calendar');
    cal.innerHTML = html || '<span style="color:#999;font-size:13px">暂无记录</span>';
    cal.querySelectorAll('.cal-item').forEach(function(el) {{
      el.addEventListener('click', function() {{
        if (this.dataset.date) goDate(this.dataset.date);
      }});
    }});
  }});
}}

function toast(msg, color) {{
  let el = document.getElementById('toast');
  el.textContent = msg;
  el.style.background = color || '#1f2937';
  el.style.display = 'block';
  setTimeout(() => el.style.display = 'none', 2000);
}}

load();
</script>
</body>
</html>""".replace('{API_JS}', API_JS).replace('{{', '{').replace('}}', '}')


class DiaryAPI:
    def _path(self, d):
        dt = date.fromisoformat(d)
        return BASE / str(dt.year) / f'{dt.month:02d}' / f'{d}.md'

    def read(self, d):
        p = self._path(d)
        return p.read_text(encoding='utf-8') if p.exists() else ''

    def save(self, d, txt):
        p = self._path(d)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(txt, encoding='utf-8')
        # Update tomorrow's ✅ 昨日计划完成情况 with today's 📋 明日计划
        dt = date.fromisoformat(d)
        tm = (dt + timedelta(days=1)).isoformat()
        tp = self._path(tm)
        if tp.exists():
            ttxt = tp.read_text(encoding='utf-8')
            body = ttxt
            if ttxt.startswith('---\n'):
                end = ttxt.find('\n---\n', 4)
                if end > 0:
                    body = ttxt[end+5:]
            today_body = txt
            if txt.startswith('---\n'):
                end = txt.find('\n---\n', 4)
                if end > 0:
                    today_body = txt[end+5:]
            m = re.search(r'## 📋 明日计划\n(.*?)(?=\n## |\Z)', today_body, re.DOTALL)
            if m:
                tasks = []
                for line in m.group(1).split('\n'):
                    line = line.strip()
                    if not line:
                        continue
                    task = re.sub(r'^\d+\.\s*', '', line)
                    task = re.sub(r'^-\s*\[\s*\]\s*', '', task).strip()
                    if task:
                        tasks.append('- [ ] ' + task)
                if tasks:
                    tasks_str = '\n'.join(tasks) + '\n'
                    new_body = re.sub(
                        r'(## ✅ 昨日计划完成情况\n\n).*?(?=\n## )',
                        r'\g<1>' + tasks_str,
                        body, flags=re.DOTALL
                    )
                    if new_body != body:
                        if ttxt.startswith('---\n'):
                            end = ttxt.find('\n---\n', 4)
                            if end > 0:
                                tp.write_text(ttxt[:end+5] + '\n' + new_body, encoding='utf-8')
                                return 'ok'
                        tp.write_text(new_body, encoding='utf-8')
        return 'ok'

    def delete_entry(self, d):
        p = self._path(d)
        if p.exists():
            p.unlink()
        return 'ok'

    def list_dates(self):
        return sorted({f.stem for f in BASE.rglob('*.md')})

    def stats(self):
        ds = self.list_dates()
        t = date.today()
        total = len(ds)
        yr = sum(1 for d in ds if d.startswith(str(t.year)))
        mo = sum(1 for d in ds if d.startswith(t.strftime('%Y-%m')))
        streak = 0
        d = t
        while d.strftime('%Y-%m-%d') in ds:
            streak += 1
            d -= timedelta(days=1)
        return {'total': total, 'this_year': yr, 'this_month': mo, 'streak': streak}

    def template(self, d):
        if TPL.exists():
            tpl = TPL.read_text(encoding='utf-8')
        else:
            tpl = '# 📔 {{date}} {{weekday}}\n\n⏰ {{time}}\n\n## 📝 今天做了什么？\n\n\n## 💡 收获与思考\n\n\n## ✅ 昨日计划完成情况\n\n\n## 📋 明日计划\n\n'
        dt = date.fromisoformat(d)
        now = datetime.now()
        tpl = tpl.replace('{{date}}', d).replace('{{weekday}}', WEEKDAYS[dt.weekday()]).replace('{{time}}', now.strftime('%H:%M:%S'))

        # Auto-populate yesterday's 明日计划 into today's 昨日计划完成情况
        yd = (dt - timedelta(days=1)).isoformat()
        yp = self._path(yd)
        if yp.exists():
            ytxt = yp.read_text(encoding='utf-8')
            body = ytxt
            if ytxt.startswith('---\n'):
                end = ytxt.find('\n---\n', 4)
                if end > 0:
                    body = ytxt[end+5:]
            m = re.search(r'## 📋 明日计划\n(.*?)(?=\n## |\Z)', body, re.DOTALL)
            if m:
                tasks = []
                for line in m.group(1).split('\n'):
                    line = line.strip()
                    if not line:
                        continue
                    task = re.sub(r'^\d+\.\s*', '', line)
                    task = re.sub(r'^-\s*\[\s*\]\s*', '', task).strip()
                    if task:
                        tasks.append('- [ ] ' + task)
                if tasks:
                    tasks_str = '\n'.join(tasks) + '\n'
                    tpl = tpl.replace('## ✅ 昨日计划完成情况\n\n', '## ✅ 昨日计划完成情况\n\n' + tasks_str)
        return tpl


if __name__ == '__main__':
    api = DiaryAPI()
    window = webview.create_window(
        '日记', html=HTML, js_api=api,
        width=780, height=660,
        resizable=True,
        text_select=True,
    )
    webview.start()
