# CSV Cleaner (Version 1)

## Purpose
This script takes a messy CSV file and transforms it into a clean, consistent dataset ready for analysis.

## Features
- Strips leading/trailing whitespace from text fields  
- Converts text columns to lowercase  
- Removes rows with missing values in key columns  
- Converts numeric columns into proper number format  
- Drops duplicates  
- Fixes date formats when applicable  

## File Structure
csv_cleaner/  
│── messy_data.csv  
│── clean_csv.py  
└── README.md  

## Requirements
- Python 3  
- pandas library  

Install dependencies:
