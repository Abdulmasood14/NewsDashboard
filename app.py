import streamlit as st
import pandas as pd
import os
import glob
from datetime import datetime, date, timedelta
import re 
import requests
from io import StringIO
import time

# Page configuration
st.set_page_config(
    page_title="Company News Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS to replicate Flask dashboard styling
st.markdown("""
<style>
    .stApp {
        background: #0a0a0a;
        background-image: 
            radial-gradient(circle at 20% 80%, rgba(120, 119, 198, 0.3) 0%, transparent 50%),
            radial-gradient(circle at 80% 20%, rgba(255, 119, 198, 0.3) 0%, transparent 50%),
            radial-gradient(circle at 40% 40%, rgba(120, 219, 255, 0.2) 0%, transparent 50%);
        color: #ffffff;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .main-container {
        display: flex;
        height: 100vh;
        gap: 20px;
        padding: 20px;
    }
    
    .sidebar-custom {
        width: 350px;
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(30px);
        border: 2px solid rgba(255,255,255,0.1);
        border-radius: 24px;
        box-shadow: 0 25px 50px rgba(0,0,0,0.5);
        overflow: hidden;
        display: flex;
        flex-direction: column;
        height: fit-content;
        max-height: 90vh;
    }
    
    .sidebar-header {
        background: linear-gradient(145deg, #ff0080 0%, #7928ca 50%, #4c1d95 100%);
        padding: 28px 24px 20px 24px;
        position: relative;
        overflow: hidden;
    }
    
    .sidebar-header h2 {
        font-size: 22px;
        font-weight: 900;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        gap: 12px;
        color: white;
        text-shadow: 0 4px 20px rgba(0,0,0,0.3);
    }
    
    .search-container {
        background: rgba(255,255,255,0.15);
        border-radius: 12px;
        padding: 16px;
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255,255,255,0.2);
    }
    
    .company-lists {
        flex: 1;
        overflow-y: auto;
        max-height: 60vh;
    }
    
    .section-header {
        padding: 18px 24px;
        font-weight: 700;
        font-size: 13px;
        text-transform: uppercase;
        letter-spacing: 1px;
        border-bottom: 1px solid rgba(255,255,255,0.1);
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: rgba(255,255,255,0.02);
    }
    
    .has-news-header {
        color: #34d399;
    }
    
    .no-news-header {
        color: #f87171;
    }
    
    .company-count {
        background: rgba(255,255,255,0.15);
        color: rgba(255,255,255,0.9);
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 600;
        backdrop-filter: blur(10px);
    }
    
    .company-item {
        padding: 16px 24px;
        border-bottom: 1px solid rgba(255,255,255,0.08);
        cursor: pointer;
        transition: all 0.3s ease;
        display: flex;
        align-items: center;
        gap: 16px;
        position: relative;
        overflow: hidden;
    }
    
    .company-item:hover {
        background: rgba(255,255,255,0.08);
        transform: translateX(4px);
    }
    
    .company-item.selected {
        background: rgba(99, 102, 241, 0.15);
        border-left: 3px solid #6366f1;
        transform: translateX(4px);
    }
    
    .status-dot {
        width: 10px;
        height: 10px;
        border-radius: 50%;
        flex-shrink: 0;
        box-shadow: 0 0 10px rgba(255,255,255,0.3);
    }
    
    .dot-green {
        background: #34d399;
        box-shadow: 0 0 15px rgba(52, 211, 153, 0.4);
    }
    
    .dot-red {
        background: #f87171;
        box-shadow: 0 0 15px rgba(248, 113, 113, 0.4);
    }
    
    .company-name {
        font-size: 14px;
        font-weight: 500;
        color: rgba(255,255,255,0.95);
    }
    
    .main-content {
        flex: 1;
        background: rgba(15, 15, 15, 0.7);
        backdrop-filter: blur(40px);
        border: 2px solid rgba(255,255,255,0.1);
        border-radius: 24px;
        box-shadow: 0 25px 50px rgba(0,0,0,0.5);
        position: relative;
        min-height: 500px;
        overflow: hidden;
    }
    
    .date-picker-float {
        position: absolute;
        top: 20px;
        right: 20px;
        z-index: 10;
        background: rgba(255,255,255,0.1);
        backdrop-filter: blur(20px);
        border-radius: 12px;
        padding: 12px;
        border: 1px solid rgba(255,255,255,0.2);
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .date-label {
        font-size: 12px;
        font-weight: 600;
        color: rgba(255,255,255,0.8);
        text-transform: uppercase;
    }
    
    .welcome-screen {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 100%;
        padding: 60px 40px;
        text-align: center;
    }
    
    .welcome-title {
        font-size: 32px;
        font-weight: 800;
        background: linear-gradient(135deg, #ffffff 0%, #e2e8f0 100%);
        background-clip: text;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 12px;
    }
    
    .news-detail {
        padding: 40px;
        padding-top: 80px;
        height: 100%;
        overflow-y: auto;
    }
    
    .company-title {
        font-size: 28px;
        font-weight: 800;
        background: linear-gradient(135deg, #ffffff 0%, #e2e8f0 100%);
        background-clip: text;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 8px;
    }
    
    .date-badge {
        display: inline-block;
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        color: white;
        padding: 8px 16px;
        border-radius: 25px;
        font-size: 13px;
        font-weight: 600;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3);
        margin-bottom: 30px;
    }
    
    .news-content ul {
        list-style: none;
        padding-left: 0;
        margin: 20px 0;
    }
    
    .news-content li {
        position: relative;
        padding-left: 20px;
        margin-bottom: 12px;
        line-height: 1.6;
        color: rgba(255,255,255,0.9);
    }
    
    .news-content li:before {
        content: '•';
        position: absolute;
        left: 0;
        color: #6366f1;
        font-weight: bold;
        font-size: 16px;
    }
    
    .no-news-message {
        background: linear-gradient(135deg, rgba(248, 113, 113, 0.1) 0%, rgba(239, 68, 68, 0.1) 100%);
        border: 1px solid rgba(248, 113, 113, 0.3);
        color: #fca5a5;
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        font-weight: 500;
        backdrop-filter: blur(10px);
        margin: 20px 0;
    }
    
    .links-section {
        margin-top: 24px;
        padding-top: 24px;
        border-top: 1px solid rgba(255,255,255,0.1);
    }
    
    .links-toggle {
        display: flex;
        align-items: center;
        gap: 8px;
        cursor: pointer;
        padding: 12px 0;
        color: rgba(255,255,255,0.8);
        font-weight: 600;
        font-size: 15px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        transition: color 0.3s ease;
        border: none;
        background: none;
        width: 100%;
        text-align: left;
    }
    
    .links-toggle:hover {
        color: rgba(255,255,255,1);
    }
    
    .toggle-arrow {
        transition: transform 0.3s ease;
        font-size: 12px;
    }
    
    .toggle-arrow.expanded {
        transform: rotate(90deg);
    }
    
    .links-content {
        margin-top: 12px;
    }
    
    .news-link {
        display: block;
        color: #60a5fa !important;
        text-decoration: none;
        font-size: 13px;
        margin-bottom: 8px;
        padding: 8px 12px;
        background: rgba(96, 165, 250, 0.1);
        border-radius: 8px;
        border-left: 3px solid #60a5fa;
        transition: all 0.3s ease;
        word-break: break-all;
    }
    
    .news-link:hover {
        color: #93c5fd !important;
        background: rgba(96, 165, 250, 0.2);
        transform: translateX(4px);
    }
    
    /* Hide Streamlit default elements */
    .stApp > header {
        display: none;
    }
    
    .stApp > div:first-child {
        padding-top: 0;
    }
    
    section[data-testid="stSidebar"] {
        display: none;
    }
    
    /* Custom input styling */
    .stTextInput > div > div > input {
        background: rgba(255,255,255,0.95) !important;
        color: #0f172a !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 500 !important;
        padding: 12px 16px !important;
    }
    
    .stDateInput > div > div > input {
        background: rgba(255,255,255,0.95) !important;
        color: #0f172a !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: 13px !important;
        padding: 8px 12px !important;
    }
</style>
""", unsafe_allow_html=True)

# Nifty 50 companies list
NIFTY_50_COMPANIES = [
    "RELIANCE", "TCS", "HDFCBANK", "BHARTIARTL", "INFY", "ICICIBANK", "SBIN", "LICI",
    "HINDUNILVR", "ITC", "KOTAKBANK", "LT", "HCLTECH", "ASIANPAINT", "AXISBANK",
    "MARUTI", "SUNPHARMA", "TITAN", "ULTRACEMCO", "ADANIENT", "WIPRO", "ONGC",
    "NTPC", "JSWSTEEL", "M&M", "POWERGRID", "BAJFINANCE", "TATAMOTORS", "TECHM",
    "ADANIPORTS", "COALINDIA", "NESTLEIND", "TATACONSUM", "BAJAJFINSV", "HDFCLIFE",
    "HINDALCO", "INDUSINDBK", "SBILIFE", "BPCL", "GRASIM", "CIPLA", "TATASTEEL",
    "APOLLOHOSP", "DRREDDY", "EICHERMOT", "BRITANNIA", "DIVISLAB", "HEROMOTOCO",
    "BAJAJ-AUTO", "UPL"
]

class CompanyDataProcessor:
    def __init__(self, github_repo="Abdulmasood14/news", csv_directory="scraper_csv_outputs"):
        self.github_repo = github_repo
        self.csv_directory = csv_directory
        self.companies_data = {}
        self.available_dates = []
        self.load_available_dates()
    
    def load_available_dates(self):
        """Load available dates by checking local CSV files or predefined list"""
        try:
            if os.path.exists(self.csv_directory):
                csv_files = glob.glob(os.path.join(self.csv_directory, "*.csv"))
                dates = []
                
                for file_path in csv_files:
                    filename = os.path.basename(file_path)
                    date_from_file = self.extract_date_from_filename(filename)
                    if date_from_file:
                        dates.append(date_from_file)
                
                self.available_dates = sorted(list(set(dates)), reverse=True)
            else:
                predefined_dates = [
                    date(2025, 8, 29),
                    date(2025, 8, 28),
                    date(2025, 8, 27),
                    date(2025, 8, 26),
                    date(2025, 8, 25),
                    date(2025, 8, 24),
                    date(2025, 8, 23),
                    date(2025, 8, 22),
                    date(2025, 8, 21),
                ]
                self.available_dates = predefined_dates
                
        except Exception as e:
            self.available_dates = []
    
    def extract_date_from_filename(self, filename):
        """Extract date from CSV filename (format: DD.MM.YYYY.csv)"""
        date_pattern = r'(\d{2})\.(\d{2})\.(\d{4})\.csv$'
        match = re.search(date_pattern, filename)
        
        if match:
            day, month, year = match.groups()
            try:
                return date(int(year), int(month), int(day))
            except ValueError:
                return None
        
        return None
    
    def load_company_data_for_date(self, selected_date):
        """Load company data for specific date from GitHub using direct URL"""
        if not selected_date:
            return
        
        date_str = selected_date.strftime("%d.%m.%Y")
        csv_filename = f"{date_str}.csv"
        
        possible_urls = [
            f"https://raw.githubusercontent.com/{self.github_repo}/main/{self.csv_directory}/{csv_filename}",
            f"https://raw.githubusercontent.com/{self.github_repo}/master/{self.csv_directory}/{csv_filename}",
            f"https://raw.githubusercontent.com/{self.github_repo}/main/{csv_filename}",
            f"https://raw.githubusercontent.com/{self.github_repo}/master/{csv_filename}"
        ]
        
        for github_raw_url in possible_urls:
            try:
                response = requests.get(github_raw_url, timeout=15)
                if response.status_code == 200 and len(response.content) > 0:
                    csv_content = StringIO(response.text)
                    df = pd.read_csv(csv_content)
                    
                    required_columns = ['Company_Name', 'Extracted_Links', 'Extracted_Text']
                    if not all(col in df.columns for col in required_columns):
                        continue
                    
                    companies_data = {}
                    
                    for index, row in df.iterrows():
                        company_name = str(row['Company_Name']).strip().upper()
                        
                        if company_name and company_name != 'NAN':
                            companies_data[company_name] = {
                                'company_name': company_name,
                                'extracted_links': str(row['Extracted_Links']) if pd.notna(row['Extracted_Links']) else '',
                                'extracted_text': str(row['Extracted_Text']) if pd.notna(row['Extracted_Text']) else '',
                                'file_path': github_raw_url,
                                'extraction_date': selected_date,
                                'row_number': index + 1
                            }
                    
                    self.companies_data = companies_data
                    return
                    
            except Exception as e:
                continue
        
        self.companies_data = {}
    
    def categorize_companies(self):
        """Categorize companies into has_news and no_news based on extracted text"""
        has_news = []
        no_news = []
        
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
        
        for company_name in NIFTY_50_COMPANIES:
            if company_name in self.companies_data:
                data = self.companies_data[company_name]
                extracted_text = data.get('extracted_text', '').lower().strip()
                
                # Check if it's "no news" content
                is_no_news = False
                if not extracted_text or len(extracted_text) < 50:
                    is_no_news = True
                else:
                    date_pattern = r"no significant corporate developments for .+ on \d{2}\.\d{2}\.\d{4}"
                    if re.search(date_pattern, extracted_text):
                        is_no_news = True
                    else:
                        for pattern in no_news_patterns:
                            if pattern in extracted_text:
                                is_no_news = True
                                break
                
                if is_no_news:
                    no_news.append(company_name)
                else:
                    has_news.append(company_name)
            else:
                # Company not in data - treat as no news
                no_news.append(company_name)
        
        return has_news, no_news
    
    def get_company_data(self, company_name):
        """Get data for specific company"""
        return self.companies_data.get(company_name.upper())
    
    def get_available_dates(self):
        """Get list of available dates"""
        return self.available_dates
    
    def search_companies(self, search_term, companies_list):
        """Search companies by name"""
        if not search_term:
            return companies_list
        
        search_term = search_term.upper()
        return [company for company in companies_list if search_term in company]

def extract_urls_from_text(text):
    """Extract URLs from text and return as list"""
    if not text or text.lower() == 'nan':
        return []
    
    url_pattern = r'(https?://[^\s"\'<>]+)'
    urls = re.findall(url_pattern, text)
    return list(set(urls))  # Remove duplicates

def convert_to_bullet_points(text):
    """Convert text to HTML bullet points"""
    if not text or text.lower() == 'nan':
        return ""
    
    sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
    
    if not sentences:
        return text
    
    if len(sentences) == 1:
        return f"<ul><li>{sentences[0]}</li></ul>"
    
    bullet_points = ''.join([f"<li>{sentence}</li>" for sentence in sentences])
    return f"<ul>{bullet_points}</ul>"

def main():
    # Initialize session state
    if 'selected_date' not in st.session_state:
        st.session_state.selected_date = None
    if 'selected_company' not in st.session_state:
        st.session_state.selected_company = None
    if 'search_term' not in st.session_state:
        st.session_state.search_term = ""
    if 'links_expanded' not in st.session_state:
        st.session_state.links_expanded = False
    
    # Initialize data processor
    processor = CompanyDataProcessor()
    
    # Main layout container
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    # Create two columns for sidebar and main content
    col1, col2 = st.columns([350, 1000], gap="medium")
    
    with col1:
        render_sidebar(processor)
    
    with col2:
        render_main_content(processor)
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_sidebar(processor):
    """Render the left sidebar with search and company lists"""
    st.markdown('<div class="sidebar-custom">', unsafe_allow_html=True)
    
    # Sidebar header
    st.markdown('''
    <div class="sidebar-header">
        <h2>📊 Company News</h2>
        <div class="search-container">
    ''', unsafe_allow_html=True)
    
    # Search input
    search_term = st.text_input(
        "",
        placeholder="Search companies...",
        key="company_search",
        label_visibility="collapsed"
    )
    st.session_state.search_term = search_term
    
    st.markdown('</div></div>', unsafe_allow_html=True)
    
    # Company lists
    st.markdown('<div class="company-lists">', unsafe_allow_html=True)
    
    # Load data if date is selected
    if st.session_state.selected_date:
        processor.load_company_data_for_date(st.session_state.selected_date)
        has_news, no_news = processor.categorize_companies()
        
        # Filter based on search
        if search_term:
            has_news = processor.search_companies(search_term, has_news)
            no_news = processor.search_companies(search_term, no_news)
        
        # Companies with news section
        if has_news:
            st.markdown(f'''
            <div class="section-header has-news-header">
                <span>✅ COMPANIES WITH NEWS</span>
                <span class="company-count">{len(has_news)}</span>
            </div>
            ''', unsafe_allow_html=True)
            
            for company in has_news:
                selected_class = "selected" if st.session_state.selected_company == company else ""
                if st.button(
                    company,
                    key=f"news_{company}",
                    help=f"View news for {company}",
                    use_container_width=True
                ):
                    st.session_state.selected_company = company
                    st.rerun()
                
                # Custom styling for company items
                if st.session_state.selected_company == company:
                    st.markdown(f'''
                    <script>
                    document.querySelector('[data-testid="stButton"]:has([key="news_{company}"])').classList.add('selected');
                    </script>
                    ''', unsafe_allow_html=True)
        
        # Companies with no news section
        if no_news:
            st.markdown(f'''
            <div class="section-header no-news-header">
                <span>📰 NO SIGNIFICANT NEWS</span>
                <span class="company-count">{len(no_news)}</span>
            </div>
            ''', unsafe_allow_html=True)
            
            for company in no_news:
                if st.button(
                    company,
                    key=f"no_news_{company}",
                    help=f"View details for {company}",
                    use_container_width=True
                ):
                    st.session_state.selected_company = company
                    st.rerun()
    else:
        # Show all companies when no date selected
        all_companies = processor.search_companies(search_term, NIFTY_50_COMPANIES)
        st.markdown(f'''
        <div class="section-header">
            <span>📋 ALL NIFTY 50 COMPANIES</span>
            <span class="company-count">{len(all_companies)}</span>
        </div>
        ''', unsafe_allow_html=True)
        
        for company in all_companies:
            if st.button(
                company,
                key=f"all_{company}",
                help=f"Select {company} (choose a date first)",
                use_container_width=True,
                disabled=True
            ):
                pass
    
    st.markdown('</div></div>', unsafe_allow_html=True)

def render_main_content(processor):
    """Render the main content area"""
    st.markdown('<div class="main-content">', unsafe_allow_html=True)
    
    # Floating date picker
    st.markdown('<div class="date-picker-float">', unsafe_allow_html=True)
    st.markdown('<span class="date-label">DATE:</span>', unsafe_allow_html=True)
    
    available_dates = processor.get_available_dates()
    if available_dates:
        selected_date = st.date_input(
            "",
            value=st.session_state.selected_date if st.session_state.selected_date else available_dates[0],
            min_value=min(available_dates),
            max_value=max(available_dates),
            key="date_picker",
            label_visibility="collapsed"
        )
        
        if selected_date != st.session_state.selected_date:
            st.session_state.selected_date = selected_date
            st.session_state.selected_company = None  # Reset company selection
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Main content based on state
    if st.session_state.selected_company and st.session_state.selected_date:
        render_company_details(processor)
    else:
        render_welcome_screen()
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_welcome_screen():
    """Render the welcome screen"""
    st.markdown('''
    <div class="welcome-screen">
        <div style="width: 100px; height: 100px; background: linear-gradient(135deg, #34d399, #3b82f6, #8b5cf6); 
                    border-radius: 20px; display: flex; align-items: center; justify-content: center; 
                    margin-bottom: 30px; box-shadow: 0 10px 30px rgba(139, 92, 246, 0.3);">
            <div style="display: flex; gap: 6px; align-items: end;">
                <div style="width: 8px; height: 25px; background: rgba(255,255,255,0.9); border-radius: 3px;"></div>
                <div style="width: 8px; height: 35px; background: rgba(255,255,255,0.9); border-radius: 3px;"></div>
                <div style="width: 8px; height: 20px; background: rgba(255,255,255,0.9); border-radius: 3px;"></div>
                <div style="width: 8px; height: 30px; background: rgba(255,255,255,0.9); border-radius: 3px;"></div>
            </div>
        </div>
        <h1 class="welcome-title">Welcome to Company News Dashboard</h1>
        <p style="font-size: 18px; color: rgba(255,255,255,0.8); line-height: 1.6;">
            Select a date from the calendar and choose a company to view its news and updates
        </p>
    </div>
    ''', unsafe_allow_html=True)

def render_company_details(processor):
    """Render company details view"""
    company_data = processor.get_company_data(st.session_state.selected_company)
    
    if not company_data:
        st.markdown('''
        <div class="news-detail">
            <div class="no-news-message">
                No news data found for this company on the selected date.
            </div>
        </div>
        ''', unsafe_allow_html=True)
        return
    
    st.markdown('<div class="news-detail">', unsafe_allow_html=True)
    
    # Company header
    st.markdown(f'''
    <h1 class="company-title">{st.session_state.selected_company}</h1>
    <div class="date-badge">
        {st.session_state.selected_date.strftime("%A, %B %d, %Y")}
    </div>
    ''', unsafe_allow_html=True)
    
    # News content
    extracted_text = company_data.get('extracted_text', '')
    if extracted_text and extracted_text.lower() != 'nan':
        # Check if it's "no news" content
        no_news_patterns = ["no significant", "no news", "no updates", "no recent news", "no developments"]
        is_no_news = any(pattern in extracted_text.lower() for pattern in no_news_patterns)
        
        if is_no_news:
            st.markdown('<div class="no-news-message">No significant news updates for this company on the selected date.</div>', unsafe_allow_html=True)
        else:
            # Convert to bullet points
            bullet_html = convert_to_bullet_points(extracted_text)
            st.markdown(f'<div class="news-content">{bullet_html}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="no-news-message">No news content available for this company.</div>', unsafe_allow_html=True)
    
    # Links section
    extracted_links = company_data.get('extracted_links', '')
    urls = extract_urls_from_text(extracted_links)
    
    if urls or (extracted_links and extracted_links.lower() != 'nan' and 'no links found' not in extracted_links.lower()):
        st.markdown('<div class="links-section">', unsafe_allow_html=True)
        
        # Toggle button for links
        if st.button(
            f"{'▼' if st.session_state.links_expanded else '▶'} SOURCE LINKS",
            key="links_toggle",
            help="Click to expand/collapse source links"
        ):
            st.session_state.links_expanded = not st.session_state.links_expanded
            st.rerun()
        
        # Show links if expanded
        if st.session_state.links_expanded:
            st.markdown('<div class="links-content">', unsafe_allow_html=True)
            
            if urls:
                for i, url in enumerate(urls, 1):
                    st.markdown(f'<a href="{url}" target="_blank" class="news-link">{i}. {url}</a>', unsafe_allow_html=True)
            else:
                st.markdown('<div style="color: rgba(255,255,255,0.6); font-style: italic; padding: 8px 12px;">No clickable links available</div>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()