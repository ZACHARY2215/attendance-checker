# Real-Time Attendance Monitoring System

A comprehensive system for monitoring student attendance at events using RFID check-in and continuous face recognition monitoring, with a modern Tkinter GUI.

## Features

- RFID-based student check-in (mocked for testing)
- Face recognition for continuous presence monitoring
- Multi-threaded, non-blocking real-time camera and monitoring
- Modern dark-mode GUI (Tkinter)
- Student registration with face capture
- Attendance log in Excel (`attendance.xlsx`)
- Reports tab with filtering, statistics, and status badges
- Reset logs and quit functionality
- Robust error handling and UI responsiveness
- Optional Google Sheets integration

## Requirements

- macOS (tested on macOS Monterey and above)
- Python 3.10 (with Tkinter support)
- Homebrew (for CMake and Python installation)
- USB Webcam(s)
- (Optional) USB RFID Reader

## Installation

1. **Clone this repository**
2. **Run the setup script (recommended):**
   ```bash
   ./setup.sh
   ```
   This will:
   - Install Homebrew (if missing)
   - Install CMake and Python 3.10 with Tkinter
   - Create and activate a virtual environment
   - Install all dependencies, including dlib and face_recognition_models

   If you prefer manual setup, see the `setup.sh` file for step-by-step commands.

## Configuration

1. **Student Database:**  
   Place your `students.csv` file in the root directory with the following format:
   ```
   student_id,name
   2025001,John Smith
   2025002,Emma Johnson
   ...
   ```
2. **Camera Configuration:**  
   (Optional) Edit `camera_config.json` if you wish to use multiple or custom cameras.

3. **Google Sheets Sync:**  
   (Optional) Set up Google Sheets credentials if you want cloud sync. See `sheets_sync.py` for details.

## Usage

1. **Activate the virtual environment:**
   ```bash
   source venv/bin/activate
   ```
2. **Launch the GUI:**
   ```bash
   python gui.py
   ```
   - Use the sidebar to access Check-in, Monitoring, and Reports tabs.
   - Register new students with face capture.
   - Start/stop camera and monitoring as needed.
   - Use the Reports tab to filter, view statistics, and export logs.

## Project Structure

- `gui.py`: Main GUI application (recommended entrypoint)
- `main.py`: (Legacy) Main application orchestrator (non-GUI)
- `check_in.py`: RFID and initial face capture handling (legacy/CLI)
- `monitor.py`: Real-time face recognition monitoring (legacy/CLI)
- `sheets_sync.py`: Google Sheets synchronization
- `camera_config.json`: Camera configuration
- `students.csv`: Student database
- `attendance.xlsx`: Real-time attendance log
- `faces/`: Directory for storing reference face snapshots and encodings
- `setup.sh`: Automated environment and dependency setup

## Attendance Log Format

The `attendance.xlsx` file contains:
- `student_id`
- `name`
- `check_in_time`
- `last_seen_time`
- `status` (`PRESENT`, `LATE`, `LEFT_EARLY`, `ABSENT`)
- `total_time_present`

## Troubleshooting

- If you encounter issues with dlib or face_recognition installation, ensure CMake and Python 3.10 (with Tkinter) are installed via Homebrew.
- For camera errors, ensure your webcam is connected and accessible.
- For Google Sheets sync, follow the setup instructions in `sheets_sync.py`.

## License

MIT License 