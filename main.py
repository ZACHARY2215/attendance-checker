import threading
import time
from check_in import CheckInSystem
from monitor import MonitoringSystem
from sheets_sync import SheetsSync
import os
import pandas as pd

class AttendanceSystem:
    def __init__(self):
        # Create necessary directories
        os.makedirs('faces', exist_ok=True)
        
        # Create initial student database if it doesn't exist
        if not os.path.exists('students.csv'):
            pd.DataFrame(columns=['student_id', 'name']).to_csv('students.csv', index=False)
        
        # Initialize components
        self.check_in = CheckInSystem()
        self.monitor = MonitoringSystem()
        self.sheets_sync = None  # Optional component
        
        # Initialize threads
        self.check_in_thread = threading.Thread(target=self._check_in_loop)
        self.check_in_thread.daemon = True
    
    def start(self, enable_sheets_sync: bool = False, spreadsheet_name: str = None):
        """Start the attendance system."""
        print("Starting Attendance Monitoring System...")
        
        # Start monitoring system
        print("Starting monitoring cameras...")
        self.monitor.start()
        
        # Start check-in system
        print("Starting check-in system...")
        self.check_in_thread.start()
        
        # Start Google Sheets sync if enabled
        if enable_sheets_sync and spreadsheet_name:
            print("Starting Google Sheets sync...")
            self.sheets_sync = SheetsSync()
            if self.sheets_sync.connect(spreadsheet_name):
                sheets_thread = threading.Thread(target=self.sheets_sync.start_auto_sync)
                sheets_thread.daemon = True
                sheets_thread.start()
            else:
                print("Failed to connect to Google Sheets. Continuing without sync...")
                self.sheets_sync = None
        
        print("\nSystem is ready!")
        print("Press Ctrl+C to stop the system")
    
    def _check_in_loop(self):
        """Main check-in loop."""
        while True:
            try:
                # Read RFID
                student_id = self.check_in.read_rfid()
                if student_id:
                    # Process check-in
                    success, message = self.check_in.process_check_in(student_id)
                    print(f"\nCheck-in: {message}")
                    
                    if success:
                        print("Please wait for face recognition...")
                        # Give the monitoring system time to detect the face
                        time.sleep(2)
                        print("You may proceed to the event area.")
                    
                time.sleep(0.1)  # Small delay to prevent CPU overuse
            except Exception as e:
                print(f"Error in check-in system: {e}")
                time.sleep(1)  # Delay before retry
    
    def stop(self):
        """Stop all components of the system."""
        print("\nStopping Attendance System...")
        
        # Stop monitoring
        print("Stopping monitoring system...")
        self.monitor.stop()
        
        # Stop check-in system
        print("Stopping check-in system...")
        self.check_in.close()
        
        # Stop sheets sync if enabled
        if self.sheets_sync:
            print("Stopping Google Sheets sync...")
            self.sheets_sync.stop()
        
        print("System stopped successfully!")

if __name__ == "__main__":
    system = AttendanceSystem()
    
    try:
        # Start the system (enable Google Sheets sync by uncommenting the following line)
        system.start()
        # system.start(enable_sheets_sync=True, spreadsheet_name="Attendance Monitoring")
        
        # Keep the main thread alive
        while True:
            time.sleep(1)
    
    except KeyboardInterrupt:
        system.stop() 