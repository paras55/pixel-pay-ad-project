from __future__ import annotations
import streamlit as st
import json
import logic
from typing import Optional, List, Dict, Any
from components.adCard import render_ad_card

def render_main_search_page(
    ads_items: List[Dict[str, Any]],
    params: Optional[Dict[str, Any]],
    card_image_key: Optional[str] = None,
    footer_format: bool = False
):
    filtered_ads = []  # Ensure filtered_ads is always defined

    # Show all ads without any deduplication
    # ads_items remains unchanged - all ads will be displayed

    # Custom CSS for the main page with dark theme styling
    st.markdown("""
    <style>
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
        
        .stApp {
            background: var(--primary-bg);
        }
        
        .main > div {
            padding-top: 1rem;
        }
        
        .search-header {
            background: linear-gradient(135deg, var(--accent-primary) 0%, var(--accent-secondary) 100%);
            border-radius: 16px;
            padding: 30px;
            margin-bottom: 30px;
            color: var(--text-primary);
            text-align: center;
            box-shadow: var(--shadow-medium);
            border: 1px solid var(--border-color);
        }
        
        .search-title {
            font-size: 32px;
            font-weight: 700;
            margin: 0 0 12px 0;
            text-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }
        
        .search-subtitle {
            font-size: 18px;
            opacity: 0.95;
            margin: 0;
            font-weight: 400;
            color: var(--text-secondary);
        }
        
        .stats-container {
            background: var(--card-bg);
            border-radius: 16px;
            padding: 25px;
            margin-bottom: 25px;
            box-shadow: var(--shadow-light);
            border: 1px solid var(--border-color);
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 20px;
            margin-top: 15px;
        }
        
        .stat-card {
            text-align: center;
            padding: 20px 15px;
            background: var(--secondary-bg);
            border-radius: 12px;
            border: 1px solid var(--border-color);
            transition: all 0.3s ease;
        }
        
        .stat-card:hover {
            transform: translateY(-2px);
            box-shadow: var(--shadow-medium);
            background: var(--tertiary-bg);
        }
        
        .stat-number {
            font-size: 28px;
            font-weight: 700;
            color: var(--accent-primary);
            display: block;
            margin-bottom: 5px;
        }
        
        .stat-label {
            font-size: 13px;
            color: var(--text-muted);
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .export-section {
            background: #2d2d2d;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
            border: 1px solid #404040;
        }
        
        .export-title {
            font-size: 20px;
            font-weight: 700;
            color: #1e293b;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .filter-section {
            background: white;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 25px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
            border: 1px solid #e2e8f0;
        }
        
        .filter-title {
            font-size: 18px;
            font-weight: 600;
            color: #1e293b;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .ads-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 25px;
            margin-top: 25px;
        }
        
        .no-results {
            text-align: center;
            padding: 80px 40px;
            background: white;
            border-radius: 15px;
            margin: 30px 0;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
            border: 1px solid #e2e8f0;
        }
        
        .no-results-icon {
            font-size: 64px;
            margin-bottom: 25px;
            opacity: 0.7;
        }
        
        .no-results-title {
            font-size: 28px;
            font-weight: 700;
            color: #1e293b;
            margin-bottom: 12px;
        }
        
        .no-results-subtitle {
            font-size: 18px;
            color: #64748b;
            margin-bottom: 30px;
            line-height: 1.5;
        }
        
        .section-divider {
            height: 3px;
            background: linear-gradient(90deg, transparent, #6366f1, transparent);
            margin: 40px 0;
            border-radius: 2px;
        }
        
        .filter-info {
            background: #eff6ff;
            border: 1px solid #dbeafe;
            border-radius: 10px;
            padding: 15px 20px;
            margin-bottom: 20px;
            color: #1e40af;
            font-weight: 500;
        }
        
        .ads-section-title {
            font-size: 24px;
            font-weight: 700;
            color: #1e293b;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .tips-section {
            background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
            border-radius: 15px;
            padding: 30px;
            margin: 30px 0;
            border: 1px solid #bae6fd;
        }
        
        .tips-title {
            font-size: 20px;
            font-weight: 700;
            color: #0c4a6e;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .tip-item {
            margin-bottom: 12px;
            color: #0f172a;
            line-height: 1.5;
        }
        
        .tip-category {
            font-weight: 600;
            color: #0c4a6e;
            margin-top: 15px;
            margin-bottom: 8px;
        }
    </style>
    """, unsafe_allow_html=True)
    
    if ads_items:
        # Get the requested count from session state
        requested_count = st.session_state.get("last_query_params", {}).get("count", "Unknown")
        
        # Header section
        st.markdown(f"""
        <div class="search-header">
            <div class="search-title">🎯 Ad Discovery Results</div>
            <div class="search-subtitle">Requested: {requested_count} ads | Found: {len(ads_items)} advertising campaigns</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Statistics section (removed Campaign Overview box as requested)
        active_ads = sum(1 for ad in ads_items if ad.get("Active", False) or str(ad.get("Active", "")).lower() == "true")
        inactive_ads = len(ads_items) - active_ads
        
        # Export section
        st.markdown("""
        <div class="export-section">
            <div class="export-title">📊 Export & Download Options</div>
        """, unsafe_allow_html=True)
        
        # Export buttons
        exp_cols = st.columns(4)
        
        with exp_cols[0]:
            st.download_button(
                label="📄 JSON Export",
                data=json.dumps(ads_items, indent=2, ensure_ascii=False),
                file_name=f"fb_ads_export_{len(ads_items)}.json",
                mime="application/json",
                key="download_json",
                use_container_width=True,
                help="Download raw ad data in JSON format"
            )
            
        with exp_cols[1]:
            df = logic.ads_to_dataframe(ads_items)
            st.download_button(
                label="📊 CSV Export",
                data=df.to_csv(index=False),
                file_name=f"fb_ads_curated_{len(ads_items)}.csv",
                mime="text/csv",
                key="download_csv",
                use_container_width=True,
                help="Download processed ad data in CSV format"
            )
            
        with exp_cols[2]:
            # Create detailed summary report
            # Calculate percentages safely
            active_percent = round(active_ads/len(ads_items)*100, 1) if ads_items else 0
            inactive_percent = round(inactive_ads/len(ads_items)*100, 1) if ads_items else 0
            
            summary_text = f"""Facebook Ad Campaign Analysis Report
Generated: {st.session_state.get('search_timestamp', 'N/A')}
Search Parameters: {params if params else 'N/A'}

EXECUTIVE SUMMARY
================
Total Unique Ads Analyzed: {len(ads_items)}
Active Campaigns: {active_ads} ({active_percent}%)
Inactive Campaigns: {inactive_ads} ({inactive_percent}%)

PLATFORM DISTRIBUTION
====================
Facebook: {len(ads_items)} ads (100%)
"""
            # Remove platform distribution loop in export/summary section
            # If you want to show only Facebook, just add a line:
            # summary_text += f"""
            # Facebook: {len(ads_items)} ads (100%)
            # """
                
            summary_text += f"""

TOP PERFORMING METRICS
=====================
Most Common Platform: Facebook
Longest Running Campaign: {max([days for ad in ads_items if (days := logic.compute_running_days(ad)) is not None and days > 0], default=0)} days

CAMPAIGN CATEGORIES
==================
"""
            categories = {}
            for ad in ads_items:
                cats = ad.get("Categories", "Uncategorized")
                if cats != "N/A":
                    categories[cats] = categories.get(cats, 0) + 1
            
            for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True)[:10]:
                summary_text += f"{cat}: {count} campaigns\n"
                
            st.download_button(
                label="📋 Summary Report",
                data=summary_text,
                file_name=f"ad_analysis_report_{len(ads_items)}.txt",
                mime="text/plain",
                key="download_summary",
                use_container_width=True,
                help="Download comprehensive analysis report"
            )
            
        with exp_cols[3]:
            with st.expander("🔍 Data Preview", expanded=False):
                st.dataframe(df.head(5), use_container_width=True, key="curated_df")
                st.caption(f"Showing 5 of {len(df)} rows")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Section divider
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        
        # Filter and sort section
        st.markdown("""
        <div class="filter-section">
            <div class="filter-title">🎛️ Filter & Sort Options</div>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            status_filter = st.selectbox(
                "Status Filter",
                options=["All Ads", "Active Only", "Inactive Only"],
                key="status_filter",
                help="Filter ads by their current status"
            )
            
        with col2:
            # Since all ads are from Facebook, we'll just show "All Platforms" option
            platform_filter = st.selectbox(
                "Platform Filter",
                options=["All Platforms"],
                key="platform_filter",
                help="Filter by advertising platform"
            )
            
        with col3:
            sort_options = ["Most Recent", "Oldest First", "Active First", "Page Name A-Z", "Longest Running"]
            sort_by = st.selectbox(
                "Sort Order",
                options=sort_options,
                key="sort_by",
                help="Choose how to sort the ad cards"
            )
            
        with col4:
            # Category filter
            all_categories = set()
            for ad in ads_items:
                cats = ad.get("Categories", "Uncategorized")
                if cats != "N/A":
                    all_categories.add(cats)
            
            category_options = ["All Categories"] + sorted(list(all_categories))
            category_filter = st.selectbox(
                "Category Filter",
                options=category_options,
                key="category_filter",
                help="Filter by ad category"
            )
        
        # Apply filters
        filtered_ads = ads_items.copy()
        
        if status_filter == "Active Only":
            filtered_ads = [ad for ad in filtered_ads if ad.get("Active", False)]
        elif status_filter == "Inactive Only":
            filtered_ads = [ad for ad in filtered_ads if not ad.get("Active", False)]
            
        # Since all ads are from Facebook, we don't need platform filtering
        # if platform_filter != "All Platforms":
        #     filtered_ads = [ad for ad in filtered_ads if ad.get("Publisher_Platform") == platform_filter]
            
        if category_filter != "All Categories":
            filtered_ads = [ad for ad in filtered_ads if ad.get("Categories") == category_filter]
        
        # Apply sorting
        if sort_by == "Most Recent":
            filtered_ads.sort(key=lambda x: x.get("Start_Date", ""), reverse=True)
        elif sort_by == "Oldest First":
            filtered_ads.sort(key=lambda x: x.get("Start_Date", ""))
        elif sort_by == "Active First":
            filtered_ads.sort(key=lambda x: x.get("Active", False), reverse=True)
        elif sort_by == "Page Name A-Z":
            filtered_ads.sort(key=lambda x: x.get("pageName", x.get("Page_Name", "")).lower())
        elif sort_by == "Longest Running":
            filtered_ads.sort(key=lambda x: logic.compute_running_days(x) or 0, reverse=True)
        
        # Show filtered count
        if len(filtered_ads) != len(ads_items):
            st.markdown(f"""
            <div class="filter-info">
                📊 Showing {len(filtered_ads)} of {len(ads_items)} ads after applying filters
            </div>
            """, unsafe_allow_html=True)
        
        # Render ad cards in a responsive grid
        if filtered_ads:
            st.markdown("""
            <div class="ads-section-title">🎯 Ad Campaign Cards</div>
            """, unsafe_allow_html=True)
            
            # Use responsive grid layout
            cols_per_row = 3
            for row_start in range(0, len(filtered_ads), cols_per_row):
                cols = st.columns(cols_per_row, gap="large")
                for i, col in enumerate(cols):
                    idx = row_start + i
                    if idx >= len(filtered_ads):
                        continue
                    ad = filtered_ads[idx]
                    with col:
                        render_ad_card(
                            item=ad,
                            idx=idx,
                            variant="search",
                            raw_item=ad,
                            image_url=ad.get(card_image_key) if card_image_key else None,
                            footer=footer_format
                        )
        else:
            st.markdown("""
            <div class="no-results">
                <div class="no-results-icon">🔍</div>
                <div class="no-results-title">No ads match your filters</div>
                <div class="no-results-subtitle">Try adjusting your filter criteria above to see more results</div>
            </div>
            """, unsafe_allow_html=True)
            
    else:
        # No results state with enhanced tips
        st.markdown("""
        <div class="no-results">
            <div class="no-results-icon">🎯</div>
            <div class="no-results-title">Ready to Discover Ads?</div>
            <div class="no-results-subtitle">Submit a search query from the sidebar to start exploring advertising campaigns and gain competitive insights</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Enhanced tips section
      
        
        # Show recent searches if available
        if hasattr(st.session_state, 'recent_searches') and st.session_state.recent_searches:
            st.markdown("### 🕒 Recent Searches")
            recent_cols = st.columns(min(len(st.session_state.recent_searches[-5:]), 5))
            for i, search in enumerate(st.session_state.recent_searches[-5:]):
                with recent_cols[i]:
                    st.code(search, language='text')  # or use 'python', 'sql', etc. as appropriate

        
        # Render ad cards in a responsive grid
        if filtered_ads:
            st.markdown("### 🎯 Ad Campaigns")
            
            # Use responsive columns
            cols_per_row = 3
            for row_start in range(0, len(filtered_ads), cols_per_row):
                cols = st.columns(cols_per_row, gap="medium")
                for i, col in enumerate(cols):
                    idx = row_start + i
                    if idx >= len(filtered_ads):
                        continue
                    ad = filtered_ads[idx]
                    with col:
                        render_ad_card(
                            item=ad,
                            idx=idx,
                            variant="search",
                            raw_item=ad,
                            image_url=ad.get(card_image_key) if card_image_key else None,
                            footer=footer_format
                        )
        else:
            st.markdown("""
            <div class="no-results">
                <div class="no-results-icon">🔍</div>
                <div class="no-results-title">No ads match your filters</div>
                <div class="no-results-subtitle">Try adjusting your filter criteria above</div>
            </div>
            """, unsafe_allow_html=True)
            
        
        # Add some helpful tips
    with st.expander("💡 Search Tips"):
            st.markdown("""
            **How to get better results:**
            
            - Use specific brand names or keywords
            - Try different date ranges for more comprehensive results  
            - Filter by platform (Facebook, Instagram, etc.)
            - Look for trending topics in your industry
            - Save interesting ads for future reference
            
            **Popular search terms:**
            - Brand names (Nike, Apple, etc.)
            - Product categories (fitness, beauty, tech)
            - Seasonal campaigns (holiday, summer, etc.)
            - Industry keywords (SaaS, ecommerce, etc.)
            """)
            
        # Recent searches or suggestions could go here
            if hasattr(st.session_state, 'recent_searches') and st.session_state.recent_searches:
                st.markdown("### 🕒 Recent Searches")
                for search in st.session_state.recent_searches[-5:]:  # Show last 5
                    st.code(search)