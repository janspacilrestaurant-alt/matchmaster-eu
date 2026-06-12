import streamlit as st
import json
import os
from datetime import datetime, date, timedelta
import calendar as cal_lib
import uuid

st.set_page_config(
    page_title="TaskFlow",
    page_icon="✓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:ital,wght@0,300;0,400;0,500;0,600;0,700;1,400&display=swap');
* { font-family: 'Inter', sans-serif !important; box-sizing: border-box; }

/* ── Sidebar ─────────────────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: #ffffff !important;
    border-right: 1px solid #e5e7eb !important;
}
[data-testid="stSidebar"] .stButton > button {
    background: transparent !important;
    border: none !important;
    color: #374151 !important;
    text-align: left !important;
    padding: 6px 10px !important;
    border-radius: 7px !important;
    font-size: 13.5px !important;
    width: 100% !important;
    font-weight: 400 !important;
    transition: background 0.12s !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: #f3f4f6 !important;
    color: #111827 !important;
}
[data-testid="stSidebar"] .stButton > button[kind="primary"] {
    background: #fef2f2 !important;
    color: #dc2626 !important;
    font-weight: 600 !important;
}
[data-testid="stSidebar"] p, [data-testid="stSidebar"] span,
[data-testid="stSidebar"] div, [data-testid="stSidebar"] label,
[data-testid="stSidebar"] input { color: #374151 !important; }

/* ── Main ────────────────────────────────────────────────────────────────── */
.stApp { background: #f9fafb; }
.main .block-container { padding-top: 1.5rem !important; max-width: 100% !important; }
p, span, div, label, .stMarkdown { color: #111827; }
h1, h2, h3, h4 { color: #111827 !important; font-weight: 700 !important; letter-spacing: -0.02em; }

/* ── Metric cards ────────────────────────────────────────────────────────── */
.kpi {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 14px;
    padding: 22px 20px;
    display: flex;
    align-items: center;
    gap: 16px;
    box-shadow: 0 1px 3px rgba(0,0,0,.04);
}
.kpi-icon {
    width: 48px; height: 48px; border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    font-size: 22px; flex-shrink: 0;
}
.kpi-num   { font-size: 28px; font-weight: 700; line-height: 1; margin: 0; }
.kpi-label { font-size: 12px; color: #6b7280; margin: 4px 0 0; }

/* ── Board section column ────────────────────────────────────────────────── */
.board-col-bg {
    background: #f3f4f6;
    border-radius: 12px;
    padding: 12px 10px;
    min-height: 120px;
}
.sec-hdr {
    font-size: 11px; font-weight: 700; letter-spacing: 0.08em;
    text-transform: uppercase; color: #6b7280;
    padding: 2px 0 10px; margin-bottom: 4px;
    border-bottom: none;
}
.sec-count {
    background: #e5e7eb; color: #374151; border-radius: 20px;
    padding: 1px 8px; font-size: 10px; margin-left: 6px;
}

/* ── Task card ───────────────────────────────────────────────────────────── */
.tc {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 10px;
    padding: 12px 14px 8px;
    margin-bottom: 8px;
    box-shadow: 0 1px 3px rgba(0,0,0,.05);
    transition: box-shadow .15s, border-color .15s;
}
.tc:hover { box-shadow: 0 4px 12px rgba(0,0,0,.09); border-color: #d1d5db; }
.tc-title  { font-size: 13.5px; font-weight: 500; color: #111827; margin: 0 0 6px; line-height: 1.4; }
.tc-done   { font-size: 13.5px; font-weight: 500; color: #9ca3af; text-decoration: line-through; margin: 0 0 6px; }
.tc-meta   { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; margin-top: 6px; }
.tc-meta span { font-size: 11.5px; color: #6b7280; }

/* Priority left-border utility */
.pri-h { border-left: 3px solid #ef4444 !important; }
.pri-m { border-left: 3px solid #f59e0b !important; }
.pri-l { border-left: 3px solid #22c55e !important; }

/* ── Tag chip ────────────────────────────────────────────────────────────── */
.chip {
    display: inline-block; background: #f3f4f6; color: #4b5563;
    border-radius: 20px; padding: 1px 9px; font-size: 11px; margin-right: 3px;
}

/* ── Status badges ───────────────────────────────────────────────────────── */
.b-on  { background:#dcfce7; color:#15803d; border-radius:6px; padding:3px 10px; font-size:12px; font-weight:600; display:inline-block; }
.b-risk{ background:#ffedd5; color:#c2410c; border-radius:6px; padding:3px 10px; font-size:12px; font-weight:600; display:inline-block; }
.b-off { background:#fee2e2; color:#b91c1c; border-radius:6px; padding:3px 10px; font-size:12px; font-weight:600; display:inline-block; }

/* ── Activity feed ───────────────────────────────────────────────────────── */
.act  { padding: 12px 0; border-bottom: 1px solid #f3f4f6; display: flex; gap: 12px; align-items: flex-start; }
.act-dot { width: 8px; height: 8px; border-radius: 50%; background: #f06a6a; flex-shrink: 0; margin-top: 5px; }

/* ── Sidebar brand / labels ──────────────────────────────────────────────── */
.s-brand { font-size: 17px; font-weight: 700; color: #111827; padding: 10px 0 6px; letter-spacing: -0.02em; }
.s-logo  { color: #f06a6a; }
.s-sec   { font-size: 10px; font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase; color: #9ca3af; padding: 12px 0 4px; }

/* ── Overdue banner ──────────────────────────────────────────────────────── */
.overdue-banner {
    background: #fef2f2; border: 1px solid #fecaca; border-radius: 10px;
    padding: 12px 16px; margin-bottom: 16px; color: #b91c1c; font-size: 13.5px; font-weight: 500;
}

/* ── Project header card ─────────────────────────────────────────────────── */
.proj-header {
    background: #ffffff; border: 1px solid #e5e7eb; border-radius: 14px;
    padding: 20px 24px; margin-bottom: 16px;
    box-shadow: 0 1px 3px rgba(0,0,0,.04);
}

/* ── Empty state ─────────────────────────────────────────────────────────── */
.empty-col {
    text-align: center; padding: 24px 8px; color: #9ca3af; font-size: 13px;
}

/* Streamlit form inputs */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    border-radius: 8px !important;
    border-color: #e5e7eb !important;
    font-size: 14px !important;
}
.stSelectbox > div > div { border-radius: 8px !important; }
div[data-testid="stExpander"] { border-radius: 10px !important; border-color: #e5e7eb !important; }

/* Scrollbar */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-thumb { background: #d1d5db; border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

# ── Constants ─────────────────────────────────────────────────────────────────
DATA_FILE = "data/projects.json"
DEFAULT_SECTIONS = ["To Do", "In Progress", "Review", "Done"]
PRIORITIES = ["high", "medium", "low"]
PRI_COLOR  = {"high": "#ef4444", "medium": "#f59e0b", "low": "#22c55e"}
PRI_CSS    = {"high": "pri-h",   "medium": "pri-m",   "low":  "pri-l"}
PROJECT_COLORS = ["#6366f1","#8b5cf6","#ec4899","#f59e0b","#10b981","#3b82f6","#ef4444","#06b6d4"]
AVATAR_COLORS  = ["#4f46e5","#0891b2","#dc2626","#7c3aed","#d97706","#059669","#db2777","#6b7280"]
STATUS_INFO = {
    "on_track":  {"label": "On Track",  "css": "b-on"},
    "at_risk":   {"label": "At Risk",   "css": "b-risk"},
    "off_track": {"label": "Off Track", "css": "b-off"},
}
KPI_ICONS = {
    "total":    ("📋", "#eff6ff", "#3b82f6"),
    "overdue":  ("⚠️", "#fff1f2", "#ef4444"),
    "progress": ("🔄", "#fffbeb", "#f59e0b"),
    "done":     ("✅", "#f0fdf4", "#22c55e"),
}

# ── Data layer ────────────────────────────────────────────────────────────────
def _load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"projects": {}, "members": ["Alice", "Bob", "Charlie", "Diana"], "activity": []}

def save():
    os.makedirs("data", exist_ok=True)
    d = st.session_state.data
    if len(d.get("activity", [])) > 120:
        d["activity"] = d["activity"][-120:]
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(d, f, indent=2, ensure_ascii=False, default=str)

def gen_id():
    return str(uuid.uuid4())[:8]

def log_activity(action, detail=""):
    st.session_state.data.setdefault("activity", []).append(
        {"action": action, "detail": detail, "at": str(datetime.now())})

def _sample_data():
    d = st.session_state.data
    today = date.today()

    def mk(title, desc, assignee, days, priority, section, tags,
           done=False, subtasks=None, cmts=None):
        tid = gen_id()
        return tid, {
            "id": tid, "title": title, "description": desc, "assignee": assignee,
            "due_date": str(today + timedelta(days=days)) if days is not None else None,
            "priority": priority, "section": section, "tags": tags,
            "subtasks": subtasks or [], "comments": cmts or [],
            "completed": done, "created_at": str(datetime.now()),
        }

    p1 = gen_id()
    t1 = mk("Create wireframes", "Homepage, dashboard, and settings pages",
             "Alice", 3, "high", "In Progress", ["design","UX"],
             subtasks=[
                 {"id": gen_id(), "title": "Homepage",  "completed": True},
                 {"id": gen_id(), "title": "Dashboard", "completed": False},
                 {"id": gen_id(), "title": "Settings",  "completed": False},
             ],
             cmts=[{"author": "Bob", "text": "Homepage looks great! Let's push the dashboard next.",
                    "created_at": str(datetime.now())}])
    t2 = mk("Set up CI/CD pipeline", "GitHub Actions + Docker", "Charlie",  7, "medium", "To Do",     ["devops"])
    t3 = mk("Write API docs",        "All REST endpoints",       "Diana",   -1, "high",   "Review",    ["docs"])
    t4 = mk("Logo redesign",         "SVG + PNG brand assets",   "Alice",   -5, "low",    "Done",      ["design"], done=True)
    d["projects"][p1] = {
        "id": p1, "name": "Website Redesign",
        "description": "Complete overhaul with new branding and UX",
        "color": "#6366f1", "status": "on_track", "sections": DEFAULT_SECTIONS[:],
        "tasks": {t[0]: t[1] for t in [t1, t2, t3, t4]},
        "created_at": str(datetime.now()),
    }

    p2 = gen_id()
    t5 = mk("Draft email newsletter",  "Q3 product launch copy",       "Bob",     5, "medium", "To Do",       ["marketing","email"])
    t6 = mk("Schedule social posts",   "30-day content calendar",      "Diana",   2, "high",   "In Progress", ["social"])
    t7 = mk("Influencer outreach",     "Micro-influencer list + DMs",  "Charlie", 10, "low",   "To Do",       ["marketing"])
    d["projects"][p2] = {
        "id": p2, "name": "Q3 Marketing Campaign",
        "description": "Social and email campaign for Q3 launch",
        "color": "#ec4899", "status": "at_risk", "sections": DEFAULT_SECTIONS[:],
        "tasks": {t[0]: t[1] for t in [t5, t6, t7]},
        "created_at": str(datetime.now()),
    }

    p3 = gen_id()
    t8 = mk("Migrate DB to PostgreSQL", "SQLite → PG + ORM update", "Charlie", 14, "high",   "To Do", ["backend","db"])
    t9 = mk("Load testing",             "k6 @ 10k req/s",           "Bob",      8, "medium", "To Do", ["devops","testing"])
    d["projects"][p3] = {
        "id": p3, "name": "Infrastructure Upgrade",
        "description": "Database migration and performance hardening",
        "color": "#10b981", "status": "on_track", "sections": DEFAULT_SECTIONS[:],
        "tasks": {t[0]: t[1] for t in [t8, t9]},
        "created_at": str(datetime.now()),
    }

    d["activity"] = [
        {"action": "Project created", "detail": "Website Redesign",       "at": str(datetime.now())},
        {"action": "Task completed",  "detail": "Logo redesign",           "at": str(datetime.now())},
        {"action": "Comment added",   "detail": 'Bob on "Create wireframes"', "at": str(datetime.now())},
    ]
    save()

# ── Session state ─────────────────────────────────────────────────────────────
if "data" not in st.session_state:
    st.session_state.data = _load_data()
    if not st.session_state.data["projects"]:
        _sample_data()

_DEFAULTS = {
    "view": "dashboard", "active_project": None, "active_task": None,
    "project_view": "board", "show_task": False, "show_new_task": False,
    "new_task_sec": None, "inline_sec": None, "show_del_proj": None,
    "search_query": "", "cal_year": date.today().year, "cal_month": date.today().month,
}
for k, v in _DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Helpers ───────────────────────────────────────────────────────────────────
def proj(pid=None):
    return st.session_state.data["projects"].get(pid or st.session_state.active_project)

def all_tasks():
    out = []
    for pid, p in st.session_state.data["projects"].items():
        for t in p["tasks"].values():
            out.append({**t, "project_id": pid, "project_name": p["name"], "project_color": p["color"]})
    return out

def due_status(ds):
    if not ds:
        return None
    try:
        d = date.fromisoformat(str(ds)[:10]); today = date.today()
        if d < today: return "overdue"
        if d <= today + timedelta(days=2): return "due-soon"
        return "ok"
    except Exception:
        return None

def rel_date(ds):
    if not ds: return "—", None
    try:
        d = date.fromisoformat(str(ds)[:10]); diff = (d - date.today()).days
        if diff < -1:  return f"Overdue {-diff}d", "overdue"
        if diff == -1: return "Yesterday",          "overdue"
        if diff == 0:  return "Today",              "due-soon"
        if diff == 1:  return "Tomorrow",           "due-soon"
        if diff <= 7:  return f"In {diff}d",        "ok"
        return d.strftime("%b %d"),                 "ok"
    except Exception:
        return str(ds), None

def avatar_html(name, size=26):
    if not name:
        return (f'<div style="width:{size}px;height:{size}px;border-radius:50%;'
                f'background:#e5e7eb;display:inline-flex;align-items:center;'
                f'justify-content:center;font-size:{int(size/2.8)}px;color:#9ca3af">?</div>')
    initials = "".join(w[0].upper() for w in str(name).split()[:2])
    color = AVATAR_COLORS[hash(name) % len(AVATAR_COLORS)]
    return (f'<div style="width:{size}px;height:{size}px;border-radius:50%;background:{color};'
            f'display:inline-flex;align-items:center;justify-content:center;'
            f'font-size:{int(size/2.8)}px;color:white;font-weight:600;flex-shrink:0">{initials}</div>')

def date_badge_html(ds):
    txt, status = rel_date(ds)
    if txt == "—": return ""
    color = "#dc2626" if status == "overdue" else ("#d97706" if status == "due-soon" else "#6b7280")
    return f'<span style="color:{color};font-size:12px">📅 {txt}</span>'

def nav(view=None, project=None, task=None, show_task=False):
    if view is not None:    st.session_state.view = view
    if project is not None: st.session_state.active_project = project
    if task is not None:    st.session_state.active_task = task
    st.session_state.show_task = show_task
    st.session_state.show_new_task = False
    st.session_state.inline_sec = None
    st.rerun()

# ── Sidebar ───────────────────────────────────────────────────────────────────
def sidebar():
    with st.sidebar:
        st.markdown('<div class="s-brand"><span class="s-logo">✓</span> TaskFlow</div>',
                    unsafe_allow_html=True)
        q = st.text_input("search", value=st.session_state.search_query,
                          label_visibility="collapsed", placeholder="🔍  Search…",
                          key="search_input")
        if q != st.session_state.search_query:
            st.session_state.search_query = q
            st.session_state.view = "search" if q else "dashboard"
            st.rerun()
        st.markdown("")

        v = st.session_state.view
        if st.button("🏠  Home",    use_container_width=True, type="primary" if v=="dashboard" else "secondary"): nav("dashboard")
        if st.button("📥  Inbox",   use_container_width=True, type="primary" if v=="inbox"     else "secondary"): nav("inbox")
        if st.button("✓  My Tasks", use_container_width=True, type="primary" if v=="my_tasks"  else "secondary"): nav("my_tasks")

        st.markdown('<div class="s-sec">Projects</div>', unsafe_allow_html=True)

        for pid, p in st.session_state.data["projects"].items():
            active = (st.session_state.active_project == pid and v == "project")
            n_open = sum(1 for t in p["tasks"].values() if not t["completed"])
            # FIX: use columns so colored dot renders correctly
            dot_col, btn_col = st.columns([0.1, 0.9])
            dot_col.markdown(
                f'<div style="width:8px;height:8px;border-radius:50%;background:{p["color"]};'
                f'margin-top:11px;margin-left:2px"></div>',
                unsafe_allow_html=True)
            if btn_col.button(f'{p["name"]}  ({n_open})', key=f"sb_{pid}",
                              use_container_width=True,
                              type="primary" if active else "secondary"):
                nav("project", project=pid)

        st.markdown("")
        if st.button("＋  New Project", use_container_width=True):
            st.session_state.view = "new_project"; st.rerun()

        st.markdown("---")
        st.markdown('<div class="s-sec">Team</div>', unsafe_allow_html=True)
        for m in st.session_state.data["members"]:
            st.markdown(
                f'<div style="display:flex;align-items:center;gap:9px;padding:4px 2px">'
                f'{avatar_html(m, 24)}'
                f'<span style="font-size:13px;color:#374151">{m}</span></div>',
                unsafe_allow_html=True)

sidebar()

# ── Task detail ───────────────────────────────────────────────────────────────
if st.session_state.show_task and st.session_state.active_task and st.session_state.active_project:
    pid  = st.session_state.active_project
    tid  = st.session_state.active_task
    p    = proj(pid)
    if not p or tid not in p["tasks"]:
        st.session_state.show_task = False; st.rerun()

    task = p["tasks"][tid]
    si   = STATUS_INFO.get(p.get("status","on_track"), STATUS_INFO["on_track"])
    pc   = PRI_COLOR.get(task.get("priority","medium"), "#f59e0b")

    back_col, _ = st.columns([1, 6])
    if back_col.button("← Back"):
        st.session_state.show_task = False; st.session_state.active_task = None; st.rerun()

    st.markdown(
        f'<div style="display:flex;align-items:center;gap:10px;margin-bottom:6px">'
        f'<div style="width:4px;height:28px;background:{pc};border-radius:2px;flex-shrink:0"></div>'
        f'<h2 style="margin:0;font-size:22px">{task["title"]}</h2></div>',
        unsafe_allow_html=True)
    st.markdown(
        f'<div style="display:flex;align-items:center;gap:10px;margin-bottom:16px">'
        f'<span style="color:#6b7280;font-size:13px">Project: <strong>{p["name"]}</strong></span>'
        f'<span class="{si["css"]}">{si["label"]}</span></div>',
        unsafe_allow_html=True)
    st.divider()

    left, right = st.columns([3, 2])

    with left:
        # Subtasks
        subtasks = task.get("subtasks", [])
        if subtasks:
            done_count = sum(1 for s in subtasks if s["completed"])
            st.markdown(
                f'<div style="font-weight:600;font-size:14px;margin-bottom:8px">'
                f'Subtasks <span style="color:#6b7280;font-weight:400">{done_count}/{len(subtasks)}</span></div>',
                unsafe_allow_html=True)
            st.progress(done_count / len(subtasks))
            for i, sub in enumerate(subtasks):
                c1, c2 = st.columns([1, 10])
                chk = c1.checkbox("", value=sub["completed"], key=f"sub_{tid}_{i}")
                if chk != sub["completed"]:
                    task["subtasks"][i]["completed"] = chk; save(); st.rerun()
                sty = "text-decoration:line-through;color:#9ca3af" if sub["completed"] else "color:#111827"
                c2.markdown(f'<span style="{sty};font-size:13.5px">{sub["title"]}</span>',
                            unsafe_allow_html=True)
            st.markdown("")

        with st.form("task_edit"):
            new_title = st.text_input("Title", value=task["title"])
            new_desc  = st.text_area("Description", value=task.get("description",""), height=90)
            new_sub   = st.text_input("＋ Add subtask", placeholder="Subtask title…")
            st.markdown("**Add comment**")
            new_comment    = st.text_area("", height=70, label_visibility="collapsed",
                                          placeholder="Write a comment…")
            comment_author = st.selectbox("Post as", st.session_state.data["members"])
            cs, cc = st.columns(2)
            saved   = cs.form_submit_button("Save Changes", type="primary", use_container_width=True)
            go_back = cc.form_submit_button("Close",                        use_container_width=True)

            if saved:
                task["title"]       = new_title.strip() or task["title"]
                task["description"] = new_desc.strip()
                if new_sub.strip():
                    task["subtasks"].append({"id": gen_id(), "title": new_sub.strip(), "completed": False})
                if new_comment.strip():
                    task["comments"].append({"author": comment_author, "text": new_comment.strip(),
                                             "created_at": str(datetime.now())})
                    log_activity("Comment added", f'{comment_author} on "{task["title"]}"')
                log_activity("Task updated", task["title"]); save(); st.rerun()
            if go_back:
                st.session_state.show_task = False; st.session_state.active_task = None; st.rerun()

        if task.get("comments"):
            st.markdown("**Comments**")
            for c in task["comments"]:
                st.markdown(
                    f'<div style="display:flex;gap:10px;margin-bottom:14px;align-items:flex-start">'
                    f'{avatar_html(c["author"],30)}'
                    f'<div style="flex:1">'
                    f'<div style="font-weight:600;font-size:13px;margin-bottom:2px">{c["author"]}'
                    f'<span style="color:#9ca3af;font-weight:400;font-size:11px;margin-left:8px">'
                    f'{c.get("created_at","")[:16]}</span></div>'
                    f'<div style="font-size:13.5px;color:#374151">{c["text"]}</div>'
                    f'</div></div>',
                    unsafe_allow_html=True)

    with right:
        st.markdown('<div style="font-weight:600;font-size:14px;margin-bottom:12px">Details</div>',
                    unsafe_allow_html=True)

        members_opts = ["(unassigned)"] + st.session_state.data["members"]
        cur_a = task.get("assignee") or "(unassigned)"
        new_a = st.selectbox("Assignee", members_opts,
                              index=members_opts.index(cur_a) if cur_a in members_opts else 0)
        if new_a != cur_a:
            task["assignee"] = None if new_a == "(unassigned)" else new_a
            log_activity("Task reassigned", f'"{task["title"]}" → {new_a}'); save(); st.rerun()

        new_pr = st.selectbox("Priority", PRIORITIES,
                               index=PRIORITIES.index(task.get("priority","medium")))
        if new_pr != task.get("priority"):
            task["priority"] = new_pr; save(); st.rerun()

        secs = p["sections"]; cur_sec = task.get("section", secs[0])
        new_sec = st.selectbox("Section", secs,
                                index=secs.index(cur_sec) if cur_sec in secs else 0)
        if new_sec != cur_sec:
            task["section"] = new_sec; task["completed"] = (new_sec == "Done")
            log_activity("Task moved", f'"{task["title"]}" → {new_sec}'); save(); st.rerun()

        cur_due = None
        if task.get("due_date"):
            try: cur_due = date.fromisoformat(str(task["due_date"])[:10])
            except Exception: pass
        new_due = st.date_input("Due date", value=cur_due)
        if new_due and str(new_due) != str(task.get("due_date",""))[:10]:
            task["due_date"] = str(new_due); save(); st.rerun()

        tags_raw = st.text_input("Tags (comma-separated)", value=", ".join(task.get("tags",[])))
        new_tags = [x.strip() for x in tags_raw.split(",") if x.strip()]
        if new_tags != task.get("tags",[]): task["tags"] = new_tags; save()

        done_toggle = st.checkbox("Mark as completed", value=task.get("completed", False))
        if done_toggle != task.get("completed", False):
            task["completed"] = done_toggle
            if done_toggle: task["section"] = "Done"
            log_activity("Task completed", task["title"]); save(); st.rerun()

        st.divider()
        if st.button("🗑️  Delete Task", use_container_width=True):
            log_activity("Task deleted", task["title"]); del p["tasks"][tid]; save()
            st.session_state.show_task = False; st.session_state.active_task = None; st.rerun()

    st.stop()

# ── New project form ──────────────────────────────────────────────────────────
if st.session_state.view == "new_project":
    st.markdown("## New Project")
    with st.form("new_proj"):
        name  = st.text_input("Project name *", placeholder="e.g. Mobile App Redesign")
        desc  = st.text_area("Description", height=70)
        r1, r2 = st.columns(2)
        color  = r1.selectbox("Color", PROJECT_COLORS)
        status = r2.selectbox("Status", list(STATUS_INFO.keys()),
                               format_func=lambda k: STATUS_INFO[k]["label"])
        c1, c2 = st.columns(2)
        ok     = c1.form_submit_button("Create Project", type="primary", use_container_width=True)
        cancel = c2.form_submit_button("Cancel",                         use_container_width=True)
        if ok and name.strip():
            pid = gen_id()
            st.session_state.data["projects"][pid] = {
                "id": pid, "name": name.strip(), "description": desc.strip(),
                "color": color, "status": status, "sections": DEFAULT_SECTIONS[:],
                "tasks": {}, "created_at": str(datetime.now()),
            }
            log_activity("Project created", name.strip()); save(); nav("project", project=pid)
        if cancel: nav("dashboard")
    st.stop()

# ── New task modal ────────────────────────────────────────────────────────────
def new_task_modal(pid):
    p = proj(pid)
    st.markdown(
        '<div style="background:#f0fdf4;border:1px solid #bbf7d0;border-radius:10px;'
        'padding:16px 20px;margin-bottom:16px"><strong style="font-size:15px">＋ New Task</strong></div>',
        unsafe_allow_html=True)
    with st.form("new_task_form"):
        title = st.text_input("Task title *", placeholder="What needs to be done?")
        desc  = st.text_area("Description (optional)", height=60, label_visibility="collapsed",
                              placeholder="Description (optional)")
        r1, r2 = st.columns(2)
        assignee = r1.selectbox("Assignee", ["(none)"] + st.session_state.data["members"])
        priority = r2.selectbox("Priority", PRIORITIES, index=1)
        r3, r4 = st.columns(2)
        default_sec = st.session_state.new_task_sec or p["sections"][0]
        idx  = p["sections"].index(default_sec) if default_sec in p["sections"] else 0
        section  = r3.selectbox("Section", p["sections"], index=idx)
        due_date = r4.date_input("Due date", value=None)
        tags_raw = st.text_input("Tags", placeholder="design, ux, frontend…")
        cs, cc = st.columns(2)
        ok     = cs.form_submit_button("Create Task", type="primary", use_container_width=True)
        cancel = cc.form_submit_button("Cancel",                      use_container_width=True)
        if ok and title.strip():
            tid = gen_id()
            p["tasks"][tid] = {
                "id": tid, "title": title.strip(), "description": desc.strip(),
                "assignee": None if assignee == "(none)" else assignee,
                "due_date": str(due_date) if due_date else None,
                "priority": priority, "section": section,
                "tags": [x.strip() for x in tags_raw.split(",") if x.strip()],
                "subtasks": [], "comments": [], "completed": False,
                "created_at": str(datetime.now()),
            }
            log_activity("Task created", title.strip()); save()
            st.session_state.show_new_task = False; st.session_state.new_task_sec = None; st.rerun()
        if cancel:
            st.session_state.show_new_task = False; st.session_state.new_task_sec = None; st.rerun()

# ── Board view ────────────────────────────────────────────────────────────────
def board_view(pid):
    p = proj(pid); secs = p["sections"]; tasks = p["tasks"]

    with st.expander("⚙️  Manage sections"):
        ec1, ec2, ec3 = st.columns([3, 1, 3])
        new_sec_name = ec1.text_input("Name", placeholder="New section name…",
                                       key="new_sec_input", label_visibility="collapsed")
        if ec2.button("Add", key="add_sec_btn") and new_sec_name.strip():
            if new_sec_name.strip() not in secs:
                p["sections"].append(new_sec_name.strip()); save(); st.rerun()
        removable = [s for s in secs if s not in DEFAULT_SECTIONS]
        if removable:
            sec_del = ec3.selectbox("Remove", ["—"] + removable,
                                     key="del_sec_sel", label_visibility="collapsed")
            if sec_del != "—" and st.button("Remove", key="del_sec_btn"):
                for t in tasks.values():
                    if t["section"] == sec_del: t["section"] = secs[0]
                p["sections"].remove(sec_del); save(); st.rerun()

    cols = st.columns(len(secs))
    for i, sec in enumerate(secs):
        sec_tasks = [t for t in tasks.values() if t["section"] == sec]
        with cols[i]:
            # Column header
            st.markdown(
                f'<div class="sec-hdr">{sec}'
                f'<span class="sec-count">{len(sec_tasks)}</span></div>',
                unsafe_allow_html=True)

            # Empty state
            if not sec_tasks:
                st.markdown('<div class="empty-col">No tasks yet</div>', unsafe_allow_html=True)

            for t in sec_tasks:
                subs      = t.get("subtasks", [])
                done_subs = sum(1 for s in subs if s["completed"])
                pc        = PRI_COLOR.get(t.get("priority","medium"), "#f59e0b")
                pri_css   = PRI_CSS.get(t.get("priority","medium"), "pri-m")
                done      = t.get("completed", False)
                dt, dst   = rel_date(t.get("due_date"))

                # Build meta parts as HTML
                meta_parts = []
                if t.get("assignee"):   meta_parts.append(avatar_html(t["assignee"], 20))
                if dt != "—":
                    c = "#dc2626" if dst=="overdue" else ("#d97706" if dst=="due-soon" else "#6b7280")
                    meta_parts.append(f'<span style="color:{c};font-size:12px">📅 {dt}</span>')
                if subs:
                    meta_parts.append(f'<span style="font-size:11px;color:#6b7280">☑ {done_subs}/{len(subs)}</span>')
                if t.get("comments"):
                    meta_parts.append(f'<span style="font-size:11px;color:#6b7280">💬 {len(t["comments"])}</span>')

                tag_html = "".join(f'<span class="chip">{tag}</span>' for tag in t.get("tags",[]))

                title_cls   = "tc-done" if done else "tc-title"
                tag_section = f'<div style="margin-bottom:6px">{tag_html}</div>' if tag_html else ""
                st.markdown(
                    f'<div class="tc {pri_css}">'
                    f'<div class="{title_cls}">{t["title"]}</div>'
                    f'{tag_section}'
                    f'<div class="tc-meta">{"".join(meta_parts)}</div>'
                    f'</div>',
                    unsafe_allow_html=True)

                # Action row
                ac1, ac2 = st.columns([3, 2])
                other = [s for s in secs if s != sec]
                if other and ac1:
                    move = ac1.selectbox("→", ["Move to…"] + other,
                                         key=f"mv_{t['id']}", label_visibility="collapsed")
                    if move != "Move to…":
                        tasks[t["id"]]["section"] = move
                        tasks[t["id"]]["completed"] = (move == "Done")
                        log_activity("Task moved", f'"{t["title"]}" → {move}'); save(); st.rerun()
                if ac2.button("Open ↗", key=f"b_{t['id']}"):
                    st.session_state.active_task = t["id"]
                    st.session_state.show_task   = True; st.rerun()

                st.markdown("<div style='height:2px'></div>", unsafe_allow_html=True)

            # Inline add
            key_inline = f"{pid}_{sec}"
            if st.session_state.inline_sec == key_inline:
                with st.form(f"inline_{sec}"):
                    it = st.text_input("", placeholder="Task name…",
                                        label_visibility="collapsed", key=f"it_{sec}")
                    ia, ic = st.columns(2)
                    ok  = ia.form_submit_button("Add",  type="primary", use_container_width=True)
                    can = ic.form_submit_button("✕",                    use_container_width=True)
                    if ok and it.strip():
                        tid = gen_id()
                        p["tasks"][tid] = {
                            "id": tid, "title": it.strip(), "description": "",
                            "assignee": None, "due_date": None, "priority": "medium",
                            "section": sec, "tags": [], "subtasks": [], "comments": [],
                            "completed": False, "created_at": str(datetime.now()),
                        }
                        log_activity("Task created", it.strip()); save()
                        st.session_state.inline_sec = None; st.rerun()
                    if can: st.session_state.inline_sec = None; st.rerun()
            else:
                if st.button("＋ Add task", key=f"add_{pid}_{sec}", use_container_width=True):
                    st.session_state.inline_sec = key_inline; st.rerun()

# ── List view ─────────────────────────────────────────────────────────────────
def list_view(pid):
    p = proj(pid); tasks = list(p["tasks"].values())
    fc1, fc2, fc3 = st.columns(3)
    f_sec = fc1.selectbox("Section",  ["All"] + p["sections"])
    f_pri = fc2.selectbox("Priority", ["All"] + PRIORITIES)
    f_ass = fc3.selectbox("Assignee", ["All"] + st.session_state.data["members"])
    if f_sec != "All": tasks = [t for t in tasks if t["section"] == f_sec]
    if f_pri != "All": tasks = [t for t in tasks if t.get("priority") == f_pri]
    if f_ass != "All": tasks = [t for t in tasks if t.get("assignee") == f_ass]

    st.markdown(f'<p style="color:#6b7280;font-size:13px;margin:0">{len(tasks)} tasks</p>',
                unsafe_allow_html=True)
    st.divider()

    heads = st.columns([4, 2, 2, 1, 2, 1])
    for col, lbl in zip(heads, ["**Title**","**Section**","**Assignee**","**Pri**","**Due**",""]):
        col.markdown(lbl)
    st.divider()

    for t in sorted(tasks, key=lambda x: x.get("due_date") or "9999"):
        c1, c2, c3, c4, c5, c6 = st.columns([4, 2, 2, 1, 2, 1])
        pc = PRI_COLOR.get(t.get("priority","medium"),"#888")
        title = f"~~{t['title']}~~" if t["completed"] else t["title"]
        c1.markdown(
            f'<span style="font-size:13.5px">'
            f'<span style="display:inline-block;width:3px;height:13px;background:{pc};'
            f'border-radius:2px;margin-right:7px;vertical-align:middle"></span>'
            f'{title}</span>',
            unsafe_allow_html=True)
        c2.write(t.get("section",""))
        if t.get("assignee"):
            c3.markdown(avatar_html(t["assignee"],22) +
                        f' <span style="font-size:13px">{t["assignee"]}</span>',
                        unsafe_allow_html=True)
        else: c3.write("—")
        c4.markdown(f'<span style="color:{pc};font-weight:700;font-size:13px">'
                    f'{t.get("priority","")[:1].upper()}</span>', unsafe_allow_html=True)
        dt, dst = rel_date(t.get("due_date"))
        if dst == "overdue":    c5.markdown(f":red[{dt}]")
        elif dst == "due-soon": c5.markdown(f":orange[{dt}]")
        else:                   c5.write(dt)
        if c6.button("↗", key=f"l_{t['id']}"):
            st.session_state.active_task = t["id"]; st.session_state.show_task = True; st.rerun()

# ── Timeline view ─────────────────────────────────────────────────────────────
def timeline_view(pid):
    p = proj(pid); today = date.today()
    start = today - timedelta(days=today.weekday())
    weeks = [start + timedelta(weeks=i) for i in range(6)]
    tasks_dated = [t for t in p["tasks"].values() if t.get("due_date")]

    html = ('<div style="overflow-x:auto">'
            '<table style="width:100%;border-collapse:collapse;font-size:13px">'
            '<thead><tr>'
            '<th style="text-align:left;padding:10px 14px;color:#374151;font-weight:600;'
            'border-bottom:2px solid #e5e7eb;min-width:200px">Task</th>'
            '<th style="padding:10px 8px;border-bottom:2px solid #e5e7eb;width:36px"></th>')
    for w in weeks:
        is_cur = w <= today < w + timedelta(weeks=1)
        bg = "background:#fef2f2;" if is_cur else ""
        html += (f'<th style="{bg}text-align:center;padding:8px 4px;color:#6b7280;'
                 f'font-size:11px;font-weight:600;border-bottom:2px solid #e5e7eb">'
                 f'{w.strftime("%b %d")}</th>')
    html += "</tr></thead><tbody>"

    if not tasks_dated:
        html += f'<tr><td colspan="{len(weeks)+2}" style="text-align:center;padding:24px;color:#9ca3af;font-style:italic">No tasks with due dates</td></tr>'

    for t in sorted(tasks_dated, key=lambda x: x.get("due_date","")):
        due = date.fromisoformat(t["due_date"][:10])
        try:    t_start = datetime.fromisoformat(t["created_at"][:10]).date()
        except: t_start = due - timedelta(days=7)
        color = ("#d1d5db" if t.get("completed") else
                 "#ef4444" if due < today else
                 "#f59e0b" if due <= today + timedelta(days=3) else "#6366f1")
        sty   = "text-decoration:line-through;color:#9ca3af" if t.get("completed") else "color:#111827"
        ava   = avatar_html(t.get("assignee"),22) if t.get("assignee") else ""
        title = t["title"][:30] + ("…" if len(t["title"]) > 30 else "")
        html += (f'<tr style="border-bottom:1px solid #f3f4f6">'
                 f'<td style="padding:8px 14px;overflow:hidden;white-space:nowrap">'
                 f'<span style="{sty}">{title}</span></td>'
                 f'<td style="padding:8px 4px">{ava}</td>')
        for w in weeks:
            w_end   = w + timedelta(weeks=1)
            in_range = t_start < w_end and due >= w
            cell_bg  = "background:#fef2f2;" if (w <= today < w_end) else ""
            if in_range:
                bar_s = max(t_start, w); bar_e = min(due, w_end - timedelta(days=1))
                left  = (bar_s - w).days / 7 * 100
                width = max(6, ((bar_e - bar_s).days + 1) / 7 * 100)
                lbl   = (f'<span style="position:absolute;right:4px;top:2px;font-size:10px;'
                         f'color:white;font-weight:700">{due.strftime("%d")}</span>'
                         if w <= due < w_end else "")
                html += (f'<td style="padding:4px 2px;{cell_bg}">'
                         f'<div style="position:relative;height:24px">'
                         f'<div style="position:absolute;left:{left:.0f}%;width:{width:.0f}%;'
                         f'height:20px;background:{color};border-radius:5px;top:2px;opacity:.9">'
                         f'{lbl}</div></div></td>')
            else:
                html += f'<td style="padding:4px 2px;{cell_bg}"></td>'
        html += "</tr>"
    html += "</tbody></table></div>"
    html += """<div style="margin-top:14px;display:flex;gap:20px;font-size:12px;color:#6b7280">
      <span><span style="display:inline-block;width:12px;height:12px;background:#6366f1;border-radius:3px;margin-right:4px"></span>Upcoming</span>
      <span><span style="display:inline-block;width:12px;height:12px;background:#f59e0b;border-radius:3px;margin-right:4px"></span>Due soon</span>
      <span><span style="display:inline-block;width:12px;height:12px;background:#ef4444;border-radius:3px;margin-right:4px"></span>Overdue</span>
      <span><span style="display:inline-block;width:12px;height:12px;background:#d1d5db;border-radius:3px;margin-right:4px"></span>Completed</span>
    </div>"""
    st.markdown(html, unsafe_allow_html=True)

# ── Calendar view ─────────────────────────────────────────────────────────────
def calendar_view(pid):
    p = proj(pid); today = date.today()
    nc1, nc2, nc3 = st.columns([1, 3, 1])
    if nc1.button("← Prev"):
        if st.session_state.cal_month == 1: st.session_state.cal_month=12; st.session_state.cal_year-=1
        else: st.session_state.cal_month-=1
        st.rerun()
    nc2.markdown(
        f'<h3 style="text-align:center;margin:0;font-size:18px">'
        f'{date(st.session_state.cal_year,st.session_state.cal_month,1).strftime("%B %Y")}</h3>',
        unsafe_allow_html=True)
    if nc3.button("Next →"):
        if st.session_state.cal_month == 12: st.session_state.cal_month=1; st.session_state.cal_year+=1
        else: st.session_state.cal_month+=1
        st.rerun()

    tasks_by_day = {}
    for t in p["tasks"].values():
        if t.get("due_date"):
            try:
                d = date.fromisoformat(t["due_date"][:10])
                if d.year == st.session_state.cal_year and d.month == st.session_state.cal_month:
                    tasks_by_day.setdefault(d.day, []).append(t)
            except Exception: pass

    month_grid = cal_lib.monthcalendar(st.session_state.cal_year, st.session_state.cal_month)
    html = '<table style="width:100%;border-collapse:collapse;margin-top:16px">'
    html += '<tr>' + "".join(
        f'<th style="text-align:center;padding:10px 4px;color:#6b7280;font-size:12px;'
        f'font-weight:600;border-bottom:2px solid #e5e7eb">{d}</th>'
        for d in ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]) + '</tr>'
    for week in month_grid:
        html += '<tr>'
        for day in week:
            if day == 0:
                html += '<td style="border:1px solid #f3f4f6;min-height:90px;background:#fafafa;vertical-align:top;padding:4px"></td>'
            else:
                is_today = (day == today.day and st.session_state.cal_month == today.month
                            and st.session_state.cal_year == today.year)
                day_bg  = "#fef2f2" if is_today else "#fff"
                num_sty = ("font-size:13px;font-weight:700;color:#dc2626" if is_today
                           else "font-size:12px;color:#6b7280")
                chips = ""
                for t in tasks_by_day.get(day, []):
                    bg_c  = "#d1d5db" if t.get("completed") else (
                            "#ef4444" if str(t.get("due_date","")) < str(today) else "#6366f1")
                    label = (t["title"][:14]+"…") if len(t["title"])>14 else t["title"]
                    chips += (f'<div style="background:{bg_c};color:white;border-radius:4px;'
                              f'padding:2px 6px;font-size:11px;margin-top:3px;overflow:hidden;'
                              f'white-space:nowrap">{label}</div>')
                html += (f'<td style="border:1px solid #e5e7eb;min-height:90px;padding:6px;'
                         f'vertical-align:top;background:{day_bg}">'
                         f'<span style="{num_sty}">{day}</span>{chips}</td>')
        html += '</tr>'
    html += '</table>'
    st.markdown(html, unsafe_allow_html=True)

# ── Project view ──────────────────────────────────────────────────────────────
def project_view(pid):
    p = proj(pid)
    if not p: st.error("Project not found."); return

    si     = STATUS_INFO.get(p.get("status","on_track"), STATUS_INFO["on_track"])
    tasks  = list(p["tasks"].values())
    n_done = sum(1 for t in tasks if t["completed"])
    pct    = n_done / len(tasks) if tasks else 0

    # Overdue banner
    n_overdue = sum(1 for t in tasks if not t["completed"] and due_status(t.get("due_date")) == "overdue")
    if n_overdue:
        st.markdown(
            f'<div class="overdue-banner">⚠️ {n_overdue} task{"s" if n_overdue>1 else ""} '
            f'overdue in this project</div>',
            unsafe_allow_html=True)

    hc1, hc2 = st.columns([4, 4])
    with hc1:
        st.markdown(
            f'<div style="display:flex;align-items:center;gap:10px;margin-bottom:4px">'
            f'<div style="width:12px;height:12px;border-radius:3px;background:{p["color"]};flex-shrink:0"></div>'
            f'<h2 style="margin:0;font-size:22px">{p["name"]}</h2>'
            f'<span class="{si["css"]}">{si["label"]}</span></div>'
            f'<p style="color:#6b7280;font-size:13.5px;margin:0 0 8px 22px">{p.get("description","")}</p>',
            unsafe_allow_html=True)
        st.progress(pct, text=f"{n_done} / {len(tasks)} tasks completed")
    with hc2:
        pv = st.session_state.project_view
        b1,b2,b3,b4,b5,b6 = st.columns(6)
        if b1.button("Board",    use_container_width=True, type="primary" if pv=="board"    else "secondary"): st.session_state.project_view="board";    st.rerun()
        if b2.button("List",     use_container_width=True, type="primary" if pv=="list"     else "secondary"): st.session_state.project_view="list";     st.rerun()
        if b3.button("Timeline", use_container_width=True, type="primary" if pv=="timeline" else "secondary"): st.session_state.project_view="timeline"; st.rerun()
        if b4.button("Calendar", use_container_width=True, type="primary" if pv=="calendar" else "secondary"): st.session_state.project_view="calendar"; st.rerun()
        if b5.button("＋ Task",  use_container_width=True, type="primary"):
            st.session_state.show_new_task = True; st.rerun()
        if b6.button("🗑️",      use_container_width=True):
            st.session_state.show_del_proj = pid; st.rerun()

    if st.session_state.show_del_proj == pid:
        st.warning(f'Delete **{p["name"]}**? All tasks will be permanently removed.')
        dc1, dc2 = st.columns(2)
        if dc1.button("Yes, delete", type="primary", use_container_width=True):
            log_activity("Project deleted", p["name"])
            del st.session_state.data["projects"][pid]; save()
            st.session_state.show_del_proj = None; nav("dashboard")
        if dc2.button("Cancel", use_container_width=True):
            st.session_state.show_del_proj = None; st.rerun()
        st.stop()

    with st.expander("📊  Update project status"):
        cur_s = p.get("status","on_track")
        new_s = st.selectbox("Status", list(STATUS_INFO.keys()),
                              index=list(STATUS_INFO.keys()).index(cur_s),
                              format_func=lambda k: STATUS_INFO[k]["label"])
        if st.button("Update status", key="upd_status"):
            p["status"] = new_s
            log_activity("Project status updated", f'{p["name"]} → {STATUS_INFO[new_s]["label"]}')
            save(); st.rerun()

    st.divider()
    if st.session_state.show_new_task: new_task_modal(pid); return

    pv = st.session_state.project_view
    if pv == "board":      board_view(pid)
    elif pv == "list":     list_view(pid)
    elif pv == "timeline": timeline_view(pid)
    elif pv == "calendar": calendar_view(pid)

# ── Dashboard ─────────────────────────────────────────────────────────────────
def dashboard():
    st.markdown("# Home")
    tasks   = all_tasks()
    total   = len(tasks)
    overdue = sum(1 for t in tasks if not t["completed"] and due_status(t.get("due_date")) == "overdue")
    in_prog = sum(1 for t in tasks if t.get("section") == "In Progress" and not t["completed"])
    done    = sum(1 for t in tasks if t["completed"])

    c1, c2, c3, c4 = st.columns(4)
    for col, key, num, label in [
        (c1,"total",   total,   "Total Tasks"),
        (c2,"overdue", overdue, "Overdue"),
        (c3,"progress",in_prog, "In Progress"),
        (c4,"done",    done,    "Completed"),
    ]:
        icon, bg, color = KPI_ICONS[key]
        col.markdown(
            f'<div class="kpi">'
            f'<div class="kpi-icon" style="background:{bg}">{icon}</div>'
            f'<div><p class="kpi-num" style="color:{color}">{num}</p>'
            f'<p class="kpi-label">{label}</p></div></div>',
            unsafe_allow_html=True)

    st.markdown("")

    # Overdue warning
    if overdue:
        st.markdown(
            f'<div class="overdue-banner">⚠️ You have <strong>{overdue} overdue task{"s" if overdue>1 else ""}</strong> across all projects</div>',
            unsafe_allow_html=True)

    left, right = st.columns([3, 2])
    with left:
        st.markdown("### Upcoming Tasks")
        upcoming = sorted([t for t in tasks if not t["completed"] and t.get("due_date")],
                          key=lambda x: x.get("due_date",""))[:10]
        if not upcoming:
            st.markdown('<div style="color:#9ca3af;font-size:14px;padding:16px 0">No upcoming tasks 🎉</div>',
                        unsafe_allow_html=True)
        else:
            for t in upcoming:
                dt, dst = rel_date(t.get("due_date"))
                pc = PRI_COLOR.get(t.get("priority","medium"),"#888")
                ct, ca, cd, cbtn = st.columns([4, 2, 2, 1])
                ct.markdown(
                    f'<div style="display:flex;align-items:flex-start;gap:7px">'
                    f'<div style="width:3px;height:16px;background:{pc};border-radius:2px;'
                    f'margin-top:2px;flex-shrink:0"></div>'
                    f'<div><div style="font-weight:500;font-size:13.5px">{t["title"]}</div>'
                    f'<div style="font-size:12px;color:#9ca3af">{t["project_name"]}</div></div></div>',
                    unsafe_allow_html=True)
                if t.get("assignee"):
                    ca.markdown(avatar_html(t["assignee"],22)+
                                f' <span style="font-size:12px">{t["assignee"]}</span>',
                                unsafe_allow_html=True)
                if dst=="overdue":    cd.markdown(f":red[{dt}]")
                elif dst=="due-soon": cd.markdown(f":orange[{dt}]")
                else:                 cd.write(dt)
                if cbtn.button("↗", key=f"dash_{t['id']}"):
                    st.session_state.active_project = t["project_id"]
                    st.session_state.active_task    = t["id"]
                    st.session_state.show_task      = True; st.rerun()
                st.divider()

    with right:
        st.markdown("### Projects")
        for pid, p in st.session_state.data["projects"].items():
            all_t  = list(p["tasks"].values())
            n_d    = sum(1 for t in all_t if t["completed"])
            n_t    = len(all_t)
            si     = STATUS_INFO.get(p.get("status","on_track"), STATUS_INFO["on_track"])
            n_ov   = sum(1 for t in all_t if not t["completed"] and due_status(t.get("due_date"))=="overdue")
            ov_badge = f'<span style="color:#ef4444;font-size:11px">⚠️ {n_ov} overdue</span>' if n_ov else ""
            st.markdown(
                f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px">'
                f'<div style="display:flex;align-items:center;gap:8px">'
                f'<div style="width:10px;height:10px;border-radius:3px;background:{p["color"]}"></div>'
                f'<span style="font-weight:600;font-size:14px">{p["name"]}</span>'
                f'{ov_badge}'
                f'</div><span class="{si["css"]}">{si["label"]}</span></div>',
                unsafe_allow_html=True)
            st.progress(n_d / n_t if n_t else 0, text=f"{n_d}/{n_t} tasks")
            if st.button("Open project →", key=f"dp_{pid}"): nav("project", project=pid)
            st.markdown("")

# ── Inbox ─────────────────────────────────────────────────────────────────────
def inbox():
    st.markdown("# Inbox")
    activity = list(reversed(st.session_state.data.get("activity", [])))
    if not activity:
        st.markdown('<div style="color:#9ca3af;font-size:14px;padding:24px 0;text-align:center">'
                    'No activity yet. Start creating projects and tasks!</div>',
                    unsafe_allow_html=True)
        return
    for item in activity[:60]:
        ts = item.get("at","")[:16]
        st.markdown(
            f'<div class="act">'
            f'<div class="act-dot"></div>'
            f'<div style="flex:1">'
            f'<span style="font-weight:600;font-size:13.5px">{item.get("action","")}</span>'
            f' <span style="color:#6b7280;font-size:13px">— {item.get("detail","")}</span>'
            f'</div>'
            f'<span style="color:#9ca3af;font-size:12px;white-space:nowrap">{ts}</span>'
            f'</div>',
            unsafe_allow_html=True)

# ── My Tasks ──────────────────────────────────────────────────────────────────
def my_tasks_view():
    st.markdown("# My Tasks")
    tasks = all_tasks()
    for pid, p in st.session_state.data["projects"].items():
        ptasks = [t for t in tasks if t["project_id"] == pid]
        if not ptasks: continue
        n_open = sum(1 for t in ptasks if not t["completed"])
        st.markdown(
            f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:4px">'
            f'<div style="width:10px;height:10px;border-radius:3px;background:{p["color"]}"></div>'
            f'<span style="font-weight:600;font-size:14px">{p["name"]}</span>'
            f'<span style="color:#9ca3af;font-size:12px">({n_open} open)</span></div>',
            unsafe_allow_html=True)
        for t in sorted(ptasks, key=lambda x: x.get("due_date") or "9999"):
            c1,c2,c3,c4,c5 = st.columns([4,2,2,2,1])
            chk = c1.checkbox(t["title"], value=t["completed"], key=f"mt_{t['id']}")
            if chk != t["completed"]:
                st.session_state.data["projects"][pid]["tasks"][t["id"]]["completed"] = chk
                if chk:
                    st.session_state.data["projects"][pid]["tasks"][t["id"]]["section"] = "Done"
                    log_activity("Task completed", t["title"])
                save(); st.rerun()
            c2.write(t.get("section",""))
            if t.get("assignee"):
                c3.markdown(avatar_html(t["assignee"],20)+
                            f' <span style="font-size:12px">{t["assignee"]}</span>',
                            unsafe_allow_html=True)
            else: c3.write("—")
            dt, dst = rel_date(t.get("due_date"))
            if dst=="overdue":    c4.markdown(f":red[{dt}]")
            elif dst=="due-soon": c4.markdown(f":orange[{dt}]")
            else:                 c4.write(dt)
            if c5.button("↗", key=f"mt_{t['id']}_o"):
                st.session_state.active_project = pid
                st.session_state.active_task    = t["id"]
                st.session_state.show_task      = True; st.rerun()
        st.markdown("")

# ── Search ────────────────────────────────────────────────────────────────────
def search_view():
    q = st.session_state.search_query.lower()
    st.markdown(f'# Search: <span style="color:#6b7280;font-style:italic">{st.session_state.search_query}</span>',
                unsafe_allow_html=True)
    tasks   = all_tasks()
    results = [t for t in tasks
               if q in t["title"].lower()
               or q in t.get("description","").lower()
               or any(q in tag.lower() for tag in t.get("tags",[]))]
    st.markdown(f'<p style="color:#6b7280;font-size:13px">{len(results)} results</p>',
                unsafe_allow_html=True)
    if not results:
        st.markdown('<div style="color:#9ca3af;font-size:14px;padding:16px 0">No tasks match your search.</div>',
                    unsafe_allow_html=True)
        return
    for t in results:
        c1,c2,c3,c4 = st.columns([4,2,2,1])
        pc = PRI_COLOR.get(t.get("priority","medium"),"#888")
        c1.markdown(
            f'<div style="display:flex;gap:8px;align-items:flex-start">'
            f'<div style="width:3px;height:16px;background:{pc};border-radius:2px;margin-top:2px;flex-shrink:0"></div>'
            f'<div><div style="font-weight:500;font-size:13.5px">{t["title"]}</div>'
            f'<div style="font-size:12px;color:#9ca3af">{t["project_name"]}</div></div></div>',
            unsafe_allow_html=True)
        c2.write(t.get("section",""))
        dt, dst = rel_date(t.get("due_date"))
        if dst=="overdue":    c3.markdown(f":red[{dt}]")
        elif dst=="due-soon": c3.markdown(f":orange[{dt}]")
        else:                 c3.write(dt)
        if c4.button("↗", key=f"sr_{t['id']}"):
            st.session_state.active_project = t["project_id"]
            st.session_state.active_task    = t["id"]
            st.session_state.show_task      = True; st.rerun()
        st.divider()

# ── Router ────────────────────────────────────────────────────────────────────
v = st.session_state.view
if   v == "dashboard":                             dashboard()
elif v == "inbox":                                 inbox()
elif v == "my_tasks":                              my_tasks_view()
elif v == "search":                                search_view()
elif v == "project" and st.session_state.active_project:
    project_view(st.session_state.active_project)
else:
    dashboard()
