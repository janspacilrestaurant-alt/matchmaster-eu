import streamlit as st
import json
import os
from datetime import datetime, date, timedelta
import calendar as cal_lib
import uuid

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="TaskFlow",
    page_icon="✓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
* { font-family: 'Inter', sans-serif !important; box-sizing: border-box; }

/* Sidebar – clean white */
[data-testid="stSidebar"] { background: #ffffff !important; border-right: 1px solid #e8e8e8 !important; }
[data-testid="stSidebar"] .stButton > button {
    background: transparent !important; border: none !important; color: #4a4a4a !important;
    text-align: left !important; padding: 7px 10px !important; border-radius: 6px !important;
    font-size: 13.5px !important; width: 100% !important; transition: background 0.1s;
}
[data-testid="stSidebar"] .stButton > button:hover { background: #f5f5f5 !important; }
[data-testid="stSidebar"] .stButton > button[kind="primary"] {
    background: #fff0ef !important; color: #d0453a !important; font-weight: 600 !important;
}
[data-testid="stSidebar"] p, [data-testid="stSidebar"] span,
[data-testid="stSidebar"] div, [data-testid="stSidebar"] label,
[data-testid="stSidebar"] input { color: #4a4a4a !important; }

/* Main area */
.stApp { background: #f9f8f8; }
.main .block-container { padding-top: 1.2rem !important; }
p, span, div, label { color: #1f1f1f; }
h1, h2, h3, h4, h5 { color: #1f1f1f !important; }

/* Metric cards */
.metric-card { background:#fff; border:1px solid #e8e8e8; border-radius:10px; padding:20px; text-align:center; }
.metric-num   { font-size:30px; font-weight:700; color:#1f1f1f; margin:0; }
.metric-label { font-size:12px; color:#6d6e6f; margin:4px 0 0; }

/* Section header in board */
.sec-hdr {
    font-size:11px; font-weight:700; letter-spacing:0.08em; text-transform:uppercase;
    color:#6d6e6f; padding:4px 0 8px; border-bottom:2px solid #e8e8e8; margin-bottom:10px;
}

/* Tag chips */
.tag { display:inline-block; background:#f0f0f0; color:#555; border-radius:10px;
       padding:1px 8px; font-size:11px; margin-right:3px; }

/* Status badges */
.st-on-track  { background:#e8f5e9; color:#2e7d32; border-radius:4px; padding:2px 10px; font-size:12px; font-weight:500; display:inline-block; }
.st-at-risk   { background:#fff3e0; color:#bf360c; border-radius:4px; padding:2px 10px; font-size:12px; font-weight:500; display:inline-block; }
.st-off-track { background:#fce4ec; color:#880e4f; border-radius:4px; padding:2px 10px; font-size:12px; font-weight:500; display:inline-block; }

/* Sidebar labels */
.s-brand   { font-size:18px; font-weight:700; color:#f06a6a; padding:12px 0 4px; }
.s-section { font-size:10px; font-weight:700; letter-spacing:0.1em; text-transform:uppercase;
             color:#bbb; padding:10px 0 4px; }

/* Activity item */
.act-item { padding:10px 0; border-bottom:1px solid #f0f0f0; font-size:13.5px; }

/* Gantt / Calendar table */
.gantt-wrap { overflow-x: auto; }
</style>
""", unsafe_allow_html=True)

# ── Constants ─────────────────────────────────────────────────────────────────
DATA_FILE = "data/projects.json"
DEFAULT_SECTIONS = ["To Do", "In Progress", "Review", "Done"]
PRIORITIES = ["high", "medium", "low"]
PRI_COLOR  = {"high": "#d0453a", "medium": "#d08d3a", "low": "#2e7d32"}
PROJECT_COLORS = ["#6366f1","#8b5cf6","#ec4899","#f59e0b","#10b981","#3b82f6","#ef4444","#06b6d4"]
AVATAR_COLORS  = ["#4CAF50","#2196F3","#FF5722","#9C27B0","#FF9800","#00BCD4","#E91E63","#795548"]
STATUS_INFO = {
    "on_track":  {"label": "On Track",  "css": "st-on-track"},
    "at_risk":   {"label": "At Risk",   "css": "st-at-risk"},
    "off_track": {"label": "Off Track", "css": "st-off-track"},
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
            "id": tid, "title": title, "description": desc,
            "assignee": assignee,
            "due_date": str(today + timedelta(days=days)) if days is not None else None,
            "priority": priority, "section": section, "tags": tags,
            "subtasks": subtasks or [], "comments": cmts or [],
            "completed": done, "created_at": str(datetime.now()),
        }

    p1 = gen_id()
    t1 = mk("Create wireframes", "Homepage, dashboard, and settings pages",
             "Alice", 3, "high", "In Progress", ["design","UX"],
             subtasks=[
                 {"id": gen_id(), "title": "Homepage", "completed": True},
                 {"id": gen_id(), "title": "Dashboard", "completed": False},
                 {"id": gen_id(), "title": "Settings",  "completed": False},
             ],
             cmts=[{"author": "Bob", "text": "Homepage looks great!", "created_at": str(datetime.now())}])
    t2 = mk("Set up CI/CD", "GitHub Actions + Docker deployment", "Charlie", 7, "medium", "To Do", ["devops"])
    t3 = mk("Write API docs", "All REST endpoints with examples", "Diana", -1, "high", "Review", ["docs"])
    t4 = mk("Logo redesign", "SVG + PNG brand assets", "Alice", -5, "low", "Done", ["design"], done=True)
    d["projects"][p1] = {
        "id": p1, "name": "Website Redesign",
        "description": "Complete overhaul with new branding and improved UX",
        "color": "#6366f1", "status": "on_track", "sections": DEFAULT_SECTIONS[:],
        "tasks": {t[0]: t[1] for t in [t1, t2, t3, t4]},
        "created_at": str(datetime.now()),
    }

    p2 = gen_id()
    t5 = mk("Draft email newsletter", "Q3 product launch copy + design", "Bob", 5, "medium", "To Do", ["marketing","email"])
    t6 = mk("Schedule social posts", "30-day content calendar", "Diana", 2, "high", "In Progress", ["social"])
    t7 = mk("Influencer outreach", "Micro-influencer list + initial DMs", "Charlie", 10, "low", "To Do", ["marketing"])
    d["projects"][p2] = {
        "id": p2, "name": "Q3 Marketing Campaign",
        "description": "Social media and email campaign for Q3 launch",
        "color": "#ec4899", "status": "at_risk", "sections": DEFAULT_SECTIONS[:],
        "tasks": {t[0]: t[1] for t in [t5, t6, t7]},
        "created_at": str(datetime.now()),
    }

    p3 = gen_id()
    t8 = mk("Migrate DB to PostgreSQL", "SQLite → PG migration + ORM update", "Charlie", 14, "high", "To Do", ["backend","db"])
    t9 = mk("Load testing", "k6 tests @ 10k req/s", "Bob", 8, "medium", "To Do", ["devops","testing"])
    d["projects"][p3] = {
        "id": p3, "name": "Infrastructure Upgrade",
        "description": "Database migration and performance hardening",
        "color": "#10b981", "status": "on_track", "sections": DEFAULT_SECTIONS[:],
        "tasks": {t[0]: t[1] for t in [t8, t9]},
        "created_at": str(datetime.now()),
    }

    d["activity"] = [
        {"action": "Project created", "detail": "Website Redesign",    "at": str(datetime.now())},
        {"action": "Task completed",  "detail": "Logo redesign",        "at": str(datetime.now())},
        {"action": "Comment added",   "detail": "Bob on Create wireframes", "at": str(datetime.now())},
    ]
    save()

# ── Session state init ────────────────────────────────────────────────────────
if "data" not in st.session_state:
    st.session_state.data = _load_data()
    if not st.session_state.data["projects"]:
        _sample_data()

_DEFAULTS = {
    "view":           "dashboard",
    "active_project": None,
    "active_task":    None,
    "project_view":   "board",
    "show_task":      False,
    "show_new_task":  False,
    "new_task_sec":   None,
    "inline_sec":     None,
    "show_del_proj":  None,
    "search_query":   "",
    "cal_year":       date.today().year,
    "cal_month":      date.today().month,
}
for k, v in _DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Helpers ───────────────────────────────────────────────────────────────────
def proj(pid=None):
    pid = pid or st.session_state.active_project
    return st.session_state.data["projects"].get(pid)

def all_tasks():
    out = []
    for pid, p in st.session_state.data["projects"].items():
        for t in p["tasks"].values():
            out.append({**t, "project_id": pid,
                        "project_name": p["name"], "project_color": p["color"]})
    return out

def due_status(ds):
    if not ds:
        return None
    try:
        d = date.fromisoformat(str(ds)[:10])
        today = date.today()
        if d < today:                        return "overdue"
        if d <= today + timedelta(days=2):   return "due-soon"
        return "ok"
    except Exception:
        return None

def rel_date(ds):
    if not ds:
        return "—", None
    try:
        d = date.fromisoformat(str(ds)[:10])
        diff = (d - date.today()).days
        if diff < -1:  return f"Overdue {-diff}d", "overdue"
        if diff == -1: return "Yesterday",           "overdue"
        if diff == 0:  return "Today",               "due-soon"
        if diff == 1:  return "Tomorrow",            "due-soon"
        if diff <= 7:  return f"In {diff}d",         "ok"
        return d.strftime("%b %d"),                  "ok"
    except Exception:
        return str(ds), None

def avatar_html(name, size=26):
    if not name:
        return (f'<div style="width:{size}px;height:{size}px;border-radius:50%;background:#e0e0e0;'
                f'display:inline-flex;align-items:center;justify-content:center;'
                f'font-size:{int(size/2.5)}px;color:#888">?</div>')
    initials = "".join(w[0].upper() for w in name.split()[:2])
    color = AVATAR_COLORS[hash(name) % len(AVATAR_COLORS)]
    return (f'<div style="width:{size}px;height:{size}px;border-radius:50%;background:{color};'
            f'display:inline-flex;align-items:center;justify-content:center;'
            f'font-size:{int(size/2.5)}px;color:white;font-weight:600;flex-shrink:0">{initials}</div>')

def due_html(ds):
    txt, status = rel_date(ds)
    if txt == "—":
        return ""
    color = "#d0453a" if status == "overdue" else ("#d08d3a" if status == "due-soon" else "#6d6e6f")
    return f'<span style="color:{color};font-size:12px">📅 {txt}</span>'

def nav(view=None, project=None, task=None, show_task=False):
    if view is not None:    st.session_state.view = view
    if project is not None: st.session_state.active_project = project
    if task is not None:    st.session_state.active_task = task
    st.session_state.show_task     = show_task
    st.session_state.show_new_task = False
    st.session_state.inline_sec    = None
    st.rerun()

# ── Sidebar ───────────────────────────────────────────────────────────────────
def sidebar():
    with st.sidebar:
        st.markdown('<div class="s-brand">✓ TaskFlow</div>', unsafe_allow_html=True)

        q = st.text_input("search", value=st.session_state.search_query,
                          label_visibility="collapsed", placeholder="🔍  Search tasks…",
                          key="search_input")
        if q != st.session_state.search_query:
            st.session_state.search_query = q
            st.session_state.view = "search" if q else "dashboard"
            st.rerun()

        st.markdown("")
        v = st.session_state.view
        if st.button("🏠  Home",     use_container_width=True, type="primary" if v=="dashboard" else "secondary"): nav("dashboard")
        if st.button("📥  Inbox",    use_container_width=True, type="primary" if v=="inbox"     else "secondary"): nav("inbox")
        if st.button("✓  My Tasks", use_container_width=True, type="primary" if v=="my_tasks"  else "secondary"): nav("my_tasks")

        st.markdown('<div class="s-section">Projects</div>', unsafe_allow_html=True)
        for pid, p in st.session_state.data["projects"].items():
            active = (st.session_state.active_project == pid and v == "project")
            n_open = sum(1 for t in p["tasks"].values() if not t["completed"])
            si     = STATUS_INFO.get(p.get("status","on_track"), STATUS_INFO["on_track"])
            label  = f'<span style="color:{p["color"]}">●</span> {p["name"]} ({n_open})'
            if st.button(label, key=f"sb_{pid}", use_container_width=True,
                         type="primary" if active else "secondary"):
                nav("project", project=pid)

        st.markdown("")
        if st.button("＋  New Project", use_container_width=True):
            st.session_state.view = "new_project"
            st.rerun()

        st.markdown("---")
        st.markdown('<div class="s-section">Team</div>', unsafe_allow_html=True)
        for m in st.session_state.data["members"]:
            st.markdown(
                f'<div style="display:flex;align-items:center;gap:8px;padding:4px 0">'
                f'{avatar_html(m,22)}'
                f'<span style="font-size:13px;color:#4a4a4a">{m}</span></div>',
                unsafe_allow_html=True)

sidebar()

# ── Task detail ───────────────────────────────────────────────────────────────
if st.session_state.show_task and st.session_state.active_task and st.session_state.active_project:
    pid  = st.session_state.active_project
    tid  = st.session_state.active_task
    p    = proj(pid)

    if not p or tid not in p["tasks"]:
        st.session_state.show_task = False
        st.rerun()

    task = p["tasks"][tid]
    si   = STATUS_INFO.get(p.get("status","on_track"), STATUS_INFO["on_track"])

    back_col, _ = st.columns([1, 6])
    if back_col.button("← Back"):
        st.session_state.show_task  = False
        st.session_state.active_task = None
        st.rerun()

    st.markdown(f'<h2 style="margin-bottom:4px">{task["title"]}</h2>', unsafe_allow_html=True)
    st.markdown(
        f'<span style="color:#6d6e6f;font-size:13px">Project: <strong>{p["name"]}</strong></span>'
        f'&nbsp;&nbsp;<span class="{si["css"]}">{si["label"]}</span>',
        unsafe_allow_html=True)
    st.markdown("---")

    left, right = st.columns([3, 2])

    with left:
        # ── Subtasks (outside form so checkboxes work immediately) ─────────
        subtasks = task.get("subtasks", [])
        if subtasks:
            done_count = sum(1 for s in subtasks if s["completed"])
            pct = done_count / len(subtasks)
            st.markdown(f"**Subtasks** &nbsp; <span style='color:#6d6e6f;font-size:13px'>{done_count}/{len(subtasks)}</span>",
                        unsafe_allow_html=True)
            st.progress(pct)
            for i, sub in enumerate(subtasks):
                c1, c2 = st.columns([1, 9])
                chk = c1.checkbox("", value=sub["completed"], key=f"sub_{tid}_{i}")
                if chk != sub["completed"]:
                    task["subtasks"][i]["completed"] = chk
                    save(); st.rerun()
                style = "text-decoration:line-through;color:#aaa" if sub["completed"] else ""
                c2.markdown(f'<span style="{style};font-size:14px">{sub["title"]}</span>',
                            unsafe_allow_html=True)

        # ── Form: title, description, new subtask, new comment ─────────────
        with st.form("task_edit"):
            new_title = st.text_input("Title", value=task["title"])
            new_desc  = st.text_area("Description", value=task.get("description",""), height=90)
            new_sub   = st.text_input("＋ Add subtask", placeholder="Subtask title")

            st.markdown("**Add comment**")
            new_comment    = st.text_area("", height=60, label_visibility="collapsed",
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
                    task["comments"].append({
                        "author": comment_author, "text": new_comment.strip(),
                        "created_at": str(datetime.now()),
                    })
                    log_activity("Comment added", f'{comment_author} on "{task["title"]}"')
                log_activity("Task updated", task["title"])
                save(); st.rerun()
            if go_back:
                st.session_state.show_task  = False
                st.session_state.active_task = None
                st.rerun()

        # ── Comments display ───────────────────────────────────────────────
        if task.get("comments"):
            st.markdown("**Comments**")
            for c in task["comments"]:
                ts = c.get("created_at","")[:16]
                st.markdown(
                    f'<div style="display:flex;align-items:flex-start;gap:10px;margin-bottom:14px">'
                    f'{avatar_html(c["author"],30)}'
                    f'<div><strong style="font-size:13px">{c["author"]}</strong>'
                    f'<span style="color:#aaa;font-size:11px;margin-left:8px">{ts}</span>'
                    f'<br><span style="font-size:13.5px">{c["text"]}</span></div></div>',
                    unsafe_allow_html=True)

    with right:
        st.markdown("**Task details**")

        # Assignee
        members_opts = ["(unassigned)"] + st.session_state.data["members"]
        cur_a = task.get("assignee") or "(unassigned)"
        new_a = st.selectbox("Assignee", members_opts,
                              index=members_opts.index(cur_a) if cur_a in members_opts else 0)
        if new_a != cur_a:
            task["assignee"] = None if new_a == "(unassigned)" else new_a
            log_activity("Task reassigned", f'"{task["title"]}" → {new_a}')
            save(); st.rerun()

        # Priority
        new_pr = st.selectbox("Priority", PRIORITIES,
                               index=PRIORITIES.index(task.get("priority","medium")))
        if new_pr != task.get("priority"):
            task["priority"] = new_pr; save(); st.rerun()

        # Section
        secs    = p["sections"]
        cur_sec = task.get("section", secs[0])
        new_sec = st.selectbox("Section", secs,
                                index=secs.index(cur_sec) if cur_sec in secs else 0)
        if new_sec != cur_sec:
            task["section"]   = new_sec
            task["completed"] = (new_sec == "Done")
            log_activity("Task moved", f'"{task["title"]}" → {new_sec}')
            save(); st.rerun()

        # Due date
        cur_due = None
        if task.get("due_date"):
            try: cur_due = date.fromisoformat(str(task["due_date"])[:10])
            except Exception: pass
        new_due = st.date_input("Due date", value=cur_due)
        if new_due and str(new_due) != str(task.get("due_date",""))[:10]:
            task["due_date"] = str(new_due); save(); st.rerun()

        # Tags
        tags_raw = st.text_input("Tags (comma-separated)", value=", ".join(task.get("tags",[])))
        new_tags = [x.strip() for x in tags_raw.split(",") if x.strip()]
        if new_tags != task.get("tags",[]):
            task["tags"] = new_tags; save()

        # Completed
        done_toggle = st.checkbox("Mark as completed", value=task.get("completed", False))
        if done_toggle != task.get("completed", False):
            task["completed"] = done_toggle
            if done_toggle: task["section"] = "Done"
            log_activity("Task completed", task["title"])
            save(); st.rerun()

        st.markdown("---")
        if st.button("🗑️  Delete Task", use_container_width=True):
            log_activity("Task deleted", task["title"])
            del p["tasks"][tid]
            save()
            st.session_state.show_task  = False
            st.session_state.active_task = None
            st.rerun()

    st.stop()

# ── New project form ──────────────────────────────────────────────────────────
if st.session_state.view == "new_project":
    st.markdown("## New Project")
    with st.form("new_proj"):
        name   = st.text_input("Project name *", placeholder="e.g. Mobile App Redesign")
        desc   = st.text_area("Description", height=70)
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
            log_activity("Project created", name.strip())
            save()
            nav("project", project=pid)
        if cancel:
            nav("dashboard")
    st.stop()

# ── New task form ─────────────────────────────────────────────────────────────
def new_task_modal(pid):
    p = proj(pid)
    st.markdown("### ＋ New Task")
    with st.form("new_task_form"):
        title    = st.text_input("Title *", placeholder="Task name")
        desc     = st.text_area("Description", height=60)
        r1, r2   = st.columns(2)
        assignee = r1.selectbox("Assignee", ["(none)"] + st.session_state.data["members"])
        priority = r2.selectbox("Priority", PRIORITIES, index=1)
        r3, r4   = st.columns(2)
        default_sec = st.session_state.new_task_sec or p["sections"][0]
        idx      = p["sections"].index(default_sec) if default_sec in p["sections"] else 0
        section  = r3.selectbox("Section", p["sections"], index=idx)
        due_date = r4.date_input("Due date", value=None)
        tags_raw = st.text_input("Tags (comma-separated)")
        cs, cc   = st.columns(2)
        ok       = cs.form_submit_button("Create Task", type="primary", use_container_width=True)
        cancel   = cc.form_submit_button("Cancel",                      use_container_width=True)

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
            log_activity("Task created", title.strip())
            save()
            st.session_state.show_new_task = False
            st.session_state.new_task_sec  = None
            st.rerun()
        if cancel:
            st.session_state.show_new_task = False
            st.session_state.new_task_sec  = None
            st.rerun()

# ── Board view ────────────────────────────────────────────────────────────────
def board_view(pid):
    p     = proj(pid)
    secs  = p["sections"]
    tasks = p["tasks"]

    with st.expander("⚙️  Manage sections"):
        ec1, ec2, ec3 = st.columns([3, 1, 3])
        new_sec_name = ec1.text_input("New section name", placeholder="e.g. Blocked",
                                       key="new_sec_input", label_visibility="collapsed")
        if ec2.button("Add", key="add_sec_btn") and new_sec_name.strip():
            if new_sec_name.strip() not in secs:
                p["sections"].append(new_sec_name.strip())
                save(); st.rerun()
        removable = [s for s in secs if s not in DEFAULT_SECTIONS]
        if removable:
            sec_del = ec3.selectbox("Remove section", ["—"] + removable,
                                     key="del_sec_sel", label_visibility="collapsed")
            if sec_del != "—" and st.button("Remove", key="del_sec_btn"):
                for t in tasks.values():
                    if t["section"] == sec_del:
                        t["section"] = secs[0]
                p["sections"].remove(sec_del)
                save(); st.rerun()

    cols = st.columns(len(secs))
    for i, sec in enumerate(secs):
        sec_tasks = [t for t in tasks.values() if t["section"] == sec]
        with cols[i]:
            st.markdown(
                f'<div class="sec-hdr">{sec}'
                f'<span style="background:#f0f0f0;border-radius:10px;padding:1px 8px;'
                f'font-size:10px;color:#888;margin-left:6px">{len(sec_tasks)}</span></div>',
                unsafe_allow_html=True)

            for t in sec_tasks:
                subs       = t.get("subtasks", [])
                done_subs  = sum(1 for s in subs if s["completed"])
                pc         = PRI_COLOR.get(t.get("priority","medium"), "#888")
                title_sty  = "text-decoration:line-through;color:#aaa" if t.get("completed") else ""

                c_ttl, c_btn = st.columns([5, 1])
                with c_ttl:
                    st.markdown(
                        f'<div style="padding:10px 0 4px">'
                        f'<span style="width:3px;height:14px;background:{pc};display:inline-block;'
                        f'border-radius:2px;margin-right:6px;vertical-align:middle"></span>'
                        f'<span style="{title_sty};font-size:13.5px;font-weight:500">{t["title"]}</span>'
                        f'</div>',
                        unsafe_allow_html=True)
                with c_btn:
                    if st.button("↗", key=f"b_{t['id']}", help="Open task"):
                        st.session_state.active_task = t["id"]
                        st.session_state.show_task   = True
                        st.rerun()

                # Meta row
                parts = []
                if t.get("assignee"):   parts.append(avatar_html(t["assignee"], 20))
                dt, dst = rel_date(t.get("due_date"))
                if dt != "—":
                    c = "#d0453a" if dst=="overdue" else ("#d08d3a" if dst=="due-soon" else "#6d6e6f")
                    parts.append(f'<span style="color:{c};font-size:12px">📅 {dt}</span>')
                if subs:
                    parts.append(f'<span style="font-size:11px;color:#888">☑ {done_subs}/{len(subs)}</span>')
                if t.get("comments"):
                    parts.append(f'<span style="font-size:11px;color:#888">💬 {len(t["comments"])}</span>')
                if parts:
                    st.markdown(
                        f'<div style="display:flex;align-items:center;gap:8px;padding:0 0 4px">'
                        + "".join(parts) + "</div>",
                        unsafe_allow_html=True)
                if t.get("tags"):
                    st.markdown("".join(f'<span class="tag">{tag}</span>' for tag in t["tags"]),
                                unsafe_allow_html=True)

                other = [s for s in secs if s != sec]
                if other:
                    move = st.selectbox("→", ["Move to…"] + other,
                                        key=f"mv_{t['id']}", label_visibility="collapsed")
                    if move != "Move to…":
                        tasks[t["id"]]["section"]   = move
                        tasks[t["id"]]["completed"] = (move == "Done")
                        log_activity("Task moved", f'"{t["title"]}" → {move}')
                        save(); st.rerun()
                st.markdown("<hr style='border-color:#f0f0f0;margin:6px 0'>", unsafe_allow_html=True)

            # Inline add
            key_inline = f"{pid}_{sec}"
            if st.session_state.inline_sec == key_inline:
                with st.form(f"inline_{sec}"):
                    inline_title = st.text_input("", placeholder="Task name",
                                                  label_visibility="collapsed",
                                                  key=f"it_{sec}")
                    ia, ic = st.columns(2)
                    add_ok  = ia.form_submit_button("Add",  type="primary", use_container_width=True)
                    add_can = ic.form_submit_button("✕",                    use_container_width=True)
                    if add_ok and inline_title.strip():
                        tid = gen_id()
                        p["tasks"][tid] = {
                            "id": tid, "title": inline_title.strip(), "description": "",
                            "assignee": None, "due_date": None, "priority": "medium",
                            "section": sec, "tags": [], "subtasks": [], "comments": [],
                            "completed": False, "created_at": str(datetime.now()),
                        }
                        log_activity("Task created", inline_title.strip())
                        save()
                        st.session_state.inline_sec = None
                        st.rerun()
                    if add_can:
                        st.session_state.inline_sec = None; st.rerun()
            else:
                if st.button(f"＋ Add task", key=f"add_{pid}_{sec}", use_container_width=True):
                    st.session_state.inline_sec = key_inline; st.rerun()

# ── List view ─────────────────────────────────────────────────────────────────
def list_view(pid):
    p     = proj(pid)
    tasks = list(p["tasks"].values())

    fc1, fc2, fc3 = st.columns(3)
    f_sec = fc1.selectbox("Section",  ["All"] + p["sections"])
    f_pri = fc2.selectbox("Priority", ["All"] + PRIORITIES)
    f_ass = fc3.selectbox("Assignee", ["All"] + st.session_state.data["members"])
    if f_sec != "All": tasks = [t for t in tasks if t["section"] == f_sec]
    if f_pri != "All": tasks = [t for t in tasks if t.get("priority") == f_pri]
    if f_ass != "All": tasks = [t for t in tasks if t.get("assignee") == f_ass]

    st.caption(f"{len(tasks)} tasks")
    st.markdown("---")
    heads = st.columns([4, 2, 2, 1, 2, 1])
    for col, lbl in zip(heads, ["**Title**","**Section**","**Assignee**","**Pri**","**Due**",""]):
        col.markdown(lbl)
    st.markdown("---")

    for t in sorted(tasks, key=lambda x: x.get("due_date") or "9999"):
        c1, c2, c3, c4, c5, c6 = st.columns([4, 2, 2, 1, 2, 1])
        title = f"~~{t['title']}~~" if t["completed"] else t["title"]
        c1.markdown(title)
        c2.write(t.get("section",""))
        if t.get("assignee"):
            c3.markdown(avatar_html(t["assignee"],22) +
                        f' <span style="font-size:13px">{t["assignee"]}</span>',
                        unsafe_allow_html=True)
        else:
            c3.write("—")
        pc = PRI_COLOR.get(t.get("priority","medium"),"#888")
        c4.markdown(f'<span style="color:{pc};font-weight:600;font-size:12px">'
                    f'{t.get("priority","")[:1].upper()}</span>', unsafe_allow_html=True)
        dt, dst = rel_date(t.get("due_date"))
        if dst == "overdue":    c5.markdown(f":red[{dt}]")
        elif dst == "due-soon": c5.markdown(f":orange[{dt}]")
        else:                   c5.write(dt)
        if c6.button("↗", key=f"l_{t['id']}"):
            st.session_state.active_task = t["id"]
            st.session_state.show_task   = True
            st.rerun()

# ── Timeline view (Gantt) ─────────────────────────────────────────────────────
def timeline_view(pid):
    p     = proj(pid)
    today = date.today()
    start = today - timedelta(days=today.weekday())   # Monday of current week
    weeks = [start + timedelta(weeks=i) for i in range(6)]

    tasks_dated = [t for t in p["tasks"].values() if t.get("due_date")]

    html = '<div class="gantt-wrap"><table style="width:100%;border-collapse:collapse;font-size:13px">'
    html += ('<thead><tr>'
             '<th style="text-align:left;padding:8px 12px;color:#6d6e6f;font-weight:600;'
             'border-bottom:2px solid #e8e8e8;min-width:200px">Task</th>'
             '<th style="padding:8px;color:#6d6e6f;font-weight:600;border-bottom:2px solid #e8e8e8;width:36px"></th>')
    for w in weeks:
        is_cur = (w <= today < w + timedelta(weeks=1))
        bg = "background:#fff5f5;" if is_cur else ""
        html += (f'<th style="{bg}text-align:center;padding:6px 4px;color:#6d6e6f;'
                 f'font-size:11px;font-weight:600;border-bottom:2px solid #e8e8e8">'
                 f'{w.strftime("%b %d")}</th>')
    html += "</tr></thead><tbody>"

    if not tasks_dated:
        html += f'<tr><td colspan="{len(weeks)+2}" style="text-align:center;padding:20px;color:#aaa;font-style:italic">No tasks with due dates</td></tr>'

    for t in sorted(tasks_dated, key=lambda x: x.get("due_date","")):
        due = date.fromisoformat(t["due_date"][:10])
        try:    t_start = datetime.fromisoformat(t["created_at"][:10]).date()
        except: t_start = due - timedelta(days=7)

        color = ("#bdbdbd" if t.get("completed") else
                 "#f06a6a" if due < today else
                 "#ff9800" if due <= today + timedelta(days=3) else
                 "#6366f1")

        sty   = "text-decoration:line-through;color:#aaa" if t.get("completed") else "color:#1f1f1f"
        ava   = avatar_html(t.get("assignee"), 22) if t.get("assignee") else ""
        title = t["title"][:30] + ("…" if len(t["title"]) > 30 else "")

        html += (f'<tr style="border-bottom:1px solid #f5f5f5">'
                 f'<td style="padding:8px 12px;max-width:200px;overflow:hidden;white-space:nowrap">'
                 f'<span style="{sty}">{title}</span></td>'
                 f'<td style="padding:8px 4px">{ava}</td>')

        for w in weeks:
            w_end    = w + timedelta(weeks=1)
            in_range = t_start < w_end and due >= w
            cell_bg  = "background:#fff5f5;" if (w <= today < w_end) else ""

            if in_range:
                bar_s  = max(t_start, w)
                bar_e  = min(due, w_end - timedelta(days=1))
                left   = (bar_s - w).days / 7 * 100
                width  = max(5, ((bar_e - bar_s).days + 1) / 7 * 100)
                due_lbl = (f'<span style="position:absolute;right:4px;top:2px;'
                           f'font-size:10px;color:white;font-weight:700">'
                           f'{due.strftime("%d")}</span>' if w <= due < w_end else "")
                html += (f'<td style="padding:4px 2px;{cell_bg}">'
                         f'<div style="position:relative;height:24px">'
                         f'<div style="position:absolute;left:{left:.0f}%;width:{width:.0f}%;'
                         f'height:20px;background:{color};border-radius:4px;top:2px;opacity:0.85">'
                         f'{due_lbl}</div></div></td>')
            else:
                html += f'<td style="padding:4px 2px;{cell_bg}"></td>'

        html += "</tr>"

    html += "</tbody></table></div>"
    html += """<div style="margin-top:12px;font-size:12px;color:#6d6e6f;display:flex;gap:16px">
      <span><span style="display:inline-block;width:12px;height:12px;background:#6366f1;border-radius:2px"></span> Upcoming</span>
      <span><span style="display:inline-block;width:12px;height:12px;background:#ff9800;border-radius:2px"></span> Due soon</span>
      <span><span style="display:inline-block;width:12px;height:12px;background:#f06a6a;border-radius:2px"></span> Overdue</span>
      <span><span style="display:inline-block;width:12px;height:12px;background:#bdbdbd;border-radius:2px"></span> Completed</span>
    </div>"""
    st.markdown(html, unsafe_allow_html=True)

# ── Calendar view ─────────────────────────────────────────────────────────────
def calendar_view(pid):
    p     = proj(pid)
    today = date.today()

    nc1, nc2, nc3 = st.columns([1, 2, 1])
    if nc1.button("← Prev"):
        if st.session_state.cal_month == 1:
            st.session_state.cal_month = 12; st.session_state.cal_year -= 1
        else:
            st.session_state.cal_month -= 1
        st.rerun()
    nc2.markdown(
        f'<h3 style="text-align:center;margin:0">'
        f'{date(st.session_state.cal_year, st.session_state.cal_month, 1).strftime("%B %Y")}</h3>',
        unsafe_allow_html=True)
    if nc3.button("Next →"):
        if st.session_state.cal_month == 12:
            st.session_state.cal_month = 1; st.session_state.cal_year += 1
        else:
            st.session_state.cal_month += 1
        st.rerun()

    tasks_by_day = {}
    for t in p["tasks"].values():
        if t.get("due_date"):
            try:
                d = date.fromisoformat(t["due_date"][:10])
                if d.year == st.session_state.cal_year and d.month == st.session_state.cal_month:
                    tasks_by_day.setdefault(d.day, []).append(t)
            except Exception:
                pass

    month_grid = cal_lib.monthcalendar(st.session_state.cal_year, st.session_state.cal_month)

    html = '<table style="width:100%;border-collapse:collapse">'
    html += '<tr>' + "".join(
        f'<th style="text-align:center;padding:8px;color:#6d6e6f;font-size:12px;'
        f'font-weight:600;border-bottom:2px solid #e8e8e8">{d}</th>'
        for d in ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
    ) + '</tr>'

    for week in month_grid:
        html += '<tr>'
        for day in week:
            if day == 0:
                html += '<td style="border:1px solid #f0f0f0;min-height:90px;background:#fafafa;vertical-align:top;padding:4px"></td>'
            else:
                is_today = (day == today.day and
                            st.session_state.cal_month == today.month and
                            st.session_state.cal_year  == today.year)
                day_bg  = "#fff5f5" if is_today else "#ffffff"
                num_sty = ("font-size:13px;font-weight:700;color:#f06a6a" if is_today
                           else "font-size:13px;color:#6d6e6f")
                chips = ""
                for t in tasks_by_day.get(day, []):
                    bg_c  = "#bdbdbd" if t.get("completed") else (
                            "#f06a6a" if str(t.get("due_date","")) < str(today) else "#6366f1")
                    label = (t["title"][:14] + "…") if len(t["title"]) > 14 else t["title"]
                    chips += (f'<div style="background:{bg_c};color:white;border-radius:3px;'
                              f'padding:2px 6px;font-size:11px;margin-top:2px;'
                              f'white-space:nowrap;overflow:hidden">{label}</div>')
                html += (f'<td style="border:1px solid #e8e8e8;min-height:90px;padding:6px;'
                         f'vertical-align:top;background:{day_bg}">'
                         f'<span style="{num_sty}">{day}</span>{chips}</td>')
        html += '</tr>'

    html += '</table>'
    st.markdown(html, unsafe_allow_html=True)

# ── Project view ──────────────────────────────────────────────────────────────
def project_view(pid):
    p = proj(pid)
    if not p:
        st.error("Project not found."); return

    si    = STATUS_INFO.get(p.get("status","on_track"), STATUS_INFO["on_track"])
    tasks = list(p["tasks"].values())
    n_done = sum(1 for t in tasks if t["completed"])
    pct    = n_done / len(tasks) if tasks else 0

    hc1, hc2 = st.columns([4, 4])
    with hc1:
        st.markdown(
            f'<h2 style="color:{p["color"]};margin-bottom:2px">{p["name"]}</h2>'
            f'<div style="display:flex;align-items:center;gap:10px;margin-bottom:4px">'
            f'<span class="{si["css"]}">{si["label"]}</span>'
            f'<span style="color:#6d6e6f;font-size:13px">{p.get("description","")}</span>'
            f'</div>',
            unsafe_allow_html=True)
        st.progress(pct, text=f"{n_done}/{len(tasks)} tasks completed")

    with hc2:
        pv = st.session_state.project_view
        b1, b2, b3, b4, b5, b6 = st.columns(6)
        if b1.button("Board",    use_container_width=True, type="primary" if pv=="board"    else "secondary"): st.session_state.project_view="board";    st.rerun()
        if b2.button("List",     use_container_width=True, type="primary" if pv=="list"     else "secondary"): st.session_state.project_view="list";     st.rerun()
        if b3.button("Timeline", use_container_width=True, type="primary" if pv=="timeline" else "secondary"): st.session_state.project_view="timeline"; st.rerun()
        if b4.button("Calendar", use_container_width=True, type="primary" if pv=="calendar" else "secondary"): st.session_state.project_view="calendar"; st.rerun()
        if b5.button("＋ Task",  use_container_width=True, type="primary"):
            st.session_state.show_new_task = True; st.rerun()
        if b6.button("🗑️",      use_container_width=True):
            st.session_state.show_del_proj = pid; st.rerun()

    # Delete confirm
    if st.session_state.show_del_proj == pid:
        st.warning(f'Delete **{p["name"]}**? All tasks will be removed.')
        dc1, dc2 = st.columns(2)
        if dc1.button("Yes, delete", type="primary", use_container_width=True):
            log_activity("Project deleted", p["name"])
            del st.session_state.data["projects"][pid]
            save()
            st.session_state.show_del_proj = None
            nav("dashboard")
        if dc2.button("Cancel", use_container_width=True):
            st.session_state.show_del_proj = None; st.rerun()
        st.stop()

    # Status update
    with st.expander("📊  Update project status"):
        cur_status = p.get("status","on_track")
        new_status = st.selectbox("Status", list(STATUS_INFO.keys()),
                                   index=list(STATUS_INFO.keys()).index(cur_status),
                                   format_func=lambda k: STATUS_INFO[k]["label"])
        if st.button("Update", key="upd_status"):
            p["status"] = new_status
            log_activity("Project status updated",
                         f'{p["name"]} → {STATUS_INFO[new_status]["label"]}')
            save(); st.rerun()

    st.markdown("---")

    if st.session_state.show_new_task:
        new_task_modal(pid); return

    pv = st.session_state.project_view
    if pv == "board":      board_view(pid)
    elif pv == "list":     list_view(pid)
    elif pv == "timeline": timeline_view(pid)
    elif pv == "calendar": calendar_view(pid)

# ── Dashboard ─────────────────────────────────────────────────────────────────
def dashboard():
    st.markdown("# 🏠 Home")
    tasks = all_tasks()

    total     = len(tasks)
    overdue   = sum(1 for t in tasks if not t["completed"] and due_status(t.get("due_date")) == "overdue")
    in_prog   = sum(1 for t in tasks if t.get("section") == "In Progress" and not t["completed"])
    completed = sum(1 for t in tasks if t["completed"])

    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(f'<div class="metric-card"><p class="metric-num">{total}</p><p class="metric-label">Total Tasks</p></div>',     unsafe_allow_html=True)
    c2.markdown(f'<div class="metric-card"><p class="metric-num" style="color:#d0453a">{overdue}</p><p class="metric-label">Overdue</p></div>',     unsafe_allow_html=True)
    c3.markdown(f'<div class="metric-card"><p class="metric-num" style="color:#3b82f6">{in_prog}</p><p class="metric-label">In Progress</p></div>',  unsafe_allow_html=True)
    c4.markdown(f'<div class="metric-card"><p class="metric-num" style="color:#10b981">{completed}</p><p class="metric-label">Completed</p></div>', unsafe_allow_html=True)

    st.markdown("---")
    left, right = st.columns([3, 2])

    with left:
        st.markdown("### 📌 Upcoming")
        upcoming = sorted(
            [t for t in tasks if not t["completed"] and t.get("due_date")],
            key=lambda x: x.get("due_date",""))[:10]

        if not upcoming:
            st.info("No upcoming tasks.")
        else:
            for t in upcoming:
                dt, dst = rel_date(t.get("due_date"))
                ct, ca, cd, cbtn = st.columns([4, 2, 2, 1])
                ct.markdown(f"**{t['title']}**  \n<span style='font-size:12px;color:#888'>{t['project_name']}</span>",
                            unsafe_allow_html=True)
                if t.get("assignee"):
                    ca.markdown(avatar_html(t["assignee"],22) +
                                f' <span style="font-size:12px">{t["assignee"]}</span>',
                                unsafe_allow_html=True)
                if dst == "overdue":    cd.markdown(f":red[{dt}]")
                elif dst == "due-soon": cd.markdown(f":orange[{dt}]")
                else:                   cd.write(dt)
                if cbtn.button("↗", key=f"dash_{t['id']}"):
                    st.session_state.active_project = t["project_id"]
                    st.session_state.active_task    = t["id"]
                    st.session_state.show_task      = True
                    st.rerun()
                st.divider()

    with right:
        st.markdown("### 📁 Projects")
        for pid, p in st.session_state.data["projects"].items():
            all_t  = list(p["tasks"].values())
            n_done = sum(1 for t in all_t if t["completed"])
            n_tot  = len(all_t)
            si     = STATUS_INFO.get(p.get("status","on_track"), STATUS_INFO["on_track"])
            st.markdown(
                f'<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:4px">'
                f'<span style="font-weight:500"><span style="color:{p["color"]}">●</span> {p["name"]}</span>'
                f'<span class="{si["css"]}">{si["label"]}</span></div>',
                unsafe_allow_html=True)
            st.progress(n_done / n_tot if n_tot else 0, text=f"{n_done}/{n_tot}")
            if st.button("Open →", key=f"dp_{pid}"):
                nav("project", project=pid)
            st.markdown("")

# ── Inbox ─────────────────────────────────────────────────────────────────────
def inbox():
    st.markdown("# 📥 Inbox")
    activity = list(reversed(st.session_state.data.get("activity", [])))
    if not activity:
        st.info("No activity yet. Start creating projects and tasks!")
        return
    for item in activity[:60]:
        ts = item.get("at","")[:16]
        st.markdown(
            f'<div class="act-item">'
            f'<strong>{item.get("action","")}</strong>'
            f' <span style="color:#6d6e6f">— {item.get("detail","")}</span>'
            f'<span style="color:#bbb;font-size:12px;float:right">{ts}</span>'
            f'</div>',
            unsafe_allow_html=True)

# ── My Tasks ──────────────────────────────────────────────────────────────────
def my_tasks_view():
    st.markdown("# ✓ My Tasks")
    tasks = all_tasks()

    for pid, p in st.session_state.data["projects"].items():
        ptasks = [t for t in tasks if t["project_id"] == pid]
        if not ptasks: continue
        n_open = sum(1 for t in ptasks if not t["completed"])
        st.markdown(
            f'<span style="color:{p["color"]}">●</span> **{p["name"]}** '
            f'<span style="color:#aaa;font-size:13px">({n_open} open)</span>',
            unsafe_allow_html=True)
        for t in sorted(ptasks, key=lambda x: x.get("due_date") or "9999"):
            c1, c2, c3, c4, c5 = st.columns([4, 2, 2, 2, 1])
            chk = c1.checkbox(t["title"], value=t["completed"], key=f"mt_{t['id']}")
            if chk != t["completed"]:
                st.session_state.data["projects"][pid]["tasks"][t["id"]]["completed"] = chk
                if chk:
                    st.session_state.data["projects"][pid]["tasks"][t["id"]]["section"] = "Done"
                    log_activity("Task completed", t["title"])
                save(); st.rerun()
            c2.write(t.get("section",""))
            if t.get("assignee"):
                c3.markdown(avatar_html(t["assignee"],20) +
                            f' <span style="font-size:12px">{t["assignee"]}</span>',
                            unsafe_allow_html=True)
            else: c3.write("—")
            dt, dst = rel_date(t.get("due_date"))
            if dst == "overdue":    c4.markdown(f":red[{dt}]")
            elif dst == "due-soon": c4.markdown(f":orange[{dt}]")
            else:                   c4.write(dt)
            if c5.button("↗", key=f"mt_{t['id']}_open"):
                st.session_state.active_project = pid
                st.session_state.active_task    = t["id"]
                st.session_state.show_task      = True
                st.rerun()
        st.markdown("")

# ── Search ────────────────────────────────────────────────────────────────────
def search_view():
    q = st.session_state.search_query.lower()
    st.markdown(f"# 🔍 Search: *{st.session_state.search_query}*")
    tasks   = all_tasks()
    results = [t for t in tasks
               if q in t["title"].lower()
               or q in t.get("description","").lower()
               or any(q in tag.lower() for tag in t.get("tags",[]))]
    st.caption(f"{len(results)} results")
    if not results:
        st.info("No tasks match your search."); return
    for t in results:
        c1, c2, c3, c4 = st.columns([4, 2, 2, 1])
        c1.markdown(f"**{t['title']}**  \n<span style='font-size:12px;color:#888'>{t['project_name']}</span>",
                    unsafe_allow_html=True)
        c2.write(t.get("section",""))
        dt, dst = rel_date(t.get("due_date"))
        if dst == "overdue":    c3.markdown(f":red[{dt}]")
        elif dst == "due-soon": c3.markdown(f":orange[{dt}]")
        else:                   c3.write(dt)
        if c4.button("↗", key=f"sr_{t['id']}"):
            st.session_state.active_project = t["project_id"]
            st.session_state.active_task    = t["id"]
            st.session_state.show_task      = True
            st.rerun()
        st.divider()

# ── Router ────────────────────────────────────────────────────────────────────
v = st.session_state.view
if   v == "dashboard":                              dashboard()
elif v == "inbox":                                  inbox()
elif v == "my_tasks":                               my_tasks_view()
elif v == "search":                                 search_view()
elif v == "project" and st.session_state.active_project:
    project_view(st.session_state.active_project)
else:
    dashboard()
