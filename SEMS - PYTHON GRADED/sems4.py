"""
=================================================================
SEMS - School Event Management System (DESKTOP EDITION)
Converted from the original SEMS web app (HTML/CSS/JS) into a
standalone Python desktop application.

Stack:
    - GUI:      Tkinter / ttk
    - Database: SQLite3 (file: sems_database.db, auto-created)

College of St. Catherine - Quezon City
=================================================================
"""

import os
import sys
import sqlite3
from datetime import datetime

import tkinter as tk
from tkinter import ttk, messagebox


# =================================================================
# 0. PATHS / CONSTANTS
# =================================================================

def resource_dir():
    """Folder the script/exe lives in (works for PyInstaller --onefile too)."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


DB_PATH = os.path.join(resource_dir(), "sems_database.db")
DB_VERSION = "2026.3"

COURSES = ["BSIT", "BSTM", "BSBA", "BSCRIM", "BSE-ENG", "BSE-SOCSCI", "BEED", "CPE"]
YEARS = ["1st Year", "2nd Year", "3rd Year", "4th Year", "CPE"]
CATEGORIES = ["Seminar", "Sports", "Cultural", "Academic", "Webinar"]
AUDIENCES = ["BSIT", "BSTM", "BSBA", "BSCRIM", "EDUC"]
EQUIPMENT = ["sound", "projector", "mics", "chairs"]
EQUIPMENT_LABELS = {"sound": "Sound System", "projector": "HD Projector",
                     "mics": "Wireless Mics", "chairs": "Chairs"}
ATTENDANCE_STATUSES = ["Advance Reserved", "Checked In", "Absent", "Cancelled"]


# =================================================================
# 1. THEME (mirrors the green/gold CSCQC branding from style.css)
# =================================================================

COLOR_BG = "#0f1b13"
COLOR_SIDEBAR = "#123322"
COLOR_SIDEBAR_ACTIVE = "#1e8449"
COLOR_PRIMARY = "#1e8449"
COLOR_PRIMARY_DARK = "#145a32"
COLOR_ACCENT = "#f1c40f"
COLOR_CARD = "#ffffff"
COLOR_CARD_ALT = "#f4f8f5"
COLOR_TEXT = "#1c2b22"
COLOR_TEXT_MUTED = "#6b7c72"
COLOR_TEXT_LIGHT = "#eef6ef"
COLOR_DANGER = "#c0392b"
COLOR_SUCCESS = "#27ae60"
COLOR_WARNING = "#e67e22"
COLOR_BORDER = "#d6e3da"

FONT_BASE = ("Segoe UI", 10)
FONT_SMALL = ("Segoe UI", 9)
FONT_BOLD = ("Segoe UI", 10, "bold")
FONT_HEADER = ("Segoe UI", 15, "bold")
FONT_TITLE = ("Segoe UI", 22, "bold")
FONT_SUBTITLE = ("Segoe UI", 10)


def init_styles(root):
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    style.configure("TFrame", background=COLOR_CARD)
    style.configure("Card.TFrame", background=COLOR_CARD)
    style.configure("Sidebar.TFrame", background=COLOR_SIDEBAR)
    style.configure("TLabel", background=COLOR_CARD, foreground=COLOR_TEXT, font=FONT_BASE)
    style.configure("Card.TLabel", background=COLOR_CARD, foreground=COLOR_TEXT, font=FONT_BASE)
    style.configure("CardHeader.TLabel", background=COLOR_CARD, foreground=COLOR_PRIMARY_DARK, font=FONT_HEADER)
    style.configure("Muted.TLabel", background=COLOR_CARD, foreground=COLOR_TEXT_MUTED, font=FONT_SMALL)
    style.configure("Sidebar.TLabel", background=COLOR_SIDEBAR, foreground=COLOR_TEXT_LIGHT, font=FONT_BASE)

    style.configure("TEntry", padding=5)
    style.configure("TCombobox", padding=4)

    style.configure("TButton", font=FONT_BOLD, padding=6)
    style.configure("Primary.TButton", background=COLOR_PRIMARY, foreground="white")
    style.map("Primary.TButton", background=[("active", COLOR_PRIMARY_DARK)])
    style.configure("Danger.TButton", background=COLOR_DANGER, foreground="white")
    style.map("Danger.TButton", background=[("active", "#922b21")])
    style.configure("Success.TButton", background=COLOR_SUCCESS, foreground="white")
    style.map("Success.TButton", background=[("active", "#1e8449")])
    style.configure("Secondary.TButton", background=COLOR_BORDER, foreground=COLOR_TEXT)

    style.configure("Treeview", font=FONT_SMALL, rowheight=26, background="white",
                     fieldbackground="white")
    style.configure("Treeview.Heading", font=FONT_BOLD, background=COLOR_PRIMARY_DARK,
                     foreground="white")
    style.map("Treeview", background=[("selected", COLOR_PRIMARY)],
              foreground=[("selected", "white")])

    style.configure("Nav.TButton", font=FONT_BASE, anchor="w", padding=(14, 8),
                     background=COLOR_SIDEBAR, foreground=COLOR_TEXT_LIGHT, borderwidth=0)
    style.map("Nav.TButton", background=[("active", COLOR_PRIMARY)])
    style.configure("NavActive.TButton", font=FONT_BOLD, anchor="w", padding=(14, 8),
                     background=COLOR_SIDEBAR_ACTIVE, foreground="white", borderwidth=0)


# =================================================================
# 2. DATABASE LAYER (mirrors the JS "DATA LAYER SEED INITIALIZATION")
# =================================================================

class Database:
    """Thin SQLite wrapper providing the same operations as the original
    localStorage-backed JS data layer (db_users, db_events, db_participants,
    db_announcements, db_feedbacks)."""

    def __init__(self, path=DB_PATH):
        self.path = path
        self._init_schema()
        self._seed_defaults()

    def connect(self):
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def _init_schema(self):
        conn = self.connect()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                username    TEXT PRIMARY KEY,
                password    TEXT NOT NULL,
                role        TEXT NOT NULL,
                full_name   TEXT,
                surname     TEXT,
                firstname   TEXT,
                mi          TEXT,
                course      TEXT,
                year        TEXT,
                section     TEXT,
                student_id  TEXT,
                department  TEXT
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                title        TEXT NOT NULL,
                venue        TEXT,
                date         TEXT,
                category     TEXT,
                description  TEXT,
                virtual_link TEXT,
                proposed_by  TEXT,
                audiences    TEXT,
                equipment    TEXT,
                status       TEXT DEFAULT 'Pending',
                time         TEXT,
                agendas      TEXT,
                speakers     TEXT,
                supplies     TEXT,
                resources    TEXT
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS participants (
                id                INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id        TEXT,
                name              TEXT,
                program           TEXT,
                event_id          INTEGER,
                waiver            INTEGER DEFAULT 0,
                fee               INTEGER DEFAULT 0,
                id_clearance      INTEGER DEFAULT 0,
                proof_pic         TEXT,
                esignature        TEXT,
                attendance_status TEXT
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS announcements (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                title       TEXT,
                content     TEXT,
                date_posted TEXT
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS feedbacks (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT,
                event_id   INTEGER,
                rating     INTEGER,
                comments   TEXT
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS meta (
                k TEXT PRIMARY KEY,
                v TEXT
            )
        """)
        conn.commit()
        conn.close()

    def _seed_defaults(self):
        conn = self.connect()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) AS c FROM users")
        if cur.fetchone()["c"] == 0:
            cur.executemany("""
                INSERT INTO users (username, password, role, full_name, surname,
                                    firstname, mi, course, year, section, student_id, department)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
            """, [
                ("admin", "admin123", "admin", "Deans Admin", "Admin", "Deans", "X",
                 "N/A", "N/A", "N/A", "N/A", "Office of the Dean"),
                ("teacher", "teacher123", "teacher", "Faculty Coordinator", "Coordinator",
                 "Faculty", "Y", "N/A", "N/A", "N/A", "N/A", "Faculty Supervisor"),
                ("student", "student123", "student", "Student User", "User", "Student",
                 "Z.", "BSIT", "3rd Year", "3B", "2026-0001", None),
            ])

        cur.execute("SELECT COUNT(*) AS c FROM events")
        if cur.fetchone()["c"] == 0:
            cur.executemany("""
                INSERT INTO events (id, title, venue, date, category, description,
                                     virtual_link, proposed_by, audiences, equipment,
                                     status, time, agendas, speakers, supplies, resources)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """, [
                (1, "Intramurals 2026", "Main Stadium", "2026-06-08", "Sports", "",
                 "", "Dean of Sports", "", "", "Approved", "08:00 AM",
                 "Opening Ceremonies, Athletics Finals", "Dean of Sports",
                 "Jerseys, Equipment", "Sound System"),
                (2, "Science Fair Expo", "Exhibition Hall", "2026-06-12", "Academic", "",
                 "", "", "", "", "Pending", "", "", "", "", ""),
                (3, "Leadership Conference", "Audio Visual Room", "2026-06-15", "Seminar", "",
                 "", "Dr. Evelyn Cruz", "", "", "Approved", "01:00 PM",
                 "Keynote Speech, Panel Discussion", "Dr. Evelyn Cruz",
                 "Certificates, Badges", "Projector, Slideware"),
            ])

        cur.execute("SELECT COUNT(*) AS c FROM participants")
        if cur.fetchone()["c"] == 0:
            cur.executemany("""
                INSERT INTO participants (id, student_id, name, program, event_id, waiver,
                                           fee, id_clearance, proof_pic, esignature, attendance_status)
                VALUES (?,?,?,?,?,?,?,?,?,?,?)
            """, [
                (1, "2026-0005", "Jenkins, Sarah M.", "EDUC - 2A", 1, 1, 0, 1,
                 "URL_Asset", "S. Jenkins", "Checked In"),
                (2, "2026-0012", "Vincent, John K.", "BSIT - 1B", 3, 0, 1, 1,
                 "N/A", "J. Vincent", "Advance Reserved"),
            ])

        cur.execute("SELECT COUNT(*) AS c FROM announcements")
        if cur.fetchone()["c"] == 0:
            cur.executemany("""
                INSERT INTO announcements (id, title, content, date_posted)
                VALUES (?,?,?,?)
            """, [
                (1, "Venue Shift Notice",
                 "Intramurals opening ceremonies will shift directly into the Main "
                 "Stadium due to weather clearing layout guidelines.", "2026-05-30 09:15 AM"),
                (2, "Registration Extended",
                 "Evaluation parameter slots for the upcoming Leadership Conference "
                 "remain open until Friday evening.", "2026-05-31 02:40 PM"),
            ])

        cur.execute("SELECT COUNT(*) AS c FROM feedbacks")
        if cur.fetchone()["c"] == 0:
            cur.execute("""
                INSERT INTO feedbacks (id, student_id, event_id, rating, comments)
                VALUES (1, 'student', 1, 5,
                'The technical logistics execution blueprint was handled incredibly well!')
            """)

        conn.commit()
        conn.close()

    def find_user(self, username, password):
        conn = self.connect()
        row = conn.execute(
            "SELECT * FROM users WHERE LOWER(username)=LOWER(?) AND password=?",
            (username, password)
        ).fetchone()
        conn.close()
        return row

    def username_exists(self, username):
        conn = self.connect()
        row = conn.execute("SELECT 1 FROM users WHERE LOWER(username)=LOWER(?)",
                            (username,)).fetchone()
        conn.close()
        return row is not None

    def add_student_self_register(self, surname, firstname, mi, course, year,
                                    section, student_id, username, password):
        full_name = f"{surname}, {firstname} {mi}".strip()
        conn = self.connect()
        conn.execute("""
            INSERT INTO users (username, password, role, full_name, surname, firstname,
                                mi, course, year, section, student_id)
            VALUES (?,?,?,?,?,?,?,?,?,?,?)
        """, (username, password, "student", full_name, surname, firstname, mi,
              course, year, section, student_id))
        conn.commit()
        conn.close()

    def list_students(self):
        conn = self.connect()
        rows = conn.execute("SELECT * FROM users WHERE role='student' ORDER BY full_name").fetchall()
        conn.close()
        return rows

    def list_teachers(self):
        conn = self.connect()
        rows = conn.execute("SELECT * FROM users WHERE role='teacher' ORDER BY full_name").fetchall()
        conn.close()
        return rows

    def get_user(self, username):
        conn = self.connect()
        row = conn.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
        conn.close()
        return row

    def find_student_for_reset(self, username, student_id):
        """Verifies a student's identity using username + student ID, the
        only two facts the registration form collects that can stand in
        for an email-based reset (no email field exists in this schema)."""
        conn = self.connect()
        row = conn.execute(
            "SELECT * FROM users WHERE LOWER(username)=LOWER(?) AND role='student' "
            "AND LOWER(TRIM(student_id))=LOWER(TRIM(?))",
            (username, student_id)
        ).fetchone()
        conn.close()
        return row

    def reset_password(self, username, new_password):
        conn = self.connect()
        conn.execute("UPDATE users SET password=? WHERE LOWER(username)=LOWER(?)",
                     (new_password, username))
        conn.commit()
        conn.close()

    def upsert_student(self, surname, firstname, mi, course, year, section, student_id,
                        username, password=None, edit_username=None):
        full_name = f"{surname}, {firstname} {mi}".strip()
        conn = self.connect()
        if edit_username:
            conn.execute("""
                UPDATE users SET surname=?, firstname=?, mi=?, full_name=?, course=?,
                                  year=?, section=?, student_id=?
                WHERE username=? AND role='student'
            """, (surname, firstname, mi, full_name, course, year, section,
                  student_id, edit_username))
        else:
            conn.execute("""
                INSERT INTO users (username, password, role, full_name, surname, firstname,
                                    mi, course, year, section, student_id)
                VALUES (?,?,?,?,?,?,?,?,?,?,?)
            """, (username, password, "student", full_name, surname, firstname, mi,
                  course, year, section, student_id))
        conn.commit()
        conn.close()

    def upsert_teacher(self, full_name, department, username, password=None, edit_username=None):
        conn = self.connect()
        if edit_username:
            if password:
                conn.execute("""
                    UPDATE users SET full_name=?, department=?, password=?
                    WHERE username=? AND role='teacher'
                """, (full_name, department, password, edit_username))
            else:
                conn.execute("""
                    UPDATE users SET full_name=?, department=?
                    WHERE username=? AND role='teacher'
                """, (full_name, department, edit_username))
        else:
            conn.execute("""
                INSERT INTO users (username, password, role, full_name, department,
                                    surname, firstname, mi, course, year, section, student_id)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
            """, (username, password, "teacher", full_name, department,
                  full_name, "", "", "N/A", "N/A", "N/A", "N/A"))
        conn.commit()
        conn.close()

    def delete_user(self, username):
        conn = self.connect()
        conn.execute("DELETE FROM users WHERE username=?", (username,))
        conn.commit()
        conn.close()

    def list_events(self):
        conn = self.connect()
        rows = conn.execute("SELECT * FROM events ORDER BY id").fetchall()
        conn.close()
        return rows

    def list_approved_events(self):
        conn = self.connect()
        rows = conn.execute("SELECT * FROM events WHERE status='Approved' ORDER BY date").fetchall()
        conn.close()
        return rows

    def get_event(self, event_id):
        conn = self.connect()
        row = conn.execute("SELECT * FROM events WHERE id=?", (event_id,)).fetchone()
        conn.close()
        return row

    def add_event(self, title, venue, date, category, description, virtual_link,
                   proposed_by, audiences, equipment, status):
        conn = self.connect()
        conn.execute("""
            INSERT INTO events (title, venue, date, category, description, virtual_link,
                                 proposed_by, audiences, equipment, status, time, agendas,
                                 speakers, supplies, resources)
            VALUES (?,?,?,?,?,?,?,?,?,?,'','','','','')
        """, (title, venue, date, category, description, virtual_link, proposed_by,
              ",".join(audiences), ",".join(equipment), status))
        conn.commit()
        conn.close()

    def update_event(self, event_id, title, venue, date, category, description,
                      virtual_link, proposed_by, audiences, equipment):
        conn = self.connect()
        conn.execute("""
            UPDATE events SET title=?, venue=?, date=?, category=?, description=?,
                               virtual_link=?, proposed_by=?, audiences=?, equipment=?
            WHERE id=?
        """, (title, venue, date, category, description, virtual_link, proposed_by,
              ",".join(audiences), ",".join(equipment), event_id))
        conn.commit()
        conn.close()

    def set_event_status(self, event_id, status):
        conn = self.connect()
        conn.execute("UPDATE events SET status=? WHERE id=?", (status, event_id))
        conn.commit()
        conn.close()

    def update_logistics(self, event_id, time_, speakers, agendas, supplies, resources):
        conn = self.connect()
        conn.execute("""
            UPDATE events SET time=?, speakers=?, agendas=?, supplies=?, resources=?
            WHERE id=?
        """, (time_, speakers, agendas, supplies, resources, event_id))
        conn.commit()
        conn.close()

    def delete_event(self, event_id):
        conn = self.connect()
        conn.execute("DELETE FROM events WHERE id=?", (event_id,))
        conn.execute("DELETE FROM participants WHERE event_id=?", (event_id,))
        conn.commit()
        conn.close()

    def list_participants(self):
        conn = self.connect()
        rows = conn.execute("SELECT * FROM participants ORDER BY id").fetchall()
        conn.close()
        return rows

    def get_participant(self, pid):
        conn = self.connect()
        row = conn.execute("SELECT * FROM participants WHERE id=?", (pid,)).fetchone()
        conn.close()
        return row

    def find_participant_for_student_event(self, event_id, student_id):
        conn = self.connect()
        row = conn.execute(
            "SELECT * FROM participants WHERE event_id=? AND student_id=?",
            (event_id, student_id)
        ).fetchone()
        conn.close()
        return row

    def add_participant(self, student_id, name, program, event_id, waiver, fee,
                         id_clearance, attendance_status, proof_pic="N/A",
                         esignature="Admin Override"):
        conn = self.connect()
        conn.execute("""
            INSERT INTO participants (student_id, name, program, event_id, waiver, fee,
                                       id_clearance, proof_pic, esignature, attendance_status)
            VALUES (?,?,?,?,?,?,?,?,?,?)
        """, (student_id, name, program, event_id, int(waiver), int(fee),
              int(id_clearance), proof_pic, esignature, attendance_status))
        conn.commit()
        conn.close()

    def update_participant(self, pid, event_id, student_id, name, program, waiver, fee,
                            id_clearance, attendance_status):
        conn = self.connect()
        conn.execute("""
            UPDATE participants SET event_id=?, student_id=?, name=?, program=?, waiver=?,
                                     fee=?, id_clearance=?, attendance_status=?
            WHERE id=?
        """, (event_id, student_id, name, program, int(waiver), int(fee),
              int(id_clearance), attendance_status, pid))
        conn.commit()
        conn.close()

    def self_checkin(self, event_id, student_id, name, program, proof_pic, esignature):
        existing = self.find_participant_for_student_event(event_id, student_id)
        conn = self.connect()
        if existing:
            conn.execute("""
                UPDATE participants SET proof_pic=?, esignature=?, attendance_status='Checked In'
                WHERE id=?
            """, (proof_pic, esignature, existing["id"]))
        else:
            conn.execute("""
                INSERT INTO participants (student_id, name, program, event_id, waiver, fee,
                                           id_clearance, proof_pic, esignature, attendance_status)
                VALUES (?,?,?,?,1,1,1,?,?,'Checked In')
            """, (student_id, name, program, event_id, proof_pic, esignature))
        conn.commit()
        conn.close()

    def delete_participant(self, pid):
        conn = self.connect()
        conn.execute("DELETE FROM participants WHERE id=?", (pid,))
        conn.commit()
        conn.close()

    def list_announcements(self):
        conn = self.connect()
        rows = conn.execute("SELECT * FROM announcements ORDER BY id").fetchall()
        conn.close()
        return rows

    def add_announcement(self, title, content):
        date_posted = datetime.now().strftime("%Y-%m-%d %I:%M %p")
        conn = self.connect()
        conn.execute("INSERT INTO announcements (title, content, date_posted) VALUES (?,?,?)",
                     (title, content, date_posted))
        conn.commit()
        conn.close()

    def update_announcement(self, aid, title, content):
        conn = self.connect()
        conn.execute("UPDATE announcements SET title=?, content=? WHERE id=?",
                     (title, content, aid))
        conn.commit()
        conn.close()

    def delete_announcement(self, aid):
        conn = self.connect()
        conn.execute("DELETE FROM announcements WHERE id=?", (aid,))
        conn.commit()
        conn.close()

    def list_feedbacks(self):
        conn = self.connect()
        rows = conn.execute("SELECT * FROM feedbacks ORDER BY id").fetchall()
        conn.close()
        return rows

    def add_feedback(self, student_id, event_id, rating, comments):
        conn = self.connect()
        conn.execute("""
            INSERT INTO feedbacks (student_id, event_id, rating, comments)
            VALUES (?,?,?,?)
        """, (student_id, event_id, rating, comments))
        conn.commit()
        conn.close()

    def metrics(self):
        conn = self.connect()
        total_approved = conn.execute(
            "SELECT COUNT(*) c FROM events WHERE status='Approved'").fetchone()["c"]
        pending = conn.execute(
            "SELECT COUNT(*) c FROM events WHERE status='Pending'").fetchone()["c"]
        total_participants = conn.execute("SELECT COUNT(*) c FROM participants").fetchone()["c"]
        checked_in = conn.execute(
            "SELECT COUNT(*) c FROM participants WHERE attendance_status='Checked In'").fetchone()["c"]
        conn.close()
        rate = f"{round((checked_in / total_participants) * 100)}%" if total_participants else "0%"
        return {
            "total_approved": total_approved,
            "pending": pending,
            "total_participants": total_participants,
            "attendance_rate": rate,
        }


db = Database()


# =================================================================
# 3. SMALL UI HELPERS
# =================================================================

def card(parent, **kw):
    f = tk.Frame(parent, bg=COLOR_CARD, highlightbackground=COLOR_BORDER,
                 highlightthickness=1, **kw)
    return f


def card_header(parent, text, icon=""):
    lbl = tk.Label(parent, text=f"{icon}  {text}".strip(), bg=COLOR_CARD,
                    fg=COLOR_PRIMARY_DARK, font=FONT_HEADER, anchor="w")
    lbl.pack(fill="x", padx=14, pady=(12, 6))
    sep = tk.Frame(parent, bg=COLOR_BORDER, height=1)
    sep.pack(fill="x", padx=14)
    return lbl


def labeled_entry(parent, label_text, **entry_kw):
    wrap = tk.Frame(parent, bg=COLOR_CARD)
    wrap.pack(fill="x", padx=14, pady=4)
    tk.Label(wrap, text=label_text, bg=COLOR_CARD, fg=COLOR_TEXT, font=FONT_SMALL,
              anchor="w").pack(fill="x")
    entry = ttk.Entry(wrap, font=FONT_BASE, **entry_kw)
    entry.pack(fill="x", pady=(2, 0))
    return entry


def labeled_combo(parent, label_text, values, default=None, **combo_kw):
    wrap = tk.Frame(parent, bg=COLOR_CARD)
    wrap.pack(fill="x", padx=14, pady=4)
    tk.Label(wrap, text=label_text, bg=COLOR_CARD, fg=COLOR_TEXT, font=FONT_SMALL,
              anchor="w").pack(fill="x")
    combo = ttk.Combobox(wrap, font=FONT_BASE, values=values, state="readonly", **combo_kw)
    if default is not None:
        combo.set(default)
    combo.pack(fill="x", pady=(2, 0))
    return combo


def labeled_text(parent, label_text, height=3):
    wrap = tk.Frame(parent, bg=COLOR_CARD)
    wrap.pack(fill="x", padx=14, pady=4)
    tk.Label(wrap, text=label_text, bg=COLOR_CARD, fg=COLOR_TEXT, font=FONT_SMALL,
              anchor="w").pack(fill="x")
    txt = tk.Text(wrap, height=height, font=FONT_BASE, wrap="word",
                   highlightbackground=COLOR_BORDER, highlightthickness=1, bd=0)
    txt.pack(fill="x", pady=(2, 0))
    return txt


def make_table(parent, columns, headings, widths=None):
    """Builds a ttk.Treeview with a vertical scrollbar. Returns the Treeview."""
    wrap = tk.Frame(parent, bg=COLOR_CARD)
    wrap.pack(fill="both", expand=True, padx=10, pady=10)

    tree = ttk.Treeview(wrap, columns=columns, show="headings", selectmode="browse")
    for i, col in enumerate(columns):
        tree.heading(col, text=headings[i])
        w = widths[i] if widths else 120
        tree.column(col, width=w, anchor="w")

    vsb = ttk.Scrollbar(wrap, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=vsb.set)
    tree.pack(side="left", fill="both", expand=True)
    vsb.pack(side="right", fill="y")
    return tree


def badge_text(value, true_label, false_label):
    return true_label if value else false_label


class TableController:
    """Drives a ttk.Treeview from a list of plain dicts, applying a live
    search filter, an optional dropdown filter, and a sort key/direction.
    Call .set_rows(list_of_dicts) whenever the underlying data changes,
    then .refresh() repaints the Treeview from current controls."""

    def __init__(self, columns, value_fn, search_fn, sort_options,
                 filter_fn=None, default_sort=None, tree=None):
        self.tree = tree
        self.columns = columns
        self.value_fn = value_fn          # row_dict -> tuple of column values
        self.search_fn = search_fn        # (row_dict, query_lower) -> bool
        self.sort_options = sort_options  # {label: row_dict -> sortable_key}
        self.filter_fn = filter_fn        # (row_dict, filter_value) -> bool
        self.rows = []
        self.search_var = tk.StringVar(value="")
        self.sort_var = tk.StringVar(value=default_sort or next(iter(sort_options)))
        self.sort_dir_desc = tk.BooleanVar(value=False)
        self.filter_var = tk.StringVar(value="All")

    def set_rows(self, rows):
        self.rows = rows
        self.refresh()

    def refresh(self):
        if self.tree is None:
            return
        query = self.search_var.get().strip().lower()
        fval = self.filter_var.get()

        visible = self.rows
        if query:
            visible = [r for r in visible if self.search_fn(r, query)]
        if self.filter_fn and fval and fval != "All":
            visible = [r for r in visible if self.filter_fn(r, fval)]

        key_fn = self.sort_options.get(self.sort_var.get())
        if key_fn:
            visible = sorted(visible, key=key_fn, reverse=self.sort_dir_desc.get())

        self.tree.delete(*self.tree.get_children())
        for r in visible:
            iid = r.get("_iid")
            vals = self.value_fn(r)
            if iid is not None:
                self.tree.insert("", "end", iid=iid, values=vals)
            else:
                self.tree.insert("", "end", values=vals)


def table_toolbar(parent, controller, search_placeholder="Search...",
                   filter_label=None, filter_values=None):
    """Builds a search box + sort dropdown + (optional) filter dropdown
    above a table, wired to the given TableController."""
    bar = tk.Frame(parent, bg=COLOR_CARD)
    bar.pack(fill="x", padx=10, pady=(10, 0))

    search_wrap = tk.Frame(bar, bg=COLOR_CARD)
    search_wrap.pack(side="left", fill="x", expand=True)
    tk.Label(search_wrap, text="\U0001F50D", bg=COLOR_CARD, fg=COLOR_TEXT_MUTED,
              font=FONT_BASE).pack(side="left", padx=(0, 4))
    search_entry = ttk.Entry(search_wrap, font=FONT_BASE, textvariable=controller.search_var)
    search_entry.pack(side="left", fill="x", expand=True)
    search_entry.insert(0, "")

    def on_key(event=None):
        controller.refresh()

    search_entry.bind("<KeyRelease>", on_key)

    if filter_label and filter_values:
        tk.Label(bar, text=filter_label, bg=COLOR_CARD, fg=COLOR_TEXT_MUTED,
                  font=FONT_SMALL).pack(side="left", padx=(14, 4))
        filter_combo = ttk.Combobox(bar, font=FONT_SMALL, state="readonly",
                                      values=["All"] + list(filter_values),
                                      textvariable=controller.filter_var, width=14)
        filter_combo.pack(side="left")
        filter_combo.bind("<<ComboboxSelected>>", lambda e: controller.refresh())

    tk.Label(bar, text="Sort by", bg=COLOR_CARD, fg=COLOR_TEXT_MUTED,
              font=FONT_SMALL).pack(side="left", padx=(14, 4))
    sort_combo = ttk.Combobox(bar, font=FONT_SMALL, state="readonly",
                                values=list(controller.sort_options.keys()),
                                textvariable=controller.sort_var, width=16)
    sort_combo.pack(side="left")
    sort_combo.bind("<<ComboboxSelected>>", lambda e: controller.refresh())

    dir_btn = ttk.Button(bar, text="\u2193 Desc", style="Secondary.TButton", width=8)
    dir_btn.pack(side="left", padx=(6, 0))

    def toggle_dir():
        controller.sort_dir_desc.set(not controller.sort_dir_desc.get())
        dir_btn.configure(text="\u2193 Desc" if controller.sort_dir_desc.get() else "\u2191 Asc")
        controller.refresh()

    dir_btn.configure(command=toggle_dir)
    return bar


def make_table_with_toolbar(parent, columns, headings, controller, widths=None,
                              search_placeholder="Search...", filter_label=None,
                              filter_values=None):
    """Packs a search/sort/filter toolbar followed by a Treeview+scrollbar,
    and attaches the live Treeview to the given (tree-less) controller."""
    table_toolbar(parent, controller, search_placeholder=search_placeholder,
                  filter_label=filter_label, filter_values=filter_values)

    wrap = tk.Frame(parent, bg=COLOR_CARD)
    wrap.pack(fill="both", expand=True, padx=10, pady=10)

    tree = ttk.Treeview(wrap, columns=columns, show="headings", selectmode="browse")
    for i, col in enumerate(columns):
        tree.heading(col, text=headings[i])
        tree.column(col, width=(widths[i] if widths else 120), anchor="w")

    vsb = ttk.Scrollbar(wrap, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=vsb.set)
    tree.pack(side="left", fill="both", expand=True)
    vsb.pack(side="right", fill="y")

    controller.tree = tree
    return tree


# =================================================================
# 4. AUTH VIEW  (login / register gateway)
# =================================================================

class AuthView(tk.Frame):
    LOGIN_SIZE = (720, 480)
    REGISTER_SIZE = (900, 620)

    def __init__(self, parent, on_login_success):
        super().__init__(parent, bg=COLOR_BG)
        self.on_login_success = on_login_success
        self.pack(fill="both", expand=True)
        self._logo_img = None
        self._build()

    # ----------------------------------------------------------- shell
    def _build(self):
        self.outer = tk.Frame(self, bg=COLOR_BG)
        self.outer.place(relx=0.5, rely=0.5, anchor="center")

        self.banner = tk.Frame(self.outer, bg=COLOR_PRIMARY_DARK)
        self.banner.grid(row=0, column=0, sticky="nsew")
        self.banner.grid_propagate(False)

        self.form_container = tk.Frame(self.outer, bg=COLOR_CARD)
        self.form_container.grid(row=0, column=1, sticky="nsew")
        self.form_container.grid_propagate(False)

        self._set_stage_size(*self.LOGIN_SIZE)
        self._build_banner()
        self._build_login_form()

    def _set_stage_size(self, total_w, total_h):
        """Resizes the banner + form pair as a unit so registration gets
        room to breathe without resorting to an awkward inner scrollbar."""
        banner_w = 300
        self.banner.configure(width=banner_w, height=total_h)
        self.form_container.configure(width=total_w - banner_w, height=total_h)

    def _build_banner(self):
        for w in self.banner.winfo_children():
            w.destroy()

        crest = tk.Frame(self.banner, bg=COLOR_PRIMARY_DARK)
        crest.pack(pady=(36, 12))

        logo_path = os.path.join(resource_dir(), "cscqclogo.png")
        if os.path.exists(logo_path):
            try:
                raw_img = tk.PhotoImage(file=logo_path)
                w, h = raw_img.width(), raw_img.height()
                rate = max(1, min(w // 110, h // 110))
                self._logo_img = raw_img.subsample(rate, rate) if rate > 1 else raw_img
                tk.Label(crest, image=self._logo_img, bg=COLOR_PRIMARY_DARK).pack()
            except Exception:
                tk.Label(crest, text="\U0001F393", bg=COLOR_PRIMARY_DARK, fg="white",
                          font=("Segoe UI", 36)).pack()
        else:
            tk.Label(crest, text="\U0001F393", bg=COLOR_PRIMARY_DARK, fg="white",
                      font=("Segoe UI", 36)).pack()

        tk.Label(self.banner, text="SEMS", bg=COLOR_PRIMARY_DARK, fg="white",
                 font=("Segoe UI", 20, "bold")).pack()
        tk.Label(self.banner, text="School Event Management System", bg=COLOR_PRIMARY_DARK,
                 fg=COLOR_ACCENT, font=FONT_SUBTITLE).pack(pady=(2, 0))
        tk.Frame(self.banner, bg=COLOR_ACCENT, height=2, width=60).pack(pady=16)
        tk.Label(self.banner, text="Manage. Organize. Execute.", bg=COLOR_PRIMARY_DARK,
                 fg="white", font=("Georgia", 12, "italic"), wraplength=240,
                 justify="center").pack(padx=20, pady=(0, 24))

        feats = tk.Frame(self.banner, bg=COLOR_PRIMARY_DARK)
        feats.pack(padx=30)
        for txt in ["Event Scheduling", "Attendance Tracking", "Analytics & Insights"]:
            row = tk.Frame(feats, bg=COLOR_PRIMARY_DARK)
            row.pack(anchor="w", pady=4, fill="x")
            tk.Label(row, text="\u2713", bg=COLOR_PRIMARY_DARK, fg=COLOR_ACCENT,
                      font=FONT_BOLD).pack(side="left", padx=(0, 8))
            tk.Label(row, text=txt, bg=COLOR_PRIMARY_DARK, fg="white", font=FONT_BASE).pack(side="left")

        tk.Label(self.banner, text="College of St. Catherine \u2013 Quezon City",
                  bg=COLOR_PRIMARY_DARK, fg=COLOR_TEXT_LIGHT, font=FONT_SMALL).pack(
                  side="bottom", pady=18)

    # ----------------------------------------------------------- login
    def _build_login_form(self):
        self._set_stage_size(*self.LOGIN_SIZE)
        for w in self.form_container.winfo_children():
            w.destroy()

        inner = tk.Frame(self.form_container, bg=COLOR_CARD)
        inner.place(relx=0.5, rely=0.5, anchor="center", width=320)

        tk.Label(inner, text="Welcome back!", font=FONT_TITLE, bg=COLOR_CARD,
                 fg=COLOR_PRIMARY_DARK).pack(anchor="w", pady=(0, 2))
        tk.Label(inner, text="Sign in to continue to your dashboard", font=FONT_SMALL,
                 bg=COLOR_CARD, fg=COLOR_TEXT_MUTED).pack(anchor="w", pady=(0, 22))

        u_entry = labeled_entry(inner, "Username or Student ID")
        p_entry, _ = self._password_field(inner, "Password")

        forgot_row = tk.Frame(inner, bg=COLOR_CARD)
        forgot_row.pack(fill="x", padx=14, pady=(2, 0))
        forgot_link = tk.Label(forgot_row, text="Forgot password?", bg=COLOR_CARD, fg=COLOR_PRIMARY,
                                font=("Segoe UI", 9, "underline"), cursor="hand2")
        forgot_link.pack(side="right")
        forgot_link.bind("<Button-1>", lambda e: self._build_forgot_password_form())

        error_lbl = tk.Label(inner, text="", bg=COLOR_CARD, fg=COLOR_DANGER, font=FONT_SMALL,
                              anchor="w", justify="left", wraplength=320)
        error_lbl.pack(fill="x", padx=14, pady=(6, 0))

        def do_login(event=None):
            uname = u_entry.get().strip()
            pwd = p_entry.get()
            if not uname or not pwd:
                error_lbl.configure(text="Enter both your username and password.")
                return
            user = db.find_user(uname, pwd)
            if user:
                error_lbl.configure(text="")
                self.on_login_success(dict(user))
            else:
                error_lbl.configure(text="Incorrect username or password. Please try again.")

        p_entry.bind("<Return>", do_login)
        ttk.Button(inner, text="Sign In", style="Primary.TButton",
                   command=do_login).pack(fill="x", padx=0, pady=(18, 10))

        foot = tk.Frame(inner, bg=COLOR_CARD)
        foot.pack(fill="x", pady=(8, 0))
        tk.Label(foot, text="New here?", bg=COLOR_CARD, fg=COLOR_TEXT_MUTED, font=FONT_SMALL).pack(side="left")
        link = tk.Label(foot, text="Create a student account", bg=COLOR_CARD, fg=COLOR_PRIMARY,
                        font=("Segoe UI", 9, "underline"), cursor="hand2")
        link.pack(side="left", padx=4)
        link.bind("<Button-1>", lambda e: self._build_register_form())

    # -------------------------------------------------- forgot password
    def _build_forgot_password_form(self):
        self._set_stage_size(*self.LOGIN_SIZE)
        for w in self.form_container.winfo_children():
            w.destroy()

        inner = tk.Frame(self.form_container, bg=COLOR_CARD)
        inner.place(relx=0.5, rely=0.5, anchor="center", width=320)

        tk.Label(inner, text="Reset your password", font=FONT_TITLE, bg=COLOR_CARD,
                 fg=COLOR_PRIMARY_DARK).pack(anchor="w", pady=(0, 2))
        tk.Label(inner, text="This is for student accounts only. Verify your\nidentity to set a new password.",
                 font=FONT_SMALL, bg=COLOR_CARD, fg=COLOR_TEXT_MUTED, justify="left").pack(anchor="w", pady=(0, 18))

        u_entry = labeled_entry(inner, "Username")
        sid_entry = labeled_entry(inner, "Student ID")

        error_lbl = tk.Label(inner, text="", bg=COLOR_CARD, fg=COLOR_DANGER, font=FONT_SMALL,
                              anchor="w", justify="left", wraplength=320)
        error_lbl.pack(fill="x", padx=14, pady=(6, 0))

        def do_verify(event=None):
            uname = u_entry.get().strip()
            sid = sid_entry.get().strip()
            if not uname or not sid:
                error_lbl.configure(text="Enter both your username and student ID.")
                return
            user = db.find_student_for_reset(uname, sid)
            if not user:
                error_lbl.configure(
                    text="We couldn't verify a student account with that username and student ID.")
                return
            error_lbl.configure(text="")
            self._build_set_new_password_form(dict(user))

        sid_entry.bind("<Return>", do_verify)
        ttk.Button(inner, text="Verify Identity", style="Primary.TButton",
                   command=do_verify).pack(fill="x", pady=(18, 10))

        foot = tk.Frame(inner, bg=COLOR_CARD)
        foot.pack(fill="x", pady=(8, 0))
        link = tk.Label(foot, text="\u2190 Back to sign in", bg=COLOR_CARD, fg=COLOR_PRIMARY,
                        font=("Segoe UI", 9, "underline"), cursor="hand2")
        link.pack(side="left")
        link.bind("<Button-1>", lambda e: self._build_login_form())

    def _build_set_new_password_form(self, user):
        self._set_stage_size(*self.LOGIN_SIZE)
        for w in self.form_container.winfo_children():
            w.destroy()

        inner = tk.Frame(self.form_container, bg=COLOR_CARD)
        inner.place(relx=0.5, rely=0.5, anchor="center", width=320)

        tk.Label(inner, text="Choose a new password", font=FONT_TITLE, bg=COLOR_CARD,
                 fg=COLOR_PRIMARY_DARK).pack(anchor="w", pady=(0, 2))
        tk.Label(inner, text=f"Identity verified for {user['full_name']}.", font=FONT_SMALL,
                 bg=COLOR_CARD, fg=COLOR_TEXT_MUTED).pack(anchor="w", pady=(0, 18))

        new_pw, _ = self._password_field(inner, "New Password")
        confirm_pw, _ = self._password_field(inner, "Confirm New Password")

        error_lbl = tk.Label(inner, text="", bg=COLOR_CARD, fg=COLOR_DANGER, font=FONT_SMALL,
                              anchor="w", justify="left", wraplength=320)
        error_lbl.pack(fill="x", padx=14, pady=(6, 0))

        def do_reset():
            pw = new_pw.get()
            cpw = confirm_pw.get()
            if not pw or not cpw:
                error_lbl.configure(text="Please fill in both password fields.")
                return
            if len(pw) < 6:
                error_lbl.configure(text="Your new password must be at least 6 characters long.")
                return
            if pw != cpw:
                error_lbl.configure(text="Passwords do not match. Please re-enter them.")
                return
            db.reset_password(user["username"], pw)
            messagebox.showinfo("Password Updated", "Your password has been reset. You can now sign in.")
            self._build_login_form()

        ttk.Button(inner, text="Save New Password", style="Success.TButton",
                   command=do_reset).pack(fill="x", pady=(18, 10))

        foot = tk.Frame(inner, bg=COLOR_CARD)
        foot.pack(fill="x", pady=(8, 0))
        link = tk.Label(foot, text="\u2190 Back to sign in", bg=COLOR_CARD, fg=COLOR_PRIMARY,
                        font=("Segoe UI", 9, "underline"), cursor="hand2")
        link.pack(side="left")
        link.bind("<Button-1>", lambda e: self._build_login_form())

    # ------------------------------------------------------- register
    def _password_field(self, parent, label_text):
        """A labeled password entry with a show/hide toggle."""
        wrap = tk.Frame(parent, bg=COLOR_CARD)
        wrap.pack(fill="x", padx=14, pady=4)
        tk.Label(wrap, text=label_text, bg=COLOR_CARD, fg=COLOR_TEXT, font=FONT_SMALL,
                  anchor="w").pack(fill="x")

        row = tk.Frame(wrap, bg=COLOR_CARD)
        row.pack(fill="x", pady=(2, 0))
        entry = ttk.Entry(row, font=FONT_BASE, show="\u2022")
        entry.pack(side="left", fill="x", expand=True)

        toggle = tk.Label(row, text="Show", bg=COLOR_CARD, fg=COLOR_PRIMARY, font=FONT_SMALL,
                            cursor="hand2", padx=8)
        toggle.pack(side="left")

        state = {"visible": False}

        def flip(event=None):
            state["visible"] = not state["visible"]
            entry.configure(show="" if state["visible"] else "\u2022")
            toggle.configure(text="Hide" if state["visible"] else "Show")

        toggle.bind("<Button-1>", flip)
        return entry, toggle

    def _build_register_form(self):
        self._set_stage_size(*self.REGISTER_SIZE)
        for w in self.form_container.winfo_children():
            w.destroy()

        # Scroll wrapper kept as a safety net for small screens, but the
        # widened stage means everything fits without scrolling in
        # the common case.
        canvas = tk.Canvas(self.form_container, bg=COLOR_CARD, bd=0, highlightthickness=0)
        vsb = ttk.Scrollbar(self.form_container, orient="vertical", command=canvas.yview)
        inner = tk.Frame(canvas, bg=COLOR_CARD)

        canvas.configure(yscrollcommand=vsb.set)
        canvas.pack(side="left", fill="both", expand=True)
        window_id = canvas.create_window((0, 0), window=inner, anchor="nw")

        def update_scroll(event=None):
            canvas.configure(scrollregion=canvas.bbox("all"))
            bbox = canvas.bbox("all")
            content_h = bbox[3] if bbox else 0
            visible_h = canvas.winfo_height()
            if content_h > visible_h:
                if not vsb.winfo_ismapped():
                    vsb.pack(side="right", fill="y")
            else:
                vsb.pack_forget()

        def sync_width(event):
            canvas.itemconfigure(window_id, width=event.width)

        inner.bind("<Configure>", update_scroll)
        canvas.bind("<Configure>", sync_width)

        content = tk.Frame(inner, bg=COLOR_CARD)
        content.pack(fill="x", padx=36, pady=28)

        tk.Label(content, text="Create your student account", font=FONT_TITLE, bg=COLOR_CARD,
                 fg=COLOR_PRIMARY_DARK).pack(anchor="w", pady=(0, 2))
        tk.Label(content, text="Register to view events, track attendance, and submit feedback.",
                 font=FONT_SMALL, bg=COLOR_CARD, fg=COLOR_TEXT_MUTED).pack(anchor="w", pady=(0, 22))

        fields_row = tk.Frame(content, bg=COLOR_CARD)
        fields_row.pack(fill="x")
        col_left = tk.Frame(fields_row, bg=COLOR_CARD)
        col_left.pack(side="left", fill="both", expand=True, padx=(0, 14))
        col_right = tk.Frame(fields_row, bg=COLOR_CARD)
        col_right.pack(side="left", fill="both", expand=True)

        def section_title(parent, text):
            wrap = tk.Frame(parent, bg=COLOR_CARD)
            wrap.pack(fill="x", pady=(4, 8))
            tk.Frame(wrap, bg=COLOR_ACCENT, width=4, height=18).pack(side="left", padx=(0, 8))
            tk.Label(wrap, text=text, bg=COLOR_CARD, fg=COLOR_PRIMARY_DARK,
                      font=FONT_BOLD).pack(side="left")

        def field_pair(parent, label_a, label_b, **kw):
            row = tk.Frame(parent, bg=COLOR_CARD)
            row.pack(fill="x")
            a = tk.Frame(row, bg=COLOR_CARD)
            a.pack(side="left", fill="both", expand=True)
            b = tk.Frame(row, bg=COLOR_CARD)
            b.pack(side="left", fill="both", expand=True)
            return labeled_entry(a, label_a, **kw), labeled_entry(b, label_b, **kw)

        def combo_entry_pair(parent, combo_label, combo_values, combo_default, entry_label):
            row = tk.Frame(parent, bg=COLOR_CARD)
            row.pack(fill="x")
            a = tk.Frame(row, bg=COLOR_CARD)
            a.pack(side="left", fill="both", expand=True)
            b = tk.Frame(row, bg=COLOR_CARD)
            b.pack(side="left", fill="both", expand=True)
            combo = labeled_combo(a, combo_label, combo_values, default=combo_default)
            entry = labeled_entry(b, entry_label)
            return combo, entry

        # ---- Section 1: Personal Information ----
        section_title(col_left, "Personal Information")
        surname = labeled_entry(col_left, "Surname *")
        firstname, mi = field_pair(col_left, "First Name *", "M.I.")

        # ---- Section 2: Academic Details ----
        section_title(col_left, "Academic Details")
        course = labeled_combo(col_left, "Course *", COURSES, default=COURSES[0])
        year, section = combo_entry_pair(col_left, "Year Level *", YEARS, YEARS[0], "Section (e.g., 3B)")
        student_id = labeled_entry(col_left, "Student ID (enter N/A if none)")

        # ---- Section 3: Account Credentials ----
        section_title(col_right, "Account Credentials")
        username = labeled_entry(col_right, "Desired Username *")
        username_hint = tk.Label(col_right, text="", bg=COLOR_CARD, fg=COLOR_DANGER,
                                   font=FONT_SMALL, anchor="w")
        username_hint.pack(fill="x", padx=14)

        password, _ = self._password_field(col_right, "Password *")
        confirm, _ = self._password_field(col_right, "Confirm Password *")

        rules = tk.Label(col_right, text="Use at least 6 characters.", bg=COLOR_CARD,
                          fg=COLOR_TEXT_MUTED, font=FONT_SMALL, anchor="w")
        rules.pack(fill="x", padx=14, pady=(2, 0))

        error_lbl = tk.Label(content, text="", bg=COLOR_CARD, fg=COLOR_DANGER, font=FONT_SMALL,
                              anchor="w", justify="left", wraplength=700)
        error_lbl.pack(fill="x", pady=(14, 0))

        def show_error(msg):
            error_lbl.configure(text=msg)
            canvas.yview_moveto(0)

        def do_register():
            username_hint.configure(text="")
            required = {
                "Surname": surname.get().strip(),
                "First Name": firstname.get().strip(),
                "Desired Username": username.get().strip(),
                "Password": password.get(),
                "Confirm Password": confirm.get(),
            }
            missing = [label for label, val in required.items() if not val]
            if missing:
                show_error(f"Please fill in: {', '.join(missing)}.")
                return

            if len(password.get()) < 6:
                show_error("Your password must be at least 6 characters long.")
                return

            if password.get() != confirm.get():
                show_error("Passwords do not match. Please re-enter them.")
                return

            uname = username.get().strip().lower()
            if db.username_exists(uname):
                username_hint.configure(text="This username is already taken.")
                show_error("That username is already in use. Please choose another.")
                return

            show_error("")
            db.add_student_self_register(
                surname.get().strip(), firstname.get().strip(), mi.get().strip(), course.get(),
                year.get(), section.get().strip(), student_id.get().strip(), uname, password.get())
            messagebox.showinfo(
                "Account Created", "Your student account has been created successfully.\nYou can now sign in.")
            self._build_login_form()

        btn_row = tk.Frame(content, bg=COLOR_CARD)
        btn_row.pack(fill="x", pady=(18, 4))
        ttk.Button(btn_row, text="Create Account", style="Success.TButton",
                   command=do_register).pack(fill="x")

        foot = tk.Frame(content, bg=COLOR_CARD)
        foot.pack(fill="x", pady=(14, 4))
        tk.Label(foot, text="Already have an account?", bg=COLOR_CARD, fg=COLOR_TEXT_MUTED,
                  font=FONT_SMALL).pack(side="left")
        link = tk.Label(foot, text="Sign in instead", bg=COLOR_CARD, fg=COLOR_PRIMARY,
                        font=("Segoe UI", 9, "underline"), cursor="hand2")
        link.pack(side="left", padx=4)
        link.bind("<Button-1>", lambda e: self._build_login_form())


# =================================================================
# 5. NAVIGATION SCHEMA (mirrors navLinksSchema in app.js)
# =================================================================

NAV_SCHEMA = [
    {"id": "dashboard", "label": "Dashboard", "icon": "\U0001F4CA", "roles": ["admin", "teacher", "student"]},
    {"id": "events", "label": "Events & Proposals", "icon": "\U0001F4C5", "roles": ["admin", "teacher"]},
    {"id": "logistics", "label": "Logistics Blueprint", "icon": "\u2699", "roles": ["teacher"]},
    {"id": "registrar", "label": "Stream Registrar", "icon": "\U0001F4DD", "roles": ["admin", "teacher"]},
    {"id": "checkin", "label": "Digital Attendance", "icon": "\u2714", "roles": ["student"]},
    {"id": "announcements", "label": "Push Bulletins", "icon": "\U0001F4E1", "roles": ["admin"]},
    {"id": "feedback", "label": "System Feedback", "icon": "\U0001F4AC", "roles": ["admin", "student"]},
    {"id": "students", "label": "Student Database", "icon": "\U0001F393", "roles": ["admin"]},
    {"id": "teachers", "label": "Teacher Database", "icon": "\U0001F468\u200D\U0001F3EB", "roles": ["admin"]},
]


# =================================================================
# 6. MAIN WORKSPACE SETUP (Section 19: WorkspaceView)
# =================================================================

class WorkspaceView(tk.Frame):
    def __init__(self, parent, user, on_logout):
        super().__init__(parent, bg=COLOR_BG)
        self.user = user
        self.on_logout = on_logout
        self.current_view_id = None
        self.nav_schema = NAV_SCHEMA
        self.pack(fill="both", expand=True)
        self._build_sidebar()

        # Target dynamic parameters for different views
        self.editing_student_username = None
        self.editing_teacher_username = None
        self.active_event_id = None
        self.editing_participant_id = None
        self.editing_announcement_id = None
        self.selected_student_event_id = None

        # Build primary panel frame area right next to navigation panels
        self._switch_view("dashboard")

    def _build_sidebar(self):
        sidebar = tk.Frame(self, bg=COLOR_SIDEBAR, width=240)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        # Container for Brand/Logo
        brand_frame = tk.Frame(sidebar, bg=COLOR_SIDEBAR)
        brand_frame.pack(fill="x", pady=(20, 10), padx=10)

        # Look for the logo image file (cscqclogo.png)
        logo_path = os.path.join(resource_dir(), "cscqclogo.png")
        if os.path.exists(logo_path):
            try:
                # Load the photo using Tkinter built-in photo mapping layer
                raw_img = tk.PhotoImage(file=logo_path)
                
                # Dynamic downsampling fallback logic if the original asset file layout is dense
                width = raw_img.width()
                height = raw_img.height()
                sample_rate = max(1, min(width // 80, height // 80))
                if sample_rate > 1:
                    logo_img = raw_img.subsample(sample_rate, sample_rate)
                else:
                    logo_img = raw_img
                
                logo_lbl = tk.Label(brand_frame, image=logo_img, bg=COLOR_SIDEBAR)
                logo_lbl.image = logo_img  # Persistent safe layout garbage collection map
                logo_lbl.pack(pady=(0, 5))
            except Exception:
                # Fallback gently to normal text layout if file decode triggers environment constraints
                pass

        # Text Headers
        tk.Label(brand_frame, text="CSC - QC", bg=COLOR_SIDEBAR, fg=COLOR_ACCENT,
                 font=("Segoe UI", 16, "bold")).pack()
        tk.Label(brand_frame, text="Event Management System", bg=COLOR_SIDEBAR, fg=COLOR_TEXT_LIGHT,
                 font=("Segoe UI", 9, "italic")).pack(pady=(0, 10))

        # Horizontal separator line
        tk.Frame(sidebar, bg=COLOR_SIDEBAR_ACTIVE, height=2).pack(fill="x", padx=15, pady=(0, 15))

        # Navigation Action Links Grid Builder
        self.nav_buttons = {}
        for item in self.nav_schema:
            if self.user["role"] in item["roles"]:
                btn = ttk.Button(
                    sidebar,
                    text=f"{item['icon']}  {item['label']}",
                    style="Nav.TButton",
                    command=lambda view_id=item["id"]: self._switch_view(view_id)
                )
                btn.pack(fill="x", padx=10, pady=2)
                self.nav_buttons[item["id"]] = btn

        # Footer User Information Profile Section block setup
        footer = tk.Frame(sidebar, bg=COLOR_SIDEBAR)
        footer.pack(side="bottom", fill="x", pady=15, padx=16)
        
        tk.Label(footer, text=self.user["full_name"], bg=COLOR_SIDEBAR, fg="white", 
                 font=FONT_BOLD, wraplength=200, justify="left").pack(anchor="w")
        
        subtext = (f"{self.user['course']} - {self.user['section']}" if self.user["role"] == "student" else "Faculty Supervisor")
        tk.Label(footer, text=subtext, bg=COLOR_SIDEBAR, fg=COLOR_TEXT_LIGHT, font=FONT_SMALL).pack(anchor="w", pady=(0, 10))
        
        ttk.Button(footer, text="⏻ Exit Session", style="Danger.TButton", command=self._logout).pack(fill="x")

        # ----- Main area -----
        main = tk.Frame(self, bg=COLOR_BG)
        main.pack(side="left", fill="both", expand=True)

        topbar = tk.Frame(main, bg=COLOR_CARD, height=60)
        topbar.pack(fill="x")
        topbar.pack_propagate(False)

        self.title_lbl = tk.Label(topbar, text="Dashboard", bg=COLOR_CARD, fg=COLOR_TEXT, font=("Segoe UI", 16, "bold"))
        self.title_lbl.pack(side="left", padx=20, pady=12)

        date_lbl = tk.Label(topbar, text=datetime.now().strftime("Active Server Window: %b %d, %Y"), bg=COLOR_CARD, fg=COLOR_TEXT_MUTED, font=FONT_SMALL)
        date_lbl.pack(side="right", padx=20)

        ttk.Button(topbar, text="↻ Refresh Data", style="Secondary.TButton", command=self._refresh_current_view).pack(side="right", padx=8)

        self.content = tk.Frame(main, bg=COLOR_BG)
        self.content.pack(fill="both", expand=True, padx=20, pady=20)

    def _switch_view(self, view_id):
        if self.current_view_id in self.nav_buttons:
            self.nav_buttons[self.current_view_id].configure(style="Nav.TButton")
        if view_id in self.nav_buttons:
            self.nav_buttons[view_id].configure(style="NavActive.TButton")

        self.current_view_id = view_id
        for w in self.content.winfo_children():
            w.destroy()

        item = next(x for x in self.nav_schema if x["id"] == view_id)
        self.title_lbl.configure(text=item["label"])

        # Dynamic structural router map trigger
        if view_id == "dashboard":
            self.view_dashboard(self.content)
        elif view_id == "events":
            self.view_events(self.content)
        elif view_id == "logistics":
            self.view_prepare_details(self.content)
        elif view_id == "registrar":
            self.view_stream_registrar(self.content)
        elif view_id == "checkin":
            self.view_digital_attendance(self.content)
        elif view_id == "announcements":
            self.view_push_bulletins(self.content)
        elif view_id == "feedback":
            self.view_system_feedback(self.content)
        elif view_id == "students":
            self.view_student_database(self.content)
        elif view_id == "teachers":
            self.view_teacher_database(self.content)

    def _refresh_current_view(self):
        if self.current_view_id:
            self._switch_view(self.current_view_id)

    def _logout(self):
        if messagebox.askyesno("Exit Session", "Terminate system dashboard interface runtime?"):
            self.on_logout()


    # =============================================================
    # 7. DASHBOARD MODULE
    # =============================================================
    def view_dashboard(self, parent):
        m = db.metrics()
        grid = tk.Frame(parent, bg=COLOR_BG)
        grid.pack(fill="x", pady=(0, 15))
        grid.columnconfigure((0, 1, 2, 3), weight=1, uniform="equal")

        cards_data = [
            ("Approved Events", str(m["total_approved"]), "\U0001F4C5", COLOR_SUCCESS),
            ("Pending Proposals", str(m["pending"]), "\u23F3", COLOR_WARNING),
            ("Total Registrants", str(m["total_participants"]), "\U0001F465", COLOR_PRIMARY),
            ("Attendance Rate", str(m["attendance_rate"]), "\U0001F4C8", COLOR_ACCENT),
        ]

        for i, (title, val, icon, color) in enumerate(cards_data):
            c = card(grid)
            c.grid(row=0, column=i, padx=6, sticky="nsew")
            accent_bar = tk.Frame(c, bg=color, height=4)
            accent_bar.pack(fill="x")
            
            body = tk.Frame(c, bg=COLOR_CARD)
            body.pack(fill="both", expand=True, padx=14, pady=12)
            
            top_row = tk.Frame(body, bg=COLOR_CARD)
            top_row.pack(fill="x")
            tk.Label(top_row, text=title, bg=COLOR_CARD, fg=COLOR_TEXT_MUTED, font=FONT_SMALL).pack(side="left")
            tk.Label(top_row, text=icon, bg=COLOR_CARD, fg=color, font=("Segoe UI", 14)).pack(side="right")
            
            tk.Label(body, text=val, bg=COLOR_CARD, fg=COLOR_TEXT, font=("Segoe UI", 24, "bold")).pack(anchor="w", pady=(6, 0))

        lower = tk.Frame(parent, bg=COLOR_BG)
        lower.pack(fill="both", expand=True)
        
        left = card(lower)
        left.pack(side="left", fill="both", expand=True, padx=(0, 8))
        card_header(left, "Active Approved Operations", "\u2699")

        cols = ("id", "title", "venue", "date", "time")
        heads = ("ID", "Event Title", "Venue / Location", "Date", "Time Schedule")

        # Toolbar goes above the table area
        approved_events = [dict(ev, _iid=str(ev["id"])) for ev in db.list_approved_events()]
        categories = sorted({ev["category"] for ev in approved_events if ev.get("category")})

        def ev_search(row, q):
            return q in (row["title"] or "").lower() or q in (row["venue"] or "").lower()

        def ev_filter(row, val):
            return row.get("category") == val

        sort_options = {
            "Date": lambda r: r["date"] or "",
            "Title (A-Z)": lambda r: (r["title"] or "").lower(),
            "Venue (A-Z)": lambda r: (r["venue"] or "").lower(),
        }

        def ev_values(row):
            return (row["id"], row["title"], row["venue"], row["date"],
                    row["time"] or "08:00 AM (Default)")

        ctrl = TableController(cols, ev_values, ev_search, sort_options,
                                filter_fn=ev_filter if categories else None,
                                default_sort="Date")
        make_table_with_toolbar(left, cols, heads, ctrl, widths=[30, 200, 120, 90, 100],
                                 search_placeholder="Search title or venue...",
                                 filter_label="Category" if categories else None,
                                 filter_values=categories if categories else None)
        ctrl.set_rows(approved_events)

        right = card(lower, width=280)
        right.pack(side="right", fill="y")
        right.pack_propagate(False)
        card_header(right, "Broadcast Bulletin", "\U0001F4E1")
        
        feed = tk.Frame(right, bg=COLOR_CARD)
        feed.pack(fill="both", expand=True, padx=10, pady=8)
        
        anns = list(reversed(db.list_announcements()))[:3]
        if not anns:
            tk.Label(feed, text="No active broadcast announcements issued.", bg=COLOR_CARD, fg=COLOR_TEXT_MUTED).pack(pady=20)
        for a in anns:
            item = tk.Frame(feed, bg=COLOR_CARD_ALT)
            item.pack(fill="x", pady=4)
            tk.Label(item, text=a["title"], bg=COLOR_CARD_ALT, fg=COLOR_PRIMARY_DARK, font=FONT_BOLD, anchor="w").pack(fill="x", padx=8, pady=(6, 0))
            tk.Label(item, text=a["date_posted"], bg=COLOR_CARD_ALT, fg=COLOR_TEXT_MUTED, font=("Segoe UI", 8), anchor="w").pack(fill="x", padx=8)
            tk.Label(item, text=a["content"], bg=COLOR_CARD_ALT, fg=COLOR_TEXT, font=FONT_SMALL, wraplength=240, justify="left", anchor="w").pack(
                fill="x", padx=8, pady=(2, 6))


    # =============================================================
    # 7b. DIGITAL ATTENDANCE MODULE (student self check-in)
    # =============================================================
    def view_digital_attendance(self, parent):
        wrap = tk.Frame(parent, bg=COLOR_BG)
        wrap.pack(fill="both", expand=True)

        student_id = self.user.get("student_id") or self.user.get("username")
        student_name = self.user.get("full_name") or self.user.get("username")
        student_program = self.user.get("course") or "N/A"

        left = card(wrap)
        left.pack(side="left", fill="both", expand=True, padx=(0, 8))
        card_header(left, "Approved Campus Events", "\U0001F4C5")

        cols = ("id", "title", "venue", "date")
        heads = ("ID", "Title", "Venue", "Date")
        tree = make_table(left, cols, heads, widths=[40, 220, 150, 100])

        right = card(wrap, width=320)
        right.pack(side="left", fill="y")
        right.pack_propagate(False)
        card_header(right, "Digital Self Check-In", "\U0001F4CB")

        detail_body = tk.Frame(right, bg=COLOR_CARD)
        detail_body.pack(fill="both", expand=True, padx=14, pady=10)

        empty_lbl = tk.Label(detail_body, text="Select an event on the left to check in.",
                              bg=COLOR_CARD, fg=COLOR_TEXT_MUTED, font=FONT_SMALL,
                              wraplength=270, justify="left")
        empty_lbl.pack(pady=30)

        events_by_id = {}

        def render_detail(ev):
            for w in detail_body.winfo_children():
                w.destroy()

            participant = db.find_participant_for_student_event(ev["id"], student_id)
            already_checked_in = bool(participant and participant["attendance_status"] == "Checked In")

            tk.Label(detail_body, text=ev["title"], bg=COLOR_CARD, fg=COLOR_PRIMARY_DARK,
                      font=FONT_BOLD, wraplength=270, justify="left", anchor="w").pack(fill="x")
            tk.Label(detail_body, text=f"\U0001F4CD {ev['venue']}", bg=COLOR_CARD, fg=COLOR_TEXT,
                      font=FONT_SMALL, anchor="w").pack(fill="x", pady=(2, 0))
            tk.Label(detail_body, text=f"\u23F0 {ev['time'] or 'TBA'}", bg=COLOR_CARD, fg=COLOR_TEXT,
                      font=FONT_SMALL, anchor="w").pack(fill="x", pady=(0, 10))

            if already_checked_in:
                tk.Label(detail_body, text="\u2713 You're already checked in to this event.",
                          bg=COLOR_CARD, fg=COLOR_SUCCESS, font=FONT_BOLD,
                          wraplength=270, justify="left", anchor="w").pack(fill="x", pady=(0, 10))
                ttk.Button(detail_body, text="\u2713 Checked In", style="Secondary.TButton",
                           state="disabled").pack(fill="x")
                return

            proof_e = labeled_entry(detail_body, "Proof / Reference (e.g., photo URL or note)")
            esig_e = labeled_entry(detail_body, "E-Signature (type your full name)")
            esig_e.insert(0, student_name or "")

            error_lbl = tk.Label(detail_body, text="", bg=COLOR_CARD, fg=COLOR_DANGER,
                                  font=FONT_SMALL, anchor="w", justify="left", wraplength=270)
            error_lbl.pack(fill="x", pady=(2, 0))

            def do_submit():
                esig = esig_e.get().strip()
                if not esig:
                    error_lbl.configure(text="Please type your full name as your e-signature.")
                    return
                db.self_checkin(ev["id"], student_id, student_name, student_program,
                                 proof_pic=proof_e.get().strip() or "N/A", esignature=esig)
                messagebox.showinfo("Checked In", f"You're checked in to \"{ev['title']}\".")
                render_detail(ev)

            ttk.Button(detail_body, text="\u2713 Submit Check-In", style="Success.TButton",
                       command=do_submit).pack(fill="x", pady=(8, 0))

        def on_select(event=None):
            sel = tree.selection()
            if not sel:
                return
            ev = events_by_id.get(int(sel[0]))
            if ev:
                render_detail(ev)

        tree.bind("<<TreeviewSelect>>", on_select)

        def refresh_list():
            tree.delete(*tree.get_children())
            events_by_id.clear()
            events = db.list_approved_events()
            if not events:
                for w in detail_body.winfo_children():
                    w.destroy()
                tk.Label(detail_body, text="No approved events are open for check-in right now.",
                          bg=COLOR_CARD, fg=COLOR_TEXT_MUTED, font=FONT_SMALL,
                          wraplength=270, justify="left").pack(pady=30)
                return
            for ev in events:
                events_by_id[ev["id"]] = ev
                tree.insert("", "end", iid=str(ev["id"]),
                            values=(ev["id"], ev["title"], ev["venue"], ev["date"]))

        refresh_list()


    # =============================================================
    # 8. EVENTS MODULE (proposal form, ledger table, admin approve/reject)
    # =============================================================
    def view_events(self, parent):
        wrap = tk.Frame(parent, bg=COLOR_BG)
        wrap.pack(fill="both", expand=True)

        left = card(wrap)
        left.pack(side="left", fill="both", expand=True, padx=(0, 8))
        card_header(left, "Events Configuration Ledger", "\U0001F4C5")

        columns = ("id", "title", "venue", "date", "proposed_by", "status")
        headings = ("ID", "Title", "Venue", "Date", "Proposed By", "Status")
        tree = make_table(left, columns, headings, widths=[30, 160, 90, 85, 110, 80])

        def refresh_tree():
            tree.delete(*tree.get_children())
            for ev in db.list_events():
                tree.insert("", "end", values=(ev["id"], ev["title"], ev["venue"], ev["date"], ev["proposed_by"], ev["status"]))

        refresh_tree()

        right = card(wrap, width=340)
        right.pack(side="left", fill="y")
        title_lbl = card_header(right, "File New Proposal / Event", "\u2795")

        # Create scrollable view frame for long event proposal structures
        canvas = tk.Canvas(right, bg=COLOR_CARD, bd=0, highlightthickness=0)
        vsb = ttk.Scrollbar(right, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg=COLOR_CARD)
        canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw", width=320)
        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        e_title = labeled_entry(scroll_frame, "Event Title *")
        e_venue = labeled_entry(scroll_frame, "Venue / Location *")
        e_date = labeled_entry(scroll_frame, "Date (YYYY-MM-DD) *")
        e_proposed_by = labeled_entry(scroll_frame, "Proposed By *")
        e_category = labeled_combo(scroll_frame, "Category Type *", CATEGORIES, default=CATEGORIES[0])
        e_link = labeled_entry(scroll_frame, "Virtual Link (optional)")
        e_desc = labeled_text(scroll_frame, "Description / Notes", height=2)

        # Audiences Checklist Grid Layout Builder Section Block Frame
        tk.Label(scroll_frame, text="Target Program Audiences", bg=COLOR_CARD, fg=COLOR_TEXT, font=FONT_SMALL).pack(anchor="w", padx=14, pady=(6, 2))
        aud_frame = tk.Frame(scroll_frame, bg=COLOR_CARD)
        aud_frame.pack(fill="x", padx=14, pady=(0, 6))
        audience_vars = {}
        for idx, aud in enumerate(AUDIENCES):
            var = tk.BooleanVar()
            audience_vars[aud] = var
            cb = ttk.Checkbutton(aud_frame, text=aud, variable=var)
            cb.grid(row=idx // 3, column=idx % 3, sticky="w", padx=2, pady=2)

        # Equipment Checklist Grid Layout Builder Section Block Frame
        tk.Label(scroll_frame, text="Logistics Equipment Checklist", bg=COLOR_CARD, fg=COLOR_TEXT, font=FONT_SMALL).pack(anchor="w", padx=14, pady=(6, 2))
        eq_frame = tk.Frame(scroll_frame, bg=COLOR_CARD)
        eq_frame.pack(fill="x", padx=14, pady=(0, 10))
        equip_vars = {}
        for idx, (eq_k, eq_v) in enumerate(EQUIPMENT_LABELS.items()):
            var = tk.BooleanVar()
            equip_vars[eq_k] = var
            cb = ttk.Checkbutton(eq_frame, text=eq_v, variable=var)
            cb.grid(row=idx // 2, column=idx % 2, sticky="w", padx=2, pady=2)

        submit_btn = ttk.Button(scroll_frame, text="\u2795 Submit Proposal", style="Primary.TButton")
        submit_btn.pack(fill="x", padx=14, pady=5)

        cancel_btn = ttk.Button(scroll_frame, text="\u2715 Cancel Edit", style="Secondary.TButton")

        def reset_form():
            for entry in (e_title, e_venue, e_date, e_proposed_by, e_link):
                entry.delete(0, "end")
            e_desc.delete("1.0", "end")
            e_category.set(CATEGORIES[0])
            for v in audience_vars.values():
                v.set(False)
            for v in equip_vars.values():
                v.set(False)
            title_lbl.configure(text="\u2795 File New Proposal / Event")
            submit_btn.configure(text="\U0001F4BE Save Event")
            cancel_btn.pack_forget()
            self.active_event_id = None
            refresh_tree()
            toggle_admin_dock()

        def load_into_form(ev):
            self.active_event_id = ev["id"]
            e_title.delete(0, "end"); e_title.insert(0, ev["title"] or "")
            e_venue.delete(0, "end"); e_venue.insert(0, ev["venue"] or "")
            e_date.delete(0, "end"); e_date.insert(0, ev["date"] or "")
            e_proposed_by.delete(0, "end"); e_proposed_by.insert(0, ev["proposed_by"] or "")
            e_category.set(ev["category"] or "")
            e_link.delete(0, "end"); e_link.insert(0, ev["virtual_link"] or "")
            e_desc.delete("1.0", "end"); e_desc.insert("1.0", ev["description"] or "")
            auds = (ev["audiences"] or "").split(",")
            for a, v in audience_vars.items():
                v.set(a in auds)
            eqs = (ev["equipment"] or "").split(",")
            for e, v in equip_vars.items():
                v.set(e in eqs)
            title_lbl.configure(text=f"\u270F Edit Event #{ev['id']}")
            submit_btn.configure(text="\U0001F4BE Update Event")
            cancel_btn.pack(fill="x", padx=14, pady=(8, 0))

        def do_submit():
            title = e_title.get().strip()
            venue = e_venue.get().strip()
            date_ = e_date.get().strip()
            proposed = e_proposed_by.get().strip()
            if not all([title, venue, date_, proposed]):
                messagebox.showwarning("Missing", "Please provide required operational gateway text field anchors.")
                return
            auds = [a for a, v in audience_vars.items() if v.get()]
            eqs = [e for e, v in equip_vars.items() if v.get()]
            if self.active_event_id:
                db.update_event(self.active_event_id, title, venue, date_, e_category.get(), e_desc.get("1.0", "end").strip(), e_link.get().strip(), proposed, auds, eqs)
                messagebox.showinfo("Success", "Proposal ledger matrix rows updated.")
            else:
                status = "Approved" if self.user["role"] == "admin" else "Pending"
                db.add_event(title, venue, date_, e_category.get(), e_desc.get("1.0", "end").strip(), e_link.get().strip(), proposed, auds, eqs, status)
                messagebox.showinfo("Success", "Proposal securely streamed into ledger stack nodes.")
            reset_form()

        submit_btn.configure(command=do_submit)
        cancel_btn.configure(command=reset_form)

        # Admin Evaluation Workspace Block Grid Logic Dock Container Hook Setup
        admin_dock = tk.Frame(left, bg=COLOR_CARD)
        def toggle_admin_dock():
            for w in admin_dock.winfo_children(): w.destroy()
            sel = tree.selection()
            if not sel or self.user["role"] != "admin":
                admin_dock.pack_forget()
                return
            ev = db.get_event(int(tree.selection()[0]))
            if not ev or ev["status"] != "Pending":
                admin_dock.pack_forget()
                return
            admin_dock.pack(fill="x", padx=14, pady=(0, 10))
            tk.Label(admin_dock, text=f"Evaluate Proposal #{ev['id']}:", bg=COLOR_CARD, font=FONT_BOLD).pack(side="left", padx=5)
            ttk.Button(admin_dock, text="\u2714 Approve", style="Success.TButton", command=lambda: [db.set_event_status(ev["id"], "Approved"), messagebox.showinfo("Approved", "Proposal live execution confirmed."), reset_form()]).pack(side="left", padx=4)
            ttk.Button(admin_dock, text="\u2715 Reject", style="Danger.TButton", command=lambda: [db.set_event_status(ev["id"], "Rejected"), messagebox.showinfo("Rejected", "Proposal archived out."), reset_form()]).pack(side="left", padx=4)

        def on_select(e):
            toggle_admin_dock()

        def edit_row(eid):
            ev = db.get_event(eid)
            if ev: load_into_form(ev)

        def delete_row(eid):
            ev = db.get_event(eid)
            if ev and messagebox.askyesno("Confirm", f'Permanently purge event "{ev["title"]}" matrix?'):
                db.delete_event(eid)
                reset_form()
                messagebox.showinfo("Deleted", f'Event "{ev["title"]}" has been permanently deleted from the database.')

        tree.bind("<<TreeviewSelect>>", on_select)
        action_row = tk.Frame(left, bg=COLOR_CARD)
        action_row.pack(fill="x", padx=10, pady=(0, 10))
        ttk.Button(action_row, text="\u270F Edit Selected", style="Secondary.TButton",
                   command=lambda: edit_row(int(tree.selection()[0])) if tree.selection() else None).pack(side="left", padx=(0, 6))
        ttk.Button(action_row, text="\U0001F5D1 Delete Selected", style="Danger.TButton",
                   command=lambda: delete_row(int(tree.selection()[0])) if tree.selection() else None).pack(side="left")
        toggle_admin_dock()


    # =============================================================
    # 9. LOGISTICS BLUEPRINTS (teacher: configure approved event details)
    # =============================================================
    def view_prepare_details(self, parent):
        wrap = card(parent)
        wrap.pack(fill="both", expand=True)
        card_header(wrap, "Logistics Blueprint Configuration", "\u2699")

        approved = db.list_approved_events()
        options = [f"#{ev['id']} - {ev['title']}" for ev in approved]
        selector = labeled_combo(wrap, "Choose Active Target Event", options)

        time_e = labeled_entry(wrap, "Time (e.g., 08:00 AM)")
        speakers_e = labeled_entry(wrap, "Speakers / Coordinator")
        agendas_t = labeled_text(wrap, "Agendas", height=2)
        supplies_t = labeled_text(wrap, "Supplies", height=2)
        resources_t = labeled_text(wrap, "Resources", height=2)

        def save():
            if not selector.get():
                messagebox.showwarning("No Selection", "Select a target operational gateway matrix index block.")
                return
            ev_id = int(selector.get().split(" - ")[0].lstrip("#"))
            db.update_logistics(ev_id, time_e.get().strip(), speakers_e.get().strip(), agendas_t.get("1.0", "end").strip(), supplies_t.get("1.0", "end").strip(), resources_t.get("1.0", "end").strip())
            messagebox.showinfo("Success", "Operational blueprint logs serialized securely.")
            self._refresh_current_view()

        def on_change(e):
            if not selector.get(): return
            ev_id = int(selector.get().split(" - ")[0].lstrip("#"))
            ev = db.get_event(ev_id)
            if ev:
                for entry, val in [(time_e, ev["time"]), (speakers_e, ev["speakers"])]:
                    entry.delete(0, "end"); entry.insert(0, val or "")
                for txt, val in [(agendas_t, ev["agendas"]), (supplies_t, ev["supplies"]), (resources_t, ev["resources"])]:
                    txt.delete("1.0", "end"); txt.insert("1.0", val or "")

        selector.bind("<<ComboboxSelected>>", on_change)
        ttk.Button(wrap, text="\U0001F4BE Commit Logistics Blueprint Matrix", style="Primary.TButton", command=save).pack(fill="x", padx=14, pady=15)


    # =============================================================
    # 10. STREAM REGISTRAR (admin/teacher: participant management)
    # =============================================================
    def view_stream_registrar(self, parent):
        wrap = tk.Frame(parent, bg=COLOR_BG)
        wrap.pack(fill="both", expand=True)

        left = card(wrap)
        left.pack(side="left", fill="both", expand=True, padx=(0, 8))
        card_header(left, "System Stream Registrar Ledger", "\U0001F4DD")

        columns = ("id", "event", "sid", "name", "status", "waiver", "fee", "clearance")
        headings = ("ID", "Target Event ID", "Student ID", "Full Name", "Status", "Waiver", "Fee", "Clearance")
        tree = make_table(left, columns, headings, widths=[30, 90, 80, 130, 95, 60, 50, 65])

        def refresh_tree():
            tree.delete(*tree.get_children())
            for p in db.list_participants():
                tree.insert("", "end", values=(p["id"], f"#{p['event_id']}", p["student_id"], p["name"], p["attendance_status"], badge_text(p["waiver"], "OK", "-"), badge_text(p["fee"], "Paid", "-"), badge_text(p["id_clearance"], "Clear", "-")))

        refresh_tree()

        right = card(wrap, width=340)
        right.pack(side="left", fill="y")
        title_lbl = card_header(right, "\u2795 Stream Registrar Row", "\u2795")

        ev_opts = [f"#{ev['id']} - {ev['title']}" for ev in db.list_events()]
        event_sel = labeled_combo(right, "Target Event Link *", ev_opts)
        sid_e = labeled_entry(right, "Student ID Key *")
        name_e = labeled_entry(right, "Student Full Name *")
        program_e = labeled_entry(right, "Program / Department Profile Block")

        chk_f = tk.Frame(right, bg=COLOR_CARD)
        chk_f.pack(fill="x", padx=14, pady=5)
        waiver_v = tk.BooleanVar(); ttk.Checkbutton(chk_f, text="Waiver Signed", variable=waiver_v).pack(anchor="w")
        fee_v = tk.BooleanVar(); ttk.Checkbutton(chk_f, text="Event Fee Settled", variable=fee_v).pack(anchor="w")
        clear_v = tk.BooleanVar(); ttk.Checkbutton(chk_f, text="ID Clearance Checked", variable=clear_v).pack(anchor="w")

        status_sel = labeled_combo(right, "Attendance Status", ATTENDANCE_STATUSES, default=ATTENDANCE_STATUSES[0])
        submit_btn = ttk.Button(right, text="\U0001F4BE Stream Registrar Row", style="Primary.TButton")
        submit_btn.pack(fill="x", padx=14, pady=(10, 4))
        cancel_btn = ttk.Button(right, text="\u2715 Cancel Edit", style="Secondary.TButton")

        def reset_form():
            self.editing_participant_id = None
            event_sel.set(""); sid_e.delete(0, "end"); name_e.delete(0, "end"); program_e.delete(0, "end")
            waiver_v.set(False); fee_v.set(False); clear_v.set(False)
            status_sel.set(ATTENDANCE_STATUSES[0])
            title_lbl.configure(text="\u2795 Stream Registrar Row")
            submit_btn.configure(text="\U0001F4BE Stream Registrar Row")
            cancel_btn.pack_forget()
            refresh_tree()

        def do_submit():
            if not event_sel.get():
                messagebox.showwarning("Missing", "Please select a target event.")
                return
            ev_id = int(event_sel.get().split(" - ")[0].lstrip("#"))
            sid = sid_e.get().strip()
            name = name_e.get().strip()
            program = program_e.get().strip()
            if not sid or not name:
                messagebox.showwarning("Missing", "Student ID and Name are required.")
                return
            if self.editing_participant_id:
                db.update_participant(self.editing_participant_id, ev_id, sid, name, program, waiver_v.get(), fee_v.get(), clear_v.get(), status_sel.get())
                messagebox.showinfo("Updated", "Participant record updated successfully.")
            else:
                db.add_participant(sid, name, program, ev_id, waiver_v.get(), fee_v.get(), clear_v.get(), status_sel.get())
                messagebox.showinfo("Streamed", "Participant structured registry logging confirmed.")
            reset_form()

        submit_btn.configure(command=do_submit)
        cancel_btn.configure(command=reset_form)

        def edit_row(pid):
            p = db.get_participant(pid)
            if not p: return
            self.editing_participant_id = pid
            target_ev = db.get_event(p["event_id"])
            if target_ev: event_sel.set(f"#{target_ev['id']} - {target_ev['title']}")
            sid_e.delete(0, "end"); sid_e.insert(0, p["student_id"])
            name_e.delete(0, "end"); name_e.insert(0, p["name"])
            program_e.delete(0, "end"); program_e.insert(0, p["program"])
            waiver_v.set(bool(p["waiver"]))
            fee_v.set(bool(p["fee"]))
            clear_v.set(bool(p["id_clearance"]))
            status_sel.set(p["attendance_status"])
            title_lbl.configure(text=f"\u270F Edit Registrar Row #{pid}")
            submit_btn.configure(text="\U0001F4BE Update Registrar Row")
            cancel_btn.pack(fill="x", padx=14, pady=(0, 8))

        def delete_row(pid):
            if messagebox.askyesno("Purge", f"Permanently delete registrar block record #{pid}?"):
                db.delete_participant(pid)
                reset_form()

        action_row = tk.Frame(left, bg=COLOR_CARD)
        action_row.pack(fill="x", padx=10, pady=(0, 10))
        ttk.Button(action_row, text="\u270F Edit Selected", style="Secondary.TButton", command=lambda: edit_row(int(tree.selection()[0])) if tree.selection() else None).pack(side="left", padx=(0, 6))
        ttk.Button(action_row, text="\U0001F5D1 Delete Selected", style="Danger.TButton", command=lambda: delete_row(int(tree.selection()[0])) if tree.selection() else None).pack(side="left")


    # =============================================================
    # 11. DIGITAL ATTENDANCE (student self check-in view module)
    # =============================================================
    def view_registration(self, parent):
        """
        Fixed Dual-Pane View for Account Registration and Faculty Profiles.
        Ensures a clean, fitted layout with scrollable form controls to eliminate clipping.
        """
        # Clear prior view remnants safely
        for w in parent.winfo_children():
            w.destroy()

        # Proportional 2-Column Grid Split: 60% Left Table, 40% Right Panel Form
        parent.columnconfigure(0, weight=60)
        parent.columnconfigure(1, weight=40)
        parent.rowconfigure(0, weight=1)

        # -------------------------------------------------------------
        # LEFT SIDE PANEL: REGISTERED PROFILES LEDGER
        # -------------------------------------------------------------
        left_panel = tk.Frame(parent, bg=COLOR_BG)
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=5)

        lbl_title = tk.Label(
            left_panel, 
            text="👥 Registered Faculty & Users Ledger", 
            bg=COLOR_BG, 
            fg=COLOR_TEXT, 
            font=("Segoe UI", 12, "bold")
        )
        lbl_title.pack(anchor="w", pady=(0, 10))

        # Base Card Context for Treeview
        table_card = tk.Frame(left_panel, bg=COLOR_CARD, bd=1, relief="solid")
        table_card.pack(fill="both", expand=True, pady=(0, 10))

        scroll_y = ttk.Scrollbar(table_card, orient="vertical")
        scroll_x = ttk.Scrollbar(table_card, orient="horizontal")

        columns = ("username", "name", "role", "dept", "status")
        tree = ttk.Treeview(
            table_card, 
            columns=columns, 
            show="headings", 
            yscrollcommand=scroll_y.set, 
            xscrollcommand=scroll_x.set
        )

        scroll_y.config(command=tree.yview)
        scroll_y.pack(side="right", fill="y")
        scroll_x.config(command=tree.xscroll)
        scroll_x.pack(side="bottom", fill="x")
        tree.pack(fill="both", expand=True)

        headers = {
            "username": ("Username / ID", 110),
            "name": ("Full Name", 150),
            "role": ("System Role", 90),
            "dept": ("Department", 100),
            "status": ("Status", 80)
        }
        for col, (text, width) in headers.items():
            tree.heading(col, text=text, anchor="w")
            tree.column(col, width=width, anchor="w")

        def refresh_tree():
            tree.delete(*tree.get_children())
            for u in db.list_users():
                tree.insert("", "end", iid=u["username"], values=(
                    u["username"], u["name"], u["role"], u["department"] or "\u2014", u["status"]
                ))

        refresh_tree()

        # -------------------------------------------------------------
        # RIGHT SIDE PANEL: ENROLLMENT / REGISTRATION FORM WITH SCROLLBAR
        # -------------------------------------------------------------
        right_card = tk.Frame(parent, bg=COLOR_CARD, bd=1, relief="solid")
        right_card.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=5)

        form_head = tk.Frame(right_card, bg=COLOR_CARD)
        form_head.pack(fill="x", padx=14, pady=(14, 8))
        title_lbl = tk.Label(
            form_head, 
            text="➕ Register New Account Profile", 
            bg=COLOR_CARD, 
            fg=COLOR_PRIMARY, 
            font=("Segoe UI", 13, "bold")
        )
        title_lbl.pack(side="left")

        # Scroll viewport infrastructure setup to avoid clipping complex layouts
        canvas = tk.Canvas(right_card, bg=COLOR_CARD, highlightthickness=0)
        scrollbar = ttk.Scrollbar(right_card, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg=COLOR_CARD)

        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw", width=340)
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True, padx=14, pady=(0, 14))

        # Core Row Template Generator
        def render_row(label_text, is_password=False):
            lbl = tk.Label(scroll_frame, text=label_text, bg=COLOR_CARD, fg=COLOR_TEXT, font=FONT_SMALL)
            lbl.pack(anchor="w", pady=(5, 1))
            show_char = "*" if is_password else ""
            ent = ttk.Entry(scroll_frame, show=show_char)
            ent.pack(fill="x", pady=(0, 5))
            return ent

        e_user = render_row("Username / Employee ID *")
        e_pass = render_row("Account Password *", is_password=True)
        e_name = render_row("Full Professional Name *")
        e_email = render_row("Email Address")
        e_phone = render_row("Contact / Mobile Number")

        # Dropdowns Selection Options
        lbl_role = tk.Label(scroll_frame, text="System Authorization Role *", bg=COLOR_CARD, fg=COLOR_TEXT, font=FONT_SMALL)
        lbl_role.pack(anchor="w", pady=(5, 1))
        e_role = ttk.Combobox(scroll_frame, values=["teacher", "admin"], state="readonly")
        e_role.pack(fill="x", pady=(0, 5))
        e_role.set("teacher")

        lbl_dept = tk.Label(scroll_frame, text="Assigned Core Department *", bg=COLOR_CARD, fg=COLOR_TEXT, font=FONT_SMALL)
        lbl_dept.pack(anchor="w", pady=(5, 1))
        e_dept = ttk.Combobox(scroll_frame, values=["ITE", "HM", "BA", "CRIM", "EDUC", "GAS"], state="readonly")
        e_dept.pack(fill="x", pady=(0, 5))

        lbl_status = tk.Label(scroll_frame, text="Account Status *", bg=COLOR_CARD, fg=COLOR_TEXT, font=FONT_SMALL)
        lbl_status.pack(anchor="w", pady=(5, 1))
        e_status = ttk.Combobox(scroll_frame, values=["Active", "Suspended"], state="readonly")
        e_status.pack(fill="x", pady=(0, 5))
        e_status.set("Active")

        # --- Dynamic Multi-Column Handling for Courses Checklist ---
        lbl_hand = tk.Label(scroll_frame, text="Handled Department Programs (Check all)", bg=COLOR_CARD, fg=COLOR_TEXT, font=FONT_SMALL)
        lbl_hand.pack(anchor="w", pady=(8, 2))

        course_grid = tk.Frame(scroll_frame, bg=COLOR_CARD)
        course_grid.pack(fill="x", pady=(0, 5))

        course_vars = {}
        for idx, course in enumerate(COURSES):
            r = idx // 3
            c = idx % 3
            v = tk.BooleanVar()
            course_vars[course] = v
            cb = ttk.Checkbutton(course_grid, text=course, variable=v)
            cb.grid(row=r, column=c, sticky="w", padx=(0, 12), pady=3)

        # --- Dynamic Multi-Column Handling for Year Levels Checklist ---
        lbl_yrs = tk.Label(scroll_frame, text="Handled Student Year Levels (Check all)", bg=COLOR_CARD, fg=COLOR_TEXT, font=FONT_SMALL)
        lbl_yrs.pack(anchor="w", pady=(8, 2))

        year_grid = tk.Frame(scroll_frame, bg=COLOR_CARD)
        year_grid.pack(fill="x", pady=(0, 10))

        year_vars = {}
        for idx, yr in enumerate(YEARS):
            r = idx // 2
            c = idx % 2
            v = tk.BooleanVar()
            year_vars[yr] = v
            cb = ttk.Checkbutton(year_grid, text=yr, variable=v)
            cb.grid(row=r, column=c, sticky="w", padx=(0, 12), pady=3)

        # Actions Configuration Layout Frame
        btn_row = tk.Frame(scroll_frame, bg=COLOR_CARD)
        btn_row.pack(fill="x", pady=12)
        
        submit_btn = ttk.Button(btn_row, text="💾 Save Account", style="Primary.TButton")
        submit_btn.pack(fill="x")
        
        cancel_btn = ttk.Button(btn_row, text="✕ Cancel Changes", style="Secondary.TButton")

        def reset_form():
            self.reg_form_mode = "INSERT"
            e_user.configure(state="normal")
            e_user.delete(0, "end"); e_pass.delete(0, "end"); e_name.delete(0, "end")
            e_email.delete(0, "end"); e_phone.delete(0, "end")
            e_role.set("teacher"); e_dept.set(""); e_status.set("Active")
            for v in course_vars.values(): v.set(False)
            for v in year_vars.values(): v.set(False)
            title_lbl.configure(text="➕ Register New Account Profile")
            submit_btn.configure(text="💾 Save Account")
            cancel_btn.pack_forget()
            refresh_tree()

        def load_into_form(u):
            self.reg_form_mode = "EDIT"
            e_user.delete(0, "end"); e_user.insert(0, u["username"])
            e_user.configure(state="disabled") # Keep unique keys protected
            e_pass.delete(0, "end"); e_pass.insert(0, u["password"])
            e_name.delete(0, "end"); e_name.insert(0, u["name"])
            e_email.delete(0, "end"); e_email.insert(0, u["email"] or "")
            e_phone.delete(0, "end"); e_phone.insert(0, u["phone"] or "")
            e_role.set(u["role"])
            e_dept.set(u["department"] or "")
            e_status.set(u["status"] or "Active")
            
            c_list = (u["courses_handled"] or "").split(",")
            for c, v in course_vars.items():
                v.set(c in c_list)
                
            y_list = (u["years_handled"] or "").split(",")
            for y, v in year_vars.items():
                v.set(y in y_list)

            title_lbl.configure(text=f"📝 Profile Update: {u['username']}")
            submit_btn.configure(text="💾 Update Profile Changes")
            cancel_btn.pack(fill="x", pady=(6, 0))

        def do_submit():
            uname = e_user.get().strip()
            upass = e_pass.get().strip()
            uname_real = e_name.get().strip()
            if not uname or not upass or not uname_real:
                messagebox.showwarning("Missing Requirements", "Please input values for Username, Password, and Full Name fields.")
                return

            sel_courses = [c for c, v in course_vars.items() if v.get()]
            sel_years = [y for y, v in year_vars.items() if v.get()]

            if self.reg_form_mode == "EDIT":
                db.update_user(uname, upass, uname_real, e_role.get(), e_dept.get(),
                               sel_courses, sel_years, e_email.get().strip(), e_phone.get().strip(), e_status.get())
                messagebox.showinfo("Success", f"Profile for '{uname}' updated completely.")
            else:
                # Deduplicate and test against prior instances
                existing = db.list_users()
                if any(x["username"].lower() == uname.lower() for x in existing):
                    messagebox.showerror("Conflict", f"Username/ID '{uname}' already exists.")
                    return
                db.register_user(uname, upass, uname_real, e_role.get(), e_dept.get(),
                                 sel_courses, sel_years, e_email.get().strip(), e_phone.get().strip(), e_status.get())
                messagebox.showinfo("Success", f"Account credentials setup for '{uname}' successfully.")
            reset_form()

        submit_btn.configure(command=do_submit)
        cancel_btn.configure(command=reset_form)

        def edit_row(uname):
            users = db.list_users()
            match = next((x for x in users if x["username"] == uname), None)
            if match:
                load_into_form(match)

        # Ledger operational row buttons actions
        action_row = tk.Frame(left_panel, bg=COLOR_BG)
        action_row.pack(fill="x", pady=5)
        
        ttk.Button(action_row, text="📝 Edit Selected", style="Secondary.TButton",
                   command=lambda: edit_row(tree.selection()[0]) if tree.selection() else None
                   ).pack(side="left", padx=(0, 8))
                   
        ttk.Button(action_row, text="🗑️ Purge Profile", style="Danger.TButton",
                   command=lambda: [db.delete_user(tree.selection()[0]), reset_form()] if tree.selection() and messagebox.askyesno("Confirm Action", "Are you sure you want to completely purge this profile?") else None
                   ).pack(side="left")

        # Global Mousewheel Scroll Bindings Integration
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        reset_form()

    # =============================================================
    # 12. PUSH BULLETINS (admin: announcements management)
    # =============================================================
    def view_push_bulletins(self, parent):
        wrap = tk.Frame(parent, bg=COLOR_BG)
        wrap.pack(fill="both", expand=True)

        left = card(wrap)
        left.pack(side="left", fill="both", expand=True, padx=(0, 8))
        card_header(left, "Active Archive Broadcast Bulletins", "\U0001F4E1")

        columns = ("id", "title", "date")
        headings = ("ID", "Bulletin Header Title", "Date Extracted/Posted")
        tree = make_table(left, columns, headings, widths=[40, 300, 160])

        def refresh_tree():
            tree.delete(*tree.get_children())
            for a in db.list_announcements():
                tree.insert("", "end", iid=a["id"], values=(a["id"], a["title"], a["date_posted"]))

        refresh_tree()

        right = card(wrap, width=340)
        right.pack(side="left", fill="y")
        title_lbl = card_header(right, "\U0001F4E1 Push Live Notice", "\U0001F4E1")

        ann_title = labeled_entry(right, "Bulletin Subject Title Line *")
        ann_content = labeled_text(right, "Content Body Document *", height=8)

        submit_btn = ttk.Button(right, text="\U0001F4E1 Push Live Notice", style="Primary.TButton")
        submit_btn.pack(fill="x", padx=14, pady=(12, 4))
        cancel_btn = ttk.Button(right, text="\u2715 Cancel Edit", style="Secondary.TButton")

        def reset_form():
            self.editing_announcement_id = None
            ann_title.delete(0, "end")
            ann_content.delete("1.0", "end")
            title_lbl.configure(text="\U0001F4E1 Push Live Notice")
            submit_btn.configure(text="\U0001F4E1 Push Live Notice")
            cancel_btn.pack_forget()
            refresh_tree()

        def do_submit():
            t = ann_title.get().strip()
            c = ann_content.get("1.0", "end").strip()
            if not t or not c:
                messagebox.showwarning("Missing", "Title and content are required.")
                return
            if self.editing_announcement_id:
                db.update_announcement(self.editing_announcement_id, t, c)
                messagebox.showinfo("Updated", "Announcement updated successfully.")
            else:
                db.add_announcement(t, c)
                messagebox.showinfo("Pushed", "Broadcast bulletin pushed live successfully.")
            reset_form()

        submit_btn.configure(command=do_submit)
        cancel_btn.configure(command=reset_form)

        def edit_row(aid):
            anns = {a["id"]: a for a in db.list_announcements()}
            a = anns.get(aid)
            if not a: return
            self.editing_announcement_id = aid
            ann_title.delete(0, "end"); ann_title.insert(0, a["title"])
            ann_content.delete("1.0", "end"); ann_content.insert("1.0", a["content"])
            title_lbl.configure(text=f"\u270F Update Bulletin #{aid}")
            submit_btn.configure(text="\U0001F4BE Update Bulletin")
            cancel_btn.pack(fill="x", padx=14, pady=(0, 8))

        def delete_row(aid):
            anns = {a["id"]: a for a in db.list_announcements()}
            a = anns.get(aid)
            if not a: return
            if messagebox.askyesno("Confirm Delete", f'Delete announcement "{a["title"]}"?'):
                db.delete_announcement(aid)
                reset_form()

        action_row = tk.Frame(left, bg=COLOR_CARD)
        action_row.pack(fill="x", padx=10, pady=(0, 10))
        ttk.Button(action_row, text="\u270F Edit Selected", style="Secondary.TButton", command=lambda: edit_row(int(tree.selection()[0])) if tree.selection() else None).pack(side="left", padx=(0, 6))
        ttk.Button(action_row, text="\U0001F5D1 Delete Selected", style="Danger.TButton", command=lambda: delete_row(int(tree.selection()[0])) if tree.selection() else None).pack(side="left")


    # =============================================================
    # 13. FEEDBACK MODULE
    # =============================================================
    def view_system_feedback(self, parent):
        wrap = tk.Frame(parent, bg=COLOR_BG)
        wrap.pack(fill="both", expand=True)

        left = card(wrap)
        left.pack(side="left", fill="both", expand=True, padx=(0, 8))
        card_header(left, "Anonymized Analytics Logs Matrix", "\U0001F4AC")

        columns = ("id", "event", "rating", "comments")
        headings = ("Feedback ID", "Target Event Index", "Score Rating (1-5)", "Evaluator Text Comments")
        tree = make_table(left, columns, headings, widths=[80, 120, 110, 240])

        feedbacks = db.list_feedbacks()
        for f in feedbacks:
            tree.insert("", "end", values=(f["id"], f"Event #{f['event_id']}", f"{f['rating']} / 5 \u2605", f["comments"]))

        if self.user["role"] == "student":
            right = card(wrap, width=340)
            right.pack(side="left", fill="y")
            card_header(right, "Deploy Evaluation Matrix", "\u270D")

            approved = db.list_approved_events()
            opts = [f"#{ev['id']} - {ev['title']}" for ev in approved]
            target_ev = labeled_combo(right, "Active Operational Event Link *", opts)
            rating_v = labeled_combo(right, "Metrics Rating Unit Scale *", ["5 - Excellent", "4 - Good", "3 - Average", "2 - Fair", "1 - Poor"], default="5 - Excellent")
            comment_t = labeled_text(right, "Comments / Text Analysis Documentation *", height=6)

            def submit_fb():
                if not target_ev.get():
                    messagebox.showwarning("Missing", "Select target event node vector index configuration link.")
                    return
                ev_id = int(target_ev.get().split(" - ")[0].lstrip("#"))
                score = int(rating_v.get().split(" - ")[0])
                db.add_feedback(self.user["username"], ev_id, score, comment_t.get("1.0", "end").strip())
                messagebox.showinfo("Success", "Feedback evaluation securely streamed into analytics stack.")
                self._refresh_current_view()

            ttk.Button(right, text="\U0001F4AC Stream Feedback Form Rows", style="Success.TButton", command=submit_fb).pack(fill="x", padx=14, pady=15)
        else:
            if not feedbacks:
                tk.Label(left, text="No quantitative assessment loops logged yet.", bg=COLOR_CARD, fg=COLOR_TEXT_MUTED).pack(parent, pady=20)


    # =============================================================
    # 14. STUDENT DATABASE MODULE (admin option view block)
    # =============================================================
    def view_student_database(self, parent):
        wrap = tk.Frame(parent, bg=COLOR_BG)
        wrap.pack(fill="both", expand=True)

        left = card(wrap)
        left.pack(side="left", fill="both", expand=True, padx=(0, 8))
        card_header(left, "Student Registry Master File", "\U0001F393")

        columns = ("name", "username", "id", "course", "section")
        headings = ("Full Name (Surname First)", "Username Node Link", "Student ID", "Program", "Section Block")

        courses_present = sorted({s["course"] for s in db.list_students() if s["course"]})

        def s_values(row):
            return (row["full_name"], row["username"], row["student_id"] or "N/A",
                    row["course"] or "N/A", f"{row['year'] or ''} - {row['section'] or ''}")

        def s_search(row, q):
            haystacks = [row["full_name"] or "", row["username"] or "",
                         row["student_id"] or "", row["course"] or "", row["section"] or ""]
            return any(q in h.lower() for h in haystacks)

        def s_filter(row, val):
            return row["course"] == val

        sort_options = {
            "Name (A-Z)": lambda r: (r["full_name"] or "").lower(),
            "Username (A-Z)": lambda r: (r["username"] or "").lower(),
            "Student ID": lambda r: (r["student_id"] or ""),
            "Course": lambda r: (r["course"] or "").lower(),
        }

        ctrl = TableController(columns, s_values, s_search, sort_options,
                                filter_fn=s_filter if courses_present else None,
                                default_sort="Name (A-Z)")
        tree = make_table_with_toolbar(left, columns, headings, ctrl,
                                        widths=[140, 100, 95, 75, 75],
                                        search_placeholder="Search name, username, ID...",
                                        filter_label="Course" if courses_present else None,
                                        filter_values=courses_present if courses_present else None)

        def refresh_tree():
            rows = [dict(s, _iid=s["username"]) for s in db.list_students()]
            ctrl.set_rows(rows)

        refresh_tree()

        right = card(wrap, width=340)
        right.pack(side="left", fill="y")
        title_lbl = card_header(right, "\U0001F393 Student Account Terminal", "\U0001F393")

        surname_e = labeled_entry(right, "Surname *")
        firstname_e = labeled_entry(right, "First Name *")
        mi_e = labeled_entry(right, "M.I.")
        course_e = labeled_combo(right, "Course *", COURSES, default=COURSES[0])
        year_e = labeled_combo(right, "Year *", YEARS, default=YEARS[0])
        section_e = labeled_entry(right, "Section *")
        sid_e = labeled_entry(right, "Student ID *")
        username_e = labeled_entry(right, "Username *")
        password_e = labeled_entry(right, "Password (new accounts only)", show="\u2022")

        submit_btn = ttk.Button(right, text="\U0001F4BE Save Student Record", style="Primary.TButton")
        submit_btn.pack(fill="x", padx=14, pady=(10, 4))
        cancel_btn = ttk.Button(right, text="\u2715 Cancel Edit", style="Secondary.TButton")

        def reset_form():
            self.editing_student_username = None
            for e in (surname_e, firstname_e, mi_e, section_e, sid_e, username_e, password_e):
                e.delete(0, "end")
            course_e.set(COURSES[0]); year_e.set(YEARS[0])
            username_e.configure(state="normal")
            title_lbl.configure(text="\U0001F393 Student Account Terminal")
            submit_btn.configure(text="\U0001F4BE Save Student Record")
            cancel_btn.pack_forget()
            refresh_tree()

        def do_submit():
            surname = surname_e.get().strip()
            firstname = firstname_e.get().strip()
            mi = mi_e.get().strip()
            course = course_e.get()
            year = year_e.get()
            section = section_e.get().strip()
            student_id = sid_e.get().strip()
            username = username_e.get().strip().lower()

            if self.editing_student_username:
                db.upsert_student(surname, firstname, mi, course, year, section, student_id, username, edit_username=self.editing_student_username)
                messagebox.showinfo("Success", "Account variables parsed safely.")
                reset_form()
            else:
                if not username or not password_e.get():
                    messagebox.showwarning("Missing Credentials", "New profiles require an initial authentication pair blueprint stack.")
                    return
                if db.username_exists(username):
                    messagebox.showerror("Conflict", "Username key exists inside directory ledger framework.")
                    return
                db.upsert_student(surname, firstname, mi, course, year, section, student_id, username, password=password_e.get())
                messagebox.showinfo("Success", "Account created successfully.")
                reset_form()

        submit_btn.configure(command=do_submit)
        cancel_btn.configure(command=reset_form)

        def edit_row(uname):
            u = db.get_user(uname)
            if not u: return
            self.editing_student_username = uname
            surname_e.insert(0, u["surname"] or ""); firstname_e.insert(0, u["firstname"] or ""); mi_e.insert(0, u["mi"] or "")
            course_e.set(u["course"] or COURSES[0]); year_e.set(u["year"] or YEARS[0])
            section_e.insert(0, u["section"] or ""); sid_e.insert(0, u["student_id"] or "")
            username_e.insert(0, u["username"]); username_e.configure(state="disabled")
            title_lbl.configure(text=f"\u270F Update Profile: {uname}")
            submit_btn.configure(text="\U0001F4BE Update Student Record")
            cancel_btn.pack(fill="x", padx=14, pady=(0, 8))

        action_row = tk.Frame(left, bg=COLOR_CARD)
        action_row.pack(fill="x", padx=10, pady=(0, 10))
        ttk.Button(action_row, text="\u270F Edit Profile", style="Secondary.TButton", command=lambda: edit_row(tree.selection()[0]) if tree.selection() else None).pack(side="left", padx=(0, 6))
        ttk.Button(action_row, text="\U0001F5D1 Wipe Profile", style="Danger.TButton", command=lambda: [db.delete_user(tree.selection()[0]), reset_form()] if tree.selection() and messagebox.askyesno("Confirm", "Purge account directory?") else None).pack(side="left")


    # =============================================================
    # 15. TEACHER DATABASE MODULE (admin option view block)
    # =============================================================
    def view_teacher_database(self, parent):
        wrap = tk.Frame(parent, bg=COLOR_BG)
        wrap.pack(fill="both", expand=True)

        left = card(wrap)
        left.pack(side="left", fill="both", expand=True, padx=(0, 8))
        card_header(left, "Faculty Master Ledger Stack", "\U0001F468\u200D\U0001F3EB")

        columns = ("name", "username", "department")
        headings = ("Full Name", "Username ID Node", "Department")

        depts_present = sorted({t["department"] for t in db.list_teachers() if t["department"]})

        def t_values(row):
            return (row["full_name"], row["username"], row["department"] or "Faculty Supervisor")

        def t_search(row, q):
            haystacks = [row["full_name"] or "", row["username"] or "", row["department"] or ""]
            return any(q in h.lower() for h in haystacks)

        def t_filter(row, val):
            return row["department"] == val

        sort_options = {
            "Name (A-Z)": lambda r: (r["full_name"] or "").lower(),
            "Username (A-Z)": lambda r: (r["username"] or "").lower(),
            "Department": lambda r: (r["department"] or "").lower(),
        }

        ctrl = TableController(columns, t_values, t_search, sort_options,
                                filter_fn=t_filter if depts_present else None,
                                default_sort="Name (A-Z)")
        tree = make_table_with_toolbar(left, columns, headings, ctrl, widths=[180, 120, 180],
                                        search_placeholder="Search name, username, dept...",
                                        filter_label="Department" if depts_present else None,
                                        filter_values=depts_present if depts_present else None)

        def refresh_tree():
            rows = [dict(t, _iid=t["username"]) for t in db.list_teachers()]
            ctrl.set_rows(rows)

        refresh_tree()

        right = card(wrap, width=360)
        right.pack(side="left", fill="y")
        title_lbl = card_header(right, "Teacher Account Terminal", "\U0001F468\u200D\U0001F3EB")

        fullname_e = labeled_entry(right, "Full Name *")
        department_e = labeled_entry(right, "Department / Role (optional)")
        username_e = labeled_entry(right, "Username *")
        password_e = labeled_entry(right, "Password *", show="\u2022")

        submit_btn = ttk.Button(right, text="\U0001F4BE Save Teacher Account", style="Primary.TButton")
        submit_btn.pack(fill="x", padx=14, pady=(10, 4))
        cancel_btn = ttk.Button(right, text="\u2715 Cancel Edit", style="Secondary.TButton")

        def reset_form():
            self.editing_teacher_username = None
            fullname_e.delete(0, "end"); department_e.delete(0, "end")
            username_e.delete(0, "end"); username_e.configure(state="normal")
            password_e.delete(0, "end")
            title_lbl.configure(text="Teacher Account Terminal")
            submit_btn.configure(text="\U0001F4BE Save Teacher Account")
            cancel_btn.pack_forget()
            refresh_tree()

        def do_submit():
            fn = fullname_e.get().strip()
            dept = department_e.get().strip()
            uname = username_e.get().strip().lower()
            pwd = password_e.get()

            if not fn or not uname:
                messagebox.showwarning("Missing Fields", "Full Name and Username are required structural keys.")
                return

            if self.editing_teacher_username:
                db.upsert_teacher(fn, dept, uname, password=pwd, edit_username=self.editing_teacher_username)
                messagebox.showinfo("Success", "Faculty structural matrix record saved.")
                reset_form()
            else:
                if not pwd:
                    messagebox.showwarning("Missing Password", "An access password token security variable must be initialized.")
                    return
                if db.username_exists(uname):
                    messagebox.showerror("Conflict", "Username identifier collision triggered.")
                    return
                db.upsert_teacher(fn, dept, uname, password=pwd)
                messagebox.showinfo("Success", "Faculty system access entry compiled.")
                reset_form()

        submit_btn.configure(command=do_submit)
        cancel_btn.configure(command=reset_form)

        def edit_row(uname):
            u = db.get_user(uname)
            if not u: return
            self.editing_teacher_username = uname
            fullname_e.insert(0, u["full_name"] or "")
            department_e.insert(0, u["department"] or "")
            username_e.insert(0, u["username"]); username_e.configure(state="disabled")
            title_lbl.configure(text=f"\u270F Edit Faculty Entry: {uname}")
            submit_btn.configure(text="\U0001F4BE Update Teacher Account")
            cancel_btn.pack(fill="x", padx=14, pady=(0, 8))

        action_row = tk.Frame(left, bg=COLOR_CARD)
        action_row.pack(fill="x", padx=10, pady=(0, 10))
        ttk.Button(action_row, text="\u270F Edit Profile", style="Secondary.TButton", command=lambda: edit_row(tree.selection()[0]) if tree.selection() else None).pack(side="left", padx=(0, 6))
        ttk.Button(action_row, text="\U0001F5D1 Purge Profile", style="Danger.TButton", command=lambda: [db.delete_user(tree.selection()[0]), reset_form()] if tree.selection() and messagebox.askyesno("Confirm", "Archive faculty profile block out?") else None).pack(side="left")


# =================================================================
# 16. MAIN APPLICATION SHELL
# =================================================================

class SemsApp(tk.Tk):
    AFK_TIMEOUT_MS = 1 * 60 * 1000  # 5 minutes of no mouse/keyboard activity

    def __init__(self):
        super().__init__()
        self.title("SEMS - School Event Management System | College of St. Catherine - QC")
        self.geometry("1200x720")
        self.minsize(1000, 620)
        self.configure(bg=COLOR_BG)
        init_styles(self)

        self.container = tk.Frame(self, bg=COLOR_BG)
        self.container.pack(fill="both", expand=True)

        self._afk_job = None
        self._afk_armed = False

        # bind_all fires on every widget in the app regardless of focus,
        # so any click, keystroke, or mouse movement counts as activity.
        self.bind_all("<Motion>", self._on_activity, add="+")
        self.bind_all("<KeyPress>", self._on_activity, add="+")
        self.bind_all("<Button>", self._on_activity, add="+")
        self.bind_all("<MouseWheel>", self._on_activity, add="+")

        self.show_auth()

    def show_auth(self):
        self._disarm_afk_timer()
        for w in self.container.winfo_children():
            w.destroy()
        AuthView(self.container, on_login_success=self.on_login_success)

    def on_login_success(self, user):
        for w in self.container.winfo_children():
            w.destroy()
        WorkspaceView(self.container, user, on_logout=self.show_auth)
        self._arm_afk_timer()

    # --------------------------------------------------- AFK auto-logout
    def _on_activity(self, event=None):
        if self._afk_armed:
            self._reset_afk_timer()

    def _arm_afk_timer(self):
        self._afk_armed = True
        self._reset_afk_timer()

    def _disarm_afk_timer(self):
        self._afk_armed = False
        if self._afk_job is not None:
            self.after_cancel(self._afk_job)
            self._afk_job = None

    def _reset_afk_timer(self):
        if self._afk_job is not None:
            self.after_cancel(self._afk_job)
        self._afk_job = self.after(self.AFK_TIMEOUT_MS, self._on_afk_timeout)

    def _on_afk_timeout(self):
        self._disarm_afk_timer()
        messagebox.showinfo("Session Timed Out",
                             "You were signed out after 1 minutes of inactivity.\nPlease sign in again.")
        self.show_auth()


if __name__ == "__main__":
    app = SemsApp()
    app.mainloop()