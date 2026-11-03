"""Process Log (UI_2): a small append-only study log.

One log = one JSON file in ../logs, named <first-tag>_<YYYYMMDD-HHMM>.json.
Entries are only ever appended; nothing already written is edited.
"""
import json
import os
import re
import sys
import threading
import time
from datetime import datetime
from pathlib import Path

from flask import Flask, Response, jsonify, request

APP_DIR = Path(__file__).resolve().parent
LOGS_DIR = APP_DIR.parent / "logs"
SCHEMA = "ui2-1"
KINDS = ("input", "note", "output", "pre", "post")
ID_RE = re.compile(r"^[a-z0-9-]+_\d{8}-\d{4}(-\d+)?$")
MAX_TEXT = 100_000

if sys.platform == "win32":
    # Don't let a stale server on the same port silently share it.
    from werkzeug.serving import BaseWSGIServer
    BaseWSGIServer.allow_reuse_address = False

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 1_000_000
_lock = threading.Lock()
_last_beat = [None]


def now():
    return datetime.now().isoformat(timespec="seconds")


def clean_tags(raw):
    """Strip, drop empties, de-duplicate case-insensitively, keep order."""
    seen, out = set(), []
    for t in raw if isinstance(raw, list) else []:
        t = str(t).strip().replace(",", " ")[:60]
        if t and t.lower() not in seen:
            seen.add(t.lower())
            out.append(t)
    return out


def slugify(tag):
    return re.sub(r"[^a-z0-9]+", "-", tag.lower()).strip("-")[:40] or "log"


def log_path(lid):
    if not ID_RE.match(lid or ""):
        return None
    p = LOGS_DIR / f"{lid}.json"
    return p if p.is_file() else None


def read_log(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def write_log(p, data):
    """Atomic write: a crash mid-save leaves the previous file intact."""
    tmp = p.with_suffix(".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, p)


def all_logs():
    LOGS_DIR.mkdir(exist_ok=True)
    out = []
    for p in LOGS_DIR.glob("*.json"):
        try:
            out.append((p, read_log(p)))
        except (OSError, ValueError):
            continue  # skip unreadable files rather than break the list
    return out


@app.after_request
def _headers(resp):
    resp.headers["Cache-Control"] = "no-store"
    return resp


@app.get("/")
def index():
    return Response(PAGE, mimetype="text/html")


@app.get("/api/logs")
def list_logs():
    rows = []
    for p, d in all_logs():
        ents = d.get("entries", [])
        rows.append({
            "id": d.get("id", p.stem),
            "title": d.get("title", p.stem),
            "count": len(ents),
            "last": ents[-1]["ts"] if ents else d.get("created", ""),
            "tags": d.get("tags", []),
        })
    rows.sort(key=lambda r: r["last"], reverse=True)
    return jsonify(rows)


@app.post("/api/logs")
def new_log():
    tags = clean_tags((request.get_json(silent=True) or {}).get("tags"))
    if not tags:
        return jsonify(error="Add at least one tag; the first becomes the log's title."), 400
    LOGS_DIR.mkdir(exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M")
    base = f"{slugify(tags[0])}_{stamp}"
    with _lock:
        lid, n = base, 1
        while (LOGS_DIR / f"{lid}.json").exists():
            n += 1
            lid = f"{base}-{n}"
        data = {"schema": SCHEMA, "id": lid, "title": tags[0],
                "created": now(), "tags": tags, "entries": []}
        write_log(LOGS_DIR / f"{lid}.json", data)
    return jsonify(data), 201


@app.get("/api/logs/<lid>")
def get_log(lid):
    p = log_path(lid)
    if not p:
        return jsonify(error="No such log."), 404
    return jsonify(read_log(p))


@app.post("/api/logs/<lid>/entries")
def add_entry(lid):
    p = log_path(lid)
    if not p:
        return jsonify(error="No such log."), 404
    d = request.get_json(silent=True) or {}
    kind = d.get("kind")
    text = str(d.get("text") or "").strip()
    topic = str(d.get("topic") or "").strip()[:80] or None
    if kind not in KINDS:
        return jsonify(error="Unknown entry kind."), 400
    if not text:
        return jsonify(error="Nothing to save."), 400
    if len(text) > MAX_TEXT:
        return jsonify(error="That entry is too long."), 400
    if kind in ("pre", "post") and not topic:
        return jsonify(error="Give this reflection a topic."), 400
    with _lock:
        data = read_log(p)
        entry = {
            "id": f"{data['id']}:{len(data['entries'])}",
            "kind": kind,
            "text": text,
            "summary": str(d.get("summary") or "").strip()[:500],
            "tags": clean_tags(d.get("tags")),
            "topic": topic,
            "ts": now(),
        }
        data["entries"].append(entry)
        known = {t.lower() for t in data["tags"]}
        for t in entry["tags"]:
            if t.lower() not in known:
                data["tags"].append(t)
                known.add(t.lower())
        write_log(p, data)
    return jsonify(entry), 201


@app.get("/api/tags")
def tag_bank():
    counts, forms = {}, {}
    for _, d in all_logs():
        names = list(d.get("tags", []))
        for e in d.get("entries", []):
            names += e.get("tags", [])
        for t in names:
            k = t.lower()
            counts[k] = counts.get(k, 0) + 1
            forms.setdefault(k, t)
    ordered = sorted(counts, key=lambda k: (-counts[k], k))
    return jsonify([forms[k] for k in ordered])


@app.post("/api/heartbeat")
def heartbeat():
    _last_beat[0] = time.time()
    return "", 204


def _watchdog(timeout=120):
    """Windowless launches have no console to close, so stop when the tab goes away."""
    while True:
        time.sleep(10)
        t = _last_beat[0]
        if t and time.time() - t > timeout:
            os._exit(0)


PAGE = r'''<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Process Log</title>
<style>
:root{--bg:#f6f7f5;--panel:#fff;--ink:#1d2321;--mut:#66726c;--line:#dde2de;--acc:#0f766e;--accink:#fff;--chip:#e3f1ee;--warn:#a15c00;--blue:#2b5f9e}
@media (prefers-color-scheme:dark){:root{--bg:#141817;--panel:#1d2321;--ink:#e6ebe8;--mut:#9aa6a0;--line:#2e3835;--acc:#2dd4bf;--accink:#04201c;--chip:#23403c;--warn:#f0b35a;--blue:#8fb8ee}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.5 system-ui,-apple-system,"Segoe UI",sans-serif}
header{display:flex;gap:10px;align-items:center;padding:12px 16px;border-bottom:1px solid var(--line);background:var(--panel);position:sticky;top:0;z-index:2}
header h1{font-size:17px;margin:0;flex:1;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
button{font:inherit;cursor:pointer;border:1px solid var(--line);background:var(--panel);color:var(--ink);padding:6px 12px;border-radius:7px}
button:hover{border-color:var(--acc)}
button.primary{background:var(--acc);color:var(--accink);border-color:var(--acc);font-weight:600}
[hidden]{display:none!important}
main{display:grid;grid-template-columns:minmax(0,1fr) 300px;gap:16px;padding:16px;max-width:1100px;margin:0 auto}
@media (max-width:800px){main{grid-template-columns:1fr}}
#left{display:flex;flex-direction:column;gap:12px}
section,.card{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:14px}
h2{font-size:13px;text-transform:uppercase;letter-spacing:.05em;color:var(--mut);margin:0 0 8px}
label{display:block;font-weight:600;margin:10px 0 4px}
label small{font-weight:400;color:var(--mut);margin-left:6px}
textarea,input[type=text]{width:100%;font:inherit;color:var(--ink);background:var(--bg);border:1px solid var(--line);border-radius:7px;padding:8px}
textarea{min-height:90px;resize:vertical}
.row{display:flex;gap:8px;justify-content:flex-end;margin-top:8px;align-items:center}
.row .hint{flex:1;color:var(--mut);font-size:13px}
.chip{background:var(--chip);border:0;border-radius:99px;padding:2px 10px;margin:0 4px 4px 0;font-size:13px}
.tagin input{margin-top:4px}
.tagin label{margin-top:0}
.sug{margin-top:4px}
.sug-item{border:1px dashed var(--line);background:transparent;border-radius:99px;padding:1px 9px;margin:0 4px 4px 0;font-size:13px;color:var(--mut)}
.loglist{list-style:none;margin:0;padding:0}
.loglist li button{display:block;width:100%;text-align:left;margin-bottom:6px}
.loglist li.cur button{border-color:var(--acc);background:var(--chip)}
.loglist small{display:block;color:var(--mut)}
.entry{border-top:1px solid var(--line);padding:10px 0}
.entry:first-of-type{border-top:0}
.meta{font-size:12px;color:var(--mut)}
.kind{display:inline-block;font-size:11px;font-weight:700;text-transform:uppercase;border-radius:4px;padding:0 6px;margin-right:6px;background:var(--chip);color:var(--acc)}
.kind[data-k=output]{color:var(--blue)}
.kind[data-k=pre],.kind[data-k=post]{color:var(--warn)}
.kind[data-k=note]{color:var(--mut)}
.body{white-space:pre-wrap;word-break:break-word}
.sum{font-style:italic;color:var(--mut)}
.err{color:#b42318;min-height:1.3em;font-size:13px}
dialog{border:1px solid var(--line);border-radius:12px;background:var(--panel);color:var(--ink);width:min(560px,94vw);padding:16px}
dialog::backdrop{background:rgba(0,0,0,.4)}
.tabs{display:flex;gap:6px;margin-bottom:6px}
.tabs button.on{background:var(--acc);color:var(--accink);border-color:var(--acc)}
.empty{color:var(--mut)}
</style></head><body>
<header>
  <h1 id="title">Process Log</h1>
  <button id="b-out" class="primary" hidden>Log LLM output</button>
  <button id="b-ref" hidden>Reflect</button>
  <button id="b-new">New log</button>
</header>
<main>
  <div id="left"></div>
  <aside><div class="card"><h2>Recent logs</h2><ul class="loglist" id="loglist"></ul></div></aside>
</main>

<dialog id="d-out"><form method="dialog" onsubmit="return false">
  <h2>Log LLM output</h2>
  <label>Pasted output <small>just the part that matters</small></label>
  <textarea id="o-text"></textarea>
  <label>Short summary <small>optional</small></label>
  <input type="text" id="o-sum" maxlength="500">
  <div id="o-tags" style="margin-top:10px"></div>
  <div class="err" id="o-err"></div>
  <div class="row"><button type="button" id="o-cancel">Cancel</button><button type="button" class="primary" id="o-save">Save output</button></div>
</form></dialog>

<dialog id="d-ref"><form method="dialog" onsubmit="return false">
  <h2>Reflect</h2>
  <div class="tabs"><button type="button" id="t-pre" class="on">Pre</button><button type="button" id="t-post">Post</button></div>
  <label>Topic <small id="r-hint"></small></label>
  <input type="text" id="r-topic" list="r-topics" maxlength="80" autocomplete="off">
  <datalist id="r-topics"></datalist>
  <label id="r-label"></label>
  <textarea id="r-text"></textarea>
  <div class="err" id="r-err"></div>
  <div class="row"><button type="button" id="r-cancel">Cancel</button><button type="button" class="primary" id="r-save">Save</button></div>
</form></dialog>

<script>
const $=s=>document.querySelector(s);
let cur=null, bank=[], logs=[], tagIns=[];

function h(tag,props={},...kids){
  const e=document.createElement(tag);
  for(const [k,v] of Object.entries(props)){
    if(k==='class')e.className=v;
    else if(k.startsWith('on'))e.addEventListener(k.slice(2),v);
    else e.setAttribute(k,v);
  }
  for(const c of kids.flat())if(c!=null)e.append(c);
  return e;
}
async function api(path,body){
  const opt=body===undefined?{}:{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)};
  const r=await fetch(path,opt);
  const j=r.status===204?null:await r.json();
  if(!r.ok)throw new Error((j&&j.error)||'Something went wrong.');
  return j;
}
const when=ts=>new Date(ts).toLocaleString([],{month:'short',day:'numeric',hour:'numeric',minute:'2-digit'});

function tagInput(label){
  let tags=[];
  const chips=h('span',{class:'chips'});
  const inp=h('input',{type:'text',placeholder:'type a tag, press Enter',autocomplete:'off',maxlength:'60'});
  const sug=h('div',{class:'sug'});
  const has=t=>tags.some(x=>x.toLowerCase()===t.toLowerCase());
  function render(){
    chips.replaceChildren(...tags.map(t=>h('button',{type:'button',class:'chip',title:'Remove',onclick:()=>{tags=tags.filter(x=>x!==t);render();}},t+' ×')));
    const q=inp.value.trim().toLowerCase();
    sug.replaceChildren(...bank.filter(t=>!has(t)&&(!q||t.toLowerCase().includes(q))).slice(0,8)
      .map(t=>h('button',{type:'button',class:'sug-item',onclick:()=>add(t)},t)));
  }
  function add(t){
    t=t.trim().replace(/,/g,' ');
    if(t&&!has(t))tags.push(t);
    inp.value='';render();inp.focus();
  }
  inp.addEventListener('input',render);
  inp.addEventListener('keydown',e=>{
    if(e.key==='Enter'||e.key===','){e.preventDefault();add(inp.value);}
    else if(e.key==='Backspace'&&!inp.value&&tags.length){tags.pop();render();}
  });
  const t={
    el:h('div',{class:'tagin'},h('label',{},label),chips,inp,sug),
    get(){if(inp.value.trim())add(inp.value);return [...tags];},
    clear(){tags=[];inp.value='';render();},
    refresh:render,
  };
  tagIns.push(t);render();return t;
}

async function refreshLogs(){logs=await api('/api/logs');renderLogs();}
async function refreshBank(){bank=await api('/api/tags');tagIns.forEach(t=>t.refresh());}

function renderLogs(){
  const ul=$('#loglist');
  if(!logs.length){ul.replaceChildren(h('li',{class:'empty'},'No logs yet.'));return;}
  ul.replaceChildren(...logs.map(l=>h('li',{class:cur&&cur.id===l.id?'cur':''},
    h('button',{type:'button',onclick:()=>openLog(l.id)},h('strong',{},l.title),h('small',{},`${l.count} entries · ${l.last?when(l.last):''}`)))));
}

async function openLog(id){
  try{cur=await api('/api/logs/'+id);}catch(e){alert(e.message);return;}
  render();renderLogs();
}

function openTopics(){
  const open=[];
  for(const e of cur.entries){
    if(e.kind==='pre'&&e.topic&&!open.includes(e.topic))open.push(e.topic);
    if(e.kind==='post'&&e.topic){const i=open.indexOf(e.topic);if(i>=0)open.splice(i,1);}
  }
  return open;
}

let capTags;
function render(){
  tagIns=[];
  $('#title').textContent=cur?cur.title:'Process Log';
  $('#b-out').hidden=$('#b-ref').hidden=!cur;
  const left=$('#left');
  if(!cur){
    const newTags=tagInput('Tags for this log');
    const err=h('div',{class:'err'});
    const go=h('button',{type:'button',class:'primary',onclick:async()=>{
      try{cur=await api('/api/logs',{tags:newTags.get()});await refreshLogs();await refreshBank();render();}
      catch(e){err.textContent=e.message;}
    }},'Start log');
    left.replaceChildren(h('section',{},h('h2',{},'New log'),
      h('p',{class:'empty'},'The first tag becomes the log’s title. Other tags go into your tag bank for suggestions. Or pick an earlier log on the right to keep adding to it.'),
      newTags.el,err,h('div',{class:'row'},go)));
    return;
  }
  capTags=tagInput('Tags for the next entry');
  const mk=(kind,name,hint)=>{
    const ta=h('textarea');
    const err=h('div',{class:'err'});
    const add=async()=>{
      err.textContent='';
      try{await addEntry({kind,text:ta.value,tags:capTags.get()});ta.value='';capTags.clear();ta.focus();}
      catch(e){err.textContent=e.message;}
    };
    ta.addEventListener('keydown',e=>{if(e.key==='Enter'&&(e.ctrlKey||e.metaKey)){e.preventDefault();add();}});
    return h('section',{},h('label',{style:'margin-top:0'},name,h('small',{},hint)),ta,err,
      h('div',{class:'row'},h('span',{class:'hint'},'Ctrl/⌘+Enter to add'),h('button',{type:'button',class:'primary',onclick:add},'Add '+kind)));
  };
  left.replaceChildren(
    h('section',{},capTags.el),
    mk('input','Input','what you typed or asked'),
    mk('note','Note','your own thought'),
    h('section',{id:'feed'}));
  renderFeed();
}

function renderFeed(){
  const feed=$('#feed');
  const list=[...cur.entries].reverse();
  feed.replaceChildren(h('h2',{},`This log · ${cur.entries.length} entries`),
    ...(list.length?list.map(e=>h('div',{class:'entry'},
      h('div',{class:'meta'},h('span',{class:'kind','data-k':e.kind},e.kind),when(e.ts),e.topic?` · topic: ${e.topic}`:''),
      h('div',{class:'body'},e.text),
      e.summary?h('div',{class:'sum'},e.summary):null,
      e.tags.length?h('div',{class:'meta'},e.tags.map(t=>'#'+t).join('  ')):null))
    :[h('div',{class:'empty'},'Nothing here yet.')]));
}

async function addEntry(p){
  const e=await api(`/api/logs/${cur.id}/entries`,p);
  cur.entries.push(e);renderFeed();
  refreshLogs();refreshBank();
  return e;
}

/* LLM output dialog */
let outTags;
$('#b-out').onclick=()=>{
  outTags=tagInput('Tags');$('#o-tags').replaceChildren(outTags.el);
  $('#o-text').value='';$('#o-sum').value='';$('#o-err').textContent='';
  $('#d-out').showModal();$('#o-text').focus();
};
$('#o-cancel').onclick=()=>$('#d-out').close();
$('#o-save').onclick=async()=>{
  try{await addEntry({kind:'output',text:$('#o-text').value,summary:$('#o-sum').value,tags:outTags.get()});$('#d-out').close();}
  catch(e){$('#o-err').textContent=e.message;}
};

/* Reflect dialog */
let mode='pre';
function setMode(m){
  mode=m;
  $('#t-pre').classList.toggle('on',m==='pre');$('#t-post').classList.toggle('on',m==='post');
  const open=openTopics();
  $('#r-label').textContent=m==='pre'?'What do you expect, plan, or already think you know?':'What happened? What surprised you? What would you do differently?';
  $('#r-hint').textContent=m==='post'?(open.length?'open: '+open.join(', '):'no open topics yet – start one under Pre'):'a short name for what you are about to work on';
  const all=[...new Set(cur.entries.filter(e=>e.topic).map(e=>e.topic))];
  $('#r-topics').replaceChildren(...(m==='post'?open:all).map(t=>h('option',{value:t})));
  if(m==='post'&&open.length&&!$('#r-topic').value)$('#r-topic').value=open[open.length-1];
}
$('#b-ref').onclick=()=>{
  $('#r-topic').value='';$('#r-text').value='';$('#r-err').textContent='';
  setMode('pre');$('#d-ref').showModal();$('#r-topic').focus();
};
$('#t-pre').onclick=()=>setMode('pre');
$('#t-post').onclick=()=>setMode('post');
$('#r-cancel').onclick=()=>$('#d-ref').close();
$('#r-save').onclick=async()=>{
  try{await addEntry({kind:mode,text:$('#r-text').value,topic:$('#r-topic').value});$('#d-ref').close();}
  catch(e){$('#r-err').textContent=e.message;}
};

$('#b-new').onclick=()=>{cur=null;render();renderLogs();};

(async()=>{
  await refreshBank();await refreshLogs();render();
  setInterval(()=>fetch('/api/heartbeat',{method:'POST'}).catch(()=>{}),15000);
  fetch('/api/heartbeat',{method:'POST'}).catch(()=>{});
})();
</script></body></html>'''


if __name__ == "__main__":
    port = int(os.environ.get("UI2_PORT", "5173"))
    if os.environ.get("UI2_WATCHDOG") == "1":
        threading.Thread(target=_watchdog, daemon=True).start()
    app.run(host="127.0.0.1", port=port, threaded=True, debug=False)
