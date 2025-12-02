# CSV Cleaner (Version 2)

## Purpose
An improved, flexible CSV cleaner script that allows the user to specify which columns should be treated as text, integers, or money values.

## Features
- Cleans money columns (removes commas, converts to numeric type)
- Cleans integer columns (converts to integers, handles missing/invalid values)
- Cleans text columns (strips whitespace, normalizes formatting)
- Preserves all other data
- Outputs a cleaning report and preview

## File Structure
csv_cleaner_2/  
│── clean_csv.py  
│── messy_data.csv  
│── clean_data.csv  
└── README.md  

## Requirements
- Python 3  
- pandas library  

Install dependencies:
