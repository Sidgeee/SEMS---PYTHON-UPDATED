import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

# =========================================================================
# 1. LOCAL DATA LAYER INITIALIZATION (PURE PYTHON & EMBEDDED SQLITE)
# =========================================================================
DB_FILE = "school_event_system.db"

def init_db():
    """Sets up the SQLite database schemas supporting Admin, Teacher, and Student workflows."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # 1. Accounts Database
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            role TEXT NOT NULL, -- 'admin', 'teacher', 'student'
            full_name TEXT NOT NULL
        )
    ''')
    
    # 2. Events Database
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            date TEXT,
            time TEXT,
            venue TEXT,
            status TEXT DEFAULT 'Pending',
            agendas TEXT,
            speakers TEXT,
            supplies TEXT,
            resources TEXT
        )
    """)
    
    # 3. Registrant Clearances & Materials Checklist Ledger
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS participants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            name TEXT NOT NULL,
            year_level TEXT NOT NULL,
            section TEXT NOT NULL,
            program TEXT NOT NULL,
            event_id INTEGER,
            attendance TEXT DEFAULT 'Absent', -- 'Present' or 'Absent'
            waiver TEXT DEFAULT 'NO',          -- Requirement Checkbox 1
            reg_fee TEXT DEFAULT 'NO',         -- Requirement Checkbox 2
            id_clearance TEXT DEFAULT 'NO',    -- Requirement Checkbox 3
            FOREIGN KEY(event_id) REFERENCES events(id)
        )
    ''')
    
    # 4. Global Announcements Hub
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS announcements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            date_posted TEXT NOT NULL
        )
    ''')
    
    # 5. Student Evaluation Feedback Analytics
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS feedbacks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            event_id INTEGER,
            rating INTEGER NOT NULL,
            comments TEXT,
            FOREIGN KEY(event_id) REFERENCES events(id)
        )
    ''')
    
    # Seed default sandbox accounts for presentation testing
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("INSERT INTO users VALUES (?, ?, ?, ?)", [
            ('admin', 'admin123', 'admin', 'Deans Admin'),
            ('teacher', 'teacher123', 'teacher', 'Faculty Coordinator'),
            ('student', 'student123', 'student', 'Student User')
        ])
    conn.commit()
    conn.close()


# =========================================================================
# 2. CORE SYSTEM PLATFORM CONTROLLER & THEMED GATEWAY MAIN WINDOW
# =========================================================================
class SchoolEventManagementSystem(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("School Event Management System - Pure Python Edition")
        self.geometry("1200x780")
        self.minsize(1100, 680)
        
        # User Session Variables
        self.current_user = None
        self.current_role = None
        self.current_name = None
        
        # Configure High-Contrast Modern Theme Styling Variables
        self.bg_dark = "#111827"       # Primary Layout Background (Slate/Dark Gray)
        self.card_bg = "#1f2937"       # Content Card Frame Background
        self.accent_blue = "#3b82f6"   # Neon Cyan/Blue Accent Highlight
        self.accent_green = "#10b981"  # Success States Accent
        self.accent_red = "#ef4444"    # Critical Alert Actions Accent
        self.text_white = "#f9fafb"    # High-contrast readable typography
        self.text_muted = "#9ca3af"    # Subtitles and Labels
        
        self.configure(bg=self.bg_dark)
        
        # Apply Tkinter Universal Theme Overrides
        self.style = ttk.Style()
        self.theme_use_name = "clam"
        self.style.theme_use(self.theme_use_name)
        self.style.configure("TNotebook", background=self.bg_dark, borderwidth=0)
        self.style.configure("TNotebook.Tab", font=("Segoe UI", 11, "bold"), padding=[14, 6], background="#374151", foreground=self.text_white)
        self.style.map("TNotebook.Tab", background=[("selected", self.accent_blue)], foreground=[("selected", "#ffffff")])
        
        self.style.configure("Treeview", background=self.card_bg, fieldbackground=self.card_bg, foreground=self.text_white, rowheight=28, font=("Segoe UI", 10))
        self.style.configure("Treeview.Heading", background="#374151", foreground=self.text_white, font=("Segoe UI", 10, "bold"))
        self.style.map("Treeview", background=[("selected", self.accent_blue)])

        # Root Layout Window View Container
        self.view_container = tk.Frame(self, bg=self.bg_dark)
        self.view_container.pack(fill="both", expand=True)
        
        self.display_login_gateway()

    def clear_view(self):
        for widget in self.view_container.winfo_children():
            widget.destroy()

    def display_login_gateway(self):
        """Generates the unified secure portal login pane."""
        self.clear_view()
        
        pane = tk.Frame(self.view_container, bg=self.card_bg, bd=0, relief="flat")
        pane.place(relx=0.5, rely=0.5, anchor="center", width=420, height=520)
        
        tk.Label(pane, text="CAMPUS EVENT PLATFORM", font=("Segoe UI", 18, "bold"), fg=self.accent_blue, bg=self.card_bg).pack(pady=(35, 5))
        tk.Label(pane, text="100% Pure Python Management System", font=("Segoe UI", 9, "italic"), fg=self.text_muted, bg=self.card_bg).pack(pady=(0, 20))
        
        tk.Label(pane, text="Account Username", font=("Segoe UI", 10, "bold"), fg=self.text_white, bg=self.card_bg).pack(anchor="w", padx=45, pady=(10, 2))
        ent_user = tk.Entry(pane, font=("Segoe UI", 12), bg="#374151", fg=self.text_white, insertbackground="white", bd=1, relief="solid")
        ent_user.pack(fill="x", padx=45, ipady=6)
        
        tk.Label(pane, text="Security Access Password", font=("Segoe UI", 10, "bold"), fg=self.text_white, bg=self.card_bg).pack(anchor="w", padx=45, pady=(15, 2))
        ent_pass = tk.Entry(pane, font=("Segoe UI", 12), bg="#374151", fg=self.text_white, insertbackground="white", show="•", bd=1, relief="solid")
        ent_pass.pack(fill="x", padx=45, ipady=6)
        
        def execute_authentication():
            u = ent_user.get().strip()
            p = ent_pass.get().strip()
            
            conn = sqlite3.connect(DB_FILE)
            conn.row_factory = sqlite3.Row
            account = conn.execute("SELECT * FROM users WHERE username = ? AND password = ?", (u, p)).fetchone()
            conn.close()
            
            if account:
                self.current_user = account['username']
                self.current_role = account['role']
                self.current_name = account['full_name']
                self.route_user_to_dashboard()
            else:
                messagebox.showerror("Access Denied", "Invalid system credentials. Please check inputs.")

        btn_auth = tk.Button(pane, text="Sign In to System", font=("Segoe UI", 12, "bold"), bg=self.accent_blue, fg="#ffffff", activebackground="#2563eb", activeforeground="#ffffff", command=execute_authentication, relief="flat", cursor="hand2")
        btn_auth.pack(fill="x", padx=45, pady=(30, 10), ipady=4)
        
        btn_register = tk.Button(pane, text="New Student? Create an Account Here", font=("Segoe UI", 9, "underline"), 
                                 bg=self.card_bg, fg=self.accent_blue, activebackground=self.card_bg, 
                                 activeforeground=self.text_white, command=self.display_registration_gateway, 
                                 relief="flat", cursor="hand2")
        btn_register.pack(pady=(5, 0))

    def display_registration_gateway(self):
        """Generates the modern account creation portal strictly configured for new student sign-ups."""
        self.clear_view()
        
        pane = tk.Frame(self.view_container, bg=self.card_bg, bd=0, relief="flat")
        pane.place(relx=0.5, rely=0.5, anchor="center", width=420, height=540)
        
        tk.Label(pane, text="STUDENT ACCOUNT SIGN UP", font=("Segoe UI", 16, "bold"), fg=self.accent_blue, bg=self.card_bg).pack(pady=(35, 15))
        tk.Label(pane, text="Note: Faculty/Staff accounts are provided by Admin", font=("Segoe UI", 9, "italic"), fg=self.text_muted, bg=self.card_bg).pack(pady=(0, 20))
        
        tk.Label(pane, text="Student Full Name", font=("Segoe UI", 10, "bold"), fg=self.text_white, bg=self.card_bg).pack(anchor="w", padx=45, pady=(5, 2))
        ent_name = tk.Entry(pane, font=("Segoe UI", 11), bg="#374151", fg=self.text_white, insertbackground="white", bd=1, relief="solid")
        ent_name.pack(fill="x", padx=45, ipady=5)
        
        tk.Label(pane, text="Desired Username", font=("Segoe UI", 10, "bold"), fg=self.text_white, bg=self.card_bg).pack(anchor="w", padx=45, pady=(12, 2))
        ent_user = tk.Entry(pane, font=("Segoe UI", 11), bg="#374151", fg=self.text_white, insertbackground="white", bd=1, relief="solid")
        ent_user.pack(fill="x", padx=45, ipady=5)
        
        tk.Label(pane, text="Choose Password", font=("Segoe UI", 10, "bold"), fg=self.text_white, bg=self.card_bg).pack(anchor="w", padx=45, pady=(12, 2))
        ent_pass = tk.Entry(pane, font=("Segoe UI", 11), bg="#374151", fg=self.text_white, insertbackground="white", show="•", bd=1, relief="solid")
        ent_pass.pack(fill="x", padx=45, ipady=5)
        
        def execute_registration():
            name = ent_name.get().strip()
            username = ent_user.get().strip()
            password = ent_pass.get().strip()
            
            if not name or not username or not password:
                messagebox.showwarning("Incomplete Fields", "All fields are required to register your student profile.")
                return
                
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            
            cursor.execute("SELECT username FROM users WHERE username = ?", (username,))
            if cursor.fetchone():
                messagebox.showerror("Conflict Error", f"The username '{username}' is already taken.")
                conn.close()
                return
                
            try:
                cursor.execute("INSERT INTO users (username, password, role, full_name) VALUES (?, ?, 'student', ?)",
                               (username, password, name))
                conn.commit()
                messagebox.showinfo("Success", "Student account created! You may now sign in.")
                self.display_login_gateway()
            except Exception as e:
                messagebox.showerror("System Error", f"Registration fault encountered: {e}")
            finally:
                conn.close()

        btn_submit = tk.Button(pane, text="Register Student Profile", font=("Segoe UI", 11, "bold"), bg=self.accent_green, fg="#ffffff", activebackground="#059669", activeforeground="#ffffff", command=execute_registration, relief="flat", cursor="hand2")
        btn_submit.pack(fill="x", padx=45, pady=25, ipady=4)
        
        btn_back = tk.Button(pane, text="Return to Login Gateway", font=("Segoe UI", 9, "underline"), bg=self.card_bg, fg=self.text_muted, command=self.display_login_gateway, relief="flat", cursor="hand2")
        btn_back.pack()

    def route_user_to_dashboard(self):
        self.clear_view()
        if self.current_role == "admin":
            AdminDashboard(self.view_container, self)
        elif self.current_role == "teacher":
            TeacherDashboard(self.view_container, self)
        elif self.current_role == "student":
            StudentDashboard(self.view_container, self)


# =========================================================================
# 3. ADMINISTRATIVE WORKSPACE PANEL
# =========================================================================
class AdminDashboard:
    def __init__(self, parent, app):
        self.app = app
        self.selected_event_id = None
        
        ribbon = tk.Frame(parent, bg=app.card_bg, height=65)
        ribbon.pack(fill="x")
        ribbon.pack_propagate(False)
        
        tk.Label(ribbon, text=f"🏛️ SYSTEM CONTROL CENTER : {app.current_name.upper()}", font=("Segoe UI", 13, "bold"), fg=app.text_white, bg=app.card_bg).pack(side="left", padx=20)
        tk.Button(ribbon, text="Exit Session", font=("Segoe UI", 9, "bold"), bg="#374151", fg="white", command=app.display_login_gateway, relief="flat", cursor="hand2", padx=15).pack(side="right", padx=20)
        
        self.tabs = ttk.Notebook(parent)
        self.tabs.pack(fill="both", expand=True, padx=15, pady=15)
        
        self.tab_config = tk.Frame(self.tabs, bg=app.bg_dark)
        self.tab_clearance = tk.Frame(self.tabs, bg=app.bg_dark)
        self.tab_attendance = tk.Frame(self.tabs, bg=app.bg_dark)
        self.tab_bulletins = tk.Frame(self.tabs, bg=app.bg_dark)
        
        self.tabs.add(self.tab_config, text=" Configure Events ")
        self.tabs.add(self.tab_clearance, text=" Manage Registrants ")
        self.tabs.add(self.tab_attendance, text=" Live Attendance Tracker ")
        self.tabs.add(self.tab_bulletins, text=" Broadcast Bulletins ")
        
        self.assemble_events_configuration()
        self.assemble_registrants_clearance()
        self.assemble_attendance_ledger()
        self.assemble_bulletins_center()

    def assemble_events_configuration(self):
        card = tk.LabelFrame(self.tab_config, text=" Open New Official Event Channel ", font=("Segoe UI", 11, "bold"), bg=self.app.card_bg, fg=self.app.text_white, bd=1, padx=15, pady=10)
        card.pack(fill="x", padx=15, pady=10)
        
        tk.Label(card, text="Event Title:", fg=self.app.text_white, bg=self.app.card_bg).grid(row=0, column=0, sticky="w", pady=5)
        ent_t = tk.Entry(card, width=25, bg="#374151", fg="white", insertbackground="white")
        ent_t.grid(row=0, column=1, padx=8, pady=5)
        
        tk.Label(card, text="Venue:", fg=self.app.text_white, bg=self.app.card_bg).grid(row=0, column=2, sticky="w", pady=5)
        ent_v = tk.Entry(card, width=18, bg="#374151", fg="white", insertbackground="white")
        ent_v.grid(row=0, column=3, padx=8, pady=5)
        
        tk.Label(card, text="Scheduled Date:", fg=self.app.text_white, bg=self.app.card_bg).grid(row=0, column=4, sticky="w", pady=5)
        ent_d = tk.Entry(card, width=12, bg="#374151", fg="white", insertbackground="white")
        ent_d.insert(0, datetime.now().strftime("%Y-%m-%d"))
        ent_d.grid(row=0, column=5, padx=8, pady=5)
        
        def save_event_action():
            if not ent_t.get() or not ent_v.get():
                messagebox.showwarning("Incomplete", "Please completely specify Title and Venue data fields.")
                return
            conn = sqlite3.connect(DB_FILE)
            conn.execute("INSERT INTO events (title, venue, date, status) VALUES (?, ?, ?, 'Approved')",
                         (ent_t.get().strip(), ent_v.get().strip(), ent_d.get().strip()))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "New Active Approved Campus Event has been successfully initialized.")
            ent_t.delete(0, tk.END); ent_v.delete(0, tk.END)
            self.refresh_events_data_grid()
            
        tk.Button(card, text="Publish Event", font=("Segoe UI", 10, "bold"), bg=self.app.accent_blue, fg="white", command=save_event_action, relief="flat", cursor="hand2").grid(row=0, column=6, padx=10)
        
        validation_card = tk.LabelFrame(self.tab_config, text=" Teacher Proposal Verification Toolroom (Select a row from table below) ", font=("Segoe UI", 11, "bold"), bg=self.app.card_bg, fg=self.app.text_white, bd=1, padx=15, pady=10)
        validation_card.pack(fill="x", padx=15, pady=5)
        
        self.lbl_selected_event = tk.Label(validation_card, text="No Event Selected", font=("Segoe UI", 10, "italic"), fg=self.app.text_muted, bg=self.app.card_bg)
        self.lbl_selected_event.pack(side="left", padx=10)
        
        def update_proposal_status(new_status, color_theme):
            if not self.selected_event_id:
                messagebox.showwarning("Selection Required", "Please select a pending event row from the grid list below first.")
                return
            conn = sqlite3.connect(DB_FILE)
            conn.execute("UPDATE events SET status = ? WHERE id = ?", (new_status, self.selected_event_id))
            conn.commit()
            conn.close()
            messagebox.showinfo("Status Updated", f"Event proposal status changed to: '{new_status}'")
            self.selected_event_id = None
            self.lbl_selected_event.config(text="No Event Selected", fg=self.app.text_muted)
            self.refresh_events_data_grid()

        self.btn_approve = tk.Button(validation_card, text="Approve Proposal", font=("Segoe UI", 9, "bold"), bg=self.app.accent_green, fg="white", state="disabled", relief="flat", cursor="hand2", command=lambda: update_proposal_status("Approved", self.app.accent_green))
        self.btn_approve.pack(side="right", padx=10)
        
        self.btn_disapprove = tk.Button(validation_card, text="Disapprove Proposal", font=("Segoe UI", 9, "bold"), bg=self.app.accent_red, fg="white", state="disabled", relief="flat", cursor="hand2", command=lambda: update_proposal_status("Disapproved", self.app.accent_red))
        self.btn_disapprove.pack(side="right", padx=10)

        self.tree_ev = ttk.Treeview(self.tab_config, columns=("ID", "Title", "Venue Location", "Target Date", "Approval Status"), show="headings")
        for c in ("ID", "Title", "Venue Location", "Target Date", "Approval Status"):
            self.tree_ev.heading(c, text=c)
            self.tree_ev.column(c, anchor="center")
        self.tree_ev.pack(fill="both", expand=True, padx=15, pady=10)
        
        def on_grid_row_select(event):
            selection = self.tree_ev.selection()
            if not selection: return
            values = self.tree_ev.item(selection, "values")
            self.selected_event_id = values[0]
            title_summary = values[1]
            status_summary = values[4]
            
            self.lbl_selected_event.config(text=f"Selected: ID {self.selected_event_id} - \"{title_summary}\" [Current: {status_summary}]", fg=self.app.text_white)
            self.btn_approve.config(state="normal")
            self.btn_disapprove.config(state="normal")

        self.tree_ev.bind("<<TreeviewSelect>>", on_grid_row_select)
        self.refresh_events_data_grid()

    def refresh_events_data_grid(self):
        for item in self.tree_ev.get_children(): self.tree_ev.delete(item)
        conn = sqlite3.connect(DB_FILE)
        for row in conn.execute("SELECT id, title, venue, date, status FROM events"): self.tree_ev.insert("", "end", values=row)
        conn.close()
        if hasattr(self, 'btn_approve'):
            self.btn_approve.config(state="disabled")
            self.btn_disapprove.config(state="disabled")

    def assemble_registrants_clearance(self):
        card = tk.LabelFrame(self.tab_clearance, text=" Map Student Registration & Document Clearance Requirements ", font=("Segoe UI", 11, "bold"), bg=self.app.card_bg, fg=self.app.text_white, padx=15, pady=10)
        card.pack(fill="x", padx=15, pady=15)
        
        tk.Label(card, text="Student ID No:", fg=self.app.text_white, bg=self.app.card_bg).grid(row=0, column=0, sticky="w", pady=5)
        ent_sid = tk.Entry(card, width=12, bg="#374151", fg="white", insertbackground="white")
        ent_sid.grid(row=0, column=1, padx=8, pady=5)
        
        tk.Label(card, text="Full Name:", fg=self.app.text_white, bg=self.app.card_bg).grid(row=0, column=2, sticky="w", pady=5)
        ent_nam = tk.Entry(card, width=22, bg="#374151", fg="white", insertbackground="white")
        ent_nam.grid(row=0, column=3, padx=8, pady=5)

        tk.Label(card, text="Yr Level:", fg=self.app.text_white, bg=self.app.card_bg).grid(row=0, column=4, sticky="w", pady=5)
        ent_yl = tk.Entry(card, width=10, bg="#374151", fg="white", insertbackground="white")
        ent_yl.grid(row=0, column=5, padx=8, pady=5)

        tk.Label(card, text="Section:", fg=self.app.text_white, bg=self.app.card_bg).grid(row=1, column=0, sticky="w", pady=5)
        ent_sec = tk.Entry(card, width=12, bg="#374151", fg="white", insertbackground="white")
        ent_sec.grid(row=1, column=1, padx=8, pady=5)

        tk.Label(card, text="Program Track:", fg=self.app.text_white, bg=self.app.card_bg).grid(row=1, column=2, sticky="w", pady=5)
        ent_prg = tk.Entry(card, width=22, bg="#374151", fg="white", insertbackground="white")
        ent_prg.grid(row=1, column=3, padx=8, pady=5)
        
        tk.Label(card, text="Event Mapping ID:", fg=self.app.text_white, bg=self.app.card_bg).grid(row=1, column=4, sticky="w", pady=5)
        ent_eid = tk.Entry(card, width=10, bg="#374151", fg="white", insertbackground="white")
        ent_eid.grid(row=1, column=5, padx=8, pady=5)
        
        chk_w = tk.StringVar(value="NO"); chk_f = tk.StringVar(value="NO"); chk_c = tk.StringVar(value="NO")
        tk.Checkbutton(card, text="Waiver Form Submitted", variable=chk_w, onvalue="YES", offvalue="NO", bg=self.app.card_bg, fg=self.app.text_white, selectcolor="#374151").grid(row=2, column=1, pady=10, sticky="w")
        tk.Checkbutton(card, text="Registration Fee Settled", variable=chk_f, onvalue="YES", offvalue="NO", bg=self.app.card_bg, fg=self.app.text_white, selectcolor="#374151").grid(row=2, column=3, pady=10, sticky="w")
        tk.Checkbutton(card, text="Student ID Verified", variable=chk_c, onvalue="YES", offvalue="NO", bg=self.app.card_bg, fg=self.app.text_white, selectcolor="#374151").grid(row=2, column=5, pady=10, sticky="w")
        
        def save_registrant_profile():
            if not ent_sid.get() or not ent_nam.get() or not ent_eid.get():
                messagebox.showwarning("Missing Links", "Student Identification and Target Event mapping values are mandatory.")
                return
            conn = sqlite3.connect(DB_FILE)
            conn.execute('''INSERT INTO participants (student_id, name, year_level, section, program, event_id, waiver, reg_fee, id_clearance)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                         (ent_sid.get().strip(), ent_nam.get().strip(), ent_yl.get().strip(), ent_sec.get().strip(), ent_prg.get().strip(), ent_eid.get().strip(), chk_w.get(), chk_f.get(), chk_c.get()))
            conn.commit()
            conn.close()
            messagebox.showinfo("Committed", "Registrant profile requirement parameters saved.")
            self.refresh_attendance_ledger()

        tk.Button(card, text="Commit Profile", font=("Segoe UI", 10, "bold"), bg=self.app.accent_green, fg="white", command=save_registrant_profile, relief="flat", cursor="hand2").grid(row=2, column=6, padx=15, sticky="e")

    def assemble_attendance_ledger(self):
        lbl = tk.Label(self.tab_attendance, text="💡 Double-click any row item inside the data matrix grid to dynamically toggle student verification status.", font=("Segoe UI", 9, "italic"), fg=self.app.text_muted, bg=self.app.bg_dark)
        lbl.pack(pady=(10, 0))
        
        self.tree_at = ttk.Treeview(self.tab_attendance, columns=("RecID", "StudentID", "Name", "Program", "EventID", "Clearance Status", "Waiver", "FeePaid", "IDCheck"), show="headings")
        for c in ("RecID", "StudentID", "Name", "Program", "EventID", "Clearance Status", "Waiver", "FeePaid", "IDCheck"):
            self.tree_at.heading(c, text=c)
            self.tree_at.column(c, anchor="center")
        self.tree_at.pack(fill="both", expand=True, padx=15, pady=15)
        
        def toggle_attendance_state(event):
            selection = self.tree_at.selection()
            if not selection: return
            vals = self.tree_at.item(selection, "values")
            r_id = vals[0]
            nxt = "Absent" if vals[5] == "Present" else "Present"
            
            conn = sqlite3.connect(DB_FILE)
            conn.execute("UPDATE participants SET attendance = ? WHERE id = ?", (nxt, r_id))
            conn.commit()
            conn.close()
            self.refresh_attendance_ledger()
            
        self.tree_at.bind("<Double-1>", toggle_attendance_state)
        self.refresh_attendance_ledger()

    def refresh_attendance_ledger(self):
        for item in self.tree_at.get_children(): self.tree_at.delete(item)
        conn = sqlite3.connect(DB_FILE)
        for row in conn.execute("SELECT id, student_id, name, program, event_id, attendance, waiver, reg_fee, id_clearance FROM participants"):
            self.tree_at.insert("", "end", values=row)
        conn.close()

    def assemble_bulletins_center(self):
        card = tk.LabelFrame(self.tab_bulletins, text=" Broadcast Real-time Bulletin Notice ", font=("Segoe UI", 11, "bold"), bg=self.app.card_bg, fg=self.app.text_white, padx=15, pady=15)
        card.pack(fill="both", expand=True, padx=25, pady=25)
        
        tk.Label(card, text="Bulletin Board Header Title:", fg=self.app.text_white, bg=self.app.card_bg, font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(5, 2))
        ent_hd = tk.Entry(card, bg="#374151", fg="white", insertbackground="white", font=("Segoe UI", 11))
        ent_hd.pack(fill="x", ipady=4, pady=5)
        
        tk.Label(card, text="Detailed Notice Content Body:", fg=self.app.text_white, bg=self.app.card_bg, font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(10, 2))
        txt_bd = tk.Text(card, bg="#374151", fg="white", insertbackground="white", height=8, font=("Segoe UI", 10))
        txt_bd.pack(fill="x", pady=5)
        
        def broadcast_action():
            if not ent_hd.get().strip() or not txt_bd.get("1.0", tk.END).strip():
                messagebox.showwarning("Empty fields", "Notice requires a Title and Content Body.")
                return
            conn = sqlite3.connect(DB_FILE)
            conn.execute("INSERT INTO announcements (title, content, date_posted) VALUES (?, ?, ?)",
                         (ent_hd.get().strip(), txt_bd.get("1.0", tk.END).strip(), datetime.now().strftime("%Y-%m-%d %H:%M")))
            conn.commit()
            conn.close()
            messagebox.showinfo("Broadcasted", "Global system notification broadcast successfully pushed.")
            ent_hd.delete(0, tk.END); txt_bd.delete("1.0", tk.END)
            
        tk.Button(card, text="Push Announcement Bulletin", font=("Segoe UI", 11, "bold"), bg=self.app.accent_blue, fg="white", command=broadcast_action, relief="flat", cursor="hand2").pack(pady=20, ipady=4)


# =========================================================================
# 4. FACULTY MANAGEMENT INTERFACE TERMINAL
# =========================================================================
class TeacherDashboard:
    def __init__(self, parent, app):
        self.app = app
        self.selected_event_id = None
        
        ribbon = tk.Frame(parent, bg=app.card_bg, height=65)
        ribbon.pack(fill="x")
        ribbon.pack_propagate(False)
        
        tk.Label(ribbon, text=f"📋 FACULTY MANAGEMENT PLATFORM : {app.current_name.upper()}", 
                 font=("Segoe UI", 13, "bold"), fg=app.text_white, bg=app.card_bg).pack(side="left", padx=20)
        tk.Button(ribbon, text="Exit Session", font=("Segoe UI", 9, "bold"), bg="#374151", fg="white", 
                  command=app.display_login_gateway, relief="flat", cursor="hand2", padx=15).pack(side="right", padx=20)
        
        self.tabs = ttk.Notebook(parent)
        self.tabs.pack(fill="both", expand=True, padx=15, pady=15)
        
        self.tab_events = tk.Frame(self.tabs, bg=app.bg_dark)
        self.tab_details = tk.Frame(self.tabs, bg=app.bg_dark)
        self.tab_attendance = tk.Frame(self.tabs, bg=app.bg_dark)
        self.tab_announcements = tk.Frame(self.tabs, bg=app.bg_dark)
        self.tab_reports = tk.Frame(self.tabs, bg=app.bg_dark)
        
        self.tabs.add(self.tab_events, text=" Events Proposal Room ")
        self.tabs.add(self.tab_details, text=" Prepare Event Details ")
        self.tabs.add(self.tab_attendance, text=" Manage Attendance ")
        self.tabs.add(self.tab_announcements, text=" Announcements ")
        self.tabs.add(self.tab_reports, text=" Feedbacks & Data Reports ")
        
        self.assemble_events_proposal_view()
        self.assemble_prepare_details_view()
        self.assemble_manage_attendance_view()
        self.assemble_announcements_view()
        self.assemble_feedbacks_reports_view()

    def assemble_events_proposal_view(self):
        left_pane = tk.LabelFrame(self.tab_events, text=" View Current Event Proposals ", font=("Segoe UI", 10, "bold"), bg=self.app.card_bg, fg=self.app.text_white, padx=10, pady=10)
        left_pane.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        
        self.tree_teacher_ev = ttk.Treeview(left_pane, columns=("ID", "Title", "Venue", "Date", "Status"), show="headings")
        for c in ("ID", "Title", "Venue", "Date", "Status"):
            self.tree_teacher_ev.heading(c, text=c)
            self.tree_teacher_ev.column(c, anchor="center")
        self.tree_teacher_ev.pack(fill="both", expand=True)
        
        right_pane = tk.LabelFrame(self.tab_events, text=" Create Event Proposal Form ", font=("Segoe UI", 10, "bold"), bg=self.app.card_bg, fg=self.app.text_white, padx=15, pady=10)
        right_pane.pack(side="right", fill="y", padx=10, pady=10)
        
        tk.Label(right_pane, text="Proposed Title:", fg=self.app.text_white, bg=self.app.card_bg).pack(anchor="w", pady=(5,2))
        ent_t = tk.Entry(right_pane, bg="#374151", fg="white", width=30, insertbackground="white", font=("Segoe UI", 10))
        ent_t.pack(fill="x", pady=5, ipady=3)
        
        tk.Label(right_pane, text="Proposed Venue:", fg=self.app.text_white, bg=self.app.card_bg).pack(anchor="w", pady=(5,2))
        ent_v = tk.Entry(right_pane, bg="#374151", fg="white", insertbackground="white", font=("Segoe UI", 10))
        ent_v.pack(fill="x", pady=5, ipady=3)
        
        tk.Label(right_pane, text="Proposed Date (YYYY-MM-DD):", fg=self.app.text_white, bg=self.app.card_bg).pack(anchor="w", pady=(5,2))
        ent_d = tk.Entry(right_pane, bg="#374151", fg="white", insertbackground="white", font=("Segoe UI", 10))
        ent_d.insert(0, datetime.now().strftime("%Y-%m-%d"))
        ent_d.pack(fill="x", pady=5, ipady=3)
        
        def file_proposal_action():
            if not ent_t.get().strip() or not ent_v.get().strip():
                messagebox.showwarning("Incomplete Data", "Please completely fill out the Title and Venue fields.")
                return
            conn = sqlite3.connect(DB_FILE)
            conn.execute("INSERT INTO events (title, venue, date, status) VALUES (?, ?, ?, 'Pending')",
                         (ent_t.get().strip(), ent_v.get().strip(), ent_d.get().strip()))
            conn.commit()
            conn.close()
            messagebox.showinfo("Proposal Submitted", "Event Proposal successfully submitted for Review.")
            ent_t.delete(0, tk.END); ent_v.delete(0, tk.END)
            self.refresh_teacher_proposals()
            
        tk.Button(right_pane, text="Submit Event Proposal", font=("Segoe UI", 11, "bold"), bg=self.app.accent_blue, fg="white", command=file_proposal_action, relief="flat", cursor="hand2").pack(fill="x", pady=20, ipady=4)
        self.refresh_teacher_proposals()

    def refresh_teacher_proposals(self):
        for item in self.tree_teacher_ev.get_children(): self.tree_teacher_ev.delete(item)
        conn = sqlite3.connect(DB_FILE)
        for row in conn.execute("SELECT id, title, venue, date, status FROM events"): self.tree_teacher_ev.insert("", "end", values=row)
        conn.close()

    def assemble_prepare_details_view(self):
        lbl = tk.Label(self.tab_details, text="Select an Approved Event from the table below, then load details fields.", font=("Segoe UI", 10, "italic"), fg=self.app.text_muted, bg=self.app.bg_dark)
        lbl.pack(pady=5)
        
        self.tree_det = ttk.Treeview(self.tab_details, columns=("ID", "Title", "Venue", "Date", "Status"), show="headings", height=5)
        for c in ("ID", "Title", "Venue", "Date", "Status"):
            self.tree_det.heading(c, text=c)
            self.tree_det.column(c, anchor="center")
        self.tree_det.pack(fill="x", padx=15, pady=5)
        
        form_frame = tk.LabelFrame(self.tab_details, text=" Step 2: Build Logistics Blueprint & Speakers Reference Profile ", font=("Segoe UI", 10, "bold"), bg=self.app.card_bg, fg=self.app.text_white, padx=15, pady=10)
        form_frame.pack(fill="both", expand=True, padx=15, pady=5)
        
        tk.Label(form_frame, text="Time Schedule:", fg=self.app.text_white, bg=self.app.card_bg).grid(row=0, column=0, sticky="w", pady=3)
        ent_time = tk.Entry(form_frame, bg="#374151", fg="white", width=20, insertbackground="white")
        ent_time.grid(row=0, column=1, sticky="w", padx=5)
        
        tk.Label(form_frame, text="Keynote Speakers:", fg=self.app.text_white, bg=self.app.card_bg).grid(row=0, column=2, sticky="w", pady=3, padx=15)
        ent_spk = tk.Entry(form_frame, bg="#374151", fg="white", width=35, insertbackground="white")
        ent_spk.grid(row=0, column=3, sticky="w", padx=5)
        
        tk.Label(form_frame, text="Event Agendas & Flow:", fg=self.app.text_white, bg=self.app.card_bg).grid(row=1, column=0, sticky="nw", pady=5)
        txt_agd = tk.Text(form_frame, bg="#374151", fg="white", height=4, width=30, insertbackground="white")
        txt_agd.grid(row=1, column=1, pady=5, sticky="w")
        
        tk.Label(form_frame, text="Supplies & Resources Required:", fg=self.app.text_white, bg=self.app.card_bg).grid(row=1, column=2, sticky="nw", pady=5, padx=15)
        txt_res = tk.Text(form_frame, bg="#374151", fg="white", height=4, width=35, insertbackground="white")
        txt_res.grid(row=1, column=3, pady=5, sticky="w")
        
        def load_selected_details(event):
            sel = self.tree_det.selection()
            if not sel: return
            vals = self.tree_det.item(sel, "values")
            self.selected_event_id = vals[0]
            
            conn = sqlite3.connect(DB_FILE)
            conn.row_factory = sqlite3.Row
            evt = conn.execute("SELECT * FROM events WHERE id=?", (self.selected_event_id,)).fetchone()
            conn.close()
            
            if evt:
                ent_time.delete(0, tk.END); ent_time.insert(0, evt['time'] if evt['time'] else "")
                ent_spk.delete(0, tk.END); ent_spk.insert(0, evt['speakers'] if evt['speakers'] else "")
                txt_agd.delete("1.0", tk.END); txt_agd.insert("1.0", evt['agendas'] if evt['agendas'] else "")
                txt_res.delete("1.0", tk.END); txt_res.insert("1.0", evt['resources'] if evt['resources'] else "")
                
        self.tree_det.bind("<<TreeviewSelect>>", load_selected_details)
        
        def save_details_action():
            if not self.selected_event_id:
                messagebox.showwarning("Selection Empty", "Please pick an approved row item from the upper checklist window matrix layout first.")
                return
            conn = sqlite3.connect(DB_FILE)
            conn.execute("UPDATE events SET time=?, agendas=?, speakers=?, resources=? WHERE id=?",
                         (ent_time.get().strip(), txt_agd.get("1.0", tk.END).strip(), ent_spk.get().strip(), txt_res.get("1.0", tk.END).strip(), self.selected_event_id))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Logistical event parameter tracking fields saved successfully.")
            self.refresh_details_approved_list()
            
        tk.Button(form_frame, text="Commit & Save Blueprint Details", font=("Segoe UI", 10, "bold"), bg=self.app.accent_green, fg="white", command=save_details_action, relief="flat", cursor="hand2").grid(row=2, column=3, pady=10, sticky="e")
        self.refresh_details_approved_list()

    def refresh_details_approved_list(self):
        for item in self.tree_det.get_children(): self.tree_det.delete(item)
        conn = sqlite3.connect(DB_FILE)
        for row in conn.execute("SELECT id, title, venue, date, status FROM events WHERE status='Approved'"): self.tree_det.insert("", "end", values=row)
        conn.close()

    def assemble_manage_attendance_view(self):
        """Generates the updated attendance control workbench featuring inline editing and removal components."""
        lbl = tk.Label(self.tab_attendance, text="📋 Double-click rows to quickly toggle presence status, or select a row to Edit/Remove its record details.", font=("Segoe UI", 10, "italic"), fg=self.app.text_muted, bg=self.app.bg_dark)
        lbl.pack(pady=10)

        # 1. Main Grid Table
        self.tree_teach_at = ttk.Treeview(self.tab_attendance, columns=("RecID", "StudentID", "Full Name", "Program", "EventID", "Attendance Status"), show="headings")
        for c in ("RecID", "StudentID", "Full Name", "Program", "EventID", "Attendance Status"):
            self.tree_teach_at.heading(c, text=c)
            self.tree_teach_at.column(c, anchor="center")
        self.tree_teach_at.pack(fill="both", expand=True, padx=15, pady=5)

        # 2. Inline Action Modification Panel
        action_pane = tk.LabelFrame(self.tab_attendance, text=" Selected Record Action Control Desk ", font=("Segoe UI", 11, "bold"), bg=self.app.card_bg, fg=self.app.text_white, padx=15, pady=10)
        action_pane.pack(fill="x", padx=15, pady=10)

        tk.Label(action_pane, text="Student ID:", fg=self.app.text_white, bg=self.app.card_bg).grid(row=0, column=0, sticky="w", pady=5, padx=5)
        ent_sid = tk.Entry(action_pane, bg="#374151", fg="white", width=12, insertbackground="white")
        ent_sid.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(action_pane, text="Full Name:", fg=self.app.text_white, bg=self.app.card_bg).grid(row=0, column=2, sticky="w", pady=5, padx=5)
        ent_nam = tk.Entry(action_pane, bg="#374151", fg="white", width=25, insertbackground="white")
        ent_nam.grid(row=0, column=3, padx=5, pady=5)

        tk.Label(action_pane, text="Program:", fg=self.app.text_white, bg=self.app.card_bg).grid(row=0, column=4, sticky="w", pady=5, padx=5)
        ent_prg = tk.Entry(action_pane, bg="#374151", fg="white", width=10, insertbackground="white")
        ent_prg.grid(row=0, column=5, padx=5, pady=5)

        # Track the active record database Primary Key privately 
        self.active_record_id = None

        # Populate action inputs when a row is clicked
        def on_student_row_select(event):
            sel = self.tree_teach_at.selection()
            if not sel: return
            vals = self.tree_teach_at.item(sel, "values")
            
            self.active_record_id = vals[0]
            ent_sid.delete(0, tk.END); ent_sid.insert(0, vals[1])
            ent_nam.delete(0, tk.END); ent_nam.insert(0, vals[2])
            ent_prg.delete(0, tk.END); ent_prg.insert(0, vals[3])

        self.tree_teach_at.bind("<<TreeviewSelect>>", on_student_row_select)

        # Quick-toggle presence on double-click
        def toggle_teach_attendance(event):
            sel = self.tree_teach_at.selection()
            if not sel: return
            vals = self.tree_teach_at.item(sel, "values")
            r_id = vals[0]
            nxt = "Absent" if vals[5] == "Present" else "Present"
            
            conn = sqlite3.connect(DB_FILE)
            conn.execute("UPDATE participants SET attendance=? WHERE id=?", (nxt, r_id))
            conn.commit()
            conn.close()
            self.refresh_teacher_attendance()

        self.tree_teach_at.bind("<Double-1>", toggle_teach_attendance)

        # Action 1: Execute Update/Edit Query
        def execute_update_record():
            if not self.active_record_id:
                messagebox.showwarning("Selection Required", "Please click a student row from the tracking matrix first.")
                return
            
            conn = sqlite3.connect(DB_FILE)
            conn.execute("""
                UPDATE participants 
                SET student_id = ?, name = ?, program = ? 
                WHERE id = ?
            """, (ent_sid.get().strip(), ent_nam.get().strip(), ent_prg.get().strip(), self.active_record_id))
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Success", "Student records structurally modernized and saved.")
            clear_action_fields()
            self.refresh_teacher_attendance()

        # Action 2: Execute Drop/Remove Query
        def execute_remove_record():
            if not self.active_record_id:
                messagebox.showwarning("Selection Required", "Please click the student row you intend to erase.")
                return
            
            confirm = messagebox.askyesno("Confirm Deletion", "Are you sure you want to completely remove this student record from the ledger entry tracking index?")
            if confirm:
                conn = sqlite3.connect(DB_FILE)
                conn.execute("DELETE FROM participants WHERE id = ?", (self.active_record_id,))
                conn.commit()
                conn.close()
                
                messagebox.showinfo("Removed", "Student record dropped successfully.")
                clear_action_fields()
                self.refresh_teacher_attendance()

        def clear_action_fields():
            self.active_record_id = None
            ent_sid.delete(0, tk.END)
            ent_nam.delete(0, tk.END)
            ent_prg.delete(0, tk.END)

        # Operational Control Triggers
        btn_edit = tk.Button(action_pane, text="Update Record", font=("Segoe UI", 9, "bold"), bg=self.app.accent_blue, fg="white", command=execute_update_record, relief="flat", cursor="hand2", padx=10)
        btn_edit.grid(row=0, column=6, padx=10, pady=5)

        btn_drop = tk.Button(action_pane, text="Remove Record", font=("Segoe UI", 9, "bold"), bg=self.app.accent_red, fg="white", command=execute_remove_record, relief="flat", cursor="hand2", padx=10)
        btn_drop.grid(row=0, column=7, padx=5, pady=5)

        self.refresh_teacher_attendance()

    def refresh_teacher_attendance(self):
        for item in self.tree_teach_at.get_children(): 
            self.tree_teach_at.delete(item)
        conn = sqlite3.connect(DB_FILE)
        for row in conn.execute("SELECT id, student_id, name, program, event_id, attendance FROM participants"):
            self.tree_teach_at.insert("", "end", values=row)
        conn.close()

    def assemble_announcements_view(self):
        self.tree_ann = ttk.Treeview(self.tab_announcements, columns=("ID", "Title", "Context Memo", "Timestamp"), show="headings")
        for c in ("ID", "Title", "Context Memo", "Timestamp"):
            self.tree_ann.heading(c, text=c)
            self.tree_ann.column(c, anchor="center")
        self.tree_ann.pack(fill="both", expand=True, padx=15, pady=15)
        self.refresh_announcements_list()

    def refresh_announcements_list(self):
        for item in self.tree_ann.get_children(): self.tree_ann.delete(item)
        conn = sqlite3.connect(DB_FILE)
        for row in conn.execute("SELECT id, title, content, date_posted FROM announcements ORDER BY id DESC"): self.tree_ann.insert("", "end", values=row)
        conn.close()

    def assemble_feedbacks_reports_view(self):
        self.tree_rep = ttk.Treeview(self.tab_reports, columns=("FeedbackID", "StudentID", "EventID", "Rating Metrics", "Comments Ledger Summary"), show="headings")
        for c in ("FeedbackID", "StudentID", "EventID", "Rating Metrics", "Comments Ledger Summary"):
            self.tree_rep.heading(c, text=c)
            self.tree_rep.column(c, anchor="center")
        self.tree_rep.pack(fill="both", expand=True, padx=15, pady=15)
        self.refresh_reports_list()

    def refresh_reports_list(self):
        for item in self.tree_rep.get_children(): self.tree_rep.delete(item)
        conn = sqlite3.connect(DB_FILE)
        for row in conn.execute("SELECT id, student_id, event_id, rating, comments FROM feedbacks"): self.tree_rep.insert("", "end", values=row)
        conn.close()


# =========================================================================
# 5. SECURE STUDENT ACCOUNT ACCESSIBILITY PORTAL
# =========================================================================
class StudentDashboard:
    def __init__(self, parent, app):
        self.app = app
        
        ribbon = tk.Frame(parent, bg=app.card_bg, height=65)
        ribbon.pack(fill="x")
        ribbon.pack_propagate(False)
        
        tk.Label(ribbon, text=f"🎓 STUDENT SYSTEM GATEWAY : {app.current_name.upper()}", font=("Segoe UI", 13, "bold"), fg=app.text_white, bg=app.card_bg).pack(side="left", padx=20)
        tk.Button(ribbon, text="Exit Session", font=("Segoe UI", 9, "bold"), bg="#374151", fg="white", command=app.display_login_gateway, relief="flat", cursor="hand2", padx=15).pack(side="right", padx=20)
        
        self.tabs = ttk.Notebook(parent)
        self.tabs.pack(fill="both", expand=True, padx=15, pady=15)
        
        self.tab_cal = tk.Frame(self.tabs, bg=app.bg_dark)
        self.tab_notif = tk.Frame(self.tabs, bg=app.bg_dark)
        self.tab_mark = tk.Frame(self.tabs, bg=app.bg_dark)
        self.tab_feed = tk.Frame(self.tabs, bg=app.bg_dark)
        
        self.tabs.add(self.tab_cal, text=" Campus Events Calendar ")
        self.tabs.add(self.tab_notif, text=" Notifications Hub ")
        self.tabs.add(self.tab_mark, text=" Self Attendance Registration ")
        self.tabs.add(self.tab_feed, text=" Submit Feedback Evaluation ")
        
        self.assemble_calendar_view()
        self.assemble_notifications_view()
        self.assemble_self_attendance_view()
        self.assemble_feedback_submission_view()

    def assemble_calendar_view(self):
        card = tk.LabelFrame(self.tab_cal, text=" Active Approved Campus Events Calendar Channels ", font=("Segoe UI", 11, "bold"), bg=self.app.card_bg, fg=self.app.text_white, padx=15, pady=15)
        card.pack(fill="both", expand=True, padx=15, pady=15)
        
        self.tree_scal = ttk.Treeview(card, columns=("ID", "Event", "Location", "Date Scheduled", "Speakers Blueprint"), show="headings")
        for c in ("ID", "Event", "Location", "Date Scheduled", "Speakers Blueprint"):
            self.tree_scal.heading(c, text=c)
            self.tree_scal.column(c, anchor="center")
        self.tree_scal.pack(fill="both", expand=True)
        self.refresh_student_calendar()

    def refresh_student_calendar(self):
        for item in self.tree_scal.get_children(): self.tree_scal.delete(item)
        conn = sqlite3.connect(DB_FILE)
        for row in conn.execute("SELECT id, title, venue, date, speakers FROM events WHERE status='Approved'"): self.tree_scal.insert("", "end", values=row)
        conn.close()

    def assemble_notifications_view(self):
        card = tk.LabelFrame(self.tab_notif, text=" Admin Notice Bulletins & Announcements Feed ", font=("Segoe UI", 11, "bold"), bg=self.app.card_bg, fg=self.app.text_white, padx=15, pady=15)
        card.pack(fill="both", expand=True, padx=15, pady=15)
        
        self.tree_snot = ttk.Treeview(card, columns=("Broadcast ID", "Notice Heading Header", "Context Details", "Time Released"), show="headings")
        for c in ("Broadcast ID", "Notice Heading Header", "Context Details", "Time Released"):
            self.tree_snot.heading(c, text=c)
            self.tree_snot.column(c, anchor="center")
        self.tree_snot.pack(fill="both", expand=True)
        self.refresh_student_bulletins()

    def refresh_student_bulletins(self):
        for item in self.tree_snot.get_children(): self.tree_snot.delete(item)
        conn = sqlite3.connect(DB_FILE)
        for row in conn.execute("SELECT id, title, content, date_posted FROM announcements ORDER BY id DESC"): self.tree_snot.insert("", "end", values=row)
        conn.close()

    def assemble_self_attendance_view(self):
        card = tk.LabelFrame(self.tab_mark, text=" Self-Service Event Check-In Interface Panel ", font=("Segoe UI", 11, "bold"), bg=self.app.card_bg, fg=self.app.text_white, padx=20, pady=20)
        card.pack(fill="both", expand=True, padx=25, pady=25)
        
        tk.Label(card, text="Enter Target Event Mapping ID Number:", font=("Segoe UI", 11, "bold"), fg=self.app.text_white, bg=self.app.card_bg).pack(anchor="w", pady=5)
        ent_eid = tk.Entry(card, bg="#374151", fg="white", font=("Segoe UI", 12), width=15, insertbackground="white")
        ent_eid.pack(anchor="w", pady=5, ipady=4)
        
        tk.Label(card, text="Provide Your Student Identification Key:", font=("Segoe UI", 11, "bold"), fg=self.app.text_white, bg=self.app.card_bg).pack(anchor="w", pady=(15, 5))
        ent_sid = tk.Entry(card, bg="#374151", fg="white", font=("Segoe UI", 12), width=25, insertbackground="white")
        ent_sid.pack(anchor="w", pady=5, ipady=4)
        
        def mark_present_action():
            eid = ent_eid.get().strip()
            sid = ent_sid.get().strip()
            if not eid or not sid:
                messagebox.showwarning("Fields Empty", "Please explicitly state both Verification variables.")
                return
                
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM participants WHERE event_id=? AND (student_id=? OR name LIKE ?)", (eid, sid, f"%{self.app.current_name}%"))
            match = cursor.fetchone()
            
            if match:
                cursor.execute("UPDATE participants SET attendance='Present' WHERE id=?", (match[0],))
                conn.commit()
                messagebox.showinfo("Success Checked-In", f"Attendance ledger verified! '{self.app.current_name}' logged as Present.")
                ent_eid.delete(0, tk.END); ent_sid.delete(0, tk.END)
            else:
                # Direct structural database fallback append mechanism
                cursor.execute("INSERT INTO participants (student_id, name, year_level, section, program, event_id, attendance) VALUES (?, ?, 'N/A', 'N/A', 'BSIT', ?, 'Present')",
                               (sid, self.app.current_name, eid))
                conn.commit()
                messagebox.showinfo("Success Registered", "New registrant mapping profile appended. Marked Present safely.")
                ent_eid.delete(0, tk.END); ent_sid.delete(0, tk.END)
            conn.close()
            
        tk.Button(card, text="Confirm Live Self Check-In Status", font=("Segoe UI", 11, "bold"), bg=self.app.accent_blue, fg="white", command=mark_present_action, relief="flat", cursor="hand2").pack(anchor="w", pady=25, ipady=5)

    def assemble_feedback_submission_view(self):
        card = tk.LabelFrame(self.tab_feed, text=" Quality Assurance Program Evaluation Form ", font=("Segoe UI", 11, "bold"), bg=self.app.card_bg, fg=self.app.text_white, padx=20, pady=20)
        card.pack(fill="both", expand=True, padx=25, pady=25)
        
        tk.Label(card, text="Target Event Reference ID:", fg=self.app.text_white, bg=self.app.card_bg).grid(row=0, column=0, sticky="w", pady=5)
        ent_feid = tk.Entry(card, bg="#374151", fg="white", insertbackground="white", width=10)
        ent_feid.grid(row=0, column=1, sticky="w", padx=10)
        
        tk.Label(card, text="Rating Score (1-5 Stars):", fg=self.app.text_white, bg=self.app.card_bg).grid(row=1, column=0, sticky="w", pady=10)
        box_rate = ttk.Combobox(card, values=["5", "4", "3", "2", "1"], width=8, state="readonly")
        box_rate.current(0)
        box_rate.grid(row=1, column=1, sticky="w", padx=10)
        
        tk.Label(card, text="Elaborated Comments / Suggestions:", fg=self.app.text_white, bg=self.app.card_bg).grid(row=2, column=0, sticky="nw", pady=10)
        txt_comm = tk.Text(card, bg="#374151", fg="white", insertbackground="white", height=5, width=40)
        txt_comm.grid(row=2, column=1, sticky="w", padx=10, pady=10)
        
        def commit_feedback_action():
            fid = ent_feid.get().strip()
            if not fid:
                messagebox.showwarning("Target Missing", "Specify the event ID being evaluated.")
                return
            conn = sqlite3.connect(DB_FILE)
            conn.execute("INSERT INTO feedbacks (student_id, event_id, rating, comments) VALUES (?, ?, ?, ?)",
                         (self.app.current_user, fid, int(box_rate.get()), txt_comm.get("1.0", tk.END).strip()))
            conn.commit()
            conn.close()
            messagebox.showinfo("Thank You", "Evaluation parameters processed safely into metrics ledger indices.")
            ent_feid.delete(0, tk.END); txt_comm.delete("1.0", tk.END)
            
        tk.Button(card, text="Dispatch Evaluation Metric Data", font=("Segoe UI", 10, "bold"), bg=self.app.accent_green, fg="white", command=commit_feedback_action, relief="flat", cursor="hand2").grid(row=3, column=1, sticky="w", padx=10, pady=10)


# =========================================================================
# 6. SYSTEM RUNTIME ENTRY POINT
# =========================================================================
if __name__ == "__main__":
    init_db()
    system_app = SchoolEventManagementSystem()
    system_app.mainloop()