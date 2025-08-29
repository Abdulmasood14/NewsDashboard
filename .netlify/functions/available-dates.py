import json
import os
import glob
from datetime import datetime

def parse_date_from_filename(filename):
    """Extract date from filename like 22.08.2025.csv"""
    try:
        date_part = filename.replace('.csv', '')
        parts = date_part.split('.')
        
        if len(parts) == 3:
            day, month, year = parts
            return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
    except:
        pass
    return None

def handler(event, context):
    try:
        # Debug: Check current working directory and files
        current_dir = os.getcwd()
        files_in_root = os.listdir('.')
        
        # CSV files are in the project root's scrapped_output folder
        csv_folder = 'scrapped_output'
        
        # Debug response to see what's happening
        debug_info = {
            'current_directory': current_dir,
            'files_in_root': files_in_root,
            'csv_folder_exists': os.path.exists(csv_folder)
        }
        
        if not os.path.exists(csv_folder):
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'dates': [],
                    'debug': debug_info
                })
            }
        
        csv_files = glob.glob(os.path.join(csv_folder, '*.csv'))
        dates = []
        
        for file_path in csv_files:
            filename = os.path.basename(file_path)
            parsed_date = parse_date_from_filename(filename)
            if parsed_date:
                dates.append({
                    'date': parsed_date,
                    'filename': filename,
                    'display_date': datetime.strptime(parsed_date, '%Y-%m-%d').strftime('%A, %B %d, %Y')
                })
        
        # Sort dates in descending order (newest first)
        dates.sort(key=lambda x: x['date'], reverse=True)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'dates': dates,
                'debug': debug_info,
                'csv_files_found': len(csv_files)
            })
        }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': str(e)})
        }