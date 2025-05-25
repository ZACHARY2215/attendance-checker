import cv2
import face_recognition
import json
import numpy as np
import os
import pandas as pd
import threading
import time
from datetime import datetime
from queue import Queue
from typing import Dict, List, Optional, Tuple

class CameraStream:
    def __init__(self, source: int, name: str, resolution: Tuple[int, int], fps: int):
        self.name = name
        self.cap = cv2.VideoCapture(source)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, resolution[0])
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution[1])
        self.cap.set(cv2.CAP_PROP_FPS, fps)
        self.frame_queue = Queue(maxsize=1)
        self.stopped = False
        
    def start(self):
        thread = threading.Thread(target=self._update, args=())
        thread.daemon = True
        thread.start()
        return self
    
    def _update(self):
        while True:
            if self.stopped:
                return
            
            ret, frame = self.cap.read()
            if not ret:
                self.stop()
                return
            
            if not self.frame_queue.empty():
                try:
                    self.frame_queue.get_nowait()
                except Queue.Empty:
                    pass
            self.frame_queue.put(frame)
    
    def read(self) -> Optional[np.ndarray]:
        return self.frame_queue.get() if not self.frame_queue.empty() else None
    
    def stop(self):
        self.stopped = True
        self.cap.release()

class MonitoringSystem:
    def __init__(self, config_path: str = 'camera_config.json',
                 faces_dir: str = 'faces'):
        # Load configuration
        try:
            with open(config_path, 'r') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            # Create default config if not exists
            self.config = {
                "monitoring_cameras": [
                    {
                        "source": 0,
                        "name": "Main Camera",
                        "resolution": [640, 480],
                        "fps": 30
                    }
                ],
                "processing": {
                    "skip_frames": 3,
                    "recognition_threshold": 0.6
                },
                "logging": {
                    "update_interval": 10
                }
            }
            with open(config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
        
        self.faces_dir = faces_dir
        self.cameras: Dict[str, CameraStream] = {}
        self.known_face_encodings: Dict[str, np.ndarray] = {}
        self.known_face_ids: List[str] = []
        self.frame_count = 0
        self.stopped = False
        
        # Initialize cameras
        self._setup_cameras()
        
        # Load known face encodings
        self._load_face_encodings()
        
        # Start monitoring thread
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.daemon = True
    
    def _setup_cameras(self):
        """Initialize all monitoring cameras."""
        for cam_config in self.config['monitoring_cameras']:
            camera = CameraStream(
                source=cam_config['source'],
                name=cam_config['name'],
                resolution=cam_config['resolution'],
                fps=cam_config['fps']
            )
            self.cameras[cam_config['name']] = camera
    
    def _load_face_encodings(self):
        """Load pre-computed face encodings for checked-in students."""
        for filename in os.listdir(self.faces_dir):
            if filename.endswith('.npy'):
                student_id = filename[:-4]  # Remove .npy extension
                encoding_path = os.path.join(self.faces_dir, filename)
                self.known_face_encodings[student_id] = np.load(encoding_path)
                self.known_face_ids.append(student_id)
    
    def start(self):
        """Start the monitoring system."""
        # Start camera streams
        for camera in self.cameras.values():
            camera.start()
        
        # Start monitoring thread
        self.monitor_thread.start()
    
    def _monitor_loop(self):
        """Main monitoring loop."""
        while not self.stopped:
            self.frame_count += 1
            
            # Process every Nth frame as specified in config
            if self.frame_count % self.config['processing']['skip_frames'] != 0:
                continue
            
            # Process each camera feed
            for camera in self.cameras.values():
                frame = camera.read()
                if frame is None:
                    continue
                
                # Find faces in frame
                face_locations = face_recognition.face_locations(frame)
                if not face_locations:
                    continue
                
                # Get face encodings
                face_encodings = face_recognition.face_encodings(frame, face_locations)
                
                # Compare with known faces
                for face_encoding in face_encodings:
                    matches = face_recognition.compare_faces(
                        [self.known_face_encodings[id] for id in self.known_face_ids],
                        face_encoding,
                        tolerance=self.config['processing']['recognition_threshold']
                    )
                    
                    if True in matches:
                        student_id = self.known_face_ids[matches.index(True)]
                        self._update_last_seen(student_id)
            
            # Update attendance log periodically
            if self.frame_count % (self.config['processing']['skip_frames'] * 
                                 self.config['logging']['update_interval']) == 0:
                self._write_attendance_log()
    
    def _update_last_seen(self, student_id: str):
        """Update last seen time for a student."""
        try:
            df = pd.read_excel('attendance.xlsx')
            if student_id in df['student_id'].values:
                df.loc[df['student_id'] == student_id, 'last_seen_time'] = datetime.now()
                df.to_excel('attendance.xlsx', index=False)
        except Exception as e:
            print(f"Error updating last seen time: {e}")
    
    def _write_attendance_log(self):
        """Write current attendance state to Excel."""
        try:
            df = pd.read_excel('attendance.xlsx')
            df.to_excel('attendance.xlsx', index=False)
        except Exception as e:
            print(f"Error writing attendance log: {e}")
    
    def stop(self):
        """Stop the monitoring system."""
        self.stopped = True
        for camera in self.cameras.values():
            camera.stop()
        
        # Write final attendance log
        self._write_attendance_log()

if __name__ == "__main__":
    # Test the monitoring system
    monitor = MonitoringSystem()
    try:
        monitor.start()
        while True:
            time.sleep(1)  # Keep main thread alive
    except KeyboardInterrupt:
        monitor.stop()
        print("\nMonitoring system closed")
