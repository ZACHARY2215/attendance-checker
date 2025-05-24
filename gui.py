import tkinter as tk
from tkinter import ttk, messagebox
import cv2
import threading
import time
from datetime import datetime
import pandas as pd
import os
import face_recognition
from PIL import Image, ImageTk
import numpy as np

class DarkTheme:
    BG = '#23272e'
    FG = '#f8f9fa'
    BUTTON_BG = '#343a40'
    BUTTON_FG = '#f8f9fa'
    ACCENT = '#007ACC'
    SUCCESS = '#28a745'
    WARNING = '#ffc107'
    ERROR = '#dc3545'
    SIDEBAR_BG = '#181a1b'
    SIDEBAR_ACTIVE = '#007ACC'
    CARD_BG = '#2c313a'
    HEADER_BG = '#181a1b'
    HEADER_FG = '#f8f9fa'
    NOTIF_BG = '#23272e'
    NOTIF_FG = '#f8f9fa'
    FONT = 'Arial'

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
        # Place in top right corner
        x = root.winfo_x() + root.winfo_width() - self.top.winfo_width() - 40
        y = root.winfo_y() + 40
        self.top.geometry(f'+{x}+{y}')
        self.top.after(duration, self.top.destroy)

class AttendanceGUI:
    UPDATE_INTERVAL = 120  # 2 minutes in seconds
    
    def __init__(self, root):
        self.root = root
        self.root.title("Attendance Monitoring System")
        self.root.geometry("1280x850")
        self.root.configure(bg=DarkTheme.BG)
        self.root.option_add("*Font", f"{DarkTheme.FONT} 11")
        
        # Camera and thread control
        self.camera = None
        self.camera_lock = threading.Lock()
        self.frame_ready = threading.Event()
        self.current_frame = None
        self.camera_active = False
        self.camera_thread = None
        self.monitoring_active = False
        self.monitoring_thread = None
        
        # Style
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Dark.TFrame', background=DarkTheme.BG)
        style.configure('Card.TFrame', background=DarkTheme.CARD_BG)
        style.configure('Sidebar.TFrame', background=DarkTheme.SIDEBAR_BG)
        style.configure('Header.TFrame', background=DarkTheme.HEADER_BG)
        style.configure('Header.TLabel', background=DarkTheme.HEADER_BG, foreground=DarkTheme.HEADER_FG, font=(DarkTheme.FONT, 20, 'bold'))
        style.configure('Sidebar.TButton', background=DarkTheme.SIDEBAR_BG, foreground=DarkTheme.FG, font=(DarkTheme.FONT, 12, 'bold'), borderwidth=0, relief='flat')
        style.map('Sidebar.TButton', background=[('active', DarkTheme.SIDEBAR_ACTIVE), ('selected', DarkTheme.SIDEBAR_ACTIVE)])
        style.configure('SidebarActive.TButton', background=DarkTheme.SIDEBAR_ACTIVE, foreground=DarkTheme.FG, font=(DarkTheme.FONT, 12, 'bold'), borderwidth=0, relief='flat')
        style.configure('Dark.TLabel', background=DarkTheme.BG, foreground=DarkTheme.FG)
        style.configure('Card.TLabel', background=DarkTheme.CARD_BG, foreground=DarkTheme.FG)
        style.configure('Dark.TEntry', fieldbackground=DarkTheme.CARD_BG, foreground=DarkTheme.FG, borderwidth=1)
        style.configure('Dark.TButton', background=DarkTheme.BUTTON_BG, foreground=DarkTheme.BUTTON_FG, font=(DarkTheme.FONT, 11, 'bold'), borderwidth=0, relief='flat')
        style.map('Dark.TButton', background=[('active', DarkTheme.ACCENT)])
        style.configure('Success.TButton', background=DarkTheme.SUCCESS, foreground=DarkTheme.BUTTON_FG)
        style.configure('Warning.TButton', background=DarkTheme.WARNING, foreground=DarkTheme.BUTTON_FG)
        style.configure('Dark.Treeview', background=DarkTheme.CARD_BG, foreground=DarkTheme.FG, fieldbackground=DarkTheme.CARD_BG, rowheight=28, font=(DarkTheme.FONT, 11))
        style.configure('Dark.Treeview.Heading', background=DarkTheme.BUTTON_BG, foreground=DarkTheme.FG, font=(DarkTheme.FONT, 12, 'bold'))
        
        # Create faces directory if it doesn't exist
        os.makedirs('faces', exist_ok=True)
        
        # Load or create attendance file
        self.attendance_file = 'attendance.xlsx'
        if not os.path.exists(self.attendance_file):
            pd.DataFrame(columns=[
                'student_id', 'name', 'check_in_time', 'last_seen_time',
                'status', 'total_time_present'
            ]).to_excel(self.attendance_file, index=False)
        
        # Define attendance status thresholds (in minutes)
        self.STATUS_THRESHOLDS = {
            'PRESENT': 0,      # Checked in
            'LATE': 15,        # 15 minutes late
            'LEFT_EARLY': 30,  # Left 30 minutes early
            'ABSENT': None     # Never checked in
        }
        
        self.active_tab = 'Check-in'
        self.create_modern_gui()
        
    def create_modern_gui(self):
        # Header bar
        header = ttk.Frame(self.root, style='Header.TFrame', height=60)
        header.pack(side='top', fill='x')
        ttk.Label(header, text="Attendance Monitoring System", style='Header.TLabel').pack(side='left', padx=30, pady=10)
        # Sidebar
        sidebar = ttk.Frame(self.root, style='Sidebar.TFrame', width=180)
        sidebar.pack(side='left', fill='y')
        self.sidebar_buttons = {}
        for tab, icon in zip(['Check-in', 'Monitoring', 'Reports', 'Quit'], ['📝', '🎥', '📊', '🚪']):
            btn_style = 'SidebarActive.TButton' if tab == self.active_tab else 'Sidebar.TButton'
            b = ttk.Button(sidebar, text=f"{icon}  {tab}", style=btn_style, command=lambda t=tab: self.switch_tab(t))
            b.pack(fill='x', pady=6, padx=10, ipady=6)
            self.sidebar_buttons[tab] = b
        # Main content area
        self.main_content = ttk.Frame(self.root, style='Dark.TFrame')
        self.main_content.pack(side='left', fill='both', expand=True, padx=0, pady=0)
        self.tab_frames = {}
        for tab in ['Check-in', 'Monitoring', 'Reports']:
            frame = ttk.Frame(self.main_content, style='Dark.TFrame')
            self.tab_frames[tab] = frame
        self.setup_check_in_tab(self.tab_frames['Check-in'])
        self.setup_monitoring_tab(self.tab_frames['Monitoring'])
        self.setup_reports_tab(self.tab_frames['Reports'])
        self.show_tab('Check-in')
        # Notification bar
        self.setup_notification_bar()
        
    def switch_tab(self, tab):
        if tab == 'Quit':
            self.quit_application()
            return
        self.active_tab = tab
        for t, btn in self.sidebar_buttons.items():
            btn.configure(style='SidebarActive.TButton' if t == tab else 'Sidebar.TButton')
        self.show_tab(tab)
        
    def show_tab(self, tab):
        for t, frame in self.tab_frames.items():
            frame.pack_forget()
        self.tab_frames[tab].pack(fill='both', expand=True, padx=30, pady=30)
    
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
        self.checkin_start_button = ttk.Button(camera_controls, 
                                             text="Start Camera", 
                                             style='Success.TButton',
                                             command=self.start_checkin_camera)
        self.checkin_start_button.pack(side='left', padx=5)
        self.checkin_stop_button = ttk.Button(camera_controls, 
                                            text="Stop Camera", 
                                            style='Warning.TButton',
                                            command=self.stop_checkin_camera)
        self.capture_button = ttk.Button(camera_controls, 
                                       text="Capture Face", 
                                       style='Dark.TButton',
                                       command=self.capture_face)
        self.capture_button.pack(side='left', padx=5)
        # Right side - Registration and Check-in
        control_frame = ttk.Frame(card, style='Card.TFrame')
        control_frame.grid(row=0, column=1, sticky='nsew', padx=20, pady=20)
        # Registration section
        reg_header = ttk.Label(control_frame, text="New Student Registration", style='Card.TLabel', font=(DarkTheme.FONT, 14, 'bold'))
        reg_header.pack(anchor='w', pady=(0, 8))
        reg_frame = ttk.Frame(control_frame, style='Card.TFrame')
        reg_frame.pack(fill='x', pady=8)
        ttk.Label(reg_frame, text="Student ID:", style='Card.TLabel').pack(anchor='w', pady=2)
        self.reg_id_var = tk.StringVar()
        ttk.Entry(reg_frame, textvariable=self.reg_id_var, style='Dark.TEntry').pack(fill='x', pady=2)
        ttk.Label(reg_frame, text="Name:", style='Card.TLabel').pack(anchor='w', pady=2)
        self.reg_name_var = tk.StringVar()
        ttk.Entry(reg_frame, textvariable=self.reg_name_var, style='Dark.TEntry').pack(fill='x', pady=2)
        ttk.Button(reg_frame, text="Register", style='Dark.TButton',
                  command=self.register_student).pack(pady=8, fill='x')
        # Separator
        ttk.Separator(control_frame, orient='horizontal').pack(fill='x', pady=16)
        # Check-in section
        checkin_header = ttk.Label(control_frame, text="Check-in", style='Card.TLabel', font=(DarkTheme.FONT, 14, 'bold'))
        checkin_header.pack(anchor='w', pady=(0, 8))
        checkin_frame = ttk.Frame(control_frame, style='Card.TFrame')
        checkin_frame.pack(fill='x', pady=8)
        ttk.Label(checkin_frame, text="Student ID:", style='Card.TLabel').pack(anchor='w', pady=2)
        self.student_id_var = tk.StringVar()
        ttk.Entry(checkin_frame, textvariable=self.student_id_var, style='Dark.TEntry').pack(fill='x', pady=2)
        ttk.Button(checkin_frame, text="Mock RFID Scan", style='Dark.TButton',
                  command=self.mock_rfid_scan).pack(pady=4, fill='x')
        ttk.Button(checkin_frame, text="Check In", style='Dark.TButton',
                  command=self.process_check_in).pack(pady=4, fill='x')
    
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
        self.start_button = ttk.Button(controls_frame, 
                                     text="▶ Start Monitoring", 
                                     style='Success.TButton',
                                     command=self.start_monitoring)
        self.start_button.pack(side='left', padx=5)
        self.stop_button = ttk.Button(controls_frame, 
                                    text="⏹ Stop Monitoring", 
                                    style='Warning.TButton',
                                    command=self.start_stop_monitoring)
        self.reset_button = ttk.Button(controls_frame,
                                     text="🔄 Reset Logs",
                                     style='Dark.TButton',
                                     command=self.reset_logs)
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
            students_df = pd.read_csv('students.csv')
            for _, row in students_df.iterrows():
                student_id = str(row['student_id'])
                encoding_path = os.path.join('faces', f"{student_id}.npy")
                if os.path.exists(encoding_path):
                    self.known_face_encodings[student_id] = np.load(encoding_path)
                    self.known_face_names[student_id] = row['name']
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load face encodings: {str(e)}")
    
    def start_camera(self):
        """Start the camera feed with proper resource management"""
        with self.camera_lock:
            if not self.camera_active:
                # Initialize camera if needed
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
                img = img.resize((640, 480), Image.Resampling.LANCZOS)
                img_tk = ImageTk.PhotoImage(img)
                
                # Update label if still active
                if self.camera_active:
                    self.camera_label.configure(image=img_tk)
                    self.camera_label.image = img_tk
            
            # Add small delay to reduce CPU usage
            time.sleep(0.01)
    
    def start_stop_monitoring(self):
        """Handle monitoring start/stop with proper thread management"""
        if self.monitoring_active:
            # Schedule stop operation
            self.root.after(0, self.stop_monitoring)
        else:
            self.start_monitoring()
    
    def start_monitoring(self):
        """Start monitoring with proper button management"""
        if not self.monitoring_active:
            self.start_camera()  # Ensure camera is running
            self.monitoring_active = True
            self.monitoring_thread = threading.Thread(target=self.monitor_faces)
            self.monitoring_thread.daemon = True
            self.monitoring_thread.start()
            
            # Update UI
            self.status_label.configure(text="🟢 Monitoring active",
                                      foreground=DarkTheme.SUCCESS)
            self.start_button.pack_forget()
            self.stop_button.pack(side='left', padx=5)
            messagebox.showinfo("Monitoring", "Face detection monitoring started")
    
    def stop_monitoring(self):
        """Stop monitoring without blocking the UI"""
        if self.monitoring_active:
            self.monitoring_active = False
            
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
            
            # Force update the Excel file
            self.save_attendance_data()
            
            # Show completion message
            self.root.after(500, lambda: messagebox.showinfo("Monitoring", "Monitoring stopped"))
    
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
            # Only update every 2 minutes
            if (self.last_update_time is not None and 
                (now - self.last_update_time).total_seconds() < self.UPDATE_INTERVAL):
                return
            # Load current attendance data
            self.attendance_df = pd.read_excel(self.attendance_file)
            # Get check-in and last seen
            if student_id in self.attendance_df['student_id'].values:
                check_in = pd.to_datetime(self.attendance_df.loc[
                    self.attendance_df['student_id'] == student_id, 
                    'check_in_time'
                ].iloc[0])
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
                self.attendance_df.loc[self.attendance_df['student_id'] == student_id] = new_row
            else:
                self.attendance_df = pd.concat([self.attendance_df, pd.DataFrame([new_row])], 
                                           ignore_index=True)
            # Save immediately
            self.attendance_df.to_excel(self.attendance_file, index=False)
            # Update last update time and label
            self.last_update_time = now
            self.last_update_label.configure(
                text=f"Last update: {now.strftime('%H:%M:%S')}"
            )
            # Refresh the display
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
                    
                    if confidence_score > 60:  # 60% confidence threshold
                        if confidence_score > confidence:  # Keep best match
                            confidence = confidence_score
                            student_id = sid
                            name = self.known_face_names[sid]
                
                if student_id:
                    badge_text, badge_color = self.get_status_badge('PRESENT')
                    detected_people.append(f"{name} {badge_text}")
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
            img = img.resize((800, 600), Image.Resampling.LANCZOS)
            img_tk = ImageTk.PhotoImage(img)
            
            if self.monitoring_active:  # Check if still active before updating
                self.monitor_label.configure(image=img_tk)
                self.monitor_label.image = img_tk
            
            time.sleep(0.01)  # Small delay to prevent CPU overuse
    
    def setup_reports_tab(self, parent):
        # Card-like main container
        card = ttk.Frame(parent, style='Card.TFrame')
        card.pack(fill='both', expand=True, padx=40, pady=40)
        # Header
        header = ttk.Label(card, text="Reports", style='Card.TLabel', font=(DarkTheme.FONT, 16, 'bold'))
        header.pack(anchor='w', pady=(0, 16))
        # Filters card
        filters_card = ttk.Frame(card, style='Card.TFrame')
        filters_card.pack(fill='x', pady=(0, 16))
        ttk.Label(filters_card, text="Date:", style='Card.TLabel').pack(side='left', padx=5)
        self.date_var = tk.StringVar(value=datetime.now().strftime('%Y-%m-%d'))
        ttk.Entry(filters_card, textvariable=self.date_var, style='Dark.TEntry', width=12).pack(side='left', padx=5)
        ttk.Label(filters_card, text="Event Start (HH:MM):", style='Card.TLabel').pack(side='left', padx=5)
        self.event_start_time = tk.StringVar(value="14:00")  # Default to 2:00 PM
        ttk.Entry(filters_card, textvariable=self.event_start_time, style='Dark.TEntry', width=7).pack(side='left', padx=2)
        ttk.Label(filters_card, text="End:", style='Card.TLabel').pack(side='left', padx=2)
        self.event_end_time = tk.StringVar(value="17:00")
        ttk.Entry(filters_card, textvariable=self.event_end_time, style='Dark.TEntry', width=7).pack(side='left', padx=2)
        ttk.Label(filters_card, text="Status:", style='Card.TLabel').pack(side='left', padx=5)
        self.status_var = tk.StringVar(value="ALL")
        status_menu = ttk.OptionMenu(filters_card, self.status_var, "ALL", 
                                   "ALL", "PRESENT", "LATE", "LEFT_EARLY", "ABSENT")
        status_menu.pack(side='left', padx=5)
        ttk.Button(filters_card, text="Refresh", style='Dark.TButton',
                  command=self.refresh_report).pack(side='left', padx=5)
        # Statistics card
        stats_card = ttk.Frame(card, style='Card.TFrame')
        stats_card.pack(fill='x', pady=(0, 16))
        self.stats_labels = {}
        for status in ['PRESENT', 'LATE', 'LEFT_EARLY', 'ABSENT']:
            self.stats_labels[status] = ttk.Label(stats_card, 
                                                text=f"{status}: 0", 
                                                style='Card.TLabel', font=(DarkTheme.FONT, 12, 'bold'))
            self.stats_labels[status].pack(side='left', padx=20)
        # Report table card
        table_card = ttk.Frame(card, style='Card.TFrame')
        table_card.pack(fill='both', expand=True, pady=(0, 0))
        self.tree = ttk.Treeview(table_card, style='Dark.Treeview',
                                columns=('ID', 'Name', 'Check-in', 'Last Seen', 'Status', 'Time Present'),
                                show='headings')
        self.tree.heading('ID', text='Student ID')
        self.tree.heading('Name', text='Name')
        self.tree.heading('Check-in', text='Check-in Time')
        self.tree.heading('Last Seen', text='Last Seen')
        self.tree.heading('Status', text='Status')
        self.tree.heading('Time Present', text='Time Present')
        self.tree.pack(fill='both', expand=True, pady=10)
        # Initial load
        self.refresh_report()
    
    def start_checkin_camera(self):
        """Start camera in check-in tab with proper button management"""
        if not self.camera_active:
            self.start_camera()  # Ensure camera is running
            # Update button visibility
            self.checkin_start_button.pack_forget()
            self.checkin_stop_button.pack(side='left', padx=5)
    
    def stop_checkin_camera(self):
        """Stop camera in check-in tab without blocking"""
        if self.camera_active:
            self.camera_active = False
            
            # Schedule camera stop in a separate thread
            stop_thread = threading.Thread(target=self._stop_checkin_camera_thread)
            stop_thread.daemon = True
            stop_thread.start()
            
            # Update UI immediately
            self.checkin_stop_button.pack_forget()
            self.checkin_start_button.pack(side='left', padx=5)
            
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
    
    def capture_face(self):
        messagebox.showerror("Error", "This function is now handled in a background thread. Please use Register.")
    
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
            df = pd.read_csv('students.csv')
            new_row = pd.DataFrame({'student_id': [student_id], 'name': [name]})
            df = pd.concat([df, new_row], ignore_index=True)
            df.to_csv('students.csv', index=False)
            self.root.after(0, lambda: [
                self.show_notification("Student registered successfully!", level='success'),
                self.reg_id_var.set(""),
                self.reg_name_var.set("")
            ])
        except Exception as e:
            self.root.after(0, lambda: self.show_notification(f"Failed to update students database: {str(e)}", level='error'))
    
    def mock_rfid_scan(self):
        try:
            df = pd.read_csv('students.csv')
            random_student = df.sample(n=1).iloc[0]
            self.student_id_var.set(random_student['student_id'])
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
            students_df = pd.read_csv('students.csv')
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
            attendance_df = pd.read_excel(self.attendance_file)
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
    
    def refresh_report(self):
        """Refresh the attendance report with filters and statistics, robust to missing columns"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        try:
            df = pd.read_excel(self.attendance_file)
            required_cols = ['student_id', 'name', 'check_in_time', 'last_seen_time', 'status', 'total_time_present']
            for col in required_cols:
                if col not in df.columns:
                    if col == 'status':
                        df[col] = 'ABSENT'
                    elif col == 'total_time_present':
                        df[col] = ''
                    else:
                        df[col] = ''
            selected_date = self.date_var.get()
            if selected_date:
                df['check_in_time'] = pd.to_datetime(df['check_in_time'], errors='coerce')
                df = df[df['check_in_time'].dt.strftime('%Y-%m-%d') == selected_date]
            selected_status = self.status_var.get()
            if selected_status != "ALL":
                df = df[df['status'] == selected_status]
            stats = df['status'].fillna('ABSENT').value_counts()
            for status in self.stats_labels:
                count = stats[status] if status in stats else 0
                self.stats_labels[status].configure(text=f"{status}: {count}")
            for _, row in df.iterrows():
                badge_text, badge_color = self.get_status_badge(row.get('status', ''))
                # Use a colored label for status badge
                self.tree.insert('', 'end', values=(
                    row.get('student_id', ''),
                    row.get('name', ''),
                    row.get('check_in_time', ''),
                    row.get('last_seen_time', ''),
                    badge_text,
                    row.get('total_time_present', '')
                ), tags=(row.get('status', ''),))
            # Tag config for status badges
            for status in ['PRESENT', 'LATE', 'LEFT_EARLY', 'ABSENT', '']:
                badge_text, badge_color = self.get_status_badge(status)
                self.tree.tag_configure(status, background=DarkTheme.CARD_BG, foreground=badge_color)
        except Exception as e:
            self.show_notification(f"Failed to refresh report: {str(e)}", level='error')
    
    def quit_application(self):
        """Safely quit the application"""
        if messagebox.askokcancel("Quit", "Do you want to quit the application?"):
            # Disable the quit button to prevent multiple clicks
            self.root.protocol('WM_DELETE_WINDOW', lambda: None)
            
            def cleanup_and_quit():
                # Stop monitoring if active
                if self.monitoring_active:
                    self.monitoring_active = False
                    self._stop_monitoring_thread()
                else:
                    # Stop camera if it's running but not monitoring
                    self.stop_camera()
                
                # Final cleanup
                if hasattr(self, 'camera') and self.camera is not None:
                    self.camera.release()
                
                # Destroy the window
                self.root.destroy()
            
            # Schedule cleanup and quit
            self.root.after(100, cleanup_and_quit)
    
    def __del__(self):
        """Ensure camera resources are properly released"""
        self.stop_monitoring()  # This will also stop the camera

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
        return f'  {status}  ', color

    def setup_notification_bar(self):
        self.notification_bar = tk.Label(self.root, text='', bg=DarkTheme.NOTIF_BG, fg=DarkTheme.NOTIF_FG, font=(DarkTheme.FONT, 11), anchor='w', padx=20)
        self.notification_bar.pack(side='bottom', fill='x')

if __name__ == "__main__":
    root = tk.Tk()
    app = AttendanceGUI(root)
    root.mainloop() 