import json
import os
import glob
import pandas as pd
import re

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

def categorize_company_news(extracted_text):
    """Determine if company has significant news"""
    if not extracted_text or pd.isna(extracted_text):
        return "no_news"
    
    text_str = str(extracted_text).strip().lower()
    
    no_news_patterns = [
        "no significant corporate developments for",
        "no significant corporate developments",
        "no significant developments", 
        "no significant news",
        "no significant",
        "no news found",
        "no news",
        "no updates",
        "no recent news",
        "no major news",
        "nothing significant",
        "no developments",
        "no announcements"
    ]
    
    # Check for the specific date pattern
    date_pattern = r"no significant corporate developments for .+ on \d{2}\.\d{2}\.\d{4}"
    if re.search(date_pattern, text_str):
        return "no_news"
    
    # If text is very short (less than 50 characters), likely no news
    if len(text_str) < 50:
        return "no_news"
    
    # Check for no news patterns
    for pattern in no_news_patterns:
        if pattern in text_str:
            return "no_news"
    
    return "has_news"

def main(event, context):
    try:
        # Extract date from path
        path = event.get('path', '')
        # Path will be something like /api/company-news/2025-08-22
        path_parts = path.strip('/').split('/')
        date = path_parts[-1] if len(path_parts) >= 3 else None
        
        if not date:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'Date parameter is required'})
            }
        
        # Find CSV file for the given date
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
        
        # Read and process CSV
        df = pd.read_csv(target_file)
        df.columns = df.columns.str.strip()
        
        companies_with_news = []
        companies_no_news = []
        
        for _, row in df.iterrows():
            company_name = str(row['Company_Name']).strip()
            extracted_text = row['Extracted_Text'] if 'Extracted_Text' in row else ''
            extracted_links = row['Extracted_Links'] if 'Extracted_Links' in row else ''
            
            news_category = categorize_company_news(extracted_text)
            
            raw_links_text = str(extracted_links) if extracted_links else ''
            
            company_data = {
                'name': company_name,
                'text': str(extracted_text) if extracted_text else '',
                'links_raw': raw_links_text,
                'has_content': len(str(extracted_text).strip()) > 0
            }
            
            if news_category == "has_news":
                companies_with_news.append(company_data)
            else:
                companies_no_news.append(company_data)
        
        # Sort alphabetically within each category
        companies_with_news.sort(key=lambda x: x['name'])
        companies_no_news.sort(key=lambda x: x['name'])
        
        result = {
            'date': date,
            'companies_with_news': companies_with_news,
            'companies_no_news': companies_no_news,
            'total_companies': len(companies_with_news) + len(companies_no_news),
            'news_count': len(companies_with_news),
            'no_news_count': len(companies_no_news)
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