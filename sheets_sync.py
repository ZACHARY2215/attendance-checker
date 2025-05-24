import gspread
import json
import pandas as pd
import time
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials
from typing import Optional

class SheetsSync:
    def __init__(self, credentials_path: str = 'credentials.json',
                 config_path: str = 'camera_config.json'):
        # Load configuration
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        # Set up Google Sheets credentials
        self.scope = ['https://spreadsheets.google.com/feeds',
                     'https://www.googleapis.com/auth/drive']
        self.credentials = ServiceAccountCredentials.from_json_keyfile_name(
            credentials_path, self.scope)
        self.client = None
        self.worksheet = None
        self.stopped = False
    
    def connect(self, spreadsheet_name: str, worksheet_name: str = 'Attendance') -> bool:
        """Connect to Google Sheets."""
        try:
            self.client = gspread.authorize(self.credentials)
            spreadsheet = self.client.open(spreadsheet_name)
            
            # Create worksheet if it doesn't exist
            try:
                self.worksheet = spreadsheet.worksheet(worksheet_name)
            except gspread.WorksheetNotFound:
                self.worksheet = spreadsheet.add_worksheet(
                    worksheet_name, rows=1000, cols=4)
                # Set up headers
                self.worksheet.append_row([
                    'Student ID',
                    'Name',
                    'Check-in Time',
                    'Last Seen Time'
                ])
            
            return True
        except Exception as e:
            print(f"Error connecting to Google Sheets: {e}")
            return False
    
    def sync_attendance(self) -> bool:
        """Sync local attendance Excel file to Google Sheets."""
        try:
            # Read local attendance file
            df = pd.read_excel('attendance.xlsx')
            
            # Convert DataFrame to list of lists
            data = df.values.tolist()
            
            # Clear existing data (except headers)
            self.worksheet.clear()
            self.worksheet.append_row([
                'Student ID',
                'Name',
                'Check-in Time',
                'Last Seen Time'
            ])
            
            # Update with new data
            if data:
                self.worksheet.append_rows(data)
            
            return True
        except Exception as e:
            print(f"Error syncing attendance: {e}")
            return False
    
    def start_auto_sync(self, interval: Optional[int] = None):
        """Start automatic synchronization."""
        if interval is None:
            interval = self.config['logging']['sheets_sync_interval']
        
        while not self.stopped:
            self.sync_attendance()
            time.sleep(interval)
    
    def stop(self):
        """Stop automatic synchronization."""
        self.stopped = True
        # Perform final sync
        self.sync_attendance()

if __name__ == "__main__":
    # Test the sheets sync
    sync = SheetsSync()
    
    # Replace with your Google Sheet name
    if sync.connect("Attendance Monitoring"):
        try:
            sync.start_auto_sync()
        except KeyboardInterrupt:
            sync.stop()
            print("\nSheets sync stopped") 