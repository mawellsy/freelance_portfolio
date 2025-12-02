# File Organizer Script

## Overview
This script organizes files inside a chosen folder into subfolders based on file type (extension). It is designed as a simple utility that non-technical users can run to quickly tidy up a messy folder.

## Features
- Automatically groups files into category folders such as:
  - `Images`
  - `Documents`
  - `Spreadsheets`
  - `Presentations`
  - `Archives`
  - `Code`
  - `Other`
- Creates category folders if they do not already exist
- Handles name conflicts by adding a numeric suffix (e.g. `file_1.txt`)
- Optional **dry-run** mode to preview what will happen before moving any files

## File Structure
```text
file_organizer/
│── file_organizer.py
│── example_files/        # (optional) sample messy folder for testing
└── README.md
