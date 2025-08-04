from __future__ import annotations
import streamlit as st
import streamlit.components.v1 as components
import uuid
import logic
from typing import Optional, Dict, Any
from components.siderbar import _card_save_ui
from components.download_utils import format_ad_dates, create_download_button, create_force_download_button, direct_download_button

def extract_best_media(item):
    snap = logic._get_snapshot_dict(item)
    
    # Priority 1: Check for original_image_url first (as requested)
    if snap.get("original_image_url"):
        return "image", snap.get("original_image_url")
    
    # Priority 2: Check for video_hd_url in root
    if snap.get("video_hd_url"):
        return "video", snap.get("video_hd_url")
    
    # Priority 3: Check for original_picture_url in root
    if snap.get("original_picture_url"):
        return "image", snap.get("original_picture_url")
    
    # Priority 4: Check for original_image_url in extracted fields
    f = logic.extract_selected_fields(item)
    if f.get("original_image_url"):
        return "image", f.get("original_image_url")
    
    # Priority 5: Check for video_hd_url in videos list
    videos = snap.get("videos")
    if isinstance(videos, list):
        for v in videos:
            if isinstance(v, dict) and v.get("video_hd_url"):
                return "video", v.get("video_hd_url")
    
    # Priority 6: Check for original_picture_url in images list
    images = snap.get("images")
    if isinstance(images, list):
        for im in images:
            if isinstance(im, dict) and im.get("original_picture_url"):
                return "image", im.get("original_picture_url")
    
    # Priority 7: Check for original_image_url in images list
    if images and isinstance(images, list):
        for im in images:
            if isinstance(im, dict) and im.get("original_image_url"):
                return "image", im.get("original_image_url")
    
    # Priority 8: Other fallbacks
    if snap.get("video_url"):
        return "video", snap.get("video_url")
    
    if images and isinstance(images, list):
        for im in images:
            if isinstance(im, dict):
                for k in ("url", "src"):
                    if im.get(k):
                        return "image", im.get(k)
    
    # Priority 9: Fallback to logic.extract_primary_media
    media_type, media_url = logic.extract_primary_media(item)
    if media_url:
        return media_type, media_url
    
    # Priority 10: Final fallback to placeholder
    return "image", "https://via.placeholder.com/400x250/6366f1/ffffff?text=Ad+Preview"

def render_ad_card(item: Dict[str, Any], idx: int, variant: str, *, team: Optional[str] = None, raw_item: Optional[Dict[str, Any]] = None, image_url: Optional[str] = None, footer=None):
    f = logic.extract_selected_fields(item)

    # Core ad data
    page_name = f.get("page_name") or item.get("pageName") or item.get("Page_Name") or "(no page name)"
    ad_text = item.get("adText") or item.get("ad_text") or item.get("text") or ""
    short_text = logic.summarize_text(ad_text, 150)
    ad_archive_id = f.get("ad_archive_id") or item.get("adId") or item.get("id") or f"#{idx}"
    # --- Ensure Active is always boolean ---
    active_val = item.get("Active", f.get("is_active"))
    if isinstance(active_val, str):
        is_active = active_val.lower() == "true"
    else:
        is_active = bool(active_val)
    status = "Active" if is_active else "Inactive"
    running_days = logic.compute_running_days(item)

    # --- Improved date handling ---
    date_info = format_ad_dates(item)
    start_date = date_info["start_date"]
    end_date = date_info["end_date"]
    active_days = date_info["active_days"]

    # --- Robust media extraction ---
    # If image_url is provided as parameter, use it for images
    if image_url and image_url != "N/A":
        media_type, media_url = "image", image_url
    else:
        media_type, media_url = extract_best_media(item)
    
    # Debug: Log which image URL is being used (only in development)
    if st.session_state.get("debug_mode", False):
        st.caption(f"🔍 Image URL: {media_url[:50]}..." if media_url else "No image found")

    # Unique IDs for this card
    card_id = f"card_{idx}_{uuid.uuid4().hex[:6]}"
    modal_id = f"modal_{idx}_{uuid.uuid4().hex[:6]}"

    # Extract all requested fields with proper mapping
    page_id = item.get("Page_ID") or item.get("page_id") or item.get("pageId") or f.get("page_id") or "N/A"
    page_profile_url = item.get("Page_Profile_Url") or item.get("page_profile_url") or item.get("page_profile_uri") or f.get("page_profile_uri") or "N/A"
    page_profile_picture_url = item.get("Page_Profile_Picture_Url") or item.get("page_profile_picture_url") or f.get("page_profile_picture_url") or "N/A"
    link_url = item.get("Link_Url") or item.get("link_url") or f.get("link_url") or "N/A"
    cta_text = item.get("Cta_Text") or item.get("cta_text") or f.get("cta_text") or "N/A"
    cta_type = item.get("Cta_Type") or item.get("cta_type") or f.get("cta_type") or "N/A"
    state_media_run_label = item.get("State_Media_Run_Label") or item.get("state_media_run_label") or f.get("state_media_run_label") or "N/A"
    categories = item.get("Categories") or item.get("categories") or f.get("categories") or "N/A"
    collation_count = item.get("Collation_Count") or item.get("collation_count") or f.get("collation_count") or "N/A"
    entity_type = item.get("Entity_Type") or item.get("entity_type") or f.get("entity_type") or "N/A"
    political_countries = item.get("Political_Countries") or item.get("political_countries") or "N/A"
    publisher_platform = item.get("Publisher_Platform") or item.get("publisher_platform") or "Facebook"
    total_active_time = item.get("Total_Active_Time") or item.get("total_active_time") or f.get("total_active_time") or "N/A"
    ad_url = item.get("ad_Url") or item.get("ad_url") or "N/A"
    
    brand_initial = page_name[0].upper() if page_name and page_name != "(no page name)" else "?"

    # Generate media HTML based on type
    if media_type == "video":
        card_media_html = f'<video class="ad-card-video" controls><source src="{media_url}" type="video/mp4">Your browser does not support the video tag.</video>'
        modal_media_html = f'<video class="modal-video" controls><source src="{media_url}" type="video/mp4">Your browser does not support the video tag.</video>'
        video_overlay = '<div class="video-play-overlay">🎥 Video Ad</div>'
    else:
        # For images, ensure we have a valid URL and proper error handling
        if media_url and media_url != "N/A" and media_url.startswith(("http://", "https://")):
            card_media_html = f'<img src="{media_url}" class="ad-card-image" alt="Ad Image" onerror="this.src=\\"https://via.placeholder.com/400x250/6366f1/ffffff?text=Ad+Preview\\"">'
            modal_media_html = f'<img src="{media_url}" class="modal-image" alt="Ad Image" onerror="this.src=\\"https://via.placeholder.com/600x400/6366f1/ffffff?text=Ad+Preview\\"">'
        else:
            # Fallback to placeholder if no valid image URL
            card_media_html = f'<img src="https://via.placeholder.com/400x250/6366f1/ffffff?text=Ad+Preview" class="ad-card-image" alt="Ad Preview">'
            modal_media_html = f'<img src="https://via.placeholder.com/600x400/6366f1/ffffff?text=Ad+Preview" class="modal-image" alt="Ad Preview">'
        video_overlay = ''

    # Generate URL HTML
    ad_url_html = f'<a href="{ad_url}" target="_blank" class="clickable-url">Click to Open</a>' if ad_url != 'N/A' else 'N/A'
    link_url_html = f'<a href="{link_url}" target="_blank" class="clickable-url">Click to Open</a>' if link_url != 'N/A' else 'N/A'
    page_profile_url_html = f'<a href="{page_profile_url}" target="_blank" class="clickable-url">Click to Open</a>' if page_profile_url != 'N/A' else 'N/A'
    page_profile_picture_url_html = f'<a href="{page_profile_picture_url}" target="_blank" class="clickable-url">Click to Open</a>' if page_profile_picture_url != 'N/A' else 'N/A'

    # Generate action button visibility
    link_btn_style = 'style="display: none;"' if link_url == "N/A" else ''
    profile_btn_style = 'style="display: none;"' if page_profile_url == "N/A" else ''
    ad_btn_style = 'style="display: none;"' if ad_url == "N/A" else ''

    # Generate card HTML using full-page popup style
    components.html(f"""
    <style>
        .ad-card {{
            background: #23272f;
            border-radius: 18px;
            padding: 0;
            box-shadow: 0 6px 24px rgba(0,0,0,0.18);
            cursor: pointer;
            transition: box-shadow 0.3s, transform 0.3s;
            border: 1.5px solid #2d2d2d;
            overflow: hidden;
            height: 100%;
            display: flex;
            flex-direction: column;
            min-height: 420px;
        }}
        .ad-card:hover {{
            transform: translateY(-6px) scale(1.02);
            box-shadow: 0 16px 40px rgba(80,80,120,0.25);
            border-color: #6366f1;
        }}
        .ad-card-media {{
            width: 100%;
            height: 220px;
            position: relative;
            background: #181a20;
            overflow: hidden;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .ad-card-image, .ad-card-video {{
            width: 100%;
            height: 100%;
            object-fit: cover;
            object-position: center;
            border-radius: 0;
            transition: transform 0.3s;
        }}
        .ad-card-image:hover, .ad-card-video:hover {{
            transform: scale(1.04);
        }}
        .video-play-overlay {{
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: rgba(30,30,40,0.85);
            color: #fff;
            padding: 10px 18px;
            border-radius: 30px;
            font-size: 15px;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 8px;
            z-index: 2;
            box-shadow: 0 2px 8px rgba(0,0,0,0.18);
        }}
        .ad-card-content {{
            padding: 22px 20px 18px 20px;
            flex: 1;
            display: flex;
            flex-direction: column;
            min-height: 180px;
        }}
        .ad-card-header {{
            display: flex;
            align-items: center;
            margin-bottom: 14px;
        }}
        .ad-brand-icon {{
            width: 32px;
            height: 32px;
            border-radius: 8px;
            background: linear-gradient(135deg, #6366f1 0%, #764ba2 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            margin-right: 12px;
            font-size: 15px;
            flex-shrink: 0;
            box-shadow: 0 2px 8px rgba(99,102,241,0.12);
        }}
        .ad-page-name {{
            font-size: 17px;
            font-weight: 700;
            color: #f3f4f6;
            flex: 1;
            line-height: 1.3;
        }}
        .ad-card-body {{
            flex: 1;
            margin-bottom: 16px;
        }}
        .ad-card-text {{
            color: #d1d5db;
            font-size: 14px;
            line-height: 1.6;
            margin-bottom: 12px;
            display: -webkit-box;
            -webkit-line-clamp: 3;
            -webkit-box-orient: vertical;
            overflow: hidden;
            text-overflow: ellipsis;
        }}
        .ad-card-footer {{
            margin-top: auto;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}
        .ad-card-badges {{
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
        }}
        .ad-card-badge {{
            background: linear-gradient(135deg, #6366f1 0%, #764ba2 100%);
            color: white;
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .ad-card-badge-secondary {{
            background: linear-gradient(135deg, #6b7280 0%, #4b5563 100%);
        }}
        .ad-card-actions {{
            display: flex;
            gap: 8px;
        }}
        .ad-card-btn {{
            background: linear-gradient(135deg, #6366f1 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }}
        .ad-card-btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(99,102,241,0.3);
        }}
        .ad-card-btn.secondary {{
            background: linear-gradient(135deg, #6b7280 0%, #4b5563 100%);
        }}
        .ad-card-btn.secondary:hover {{
            box-shadow: 0 4px 12px rgba(107,114,128,0.3);
        }}
        
        /* Modal Styles */
        .ad-modal {{
            display: none;
            position: fixed;
            z-index: 10000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.8);
            backdrop-filter: blur(10px);
        }}
        .ad-modal-content {{
            background: white;
            margin: 2% auto;
            padding: 0;
            border-radius: 20px;
            width: 90%;
            max-width: 1400px;
            max-height: 90vh;
            overflow-y: auto;
            position: relative;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }}
        .ad-modal-close {{
            position: absolute;
            right: 20px;
            top: 20px;
            background: rgba(0,0,0,0.7);
            color: white;
            border: none;
            font-size: 28px;
            cursor: pointer;
            width: 40px;
            height: 40px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 10001;
            transition: all 0.3s ease;
        }}
        .ad-modal-close:hover {{
            background: rgba(0,0,0,0.9);
            transform: scale(1.1);
        }}
        .modal-header-section {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 40px 30px 40px;
            border-radius: 20px 20px 0 0;
            text-align: center;
        }}
        .modal-title {{
            font-size: 32px;
            font-weight: 700;
            margin: 0 0 10px 0;
            text-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .modal-status {{
            font-size: 18px;
            margin: 0 0 8px 0;
            font-weight: 600;
        }}
        .modal-subtitle {{
            font-size: 16px;
            opacity: 0.9;
            margin: 0;
        }}
        .modal-body-section {{
            padding: 40px;
            background: white;
        }}
        .modal-content-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 40px;
            margin-bottom: 40px;
        }}
        .modal-left-panel {{
            background: #f8fafc;
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }}
        .modal-right-panel {{
            background: white;
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            border: 1px solid #e0e0e0;
        }}
        .modal-media {{
            width: 100%;
            height: 400px;
            border-radius: 15px;
            margin-bottom: 30px;
            box-shadow: 0 8px 30px rgba(0,0,0,0.15);
            overflow: hidden;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .modal-image {{
            width: 100%;
            height: 100%;
            object-fit: cover;
            object-position: center;
        }}
        .modal-video {{
            width: 100%;
            height: 100%;
            object-fit: cover;
            object-position: center;
        }}
        .detail-section {{
            margin-bottom: 30px;
        }}
        .section-title {{
            font-size: 20px;
            font-weight: 700;
            color: #333;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 3px solid #667eea;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .detail-row {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px 0;
            border-bottom: 1px solid #f0f0f0;
            transition: background-color 0.2s ease;
        }}
        .detail-row:hover {{
            background-color: #f8f9fa;
            border-radius: 8px;
            padding-left: 10px;
            padding-right: 10px;
        }}
        .detail-row:last-child {{
            border-bottom: none;
        }}
        .detail-label {{
            font-size: 14px;
            color: #666;
            font-weight: 600;
            min-width: 150px;
        }}
        .detail-value {{
            font-size: 14px;
            color: #333;
            font-weight: 500;
            text-align: right;
            max-width: 250px;
            word-break: break-word;
        }}
        .clickable-url {{
            color: #667eea;
            text-decoration: none;
            font-weight: 600;
            cursor: pointer;
            transition: color 0.2s ease;
        }}
        .clickable-url:hover {{
            color: #764ba2;
            text-decoration: underline;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }}
        .stat-card {{
            background: white;
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            border: 1px solid #e0e0e0;
        }}
        .stat-number {{
            font-size: 24px;
            font-weight: 700;
            color: #667eea;
            display: block;
            margin-bottom: 5px;
        }}
        .stat-label {{
            font-size: 12px;
            color: #666;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .download-section {{
            background: #f8f9fa;
            border-radius: 15px;
            padding: 20px;
            margin-top: 20px;
            border: 1px solid #e9ecef;
        }}
        .download-title {{
            font-size: 18px;
            font-weight: 600;
            color: #333;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .download-buttons {{
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }}
        .download-btn {{
            background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            display: inline-flex;
            align-items: center;
            gap: 8px;
        }}
        .download-btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(40,167,69,0.3);
        }}
        .download-btn.video {{
            background: linear-gradient(135deg, #dc3545 0%, #c82333 100%);
        }}
        .download-btn.video:hover {{
            box-shadow: 0 4px 12px rgba(220,53,69,0.3);
        }}
        
        .action-buttons-section {{
            background: #f8f9fa;
            border-radius: 15px;
            padding: 20px;
            margin-top: 20px;
            border: 1px solid #e9ecef;
        }}
        .action-buttons {{
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            justify-content: center;
        }}
        .action-btn {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            display: inline-flex;
            align-items: center;
            gap: 8px;
        }}
        .action-btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(102,126,234,0.3);
        }}
        .action-btn.close-btn {{
            background: linear-gradient(135deg, #6c757d 0%, #495057 100%);
        }}
        .action-btn.close-btn:hover {{
            box-shadow: 0 4px 12px rgba(108,117,125,0.3);
        }}
        
        @media (max-width: 768px) {{
            .modal-content-grid {{
                grid-template-columns: 1fr;
                gap: 20px;
            }}
            .modal-body-section {{
                padding: 20px;
            }}
            .modal-header-section {{
                padding: 30px 20px 20px 20px;
            }}
            .modal-title {{
                font-size: 24px;
            }}
        }}
    </style>

    <div class="ad-card" onclick="openAdModal_{modal_id}()">
        <div class="ad-card-media">
            {card_media_html}
            {video_overlay}
        </div>
        <div class="ad-card-content">
            <div class="ad-card-header">
                <div class="ad-brand-icon">{brand_initial}</div>
                <div class="ad-page-name">{page_name}</div>
            </div>
            <div class="ad-card-body">
                <div class="ad-card-text">{short_text}</div>
            </div>
            <div class="ad-card-footer">
                <div class="ad-card-badges">
                    <span class="ad-card-badge">{status}</span>
                    <span class="ad-card-badge ad-card-badge-secondary">{running_days or '–'}D</span>
                </div>
                <div class="ad-card-actions">
                    <button class="ad-card-btn" onclick="event.stopPropagation(); openAdModal_{modal_id}()">
                        🔍 See Ad Details
                    </button>
                </div>
            </div>
        </div>
    </div>

    <div id="adModal{modal_id}" class="ad-modal">
        <div class="ad-modal-content">
            <button class="ad-modal-close" onclick="closeAdModal_{modal_id}()">&times;</button>
            
            <div class="modal-header-section">
                <h1 class="modal-title">{page_name}</h1>
                <p class="modal-status" style="color: {'#22c55e' if is_active else '#ef4444'}; font-weight: bold;">
                    Status: {status}
                </p>
                <p class="modal-subtitle">Ad ID: {ad_archive_id} | Platform: {publisher_platform}</p>
            </div>
            
            <div class="modal-body-section">
                <div class="modal-content-grid">
                    <div class="modal-left-panel">
                        <div class="modal-media">
                            {modal_media_html}
                        </div>
                        
                        <div class="detail-section">
                            <div class="section-title">📝 Ad Content</div>
                            <p style="color: #666; line-height: 1.8; font-size: 16px; margin: 0;">
                                {ad_text if ad_text.strip() else 'No ad text available'}
                            </p>
                        </div>
                        
                        <div class="stats-grid">
                            <div class="stat-card">
                                <span class="stat-number">{running_days or 'N/A'}</span>
                                <div class="stat-label">Days Running</div>
                            </div>
                            <div class="stat-card">
                                <span class="stat-number">{collation_count}</span>
                                <div class="stat-label">Collations</div>
                            </div>
                            <div class="stat-card">
                                <span class="stat-number">{active_days}</span>
                                <div class="stat-label">Active Days</div>
                            </div>
                        </div>
                        
                        <!-- Download Section -->
                        <div class="download-section">
                            <div class="download-title">📥 Download Media</div>
                            <div class="download-buttons">
                                <button class="download-btn" onclick="downloadMedia_{modal_id}('{media_url}', '{ad_archive_id}', '{media_type}')">
                                    📥 Download {media_type.title()}
                                </button>
                            </div>
                        </div>
                    </div>
                    
                    <div class="modal-right-panel">
                        <div class="detail-section">
                            <div class="section-title">🔍 Basic Information</div>
                            <div class="detail-row">
                                <span class="detail-label">Page ID</span>
                                <span class="detail-value">{page_id}</span>
                            </div>
                            <div class="detail-row">
                                <span class="detail-label">Page Name</span>
                                <span class="detail-value">{page_name}</span>
                            </div>
                            <div class="detail-row">
                                <span class="detail-label">Ad ID</span>
                                <span class="detail-value">{ad_archive_id}</span>
                            </div>
                            <div class="detail-row">
                                <span class="detail-label">Active Status</span>
                                <span class="detail-value" style="color: {'#22c55e' if is_active else '#ef4444'}; font-weight: bold;">{status}</span>
                            </div>
                        </div>

                        <div class="detail-section">
                            <div class="section-title">📅 Campaign Dates</div>
                            <div class="detail-row">
                                <span class="detail-label">Start Date</span>
                                <span class="detail-value">{start_date}</span>
                            </div>
                            <div class="detail-row">
                                <span class="detail-label">End Date</span>
                                <span class="detail-value">{end_date}</span>
                            </div>
                            <div class="detail-row">
                                <span class="detail-label">Active Days</span>
                                <span class="detail-value">{active_days}</span>
                            </div>
                            <div class="detail-row">
                                <span class="detail-label">Total Active Time</span>
                                <span class="detail-value">{total_active_time}</span>
                            </div>
                        </div>

                        <div class="detail-section">
                            <div class="section-title">🔗 URLs & Links</div>
                            <div class="detail-row">
                                <span class="detail-label">Ad URL</span>
                                <span class="detail-value">{ad_url_html}</span>
                            </div>
                            <div class="detail-row">
                                <span class="detail-label">Link URL</span>
                                <span class="detail-value">{link_url_html}</span>
                            </div>
                            <div class="detail-row">
                                <span class="detail-label">Page Profile URL</span>
                                <span class="detail-value">{page_profile_url_html}</span>
                            </div>
                            <div class="detail-row">
                                <span class="detail-label">Page Profile Picture URL</span>
                                <span class="detail-value">{page_profile_picture_url_html}</span>
                            </div>
                        </div>

                        <div class="detail-section">
                            <div class="section-title">🎯 Campaign Details</div>
                            <div class="detail-row">
                                <span class="detail-label">CTA Text</span>
                                <span class="detail-value">{cta_text}</span>
                            </div>
                            <div class="detail-row">
                                <span class="detail-label">CTA Type</span>
                                <span class="detail-value">{cta_type}</span>
                            </div>
                            <div class="detail-row">
                                <span class="detail-label">Categories</span>
                                <span class="detail-value">{categories}</span>
                </div>
                            <div class="detail-row">
                                <span class="detail-label">Entity Type</span>
                                <span class="detail-value">{entity_type}</span>
                    </div>
                    </div>

                        <div class="detail-section">
                            <div class="section-title">📊 Platform & Analytics</div>
                            <div class="detail-row">
                                <span class="detail-label">Publisher Platform</span>
                                <span class="detail-value">{publisher_platform}</span>
                    </div>
                            <div class="detail-row">
                                <span class="detail-label">Collation Count</span>
                                <span class="detail-value">{collation_count}</span>
                    </div>
                            <div class="detail-row">
                                <span class="detail-label">State Media Run Label</span>
                                <span class="detail-value">{state_media_run_label}</span>
                    </div>
                            <div class="detail-row">
                                <span class="detail-label">Political Countries</span>
                                <span class="detail-value">{political_countries}</span>
                    </div>
                    </div>
                    </div>
                    </div>
                
                <div class="action-buttons-section">
                    <div class="action-buttons">
                        <button class="action-btn" onclick="window.open('{link_url}', '_blank')" {link_btn_style}>
                            🔗 Visit Landing Page
                        </button>
                        <button class="action-btn" onclick="window.open('{page_profile_url}', '_blank')" {profile_btn_style}>
                            👤 View Page Profile
                        </button>
                        <button class="action-btn" onclick="window.open('{ad_url}', '_blank')" {ad_btn_style}>
                            📺 View Ad
                        </button>
                        <button class="action-btn close-btn" onclick="closeAdModal_{modal_id}()">
                            ❌ Close Details
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        function openAdModal_{modal_id}() {{
            document.getElementById('adModal{modal_id}').style.display = 'block';
            document.body.style.overflow = 'hidden';
        }}
        function closeAdModal_{modal_id}() {{
            document.getElementById('adModal{modal_id}').style.display = 'none';
            document.body.style.overflow = 'auto';
        }}
        document.getElementById('adModal{modal_id}').onclick = function(event) {{
            const modal = document.getElementById('adModal{modal_id}');
            const content = modal.querySelector('.ad-modal-content');
            if (!content.contains(event.target)) {{
                closeAdModal_{modal_id}();
            }}
        }}
        document.addEventListener('keydown', function(event) {{
            if (event.key === 'Escape') {{
                closeAdModal_{modal_id}();
            }}
        }});
        
        function downloadMedia_{modal_id}(mediaUrl, adId, mediaType) {{
            if (!mediaUrl || mediaUrl === 'N/A') {{
                alert('No media URL available for download');
                return;
            }}
            
            // Show loading state
            const downloadBtn = event.target;
            const originalText = downloadBtn.innerHTML;
            downloadBtn.innerHTML = '⏳ Downloading...';
            downloadBtn.disabled = true;
            
            // Fetch the file with proper headers
            fetch(mediaUrl, {{
                method: 'GET',
                headers: {{
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }}
            }})
            .then(response => response.blob())
            .then(blob => {{
                // Create blob URL for download
                const blobUrl = window.URL.createObjectURL(blob);
                
                // Determine file extension
                let extension = '.jpg';
                if (mediaType === 'video') {{
                    extension = '.mp4';
                }} else if (mediaUrl.includes('.png')) {{
                    extension = '.png';
                }} else if (mediaUrl.includes('.gif')) {{
                    extension = '.gif';
                }} else if (mediaUrl.includes('.webp')) {{
                    extension = '.webp';
                }}
                
                // Create download link
                const link = document.createElement('a');
                link.href = blobUrl;
                link.download = `facebook_ad_${{adId}}_${{mediaType}}${{extension}}`;
                link.style.display = 'none';
                
                // Trigger download
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
                
                // Clean up blob URL
                window.URL.revokeObjectURL(blobUrl);
                
                // Show success message
                downloadBtn.innerHTML = '✅ Downloaded!';
                downloadBtn.style.background = 'linear-gradient(135deg, #28a745 0%, #20c997 100%)';
                
                setTimeout(() => {{
                    downloadBtn.innerHTML = originalText;
                    downloadBtn.style.background = 'linear-gradient(135deg, #28a745 0%, #20c997 100%)';
                    downloadBtn.disabled = false;
                }}, 2000);
            }})
            .catch(error => {{
                console.error('Download failed:', error);
                alert('Download failed. Please try again.');
                downloadBtn.innerHTML = originalText;
                downloadBtn.disabled = false;
            }});
        }}
    </script>
    """, height=450)

    # Optional Save UI for search variant
    if variant == "search":
        if st.button("💾 Save Ad", key=f"save_{idx}", use_container_width=True, type="secondary"):
            st.session_state["save_pending_idx"] = idx
        
        if st.session_state.get("save_pending_idx") == idx:
            _card_save_ui(idx, f, raw_item or item)