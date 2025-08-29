import json
import os
import glob
import pandas as pd
import re
from urllib.parse import unquote

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

def process_links(links_str):
    """Process and clean links from CSV"""
    if not links_str or pd.isna(links_str):
        return []
        
    links_str = str(links_str).strip()
    if not links_str or links_str.lower().startswith('no links found'):
        return []
    
    processed_links = []
    
    # Try different delimiters
    potential_links = []
    for delimiter in [',', ';', '\n', '|', '\t']:
        if delimiter in links_str:
            potential_links = [link.strip() for link in links_str.split(delimiter)]
            break
    
    if not potential_links:  # Single link
        potential_links = [links_str]
    
    # Clean and validate each link
    for link in potential_links:
        link = link.strip()
        if link and len(link) > 10:
            # Add protocol if missing
            if not link.startswith(('http://', 'https://')):
                if link.startswith('www.'):
                    link = 'https://' + link
                elif '.' in link and not link.startswith('no '):
                    link = 'https://' + link
            
            # Validate it looks like a URL
            if any(domain in link for domain in ['http', 'www.', '.com', '.org', '.net', '.in']):
                processed_links.append(link)
    
    return processed_links

def handler(event, context):
    try:
        # Extract parameters from query parameters (Netlify redirects)
        query_params = event.get('queryStringParameters', {}) or {}
        date = query_params.get('date')
        company_name = query_params.get('company_name')
        
        if not date or not company_name:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'Date and company_name parameters are required'})
            }
        
        # Decode URL-encoded company name
        company_name = unquote(company_name)
        
        # Find and read CSV file
        csv_folder = 'scrapped_output'
        csv_files = glob.glob(os.path.join(csv_folder, '*.csv'))
        target_file = None
        
        for file_path in csv_files:
            filename = os.path.basename(file_path)
            parsed_date = parse_date_from_filename(filename)
            if parsed_date == date:
                target_file = file_path
                break
        
        if not target_file:
            return {
                'statusCode': 404,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'No data found for this date'})
            }
        
        df = pd.read_csv(target_file)
        df.columns = df.columns.str.strip()
        
        # Find the specific company
        company_row = df[df['Company_Name'].str.strip() == company_name]
        
        if company_row.empty:
            return {
                'statusCode': 404,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'Company not found'})
            }
        
        row = company_row.iloc[0]
        
        # Process links for this specific company
        processed_links = process_links(str(row['Extracted_Links']) if 'Extracted_Links' in row else '')
        
        result = {
            'company_name': company_name,
            'extracted_text': str(row['Extracted_Text']) if 'Extracted_Text' in row else '',
            'links_raw': str(row['Extracted_Links']) if 'Extracted_Links' in row else '',
            'processed_links': processed_links,
            'date': date
        }
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(result)
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