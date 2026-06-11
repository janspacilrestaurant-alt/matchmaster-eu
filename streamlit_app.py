import streamlit as st
import json
import os
from datetime import datetime, date, timedelta
import uuid

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="TaskFlow – Project Planning",
    page_icon="✓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

[data-testid="stSidebar"] {
    background: #1a1a2e;
    border-right: 1px solid #2d2d44;
}
[data-testid="stSidebar"] .stButton > button {
    text-align: left !important;
    background: transparent !important;
    border: none !important;
    color: #b8bcc8 !important;
    padding: 6px 10px !important;
    border-radius: 6px !important;
    font-size: 14px !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: #2d2d44 !important;
    color: #e8eaf0 !important;
}
[data-testid="stSidebar"] .stButton > button[kind="primary"] {
    background: #2d2d44 !important;
    color: #ffffff !important;
    font-weight: 600 !important;
}

.metric-card {
    background: linear-gradient(135deg, #1e1e30 0%, #252540 100%);
    border: 1px solid #3a3a55;
    border-radius: 12px;
    padding: 20px;
    text-align: center;
    margin-bottom: 8px;
}
.metric-num { font-size: 32px; font-weight: 700; color: #a78bfa; margin: 0; }
.metric-label { font-size: 13px; color: #9ca3af; margin: 4px 0 0 0; }

.section-col-header {
    font-size: 13px;
    font-weight: 600;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    color: #9ca3af;
    padding: 6px 0 10px 0;
    border-bottom: 2px solid #374151;
    margin-bottom: 10px;
}

.task-card-title { font-size: 14px; font-weight: 500; color: #e2e8f0; margin-bottom: 6px; }
.task-card-meta  { font-size: 12px; color: #6b7280; }
.tag-chip {
    display: inline-block;
    background: #374151;
    color: #d1d5db;
    border-radius: 4px;
    padding: 1px 7px;
    font-size: 11px;
    margin-right: 4px;
}

.sidebar-brand {
    font-size: 20px;
    font-weight: 700;
    color: #a78bfa;
    padding: 16px 0 8px 0;
}
.sidebar-section-label {
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #4b5563;
    padding: 12px 0 4px 0;
}
</style>
""", unsafe_allow_html=True)

# ── Constants ─────────────────────────────────────────────────────────────────
DATA_FILE = "data/projects.json"
DEFAULT_SECTIONS = ["To Do", "In Progress", "Review", "Done"]
PRIORITIES = ["high", "medium", "low"]
PRIORITY_ICON = {"high": "🔴", "medium": "🟡", "low": "🟢"}
PROJECT_COLORS = [
    "#6366f1", "#8b5cf6", "#ec4899", "#f59e0b",
    "#10b981", "#3b82f6", "#ef4444", "#06b6d4",
]

# ── Data layer ────────────────────────────────────────────────────────────────
def _load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"projects": {}, "members": ["Alice", "Bob", "Charlie", "Diana"]}

def save():
    os.makedirs("data", exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(st.session_state.data, f, indent=2, ensure_ascii=False, default=str)

def gen_id():
    return str(uuid.uuid4())[:8]

def _sample_data():
    d = st.session_state.data
    today = date.today()

    def make_task(title, desc, assignee, days, priority, section, tags, done=False, comments=None):
        tid = gen_id()
        return tid, {
            "id": tid, "title": title, "description": desc,
            "assignee": assignee,
            "due_date": str(today + timedelta(days=days)) if days is not None else None,
            "priority": priority, "section": section,
            "tags": tags, "comments": comments or [],
            "completed": done, "created_at": str(datetime.now()),
        }

    p1 = gen_id()
    items = [
        make_task("Create wireframes", "Design wireframes for all main pages",
                  "Alice", 3, "high", "In Progress", ["design", "UX"],
                  False, [{"author": "Bob", "text": "Looking great!", "created_at": str(datetime.now())}]),
        make_task("Set up CI/CD pipeline", "Configure GitHub Actions for testing and deployment",
                  "Charlie", 7, "medium", "To Do", ["devops"]),
        make_task("Write API documentation", "Document all REST endpoints with examples",
                  "Diana", -1, "high", "Review", ["docs"]),
        make_task("Logo redesign", "Create new company logo in SVG format",
                  "Alice", -5, "low", "Done", ["design"], True),
    ]
    d["projects"][p1] = {
        "id": p1, "name": "Website Redesign",
        "description": "Complete overhaul of company website with new branding",
        "color": "#6366f1", "sections": DEFAULT_SECTIONS[:],
        "tasks": {tid: task for tid, task in items},
        "created_at": str(datetime.now()),
    }

    p2 = gen_id()
    items2 = [
        make_task("Draft email newsletter", "Write copy for monthly newsletter",
                  "Bob", 5, "medium", "To Do", ["marketing", "email"]),
        make_task("Schedule social posts", "Plan 30 days of social media content",
                  "Diana", 2, "high", "In Progress", ["social"]),
        make_task("Influencer outreach list", "Compile list of micro-influencers in target segment",
                  "Charlie", 10, "low", "To Do", ["marketing"]),
    ]
    d["projects"][p2] = {
        "id": p2, "name": "Q3 Marketing Campaign",
        "description": "Social media and email campaign for Q3 product launch",
        "color": "#ec4899", "sections": DEFAULT_SECTIONS[:],
        "tasks": {tid: task for tid, task in items2},
        "created_at": str(datetime.now()),
    }

    p3 = gen_id()
    items3 = [
        make_task("Migrate database to PostgreSQL", "Switch from SQLite to PG on prod server",
                  "Charlie", 14, "high", "To Do", ["backend", "db"]),
        make_task("Load testing", "Run k6 load tests targeting 10k req/s",
                  "Bob", 8, "medium", "To Do", ["devops", "testing"]),
    ]
    d["projects"][p3] = {
        "id": p3, "name": "Infrastructure Upgrade",
        "description": "Upgrade server stack and database layer",
        "color": "#10b981", "sections": DEFAULT_SECTIONS[:],
        "tasks": {tid: task for tid, task in items3},
        "created_at": str(datetime.now()),
    }
    save()

# ── Session state init ────────────────────────────────────────────────────────
if "data" not in st.session_state:
    st.session_state.data = _load_data()
    if not st.session_state.data["projects"]:
        _sample_data()

_defaults = {
    "view": "dashboard",
    "active_project": None,
    "active_task": None,
    "board_view": "board",
    "show_new_project": False,
    "show_new_task": False,
    "new_task_section": None,
    "show_task_detail": False,
    "show_delete_project": None,
}
for k, v in _defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Helpers ───────────────────────────────────────────────────────────────────
def proj(pid):
    return st.session_state.data["projects"].get(pid)

def all_tasks():
    out = []
    for pid, p in st.session_state.data["projects"].items():
        for tid, t in p["tasks"].items():
            out.append({**t, "project_id": pid,
                        "project_name": p["name"], "project_color": p["color"]})
    return out

def due_status(ds):
    if not ds:
        return None
    try:
        d = date.fromisoformat(str(ds)[:10])
        today = date.today()
        if d < today:
            return "overdue"
        if d <= today + timedelta(days=2):
            return "due-soon"
        return "ok"
    except Exception:
        return None

def fmt_date(ds):
    if not ds:
        return "—"
    try:
        return date.fromisoformat(str(ds)[:10]).strftime("%b %d")
    except Exception:
        return str(ds)

def nav(view=None, project=None, task=None, task_detail=False):
    if view is not None:
        st.session_state.view = view
    if project is not None:
        st.session_state.active_project = project
    if task is not None:
        st.session_state.active_task = task
    st.session_state.show_task_detail = task_detail
    st.session_state.show_new_task = False
    st.session_state.show_new_project = False
    st.rerun()

# ── Sidebar ───────────────────────────────────────────────────────────────────
def sidebar():
    with st.sidebar:
        st.markdown('<div class="sidebar-brand">✓ TaskFlow</div>', unsafe_allow_html=True)
        st.markdown("---")

        v = st.session_state.view
        if st.button("🏠  Dashboard", use_container_width=True,
                     type="primary" if v == "dashboard" else "secondary"):
            nav("dashboard")
        if st.button("📋  All Tasks", use_container_width=True,
                     type="primary" if v == "my_tasks" else "secondary"):
            nav("my_tasks")

        st.markdown('<div class="sidebar-section-label">Projects</div>', unsafe_allow_html=True)

        for pid, p in st.session_state.data["projects"].items():
            active = st.session_state.active_project == pid and v == "project"
            n_open = sum(1 for t in p["tasks"].values() if not t["completed"])
            label = f'<span style="color:{p["color"]}">●</span> {p["name"]} ({n_open})'
            if st.button(label, key=f"sb_{pid}", use_container_width=True,
                         type="primary" if active else "secondary"):
                nav("project", project=pid)

        st.markdown("")
        if st.button("＋  New Project", use_container_width=True):
            st.session_state.view = "new_project"
            st.rerun()

        st.markdown("---")
        st.markdown('<div class="sidebar-section-label">Team</div>', unsafe_allow_html=True)
        for m in st.session_state.data["members"]:
            st.markdown(f"<span style='color:#9ca3af;font-size:13px'>👤 {m}</span>",
                        unsafe_allow_html=True)

sidebar()

# ── Task detail ───────────────────────────────────────────────────────────────
if st.session_state.show_task_detail and st.session_state.active_task and st.session_state.active_project:
    pid = st.session_state.active_project
    tid = st.session_state.active_task
    p = proj(pid)
    if p and tid in p["tasks"]:
        task = p["tasks"][tid]

        back_col, _ = st.columns([1, 5])
        if back_col.button("← Back"):
            st.session_state.show_task_detail = False
            st.session_state.active_task = None
            st.rerun()

        st.markdown(f"## {task['title']}")
        st.markdown(f"*Project: **{p['name']}***")
        st.markdown("---")

        left, right = st.columns([3, 2])

        with left:
            with st.form("edit_task"):
                new_title = st.text_input("Title", value=task["title"])
                new_desc  = st.text_area("Description", value=task.get("description", ""), height=120)

                st.markdown("**Comments**")
                for c in task.get("comments", []):
                    ts = c.get("created_at", "")[:16]
                    st.markdown(f"**{c['author']}** · "
                                f"<span style='color:#6b7280;font-size:12px'>{ts}</span>"
                                f"<br>{c['text']}",
                                unsafe_allow_html=True)
                    st.markdown("")

                new_comment    = st.text_input("Add a comment…")
                comment_author = st.selectbox("Post as", st.session_state.data["members"])

                cs, cc = st.columns(2)
                saved   = cs.form_submit_button("Save", type="primary", use_container_width=True)
                go_back = cc.form_submit_button("Close", use_container_width=True)

                if saved:
                    task["title"]       = new_title.strip() or task["title"]
                    task["description"] = new_desc.strip()
                    if new_comment.strip():
                        task["comments"].append({
                            "author": comment_author,
                            "text":   new_comment.strip(),
                            "created_at": str(datetime.now()),
                        })
                    save()
                    st.rerun()
                if go_back:
                    st.session_state.show_task_detail = False
                    st.session_state.active_task = None
                    st.rerun()

        with right:
            st.markdown("**Details**")

            members_opts = ["(unassigned)"] + st.session_state.data["members"]
            cur_a  = task.get("assignee") or "(unassigned)"
            new_a  = st.selectbox("Assignee", members_opts,
                                  index=members_opts.index(cur_a) if cur_a in members_opts else 0)
            if new_a != cur_a:
                task["assignee"] = None if new_a == "(unassigned)" else new_a
                save(); st.rerun()

            new_pr = st.selectbox("Priority", PRIORITIES,
                                  index=PRIORITIES.index(task.get("priority", "medium")))
            if new_pr != task.get("priority"):
                task["priority"] = new_pr; save(); st.rerun()

            sec_list = p["sections"]
            cur_sec  = task.get("section", sec_list[0])
            new_sec  = st.selectbox("Section", sec_list,
                                    index=sec_list.index(cur_sec) if cur_sec in sec_list else 0)
            if new_sec != cur_sec:
                task["section"]   = new_sec
                task["completed"] = (new_sec == "Done")
                save(); st.rerun()

            cur_due = None
            if task.get("due_date"):
                try:
                    cur_due = date.fromisoformat(str(task["due_date"])[:10])
                except Exception:
                    pass
            new_due = st.date_input("Due date", value=cur_due)
            if new_due and str(new_due) != str(task.get("due_date", ""))[:10]:
                task["due_date"] = str(new_due); save(); st.rerun()

            tags_raw = st.text_input("Tags (comma-separated)",
                                     value=", ".join(task.get("tags", [])))
            new_tags = [x.strip() for x in tags_raw.split(",") if x.strip()]
            if new_tags != task.get("tags", []):
                task["tags"] = new_tags; save()

            done_toggle = st.checkbox("Mark as completed", value=task.get("completed", False))
            if done_toggle != task.get("completed", False):
                task["completed"] = done_toggle
                if done_toggle and task.get("section") != "Done":
                    task["section"] = "Done"
                save(); st.rerun()

            st.markdown("---")
            if st.button("🗑️  Delete Task", use_container_width=True):
                del p["tasks"][tid]
                save()
                st.session_state.show_task_detail = False
                st.session_state.active_task = None
                st.rerun()
    else:
        st.session_state.show_task_detail = False
        st.rerun()
    st.stop()

# ── New project form ──────────────────────────────────────────────────────────
if st.session_state.view == "new_project":
    st.markdown("## New Project")
    with st.form("new_proj_form"):
        name  = st.text_input("Project name *", placeholder="e.g. Mobile App Redesign")
        desc  = st.text_area("Description", placeholder="What is this project about?", height=80)
        color = st.selectbox("Color", PROJECT_COLORS)

        c1, c2 = st.columns(2)
        ok     = c1.form_submit_button("Create Project", type="primary", use_container_width=True)
        cancel = c2.form_submit_button("Cancel", use_container_width=True)

        if ok and name.strip():
            pid = gen_id()
            st.session_state.data["projects"][pid] = {
                "id": pid, "name": name.strip(), "description": desc.strip(),
                "color": color, "sections": DEFAULT_SECTIONS[:],
                "tasks": {}, "created_at": str(datetime.now()),
            }
            save()
            nav("project", project=pid)
        if cancel:
            nav("dashboard")
    st.stop()

# ── New task form ─────────────────────────────────────────────────────────────
def new_task_form(pid):
    p = proj(pid)
    st.markdown("### ＋ New Task")
    with st.form("new_task"):
        title = st.text_input("Title *", placeholder="What needs to be done?")
        desc  = st.text_area("Description", height=70)
        r1, r2 = st.columns(2)
        assignee = r1.selectbox("Assignee", ["(none)"] + st.session_state.data["members"])
        priority = r2.selectbox("Priority", PRIORITIES, index=1)
        r3, r4 = st.columns(2)
        default_sec = st.session_state.new_task_section or p["sections"][0]
        idx = p["sections"].index(default_sec) if default_sec in p["sections"] else 0
        section  = r3.selectbox("Section", p["sections"], index=idx)
        due_date = r4.date_input("Due date", value=None)
        tags_raw = st.text_input("Tags (comma-separated)")

        cs, cc = st.columns(2)
        ok     = cs.form_submit_button("Create Task", type="primary", use_container_width=True)
        cancel = cc.form_submit_button("Cancel", use_container_width=True)

        if ok and title.strip():
            tid = gen_id()
            p["tasks"][tid] = {
                "id": tid, "title": title.strip(), "description": desc.strip(),
                "assignee": None if assignee == "(none)" else assignee,
                "due_date": str(due_date) if due_date else None,
                "priority": priority, "section": section,
                "tags": [x.strip() for x in tags_raw.split(",") if x.strip()],
                "comments": [], "completed": False,
                "created_at": str(datetime.now()),
            }
            save()
            st.session_state.show_new_task = False
            st.session_state.new_task_section = None
            st.rerun()
        if cancel:
            st.session_state.show_new_task = False
            st.session_state.new_task_section = None
            st.rerun()

# ── Board view ────────────────────────────────────────────────────────────────
def board_view(pid):
    p = proj(pid)
    sections = p["sections"]
    tasks    = p["tasks"]
    cols = st.columns(len(sections))

    for i, sec in enumerate(sections):
        sec_tasks = [t for t in tasks.values() if t["section"] == sec]
        with cols[i]:
            st.markdown(
                f'<div class="section-col-header">{sec}'
                f' <span style="background:#374151;border-radius:10px;'
                f'padding:1px 8px;font-size:11px">{len(sec_tasks)}</span></div>',
                unsafe_allow_html=True)

            for t in sec_tasks:
                ds = due_status(t.get("due_date"))

                col_title, col_open = st.columns([5, 1])
                with col_title:
                    st.markdown(
                        f'<div class="task-card-title">'
                        f'{PRIORITY_ICON.get(t.get("priority","medium"),"")} {t["title"]}</div>',
                        unsafe_allow_html=True)
                with col_open:
                    if st.button("↗", key=f"b_open_{t['id']}"):
                        st.session_state.active_task = t["id"]
                        st.session_state.show_task_detail = True
                        st.rerun()

                meta = []
                if t.get("assignee"):
                    meta.append(f"👤 {t['assignee']}")
                if t.get("due_date"):
                    dtxt = fmt_date(t["due_date"])
                    if ds == "overdue":   meta.append(f"🔴 {dtxt}")
                    elif ds == "due-soon": meta.append(f"🟡 {dtxt}")
                    else:                  meta.append(f"📅 {dtxt}")
                if meta:
                    st.markdown(
                        f'<div class="task-card-meta">{" &nbsp;·&nbsp; ".join(meta)}</div>',
                        unsafe_allow_html=True)

                if t.get("tags"):
                    chips = "".join(f'<span class="tag-chip">{tag}</span>' for tag in t["tags"])
                    st.markdown(f'<div style="margin-top:4px">{chips}</div>', unsafe_allow_html=True)

                other = [s for s in sections if s != sec]
                if other:
                    move = st.selectbox("→", ["Move to…"] + other,
                                        key=f"mv_{t['id']}", label_visibility="collapsed")
                    if move != "Move to…":
                        tasks[t["id"]]["section"]   = move
                        tasks[t["id"]]["completed"] = (move == "Done")
                        save(); st.rerun()

                st.markdown(
                    "<hr style='border-color:#2d2d44;margin:8px 0'>", unsafe_allow_html=True)

            if st.button(f"＋ Add task", key=f"add_{sec}", use_container_width=True):
                st.session_state.new_task_section = sec
                st.session_state.show_new_task    = True
                st.rerun()

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

    h1, h2, h3, h4, h5, h6 = st.columns([4, 2, 2, 1, 2, 1])
    h1.markdown("**Title**"); h2.markdown("**Section**"); h3.markdown("**Assignee**")
    h4.markdown("**Pri**");   h5.markdown("**Due**");     h6.markdown("")
    st.markdown("---")

    for t in sorted(tasks, key=lambda x: x.get("due_date") or "9999"):
        c1, c2, c3, c4, c5, c6 = st.columns([4, 2, 2, 1, 2, 1])
        title = f"~~{t['title']}~~" if t["completed"] else t["title"]
        c1.markdown(title)
        c2.write(t.get("section", ""))
        c3.write(t.get("assignee") or "—")
        c4.write(PRIORITY_ICON.get(t.get("priority", "medium"), ""))
        ds   = due_status(t.get("due_date"))
        dtxt = fmt_date(t.get("due_date"))
        if ds == "overdue":    c5.markdown(f":red[{dtxt}]")
        elif ds == "due-soon": c5.markdown(f":orange[{dtxt}]")
        else:                  c5.write(dtxt)
        if c6.button("↗", key=f"l_open_{t['id']}"):
            st.session_state.active_task      = t["id"]
            st.session_state.show_task_detail = True
            st.rerun()

# ── Project view ──────────────────────────────────────────────────────────────
def project_view(pid):
    p = proj(pid)
    if not p:
        st.error("Project not found.")
        return

    hc1, hc2 = st.columns([4, 3])
    with hc1:
        st.markdown(
            f'<h2 style="color:{p["color"]};margin-bottom:2px">{p["name"]}</h2>'
            f'<p style="color:#6b7280;font-size:14px;margin-top:0">{p.get("description","")}</p>',
            unsafe_allow_html=True)
    with hc2:
        b1, b2, b3, b4 = st.columns(4)
        bv = st.session_state.board_view
        if b1.button("Board", type="primary" if bv == "board" else "secondary",
                     use_container_width=True):
            st.session_state.board_view = "board"; st.rerun()
        if b2.button("List", type="primary" if bv == "list" else "secondary",
                     use_container_width=True):
            st.session_state.board_view = "list"; st.rerun()
        if b3.button("＋ Task", type="primary", use_container_width=True):
            st.session_state.show_new_task = True; st.rerun()
        if b4.button("🗑️", use_container_width=True):
            st.session_state.show_delete_project = pid; st.rerun()

    if st.session_state.show_delete_project == pid:
        st.warning(f'Delete project **{p["name"]}**? This will remove all tasks.')
        dc1, dc2 = st.columns(2)
        if dc1.button("Yes, delete", type="primary", use_container_width=True):
            del st.session_state.data["projects"][pid]
            save()
            st.session_state.show_delete_project = None
            nav("dashboard")
        if dc2.button("Cancel", use_container_width=True):
            st.session_state.show_delete_project = None; st.rerun()
        st.stop()

    st.markdown("---")

    if st.session_state.show_new_task:
        new_task_form(pid)
        return

    if bv == "board":
        board_view(pid)
    else:
        list_view(pid)

# ── Dashboard ─────────────────────────────────────────────────────────────────
def dashboard():
    st.markdown("# 🏠 Dashboard")
    tasks = all_tasks()

    total     = len(tasks)
    overdue   = sum(1 for t in tasks if not t["completed"] and due_status(t.get("due_date")) == "overdue")
    in_prog   = sum(1 for t in tasks if t.get("section") == "In Progress" and not t["completed"])
    completed = sum(1 for t in tasks if t["completed"])

    st.markdown("### Overview")
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(
        f'<div class="metric-card"><p class="metric-num">{total}</p>'
        f'<p class="metric-label">Total Tasks</p></div>', unsafe_allow_html=True)
    c2.markdown(
        f'<div class="metric-card"><p class="metric-num" style="color:#f87171">{overdue}</p>'
        f'<p class="metric-label">Overdue</p></div>', unsafe_allow_html=True)
    c3.markdown(
        f'<div class="metric-card"><p class="metric-num" style="color:#60a5fa">{in_prog}</p>'
        f'<p class="metric-label">In Progress</p></div>', unsafe_allow_html=True)
    c4.markdown(
        f'<div class="metric-card"><p class="metric-num" style="color:#34d399">{completed}</p>'
        f'<p class="metric-label">Completed</p></div>', unsafe_allow_html=True)

    st.markdown("---")
    left, right = st.columns([3, 2])

    with left:
        st.markdown("### 📌 Upcoming Tasks")
        upcoming = sorted(
            [t for t in tasks if not t["completed"] and t.get("due_date")],
            key=lambda x: x.get("due_date", ""))[:12]

        if not upcoming:
            st.info("No upcoming tasks.")
        else:
            for t in upcoming:
                ds = due_status(t.get("due_date"))
                ct, cp, cd, ca = st.columns([4, 2, 2, 1])
                ct.markdown(f"**{t['title']}**  \n*{t['project_name']}*")
                cp.write(f"{PRIORITY_ICON.get(t.get('priority','medium'),'')} {t.get('priority','')}")
                dtxt = fmt_date(t.get("due_date"))
                if ds == "overdue":    cd.markdown(f":red[{dtxt}]")
                elif ds == "due-soon": cd.markdown(f":orange[{dtxt}]")
                else:                  cd.write(dtxt)
                if ca.button("↗", key=f"dash_{t['id']}"):
                    st.session_state.active_project   = t["project_id"]
                    st.session_state.active_task      = t["id"]
                    st.session_state.show_task_detail = True
                    st.rerun()
                st.divider()

    with right:
        st.markdown("### 📁 Projects")
        for pid, p in st.session_state.data["projects"].items():
            all_t  = list(p["tasks"].values())
            n_done = sum(1 for t in all_t if t["completed"])
            n_tot  = len(all_t)
            pct    = n_done / n_tot if n_tot else 0
            st.markdown(
                f'<span style="color:{p["color"]}">●</span> **{p["name"]}**',
                unsafe_allow_html=True)
            st.progress(pct, text=f"{n_done}/{n_tot} completed")
            if st.button("Open project →", key=f"dash_proj_{pid}"):
                nav("project", project=pid)
            st.markdown("")

# ── All tasks view ────────────────────────────────────────────────────────────
def my_tasks_view():
    st.markdown("# 📋 All Tasks")
    tasks = all_tasks()

    for pid, p in st.session_state.data["projects"].items():
        ptasks = [t for t in tasks if t["project_id"] == pid]
        if not ptasks:
            continue
        n_open = sum(1 for t in ptasks if not t["completed"])
        st.markdown(
            f'<span style="color:{p["color"]}">●</span> **{p["name"]}** '
            f'<span style="color:#6b7280;font-size:13px">({n_open} open)</span>',
            unsafe_allow_html=True)

        for t in sorted(ptasks, key=lambda x: x.get("due_date") or "9999"):
            c1, c2, c3, c4, c5 = st.columns([4, 2, 2, 2, 1])
            chk = c1.checkbox(t["title"], value=t["completed"], key=f"chk_{t['id']}")
            if chk != t["completed"]:
                st.session_state.data["projects"][pid]["tasks"][t["id"]]["completed"] = chk
                if chk:
                    st.session_state.data["projects"][pid]["tasks"][t["id"]]["section"] = "Done"
                save(); st.rerun()
            c2.write(t.get("section", ""))
            c3.write(t.get("assignee") or "—")
            ds   = due_status(t.get("due_date"))
            dtxt = fmt_date(t.get("due_date"))
            if ds == "overdue":    c4.markdown(f":red[{dtxt}]")
            elif ds == "due-soon": c4.markdown(f":orange[{dtxt}]")
            else:                  c4.write(dtxt)
            if c5.button("↗", key=f"my_{t['id']}"):
                st.session_state.active_project   = pid
                st.session_state.active_task      = t["id"]
                st.session_state.show_task_detail = True
                st.rerun()
        st.markdown("")

# ── Router ────────────────────────────────────────────────────────────────────
v = st.session_state.view

if v == "dashboard":
    dashboard()
elif v == "my_tasks":
    my_tasks_view()
elif v == "project" and st.session_state.active_project:
    project_view(st.session_state.active_project)
else:
    dashboard()
