from __future__ import annotations
import streamlit as st
import requests
from datetime import datetime, timezone
import base64
from io import BytesIO
from PIL import Image
import os
from urllib.parse import urlparse
import mimetypes
from typing import Optional, Tuple, Any

# Date formatting functions
def format_date(ts: Any) -> str:
    """Convert Unix timestamp to readable date"""
    if ts is None or ts == 0 or ts == "N/A":
        return "N/A"
    
    # Handle string dates
    if isinstance(ts, str):
        try:
            # Try to parse as datetime string
            for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"):
                try:
                    dt = datetime.strptime(ts, fmt)
                    return dt.strftime("%Y-%m-%d")
                except ValueError:
                    continue
            # If it's a numeric string, treat as timestamp
            if ts.replace('.', '').replace('-', '').isdigit():
                ts = float(ts)
            else:
                return "Invalid Date"
        except:
            return "Invalid Date"
    
    # Handle numeric timestamps
    if isinstance(ts, (int, float)):
        # Handle milliseconds
        if ts > 1e12:
            ts = ts / 1000
        
        try:
            dt = datetime.fromtimestamp(ts, tz=timezone.utc)
            return dt.strftime("%Y-%m-%d")
        except (ValueError, OSError):
            return "Invalid Date"
    
    return "Invalid Date"

def calculate_days(start_ts: Any, end_ts: Any) -> int:
    """Calculate total active time in days"""
    if start_ts is None or end_ts is None or start_ts == 0 or end_ts == 0:
        return 0
    
    # Handle string dates
    if isinstance(start_ts, str):
        try:
            start_ts = datetime.strptime(start_ts, "%Y-%m-%d").timestamp()
        except:
            return 0
    
    if isinstance(end_ts, str):
        try:
            end_ts = datetime.strptime(end_ts, "%Y-%m-%d").timestamp()
        except:
            return 0
    
    # Handle numeric timestamps
    if isinstance(start_ts, (int, float)) and isinstance(end_ts, (int, float)):
        # Handle milliseconds
        if start_ts > 1e12:
            start_ts = start_ts / 1000
        if end_ts > 1e12:
            end_ts = end_ts / 1000
        
        try:
            start_date = datetime.fromtimestamp(start_ts, tz=timezone.utc)
            end_date = datetime.fromtimestamp(end_ts, tz=timezone.utc)
            return abs((end_date - start_date).days)
        except (ValueError, OSError):
            return 0
    
    return 0

def get_file_extension_from_url(url: str) -> str:
    """Extract file extension from URL"""
    if not url or url == "N/A":
        return '.jpg'
    
    parsed_url = urlparse(url)
    path = parsed_url.path
    
    # Get extension from path
    _, ext = os.path.splitext(path)
    if ext:
        return ext.lower()
    
    # Fallback: guess from content type
    try:
        response = requests.head(url, timeout=10)
        content_type = response.headers.get('content-type', '')
        ext = mimetypes.guess_extension(content_type.split(';')[0])
        return ext if ext else '.jpg'  # default fallback
    except:
        return '.jpg'  # default fallback

def download_media_file(url: str, filename: Optional[str] = None) -> Tuple[Optional[bytes], Optional[str]]:
    """Download media file from URL and return bytes"""
    if not url or url == "N/A":
        return None, None
    
    try:
        # Add headers to ensure proper download
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, timeout=30, headers=headers)
        response.raise_for_status()
        
        if not filename:
            # Generate filename from URL or use default
            parsed_url = urlparse(url)
            filename = os.path.basename(parsed_url.path)
            if not filename or '.' not in filename:
                ext = get_file_extension_from_url(url)
                filename = f"facebook_ad_media{ext}"
        
        return response.content, filename
    except requests.RequestException as e:
        st.error(f"Error downloading media: {str(e)}")
        return None, None

def get_proper_mime_type(file_data: bytes, filename: str) -> str:
    """Get proper MIME type for file download"""
    ext = os.path.splitext(filename)[1].lower()
    
    # Map extensions to MIME types for proper download behavior
    mime_map = {
        '.jpg': 'application/octet-stream',
        '.jpeg': 'application/octet-stream', 
        '.png': 'application/octet-stream',
        '.gif': 'application/octet-stream',
        '.webp': 'application/octet-stream',
        '.bmp': 'application/octet-stream',
        '.mp4': 'video/mp4',
        '.mov': 'video/quicktime',
        '.avi': 'video/x-msvideo',
        '.webm': 'video/webm'
    }
    
    # Use application/octet-stream for images to force download
    return mime_map.get(ext, 'application/octet-stream')

def create_download_button(media_url: str, ad_id: str, media_type: str = "image") -> None:
    """Create download button for ad media"""
    if not media_url or media_url == "N/A":
        st.warning("No media URL available for download")
        return
    
    # Determine file extension and name
    ext = get_file_extension_from_url(media_url)
    filename = f"facebook_ad_{ad_id}_{media_type}{ext}"
    
    # Create download button
    if st.button(f"📥 Download {media_type.title()}", key=f"download_{ad_id}_{media_type}"):
        with st.spinner(f"Downloading {media_type}..."):
            file_data, actual_filename = download_media_file(media_url, filename)
            
            if file_data:
                # Get proper MIME type to force download
                mime_type = get_proper_mime_type(file_data, actual_filename)
                
                # Create download link with forced download behavior
                st.download_button(
                    label=f"💾 Save {actual_filename}",
                    data=file_data,
                    file_name=actual_filename,
                    mime=mime_type,
                    key=f"save_{ad_id}_{media_type}",
                    use_container_width=True
                )
                st.success(f"{media_type.title()} ready for download!")
            else:
                st.error(f"Failed to download {media_type}")

def create_force_download_button(media_url: str, ad_id: str, media_type: str = "image") -> None:
    """Create download button that forces download using base64 encoding"""
    if not media_url or media_url == "N/A":
        st.warning("No media URL available for download")
        return
    
    # Determine file extension and name
    ext = get_file_extension_from_url(media_url)
    filename = f"facebook_ad_{ad_id}_{media_type}{ext}"
    
    # Create download button
    if st.button(f"📥 Download {media_type.title()}", key=f"download_{ad_id}_{media_type}"):
        with st.spinner(f"Downloading {media_type}..."):
            file_data, actual_filename = download_media_file(media_url, filename)
            
            if file_data:
                # Convert to base64 for guaranteed download
                b64_data = base64.b64encode(file_data).decode()
                
                # Create HTML download link that forces download
                href = f'data:application/octet-stream;base64,{b64_data}'
                
                st.markdown(f'''
                <a href="{href}" download="{actual_filename}">
                    <button style="
                        background-color: #4CAF50;
                        color: white;
                        padding: 10px 20px;
                        border: none;
                        border-radius: 5px;
                        cursor: pointer;
                        font-size: 16px;
                        width: 100%;
                        margin-top: 10px;
                    ">
                        💾 Click to Save {actual_filename}
                    </button>
                </a>
                ''', unsafe_allow_html=True)
                
                st.success(f"{media_type.title()} ready for download! Click the button above to save.")
            else:
                st.error(f"Failed to download {media_type}")

def direct_download_button(media_url: str, filename: str, media_type: str = "file") -> None:
    """Create a direct download button without pre-fetching"""
    if not media_url or media_url == "N/A":
        return
    
    st.markdown(f"""
    <a href="{media_url}" download="{filename}" target="_blank">
        <button style="
            background-color: #ff4b4b;
            color: white;
            padding: 0.5rem 1rem;
            border: none;
            border-radius: 0.25rem;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
        ">
            📥 Download {media_type.title()}
        </button>
    </a>
    """, unsafe_allow_html=True)

def format_ad_dates(item: dict) -> dict:
    """Format and calculate date information for an ad"""
    # Extract date fields
    start_date = item.get("Start_Date") or item.get("start_date") or item.get("startDate")
    end_date = item.get("End_Date") or item.get("end_date") or item.get("endDate")
    
    # Format dates
    formatted_start = format_date(start_date)
    formatted_end = format_date(end_date)
    
    # Calculate active days
    active_days = calculate_days(start_date, end_date)
    
    return {
        "start_date": formatted_start,
        "end_date": formatted_end,
        "active_days": active_days,
        "raw_start": start_date,
        "raw_end": end_date
    } 