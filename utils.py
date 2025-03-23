"""
Utility functions for the Tracking Tool application.
This module contains helper functions for file handling, Excel processing, and data manipulation.
"""
import os
import pandas as pd
import secrets
import logging
import re
from datetime import datetime
from werkzeug.utils import secure_filename

# Configure logger for this module
logger = logging.getLogger(__name__)

def allowed_file(filename, allowed_extensions):
    """
    Check if a file has an allowed extension.
    
    Args:
        filename (str): The name of the file to check
        allowed_extensions (set): Set of allowed file extensions
        
    Returns:
        bool: True if the file has an allowed extension, False otherwise
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def save_uploaded_file(file, upload_folder, allowed_extensions):
    """
    Save an uploaded file with a secure filename.
    
    Args:
        file (FileStorage): The uploaded file object
        upload_folder (str): Directory to save the file
        allowed_extensions (set): Set of allowed file extensions
        
    Returns:
        tuple: (filepath, filename) if successful, (None, error_message) if failed
    """
    if not file or not allowed_file(file.filename, allowed_extensions):
        return None, "Invalid file type"
    
    filename = secure_filename(file.filename)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    new_filename = f"{timestamp}_{filename}"
    filepath = os.path.join(upload_folder, new_filename)
    
    try:
        file.save(filepath)
        logger.info(f"File saved successfully: {filepath}")
        return filepath, new_filename
    except Exception as e:
        logger.error(f"Error saving file {filename}: {str(e)}")
        return None, str(e)

def validate_excel_file(filepath):
    """
    Validate that the Excel file has the required columns.
    
    Args:
        filepath (str): Path to the Excel file
        
    Returns:
        tuple: (is_valid, result) where:
               - If valid: (True, pandas.DataFrame)
               - If invalid: (False, error_message)
    """
    required_columns = ['Placement Name', 'Ad Name', 'Creative Name', 'Click Tag']
    
    try:
        # Try to read without header first to find header row
        logger.info(f"Reading Excel file: {filepath}")
        df_no_header = pd.read_excel(filepath, header=None)
        
        # Remove completely empty rows
        df_no_header = df_no_header.dropna(how='all')
        
        if df_no_header.empty:
            logger.warning("File is empty after removing empty rows")
            return False, "File is empty"
            
        logger.debug(f"Excel file shape after removing empty rows: {df_no_header.shape}")
        
        # Find the row containing the required headers
        header_row = None
        for idx, row in df_no_header.iterrows():
            # Convert row values to strings for comparison
            row_values = [str(val).strip() if pd.notnull(val) else "" for val in row]
            logger.debug(f"Checking row {idx} for headers")
            
            # Check if all required columns are in this row
            matches = []
            for col in required_columns:
                found = False
                for val in row_values:
                    if val and col.lower() == val.lower():
                        found = True
                        break
                matches.append(found)
            
            if all(matches):
                header_row = idx
                logger.info(f"Found header row at index {header_row}")
                break
        
        if header_row is None:
            # Try a more relaxed search that checks for substring matches
            logger.info("Exact match failed, trying partial match...")
            
            for idx, row in df_no_header.iterrows():
                # Convert row values to strings for comparison
                row_values = [str(val).strip() if pd.notnull(val) else "" for val in row]
                
                # Check if all required columns are substrings of any value in this row
                matches = []
                for col in required_columns:
                    found = False
                    for val in row_values:
                        if val and col.lower() in val.lower():
                            found = True
                            break
                    matches.append(found)
                
                if all(matches):
                    header_row = idx
                    logger.info(f"Found header row with partial match at index {header_row}")
                    break
        
        if header_row is None:
            logger.warning(f"Required columns not found: {', '.join(required_columns)}")
            return False, f"Required columns not found: {', '.join(required_columns)}"
        
        # Re-read the file with the correct header row
        logger.info(f"Reading Excel with header at row {header_row}")
        df = pd.read_excel(filepath, header=header_row)
        
        # Display the actual column names found
        logger.debug(f"Columns found in Excel: {list(df.columns)}")
        
        # Normalize column names (remove extra spaces, lowercase for checking)
        df.columns = [str(col).strip() for col in df.columns]
        
        # Check that all required columns are present
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            logger.warning(f"Missing required columns: {', '.join(missing_columns)}")
            return False, f"Missing required columns: {', '.join(missing_columns)}"
        
        # Handle case where file only has headers but no data
        if len(df) == 0:
            logger.warning("File contains headers but no data")
            return False, "File contains headers but no data"
        
        logger.info(f"Valid Excel file found with {len(df)} rows of data")
        return True, df
        
    except Exception as e:
        logger.exception(f"Error validating Excel file: {str(e)}")
        return False, f"Error validating Excel file: {str(e)}"

def process_excel_file(df, uploaded_file_id):
    """
    Process Excel data and prepare tracking data for database insertion.
    
    Args:
        df (pandas.DataFrame): DataFrame containing the Excel data
        uploaded_file_id (int): ID of the uploaded file record
        
    Returns:
        list: List of dictionaries containing processed tracking data
    """
    tracking_data = []
    
    # Normalize column names for consistent access
    norm_columns = {col.strip().lower(): col for col in df.columns}
    
    # Column name variations to handle different file formats
    placement_cols = ['placement name', 'placement']
    ad_cols = ['ad name', 'ad']
    creative_cols = ['creative name', 'creative']
    click_cols = ['click tag', 'click url', 'click tracking url']
    imp_cols = ['impression tag', 'impression tag (image)', 'impression url', 'imp tag', 'imp url', 'image tag']
    third_party_cols = ['3rd party tracking', 'third-party vendor tracking tag', 'third party tracking', 'third-party tracking']
    
    # Find the actual column names from normalized options
    placement_col = next((norm_columns[col] for col in placement_cols if col in norm_columns), None)
    ad_col = next((norm_columns[col] for col in ad_cols if col in norm_columns), None)
    creative_col = next((norm_columns[col] for col in creative_cols if col in norm_columns), None)
    click_col = next((norm_columns[col] for col in click_cols if col in norm_columns), None)
    imp_col = next((norm_columns[col] for col in imp_cols if col in norm_columns), None)
    third_party_col = next((norm_columns[col] for col in third_party_cols if col in norm_columns), None)
    
    # Process each row in the dataframe
    for _, row in df.iterrows():
        # Skip rows with missing essential data
        if pd.isna(row[placement_col]) or pd.isna(row[ad_col]) or pd.isna(row[click_col]):
            logger.warning(f"Skipping row with missing data: {row[placement_col] if not pd.isna(row[placement_col]) else 'N/A'}")
            continue
            
        # Extract data from the row with fallbacks for optional fields
        placement_name = str(row[placement_col]).strip()
        ad_name = str(row[ad_col]).strip()
        creative_name = str(row[creative_col]).strip() if creative_col and not pd.isna(row[creative_col]) else ""
        click_tag = str(row[click_col]).strip() if not pd.isna(row[click_col]) else ""
        imp_tag = str(row[imp_col]).strip() if imp_col and not pd.isna(row[imp_col]) else ""
        third_party_tag = str(row[third_party_col]).strip() if third_party_col and not pd.isna(row[third_party_col]) else ""
        
        # Process click tag URL (cleaning and parameter replacement)
        processed_click_tag = clean_url(click_tag) if click_tag else ""
        processed_click_tag = replace_placeholders(processed_click_tag) if processed_click_tag else ""
        
        # Process impression tag URL
        processed_imp_tag = clean_url(imp_tag) if imp_tag else ""
        processed_imp_tag = replace_placeholders(processed_imp_tag) if processed_imp_tag else ""
        
        # Process third-party tracking URL
        processed_third_party_tag = clean_url(third_party_tag) if third_party_tag else ""
        processed_third_party_tag = replace_placeholders(processed_third_party_tag) if processed_third_party_tag else ""
        
        # Create data record
        data = {
            'file_id': uploaded_file_id,
            'placement_name': placement_name,
            'ad_name': ad_name,
            'creative_name': creative_name,
            'click_tag': click_tag,
            'click_tag_converted': processed_click_tag,
            'imp_tag': imp_tag,
            'imp_tag_converted': processed_imp_tag,
            'third_party_tracking': third_party_tag,
            'third_party_converted': processed_third_party_tag
        }
        
        tracking_data.append(data)
        logger.debug(f"Processed row: {placement_name} - {ad_name}")
    
    logger.info(f"Processed {len(tracking_data)} rows of tracking data")
    return tracking_data

def clean_url(url):
    """
    Clean a URL by removing extra whitespace and handling encoding issues.
    
    Args:
        url (str): The URL to clean
        
    Returns:
        str: Cleaned URL
    """
    url = url.strip()
    
    # Extract URL from HTML tags if present
    if '<a ' in url.lower() or '<img ' in url.lower() or '<script ' in url.lower():
        # Extract from href attribute
        href_match = re.search(r'href=["\']([^"\']+)["\']', url, re.IGNORECASE)
        if href_match:
            url = href_match.group(1)
        else:
            # Extract from src attribute
            src_match = re.search(r'src=["\']([^"\']+)["\']', url, re.IGNORECASE)
            if src_match:
                url = src_match.group(1)
    
    # Remove GDPR-related parameters
    url = url.replace('${GDPR}', '')
    url = re.sub(r'\$\{GDPR_CONSENT_\d+\}', '', url)
    
    return url

def replace_placeholders(url):
    """
    Replace placeholders in tracking URLs with standardized macros.
    
    Args:
        url (str): The URL containing placeholders
        
    Returns:
        str: URL with standardized placeholders
    """
    # Common placeholder replacements for ad tracking
    replacements = {
        "[timestamp]": "{timestamp}",
        "[random]": "{random}",
        "[CACHEBUSTER]": "{cachebuster}",
        "%CACHEBUSTER%": "{cachebuster}",
        "[cachebuster]": "{cachebuster}",
        "%%CACHEBUSTER%%": "{cachebuster}",
        "${CACHEBUSTER}": "{cachebuster}",
        "${timestamp}": "{timestamp}",
        "${TIMESTAMP}": "{timestamp}",
        "%timestamp%": "{timestamp}",
        "%TIMESTAMP%": "{timestamp}",
        "[TIMESTAMP]": "{timestamp}",
    }
    
    for old, new in replacements.items():
        url = url.replace(old, new)
    
    return url 