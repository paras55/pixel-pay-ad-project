#!/usr/bin/env python3
"""
app.py — FB Ads Explorer (Streamlit) w/ SQLite saved teams.

Modes:
  • Search Ads  – scrape via Apify, view, save.
  • Saved Ads   – browse ads saved in team1/team2/team3.

This file coordinates page config, mode switching, data fetch, and delegating
UI rendering to ui.py. Database helpers live in logic.py.
"""

from __future__ import annotations
import streamlit as st
import ui
import logic
from datetime import datetime

from components.dbtoItem import _db_row_to_item
from ui import render_main_search_page
from components.mainSearchPage import render_main_search_page

# -----------------------------------------------------------------------------
# Config
# -----------------------------------------------------------------------------
st.set_page_config(page_title="Facebook Ads Extractor", layout="wide")
ui.inject_global_css()
logic.init_db()

# -----------------------------------------------------------------------------
# Professional Dark Theme Styling
# -----------------------------------------------------------------------------
st.markdown("""
<style>
/* Import Inter font */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

/* Dark Theme Variables */
:root {
    --primary-bg: #0f0f23;
    --secondary-bg: #1a1a2e;
    --tertiary-bg: #16213e;
    --card-bg: #1e1e3f;
    --border-color: #2d2d5a;
    --text-primary: #ffffff;
    --text-secondary: #a0a0c0;
    --text-muted: #6b6b8a;
    --accent-primary: #6366f1;
    --accent-secondary: #8b5cf6;
    --success-color: #10b981;
    --warning-color: #f59e0b;
    --error-color: #ef4444;
    --shadow-light: 0 2px 8px rgba(0,0,0,0.3);
    --shadow-medium: 0 4px 16px rgba(0,0,0,0.4);
    --shadow-heavy: 0 8px 32px rgba(0,0,0,0.5);
}

/* Global Styles */
* {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

/* Main Background */
.main .block-container {
    background: var(--primary-bg);
    padding-top: 0;
    padding-bottom: 0;
    max-width: 1200px;
    margin: 0 auto;
    color: var(--text-primary);
}

/* Hide Streamlit elements */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Professional Header */
.main-header {
    background: linear-gradient(135deg, var(--secondary-bg) 0%, var(--tertiary-bg) 50%, var(--accent-primary) 100%);
    padding: 40px 0;
    margin: -1rem -1rem 32px -1rem;
    text-align: center;
    position: relative;
    overflow: hidden;
    border-bottom: 1px solid var(--border-color);
}

.main-header::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(45deg, rgba(26,26,46,0.9) 0%, rgba(22,33,62,0.9) 50%, rgba(99,102,241,0.1) 100%);
    backdrop-filter: blur(10px);
}

.main-title {
    font-size: 28px;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 4px;
    position: relative;
    z-index: 1;
    letter-spacing: -0.5px;
}

.main-subtitle {
    font-size: 14px;
    color: var(--text-secondary);
    font-weight: 400;
    position: relative;
    z-index: 1;
}

/* Mode Selector */
.mode-selector {
    background: var(--card-bg);
    border: 1px solid var(--border-color);
    border-radius: 16px;
    padding: 24px;
    margin: 0 auto 32px auto;
    max-width: 1200px;
    text-align: center;
    box-shadow: var(--shadow-medium);
}

.mode-tab {
    display: inline-block;
    padding: 12px 24px;
    margin: 0 6px;
    border-radius: 20px;
    cursor: pointer;
    transition: all 0.3s ease-in-out;
    font-weight: 500;
    font-size: 14px;
    border: 1px solid var(--border-color);
    background: var(--secondary-bg);
    color: var(--text-secondary);
}

.mode-tab.active {
    background: linear-gradient(135deg, var(--accent-primary) 0%, var(--accent-secondary) 100%);
    color: var(--text-primary);
    box-shadow: var(--shadow-medium);
    transform: translateY(-1px);
    border-color: var(--accent-primary);
}

.mode-tab:not(.active):hover {
    background: var(--tertiary-bg);
    color: var(--text-primary);
    transform: translateY(-1px);
    border-color: var(--accent-primary);
}

/* Search Container */
.search-container {
    background: var(--card-bg);
    border: 1px solid var(--border-color);
    border-radius: 16px;
    padding: 32px;
    margin: 0 auto 32px auto;
    max-width: 1200px;
    box-shadow: var(--shadow-medium);
}

/* Step Indicators */
.search-step {
    background: linear-gradient(135deg, var(--accent-primary) 0%, var(--accent-secondary) 100%);
    color: var(--text-primary);
    padding: 20px 32px;
    border-radius: 12px;
    margin-bottom: 32px;
    font-weight: 600;
    font-size: 16px;
    text-align: center;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    box-shadow: var(--shadow-medium);
}

/* Search Type Cards */
.search-type-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 24px;
    margin-bottom: 32px;
}

.search-type-card {
    background: var(--card-bg);
    border: 1px solid var(--border-color);
    border-radius: 16px;
    padding: 32px;
    text-align: center;
    cursor: pointer;
    transition: all 0.3s ease-in-out;
    box-shadow: var(--shadow-light);
}

.search-type-card:hover {
    border-color: var(--accent-primary);
    transform: translateY(-2px);
    box-shadow: var(--shadow-heavy);
    background: var(--secondary-bg);
}

.search-type-card.selected {
    border-color: var(--accent-primary);
    background: linear-gradient(135deg, rgba(99,102,241,0.1) 0%, rgba(139,92,246,0.1) 100%);
    box-shadow: var(--shadow-heavy);
}

.search-type-icon {
    font-size: 32px;
    margin-bottom: 16px;
    color: var(--accent-primary);
}

.search-type-title {
    font-size: 16px;
    font-weight: 600;
    margin-bottom: 8px;
    color: var(--text-primary);
}

.search-type-desc {
    font-size: 13px;
    color: var(--text-secondary);
    line-height: 1.5;
}

/* Dynamic Form */
.dynamic-form {
    background: var(--card-bg);
    border: 1px solid var(--border-color);
    border-radius: 16px;
    padding: 32px;
    margin-top: 24px;
    border-left: 3px solid var(--accent-primary);
}

/* Form Elements */
.stSelectbox, .stTextInput, .stNumberInput {
    background: var(--secondary-bg) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 8px !important;
    color: var(--text-primary) !important;
    font-size: 14px !important;
    font-weight: 400 !important;
    padding: 12px 16px !important;
    height: 44px !important;
    transition: all 0.2s ease !important;
    width: 100% !important;
    margin-bottom: 8px !important;
}

.stSelectbox:focus, .stTextInput:focus, .stNumberInput:focus {
    border-color: var(--accent-primary) !important;
    box-shadow: 0 0 0 2px rgba(99,102,241,0.2) !important;
    outline: none !important;
    background: var(--tertiary-bg) !important;
}

.stSelectbox option {
    background: var(--secondary-bg) !important;
    color: var(--text-primary) !important;
}

/* Labels */
.stSelectbox label, .stTextInput label, .stNumberInput label {
    color: var(--text-secondary) !important;
    font-weight: 500 !important;
    font-size: 13px !important;
    text-transform: capitalize !important;
    margin-bottom: 6px !important;
    display: block !important;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, var(--accent-primary) 0%, var(--accent-secondary) 100%) !important;
    color: var(--text-primary) !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 12px 24px !important;
    font-size: 14px !important;
    font-weight: 600 !important;
    height: 44px !important;
    transition: all 0.2s ease !important;
    box-shadow: var(--shadow-light) !important;
    min-width: 120px !important;
}

.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: var(--shadow-medium) !important;
    background: linear-gradient(135deg, var(--accent-secondary) 0%, var(--accent-primary) 100%) !important;
}

.stButton > button:active {
    transform: scale(0.98) !important;
}

/* Info Messages */
.stAlert {
    background: var(--secondary-bg) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 8px !important;
    color: var(--text-secondary) !important;
    padding: 16px !important;
    font-size: 14px !important;
    margin-top: 8px !important;
    margin-bottom: 16px !important;
}

/* Success/Error Messages */
.success-message {
    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
    color: #FFFFFF;
    padding: 20px 32px;
    border-radius: 12px;
    margin-bottom: 24px;
    font-weight: 600;
    text-align: center;
    box-shadow: 0 4px 20px rgba(16,185,129,0.3);
}

.warning-message {
    background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
    color: #FFFFFF;
    padding: 20px 32px;
    border-radius: 12px;
    margin-bottom: 24px;
    font-weight: 600;
    text-align: center;
    box-shadow: 0 4px 20px rgba(239,68,68,0.3);
}

/* Results Summary */
.results-summary {
    background: linear-gradient(135deg, rgba(76,139,245,0.1) 0%, rgba(59,130,246,0.1) 100%);
    color: #E5E7EB;
    padding: 20px 32px;
    border-radius: 12px;
    margin-bottom: 24px;
    font-weight: 600;
    text-align: center;
    box-shadow: 0 4px 20px rgba(76,139,245,0.2);
    border: 1px solid rgba(76,139,245,0.2);
}

/* Filter Tags */
.filter-tag {
    background: linear-gradient(135deg, #4c8bf5 0%, #3b82f6 100%);
    color: #FFFFFF;
    padding: 8px 16px;
    border-radius: 16px;
    font-size: 12px;
    display: inline-flex;
    align-items: center;
    gap: 8px;
    margin-right: 12px;
    margin-bottom: 12px;
    box-shadow: 0 2px 8px rgba(76,139,245,0.3);
}

/* Radio Buttons */
.stRadio > div {
    background: #1e1f23 !important;
    border: 1px solid #2a2b2f !important;
    border-radius: 8px !important;
    padding: 16px !important;
    margin-bottom: 8px !important;
}

.stRadio > div > label {
    color: #E5E7EB !important;
    font-weight: 500 !important;
}

/* Expander */
.streamlit-expanderHeader {
    background: #1e1f23 !important;
    border: 1px solid #2a2b2f !important;
    border-radius: 8px !important;
    color: #E5E7EB !important;
    font-weight: 500 !important;
    padding: 16px !important;
}

.streamlit-expanderContent {
    background: #1e1f23 !important;
    border: 1px solid #2a2b2f !important;
    border-radius: 8px !important;
    color: #9CA3AF !important;
    padding: 16px !important;
}

/* Responsive Design */
@media (max-width: 768px) {
    .main-title {
        font-size: 24px;
    }
    
    .search-container {
        padding: 24px;
        margin: 0 16px 24px 16px;
    }
    
    .search-type-grid {
        grid-template-columns: 1fr;
    }
    
    .mode-tab {
        padding: 10px 20px;
        font-size: 13px;
    }
}

/* Loading Animation */
@keyframes pulse {
    0% { opacity: 1; }
    50% { opacity: 0.5; }
    100% { opacity: 1; }
}

.stSpinner > div {
    animation: pulse 1.5s ease-in-out infinite;
}

/* Focus Accessibility */
*:focus {
    outline: 2px solid #4c8bf5 !important;
    outline-offset: 2px !important;
}

/* Scrollbar Styling */
::-webkit-scrollbar {
    width: 6px;
}

::-webkit-scrollbar-track {
    background: #1e1f23;
}

::-webkit-scrollbar-thumb {
    background: linear-gradient(135deg, #4c8bf5 0%, #3b82f6 100%);
    border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
}

/* Better spacing and alignment */
.element-container {
    margin-bottom: 20px !important;
}

.row-widget.stHorizontal {
    gap: 20px !important;
}

/* Center content properly */
.main .block-container {
    padding-left: 2rem;
    padding-right: 2rem;
}

/* Better column spacing */
[data-testid="column"] {
    padding: 0 10px;
}

/* Form group spacing */
.form-group {
    margin-bottom: 20px;
}

/* Button container */
.button-container {
    text-align: center;
    margin-top: 24px;
    margin-bottom: 16px;
}

/* Info box spacing */
.info-box {
    margin: 16px 0;
    padding: 16px;
    background: #1e1f23;
    border-radius: 8px;
    border: 1px solid #2a2b2f;
    color: #9CA3AF;
}

/* Dashboard-style cards */
.dashboard-card {
    background: #1e1f23;
    border: 1px solid #2a2b2f;
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 20px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.2);
}

/* Glow effects for interactive elements */
.glow-effect {
    transition: all 0.3s ease-in-out;
}

.glow-effect:hover {
    box-shadow: 0 0 20px rgba(76,139,245,0.3);
}

/* Modern input styling */
.modern-input {
    background: #1e1f23 !important;
    border: 1px solid #2a2b2f !important;
    border-radius: 8px !important;
    color: #FFFFFF !important;
    transition: all 0.3s ease-in-out !important;
}

.modern-input:focus {
    border-color: #4c8bf5 !important;
    box-shadow: 0 0 0 2px rgba(76,139,245,0.2) !important;
    background: #2a2b2f !important;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Main Header
# -----------------------------------------------------------------------------
st.markdown("""
<div class="main-header">
    <div class="main-title">Facebook Ads Extractor</div>
    <div class="main-subtitle">by PixelPay Media</div>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Mode Selector
# -----------------------------------------------------------------------------
st.markdown('<div class="mode-selector">', unsafe_allow_html=True)
mode = st.radio("", ["Search Ads", "Saved Ads"], horizontal=True, key="app_mode_radio", label_visibility="collapsed")
st.markdown('</div>', unsafe_allow_html=True)

# Clear session state when switching between modes
if st.session_state.get("_last_mode") and st.session_state["_last_mode"] != mode:
    st.session_state.pop("selected_ad_idx", None)
    st.session_state.pop("save_pending_idx", None)
    for t in logic.TEAM_TABLES:
        st.session_state.pop(f"saved_selected_idx_{t}", None)
st.session_state["_last_mode"] = mode

# -----------------------------------------------------------------------------
# SEARCH MODE - Modern SaaS Dashboard
# -----------------------------------------------------------------------------
if mode == "Search Ads":
    if "search_mode" not in st.session_state:
        st.session_state["search_mode"] = None

    # Step 1: Search Type Selection
    st.markdown('<div class="search-step">Step 1: Choose Search Type</div>', unsafe_allow_html=True)
    
    # Search type cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔍 Keyword Search", key="keyword_btn", use_container_width=True):
            st.session_state["search_mode"] = "Keyword Search"
            st.rerun()
    
    with col2:
        if st.button("📄 Page ID Search", key="page_id_btn", use_container_width=True):
            st.session_state["search_mode"] = "Page ID Search"
            st.rerun()
    
    with col3:
        if st.button("🌐 Landing Domain Search", key="domain_btn", use_container_width=True):
            st.session_state["search_mode"] = "Landing Page Domain Search"
            st.rerun()

    # Step 2: Dynamic Form Based on Search Type
    if st.session_state["search_mode"]:
        st.markdown(f'<div class="search-step">Step 2: Configure {st.session_state["search_mode"]}</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="dynamic-form">', unsafe_allow_html=True)
        
        # Common parameters - First row
        col1, col2 = st.columns(2)
        
        with col1:
            # Country selector
            country_labels = [n for n, _ in logic.COMMON_COUNTRIES] + ["Custom…"]
            country_label_sel = st.selectbox("🌍 Country", options=country_labels, index=0, key="search_country_sel")
            if country_label_sel == "Custom…":
                country_code = st.text_input("ISO country code", value="", key="search_country_custom").strip().upper() or "US"
                country_label = country_code
            else:
                country_code = dict(logic.COMMON_COUNTRIES)[country_label_sel]
                country_label = country_label_sel
        
        with col2:
            # Number of ads
            count = st.number_input("📊 Number of Ads", min_value=1, max_value=1000, value=10, step=1, key="search_count")
        
        # Search type specific inputs - Second row
        if st.session_state["search_mode"] == "Keyword Search":
            user_input = st.text_input("🔍 Keyword", placeholder="Enter keyword (e.g. auto insurance)", key="search_keyword_input")
            st.markdown('<div class="info-box">💡 Enter keywords to search for ads containing specific terms</div>', unsafe_allow_html=True)
            
        elif st.session_state["search_mode"] == "Page ID Search":
            user_input = st.text_input("📄 Page ID", placeholder="Enter Facebook Page ID (e.g. 113923695147163)", key="search_page_id_input")
            st.markdown('<div class="info-box">💡 Enter the Facebook Page ID to find all ads from that specific page</div>', unsafe_allow_html=True)
            
        elif st.session_state["search_mode"] == "Landing Page Domain Search":
            user_input = st.text_input("🌐 Domain", placeholder="Enter domain (e.g. example.com)", key="search_domain_input")
            st.markdown('<div class="info-box">💡 Enter a domain to find ads that link to that website</div>', unsafe_allow_html=True)
        
        # Additional filters - Third row
        col3, col4 = st.columns(2)
        
        with col3:
            # Ad category selector
            ad_category_label = st.selectbox(
                "📋 Ad Category", 
                options=list(logic.CATEGORY_LABEL_TO_ADTYPE.keys()), 
                index=0, 
                key="search_category"
            )
            ad_type_param = logic.CATEGORY_LABEL_TO_ADTYPE[ad_category_label]
        
        with col4:
            # Active status filter
            active_status_label = st.selectbox(
                "⚡ Active Status", 
                options=list(logic.ACTIVE_STATUS_LABEL_TO_PARAM.keys()), 
                index=0, 
                key="search_status"
            )
            active_status_param = logic.ACTIVE_STATUS_LABEL_TO_PARAM[active_status_label]
        
        # Search button - Fourth row
        st.markdown('<div class="button-container">', unsafe_allow_html=True)
        fetch_clicked = st.button("🚀 Start Search", type="primary", key="search_fetch_btn", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

        # Main: Fetch and display ads
        if fetch_clicked:
            # Validation
            if not user_input.strip():
                st.error("❌ Please enter a search term!")
                st.stop()
            
            # Get Apify token from backend
            apify_token = logic.resolve_apify_token()
            if not apify_token:
                st.error("❌ Apify API token not configured. Please set APIFY_TOKEN in your environment variables or Streamlit secrets.")
                st.stop()

            # Build correct URL based on search mode
            if st.session_state["search_mode"] == "Keyword Search":
                url = logic.build_fb_ads_library_url(
                    country=country_code,
                    keyword=user_input,
                    ad_type=ad_type_param,
                    active_status=active_status_param,
                    search_mode="keyword_unordered",
                )
            elif st.session_state["search_mode"] == "Page ID Search":
                # For page ID search, we use fixed parameters as per the exact format
                url = logic.build_fb_ads_library_url(
                    country="ALL",  # Always use ALL for page ID search
                    page_id=user_input,
                    ad_type="all",  # Always use all for page ID search
                    active_status="all",  # Always use all for page ID search
                    search_mode="page_id",
                )
            elif st.session_state["search_mode"] == "Landing Page Domain Search":
                # For landing domain search, we use fixed parameters as per the exact format
                url = logic.build_fb_ads_library_url(
                    country=country_code,  # Use user-selected country
                    landing_domain=user_input,
                    ad_type="all",  # Always use all for landing domain search
                    active_status="active",  # Always use active for landing domain search
                    search_mode="landing_domain",
                )
            else:
                st.error("❌ Unknown search mode selected.")
                st.stop()

            st.session_state["last_query_url"] = url
            st.session_state["last_query_params"] = {
                "country_code": country_code,
                "country_label": country_label,
                "user_input": user_input,
                "ad_type_param": ad_type_param,
                "active_status_param": active_status_param,
                "count": count,
                "search_mode": st.session_state["search_mode"],
            }
            
            # Debug: Show the request format being sent
            request_format = {
                "count": int(count),
                "scrapeAdDetails": True,
                "scrapePageAds.activeStatus": active_status_param,
                "urls": [
                    {
                        "url": url,
                        "method": "GET"
                    }
                ],
                "period": ""
            }
            st.session_state["last_request_format"] = request_format

            with st.spinner(f"🔍 Running Apify scrape for {count} ads…"):
                try:
                    items = logic.run_apify_scrape(
                        apify_token,
                        url,
                        int(count),
                        active_status_param,
                    )
                except Exception as e:
                    st.error(f"❌ Apify scrape failed: {e}")
                    st.stop()

            st.session_state["ads_items"] = items
            st.session_state["search_timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.session_state.pop("selected_ad_idx", None)
            st.session_state.pop("save_pending_idx", None)
            
            # Show success message with search details
            if items:
                if st.session_state["search_mode"] == "Page ID Search":
                    st.markdown(f'<div class="success-message">✅ Successfully retrieved {len(items)} ads from Page ID: {user_input}!</div>', unsafe_allow_html=True)
                elif st.session_state["search_mode"] == "Landing Page Domain Search":
                    st.markdown(f'<div class="success-message">✅ Successfully retrieved {len(items)} ads for domain: {user_input}!</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="success-message">✅ Successfully retrieved {len(items)} ads for keyword: {user_input}!</div>', unsafe_allow_html=True)
            else:
                if st.session_state["search_mode"] == "Page ID Search":
                    st.markdown(f'<div class="warning-message">⚠️ No ads found for Page ID: {user_input}. Please verify the Page ID is correct.</div>', unsafe_allow_html=True)
                elif st.session_state["search_mode"] == "Landing Page Domain Search":
                    st.markdown(f'<div class="warning-message">⚠️ No ads found for domain: {user_input}. Please verify the domain is correct.</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="warning-message">⚠️ No ads found for keyword: {user_input}. Try a different search term.</div>', unsafe_allow_html=True)

    # Render main results
    params = st.session_state.get("last_query_params")
    ads_items = st.session_state.get("ads_items", [])

    if ads_items:
        render_main_search_page(ads_items, params, card_image_key="original_image_url")


# -----------------------------------------------------------------------------
# SAVED MODE
# -----------------------------------------------------------------------------
else:
    st.markdown('<div class="search-container">', unsafe_allow_html=True)
    st.markdown('<div class="search-step">Saved Ads</div>', unsafe_allow_html=True)
    
    # Get all available teams (default + custom)
    all_teams = logic.get_all_teams()
    
    # Check if we have a newly created team to select
    newly_created_team = st.session_state.get("newly_created_team")
    default_index = 0
    if newly_created_team and newly_created_team in all_teams:
        default_index = all_teams.index(newly_created_team) + 1  # +1 because "(choose)" is at index 0
        # Clear the session state after using it
        st.session_state.pop("newly_created_team", None)
    
    # Check if we need to reset team selection (after deletion)
    if st.session_state.get("reset_team_selection", False):
        default_index = 0  # Reset to "(choose)"
        st.session_state.pop("reset_team_selection", None)
    
    # Add Team functionality
    col1, col2 = st.columns([3, 1])
    
    with col1:
        team_choice = st.selectbox(
            "📁 Select Team",
            options=["(choose)"] + all_teams,
            index=default_index,
            key="saved_team_sel",
        )
    
    with col2:
        if st.button("➕ Add Team", key="add_team_btn", use_container_width=True):
            st.session_state["show_add_team"] = True
    
    # Delete Team functionality
    if team_choice and team_choice != "(choose)" and logic.is_custom_team(team_choice):
        col3, col4 = st.columns([3, 1])
        with col4:
            if st.button("🗑️ Delete Team", key="delete_team_btn", use_container_width=True, type="secondary"):
                st.session_state["show_delete_team"] = True
                st.session_state["team_to_delete"] = team_choice
    
    # Delete Team Confirmation
    if st.session_state.get("show_delete_team", False):
        team_to_delete = st.session_state.get("team_to_delete")
        if team_to_delete:
            st.markdown('<div class="dynamic-form">', unsafe_allow_html=True)
            st.markdown(f'<div class="search-step">Delete Team: {team_to_delete}</div>', unsafe_allow_html=True)
            
            st.warning(f"⚠️ Are you sure you want to delete team '{team_to_delete}'? This action cannot be undone and will permanently remove all saved ads in this team.")
            
            col5, col6 = st.columns(2)
            
            with col5:
                if st.button("🗑️ Yes, Delete Team", key="confirm_delete_team_btn", use_container_width=True, type="secondary"):
                    try:
                        if logic.delete_custom_team(team_to_delete):
                            st.success(f"✅ Team '{team_to_delete}' deleted successfully!")
                            st.session_state["show_delete_team"] = False
                            st.session_state["team_to_delete"] = None
                            st.session_state["reset_team_selection"] = True
                            st.rerun()
                        else:
                            st.error(f"❌ Failed to delete team '{team_to_delete}'")
                    except ValueError as e:
                        st.error(f"❌ {str(e)}")
            
            with col6:
                if st.button("❌ Cancel", key="cancel_delete_team_btn", use_container_width=True):
                    st.session_state["show_delete_team"] = False
                    st.session_state["team_to_delete"] = None
                    st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Add Team Form
    if st.session_state.get("show_add_team", False):
        st.markdown('<div class="dynamic-form">', unsafe_allow_html=True)
        st.markdown('<div class="search-step">Create New Team</div>', unsafe_allow_html=True)
        
        new_team_name = st.text_input(
            "Team Name",
            placeholder="Enter team name (e.g., Marketing Team, Research Group)",
            key="new_team_name_input",
            help="Team name can contain letters, numbers, spaces, underscores, and hyphens"
        )
        
        col7, col8 = st.columns(2)
        
        with col7:
            if st.button("✅ Create Team", key="create_team_btn", use_container_width=True):
                if new_team_name and new_team_name.strip():
                    try:
                        if logic.is_valid_team_name(new_team_name):
                            table_name = logic.create_custom_team(new_team_name.strip())
                            st.success(f"✅ Team '{new_team_name}' created successfully!")
                            st.session_state["show_add_team"] = False
                            st.session_state["newly_created_team"] = new_team_name.strip()
                            # Use rerun to refresh the page and update the team list
                            st.rerun()
                        else:
                            st.error("❌ Invalid team name. Please use only letters, numbers, spaces, underscores, and hyphens (2-50 characters).")
                    except ValueError as e:
                        st.error(f"❌ {str(e)}")
                else:
                    st.error("❌ Please enter a team name.")
        
        with col8:
            if st.button("❌ Cancel", key="cancel_team_btn", use_container_width=True):
                st.session_state["show_add_team"] = False
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    if team_choice and team_choice != "(choose)":
        rows = logic.db_fetch_team(team_choice)
        ui.render_saved_ads_page(team_choice, rows)
    else:
        st.info("💾 Select a team from the dropdown to view saved ads, or create a new team using the 'Add Team' button.")

# -----------------------------------------------------------------------------
# Debug Info
# -----------------------------------------------------------------------------
with st.expander("🔧 Debug Info"):
    st.write("Mode:", mode)
    st.write("Last query params:", st.session_state.get("last_query_params"))
    st.write("Last query URL:", st.session_state.get("last_query_url"))
    
    # Show the request format being sent to Apify
    if st.session_state.get("last_request_format"):
        st.write("**Request Format Sent to Apify:**")
        st.json(st.session_state.get("last_request_format"))
    
    # Add test buttons
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("🔍 Test Database"):
            logic.test_delete_functionality()
    with col2:
        if st.button("🔗 Test URL Building"):
            logic.test_url_building()
    with col3:
        if st.button("📋 Test Page ID Request"):
            logic.test_page_id_request_format()
    with col4:
        if st.button("🌐 Test Landing Domain Request"):
            logic.test_landing_domain_request_format()
