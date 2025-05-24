#!/bin/bash

# Check if Homebrew is installed
if ! command -v brew &> /dev/null; then
    echo "Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

# Install CMake using Homebrew
echo "Installing CMake..."
brew install cmake

# Install Python 3.10 with tkinter support
echo "Installing Python 3.10 with tkinter support..."
brew reinstall python@3.10 --with-tcl-tk

# Create and activate virtual environment
echo "Creating virtual environment..."
python3.10 -m venv venv
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip

# Install face recognition models first
echo "Installing face recognition models..."
pip install git+https://github.com/ageitgey/face_recognition_models

# Install dlib separately first
echo "Installing dlib..."
pip install dlib

# Install remaining requirements
echo "Installing remaining dependencies..."
pip install -r requirements.txt

echo "Setup complete! To activate the environment, run:"
echo "source venv/bin/activate" 