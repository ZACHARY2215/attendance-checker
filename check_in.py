import cv2
import face_recognition
import json
import os
import pandas as pd
import serial
from datetime import datetime
from typing import Tuple, Optional
import numpy as np

class CheckInSystem:
    def __init__(self, config_path: str = 'camera_config.json', 
                 students_path: str = 'students.csv',
                 faces_dir: str = 'faces'):
        # Load configuration
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        # Initialize camera
        self.camera = self._setup_camera()
        
        # Load student database
        self.students_df = pd.read_csv(students_path)
        
        # Create faces directory if it doesn't exist
        self.faces_dir = faces_dir
        os.makedirs(self.faces_dir, exist_ok=True)
        
        # Initialize RFID reader
        self.rfid_reader = self._setup_rfid()
    
    def _setup_camera(self):
        """Initialize the check-in camera."""
        cam_config = self.config['check_in_camera']
        cap = cv2.VideoCapture(cam_config['source'])
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, cam_config['resolution'][0])
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, cam_config['resolution'][1])
        cap.set(cv2.CAP_PROP_FPS, cam_config['fps'])
        return cap
    
    def _setup_rfid(self):
        """Initialize RFID reader - modify port as needed."""
        try:
            return serial.Serial('/dev/tty.usbserial', 9600, timeout=1)
        except:
            print("Warning: RFID reader not connected")
            return None
    
    def read_rfid(self) -> Optional[str]:
        """Read RFID card number."""
        if self.rfid_reader is None:
            # For testing without RFID reader
            return input("Enter student ID: ")
        
        if self.rfid_reader.in_waiting:
            rfid_data = self.rfid_reader.readline().decode('utf-8').strip()
            return rfid_data
        return None
    
    def capture_face(self) -> Optional[np.ndarray]:
        """Capture and return a frame from the camera."""
        ret, frame = self.camera.read()
        if not ret:
            return None
        return frame
    
    def process_check_in(self, student_id: str) -> Tuple[bool, str]:
        """Process student check-in with RFID and face capture."""
        # Verify student ID exists
        student = self.students_df[self.students_df['student_id'] == student_id]
        if student.empty:
            return False, "Student ID not found"
        
        # Capture face
        frame = self.capture_face()
        if frame is None:
            return False, "Failed to capture image"
        
        # Detect face in frame
        face_locations = face_recognition.face_locations(frame)
        if not face_locations:
            return False, "No face detected"
        
        # Save face image
        face_path = os.path.join(self.faces_dir, f"{student_id}.jpg")
        cv2.imwrite(face_path, frame)
        
        # Get face encoding
        face_encoding = face_recognition.face_encodings(frame, face_locations)[0]
        encoding_path = os.path.join(self.faces_dir, f"{student_id}.npy")
        np.save(encoding_path, face_encoding)
        
        # Log check-in time
        check_in_time = datetime.now()
        self._update_attendance_log(student_id, student.iloc[0]['name'], check_in_time)
        
        return True, "Check-in successful"
    
    def _update_attendance_log(self, student_id: str, name: str, check_in_time: datetime):
        """Update the attendance log Excel file."""
        try:
            df = pd.read_excel('attendance.xlsx')
        except FileNotFoundError:
            df = pd.DataFrame(columns=['student_id', 'name', 'check_in_time', 'last_seen_time'])
        
        # Update or append new check-in
        new_row = {
            'student_id': student_id,
            'name': name,
            'check_in_time': check_in_time,
            'last_seen_time': check_in_time
        }
        
        if student_id in df['student_id'].values:
            df.loc[df['student_id'] == student_id] = new_row
        else:
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        
        df.to_excel('attendance.xlsx', index=False)
    
    def close(self):
        """Clean up resources."""
        if self.camera is not None:
            self.camera.release()
        if self.rfid_reader is not None:
            self.rfid_reader.close()

if __name__ == "__main__":
    # Test the check-in system
    check_in_system = CheckInSystem()
    try:
        while True:
            student_id = check_in_system.read_rfid()
            if student_id:
                success, message = check_in_system.process_check_in(student_id)
                print(f"Check-in result: {message}")
    except KeyboardInterrupt:
        check_in_system.close()
        print("\nCheck-in system closed") 