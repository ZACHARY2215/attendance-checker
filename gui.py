import tkinter as tk
from tkinter import ttk, messagebox
import cv2
import threading
import time
from datetime import datetime, timedelta
import pandas as pd
import os
import face_recognition
from PIL import Image, ImageTk
import numpy as np
import customtkinter
import tkinter.filedialog as filedialog
import hashlib

class DarkTheme:
    BG = '#23272e'
    FG = '#f8f9fa'
    BUTTON_BG = '#343a40'
    BUTTON_FG = '#f8f9fa'
    BUTTON_HOVER = '#424a53'
    ACCENT = '#007ACC'
    ACCENT_HOVER = '#0090EA'
    SUCCESS = '#28a745'
    SUCCESS_HOVER = '#2fc751'
    WARNING = '#ffc107'
    WARNING_HOVER = '#ffcd39'
    ERROR = '#dc3545'
    ERROR_HOVER = '#e04757'
    SIDEBAR_BG = '#181a1b'
    SIDEBAR_ACTIVE = '#007ACC'
    CARD_BG = '#2c313a'
    HEADER_BG = '#181a1b'
    HEADER_FG = '#f8f9fa'
    NOTIF_BG = '#23272e'
    NOTIF_FG = '#f8f9fa'
    FONT = 'Arial'
    BUTTON_FONT = ('Arial', 11, 'bold')
    BUTTON_PADDING = 8
    BUTTON_RADIUS = 8
    BUTTON_SHADOW = '0 2 4 #00000033'
    TRANSITION_TIME = '0.2s'

class CustomCalendar(tk.Toplevel):
    def __init__(self, parent, date_var):
        super().__init__(parent)
        self.date_var = date_var
        self.title("Select Date")
        self.configure(bg=DarkTheme.CARD_BG)
        self.resizable(False, False)
        self.grab_set()
        
        try:
            current_date = datetime.strptime(date_var.get(), '%Y-%m-%d')
        except:
            current_date = datetime.now()
        
        self.year = current_date.year
        self.month = current_date.month
        
        # Header frame
        header_frame = tk.Frame(self, bg=DarkTheme.CARD_BG)
        header_frame.pack(fill='x', padx=10, pady=5)
        
        # Previous month button
        prev_btn = customtkinter.CTkButton(
            header_frame,
            text="<",
            command=self.prev_month,
            width=30,
            height=30,
            fg_color=DarkTheme.BUTTON_BG,
            hover_color=DarkTheme.BUTTON_HOVER,
            bg_color=DarkTheme.CARD_BG,
            text_color=DarkTheme.FG,
            font=customtkinter.CTkFont(family=DarkTheme.FONT, size=11)
        )
        prev_btn.pack(side='left', padx=5)
        
        # Month and year label
        self.header_label = tk.Label(
            header_frame,
            text="",
            bg=DarkTheme.CARD_BG,
            fg=DarkTheme.FG,
            font=(DarkTheme.FONT, 12, 'bold')
        )
        self.header_label.pack(side='left', expand=True)
        
        # Next month button
        next_btn = customtkinter.CTkButton(
            header_frame,
            text=">",
            command=self.next_month,
            width=30,
            height=30,
            fg_color=DarkTheme.BUTTON_BG,
            hover_color=DarkTheme.BUTTON_HOVER,
            bg_color=DarkTheme.CARD_BG,
            text_color=DarkTheme.FG,
            font=customtkinter.CTkFont(family=DarkTheme.FONT, size=11)
        )
        next_btn.pack(side='right', padx=5)
        
        # Calendar frame
        calendar_frame = tk.Frame(self, bg=DarkTheme.CARD_BG)
        calendar_frame.pack(padx=10, pady=5)
        
        # Weekday headers
        weekdays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        for i, day in enumerate(weekdays):
            tk.Label(
                calendar_frame,
                text=day,
                width=4,
                bg=DarkTheme.CARD_BG,
                fg=DarkTheme.FG,
                font=(DarkTheme.FONT, 10)
            ).grid(row=0, column=i, padx=2, pady=2)
        
        # Create buttons for days
        self.day_buttons = []
        for week in range(6):
            for day in range(7):
                btn = customtkinter.CTkButton(
                    calendar_frame,
                    text="",
                    width=40,
                    height=30,
                    fg_color=DarkTheme.BUTTON_BG,
                    hover_color=DarkTheme.BUTTON_HOVER,
                    bg_color=DarkTheme.CARD_BG,
                    text_color=DarkTheme.FG,
                    font=customtkinter.CTkFont(family=DarkTheme.FONT, size=10),
                    command=lambda w=week, d=day: self.select_date(w, d)
                )
                btn.grid(row=week + 1, column=day, padx=2, pady=2)
                self.day_buttons.append(btn)
        
        # Year selection
        year_frame = tk.Frame(self, bg=DarkTheme.CARD_BG)
        year_frame.pack(fill='x', padx=10, pady=5)
        
        prev_year_btn = customtkinter.CTkButton(
            year_frame,
            text="◀",
            command=self.prev_year,
            width=30,
            height=30,
            fg_color=DarkTheme.BUTTON_BG,
            hover_color=DarkTheme.BUTTON_HOVER,
            bg_color=DarkTheme.CARD_BG,
            text_color=DarkTheme.FG,
            font=customtkinter.CTkFont(family=DarkTheme.FONT, size=11)
        )
        prev_year_btn.pack(side='left', padx=5)
        
        self.year_label = tk.Label(
            year_frame,
            text=str(self.year),
            bg=DarkTheme.CARD_BG,
            fg=DarkTheme.FG,
            font=(DarkTheme.FONT, 12, 'bold')
        )
        self.year_label.pack(side='left', expand=True)
        
        next_year_btn = customtkinter.CTkButton(
            year_frame,
            text="▶",
            command=self.next_year,
            width=30,
            height=30,
            fg_color=DarkTheme.BUTTON_BG,
            hover_color=DarkTheme.BUTTON_HOVER,
            bg_color=DarkTheme.CARD_BG,
            text_color=DarkTheme.FG,
            font=customtkinter.CTkFont(family=DarkTheme.FONT, size=11)
        )
        next_year_btn.pack(side='right', padx=5)
        
        self.update_calendar()
        self.geometry(f"+{parent.winfo_rootx()}+{parent.winfo_rooty() + 50}")
    
    def update_calendar(self):
        month_name = datetime(2000, self.month, 1).strftime('%B')
        self.header_label.config(text=month_name)
        self.year_label.config(text=str(self.year))
        
        first_day = datetime(self.year, self.month, 1)
        last_day = (datetime(self.year, self.month + 1, 1) if self.month < 12 
                   else datetime(self.year + 1, 1, 1)) - timedelta(days=1)
        num_days = last_day.day
        
        first_weekday = first_day.weekday()
        
        for btn in self.day_buttons:
            btn.configure(text="", state="disabled", fg_color=DarkTheme.BUTTON_BG)
        
        for i in range(num_days):
            day = i + 1
            button_index = first_weekday + i
            if button_index < len(self.day_buttons):
                self.day_buttons[button_index].configure(
                    text=str(day),
                    state="normal",
                    fg_color=DarkTheme.BUTTON_BG
                )
    
    def select_date(self, week, day):
        button_index = week * 7 + day
        if button_index < len(self.day_buttons):
            btn = self.day_buttons[button_index]
            if btn.cget("state") != "disabled":
                day = int(btn.cget("text"))
                selected_date = datetime(self.year, self.month, day)
                self.date_var.set(selected_date.strftime('%Y-%m-%d'))
                self.destroy()
    
    def prev_month(self):
        if self.month > 1:
            self.month -= 1
        else:
            self.month = 12
            self.year -= 1
        self.update_calendar()
    
    def next_month(self):
        if self.month < 12:
            self.month += 1
        else:
            self.month = 1
            self.year += 1
        self.update_calendar()
    
    def prev_year(self):
        self.year -= 1
        self.update_calendar()
    
    def next_year(self):
        self.year += 1
        self.update_calendar()

class NotificationPopup:
    def __init__(self, root, message, level='info', duration=4000):
        self.top = tk.Toplevel(root)
        self.top.overrideredirect(True)
        self.top.attributes('-topmost', True)
        color = {
            'info': DarkTheme.ACCENT,
            'success': DarkTheme.SUCCESS,
            'error': DarkTheme.ERROR,
            'warning': DarkTheme.WARNING
        }.get(level, DarkTheme.ACCENT)
        self.top.configure(bg=color)
        label = tk.Label(self.top, text=message, bg=color, fg=DarkTheme.NOTIF_FG, font=(DarkTheme.FONT, 11), padx=20, pady=10)
        label.pack()
        self.top.update_idletasks()
        x = root.winfo_x() + root.winfo_width() - self.top.winfo_width() - 40
        y = root.winfo_y() + 90
        self.top.geometry(f'+{x}+{y}')
        self.top.after(duration, self.top.destroy)

class AttendanceGUI:
    UPDATE_INTERVAL = 30
    
    def __init__(self, root):
        self.root = root
        self.root.title("Attendance Monitoring System")
        self.root.geometry("1280x850")
        self.root.configure(bg=DarkTheme.BG)
        self.root.option_add("*Font", f"{DarkTheme.FONT} 11")
        
        # User authentication
        self.current_user = None
        self.ensure_default_admin()
        
        # Configure customtkinter
        customtkinter.set_appearance_mode("dark")
        customtkinter.set_default_color_theme("blue")
        customtkinter.set_widget_scaling(1.0)
        customtkinter.set_window_scaling(1.0)
        
        self.create_custom_buttons()
        self.button_props = {
            'corner_radius': 10,
            'border_width': 0,
            'font': customtkinter.CTkFont(family=DarkTheme.FONT, size=11, weight="bold"),
            'hover': True,
            'border_spacing': 10
        }
        
        # Camera and thread control
        self.camera = None
        self.camera_lock = threading.Lock()
        self.frame_ready = threading.Event()
        self.current_frame = None
        self.camera_active = False
        self.camera_thread = None
        self.monitoring_active = False
        self.monitoring_thread = None
        
        os.makedirs('faces', exist_ok=True)
        self.attendance_file = 'attendance.xlsx'
        if not os.path.exists(self.attendance_file):
            pd.DataFrame(columns=[
                'student_id', 'name', 'check_in_time', 'last_seen_time',
                'status', 'total_time_present'
            ]).to_excel(self.attendance_file, index=False)
        
        self.STATUS_THRESHOLDS = {
            'PRESENT': 0,
            'LATE': 15,
            'LEFT_EARLY': 30,
            'ABSENT': None
        }
        
        # Initialize with login screen
        self.show_login_screen()
    
    def ensure_default_admin(self):
        if not os.path.exists('users.csv'):
            df = pd.DataFrame([{'username': 'admin', 'password': hashlib.sha256('admin'.encode()).hexdigest(), 'role': 'admin'}])
            df.to_csv('users.csv', index=False)
    
    def show_login_screen(self):
        """Show login interface in the main window"""
        # Clear any existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Create login container
        login_container = tk.Frame(self.root, bg=DarkTheme.BG)
        login_container.pack(fill='both', expand=True)
        
        # Center the login form
        login_frame = tk.Frame(login_container, bg=DarkTheme.CARD_BG, padx=40, pady=40)
        login_frame.place(relx=0.5, rely=0.5, anchor='center')
        
        # Title
        title_label = tk.Label(
            login_frame,
            text="Attendance Monitoring System",
            bg=DarkTheme.CARD_BG,
            fg=DarkTheme.FG,
            font=(DarkTheme.FONT, 24, 'bold')
        )
        title_label.pack(pady=(0, 10))
        
        # Subtitle
        subtitle_label = tk.Label(
            login_frame,
            text="Please login to continue.",
            bg=DarkTheme.CARD_BG,
            fg=DarkTheme.FG,
            font=(DarkTheme.FONT, 10)
        )
        subtitle_label.pack(pady=(0, 50))
        
        # Username field
        tk.Label(
            login_frame,
            text="Username:",
            bg=DarkTheme.CARD_BG,
            fg=DarkTheme.FG,
            font=(DarkTheme.FONT, 12)
        ).pack( pady=(0, 5))
        
        self.username_var = tk.StringVar()
        username_entry = customtkinter.CTkEntry(
            login_frame,
            textvariable=self.username_var,
            width=300,
            height=40,
            fg_color=DarkTheme.BG,
            bg_color=DarkTheme.CARD_BG,
            text_color=DarkTheme.FG,
            border_color=DarkTheme.BUTTON_BG,
            font=customtkinter.CTkFont(family=DarkTheme.FONT, size=12)
        )
        username_entry.pack(pady=(0, 20))
        username_entry.focus()
        
        # Password field
        tk.Label(
            login_frame,
            text="Password:",
            bg=DarkTheme.CARD_BG,
            fg=DarkTheme.FG,
            font=(DarkTheme.FONT, 12)
        ).pack(pady=(0, 5))
        
        self.password_var = tk.StringVar()
        password_entry = customtkinter.CTkEntry(
            login_frame,
            textvariable=self.password_var,
            width=300,
            height=40,
            fg_color=DarkTheme.BG,
            bg_color=DarkTheme.CARD_BG,
            text_color=DarkTheme.FG,
            border_color=DarkTheme.BUTTON_BG,
            show='*',
            font=customtkinter.CTkFont(family=DarkTheme.FONT, size=12)
        )
        password_entry.pack(pady=(0, 30))
        
        # Login button
        login_btn = customtkinter.CTkButton(
            login_frame,
            text="Login",
            command=self.do_login,
            width=300,
            height=40,
            fg_color=DarkTheme.ACCENT,
            hover_color=DarkTheme.ACCENT_HOVER,
            bg_color=DarkTheme.CARD_BG,
            text_color=DarkTheme.FG,
            font=customtkinter.CTkFont(family=DarkTheme.FONT, size=14, weight="bold")
        )
        login_btn.pack(pady=(0, 20))
        
        # Error message label
        self.error_label = tk.Label(
            login_frame,
            text="",
            bg=DarkTheme.CARD_BG,
            fg=DarkTheme.ERROR,
            font=(DarkTheme.FONT, 11)
        )
        self.error_label.pack()
        
        
        # Bind Enter key to login
        self.root.bind('<Return>', lambda event: self.do_login())
    
    def do_login(self):
        """Handle login authentication"""
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()
        
        if not username or not password:
            self.error_label.config(text="Please enter both username and password")
            return
        
        if not os.path.exists('users.csv'):
            self.error_label.config(text="No users found in system")
            return
        
        try:
            df = pd.read_csv('users.csv')
            hashed = hashlib.sha256(password.encode()).hexdigest()
            user_row = df[(df['username'] == username) & (df['password'] == hashed)]
            
            if user_row.empty:
                self.error_label.config(text="Invalid username or password")
                return
            
            # Successful login
            self.current_user = {'username': username, 'role': user_row.iloc[0]['role']}
            self.show_main_application()
            
        except Exception as e:
            self.error_label.config(text=f"Login error: {str(e)}")
    
    def show_main_application(self):
        """Show the main attendance monitoring application after successful login"""
        # Clear login screen
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Unbind Enter key
        self.root.unbind('<Return>')
        
        # Initialize main application
        self.active_tab = 'Check-in'
        self.create_modern_gui()
        
        # Start camera automatically on launch
        self.start_camera()
        
        # Show welcome notification
        self.root.after(500, lambda: self.show_notification(
            f"Welcome, {self.current_user['username']}!", level='success'
        ))
    
    def create_custom_buttons(self):
        """Configure styles for all widgets to match dark theme"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure frame styles
        style.configure('Dark.TFrame', background=DarkTheme.BG)
        style.configure('Card.TFrame', background=DarkTheme.CARD_BG)
        style.configure('Header.TFrame', background=DarkTheme.HEADER_BG)
        
        # Configure label styles
        style.configure('Dark.TLabel',
                       background=DarkTheme.BG,
                       foreground=DarkTheme.FG)
        style.configure('Card.TLabel',
                       background=DarkTheme.CARD_BG,
                       foreground=DarkTheme.FG)
        style.configure('Header.TLabel',
                       background=DarkTheme.HEADER_BG,
                       foreground=DarkTheme.HEADER_FG,
                       font=(DarkTheme.FONT, 20, 'bold'))
        
        # Configure entry style
        style.configure('Dark.TEntry',
                       fieldbackground=DarkTheme.CARD_BG,
                       foreground=DarkTheme.FG,
                       insertcolor=DarkTheme.FG,
                       borderwidth=1)
        
        # Configure modern treeview style
        style.configure('Dark.Treeview',
                       background=DarkTheme.CARD_BG,
                       foreground=DarkTheme.FG,
                       fieldbackground=DarkTheme.CARD_BG,
                       borderwidth=0,
                       font=(DarkTheme.FONT, 11),
                       rowheight=40)
        
        style.configure('Dark.Treeview.Heading',
                       background=DarkTheme.BUTTON_BG,
                       foreground=DarkTheme.FG,
                       borderwidth=0,
                       font=(DarkTheme.FONT, 12, 'bold'),
                       padding=10)
        
        # Remove borders and configure selection
        style.layout('Dark.Treeview', [
            ('Treeview.treearea', {'sticky': 'nswe'})
        ])
        
        # Configure selection colors
        style.map('Dark.Treeview',
                 background=[('selected', DarkTheme.ACCENT),
                           ('!selected', DarkTheme.CARD_BG)],
                 foreground=[('selected', DarkTheme.FG)])
        
        # Configure heading style
        style.layout("Dark.Treeview.Heading", [
            ("Treeheading.cell", {"sticky": "nswe"}),
            ("Treeheading.border", {"sticky": "nswe", "children": [
                ("Treeheading.padding", {"sticky": "nswe", "children": [
                    ("Treeheading.image", {"side": "right", "sticky": ""}),
                    ("Treeheading.text", {"sticky": "we"})
                ]})
            ]})
        ])
        
        style.map("Dark.Treeview.Heading",
                 background=[("", DarkTheme.BUTTON_BG)],
                 foreground=[("", DarkTheme.FG)])
                 
        # Configure row colors
        style.map('Dark.Treeview',
                 background=[('selected', DarkTheme.ACCENT),
                           ('!selected', DarkTheme.CARD_BG)],
                 foreground=[('selected', DarkTheme.FG)])
        
        # Configure scrollbar style
        style.configure('Dark.Vertical.TScrollbar',
                       background=DarkTheme.CARD_BG,
                       borderwidth=0,
                       arrowcolor=DarkTheme.FG,
                       troughcolor=DarkTheme.BG)
        
        # Configure scrollbar layout
        style.layout('Dark.Vertical.TScrollbar', 
                 [('Vertical.Scrollbar.trough',
                   {'children': [('Vertical.Scrollbar.thumb', 
                                {'expand': '1'})],
                    'sticky': 'ns'})])
        
        # Remove borders from frames
        style.configure('TFrame', borderwidth=0)
        
        # Configure separator style
        style.configure('TSeparator', background=DarkTheme.BUTTON_BG)

    def create_modern_gui(self):
        # Header bar
        header = ttk.Frame(self.root, style='Header.TFrame', height=60)
        header.pack(side='top', fill='x')
        
        # Header content
        header_content = tk.Frame(header, bg=DarkTheme.HEADER_BG)
        header_content.pack(fill='both', expand=True, padx=30, pady=10)
        
        ttk.Label(header_content, text="Attendance Monitoring System", style='Header.TLabel').pack(side='left')
        
        # User info and logout
        user_frame = tk.Frame(header_content, bg=DarkTheme.HEADER_BG)
        user_frame.pack(side='right')
        
        user_label = tk.Label(
            user_frame,
            text=f"Welcome, {self.current_user['username']} ({self.current_user['role']})",
            bg=DarkTheme.HEADER_BG,
            fg=DarkTheme.HEADER_FG,
            font=(DarkTheme.FONT, 12)
        )
        user_label.pack(side='left', padx=(0, 20))
        
        logout_btn = customtkinter.CTkButton(
            user_frame,
            text="Logout",
            command=self.logout,
            width=80,
            height=30,
            fg_color=DarkTheme.ERROR,
            hover_color=DarkTheme.ERROR_HOVER,
            bg_color=DarkTheme.HEADER_BG,
            text_color=DarkTheme.FG,
            font=customtkinter.CTkFont(family=DarkTheme.FONT, size=10)
        )
        logout_btn.pack(side='right')
        
        # Sidebar
        sidebar = tk.Frame(self.root, bg=DarkTheme.SIDEBAR_BG, width=180)
        sidebar.pack(side='left', fill='y')
        sidebar.pack_propagate(False)
        
        self.sidebar_buttons = {}
        for tab, icon in zip(['Check-in', 'Monitoring', 'Reports', 'Admin', 'Quit'], ['📝', '🎥', '📊', '⚙️', '🚪']):
            btn = customtkinter.CTkButton(
                sidebar,
                text=f"{icon}  {tab}",
                command=lambda t=tab: self.switch_tab(t),
                fg_color=DarkTheme.SIDEBAR_BG if tab != self.active_tab else DarkTheme.SIDEBAR_ACTIVE,
                hover_color=DarkTheme.SIDEBAR_ACTIVE,
                bg_color=DarkTheme.SIDEBAR_BG,
                width=160,
                height=40,
                corner_radius=8,
                border_width=0,
                font=customtkinter.CTkFont(family=DarkTheme.FONT, size=12),
                hover=True
            )
            btn.pack(pady=6, padx=10)
            self.sidebar_buttons[tab] = btn
        
        self.main_content = ttk.Frame(self.root, style='Dark.TFrame')
        self.main_content.pack(side='left', fill='both', expand=True, padx=0, pady=0)
        
        self.tab_frames = {}
        for tab in ['Check-in', 'Monitoring', 'Reports', 'Admin']:
            frame = ttk.Frame(self.main_content, style='Dark.TFrame')
            self.tab_frames[tab] = frame
        
        self.setup_check_in_tab(self.tab_frames['Check-in'])
        self.setup_monitoring_tab(self.tab_frames['Monitoring'])
        self.setup_reports_tab(self.tab_frames['Reports'])
        self.setup_admin_tab(self.tab_frames['Admin'])
        
        self.show_tab('Check-in')
        self.setup_notification_bar()
    
    def logout(self):
        """Handle user logout"""
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            # Stop any active monitoring
            if self.monitoring_active:
                self.stop_monitoring()
            
            # Stop camera
            if self.camera_active:
                self.stop_camera()
            
            # Reset user
            self.current_user = None
            
            # Show login screen again
            self.show_login_screen()
    
    def switch_tab(self, tab):
        if tab == 'Quit':
            self.quit_application()
            return
            
        self.active_tab = tab
        # Update button styles
        for t, btn in self.sidebar_buttons.items():
            if t != 'Quit':
                if t == tab:
                    btn.configure(fg_color=DarkTheme.SIDEBAR_ACTIVE)
                else:
                    btn.configure(fg_color=DarkTheme.SIDEBAR_BG)
        
        self.show_tab(tab)
        
    def show_tab(self, tab):
        for t, frame in self.tab_frames.items():
            frame.pack_forget()
        self.tab_frames[tab].pack(fill='both', expand=True, padx=30, pady=30)
        # Auto-refresh report when switching to Reports tab
        if tab == 'Reports':
            self.refresh_report()
    
    def setup_check_in_tab(self, parent):
        # Card-like main container
        card = ttk.Frame(parent, style='Card.TFrame')
        card.pack(fill='both', expand=True, padx=40, pady=40)
        card.grid_columnconfigure(0, weight=2)
        card.grid_columnconfigure(1, weight=1)
        
        # Left side - Camera
        camera_frame = ttk.Frame(card, style='Card.TFrame')
        camera_frame.grid(row=0, column=0, sticky='nsew', padx=20, pady=20)
        camera_header = ttk.Label(camera_frame, text="Camera", style='Card.TLabel', font=(DarkTheme.FONT, 16, 'bold'))
        camera_header.pack(anchor='w', pady=(0, 10))
        self.camera_label = ttk.Label(camera_frame, style='Card.TLabel')
        self.camera_label.pack(pady=10)
        
        # Camera controls
        camera_controls = ttk.Frame(camera_frame, style='Card.TFrame')
        camera_controls.pack(pady=10)
        
        self.checkin_stop_button = customtkinter.CTkButton(
            camera_controls,
            text="Stop Camera",
            command=self.stop_checkin_camera,
            fg_color=DarkTheme.WARNING,
            hover_color=DarkTheme.WARNING_HOVER,
            bg_color=DarkTheme.CARD_BG,
            width=120,
            **self.button_props
        )
        self.checkin_stop_button.pack(side='left', padx=5)
        
        # Right side - Registration and Check-in
        control_frame = ttk.Frame(card, style='Card.TFrame')
        control_frame.grid(row=0, column=1, sticky='nsew', padx=20, pady=20)
        
        # Registration section
        reg_header = ttk.Label(control_frame, text="New Student Registration", 
                             style='Card.TLabel', font=(DarkTheme.FONT, 14, 'bold'))
        reg_header.pack(anchor='w', pady=(0, 8))

        reg_frame = ttk.Frame(control_frame, style='Card.TFrame')
        reg_frame.pack(fill='x', pady=8)
        
        ttk.Label(reg_frame, text="Student ID:", style='Card.TLabel').pack(anchor='w', pady=2)
        self.reg_id_var = tk.StringVar()
        ttk.Entry(reg_frame, textvariable=self.reg_id_var, style='Dark.TEntry').pack(fill='x', pady=2)
        
        ttk.Label(reg_frame, text="Name:", style='Card.TLabel').pack(anchor='w', pady=2)
        self.reg_name_var = tk.StringVar()
        ttk.Entry(reg_frame, textvariable=self.reg_name_var, style='Dark.TEntry').pack(fill='x', pady=2)
        
        register_btn = customtkinter.CTkButton(
            reg_frame,
            text="Register and Capture Face",
            command=self.register_student,
            fg_color=DarkTheme.BUTTON_BG,
            hover_color=DarkTheme.BUTTON_HOVER,
            bg_color=DarkTheme.CARD_BG,
            width=200,
            **self.button_props
        )
        register_btn.pack(pady=8)
        
        # Separator
        ttk.Separator(control_frame, orient='horizontal').pack(fill='x', pady=16)
        
        # Check-in section
        checkin_header = ttk.Label(control_frame, text="Check-in", 
                                 style='Card.TLabel', font=(DarkTheme.FONT, 14, 'bold'))
        checkin_header.pack(anchor='w', pady=(0, 8))

        checkin_frame = ttk.Frame(control_frame, style='Card.TFrame')
        checkin_frame.pack(fill='x', pady=8)
        
        ttk.Label(checkin_frame, text="Student ID:", style='Card.TLabel').pack(anchor='w', pady=2)
        self.student_id_var = tk.StringVar()
        ttk.Entry(checkin_frame, textvariable=self.student_id_var, style='Dark.TEntry').pack(fill='x', pady=2)
        
        mock_rfid_btn = customtkinter.CTkButton(
            checkin_frame,
            text="Mock RFID Scan",
            command=self.mock_rfid_scan,
            fg_color=DarkTheme.BUTTON_BG,
            hover_color=DarkTheme.BUTTON_HOVER,
            bg_color=DarkTheme.CARD_BG,
            width=200,
            **self.button_props
        )
        mock_rfid_btn.pack(pady=4)
        
        checkin_btn = customtkinter.CTkButton(
            checkin_frame,
            text="Check In",
            command=self.process_check_in,
            fg_color=DarkTheme.ACCENT,
            hover_color=DarkTheme.ACCENT_HOVER,
            bg_color=DarkTheme.CARD_BG,
            width=200,
            **self.button_props
        )
        checkin_btn.pack(pady=4)
    
    def setup_monitoring_tab(self, parent):
        # Card-like main container
        card = ttk.Frame(parent, style='Card.TFrame')
        card.pack(fill='both', expand=True, padx=40, pady=40)
        
        # Header
        header = ttk.Label(card, text="Monitoring", style='Card.TLabel', font=(DarkTheme.FONT, 16, 'bold'))
        header.pack(anchor='w', pady=(0, 16))
        
        # Status and controls card
        status_card = ttk.Frame(card, style='Card.TFrame')
        status_card.pack(fill='x', pady=(0, 20))
        status_card.columnconfigure(0, weight=1)
        status_card.columnconfigure(1, weight=0)
        
        # Status indicators
        status_frame = ttk.Frame(status_card, style='Card.TFrame')
        status_frame.grid(row=0, column=0, sticky='w', padx=10)
        
        self.status_label = ttk.Label(status_frame, 
                                    text="⚫ Monitoring inactive", 
                                    style='Card.TLabel',
                                    font=(DarkTheme.FONT, 12, 'bold'))
        self.status_label.pack(side='left', padx=5)
        
        self.last_update_label = ttk.Label(status_frame,
                                         text="Last update: Never",
                                         style='Card.TLabel')
        self.last_update_label.pack(side='left', padx=20)
        
        # Controls
        controls_frame = ttk.Frame(status_card, style='Card.TFrame')
        controls_frame.grid(row=0, column=1, sticky='e', padx=10)
        
        self.start_button = customtkinter.CTkButton(
            controls_frame,
            text="▶ Start Monitoring",
            command=self.start_monitoring,
            fg_color=DarkTheme.SUCCESS,
            hover_color=DarkTheme.SUCCESS_HOVER,
            bg_color=DarkTheme.CARD_BG,
            width=150,
            **self.button_props
        )
        self.start_button.pack(side='left', padx=5)
        
        self.stop_button = customtkinter.CTkButton(
            controls_frame,
            text="⏹ Stop Monitoring",
            command=self.start_stop_monitoring,
            fg_color=DarkTheme.WARNING,
            hover_color=DarkTheme.WARNING_HOVER,
            bg_color=DarkTheme.CARD_BG,
            width=150,
            **self.button_props
        )
        
        self.reset_button = customtkinter.CTkButton(
            controls_frame,
            text="🔄 Reset Logs",
            command=self.reset_logs,
            fg_color=DarkTheme.BUTTON_BG,
            hover_color=DarkTheme.BUTTON_HOVER,
            bg_color=DarkTheme.CARD_BG,
            width=120,
            **self.button_props
        )
        self.reset_button.pack(side='left', padx=5)
        
        # Camera view card
        camera_card = ttk.Frame(card, style='Card.TFrame')
        camera_card.pack(fill='both', expand=True, pady=20)
        self.monitor_label = ttk.Label(camera_card, style='Card.TLabel', borderwidth=2, relief="solid")
        self.monitor_label.pack(pady=10, padx=10)
        
        # Detection info card
        info_card = ttk.Frame(card, style='Card.TFrame')
        info_card.pack(fill='x', pady=10)
        detection_header = ttk.Label(info_card, text="Currently Detected:", style='Card.TLabel', font=(DarkTheme.FONT, 12, 'bold'))
        detection_header.pack(side='left', padx=5)
        self.current_detections = ttk.Label(info_card, 
                                          text="No faces detected", 
                                          style='Card.TLabel',
                                          font=(DarkTheme.FONT, 12))
        self.current_detections.pack(side='left', padx=5)
        
        # Initialize monitoring variables
        self.known_face_encodings = {}
        self.known_face_names = {}
        self.last_update_time = None
        self.load_known_faces()
    
    def load_known_faces(self):
        """Load all registered face encodings"""
        try:
            # Clear existing encodings
            self.known_face_encodings.clear()
            self.known_face_names.clear()

            students_df = pd.read_csv('students.csv') if os.path.exists('students.csv') else pd.DataFrame(columns=['student_id', 'name'])
            for _, row in students_df.iterrows():
                student_id = str(row['student_id'])
                encoding_path = os.path.join('faces', f"{student_id}.npy")
                if os.path.exists(encoding_path):
                    self.known_face_encodings[student_id] = np.load(encoding_path)
                    self.known_face_names[student_id] = row['name']
            print(f"Loaded {len(self.known_face_encodings)} face encodings for recognition")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load face encodings: {str(e)}")
    
    def start_camera(self):
        """Start the camera feed with proper resource management"""
        with self.camera_lock:
            if not self.camera_active:
                if self.camera is None:
                    self.camera = cv2.VideoCapture(0)
                if not self.camera.isOpened():
                    messagebox.showerror("Error", "Failed to open camera")
                    return
                # Set camera properties for better performance
                self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                self.camera.set(cv2.CAP_PROP_FPS, 30)
                self.camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            self.camera_active = True
            self.camera_thread = threading.Thread(target=self.update_camera_feed)
            self.camera_thread.daemon = True
            self.camera_thread.start()
    
    def stop_camera(self):
        """Safely stop the camera without blocking"""
        with self.camera_lock:
            self.camera_active = False
        
        def cleanup_camera():
            with self.camera_lock:
                if self.camera is not None:
                    self.camera.release()
                    self.camera = None
                # Clear the camera display
                if hasattr(self, 'camera_label'):
                    self.camera_label.configure(image='')
                    self.camera_label.image = None
        
        # Schedule camera cleanup in the main thread
        self.root.after(0, cleanup_camera)
    
    def update_camera_feed(self):
        """Update camera feed with frame skipping for performance"""
        frame_count = 0
        
        while self.camera_active:
            with self.camera_lock:
                if self.camera is None or not self.camera.isOpened():
                    break
                    
                ret, frame = self.camera.read()
                if not ret:
                    break
                
                # Process every 2nd frame for better performance
                frame_count += 1
                if frame_count % 2 != 0:
                    continue
                
                # Store current frame for monitoring
                self.current_frame = frame.copy()
                self.frame_ready.set()
                
                # Convert and resize for display
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame_rgb)
                img = img.resize((320, 240), Image.Resampling.LANCZOS)
                img_tk = ImageTk.PhotoImage(img)
                
                # Update label if still active
                if self.camera_active and hasattr(self, 'camera_label'):
                    self.camera_label.configure(image=img_tk)
                    self.camera_label.image = img_tk
            
            # Add small delay to reduce CPU usage
            time.sleep(0.01)
    
    def start_stop_monitoring(self):
        """Handle monitoring start/stop with proper thread management"""
        if self.monitoring_active:
            self.root.after(0, self.stop_monitoring)
        else:
            self.start_monitoring()
    
    def start_monitoring(self):
        """Start monitoring with proper button management"""
        if not self.monitoring_active:
            if not self.camera_active:
                self.start_camera()
            self.monitoring_active = True
            self.present_students_last_seen = {}
            self.monitoring_thread = threading.Thread(target=self.monitor_faces)
            self.monitoring_thread.daemon = True
            self.monitoring_thread.start()
            # Update UI
            self.status_label.configure(text="🟢 Monitoring active",
                                      foreground=DarkTheme.SUCCESS)
            self.start_button.pack_forget()
            self.stop_button.pack(side='left', padx=5)
            messagebox.showinfo("Monitoring", "Face detection monitoring started")
            # Immediately show the current camera frame in the monitoring tab if available
            if self.current_frame is not None:
                frame_rgb = cv2.cvtColor(self.current_frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame_rgb)
                img = img.resize((320, 240), Image.Resampling.LANCZOS)
                img_tk = ImageTk.PhotoImage(img)
                self.monitor_label.configure(image=img_tk)
                self.monitor_label.image = img_tk
            # Start periodic monitoring update
            self.monitor_periodic_job = self.root.after(30000, self.periodic_monitor_update)
    
    def stop_monitoring(self):
        """Stop monitoring without blocking the UI"""
        if self.monitoring_active:
            self.monitoring_active = False
            # Cancel periodic update if running
            if hasattr(self, 'monitor_periodic_job') and self.monitor_periodic_job:
                self.root.after_cancel(self.monitor_periodic_job)
                self.monitor_periodic_job = None
            # Schedule camera stop in a separate thread
            stop_thread = threading.Thread(target=self._stop_monitoring_thread)
            stop_thread.daemon = True
            stop_thread.start()
            # Update UI immediately
            self.status_label.configure(text="⚫ Monitoring inactive",
                                      foreground=DarkTheme.FG)
            self.current_detections.configure(text="No faces detected")
            self.stop_button.pack_forget()
            self.start_button.pack(side='left', padx=5)
            # Clear the monitor display
            self.monitor_label.configure(image='')
            self.monitor_label.image = None
            # Save the Excel file on stop
            self.save_attendance_data()
            # Show completion message
            self.root.after(500, lambda: messagebox.showinfo("Monitoring", "Monitoring stopped"))
    
    def periodic_monitor_update(self):
        """Periodic update for monitoring tab (every 30 seconds)."""
        if self.monitoring_active:
            now = datetime.now()
            # Load current attendance data
            try:
                df = pd.read_excel(self.attendance_file)
            except Exception as e:
                print(f"Error reading attendance file: {e}")
                return
            updated = False
            # Update present students
            to_remove = []
            for sid, last_seen in self.present_students_last_seen.items():
                if sid in df['student_id'].values:
                    idx = df['student_id'] == sid
                    check_in = pd.to_datetime(df.loc[idx, 'check_in_time'].iloc[0])
                    # If not seen for 30 minutes, mark as LEFT_EARLY and schedule for removal
                    if (now - last_seen).total_seconds() > 1800:
                        if df.loc[idx, 'status'].iloc[0] != 'LEFT_EARLY':
                            df.loc[idx, 'status'] = 'LEFT_EARLY'
                            updated = True
                        to_remove.append(sid)
                    else:
                        # Update last_seen_time and total_time_present
                        df.loc[idx, 'last_seen_time'] = last_seen
                        df.loc[idx, 'total_time_present'] = str(last_seen - check_in)
                        df.loc[idx, 'status'] = self.calculate_attendance_status(check_in, last_seen)
                        updated = True
            # Remove students marked as LEFT_EARLY from present_students_last_seen
            for sid in to_remove:
                del self.present_students_last_seen[sid]
            if updated:
                df.to_excel(self.attendance_file, index=False)
            self.refresh_report()
            self.last_update_label.configure(text=f"Last update: {now.strftime('%H:%M:%S')}")
            # Schedule next update
            self.monitor_periodic_job = self.root.after(30000, self.periodic_monitor_update)
    
    def _stop_monitoring_thread(self):
        """Handle monitoring cleanup in a separate thread"""
        try:
            # Wait for monitoring thread with timeout
            if self.monitoring_thread and self.monitoring_thread.is_alive():
                self.monitoring_thread.join(timeout=0.5)
            
            # Stop the camera
            self.stop_camera()
            
        except Exception as e:
            print(f"Error stopping monitoring: {e}")
    
    def save_attendance_data(self):
        """Save current attendance data to Excel file"""
        try:
            if hasattr(self, 'attendance_df'):
                self.attendance_df.to_excel(self.attendance_file, index=False)
        except Exception as e:
            print(f"Error saving attendance data: {str(e)}")
    
    def reset_logs(self):
        """Reset attendance logs"""
        if messagebox.askyesno("Reset Logs", 
                             "Are you sure you want to reset all attendance logs? This cannot be undone."):
            try:
                # Create new empty DataFrame with same columns
                new_df = pd.DataFrame(columns=[
                    'student_id', 'name', 'check_in_time', 'last_seen_time',
                    'status', 'total_time_present'
                ])
                new_df.to_excel(self.attendance_file, index=False)
                
                # Refresh the display
                self.refresh_report()
                messagebox.showinfo("Success", "Attendance logs have been reset")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to reset logs: {str(e)}")
    
    def update_attendance(self, student_id, name):
        """Update attendance record with new timestamp and status"""
        try:
            now = datetime.now()
            # Only update every UPDATE_INTERVAL seconds
            if (hasattr(self, 'last_update_time') and self.last_update_time is not None and 
                (now - self.last_update_time).total_seconds() < self.UPDATE_INTERVAL):
                return
            # Load or use in-memory attendance data
            if not hasattr(self, 'attendance_df'):
                self.attendance_df = pd.read_excel(self.attendance_file)
            # Get check-in and last seen
            if student_id in self.attendance_df['student_id'].values:
                idx = self.attendance_df['student_id'] == student_id
                check_in = pd.to_datetime(self.attendance_df.loc[idx, 'check_in_time'].iloc[0])
            else:
                check_in = now
            last_seen = now
            # Calculate status
            status = self.calculate_attendance_status(check_in, last_seen)
            # Calculate total time present
            if student_id in self.attendance_df['student_id'].values:
                total_time = str(last_seen - check_in)
            else:
                total_time = "0:00:00"
            new_row = {
                'student_id': student_id,
                'name': name,
                'check_in_time': check_in,
                'last_seen_time': last_seen,
                'status': status,
                'total_time_present': total_time
            }
            if student_id in self.attendance_df['student_id'].values:
                # Only update last_seen_time, status, and total_time_present
                self.attendance_df.loc[idx, 'last_seen_time'] = last_seen
                self.attendance_df.loc[idx, 'status'] = status
                self.attendance_df.loc[idx, 'total_time_present'] = total_time
                # Do not update check_in_time or name
            else:
                self.attendance_df = pd.concat([self.attendance_df, pd.DataFrame([new_row])], 
                                           ignore_index=True)
            # Only update the label and report in the GUI
            self.last_update_time = now
            self.last_update_label.configure(
                text=f"Last update: {now.strftime('%H:%M:%S')}"
            )
            self.refresh_report()
        except Exception as e:
            print(f"Error updating attendance: {str(e)}")
    
    def calculate_attendance_status(self, check_in_time, last_seen_time):
        """Calculate attendance status based on event start/end and thresholds"""
        # Parse event start/end from GUI
        try:
            event_date = pd.to_datetime(self.date_var.get())
            start_hour, start_minute = map(int, self.event_start_time.get().split(":"))
            end_hour, end_minute = map(int, self.event_end_time.get().split(":"))
            event_start = event_date.replace(hour=start_hour, minute=start_minute, second=0, microsecond=0)
            event_end = event_date.replace(hour=end_hour, minute=end_minute, second=0, microsecond=0)
        except Exception:
            # Fallback to 9:00-17:00
            event_start = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
            event_end = datetime.now().replace(hour=17, minute=0, second=0, microsecond=0)
        # Late threshold (minutes)
        late_threshold = self.STATUS_THRESHOLDS['LATE']
        # If never checked in
        if pd.isnull(check_in_time):
            return 'ABSENT'
        # If checked in after late threshold
        if (check_in_time - event_start).total_seconds() / 60 > late_threshold:
            status = 'LATE'
        else:
            status = 'PRESENT'
        # If left before end
        if pd.notnull(last_seen_time) and last_seen_time < event_end:
            # Only mark as left early if last seen is at least 10 minutes before end
            if (event_end - last_seen_time).total_seconds() > 600:
                status = 'LEFT_EARLY'
        return status
    
    def monitor_faces(self):
        """Real-time face detection and recognition with performance optimization"""
        frame_count = 0
        while self.monitoring_active:
            # Wait for a new frame
            if not self.frame_ready.wait(timeout=1.0):
                continue
            self.frame_ready.clear()
            with self.camera_lock:
                if self.current_frame is None:
                    continue
                frame = self.current_frame.copy()
            # Process every 3rd frame for face detection
            frame_count += 1
            if frame_count % 3 != 0:
                continue
            # Convert to RGB for face_recognition
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # Reduce frame size for faster processing
            small_frame = cv2.resize(rgb_frame, (0, 0), fx=0.5, fy=0.5)
            # Find faces in frame
            face_locations = face_recognition.face_locations(small_frame, model="hog")
            face_encodings = face_recognition.face_encodings(small_frame, face_locations)
            detected_people = []
            detected_ids = set()
            now = datetime.now()
            # Scale back face locations to original size
            face_locations = [(top * 2, right * 2, bottom * 2, left * 2) 
                            for top, right, bottom, left in face_locations]
            # Process detected faces
            for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                matches = []
                name = "Unknown"
                student_id = None
                confidence = 0
                # Check against known faces
                for sid, known_encoding in self.known_face_encodings.items():
                    # Calculate face distance (lower is better)
                    face_distance = face_recognition.face_distance([known_encoding], face_encoding)[0]
                    # Convert distance to confidence score (0-100%)
                    confidence_score = (1 - face_distance) * 100
                    if confidence_score > 30: # 30%confidence threshold
                        if confidence_score > confidence:  # Keep best match
                            confidence = confidence_score
                            student_id = sid
                            name = self.known_face_names[sid]
                if student_id:
                    badge_text, badge_color = self.get_status_badge('PRESENT')
                    detected_people.append(f"{name} {badge_text}")
                    detected_ids.add(student_id)
                    # Update last seen time for this student
                    self.present_students_last_seen[student_id] = now
                    # Update attendance
                    self.update_attendance(student_id, name)
                # Draw rectangle with color based on confidence
                if confidence > 80:
                    color = (0, 255, 0)  # Green for high confidence
                elif confidence > 60:
                    color = (0, 255, 255)  # Yellow for medium confidence
                else:
                    color = (0, 0, 255)  # Red for unknown/low confidence
                # Draw rectangle
                cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                # Draw name and confidence
                label = f"{name} ({confidence:.1f}%)" if confidence > 0 else name
                y = bottom - 15 if top > 20 else top + 15
                cv2.rectangle(frame, (left, y-20), (right, y), color, cv2.FILLED)
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(frame, label, (left + 6, y-6), font, 0.6, (0, 0, 0), 1)
            # Track currently present students
            self.currently_present_students = detected_ids
            # Update UI with results
            if detected_people:
                self.current_detections.configure(
                    text=f"Detected: {', '.join(detected_people)}"
                )
            else:
                self.current_detections.configure(text="No faces detected")
            # Display processed frame
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            img = img.resize((320, 240), Image.Resampling.LANCZOS)
            img_tk = ImageTk.PhotoImage(img)
            if self.monitoring_active:  # Check if still active before updating
                self.monitor_label.configure(image=img_tk)
                self.monitor_label.image = img_tk
            time.sleep(0.01)  # Small delay to prevent CPU overuse
    
    def setup_reports_tab(self, parent):
        # Main container with card style
        card = ttk.Frame(parent, style='Card.TFrame')
        card.pack(fill='both', expand=True, padx=40, pady=40)
        
        # Header section
        header_frame = ttk.Frame(card, style='Card.TFrame')
        header_frame.pack(fill='x', pady=(0, 20))
        
        # Title row
        title_row = ttk.Frame(header_frame, style='Card.TFrame')
        title_row.pack(fill='x', pady=(0, 20))
        
        ttk.Label(title_row, 
                 text="Attendance Reports", 
                 style='Card.TLabel',
                 font=(DarkTheme.FONT, 24, 'bold')).pack(side='left')
        
        # Filters row
        filters_frame = ttk.Frame(header_frame, style='Card.TFrame')
        filters_frame.pack(fill='x', pady=(0, 20))
        
        # Date filter
        date_frame = ttk.Frame(filters_frame, style='Card.TFrame')
        date_frame.pack(side='left', padx=(0, 20))
        ttk.Label(date_frame, text="Date:", style='Card.TLabel').pack(side='left', padx=(0, 10))
        self.date_var = tk.StringVar(value=datetime.now().strftime('%Y-%m-%d'))
        date_entry = customtkinter.CTkEntry(
            date_frame,
            textvariable=self.date_var,
            width=120,
            height=32,
            fg_color=DarkTheme.BG,
            bg_color=DarkTheme.CARD_BG,
            text_color=DarkTheme.FG,
            border_color=DarkTheme.BUTTON_BG
        )
        date_entry.pack(side='left')
        
        # Calendar button
        calendar_btn = customtkinter.CTkButton(
            date_frame,
            text="📅",
            command=lambda: CustomCalendar(self.root, self.date_var),
            width=32,
            height=32,
            fg_color=DarkTheme.BUTTON_BG,
            hover_color=DarkTheme.BUTTON_HOVER,
            bg_color=DarkTheme.CARD_BG,
            text_color=DarkTheme.FG,
            font=customtkinter.CTkFont(family=DarkTheme.FONT, size=14)
        )
        calendar_btn.pack(side='left', padx=5)
        
        # Add trace to date_var to auto-refresh report
        self.date_var.trace_add('write', lambda *args: self.refresh_report())
        
        # Time range filter
        time_frame = ttk.Frame(filters_frame, style='Card.TFrame')
        time_frame.pack(side='left', padx=20)
        ttk.Label(time_frame, text="Time Range:", style='Card.TLabel').pack(side='left', padx=(0, 10))
        
        self.event_start_time = tk.StringVar(value="09:00")
        start_entry = customtkinter.CTkEntry(
            time_frame,
            textvariable=self.event_start_time,
            width=70,
            height=32,
            fg_color=DarkTheme.BG,
            bg_color=DarkTheme.CARD_BG,
            text_color=DarkTheme.FG,
            border_color=DarkTheme.BUTTON_BG
        )
        start_entry.pack(side='left', padx=5)
        
        ttk.Label(time_frame, text="to", style='Card.TLabel').pack(side='left', padx=5)
        
        self.event_end_time = tk.StringVar(value="17:00")
        end_entry = customtkinter.CTkEntry(
            time_frame,
            textvariable=self.event_end_time,
            width=70,
            height=32,
            fg_color=DarkTheme.BG,
            bg_color=DarkTheme.CARD_BG,
            text_color=DarkTheme.FG,
            border_color=DarkTheme.BUTTON_BG
        )
        end_entry.pack(side='left', padx=5)
        
        # Status filter
        status_frame = ttk.Frame(filters_frame, style='Card.TFrame')
        status_frame.pack(side='left', padx=20)
        ttk.Label(status_frame, text="Status:", style='Card.TLabel').pack(side='left', padx=(0, 10))
        
        self.status_var = tk.StringVar(value="ALL")
        status_menu = customtkinter.CTkOptionMenu(
            status_frame,
            values=["ALL", "PRESENT", "LATE", "LEFT_EARLY", "ABSENT"],
            variable=self.status_var,
            width=120,
            height=32,
            fg_color=DarkTheme.BUTTON_BG,
            bg_color=DarkTheme.CARD_BG,
            button_color=DarkTheme.BUTTON_HOVER,
            button_hover_color=DarkTheme.BUTTON_HOVER,
            dropdown_fg_color=DarkTheme.CARD_BG,
            text_color=DarkTheme.FG,
            font=customtkinter.CTkFont(family=DarkTheme.FONT, size=11)
        )
        status_menu.pack(side='left')
        # Add trace for status_var to auto-refresh report
        self.status_var.trace_add('write', lambda *args: self.refresh_report())
        
        # Refresh button
        refresh_btn = customtkinter.CTkButton(
            filters_frame,
            text="🔄 Refresh",
            command=self.refresh_report,
            width=100,
            height=32,
            fg_color=DarkTheme.ACCENT,
            bg_color=DarkTheme.CARD_BG,
            hover_color=DarkTheme.ACCENT_HOVER,
            text_color=DarkTheme.FG,
            font=customtkinter.CTkFont(family=DarkTheme.FONT, size=11, weight="bold")
        )
        refresh_btn.pack(side='right', padx=20)
        
        # Stats cards
        stats_frame = ttk.Frame(card, style='Card.TFrame')
        stats_frame.pack(fill='x', pady=(0, 20))
        
        # Create modern stat cards
        self.stats_labels = {}
        stats_data = [
            ('PRESENT', '🟢', DarkTheme.SUCCESS),
            ('LATE', '🟡', DarkTheme.WARNING),
            ('LEFT_EARLY', '🔴', DarkTheme.ERROR),
            ('ABSENT', '⚫', DarkTheme.BUTTON_BG)
        ]
        
        for status, icon, color in stats_data:
            stat_card = ttk.Frame(stats_frame, style='Card.TFrame')
            stat_card.pack(side='left', padx=10, fill='x', expand=True)
            
            # Status label with icon
            ttk.Label(stat_card, 
                     text=f"{icon} {status}", 
                     style='Card.TLabel',
                     foreground=color,
                     font=(DarkTheme.FONT, 12)).pack(anchor='w', padx=10, pady=(5, 0))
            
            # Count label
            count_label = ttk.Label(stat_card, 
                                  text="0", 
                                  style='Card.TLabel',
                                  foreground=color,
                                  font=(DarkTheme.FONT, 24, 'bold'))
            count_label.pack(anchor='w', padx=10, pady=(0, 5))
            self.stats_labels[status] = count_label
        
        # Table frame with modern styling
        table_frame = ttk.Frame(card, style='Card.TFrame')
        table_frame.pack(fill='both', expand=True)
        
        # Create modern treeview
        self.tree = ttk.Treeview(table_frame, 
                                style='Dark.Treeview',
                                columns=('ID', 'Name', 'Check-in', 'Last Seen', 'Status', 'Time Present'),
                                show='headings',
                                height=15)
        
        # Configure modern column headings
        columns = [
            ('ID', 'Student ID', 100),
            ('Name', 'Name', 200),
            ('Check-in', 'Check-in Time', 150),
            ('Last Seen', 'Last Seen', 150),
            ('Status', 'Status', 120),
            ('Time Present', 'Time Present', 120)
        ]
        
        for col, heading, width in columns:
            self.tree.heading(col, text=heading)
            self.tree.column(col, width=width, anchor='center', stretch=True)
        
        # Add modern scrollbar
        scrollbar = ttk.Scrollbar(table_frame, 
                                orient='vertical', 
                                command=self.tree.yview,
                                style='Dark.Vertical.TScrollbar')
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack table and scrollbar with proper spacing
        self.tree.pack(side='left', fill='both', expand=True, padx=(10, 0), pady=10)
        scrollbar.pack(side='right', fill='y', pady=10)
        
        # Initial load
        self.refresh_report()
    
    def setup_admin_tab(self, parent):
        # Make the Admin tab scrollable
        canvas = tk.Canvas(parent, borderwidth=0, background=DarkTheme.BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scroll_frame = ttk.Frame(canvas, style='Dark.TFrame')
        scroll_frame_id = canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        def on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        scroll_frame.bind("<Configure>", on_frame_configure)
        
        # Place all admin content in scroll_frame instead of parent
        card = ttk.Frame(scroll_frame, style='Card.TFrame')
        card.pack(fill='both', expand=True, padx=40, pady=40)
        header = ttk.Label(card, text="Admin & Settings", style='Card.TLabel', font=(DarkTheme.FONT, 20, 'bold'))
        header.pack(anchor='w', pady=(0, 20))
        desc = ttk.Label(card, text="Manage students, correct attendance, schedule events, and configure user roles here.", style='Card.TLabel')
        desc.pack(anchor='w', pady=(0, 10))
        
        # Export/Import controls
        btn_frame = ttk.Frame(card, style='Card.TFrame')
        btn_frame.pack(anchor='w', pady=(10, 20))
        
        export_csv_btn = customtkinter.CTkButton(
            btn_frame,
            text="Export to CSV",
            command=self.export_to_csv,
            fg_color=DarkTheme.ACCENT,
            hover_color=DarkTheme.ACCENT_HOVER,
            bg_color=DarkTheme.CARD_BG,
            width=150,
            **self.button_props
        )
        export_csv_btn.pack(side='left', padx=5)
        
        export_pdf_btn = customtkinter.CTkButton(
            btn_frame,
            text="Export to PDF",
            command=self.export_to_pdf,
            fg_color=DarkTheme.ACCENT,
            hover_color=DarkTheme.ACCENT_HOVER,
            bg_color=DarkTheme.CARD_BG,
            width=150,
            **self.button_props
        )
        export_pdf_btn.pack(side='left', padx=5)
        
        import_csv_btn = customtkinter.CTkButton(
            btn_frame,
            text="Import from CSV",
            command=self.import_from_csv,
            fg_color=DarkTheme.SUCCESS,
            hover_color=DarkTheme.SUCCESS_HOVER,
            bg_color=DarkTheme.CARD_BG,
            width=170,
            **self.button_props
        )
        import_csv_btn.pack(side='left', padx=5)
        
        # Student Management section
        student_card = ttk.Frame(card, style='Card.TFrame')
        student_card.pack(fill='x', pady=(10, 20))
        student_header = ttk.Label(student_card, text="Student Management", style='Card.TLabel', font=(DarkTheme.FONT, 16, 'bold'))
        student_header.pack(anchor='w', pady=(0, 10))
        
        # Student table
        self.student_tree = ttk.Treeview(student_card, columns=('ID', 'Name'), show='headings', height=6, style='Dark.Treeview')
        self.student_tree.heading('ID', text='Student ID')
        self.student_tree.heading('Name', text='Name')
        self.student_tree.column('ID', width=120, anchor='center')
        self.student_tree.column('Name', width=200, anchor='center')
        self.student_tree.pack(side='left', padx=(0, 10), pady=5)
        
        # Student action buttons
        student_btns = ttk.Frame(student_card, style='Card.TFrame')
        student_btns.pack(side='left', padx=10, pady=5)
        
        edit_btn = customtkinter.CTkButton(
            student_btns,
            text="Edit",
            command=self.edit_student,
            fg_color=DarkTheme.BUTTON_BG,
            hover_color=DarkTheme.BUTTON_HOVER,
            bg_color=DarkTheme.CARD_BG,
            width=100,
            **self.button_props
        )
        edit_btn.pack(pady=2)
        
        delete_btn = customtkinter.CTkButton(
            student_btns,
            text="Delete",
            command=self.delete_student,
            fg_color=DarkTheme.ERROR,
            hover_color=DarkTheme.ERROR_HOVER,
            bg_color=DarkTheme.CARD_BG,
            width=100,
            **self.button_props
        )
        delete_btn.pack(pady=2)
        
        view_face_btn = customtkinter.CTkButton(
            student_btns,
            text="View Face",
            command=self.view_face_image,
            fg_color=DarkTheme.ACCENT,
            hover_color=DarkTheme.ACCENT_HOVER,
            bg_color=DarkTheme.CARD_BG,
            width=100,
            **self.button_props
        )
        view_face_btn.pack(pady=2)
        
        # Load students into the table
        self.load_students_to_tree()
        
        # User Management section
        user_card = ttk.Frame(card, style='Card.TFrame')
        user_card.pack(fill='x', pady=(10, 20))
        user_header = ttk.Label(user_card, text="User Management", style='Card.TLabel', font=(DarkTheme.FONT, 16, 'bold'))
        user_header.pack(anchor='w', pady=(0, 10))
        
        self.user_tree = ttk.Treeview(user_card, columns=('Username', 'Role'), show='headings', height=5, style='Dark.Treeview')
        self.user_tree.heading('Username', text='Username')
        self.user_tree.heading('Role', text='Role')
        self.user_tree.column('Username', width=140, anchor='center')
        self.user_tree.column('Role', width=80, anchor='center')
        self.user_tree.pack(side='left', padx=(0, 10), pady=5)
        
        user_btns = ttk.Frame(user_card, style='Card.TFrame')
        user_btns.pack(side='left', padx=10, pady=5, anchor='n')
        
        add_user_btn = customtkinter.CTkButton(
            user_btns,
            text="Add",
            command=self.add_user,
            fg_color=DarkTheme.SUCCESS,
            hover_color=DarkTheme.SUCCESS_HOVER,
            bg_color=DarkTheme.CARD_BG,
            width=100,
            **self.button_props
        )
        add_user_btn.pack(pady=(0, 6), anchor='w')
        
        edit_user_btn = customtkinter.CTkButton(
            user_btns,
            text="Edit",
            command=self.edit_user,
            fg_color=DarkTheme.BUTTON_BG,
            hover_color=DarkTheme.BUTTON_HOVER,
            bg_color=DarkTheme.CARD_BG,
            width=100,
            **self.button_props
        )
        edit_user_btn.pack(pady=(0, 6), anchor='w')
        
        delete_user_btn = customtkinter.CTkButton(
            user_btns,
            text="Delete",
            command=self.delete_user,
            fg_color=DarkTheme.ERROR,
            hover_color=DarkTheme.ERROR_HOVER,
            bg_color=DarkTheme.CARD_BG,
            width=100,
            **self.button_props
        )
        delete_user_btn.pack(pady=(0, 6), anchor='w')
        
        self.load_users_to_tree()
    
    def stop_checkin_camera(self):
        """Stop camera in check-in tab without blocking"""
        if self.camera_active:
            self.camera_active = False
            
            # Schedule camera stop in a separate thread
            stop_thread = threading.Thread(target=self._stop_checkin_camera_thread)
            stop_thread.daemon = True
            stop_thread.start()
            
            # Clear the camera display
            self.camera_label.configure(image='')
            self.camera_label.image = None
    
    def _stop_checkin_camera_thread(self):
        """Handle camera cleanup in a separate thread"""
        try:
            # Wait for camera thread with timeout
            if self.camera_thread and self.camera_thread.is_alive():
                self.camera_thread.join(timeout=0.5)
            
            # Stop the camera
            with self.camera_lock:
                if self.camera is not None:
                    self.camera.release()
                    self.camera = None
            
        except Exception as e:
            print(f"Error stopping check-in camera: {e}")
            # Schedule error message in main thread
            self.root.after(0, lambda: messagebox.showerror("Error", 
                                                          "Failed to stop camera properly"))
    
    def register_student(self):
        threading.Thread(target=self.capture_face_thread, daemon=True).start()
        self.show_notification("Registering student...", level='info')

    def capture_face_thread(self):
        student_id = self.reg_id_var.get()
        name = self.reg_name_var.get()
        if not student_id or not name:
            self.root.after(0, lambda: self.show_notification("Please enter both Student ID and Name", level='error'))
            return

        with self.camera_lock:
            if self.camera is None or not self.camera.isOpened():
                self.root.after(0, lambda: self.show_notification("Camera is not properly initialized", level='error'))
                return
            ret, frame = self.camera.read()
            if not ret:
                self.root.after(0, lambda: self.show_notification("Failed to capture image from camera", level='error'))
                return

        # Detect face
        face_locations = face_recognition.face_locations(frame)
        if not face_locations:
            self.root.after(0, lambda: self.show_notification("No face detected", level='error'))
            return

        # Save face image and encoding
        face_path = os.path.join('faces', f"{student_id}.jpg")
        cv2.imwrite(face_path, frame)
        face_encoding = face_recognition.face_encodings(frame, face_locations)[0]
        encoding_path = os.path.join('faces', f"{student_id}.npy")
        np.save(encoding_path, face_encoding)

        # Update students.csv
        try:
            if os.path.exists('students.csv'):
                df = pd.read_csv('students.csv')
            else:
                df = pd.DataFrame(columns=['student_id', 'name'])
            new_row = pd.DataFrame({'student_id': [student_id], 'name': [name]})
            df = pd.concat([df, new_row], ignore_index=True)
            df.to_csv('students.csv', index=False)
            self.root.after(0, lambda: [
                self.load_known_faces(),  # Reload face encodings for immediate recognition
                self.show_notification("Student registered successfully! Face recognition updated.", level='success'),
                self.reg_id_var.set(""),
                self.reg_name_var.set(""),
                self.load_students_to_tree() if hasattr(self, 'student_tree') else None  # Refresh admin table if exists
            ])
        except Exception as e:
            self.root.after(0, lambda: self.show_notification(f"Failed to update students database: {str(e)}", level='error'))
    
    def mock_rfid_scan(self):
        try:
            if os.path.exists('students.csv'):
                df = pd.read_csv('students.csv')
                if not df.empty:
                    random_student = df.sample(n=1).iloc[0]
                    self.student_id_var.set(random_student['student_id'])
                else:
                    self.show_notification("No students registered yet", level='warning')
            else:
                self.show_notification("No students database found", level='warning')
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read students.csv: {str(e)}")
    
    def process_check_in(self):
        """Process check-in with proper camera handling in a background thread"""
        threading.Thread(target=self.process_check_in_thread, daemon=True).start()

    def process_check_in_thread(self):
        student_id = self.student_id_var.get()
        if not student_id:
            self.root.after(0, lambda: self.show_notification("Please enter a student ID", level='error'))
            return
        try:
            students_df = pd.read_csv('students.csv') if os.path.exists('students.csv') else pd.DataFrame(columns=['student_id', 'name'])
            student = students_df[students_df['student_id'] == int(student_id)]
            if student.empty:
                self.root.after(0, lambda: self.show_notification("Student ID not found", level='error'))
                return
            if not self.camera_active:
                self.root.after(0, lambda: self.show_notification("Please start the camera first", level='error'))
                return
            with self.camera_lock:
                if self.camera is None or not self.camera.isOpened():
                    self.root.after(0, lambda: self.show_notification("Camera is not properly initialized", level='error'))
                    return
                ret, frame = self.camera.read()
                if not ret:
                    self.root.after(0, lambda: self.show_notification("Could not capture image from camera", level='error'))
                    return
            encoding_path = os.path.join('faces', f"{student_id}.npy")
            if not os.path.exists(encoding_path):
                self.root.after(0, lambda: self.show_notification("No face data found for this student. Please register first.", level='error'))
                return
            face_locations = face_recognition.face_locations(frame)
            if not face_locations:
                self.root.after(0, lambda: self.show_notification("No face detected in camera", level='error'))
                return
            current_encoding = face_recognition.face_encodings(frame, face_locations)[0]
            registered_encoding = np.load(encoding_path)
            matches = face_recognition.compare_faces([registered_encoding], current_encoding, tolerance=0.6)
            if not matches[0]:
                self.root.after(0, lambda: self.show_notification("Face does not match registered student", level='error'))
                return
            now = datetime.now()
            attendance_df = pd.read_excel(self.attendance_file) if os.path.exists(self.attendance_file) else pd.DataFrame(columns=['student_id', 'name', 'check_in_time', 'last_seen_time', 'status', 'total_time_present'])
            new_row = {
                'student_id': student_id,
                'name': student.iloc[0]['name'],
                'check_in_time': now,
                'last_seen_time': now
            }
            if student_id in attendance_df['student_id'].values:
                attendance_df.loc[attendance_df['student_id'] == student_id] = new_row
            else:
                attendance_df = pd.concat([attendance_df, pd.DataFrame([new_row])], 
                                       ignore_index=True)
            attendance_df.to_excel(self.attendance_file, index=False)
            self.root.after(0, lambda: [
                self.show_notification("Check-in successful!", level='success'),
                self.refresh_report()
            ])
        except Exception as e:
            self.root.after(0, lambda: self.show_notification(f"Check-in failed: {str(e)}", level='error'))
    
    def get_status_display(self, status):
        """Get the display text and color for a status"""
        icons = {
            'PRESENT': '🟢',
            'LATE': '🟡',
            'LEFT_EARLY': '🔴',
            'ABSENT': '⚫'
        }
        colors = {
            'PRESENT': DarkTheme.SUCCESS,
            'LATE': DarkTheme.WARNING,
            'LEFT_EARLY': DarkTheme.ERROR,
            'ABSENT': DarkTheme.BUTTON_BG
        }
        if not status or pd.isnull(status) or str(status).lower() == 'nan':
            status = 'ABSENT'
        return f"{icons.get(status, '⚫')} {status}", colors.get(status, DarkTheme.BUTTON_BG)

    def refresh_report(self):
        """Refresh the attendance report with filters and statistics"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        try:
            # Use in-memory DataFrame if available and monitoring is active
            if hasattr(self, 'attendance_df') and self.monitoring_active:
                df = self.attendance_df.copy()
            else:
                df = pd.read_excel(self.attendance_file)
            
            # Add missing columns if needed
            required_cols = ['student_id', 'name', 'check_in_time', 'last_seen_time', 'status', 'total_time_present']
            for col in required_cols:
                if col not in df.columns:
                    if col == 'status':
                        df[col] = 'ABSENT'
                    elif col == 'total_time_present':
                        df[col] = '0:00:00'
                    else:
                        df[col] = ''
            
            # Convert timestamps
            df['check_in_time'] = pd.to_datetime(df['check_in_time'], errors='coerce')
            df['last_seen_time'] = pd.to_datetime(df['last_seen_time'], errors='coerce')
            
            # Apply date filter
            selected_date = self.date_var.get()
            if selected_date:
                df = df[df['check_in_time'].dt.strftime('%Y-%m-%d') == selected_date]
            
            # Apply status filter
            selected_status = self.status_var.get()
            if selected_status != "ALL":
                df = df[df['status'] == selected_status]
            
            # Remove duplicates keeping the latest entry for each student
            df = df.sort_values('check_in_time').drop_duplicates('student_id', keep='last')
            
            # Update statistics
            status_counts = {'PRESENT': 0, 'LATE': 0, 'LEFT_EARLY': 0, 'ABSENT': 0}
            for status in df['status'].fillna('ABSENT'):
                if status in status_counts:
                    status_counts[status] += 1
            
            # Update status count labels
            for status, count in status_counts.items():
                self.stats_labels[status].configure(text=str(count))
            
            # Update table with colored status
            for _, row in df.iterrows():
                status = row.get('status', 'ABSENT')
                if pd.isnull(status) or status == '':
                    status = 'ABSENT'
                    
                # Format timestamps
                check_in = row.get('check_in_time', '')
                last_seen = row.get('last_seen_time', '')
                if pd.notnull(check_in):
                    check_in = check_in.strftime('%Y-%m-%d %H:%M:%S')
                if pd.notnull(last_seen):
                    last_seen = last_seen.strftime('%Y-%m-%d %H:%M:%S')
                
                # Format total_time_present to remove days
                total_time = str(row.get('total_time_present', '0:00:00'))
                if 'day' in total_time:
                    # Remove 'X days' prefix
                    total_time = total_time.split(',')[-1].strip()
                
                # Get status display
                status_text, status_color = self.get_status_display(status)
                
                values = (
                    str(row.get('student_id', '')),
                    str(row.get('name', '')),
                    check_in,
                    last_seen,
                    status_text,
                    total_time
                )
                
                # Insert with status-based tag
                item = self.tree.insert('', 'end', values=values, tags=(status,))
            
            # Configure status-based colors
            status_colors = {
                'PRESENT': DarkTheme.SUCCESS,
                'LATE': DarkTheme.WARNING,
                'LEFT_EARLY': DarkTheme.ERROR,
                'ABSENT': DarkTheme.BUTTON_BG
            }
            
            # Apply tag configurations
            for status, color in status_colors.items():
                self.tree.tag_configure(status, foreground=color)
                
        except Exception as e:
            self.show_notification(f"Failed to refresh report: {str(e)}", level='error')
    
    def quit_application(self):
        """Safely quit the application asynchronously"""
        if messagebox.askokcancel("Quit", "Do you want to quit the application?"):
            # Disable the quit button to prevent multiple clicks
            self.root.protocol('WM_DELETE_WINDOW', lambda: None)
            def cleanup_and_quit_async():
                # Stop monitoring if active
                if self.monitoring_active:
                    self.monitoring_active = False
                    # Cancel periodic update if running
                    if hasattr(self, 'monitor_periodic_job') and self.monitor_periodic_job:
                        self.root.after_cancel(self.monitor_periodic_job)
                        self.monitor_periodic_job = None
                    self._stop_monitoring_thread()
                # Stop camera if it's running
                self.stop_camera()
                # Final cleanup
                if hasattr(self, 'attendance_df'):
                    self.attendance_df.to_excel(self.attendance_file, index=False)
                if hasattr(self, 'camera') and self.camera is not None:
                    self.camera.release()
                # Destroy the window in the main thread
                self.root.after(200, self.root.destroy)
            # Run cleanup in a background thread
            threading.Thread(target=cleanup_and_quit_async, daemon=True).start()
    
    def __del__(self):
        """Ensure camera resources are properly released"""
        if hasattr(self, 'monitoring_active') and self.monitoring_active:
            self.stop_monitoring()

    def show_notification(self, message, level='info'):
        # Show a popup in the top right corner
        NotificationPopup(self.root, message, level)

    def get_status_badge(self, status):
        # Always return a valid status string
        if not status or pd.isnull(status) or str(status).lower() == 'nan':
            status = 'PRESENT'
        color = {
            'PRESENT': '#28a745',
            'LATE': '#ffc107',
            'LEFT_EARLY': '#dc3545',
            'ABSENT': '#6c757d',
            '': '#6c757d',
            None: '#6c757d'
        }.get(status, '#6c757d')
        return status, color

    def setup_notification_bar(self):
        self.notification_bar = tk.Label(self.root, text='', bg=DarkTheme.NOTIF_BG, fg=DarkTheme.NOTIF_FG, font=(DarkTheme.FONT, 11), anchor='w', padx=20)
        self.notification_bar.pack(side='bottom', fill='x')

    def load_students_to_tree(self):
        # Load students from students.csv into the student_tree
        try:
            for item in self.student_tree.get_children():
                self.student_tree.delete(item)
            if os.path.exists('students.csv'):
                df = pd.read_csv('students.csv')
                for _, row in df.iterrows():
                    self.student_tree.insert('', 'end', values=(row['student_id'], row['name']))
        except Exception as e:
            self.show_notification(f"Failed to load students: {str(e)}", level='error')

    def edit_student(self):
        # Edit selected student's name/ID
        selected = self.student_tree.selection()
        if not selected:
            self.show_notification("Select a student to edit.", level='warning')
            return
        item = self.student_tree.item(selected[0])
        old_id, old_name = item['values']
        # Modal dialog for editing
        edit_win = tk.Toplevel(self.root)
        edit_win.title("Edit Student")
        edit_win.grab_set()
        tk.Label(edit_win, text="Student ID:").grid(row=0, column=0, padx=10, pady=10)
        id_var = tk.StringVar(value=str(old_id))
        tk.Entry(edit_win, textvariable=id_var).grid(row=0, column=1, padx=10, pady=10)
        tk.Label(edit_win, text="Name:").grid(row=1, column=0, padx=10, pady=10)
        name_var = tk.StringVar(value=old_name)
        tk.Entry(edit_win, textvariable=name_var).grid(row=1, column=1, padx=10, pady=10)
        def save_edit():
            new_id = id_var.get().strip()
            new_name = name_var.get().strip()
            if not new_id or not new_name:
                messagebox.showerror("Error", "Both fields are required.")
                return
            try:
                df = pd.read_csv('students.csv')
                # Check for ID conflict
                if new_id != str(old_id) and new_id in df['student_id'].astype(str).values:
                    messagebox.showerror("Error", "Student ID already exists.")
                    return
                df.loc[df['student_id'] == old_id, 'student_id'] = new_id
                df.loc[df['student_id'] == new_id, 'name'] = new_name
                df.to_csv('students.csv', index=False)
                # Rename face files if ID changed
                if new_id != str(old_id):
                    old_jpg = os.path.join('faces', f"{old_id}.jpg")
                    old_npy = os.path.join('faces', f"{old_id}.npy")
                    new_jpg = os.path.join('faces', f"{new_id}.jpg")
                    new_npy = os.path.join('faces', f"{new_id}.npy")
                    if os.path.exists(old_jpg):
                        os.rename(old_jpg, new_jpg)
                    if os.path.exists(old_npy):
                        os.rename(old_npy, new_npy)
                self.load_known_faces()  # Reload face encodings
                self.load_students_to_tree()
                edit_win.destroy()
                self.show_notification("Student updated.", level='success')
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update student: {str(e)}")
        tk.Button(edit_win, text="Save", command=save_edit).grid(row=2, column=0, columnspan=2, pady=10)

    def delete_student(self):
        # Delete selected student
        selected = self.student_tree.selection()
        if not selected:
            self.show_notification("Select a student to delete.", level='warning')
            return
        item = self.student_tree.item(selected[0])
        student_id, name = item['values']
        if not messagebox.askyesno("Delete Student", f"Delete student {name} (ID: {student_id})? This cannot be undone."):
            return
        try:
            df = pd.read_csv('students.csv')
            df = df[df['student_id'] != student_id]
            df.to_csv('students.csv', index=False)
            # Remove face files
            jpg = os.path.join('faces', f"{student_id}.jpg")
            npy = os.path.join('faces', f"{student_id}.npy")
            if os.path.exists(jpg):
                os.remove(jpg)
            if os.path.exists(npy):
                os.remove(npy)
            self.load_known_faces()  # Reload face encodings
            self.load_students_to_tree()
            self.show_notification("Student deleted.", level='success')
        except Exception as e:
            self.show_notification(f"Failed to delete student: {str(e)}", level='error')

    def view_face_image(self):
        # Show registered face image for selected student
        selected = self.student_tree.selection()
        if not selected:
            self.show_notification("Select a student to view face image.", level='warning')
            return
        item = self.student_tree.item(selected[0])
        student_id, name = item['values']
        img_path = os.path.join('faces', f"{student_id}.jpg")
        if not os.path.exists(img_path):
            self.show_notification("No face image found for this student.", level='warning')
            return
        # Show image in a popup
        top = tk.Toplevel(self.root)
        top.title(f"Face Image: {name}")
        img = Image.open(img_path)
        img = img.resize((160, 160), Image.Resampling.LANCZOS)
        img_tk = ImageTk.PhotoImage(img)
        label = tk.Label(top, image=img_tk)
        label.image = img_tk
        label.pack(padx=10, pady=10)
        close_btn = tk.Button(top, text="Close", command=top.destroy)
        close_btn.pack(pady=(0, 10))

    def export_to_csv(self):
        # Export attendance to CSV
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension='.csv',
                filetypes=[('CSV files', '*.csv')],
                title='Export Attendance to CSV'
            )
            if not file_path:
                return
            if hasattr(self, 'attendance_df'):
                df = self.attendance_df.copy()
            else:
                df = pd.read_excel(self.attendance_file)
            df.to_csv(file_path, index=False)
            self.show_notification(f"Attendance exported to {file_path}", level='success')
        except Exception as e:
            self.show_notification(f"Export to CSV failed: {str(e)}", level='error')

    def export_to_pdf(self):
        # Export attendance to PDF (simple table)
        try:
            try:
                from reportlab.lib.pagesizes import letter
                from reportlab.pdfgen import canvas
                from reportlab.platypus import Table, TableStyle
                from reportlab.lib import colors
            except ImportError:
                self.show_notification("reportlab is not installed. Please install it to export PDF.", level='error')
                return
            file_path = filedialog.asksaveasfilename(
                defaultextension='.pdf',
                filetypes=[('PDF files', '*.pdf')],
                title='Export Attendance to PDF'
            )
            if not file_path:
                return
            if hasattr(self, 'attendance_df'):
                df = self.attendance_df.copy()
            else:
                df = pd.read_excel(self.attendance_file)
            data = [list(df.columns)] + df.astype(str).values.tolist()
            c = canvas.Canvas(file_path, pagesize=letter)
            width, height = letter
            table = Table(data, repeatRows=1)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            table.wrapOn(c, width, height)
            table_height = 20 * (len(data))
            table.drawOn(c, 30, height - 40 - table_height)
            c.save()
            self.show_notification(f"Attendance exported to {file_path}", level='success')
        except Exception as e:
            self.show_notification(f"Export to PDF failed: {str(e)}", level='error')

    def import_from_csv(self):
        # Import attendance from CSV (replace current log)
        try:
            file_path = filedialog.askopenfilename(
                filetypes=[('CSV files', '*.csv')],
                title='Import Attendance from CSV'
            )
            if not file_path:
                return
            if not messagebox.askyesno("Import Attendance", "This will replace the current attendance log. Continue?"):
                return
            df = pd.read_csv(file_path)
            # Validate columns
            required_cols = ['student_id', 'name', 'check_in_time', 'last_seen_time', 'status', 'total_time_present']
            for col in required_cols:
                if col not in df.columns:
                    self.show_notification(f"Missing required column: {col}", level='error')
                    return
            df.to_excel(self.attendance_file, index=False)
            self.attendance_df = df.copy()
            self.refresh_report()
            self.show_notification(f"Attendance imported from {file_path}", level='success')
        except Exception as e:
            self.show_notification(f"Import from CSV failed: {str(e)}", level='error')

    def load_users_to_tree(self):
        try:
            for item in self.user_tree.get_children():
                self.user_tree.delete(item)
            if os.path.exists('users.csv'):
                df = pd.read_csv('users.csv')
                for _, row in df.iterrows():
                    self.user_tree.insert('', 'end', values=(row['username'], row['role']))
        except Exception as e:
            self.show_notification(f"Failed to load users: {str(e)}", level='error')

    def add_user(self):
        # Dialog to add a new user
        add_win = tk.Toplevel(self.root)
        add_win.title("Add User")
        add_win.grab_set()
        tk.Label(add_win, text="Username:").grid(row=0, column=0, padx=10, pady=5)
        user_var = tk.StringVar()
        tk.Entry(add_win, textvariable=user_var).grid(row=0, column=1, padx=10, pady=5)
        tk.Label(add_win, text="Password:").grid(row=1, column=0, padx=10, pady=5)
        pass_var = tk.StringVar()
        tk.Entry(add_win, textvariable=pass_var, show='*').grid(row=1, column=1, padx=10, pady=5)
        tk.Label(add_win, text="Role:").grid(row=2, column=0, padx=10, pady=5)
        role_var = tk.StringVar(value="teacher")
        role_menu = ttk.Combobox(add_win, textvariable=role_var, values=["admin", "teacher", "guest"])
        role_menu.grid(row=2, column=1, padx=10, pady=5)
        def save_add():
            username = user_var.get().strip()
            password = pass_var.get().strip()
            role = role_var.get().strip()
            if not username or not password or not role:
                messagebox.showerror("Error", "All fields are required.")
                return
            if os.path.exists('users.csv'):
                df = pd.read_csv('users.csv')
                if username in df['username'].values:
                    messagebox.showerror("Error", "Username already exists.")
                    return
            else:
                df = pd.DataFrame(columns=['username', 'password', 'role'])
            hashed = hashlib.sha256(password.encode()).hexdigest()
            df = pd.concat([df, pd.DataFrame([{'username': username, 'password': hashed, 'role': role}])], ignore_index=True)
            df.to_csv('users.csv', index=False)
            self.load_users_to_tree()
            add_win.destroy()
            self.show_notification("User added.", level='success')
        tk.Button(add_win, text="Save", command=save_add).grid(row=3, column=0, columnspan=2, pady=10)

    def edit_user(self):
        # Dialog to edit selected user's password and role
        selected = self.user_tree.selection()
        if not selected:
            self.show_notification("Select a user to edit.", level='warning')
            return
        item = self.user_tree.item(selected[0])
        username, old_role = item['values']
        if username == self.current_user['username']:
            self.show_notification("You cannot edit your own user while logged in.", level='warning')
            return
        edit_win = tk.Toplevel(self.root)
        edit_win.title("Edit User")
        edit_win.grab_set()
        tk.Label(edit_win, text="Username:").grid(row=0, column=0, padx=10, pady=5)
        tk.Label(edit_win, text=username).grid(row=0, column=1, padx=10, pady=5)
        tk.Label(edit_win, text="New Password (leave blank to keep current):").grid(row=1, column=0, padx=10, pady=5)
        pass_var = tk.StringVar()
        tk.Entry(edit_win, textvariable=pass_var, show='*').grid(row=1, column=1, padx=10, pady=5)
        tk.Label(edit_win, text="Role:").grid(row=2, column=0, padx=10, pady=5)
        role_var = tk.StringVar(value=old_role)
        role_menu = ttk.Combobox(edit_win, textvariable=role_var, values=["admin", "teacher", "guest"])
        role_menu.grid(row=2, column=1, padx=10, pady=5)
        def save_edit():
            new_password = pass_var.get().strip()
            new_role = role_var.get().strip()
            df = pd.read_csv('users.csv')
            idx = df['username'] == username
            if new_password:
                df.loc[idx, 'password'] = hashlib.sha256(new_password.encode()).hexdigest()
            df.loc[idx, 'role'] = new_role
            df.to_csv('users.csv', index=False)
            self.load_users_to_tree()
            edit_win.destroy()
            self.show_notification("User updated.", level='success')
        tk.Button(edit_win, text="Save", command=save_edit).grid(row=3, column=0, columnspan=2, pady=10)

    def delete_user(self):
        # Delete selected user
        selected = self.user_tree.selection()
        if not selected:
            self.show_notification("Select a user to delete.", level='warning')
            return
        item = self.user_tree.item(selected[0])
        username, role = item['values']
        if username == self.current_user['username']:
            self.show_notification("You cannot delete your own user while logged in.", level='warning')
            return
        df = pd.read_csv('users.csv')
        if role == 'admin' and (df['role'] == 'admin').sum() <= 1:
            self.show_notification("Cannot delete the last admin user.", level='warning')
            return
        if not messagebox.askyesno("Delete User", f"Delete user {username}? This cannot be undone."):
            return
        df = df[df['username'] != username]
        df.to_csv('users.csv', index=False)
        self.load_users_to_tree()
        self.show_notification("User deleted.", level='success')

if __name__ == "__main__":
    root = tk.Tk()
    app = AttendanceGUI(root)
    root.mainloop()
