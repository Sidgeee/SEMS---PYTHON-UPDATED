"""
SEMS - School Event Management System
College of St. Catherine - Quezon City
Python + SQLite + Tkinter Desktop Application
Modes: Admin | Teacher | Student
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import sqlite3
import hashlib
import os
from datetime import datetime

# ─────────────────────────────────────────────
# DATABASE SETUP
# ─────────────────────────────────────────────
DB_FILE = "sems.db"

def get_conn():
    return sqlite3.connect(DB_FILE)

def init_db():
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            full_name TEXT,
            student_id TEXT,
            course TEXT,
            year TEXT,
            section TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            venue TEXT,
            date TEXT,
            proposed_by TEXT,
            category TEXT,
            virtual_link TEXT,
            description TEXT,
            target_audience TEXT,
            equipment TEXT,
            status TEXT DEFAULT 'Pending',
            created_by TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS logistics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id INTEGER,
            time TEXT,
            speakers TEXT,
            agendas TEXT,
            supplies TEXT,
            resources TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id INTEGER,
            student_id TEXT,
            full_name TEXT,
            program TEXT,
            waiver INTEGER DEFAULT 0,
            fee_paid INTEGER DEFAULT 0,
            clearance INTEGER DEFAULT 0,
            status TEXT DEFAULT 'Advance Reserved',
            proof TEXT,
            signature TEXT,
            registered_by TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS announcements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT,
            posted_at TEXT,
            posted_by TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS feedbacks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_username TEXT,
            event_id INTEGER,
            rating INTEGER,
            comments TEXT
        )
    """)

    # Seed default accounts
    def seed_user(username, password, role, full_name, sid="N/A", course="", year="", section=""):
        hashed = hashlib.sha256(password.encode()).hexdigest()
        try:
            c.execute("INSERT INTO users (username,password,role,full_name,student_id,course,year,section) VALUES (?,?,?,?,?,?,?,?)",
                      (username, hashed, role, full_name, sid, course, year, section))
        except sqlite3.IntegrityError:
            pass

    seed_user("admin", "admin123", "Admin", "System Administrator")
    seed_user("teacher", "teacher123", "Teacher", "Ms. Santos")

    conn.commit()
    conn.close()

def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

# ─────────────────────────────────────────────
# COLORS & STYLES
# ─────────────────────────────────────────────
BG_DARK    = "#0f172a"
BG_CARD    = "#1e293b"
BG_SIDEBAR = "#1a2236"
ACCENT     = "#22c55e"
ACCENT2    = "#38bdf8"
ACCENT_AMB = "#f59e0b"
DANGER     = "#ef4444"
TEXT_PRI   = "#f1f5f9"
TEXT_SEC   = "#94a3b8"
BORDER     = "#334155"
BTN_PRI    = "#2563eb"
BTN_SUC    = "#16a34a"
BTN_DNG    = "#dc2626"
BTN_SEC    = "#475569"
CARD2      = "#263045"

FONT_TITLE  = ("Segoe UI", 15, "bold")
FONT_HEAD   = ("Segoe UI", 11, "bold")
FONT_BODY   = ("Segoe UI", 10)
FONT_SMALL  = ("Segoe UI", 9)
FONT_TINY   = ("Segoe UI", 8)

# ─────────────────────────────────────────────
# HELPER WIDGETS
# ─────────────────────────────────────────────
def styled_btn(parent, text, cmd, color=BTN_PRI, fg=TEXT_PRI, pad=(14,8)):
    b = tk.Button(parent, text=text, command=cmd,
                  bg=color, fg=fg, font=FONT_BODY, relief="flat",
                  padx=pad[0], pady=pad[1], cursor="hand2",
                  activebackground=color, activeforeground=fg)
    return b

def label(parent, text, font=FONT_BODY, fg=TEXT_PRI, bg=None, **kw):
    if bg is None:
        bg = parent.cget("bg") if hasattr(parent, "cget") else BG_CARD
    return tk.Label(parent, text=text, font=font, fg=fg, bg=bg, **kw)

def entry(parent, width=30, show=None):
    e = tk.Entry(parent, width=width, bg=CARD2, fg=TEXT_PRI,
                 insertbackground=TEXT_PRI, relief="flat",
                 font=FONT_BODY, highlightthickness=1,
                 highlightbackground=BORDER, highlightcolor=ACCENT2)
    if show:
        e.config(show=show)
    return e

def combo(parent, values, width=28):
    c = ttk.Combobox(parent, values=values, width=width, font=FONT_BODY, state="readonly")
    c.configure(background=CARD2)
    return c

def textarea(parent, rows=4, width=40):
    t = tk.Text(parent, height=rows, width=width, bg=CARD2, fg=TEXT_PRI,
                insertbackground=TEXT_PRI, relief="flat", font=FONT_BODY,
                highlightthickness=1, highlightbackground=BORDER, highlightcolor=ACCENT2)
    return t

def scrolltree(parent, cols, heights=12):
    frame = tk.Frame(parent, bg=BG_CARD)
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Custom.Treeview",
        background=BG_CARD, foreground=TEXT_PRI,
        fieldbackground=BG_CARD, borderwidth=0,
        rowheight=26, font=FONT_SMALL)
    style.configure("Custom.Treeview.Heading",
        background=BG_SIDEBAR, foreground=ACCENT2,
        font=("Segoe UI", 9, "bold"), relief="flat")
    style.map("Custom.Treeview", background=[("selected", "#1d4ed8")])

    tv = ttk.Treeview(frame, columns=cols, show="headings",
                      height=heights, style="Custom.Treeview")
    for col in cols:
        tv.heading(col, text=col)
        tv.column(col, width=100, anchor="w")
    vsb = ttk.Scrollbar(frame, orient="vertical", command=tv.yview)
    hsb = ttk.Scrollbar(frame, orient="horizontal", command=tv.xview)
    tv.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
    tv.grid(row=0, column=0, sticky="nsew")
    vsb.grid(row=0, column=1, sticky="ns")
    hsb.grid(row=1, column=0, sticky="ew")
    frame.rowconfigure(0, weight=1)
    frame.columnconfigure(0, weight=1)
    return frame, tv

def section_title(parent, text, bg=BG_CARD):
    f = tk.Frame(parent, bg=BORDER, height=1)
    f.pack(fill="x", pady=(12,4))
    label(parent, text, font=("Segoe UI", 9, "bold"), fg=ACCENT2, bg=bg).pack(anchor="w", padx=2)

def card(parent, **kwargs):
    f = tk.Frame(parent, bg=BG_CARD, bd=0, highlightthickness=1,
                 highlightbackground=BORDER, **kwargs)
    return f

# ─────────────────────────────────────────────
# LOGIN / REGISTER WINDOW
# ─────────────────────────────────────────────
class AuthWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("SEMS - School Event Management System")
        self.root.configure(bg=BG_DARK)
        self.root.geometry("900x600")
        self.root.resizable(False, False)
        self._build()

    def _build(self):
        outer = tk.Frame(self.root, bg=BG_DARK)
        outer.pack(fill="both", expand=True, padx=30, pady=30)

        # Left banner
        left = tk.Frame(outer, bg="#14532d", width=380)
        left.pack(side="left", fill="both")
        left.pack_propagate(False)
        self._build_banner(left)

        # Right form
        right = tk.Frame(outer, bg=BG_CARD, width=380)
        right.pack(side="right", fill="both", expand=True)
        right.pack_propagate(False)

        self.form_frame = right
        self._show_login()

    def _build_banner(self, parent):
        try:
            from PIL import Image, ImageTk
            img = Image.open("cscqclogo.png").resize((80,80), Image.LANCZOS)
            self._logo = ImageTk.PhotoImage(img)
            tk.Label(parent, image=self._logo, bg="#14532d").pack(pady=(30,5))
        except Exception:
            tk.Label(parent, text="🎓", font=("Segoe UI",40), bg="#14532d", fg="white").pack(pady=(30,5))

        label(parent, "SEMS", font=("Segoe UI",22,"bold"), fg="white", bg="#14532d").pack()
        label(parent, "School Event Management", font=FONT_BODY, fg="#bbf7d0", bg="#14532d").pack()

        tk.Frame(parent, bg="#22c55e", height=2).pack(fill="x", padx=20, pady=12)

        label(parent, "Manage. Organize. Execute.", font=("Segoe UI",11,"bold"), fg="white", bg="#14532d").pack(padx=20)
        label(parent, "Your complete event management\nworkspace for College of St. Catherine\n— from proposals to post-event analytics.",
              font=FONT_SMALL, fg="#bbf7d0", bg="#14532d", justify="center").pack(padx=20, pady=8)

        for pill in ["📅 Event Scheduling", "👥 Attendance Tracking", "📊 Analytics"]:
            f = tk.Frame(parent, bg="#166534", bd=0)
            f.pack(pady=3)
            label(f, pill, font=FONT_SMALL, fg="#4ade80", bg="#166534").pack(padx=10, pady=3)

        tk.Frame(parent, bg="#22c55e", height=2).pack(fill="x", padx=20, pady=12)
        label(parent, "College of St. Catherine", font=("Segoe UI",9,"bold"), fg="white", bg="#14532d").pack()
        label(parent, "Quezon City", font=FONT_TINY, fg="#bbf7d0", bg="#14532d").pack()

    def _clear_form(self):
        for w in self.form_frame.winfo_children():
            w.destroy()

    def _show_login(self):
        self._clear_form()
        p = self.form_frame
        label(p, "System Sign In", font=FONT_TITLE, bg=BG_CARD).pack(pady=(30,4))
        label(p, "Enter your authorization credentials below", font=FONT_SMALL, fg=TEXT_SEC, bg=BG_CARD).pack()

        f = tk.Frame(p, bg=BG_CARD)
        f.pack(padx=30, pady=20, fill="x")

        label(f, "👤 Username", bg=BG_CARD).pack(anchor="w")
        self.login_user = entry(f, width=32)
        self.login_user.pack(fill="x", pady=(2,10))

        label(f, "🔒 Password", bg=BG_CARD).pack(anchor="w")
        self.login_pass = entry(f, width=32, show="•")
        self.login_pass.pack(fill="x", pady=(2,10))

        styled_btn(p, "Log In to Workspace", self._do_login, color=BTN_PRI).pack(padx=30, pady=4, fill="x")

        sep = tk.Frame(p, bg=BG_CARD); sep.pack(pady=8)
        label(sep, "New student? ", font=FONT_SMALL, fg=TEXT_SEC, bg=BG_CARD).pack(side="left")
        lnk = label(sep, "Create an Account Here", font=FONT_SMALL, fg=ACCENT2, bg=BG_CARD, cursor="hand2")
        lnk.pack(side="left")
        lnk.bind("<Button-1>", lambda e: self._show_register())

        label(p, "─── Default Credentials ───", font=FONT_TINY, fg=BORDER, bg=BG_CARD).pack(pady=(10,2))
        label(p, "Admin: admin / admin123\nTeacher: teacher / teacher123", font=FONT_TINY, fg=TEXT_SEC, bg=BG_CARD).pack()

        self.login_user.bind("<Return>", lambda e: self._do_login())
        self.login_pass.bind("<Return>", lambda e: self._do_login())

    def _do_login(self):
        u = self.login_user.get().strip()
        pw = self.login_pass.get().strip()
        if not u or not pw:
            messagebox.showerror("Error", "Please fill in all fields.")
            return
        conn = get_conn()
        row = conn.execute("SELECT * FROM users WHERE username=? AND password=?",
                           (u, hash_pw(pw))).fetchone()
        conn.close()
        if row:
            self.root.destroy()
            launch_workspace(row)
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")

    def _show_register(self):
        self._clear_form()
        p = self.form_frame
        label(p, "Student Registration", font=FONT_TITLE, bg=BG_CARD).pack(pady=(20,2))
        label(p, "Register your profile into the database", font=FONT_SMALL, fg=TEXT_SEC, bg=BG_CARD).pack()

        canvas = tk.Canvas(p, bg=BG_CARD, highlightthickness=0)
        sb = ttk.Scrollbar(p, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        canvas.pack(fill="both", expand=True)
        f = tk.Frame(canvas, bg=BG_CARD)
        canvas.create_window((0,0), window=f, anchor="nw")
        f.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        def row2(parent, l1, w1, l2, w2):
            r = tk.Frame(parent, bg=BG_CARD); r.pack(fill="x", padx=20, pady=2)
            c1 = tk.Frame(r, bg=BG_CARD); c1.pack(side="left", expand=True, fill="x", padx=(0,5))
            c2 = tk.Frame(r, bg=BG_CARD); c2.pack(side="left", expand=True, fill="x")
            label(c1, l1, font=FONT_SMALL, bg=BG_CARD).pack(anchor="w")
            w1.pack = w1.pack  # already configured
            w1['master'] = c1
            w1.pack(fill="x")
            label(c2, l2, font=FONT_SMALL, bg=BG_CARD).pack(anchor="w")
            w2['master'] = c2
            w2.pack(fill="x")

        # Name row
        nr = tk.Frame(f, bg=BG_CARD); nr.pack(fill="x", padx=20, pady=4)
        for lbl, w in [("Surname", 14), ("First Name", 14), ("M.I.", 4)]:
            c = tk.Frame(nr, bg=BG_CARD); c.pack(side="left", fill="x", expand=True, padx=2)
            label(c, lbl, font=FONT_SMALL, bg=BG_CARD).pack(anchor="w")
            e = entry(c, width=w); e.pack(fill="x")
            setattr(self, f"reg_{lbl.lower().replace(' ','_').replace('.','')}", e)

        # Course / Year / Section
        cr = tk.Frame(f, bg=BG_CARD); cr.pack(fill="x", padx=20, pady=4)
        for lbl, attr, vals in [
            ("Course","reg_course",["BSIT","BSTM","BSBA","BSCRIM","BSE-ENG","BSE-SOCSCI","BEED","CPE"]),
            ("Year","reg_year",["1st Year","2nd Year","3rd Year","4th Year","CPE"]),
        ]:
            c = tk.Frame(cr, bg=BG_CARD); c.pack(side="left", fill="x", expand=True, padx=2)
            label(c, lbl, font=FONT_SMALL, bg=BG_CARD).pack(anchor="w")
            cb = combo(c, vals, width=12); cb.pack(fill="x"); cb.current(0)
            setattr(self, attr, cb)
        c = tk.Frame(cr, bg=BG_CARD); c.pack(side="left", fill="x", expand=True, padx=2)
        label(c, "Section", font=FONT_SMALL, bg=BG_CARD).pack(anchor="w")
        self.reg_section = entry(c, width=8); self.reg_section.pack(fill="x")

        for lbl_text, attr in [("Student ID (N/A if none)", "reg_sid"),
                                ("Desired Username", "reg_username")]:
            tk.Frame(f, bg=BORDER, height=1).pack(fill="x", padx=20, pady=2)
            label(f, lbl_text, font=FONT_SMALL, bg=BG_CARD).pack(anchor="w", padx=20)
            e = entry(f, width=36); e.pack(padx=20, fill="x", pady=2)
            setattr(self, attr, e)

        label(f, "Choose Password", font=FONT_SMALL, bg=BG_CARD).pack(anchor="w", padx=20)
        self.reg_password = entry(f, width=36, show="•"); self.reg_password.pack(padx=20, fill="x", pady=2)

        styled_btn(f, "Register Student Profile", self._do_register, color=BTN_SUC).pack(padx=20, pady=8, fill="x")

        sep = tk.Frame(f, bg=BG_CARD); sep.pack(pady=4)
        label(sep, "Already have an account? ", font=FONT_SMALL, fg=TEXT_SEC, bg=BG_CARD).pack(side="left")
        lnk = label(sep, "Return to Login", font=FONT_SMALL, fg=ACCENT2, bg=BG_CARD, cursor="hand2")
        lnk.pack(side="left")
        lnk.bind("<Button-1>", lambda e: self._show_login())

    def _do_register(self):
        sn = self.reg_surname.get().strip()
        fn = self.reg_first_name.get().strip()
        mi = self.reg_mi.get().strip()
        course = self.reg_course.get()
        year = self.reg_year.get()
        sec = self.reg_section.get().strip()
        sid = self.reg_sid.get().strip()
        uname = self.reg_username.get().strip()
        pw = self.reg_password.get().strip()

        if not all([sn, fn, course, year, sec, sid, uname, pw]):
            messagebox.showerror("Error", "Please fill in all required fields.")
            return
        full_name = f"{sn}, {fn} {mi}".strip(", ")
        conn = get_conn()
        try:
            conn.execute(
                "INSERT INTO users (username,password,role,full_name,student_id,course,year,section) VALUES (?,?,?,?,?,?,?,?)",
                (uname, hash_pw(pw), "Student", full_name, sid, course, year, sec)
            )
            conn.commit()
            messagebox.showinfo("Success", f"Account created for {full_name}!\nYou can now log in.")
            self._show_login()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Username already exists. Choose another.")
        finally:
            conn.close()


# ─────────────────────────────────────────────
# MAIN WORKSPACE
# ─────────────────────────────────────────────
class WorkspaceWindow:
    def __init__(self, root, user_row):
        self.root = root
        self.user = {
            "id": user_row[0], "username": user_row[1],
            "role": user_row[3], "full_name": user_row[4],
            "student_id": user_row[5], "course": user_row[6],
            "year": user_row[7], "section": user_row[8]
        }
        self.root.title(f"SEMS — {self.user['role']} Workspace")
        self.root.configure(bg=BG_DARK)
        self.root.geometry("1280x800")
        self.root.state("zoomed")
        self.current_view = None
        self._build()
        self._nav_to("dashboard")

    def _build(self):
        outer = tk.Frame(self.root, bg=BG_DARK)
        outer.pack(fill="both", expand=True)

        # Sidebar
        self.sidebar = tk.Frame(outer, bg=BG_SIDEBAR, width=210)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        self._build_sidebar()

        # Main content
        self.content = tk.Frame(outer, bg=BG_DARK)
        self.content.pack(side="right", fill="both", expand=True)
        self._build_topbar()

        self.viewport = tk.Frame(self.content, bg=BG_DARK)
        self.viewport.pack(fill="both", expand=True, padx=14, pady=10)

    def _build_sidebar(self):
        # Header
        hdr = tk.Frame(self.sidebar, bg="#0f2a1a", pady=14)
        hdr.pack(fill="x")
        label(hdr, "🛡 SEMS", font=("Segoe UI",14,"bold"), fg=ACCENT, bg="#0f2a1a").pack()
        label(hdr, self.user["role"], font=FONT_SMALL, fg=ACCENT2, bg="#0f2a1a").pack()

        tk.Frame(self.sidebar, bg=BORDER, height=1).pack(fill="x")

        # Nav items per role
        role = self.user["role"]
        nav_items = []
        if role == "Admin":
            nav_items = [
                ("📊", "Dashboard", "dashboard"),
                ("📅", "Events Ledger", "events"),
                ("📋", "Logistics", "logistics"),
                ("✅", "Attendance", "attendance"),
                ("📢", "Announcements", "announcements"),
                ("💬", "Feedbacks", "feedbacks"),
                ("👥", "User Management", "users"),
            ]
        elif role == "Teacher":
            nav_items = [
                ("📊", "Dashboard", "dashboard"),
                ("📅", "Propose Event", "events"),
                ("📋", "Logistics", "logistics"),
                ("✅", "Attendance", "attendance"),
                ("📢", "Announcements", "announcements"),
                ("💬", "Feedbacks", "feedbacks"),
            ]
        else:  # Student
            nav_items = [
                ("📊", "Dashboard", "dashboard"),
                ("📅", "View Events", "student_events"),
                ("✅", "Self Check-in", "self_checkin"),
                ("💬", "Submit Feedback", "feedback_form"),
                ("📢", "Announcements", "announcements"),
            ]

        self.nav_btns = {}
        for icon, text, key in nav_items:
            f = tk.Frame(self.sidebar, bg=BG_SIDEBAR, cursor="hand2")
            f.pack(fill="x")
            inner = tk.Frame(f, bg=BG_SIDEBAR, pady=10, padx=14)
            inner.pack(fill="x")
            lbl = tk.Label(inner, text=f"  {icon}  {text}", font=FONT_BODY,
                           fg=TEXT_SEC, bg=BG_SIDEBAR, anchor="w")
            lbl.pack(fill="x")
            for w in [f, inner, lbl]:
                w.bind("<Button-1>", lambda e, k=key: self._nav_to(k))
                w.bind("<Enter>", lambda e, w=f, il=inner, ll=lbl: [w.config(bg=CARD2), il.config(bg=CARD2), ll.config(bg=CARD2, fg=TEXT_PRI)])
                w.bind("<Leave>", lambda e, k2=key, ww=f, il=inner, ll=lbl: self._restore_nav_style(k2, ww, il, ll))
            self.nav_btns[key] = (f, inner, lbl)

        # Footer
        tk.Frame(self.sidebar, bg=BORDER, height=1).pack(fill="x", side="bottom", pady=0)
        foot = tk.Frame(self.sidebar, bg=BG_SIDEBAR, pady=10)
        foot.pack(side="bottom", fill="x")
        label(foot, f"👤 {self.user['full_name']}", font=FONT_SMALL, fg=TEXT_PRI, bg=BG_SIDEBAR).pack(padx=10, anchor="w")
        label(foot, self.user["username"], font=FONT_TINY, fg=TEXT_SEC, bg=BG_SIDEBAR).pack(padx=10, anchor="w")
        styled_btn(foot, "⏻ Exit Session", self._logout, color=BTN_DNG, pad=(10,6)).pack(padx=10, pady=6, fill="x")

    def _restore_nav_style(self, key, f, inner, lbl):
        if self.current_view == key:
            f.config(bg="#1d3a28"); inner.config(bg="#1d3a28"); lbl.config(bg="#1d3a28", fg=ACCENT)
        else:
            f.config(bg=BG_SIDEBAR); inner.config(bg=BG_SIDEBAR); lbl.config(bg=BG_SIDEBAR, fg=TEXT_SEC)

    def _build_topbar(self):
        bar = tk.Frame(self.content, bg=BG_CARD, height=52, bd=0,
                       highlightthickness=1, highlightbackground=BORDER)
        bar.pack(fill="x")
        bar.pack_propagate(False)

        self.view_title_lbl = label(bar, "Dashboard", font=FONT_TITLE, fg=TEXT_PRI, bg=BG_CARD)
        self.view_title_lbl.pack(side="left", padx=18, pady=8)

        time_pill = tk.Frame(bar, bg=CARD2, bd=0)
        time_pill.pack(side="right", padx=14, pady=10)
        self.time_lbl = label(time_pill, "", font=FONT_SMALL, fg=ACCENT2, bg=CARD2)
        self.time_lbl.pack(padx=10, pady=4)
        self._tick()

        styled_btn(bar, "🔄 Refresh", self._refresh_view, color=BTN_SEC, pad=(10,5)).pack(side="right", padx=4, pady=10)

    def _tick(self):
        self.time_lbl.config(text=datetime.now().strftime("📅 %A, %B %d %Y  %I:%M:%S %p"))
        self.root.after(1000, self._tick)

    def _nav_to(self, key):
        prev = self.current_view
        self.current_view = key

        # Update sidebar highlight
        for k, (f, inner, lbl) in self.nav_btns.items():
            if k == key:
                f.config(bg="#1d3a28"); inner.config(bg="#1d3a28"); lbl.config(bg="#1d3a28", fg=ACCENT)
            else:
                f.config(bg=BG_SIDEBAR); inner.config(bg=BG_SIDEBAR); lbl.config(bg=BG_SIDEBAR, fg=TEXT_SEC)

        for w in self.viewport.winfo_children():
            w.destroy()

        titles = {
            "dashboard": "Dashboard Overview",
            "events": "Events Ledger",
            "logistics": "Event Logistics Blueprint",
            "attendance": "Attendance Registrar",
            "announcements": "Campus Announcements",
            "feedbacks": "Feedback Reports",
            "users": "User Management",
            "student_events": "Active Events",
            "self_checkin": "Self Check-in",
            "feedback_form": "Submit Feedback",
        }
        self.view_title_lbl.config(text=titles.get(key, key.title()))

        views = {
            "dashboard": self._view_dashboard,
            "events": self._view_events,
            "logistics": self._view_logistics,
            "attendance": self._view_attendance,
            "announcements": self._view_announcements,
            "feedbacks": self._view_feedbacks,
            "users": self._view_users,
            "student_events": self._view_student_events,
            "self_checkin": self._view_self_checkin,
            "feedback_form": self._view_feedback_form,
        }
        if key in views:
            views[key](self.viewport)

    def _refresh_view(self):
        self._nav_to(self.current_view)

    def _logout(self):
        if messagebox.askyesno("Exit", "Exit current session?"):
            self.root.destroy()
            start_app()

    # ─────────────────────────────────────────
    # DASHBOARD VIEW
    # ─────────────────────────────────────────
    def _view_dashboard(self, parent):
        conn = get_conn()
        total_events   = conn.execute("SELECT COUNT(*) FROM events WHERE status='Approved'").fetchone()[0]
        pending        = conn.execute("SELECT COUNT(*) FROM events WHERE status='Pending'").fetchone()[0]
        total_att      = conn.execute("SELECT COUNT(*) FROM attendance").fetchone()[0]
        checked_in     = conn.execute("SELECT COUNT(*) FROM attendance WHERE status='Checked In'").fetchone()[0]
        rate           = f"{round(checked_in/total_att*100)}%" if total_att else "0%"
        announcements  = conn.execute("SELECT title, posted_at FROM announcements ORDER BY id DESC LIMIT 5").fetchall()
        events         = conn.execute("SELECT title, venue, date FROM events WHERE status='Approved' ORDER BY date LIMIT 3").fetchall()
        conn.close()

        # Metric cards
        metrics = [
            ("Active/Approved Events", str(total_events), "📅", "#1d4ed8"),
            ("Pending Proposals",      str(pending),       "⏳", "#92400e"),
            ("Total Registrants",      str(total_att),     "👥", "#14532d"),
            ("Attendance Rate",        rate,               "📊", "#134e4a"),
        ]
        mf = tk.Frame(parent, bg=BG_DARK)
        mf.pack(fill="x", pady=(0,10))
        for i, (lbl_text, val, icon, bg) in enumerate(metrics):
            c = tk.Frame(mf, bg=bg, bd=0, highlightthickness=1, highlightbackground=BORDER)
            c.grid(row=0, column=i, padx=6, pady=4, sticky="ew")
            mf.columnconfigure(i, weight=1)
            tk.Label(c, text=icon, font=("Segoe UI",24), bg=bg, fg="white").pack(side="right", padx=14, pady=10)
            left = tk.Frame(c, bg=bg); left.pack(side="left", padx=14, pady=10)
            tk.Label(left, text=val, font=("Segoe UI",22,"bold"), fg="white", bg=bg).pack(anchor="w")
            tk.Label(left, text=lbl_text, font=FONT_SMALL, fg="#cbd5e1", bg=bg).pack(anchor="w")

        # Bottom split
        bf = tk.Frame(parent, bg=BG_DARK)
        bf.pack(fill="both", expand=True)
        bf.columnconfigure(0, weight=2)
        bf.columnconfigure(1, weight=1)

        # Featured events
        ec = card(bf); ec.grid(row=0, column=0, padx=(0,8), sticky="nsew")
        label(ec, "⭐ Featured Upcoming Events", font=FONT_HEAD, fg=ACCENT2, bg=BG_CARD).pack(anchor="w", padx=14, pady=(10,4))
        tk.Frame(ec, bg=BORDER, height=1).pack(fill="x")
        if events:
            for title, venue, date in events:
                ef = tk.Frame(ec, bg=CARD2); ef.pack(fill="x", padx=10, pady=4)
                label(ef, f"📅 {title}", font=("Segoe UI",10,"bold"), fg=TEXT_PRI, bg=CARD2).pack(anchor="w", padx=8, pady=(6,2))
                label(ef, f"📍 {venue}   🗓 {date}", font=FONT_SMALL, fg=TEXT_SEC, bg=CARD2).pack(anchor="w", padx=8, pady=(0,6))
        else:
            label(ec, "No approved events yet.", font=FONT_SMALL, fg=TEXT_SEC, bg=BG_CARD).pack(pady=20)

        # Announcements
        ac = card(bf); ac.grid(row=0, column=1, sticky="nsew")
        label(ac, "📢 Campus Bulletins", font=FONT_HEAD, fg=ACCENT2, bg=BG_CARD).pack(anchor="w", padx=14, pady=(10,4))
        tk.Frame(ac, bg=BORDER, height=1).pack(fill="x")
        if announcements:
            for t, ts in announcements:
                af = tk.Frame(ac, bg=CARD2); af.pack(fill="x", padx=10, pady=4)
                label(af, f"• {t}", font=FONT_SMALL, fg=TEXT_PRI, bg=CARD2, wraplength=220, justify="left").pack(anchor="w", padx=8, pady=(6,2))
                label(af, ts[:16] if ts else "", font=FONT_TINY, fg=TEXT_SEC, bg=CARD2).pack(anchor="w", padx=8, pady=(0,6))
        else:
            label(ac, "No bulletins yet.", font=FONT_SMALL, fg=TEXT_SEC, bg=BG_CARD).pack(pady=20)

    # ─────────────────────────────────────────
    # EVENTS VIEW
    # ─────────────────────────────────────────
    def _view_events(self, parent):
        role = self.user["role"]
        pane = tk.PanedWindow(parent, orient="horizontal", bg=BG_DARK, sashwidth=6)
        pane.pack(fill="both", expand=True)

        # Left: table
        lf = card(pane); pane.add(lf, minsize=450)
        label(lf, "📋 Events Ledger", font=FONT_HEAD, fg=ACCENT2, bg=BG_CARD).pack(anchor="w", padx=12, pady=(10,4))
        tk.Frame(lf, bg=BORDER, height=1).pack(fill="x")

        cols = ["ID","Title","Venue","Date","Proposed By","Status"]
        tf, self.events_tree = scrolltree(lf, cols, heights=18)
        tf.pack(fill="both", expand=True, padx=6, pady=6)
        self._load_events_table()
        self.events_tree.bind("<<TreeviewSelect>>", self._on_event_select)

        # Right: form
        rf = card(pane); pane.add(rf, minsize=380)
        self.evt_form_title = label(rf, "📅 Event Configuration", font=FONT_HEAD, fg=ACCENT2, bg=BG_CARD)
        self.evt_form_title.pack(anchor="w", padx=12, pady=(10,4))
        tk.Frame(rf, bg=BORDER, height=1).pack(fill="x")

        canvas = tk.Canvas(rf, bg=BG_CARD, highlightthickness=0)
        sb = ttk.Scrollbar(rf, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        canvas.pack(fill="both", expand=True)
        ff = tk.Frame(canvas, bg=BG_CARD)
        canvas.create_window((0,0), window=ff, anchor="nw")
        ff.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        def lbl(text, bg=BG_CARD): return label(ff, text, font=FONT_SMALL, bg=bg)

        lbl("Event Title *").pack(anchor="w", padx=12, pady=(8,1))
        self.evt_title = entry(ff, width=42); self.evt_title.pack(padx=12, fill="x")

        r2 = tk.Frame(ff, bg=BG_CARD); r2.pack(fill="x", padx=12, pady=4)
        c1 = tk.Frame(r2, bg=BG_CARD); c1.pack(side="left", fill="x", expand=True, padx=(0,4))
        c2 = tk.Frame(r2, bg=BG_CARD); c2.pack(side="right", fill="x", expand=True)
        label(c1, "Venue *", font=FONT_SMALL, bg=BG_CARD).pack(anchor="w")
        self.evt_venue = entry(c1, width=18); self.evt_venue.pack(fill="x")
        label(c2, "Date * (YYYY-MM-DD)", font=FONT_SMALL, bg=BG_CARD).pack(anchor="w")
        self.evt_date = entry(c2, width=18); self.evt_date.pack(fill="x")

        lbl("Proposed By *").pack(anchor="w", padx=12, pady=(6,1))
        self.evt_proposed = entry(ff, width=42); self.evt_proposed.pack(padx=12, fill="x")

        r3 = tk.Frame(ff, bg=BG_CARD); r3.pack(fill="x", padx=12, pady=4)
        cc1 = tk.Frame(r3, bg=BG_CARD); cc1.pack(side="left", fill="x", expand=True, padx=(0,4))
        cc2 = tk.Frame(r3, bg=BG_CARD); cc2.pack(side="right", fill="x", expand=True)
        label(cc1, "Category *", font=FONT_SMALL, bg=BG_CARD).pack(anchor="w")
        self.evt_category = combo(cc1, ["Seminar","Sports","Cultural","Academic","Webinar"], width=14)
        self.evt_category.pack(fill="x")
        label(cc2, "Virtual Link (optional)", font=FONT_SMALL, bg=BG_CARD).pack(anchor="w")
        self.evt_vlink = entry(cc2, width=18); self.evt_vlink.pack(fill="x")

        lbl("Description *").pack(anchor="w", padx=12, pady=(6,1))
        self.evt_desc = textarea(ff, rows=3, width=42); self.evt_desc.pack(padx=12, fill="x")

        section_title(ff, "🎯 Target Audience", bg=BG_CARD)
        self.aud_vars = {}
        af = tk.Frame(ff, bg=BG_CARD); af.pack(padx=12, fill="x")
        for i, dept in enumerate(["BSIT","BSTM","BSBA","BSCRIM","EDUC"]):
            v = tk.IntVar()
            tk.Checkbutton(af, text=dept, variable=v, bg=BG_CARD, fg=TEXT_PRI,
                           selectcolor=CARD2, activebackground=BG_CARD, font=FONT_SMALL).grid(row=0, column=i, padx=4)
            self.aud_vars[dept] = v

        section_title(ff, "🔧 Equipment", bg=BG_CARD)
        self.equip_vars = {}
        ef = tk.Frame(ff, bg=BG_CARD); ef.pack(padx=12, fill="x")
        for i, eq in enumerate(["Sound System","HD Projector","Wireless Mics","Chairs"]):
            v = tk.IntVar()
            tk.Checkbutton(ef, text=eq, variable=v, bg=BG_CARD, fg=TEXT_PRI,
                           selectcolor=CARD2, activebackground=BG_CARD, font=FONT_SMALL).grid(row=0, column=i, padx=4)
            self.equip_vars[eq] = v

        self.evt_editing_id = None
        btf = tk.Frame(ff, bg=BG_CARD); btf.pack(padx=12, pady=10, fill="x")
        styled_btn(btf, "💾 Save Event", self._save_event, color=BTN_PRI).pack(fill="x", pady=2)
        self.btn_cancel_evt = styled_btn(btf, "✖ Cancel Edit", self._cancel_evt_edit, color=BTN_SEC)
        self.btn_cancel_evt.pack(fill="x", pady=2)
        self.btn_cancel_evt.pack_forget()

        # Admin approval dock
        if role == "Admin":
            dock = tk.Frame(ff, bg=BG_CARD); dock.pack(padx=12, pady=4, fill="x")
            tk.Frame(dock, bg=BORDER, height=1).pack(fill="x", pady=4)
            label(dock, "⚠ Admin Overrides", font=FONT_SMALL, fg=ACCENT_AMB, bg=BG_CARD).pack(anchor="w")
            brow = tk.Frame(dock, bg=BG_CARD); brow.pack(fill="x", pady=4)
            styled_btn(brow, "✔ Approve", self._approve_event, color=BTN_SUC, pad=(10,6)).pack(side="left", padx=(0,6))
            styled_btn(brow, "✘ Deny", self._deny_event, color=BTN_DNG, pad=(10,6)).pack(side="left")

    def _load_events_table(self):
        t = self.events_tree
        for row in t.get_children(): t.delete(row)
        conn = get_conn()
        rows = conn.execute("SELECT id,title,venue,date,proposed_by,status FROM events ORDER BY id DESC").fetchall()
        conn.close()
        for r in rows:
            tag = "approved" if r[5]=="Approved" else ("denied" if r[5]=="Denied" else "")
            t.insert("", "end", values=r, tags=(tag,))
        t.tag_configure("approved", foreground="#4ade80")
        t.tag_configure("denied", foreground="#f87171")

    def _on_event_select(self, event):
        sel = self.events_tree.selection()
        if not sel: return
        vals = self.events_tree.item(sel[0])["values"]
        eid = vals[0]
        conn = get_conn()
        row = conn.execute("SELECT * FROM events WHERE id=?", (eid,)).fetchone()
        conn.close()
        if not row: return
        self.evt_editing_id = eid
        self.evt_title.delete(0,"end"); self.evt_title.insert(0, row[1] or "")
        self.evt_venue.delete(0,"end"); self.evt_venue.insert(0, row[2] or "")
        self.evt_date.delete(0,"end"); self.evt_date.insert(0, row[3] or "")
        self.evt_proposed.delete(0,"end"); self.evt_proposed.insert(0, row[4] or "")
        if row[5] in ["Seminar","Sports","Cultural","Academic","Webinar"]:
            self.evt_category.set(row[5])
        self.evt_vlink.delete(0,"end"); self.evt_vlink.insert(0, row[6] or "")
        self.evt_desc.delete("1.0","end"); self.evt_desc.insert("1.0", row[7] or "")
        aud = (row[8] or "").split(",")
        for dept, v in self.aud_vars.items(): v.set(1 if dept in aud else 0)
        equip = (row[9] or "").split(",")
        for eq, v in self.equip_vars.items(): v.set(1 if eq in equip else 0)
        self.btn_cancel_evt.pack(fill="x", pady=2)
        self.evt_form_title.config(text="✏ Edit Event")

    def _save_event(self):
        title = self.evt_title.get().strip()
        venue = self.evt_venue.get().strip()
        date  = self.evt_date.get().strip()
        prop  = self.evt_proposed.get().strip()
        cat   = self.evt_category.get()
        vlink = self.evt_vlink.get().strip()
        desc  = self.evt_desc.get("1.0","end").strip()
        aud   = ",".join(k for k,v in self.aud_vars.items() if v.get())
        equip = ",".join(k for k,v in self.equip_vars.items() if v.get())
        role  = self.user["role"]

        if not all([title, venue, date, prop, cat, desc]):
            messagebox.showerror("Error", "Please fill in all required fields.")
            return

        status = "Approved" if role == "Admin" else "Pending"
        conn = get_conn()
        if self.evt_editing_id:
            conn.execute("""UPDATE events SET title=?,venue=?,date=?,proposed_by=?,
                category=?,virtual_link=?,description=?,target_audience=?,equipment=?
                WHERE id=?""",
                (title,venue,date,prop,cat,vlink,desc,aud,equip,self.evt_editing_id))
            msg = "Event updated."
        else:
            conn.execute("""INSERT INTO events (title,venue,date,proposed_by,category,virtual_link,
                description,target_audience,equipment,status,created_by) VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                (title,venue,date,prop,cat,vlink,desc,aud,equip,status,self.user["username"]))
            msg = f"Event saved! Status: {status}"
        conn.commit(); conn.close()
        messagebox.showinfo("Success", msg)
        self._cancel_evt_edit()
        self._load_events_table()

    def _cancel_evt_edit(self):
        self.evt_editing_id = None
        self.evt_title.delete(0,"end"); self.evt_venue.delete(0,"end")
        self.evt_date.delete(0,"end"); self.evt_proposed.delete(0,"end")
        self.evt_vlink.delete(0,"end"); self.evt_desc.delete("1.0","end")
        for v in self.aud_vars.values(): v.set(0)
        for v in self.equip_vars.values(): v.set(0)
        self.btn_cancel_evt.pack_forget()
        self.evt_form_title.config(text="📅 Event Configuration")

    def _approve_event(self):
        sel = self.events_tree.selection()
        if not sel: return messagebox.showwarning("Select Event", "Please select an event first.")
        eid = self.events_tree.item(sel[0])["values"][0]
        conn = get_conn()
        conn.execute("UPDATE events SET status='Approved' WHERE id=?", (eid,))
        conn.commit(); conn.close()
        messagebox.showinfo("Approved", "Event approved!")
        self._load_events_table()

    def _deny_event(self):
        sel = self.events_tree.selection()
        if not sel: return messagebox.showwarning("Select Event", "Please select an event first.")
        eid = self.events_tree.item(sel[0])["values"][0]
        conn = get_conn()
        conn.execute("UPDATE events SET status='Denied' WHERE id=?", (eid,))
        conn.commit(); conn.close()
        messagebox.showinfo("Denied", "Event denied.")
        self._load_events_table()

    # ─────────────────────────────────────────
    # LOGISTICS VIEW
    # ─────────────────────────────────────────
    def _view_logistics(self, parent):
        cf = card(parent); cf.pack(fill="both", expand=True)
        label(cf, "📋 Event Logistics Blueprint", font=FONT_HEAD, fg=ACCENT2, bg=BG_CARD).pack(anchor="w", padx=14, pady=(10,4))
        tk.Frame(cf, bg=BORDER, height=1).pack(fill="x")

        body = tk.Frame(cf, bg=BG_CARD); body.pack(padx=20, pady=14, fill="both")

        label(body, "Select Approved Event *", bg=BG_CARD).pack(anchor="w")
        conn = get_conn()
        evts = conn.execute("SELECT id, title FROM events WHERE status='Approved'").fetchall()
        conn.close()
        evt_map = {f"[{r[0]}] {r[1]}": r[0] for r in evts}
        self.log_evt_cb = combo(body, list(evt_map.keys()), width=50)
        self.log_evt_cb.pack(anchor="w", pady=(2,10))

        r2 = tk.Frame(body, bg=BG_CARD); r2.pack(fill="x", pady=4)
        c1 = tk.Frame(r2, bg=BG_CARD); c1.pack(side="left", fill="x", expand=True, padx=(0,8))
        c2 = tk.Frame(r2, bg=BG_CARD); c2.pack(side="right", fill="x", expand=True)
        label(c1, "Start Time", bg=BG_CARD).pack(anchor="w")
        self.log_time = entry(c1, width=20); self.log_time.pack(fill="x")
        label(c2, "Keynote Speakers", bg=BG_CARD).pack(anchor="w")
        self.log_speakers = entry(c2, width=20); self.log_speakers.pack(fill="x")

        label(body, "Agenda Sequence", bg=BG_CARD).pack(anchor="w", pady=(8,2))
        self.log_agendas = textarea(body, rows=4, width=60); self.log_agendas.pack(fill="x")

        r3 = tk.Frame(body, bg=BG_CARD); r3.pack(fill="x", pady=4)
        c3 = tk.Frame(r3, bg=BG_CARD); c3.pack(side="left", fill="x", expand=True, padx=(0,8))
        c4 = tk.Frame(r3, bg=BG_CARD); c4.pack(side="right", fill="x", expand=True)
        label(c3, "Supplies / Equipment", bg=BG_CARD).pack(anchor="w")
        self.log_supplies = entry(c3, width=20); self.log_supplies.pack(fill="x")
        label(c4, "AV/IT Resources", bg=BG_CARD).pack(anchor="w")
        self.log_resources = entry(c4, width=20); self.log_resources.pack(fill="x")

        styled_btn(body, "💾 Commit Logistics", lambda: self._save_logistics(evt_map), color=BTN_PRI).pack(pady=12)

        # Display existing
        section_title(body, "📊 Saved Logistics Records", bg=BG_CARD)
        cols = ["Log ID","Event ID","Time","Speakers","Supplies","Resources"]
        tf, self.log_tree = scrolltree(body, cols, heights=8)
        tf.pack(fill="both", expand=True)
        self._load_logistics_table()

    def _save_logistics(self, evt_map):
        sel = self.log_evt_cb.get()
        if not sel: return messagebox.showerror("Error", "Select an event first.")
        eid = evt_map.get(sel)
        conn = get_conn()
        conn.execute("INSERT INTO logistics (event_id,time,speakers,agendas,supplies,resources) VALUES (?,?,?,?,?,?)",
            (eid, self.log_time.get(), self.log_speakers.get(),
             self.log_agendas.get("1.0","end").strip(),
             self.log_supplies.get(), self.log_resources.get()))
        conn.commit(); conn.close()
        messagebox.showinfo("Saved", "Logistics committed.")
        self._load_logistics_table()

    def _load_logistics_table(self):
        t = self.log_tree
        for r in t.get_children(): t.delete(r)
        conn = get_conn()
        rows = conn.execute("SELECT id,event_id,time,speakers,supplies,resources FROM logistics ORDER BY id DESC").fetchall()
        conn.close()
        for r in rows: t.insert("","end",values=r)

    # ─────────────────────────────────────────
    # ATTENDANCE VIEW
    # ─────────────────────────────────────────
    def _view_attendance(self, parent):
        pane = tk.PanedWindow(parent, orient="horizontal", bg=BG_DARK, sashwidth=6)
        pane.pack(fill="both", expand=True)

        # Table
        lf = card(pane); pane.add(lf, minsize=500)
        label(lf, "✅ Attendance Registrar", font=FONT_HEAD, fg=ACCENT2, bg=BG_CARD).pack(anchor="w", padx=12, pady=(10,4))
        tk.Frame(lf, bg=BORDER, height=1).pack(fill="x")
        cols = ["ID","Event","Name","Course","Status","Waiver","Fee","Clearance"]
        tf, self.att_tree = scrolltree(lf, cols, heights=20)
        tf.pack(fill="both", expand=True, padx=6, pady=6)
        self._load_att_table()
        self.att_tree.bind("<<TreeviewSelect>>", self._on_att_select)

        # Form
        rf = card(pane); pane.add(rf, minsize=320)
        label(rf, "➕ Manual Registrar", font=FONT_HEAD, fg=ACCENT2, bg=BG_CARD).pack(anchor="w", padx=12, pady=(10,4))
        tk.Frame(rf, bg=BORDER, height=1).pack(fill="x")

        ff = tk.Frame(rf, bg=BG_CARD); ff.pack(padx=14, pady=10, fill="both")

        label(ff, "Event *", bg=BG_CARD).pack(anchor="w")
        conn = get_conn()
        evts = conn.execute("SELECT id,title FROM events WHERE status='Approved'").fetchall()
        conn.close()
        self.att_evt_map = {f"[{r[0]}] {r[1]}": r[0] for r in evts}
        self.att_evt_cb = combo(ff, list(self.att_evt_map.keys()), width=34)
        self.att_evt_cb.pack(fill="x", pady=(2,6))

        for lbl_text, attr in [("Student ID *","att_sid"), ("Full Name *","att_name"), ("Course/Section *","att_program")]:
            label(ff, lbl_text, bg=BG_CARD).pack(anchor="w")
            e = entry(ff, width=36); e.pack(fill="x", pady=(2,6))
            setattr(self, attr, e)

        label(ff, "Compliance", font=FONT_SMALL, fg=TEXT_SEC, bg=BG_CARD).pack(anchor="w", pady=(4,2))
        cf = tk.Frame(ff, bg=BG_CARD); cf.pack(fill="x", pady=2)
        self.att_waiver = tk.IntVar()
        self.att_fee    = tk.IntVar()
        self.att_clear  = tk.IntVar()
        for text, var in [("Waiver",self.att_waiver),("Fee Paid",self.att_fee),("ID Checked",self.att_clear)]:
            tk.Checkbutton(cf, text=text, variable=var, bg=BG_CARD, fg=TEXT_PRI,
                           selectcolor=CARD2, font=FONT_SMALL).pack(side="left", padx=4)

        label(ff, "Status *", bg=BG_CARD).pack(anchor="w", pady=(6,1))
        self.att_status = combo(ff, ["Advance Reserved","Checked In"], width=30)
        self.att_status.current(0)
        self.att_status.pack(fill="x")

        self.att_editing_id = None
        btf = tk.Frame(ff, bg=BG_CARD); btf.pack(fill="x", pady=8)
        styled_btn(btf, "✔ Save Registrar Row", self._save_attendance, color=BTN_SUC).pack(fill="x", pady=2)
        self.btn_cancel_att = styled_btn(btf, "✖ Cancel", self._cancel_att_edit, color=BTN_SEC)
        self.btn_cancel_att.pack(fill="x", pady=2)
        self.btn_cancel_att.pack_forget()

        if self.user["role"] == "Admin":
            tk.Frame(ff, bg=BORDER, height=1).pack(fill="x", pady=6)
            styled_btn(ff, "🗑 Delete Selected", self._delete_att, color=BTN_DNG).pack(fill="x", pady=2)

    def _load_att_table(self):
        t = self.att_tree
        for r in t.get_children(): t.delete(r)
        conn = get_conn()
        rows = conn.execute("""
            SELECT a.id, e.title, a.full_name, a.program, a.status, 
                   a.waiver, a.fee_paid, a.clearance
            FROM attendance a LEFT JOIN events e ON a.event_id=e.id
            ORDER BY a.id DESC
        """).fetchall()
        conn.close()
        for r in rows:
            display = list(r)
            display[5] = "✔" if r[5] else "✘"
            display[6] = "✔" if r[6] else "✘"
            display[7] = "✔" if r[7] else "✘"
            t.insert("","end",values=display)

    def _on_att_select(self, event):
        sel = self.att_tree.selection()
        if not sel: return
        aid = self.att_tree.item(sel[0])["values"][0]
        conn = get_conn()
        row = conn.execute("SELECT * FROM attendance WHERE id=?", (aid,)).fetchone()
        conn.close()
        if not row: return
        self.att_editing_id = aid
        self.att_sid.delete(0,"end"); self.att_sid.insert(0, row[2] or "")
        self.att_name.delete(0,"end"); self.att_name.insert(0, row[3] or "")
        self.att_program.delete(0,"end"); self.att_program.insert(0, row[4] or "")
        self.att_waiver.set(row[5]); self.att_fee.set(row[6]); self.att_clear.set(row[7])
        self.att_status.set(row[8] or "Advance Reserved")
        self.btn_cancel_att.pack(fill="x", pady=2)

    def _save_attendance(self):
        evt_sel = self.att_evt_cb.get()
        if not evt_sel: return messagebox.showerror("Error","Select event.")
        eid = self.att_evt_map.get(evt_sel)
        sid = self.att_sid.get().strip()
        name = self.att_name.get().strip()
        prog = self.att_program.get().strip()
        if not all([sid, name, prog]): return messagebox.showerror("Error","Fill all fields.")
        conn = get_conn()
        if self.att_editing_id:
            conn.execute("""UPDATE attendance SET student_id=?,full_name=?,program=?,
                waiver=?,fee_paid=?,clearance=?,status=? WHERE id=?""",
                (sid,name,prog,self.att_waiver.get(),self.att_fee.get(),
                 self.att_clear.get(),self.att_status.get(),self.att_editing_id))
        else:
            conn.execute("""INSERT INTO attendance (event_id,student_id,full_name,program,
                waiver,fee_paid,clearance,status,registered_by) VALUES (?,?,?,?,?,?,?,?,?)""",
                (eid,sid,name,prog,self.att_waiver.get(),self.att_fee.get(),
                 self.att_clear.get(),self.att_status.get(),self.user["username"]))
        conn.commit(); conn.close()
        messagebox.showinfo("Saved","Attendance record saved.")
        self._cancel_att_edit()
        self._load_att_table()

    def _cancel_att_edit(self):
        self.att_editing_id = None
        self.att_sid.delete(0,"end"); self.att_name.delete(0,"end"); self.att_program.delete(0,"end")
        self.att_waiver.set(0); self.att_fee.set(0); self.att_clear.set(0)
        self.btn_cancel_att.pack_forget()

    def _delete_att(self):
        sel = self.att_tree.selection()
        if not sel: return messagebox.showwarning("Select","Select a row first.")
        aid = self.att_tree.item(sel[0])["values"][0]
        if messagebox.askyesno("Confirm","Delete this attendance record?"):
            conn = get_conn()
            conn.execute("DELETE FROM attendance WHERE id=?", (aid,))
            conn.commit(); conn.close()
            self._load_att_table()

    # ─────────────────────────────────────────
    # ANNOUNCEMENTS VIEW
    # ─────────────────────────────────────────
    def _view_announcements(self, parent):
        pane = tk.PanedWindow(parent, orient="horizontal", bg=BG_DARK, sashwidth=6)
        pane.pack(fill="both", expand=True)

        # Table
        lf = card(pane); pane.add(lf, minsize=480)
        label(lf, "📢 Announcements Board", font=FONT_HEAD, fg=ACCENT2, bg=BG_CARD).pack(anchor="w", padx=12, pady=(10,4))
        tk.Frame(lf, bg=BORDER, height=1).pack(fill="x")
        cols = ["ID","Title","Posted At","Posted By"]
        tf, self.ann_tree = scrolltree(lf, cols, heights=10)
        tf.pack(fill="x", padx=6, pady=6)
        self.ann_tree.bind("<<TreeviewSelect>>", self._on_ann_select)

        # Content display
        self.ann_content_display = scrolledtext.ScrolledText(lf, height=8, bg=CARD2, fg=TEXT_PRI,
            font=FONT_BODY, relief="flat", state="disabled")
        self.ann_content_display.pack(fill="x", padx=6, pady=(0,6))
        self._load_ann_table()

        role = self.user["role"]
        if role in ("Admin", "Teacher"):
            rf = card(pane); pane.add(rf, minsize=300)
            label(rf, "📡 Dispatch Bulletin", font=FONT_HEAD, fg=ACCENT2, bg=BG_CARD).pack(anchor="w", padx=12, pady=(10,4))
            tk.Frame(rf, bg=BORDER, height=1).pack(fill="x")
            ff = tk.Frame(rf, bg=BG_CARD); ff.pack(padx=14, pady=10, fill="x")
            label(ff, "Title *", bg=BG_CARD).pack(anchor="w")
            self.ann_title = entry(ff, width=36); self.ann_title.pack(fill="x", pady=(2,6))
            label(ff, "Content *", bg=BG_CARD).pack(anchor="w")
            self.ann_content = textarea(ff, rows=8, width=36); self.ann_content.pack(fill="x")
            self.ann_editing_id = None
            btf = tk.Frame(ff, bg=BG_CARD); btf.pack(fill="x", pady=8)
            styled_btn(btf, "📤 Push Live Notice", self._save_ann, color=BTN_PRI).pack(fill="x", pady=2)
            self.btn_cancel_ann = styled_btn(btf, "✖ Cancel", self._cancel_ann_edit, color=BTN_SEC)
            self.btn_cancel_ann.pack(fill="x", pady=2); self.btn_cancel_ann.pack_forget()
            if role == "Admin":
                styled_btn(ff, "🗑 Delete Selected", self._delete_ann, color=BTN_DNG).pack(fill="x", pady=2)

    def _load_ann_table(self):
        t = self.ann_tree
        for r in t.get_children(): t.delete(r)
        conn = get_conn()
        rows = conn.execute("SELECT id,title,posted_at,posted_by FROM announcements ORDER BY id DESC").fetchall()
        conn.close()
        for r in rows: t.insert("","end",values=r)

    def _on_ann_select(self, event):
        sel = self.ann_tree.selection()
        if not sel: return
        aid = self.ann_tree.item(sel[0])["values"][0]
        conn = get_conn()
        row = conn.execute("SELECT * FROM announcements WHERE id=?", (aid,)).fetchone()
        conn.close()
        if not row: return
        self.ann_content_display.configure(state="normal")
        self.ann_content_display.delete("1.0","end")
        self.ann_content_display.insert("1.0", row[2] or "")
        self.ann_content_display.configure(state="disabled")
        if hasattr(self, "ann_editing_id"):
            self.ann_editing_id = aid
            self.ann_title.delete(0,"end"); self.ann_title.insert(0, row[1] or "")
            self.ann_content.delete("1.0","end"); self.ann_content.insert("1.0", row[2] or "")
            self.btn_cancel_ann.pack(fill="x", pady=2)

    def _save_ann(self):
        title = self.ann_title.get().strip()
        content = self.ann_content.get("1.0","end").strip()
        if not title or not content: return messagebox.showerror("Error","Fill all fields.")
        ts = datetime.now().strftime("%Y-%m-%d %H:%M")
        conn = get_conn()
        if self.ann_editing_id:
            conn.execute("UPDATE announcements SET title=?,content=?,posted_at=? WHERE id=?",
                         (title, content, ts, self.ann_editing_id))
        else:
            conn.execute("INSERT INTO announcements (title,content,posted_at,posted_by) VALUES (?,?,?,?)",
                         (title, content, ts, self.user["username"]))
        conn.commit(); conn.close()
        messagebox.showinfo("Posted","Bulletin dispatched.")
        self._cancel_ann_edit()
        self._load_ann_table()

    def _cancel_ann_edit(self):
        self.ann_editing_id = None
        self.ann_title.delete(0,"end"); self.ann_content.delete("1.0","end")
        self.btn_cancel_ann.pack_forget()

    def _delete_ann(self):
        sel = self.ann_tree.selection()
        if not sel: return messagebox.showwarning("Select","Select an announcement.")
        aid = self.ann_tree.item(sel[0])["values"][0]
        if messagebox.askyesno("Confirm","Delete this announcement?"):
            conn = get_conn()
            conn.execute("DELETE FROM announcements WHERE id=?", (aid,))
            conn.commit(); conn.close()
            self._load_ann_table()

    # ─────────────────────────────────────────
    # FEEDBACKS VIEW
    # ─────────────────────────────────────────
    def _view_feedbacks(self, parent):
        cf = card(parent); cf.pack(fill="both", expand=True)
        label(cf, "💬 Feedback Reports", font=FONT_HEAD, fg=ACCENT2, bg=BG_CARD).pack(anchor="w", padx=12, pady=(10,4))
        tk.Frame(cf, bg=BORDER, height=1).pack(fill="x")
        cols = ["ID","Student","Event","Rating","Comments"]
        tf, self.fb_tree = scrolltree(cf, cols, heights=20)
        tf.pack(fill="both", expand=True, padx=6, pady=6)
        self._load_feedbacks_table()

    def _load_feedbacks_table(self):
        t = self.fb_tree
        for r in t.get_children(): t.delete(r)
        conn = get_conn()
        rows = conn.execute("""
            SELECT f.id, f.student_username, e.title, f.rating, f.comments
            FROM feedbacks f LEFT JOIN events e ON f.event_id=e.id
            ORDER BY f.id DESC
        """).fetchall()
        conn.close()
        stars = {5:"⭐⭐⭐⭐⭐", 4:"⭐⭐⭐⭐", 3:"⭐⭐⭐", 2:"⭐⭐", 1:"⭐"}
        for r in rows:
            display = list(r)
            display[3] = stars.get(r[3], str(r[3]))
            t.insert("","end",values=display)

    # ─────────────────────────────────────────
    # USER MANAGEMENT (Admin only)
    # ─────────────────────────────────────────
    def _view_users(self, parent):
        cf = card(parent); cf.pack(fill="both", expand=True)
        label(cf, "👥 User Management", font=FONT_HEAD, fg=ACCENT2, bg=BG_CARD).pack(anchor="w", padx=12, pady=(10,4))
        tk.Frame(cf, bg=BORDER, height=1).pack(fill="x")

        cols = ["ID","Username","Role","Full Name","Student ID","Course","Year","Section"]
        tf, self.usr_tree = scrolltree(cf, cols, heights=18)
        tf.pack(fill="both", expand=True, padx=6, pady=6)
        self._load_users_table()

        btf = tk.Frame(cf, bg=BG_CARD); btf.pack(padx=12, pady=8, fill="x")
        styled_btn(btf, "🗑 Delete Selected User", self._delete_user, color=BTN_DNG).pack(side="left", padx=4)
        styled_btn(btf, "🔄 Refresh", self._load_users_table, color=BTN_SEC).pack(side="left", padx=4)

    def _load_users_table(self, *args):
        t = self.usr_tree
        for r in t.get_children(): t.delete(r)
        conn = get_conn()
        rows = conn.execute("SELECT id,username,role,full_name,student_id,course,year,section FROM users ORDER BY role,username").fetchall()
        conn.close()
        for r in rows: t.insert("","end",values=r)

    def _delete_user(self):
        sel = self.usr_tree.selection()
        if not sel: return messagebox.showwarning("Select","Select a user first.")
        uid = self.usr_tree.item(sel[0])["values"][0]
        uname = self.usr_tree.item(sel[0])["values"][1]
        if uname == self.user["username"]:
            return messagebox.showerror("Error","Cannot delete your own account.")
        if messagebox.askyesno("Confirm",f"Delete user '{uname}'?"):
            conn = get_conn()
            conn.execute("DELETE FROM users WHERE id=?", (uid,))
            conn.commit(); conn.close()
            self._load_users_table()

    # ─────────────────────────────────────────
    # STUDENT — VIEW EVENTS
    # ─────────────────────────────────────────
    def _view_student_events(self, parent):
        cf = card(parent); cf.pack(fill="both", expand=True)
        label(cf, "📅 Active Approved Events", font=FONT_HEAD, fg=ACCENT2, bg=BG_CARD).pack(anchor="w", padx=12, pady=(10,4))
        tk.Frame(cf, bg=BORDER, height=1).pack(fill="x")
        cols = ["ID","Title","Venue","Date","Category","Proposed By"]
        tf, tv = scrolltree(cf, cols, heights=20)
        tf.pack(fill="both", expand=True, padx=6, pady=6)
        conn = get_conn()
        rows = conn.execute("SELECT id,title,venue,date,category,proposed_by FROM events WHERE status='Approved' ORDER BY date").fetchall()
        conn.close()
        for r in rows: tv.insert("","end",values=r)

    # ─────────────────────────────────────────
    # STUDENT — SELF CHECK-IN
    # ─────────────────────────────────────────
    def _view_self_checkin(self, parent):
        pane = tk.PanedWindow(parent, orient="horizontal", bg=BG_DARK, sashwidth=6)
        pane.pack(fill="both", expand=True)

        lf = card(pane); pane.add(lf, minsize=440)
        label(lf, "📋 Available Events", font=FONT_HEAD, fg=ACCENT2, bg=BG_CARD).pack(anchor="w", padx=12, pady=(10,4))
        tk.Frame(lf, bg=BORDER, height=1).pack(fill="x")
        cols = ["ID","Title","Venue","Date"]
        tf, self.ci_tree = scrolltree(lf, cols, heights=18)
        tf.pack(fill="both", expand=True, padx=6, pady=6)
        conn = get_conn()
        rows = conn.execute("SELECT id,title,venue,date FROM events WHERE status='Approved' ORDER BY date").fetchall()
        conn.close()
        for r in rows: self.ci_tree.insert("","end",values=r)
        self.ci_tree.bind("<<TreeviewSelect>>", self._on_ci_select)

        rf = card(pane); pane.add(rf, minsize=320)
        label(rf, "✅ Self Verification", font=FONT_HEAD, fg=ACCENT2, bg=BG_CARD).pack(anchor="w", padx=12, pady=(10,4))
        tk.Frame(rf, bg=BORDER, height=1).pack(fill="x")

        self.ci_info_lbl = label(rf, "Select an event to check in", font=FONT_BODY, fg=TEXT_SEC, bg=BG_CARD)
        self.ci_info_lbl.pack(pady=20)

        self.ci_form = tk.Frame(rf, bg=BG_CARD)
        ff = self.ci_form; ff.pack(padx=14, fill="x")
        label(ff, "Payment Proof / URL *", bg=BG_CARD).pack(anchor="w")
        self.ci_proof = entry(ff, width=36); self.ci_proof.pack(fill="x", pady=(2,6))
        label(ff, "E-Signature (Full Name) *", bg=BG_CARD).pack(anchor="w")
        self.ci_sig = entry(ff, width=36); self.ci_sig.pack(fill="x", pady=(2,6))
        styled_btn(ff, "⚡ Submit Attendance", self._do_checkin, color=BTN_SUC).pack(fill="x", pady=6)
        self.ci_form.pack_forget()
        self.ci_selected_eid = None

    def _on_ci_select(self, event):
        sel = self.ci_tree.selection()
        if not sel: return
        vals = self.ci_tree.item(sel[0])["values"]
        self.ci_selected_eid = vals[0]
        self.ci_info_lbl.config(text=f"📅 {vals[1]}\n📍 {vals[2]}  🗓 {vals[3]}", fg=ACCENT2)
        self.ci_form.pack(padx=14, fill="x")

    def _do_checkin(self):
        if not self.ci_selected_eid: return
        proof = self.ci_proof.get().strip()
        sig   = self.ci_sig.get().strip()
        if not proof or not sig: return messagebox.showerror("Error","Fill all fields.")
        u = self.user
        name = u["full_name"]
        prog = f"{u['course']} {u['year']} - {u['section']}"
        conn = get_conn()
        # Check if already registered
        existing = conn.execute("SELECT id FROM attendance WHERE event_id=? AND student_id=?",
                                (self.ci_selected_eid, u["student_id"])).fetchone()
        if existing:
            conn.close()
            return messagebox.showwarning("Already Registered","You are already checked in for this event.")
        conn.execute("""INSERT INTO attendance (event_id,student_id,full_name,program,
            waiver,fee_paid,clearance,status,proof,signature,registered_by)
            VALUES (?,?,?,?,0,0,0,'Advance Reserved',?,?,?)""",
            (self.ci_selected_eid, u["student_id"], name, prog, proof, sig, u["username"]))
        conn.commit(); conn.close()
        messagebox.showinfo("Success","Attendance entry submitted! Awaiting admin verification.")
        self.ci_proof.delete(0,"end"); self.ci_sig.delete(0,"end")

    # ─────────────────────────────────────────
    # STUDENT — FEEDBACK FORM
    # ─────────────────────────────────────────
    def _view_feedback_form(self, parent):
        cf = card(parent); cf.pack(fill="both", expand=True)
        label(cf, "💬 Quality Evaluation Submission", font=FONT_HEAD, fg=ACCENT2, bg=BG_CARD).pack(anchor="w", padx=12, pady=(10,4))
        tk.Frame(cf, bg=BORDER, height=1).pack(fill="x")

        ff = tk.Frame(cf, bg=BG_CARD); ff.pack(padx=30, pady=16, fill="x")

        r2 = tk.Frame(ff, bg=BG_CARD); r2.pack(fill="x")
        c1 = tk.Frame(r2, bg=BG_CARD); c1.pack(side="left", fill="x", expand=True, padx=(0,10))
        c2 = tk.Frame(r2, bg=BG_CARD); c2.pack(side="right", fill="x", expand=True)

        label(c1, "Select Event *", bg=BG_CARD).pack(anchor="w")
        conn = get_conn()
        evts = conn.execute("SELECT id,title FROM events WHERE status='Approved'").fetchall()
        conn.close()
        self.fb_evt_map = {f"[{r[0]}] {r[1]}": r[0] for r in evts}
        self.fb_evt_cb = combo(c1, list(self.fb_evt_map.keys()), width=30)
        self.fb_evt_cb.pack(fill="x", pady=(2,6))

        label(c2, "Rating *", bg=BG_CARD).pack(anchor="w")
        self.fb_rating = combo(c2, [
            "⭐⭐⭐⭐⭐ 5 - Highly Exceptional",
            "⭐⭐⭐⭐ 4 - Good Quality",
            "⭐⭐⭐ 3 - Satisfactory",
            "⭐⭐ 2 - Needs Revision",
            "⭐ 1 - Critical Failure"
        ], width=30)
        self.fb_rating.current(0)
        self.fb_rating.pack(fill="x", pady=(2,6))

        label(ff, "Comments / Suggestions *", bg=BG_CARD).pack(anchor="w", pady=(8,2))
        self.fb_comments = textarea(ff, rows=6, width=60); self.fb_comments.pack(fill="x")
        styled_btn(ff, "📤 Submit Evaluation", self._submit_feedback, color=BTN_SUC).pack(pady=12)

        # View own feedbacks
        tk.Frame(ff, bg=BORDER, height=1).pack(fill="x", pady=8)
        label(ff, "Your Previous Feedbacks", font=FONT_SMALL, fg=TEXT_SEC, bg=BG_CARD).pack(anchor="w")
        cols = ["ID","Event","Rating","Comments"]
        tf, tv = scrolltree(ff, cols, heights=6)
        tf.pack(fill="x", pady=6)
        conn = get_conn()
        rows = conn.execute("""
            SELECT f.id, e.title, f.rating, f.comments
            FROM feedbacks f LEFT JOIN events e ON f.event_id=e.id
            WHERE f.student_username=? ORDER BY f.id DESC
        """, (self.user["username"],)).fetchall()
        conn.close()
        stars = {5:"⭐⭐⭐⭐⭐", 4:"⭐⭐⭐⭐", 3:"⭐⭐⭐", 2:"⭐⭐", 1:"⭐"}
        for r in rows:
            d = list(r); d[2] = stars.get(r[2], str(r[2]))
            tv.insert("","end",values=d)

    def _submit_feedback(self):
        sel = self.fb_evt_cb.get()
        if not sel: return messagebox.showerror("Error","Select an event.")
        eid = self.fb_evt_map.get(sel)
        rating_str = self.fb_rating.get()
        rating = int(rating_str[rating_str.index(" ")+1]) if " " in rating_str else 5
        # Parse rating number from string like "⭐⭐⭐⭐⭐ 5 - ..."
        for i in range(1,6):
            if str(i) in rating_str[:12]:
                rating = i; break
        comments = self.fb_comments.get("1.0","end").strip()
        if not comments: return messagebox.showerror("Error","Please enter comments.")
        conn = get_conn()
        conn.execute("INSERT INTO feedbacks (student_username,event_id,rating,comments) VALUES (?,?,?,?)",
                     (self.user["username"], eid, rating, comments))
        conn.commit(); conn.close()
        messagebox.showinfo("Submitted","Feedback submitted. Thank you!")
        self.fb_comments.delete("1.0","end")
        self._nav_to("feedback_form")


# ─────────────────────────────────────────────
# APP ENTRY
# ─────────────────────────────────────────────
def launch_workspace(user_row):
    root = tk.Tk()
    WorkspaceWindow(root, user_row)
    root.mainloop()

def start_app():
    init_db()
    root = tk.Tk()
    AuthWindow(root)
    root.mainloop()

if __name__ == "__main__":
    start_app()