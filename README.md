# Real-Time Attendance Monitoring System

A comprehensive system for monitoring student attendance at events using RFID check-in and continuous face recognition monitoring, with a modern Tkinter GUI.

## Features

- User authentication and roles (admin/teacher/guest)
- Student registration with face capture, edit, delete, and view face image
- Attendance correction: edit and delete attendance records
- Event scheduling: add, edit, and delete events
- Export attendance log to CSV and PDF
- Smaller, compact camera and monitor windows
- RFID-based student check-in (mocked for testing)
- Face recognition for continuous presence monitoring
- Multi-threaded, non-blocking real-time camera and monitoring
- Modern dark-mode GUI (Tkinter)
- Attendance log in Excel (`attendance.xlsx`)
- Reports tab with filtering, statistics, and status badges
- Reset logs and quit functionality
- Robust error handling and UI responsiveness
- Optional Google Sheets integration

## Requirements

- macOS (tested on macOS Monterey and above)
- Windows 10/11 (see Windows instructions below)
- Python 3.10 (with Tkinter support)
- Homebrew (for CMake and Python installation on macOS)
- USB Webcam(s)
- (Optional) USB RFID Reader

## Installation

### On macOS

1. **Clone this repository**
2. **Run the setup script (recommended):**
   ```bash
   ./setup.sh
   ```
   This will:
   - Install Homebrew (if missing)
   - Install CMake and Python 3.10 with Tkinter
   - Create and activate a virtual environment
   - Install all dependencies, including dlib, face_recognition_models, and reportlab (for PDF export)

   If you prefer manual setup, see the `setup.sh` file for step-by-step commands.

3. **(If not using setup.sh) Install dependencies manually:**
   ```bash
   pip install -r requirements.txt
   pip install reportlab
   ```

### On Windows

1. **Install Python 3.10**
   - Download and install Python 3.10 from the [official website](https://www.python.org/downloads/release/python-3100/).
   - Make sure to check "Add Python to PATH" during installation.
2. **Install CMake**
   - Download and install CMake from [cmake.org](https://cmake.org/download/).
   - Add CMake to your system PATH if not done automatically.
3. **Install Visual Studio Build Tools**
   - Download and install [Build Tools for Visual Studio](https://visualstudio.microsoft.com/visual-cpp-build-tools/).
   - During installation, select the "Desktop development with C++" workload.
4. **Clone this repository**
   ```sh
   git clone https://github.com/ZACHARY2215/attendance-checker.git
   cd attendance-checker
   ```
5. **Create and activate a virtual environment**
   ```sh
   python -m venv venv
   venv\Scripts\activate
   ```
6. **Upgrade pip**
   ```sh
   python -m pip install --upgrade pip
   ```
7. **Install dependencies**
   ```sh
   pip install cmake
   pip install dlib
   pip install git+https://github.com/ageitgey/face_recognition_models
   pip install -r requirements.txt
   pip install reportlab
   pip install --upgrade setuptools
   pip install customtkinter
   ```
   - If you encounter issues with `dlib`, ensure CMake and Visual Studio Build Tools are correctly installed and on your PATH.
   - If you have issues with `face_recognition`, try installing the wheel from [PyPI](https://pypi.org/project/face-recognition/) or [Unofficial Windows Binaries for Python Extension Packages](https://www.lfd.uci.edu/~gohlke/pythonlibs/#dlib).

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
   (Optional) Edit `camera_config.json` if you wish to use custom camera settings.

3. **Google Sheets Sync:**  
   (Optional) Set up Google Sheets credentials if you want cloud sync. See `sheets_sync.py` for details.

4. **User Management:**
   - On first run, a default admin user is created:
     - Username: `admin`
     - Password: `admin`
   - Log in as admin to add, edit, or delete users and assign roles (admin, teacher, guest).
   - Only admins can access the Admin tab and all management features.

## Usage

1. **Activate the virtual environment:**
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```
   - On Windows:
     ```cmd
     venv\Scripts\activate
     ```
2. **Launch the GUI:**
   ```bash
   python gui.py
   ```
   - On first run, log in with:
     - Username: `admin`
     - Password: `admin`
   - Use the sidebar to access Check-in, Monitoring, Reports, and Admin tabs.
   - Register new students with face capture, edit or delete students, and view their face images in the Admin tab.
   - Use Attendance Correction to manually edit or delete attendance records.
   - Use Event Scheduling to add, edit, or delete events.
   - Export attendance logs to CSV or PDF from the Admin tab.
   - The Admin tab is scrollable for easy access to all management features.
   - Camera and monitor windows are compact (320x240) for a cleaner UI.

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
- `setup.sh`: Automated environment and dependency setup (macOS)
- `events.csv`: Event scheduling data
- `users.csv`: User authentication and roles

## Attendance Log Format

The `attendance.xlsx` file contains:
- `student_id`
- `name`
- `check_in_time`
- `last_seen_time`
- `status` (`PRESENT`, `LATE`, `LEFT_EARLY`, `ABSENT`)
- `total_time_present`

## Admin Tab Features

- **User Management:** Add, edit, and delete users; assign roles (admin, teacher, guest).
- **Student Management:** Register, edit, delete, and view face images for students.
- **Attendance Correction:** Edit or delete attendance records manually.
- **Event Scheduling:** Add, edit, and delete events for attendance tracking.
- **Export:** Export attendance logs to CSV or PDF.
- **Scrollable Layout:** Easily access all management features, even on smaller screens.

## Troubleshooting

- If you encounter issues with dlib or face_recognition installation, ensure CMake and Python 3.10 (with Tkinter) are installed (and Visual Studio Build Tools on Windows).
- For camera errors, ensure your webcam is connected and accessible.
- For Google Sheets sync, follow the setup instructions in `sheets_sync.py`.
- For PDF export, install `reportlab` with `pip install reportlab` if not already present. If PDF export fails, check that `reportlab` is installed in your virtual environment.

## License

MIT License 