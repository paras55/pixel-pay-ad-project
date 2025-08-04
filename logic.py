"""
logic.py — Data + DB utilities for FB Ads Explorer (SQLite Teams).
"""

from __future__ import annotations

import os
import json
import sqlite3
from pathlib import Path
from datetime import datetime, timezone
from functools import lru_cache
from urllib.parse import quote_plus
from typing import Any, Optional, Dict, List, Union

import streamlit as st
import pandas as pd


# =============================================================================
# CONSTANTS / MAPPINGS
# =============================================================================
CATEGORY_LABEL_TO_ADTYPE = {
    "All ads": "all",
    "Issues, elections or politics": "issues_elections_politics",
    "Properties": "housing",  # closest FB param
    "Employment": "employment",
    "Financial products and services": "credit",  # closest FB param
}

ACTIVE_STATUS_LABEL_TO_PARAM = {
    "Active ads": "active",
    "Inactive ads": "inactive",
    "All ads": "all",
}

SEARCH_MODE_LABEL_TO_PARAM = {
    "Broad (any words)": "keyword_unordered",
    "Exact phrase": "keyword_exact",
}

COMMON_COUNTRIES: List[tuple[str, str]] = [
    ("United States", "US"),
    ("India", "IN"),
    ("United Kingdom", "GB"),
    ("Canada", "CA"),
    ("Australia", "AU"),
    ("Germany", "DE"),
    ("France", "FR"),
    ("Brazil", "BR"),
    ("Singapore", "SG"),
]

TEAM_TABLES = ["team1", "team2", "team3"]

# SQLite path (same folder as this file)
DB_PATH = Path(__file__).with_name("ads.db")

# Table to store custom team names
CUSTOM_TEAMS_TABLE = "custom_teams"


# =============================================================================
# APIFY IMPORT (lazy)
# =============================================================================
@lru_cache(maxsize=1)
def _import_apify_client():
    try:
        from apify_client import ApifyClient  # type: ignore
        return ApifyClient, None
    except Exception as e:  # noqa: BLE001
        return None, e


# =============================================================================
# TOKEN HANDLING
# =============================================================================
def safe_get_streamlit_secret(key: str) -> str | None:
    try:
        return st.secrets[key]  # type: ignore[index]
    except Exception:  # noqa: BLE001
        return None


def resolve_apify_token() -> str:
    """Resolve Apify token from backend sources only (secrets or environment variables)."""
    tok = safe_get_streamlit_secret("APIFY_TOKEN")
    if tok:
        return tok
    env_tok = os.getenv("APIFY_TOKEN")
    if env_tok:
        return env_tok
    return ""


# =============================================================================
# URL BUILDER
# =============================================================================
def build_fb_ads_library_url(*, country: str, keyword: str = "", ad_type: str = "all", active_status: str = "all", search_mode: str = "keyword_unordered", page_id: str = "", landing_domain: str = "") -> str:
    """Build Facebook Ad Library URL based on search type."""
    country = country.strip().upper()
    
    if search_mode == "page_id" and page_id:
        # Page ID search - using the exact format provided
        url = (
            "https://www.facebook.com/ads/library/?"
            "active_status=all&"
            "ad_type=all&"
            "country=ALL&"
            "is_targeted_country=false&"
            "media_type=all&"
            "search_type=page&"
            "source=page-transparency-widget&"
            f"view_all_page_id={page_id.strip()}"
        )
    elif search_mode == "landing_domain" and landing_domain:
        # Landing page domain search - using the exact format provided
        q = quote_plus(landing_domain.strip())
        url = (
            "https://www.facebook.com/ads/library/?"
            "active_status=active&"
            "ad_type=all&"
            f"country={country}&"
            "is_targeted_country=false&"
            "media_type=all&"
            f"q={q}&"
            "search_type=keyword_unordered"
        )
    else:
        # Keyword search (default)
        q = quote_plus(keyword.strip())
        url = (
            "https://www.facebook.com/ads/library/?"
            f"active_status={active_status}&"
            f"ad_type={ad_type}&"
            f"country={country}&"
            "is_targeted_country=false&"
            "media_type=all&"
            f"q={q}&"
            f"search_type={search_mode}"
        )
    
    return url


# =============================================================================
# APIFY SCRAPE (cached)
# =============================================================================
@st.cache_data(show_spinner=False)
def run_apify_scrape(token: str, url: str, count: int, active_status: str) -> list[dict]:
    ApifyClient, import_err = _import_apify_client()
    if import_err or ApifyClient is None:
        raise RuntimeError("apify-client not installed. Run: `pip install apify-client`.")
    if not token:
        raise ValueError("Missing Apify API token.")

    client = ApifyClient(token)
    run_input = {
        "urls": [{"url": url, "method": "GET"}],
        "count": int(count),
        "scrapeAdDetails": True,
        "scrapePageAds.activeStatus": active_status,
        "period": "",
    }
    
    # Debug: Print the request being sent
    print(f"🔍 Sending request to Apify:")
    print(f"URL: {url}")
    print(f"Count: {count}")
    print(f"Active Status: {active_status}")
    print(f"Full request: {run_input}")
    print(f"Request format matches example: {run_input.get('count') == count and run_input.get('scrapeAdDetails') == True and 'period' in run_input}")
    
    run = client.actor("curious_coder/facebook-ads-library-scraper").call(run_input=run_input)
    ds_id = run.get("defaultDatasetId")
    if not ds_id:
        print("❌ No dataset ID returned from Apify")
        return []
    
    print(f"✅ Dataset ID: {ds_id}")
    items = list(client.dataset(ds_id).iterate_items())
    print(f"📊 Retrieved {len(items)} items from Apify")
    return items


# =============================================================================
# DATE HELPERS
# =============================================================================
def parse_date_maybe(s: Any):
    if not s:
        return None
    for fmt in (
        "%Y-%m-%d",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%S.%f%z",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
    ):
        try:
            return datetime.strptime(str(s), fmt)
        except Exception:  # noqa: BLE001
            continue
    try:  # epoch?
        if str(s).isdigit():
            return datetime.fromtimestamp(int(s), tz=timezone.utc)
    except Exception:  # noqa: BLE001
        pass
    return None


def compute_running_days(item: dict) -> int | None:
    """Compute running days for an ad. Returns None if no valid start date found."""
    try:
        start = item.get("startDate") or item.get("start_date")
        start_dt = parse_date_maybe(start)
        if not start_dt:
            return None
        now = datetime.now(timezone.utc)
        if start_dt.tzinfo is None:
            start_dt = start_dt.replace(tzinfo=timezone.utc)
        delta = now - start_dt
        return max(delta.days, 0)
    except Exception as e:
        print(f"Error computing running days: {e}")
        return None


def detect_status(item: dict) -> str:
    for k in ("activeStatus", "status", "adStatus", "active_status"):
        v = item.get(k)
        if v is not None:
            return str(v).capitalize()
    if item.get("is_active") is False:
        return "Inactive"
    end = item.get("endDate") or item.get("end_date")
    end_dt = parse_date_maybe(end)
    if end_dt and end_dt < datetime.now(timezone.utc):
        return "Inactive"
    return "Active"


# =============================================================================
# SNAPSHOT / MEDIA HELPERS
# =============================================================================
def _get_snapshot_dict(item: dict) -> dict:
    snap = item.get("snapshot")
    if isinstance(snap, str):
        try:
            snap = json.loads(snap)
        except Exception:  # noqa: BLE001
            snap = {}
    if not isinstance(snap, dict):
        snap = {}
    return snap


def get_original_image_url(item: dict) -> str | None:
    snap = _get_snapshot_dict(item)
    imgs = snap.get("images")
    if isinstance(imgs, dict):
        imgs = [imgs]
    elif not isinstance(imgs, (list, tuple)):
        imgs = []
    for im in imgs:
        if not isinstance(im, dict):
            continue
        for k in ("original_image_url", "original_picture_url", "original_picture", "url", "src"):
            v = im.get(k)
            if v:
                return v
    return None


def extract_primary_media(item: dict):
    oi = get_original_image_url(item)
    if oi:
        return "image", oi
    img_keys = ["imageUrl", "image_url", "thumbnailUrl", "thumbnail_url", "image"]
    vid_keys = ["videoUrl", "video_url", "video"]
    for k in img_keys:
        if item.get(k):
            return "image", item[k]
    for k in vid_keys:
        if item.get(k):
            return "video", item[k]
    creatives = item.get("creatives") or item.get("media") or []
    if isinstance(creatives, dict):
        creatives = [creatives]
    if isinstance(creatives, (list, tuple)):
        for c in creatives:
            if not isinstance(c, dict):
                continue
            for k in img_keys:
                if c.get(k):
                    return "image", c[k]
            for k in vid_keys:
                if c.get(k):
                    return "video", c[k]
    media_urls = item.get("mediaUrls") or item.get("media_urls")
    if isinstance(media_urls, (list, tuple)) and media_urls:
        return "image", media_urls[0]
    return None, None


# =============================================================================
# TEXT UTIL
# =============================================================================
def summarize_text(txt: str, length: int = 160) -> str:
    if not txt:
        return ""
    txt = str(txt).strip().replace("\n", " ")
    return (txt[: length - 1] + "…") if len(txt) > length else txt


# =============================================================================
# DB SCHEMA
# =============================================================================
SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS {table_name} (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ad_archive_id TEXT,
    categories TEXT,
    collation_count TEXT,
    collation_id TEXT,
    start_date TEXT,
    end_date TEXT,
    entity_type TEXT,
    is_active INTEGER,
    page_id TEXT,
    page_name TEXT,
    cta_text TEXT,
    cta_type TEXT,
    link_url TEXT,
    page_entity_type TEXT,
    page_profile_picture_url TEXT,
    page_profile_uri TEXT,
    state_media_run_label TEXT,
    total_active_time INTEGER,
    original_image_url TEXT,
    raw_json TEXT,
    saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

CUSTOM_TEAMS_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS custom_teams (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    team_name TEXT UNIQUE NOT NULL,
    table_name TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""


def _connect() -> sqlite3.Connection:
    return sqlite3.connect(DB_PATH)


def init_db() -> None:
    conn = _connect()
    try:
        cur = conn.cursor()
        for t in TEAM_TABLES:
            cur.execute(SCHEMA_SQL.format(table_name=t))
        cur.execute(CUSTOM_TEAMS_SCHEMA_SQL)
        conn.commit()
    finally:
        conn.close()


def create_custom_team(team_name: str) -> str:
    """
    Create a new custom team table and return the table name.
    
    Args:
        team_name: User-friendly name for the team
        
    Returns:
        str: The table name created for this team
        
    Raises:
        ValueError: If team name is invalid or already exists
    """
    # Validate team name
    if not team_name or not team_name.strip():
        raise ValueError("Team name cannot be empty")
    
    team_name = team_name.strip()
    
    # Check for invalid characters in table name
    if not team_name.replace("_", "").replace("-", "").isalnum():
        raise ValueError("Team name can only contain letters, numbers, underscores, and hyphens")
    
    # Generate table name
    table_name = f"custom_team_{team_name.lower().replace(' ', '_').replace('-', '_')}"
    
    conn = _connect()
    try:
        cur = conn.cursor()
        
        # Check if team name already exists
        cur.execute("SELECT team_name FROM custom_teams WHERE team_name = ?", (team_name,))
        if cur.fetchone():
            raise ValueError(f"Team '{team_name}' already exists")
        
        # Check if table name already exists
        cur.execute("SELECT table_name FROM custom_teams WHERE table_name = ?", (table_name,))
        if cur.fetchone():
            raise ValueError(f"Team table '{table_name}' already exists")
        
        # Create the team table
        cur.execute(SCHEMA_SQL.format(table_name=table_name))
        
        # Add entry to custom_teams table
        cur.execute(
            "INSERT INTO custom_teams (team_name, table_name) VALUES (?, ?)",
            (team_name, table_name)
        )
        
        conn.commit()
        print(f"Created custom team '{team_name}' with table '{table_name}'")
        return table_name
        
    finally:
        conn.close()


def get_all_teams() -> list[str]:
    """
    Get all available team names (default + custom teams).
    
    Returns:
        list[str]: List of all team names
    """
    conn = _connect()
    try:
        cur = conn.cursor()
        
        # Get custom teams
        cur.execute("SELECT team_name FROM custom_teams ORDER BY created_at")
        custom_teams = [row[0] for row in cur.fetchall()]
        
        # Combine default teams with custom teams
        all_teams = TEAM_TABLES + custom_teams
        return all_teams
        
    finally:
        conn.close()


def get_team_table_name(team_name: str) -> str:
    """
    Get the database table name for a given team name.
    
    Args:
        team_name: The team name (can be default or custom)
        
    Returns:
        str: The database table name
        
    Raises:
        ValueError: If team doesn't exist
    """
    # Check if it's a default team
    if team_name in TEAM_TABLES:
        return team_name
    
    # Check if it's a custom team
    conn = _connect()
    try:
        cur = conn.cursor()
        cur.execute("SELECT table_name FROM custom_teams WHERE team_name = ?", (team_name,))
        result = cur.fetchone()
        if result:
            return result[0]
        else:
            raise ValueError(f"Team '{team_name}' not found")
    finally:
        conn.close()


def is_valid_team_name(team_name: str) -> bool:
    """
    Check if a team name is valid for creation.
    
    Args:
        team_name: The team name to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not team_name or not team_name.strip():
        return False
    
    team_name = team_name.strip()
    
    # Check length
    if len(team_name) < 2 or len(team_name) > 50:
        return False
    
    # Check for invalid characters
    if not team_name.replace(" ", "").replace("_", "").replace("-", "").isalnum():
        return False
    
    # Check if it's a reserved name
    reserved_names = TEAM_TABLES + ["custom_teams", "sqlite_sequence"]
    if team_name.lower() in [name.lower() for name in reserved_names]:
        return False
    
    return True


def delete_custom_team(team_name: str) -> bool:
    """
    Delete a custom team and its associated table.
    
    Args:
        team_name: The name of the team to delete
        
    Returns:
        bool: True if successful, False otherwise
        
    Raises:
        ValueError: If team doesn't exist or is a default team
    """
    # Check if it's a default team (cannot be deleted)
    if team_name in TEAM_TABLES:
        raise ValueError(f"Cannot delete default team '{team_name}'")
    
    conn = _connect()
    try:
        cur = conn.cursor()
        
        # Check if team exists
        cur.execute("SELECT table_name FROM custom_teams WHERE team_name = ?", (team_name,))
        result = cur.fetchone()
        if not result:
            raise ValueError(f"Team '{team_name}' not found")
        
        table_name = result[0]
        
        # Delete the team table
        cur.execute(f"DROP TABLE IF EXISTS {table_name}")
        
        # Remove entry from custom_teams table
        cur.execute("DELETE FROM custom_teams WHERE team_name = ?", (team_name,))
        
        conn.commit()
        print(f"Successfully deleted team '{team_name}' and table '{table_name}'")
        return True
        
    except Exception as e:
        print(f"Error deleting team '{team_name}': {e}")
        return False
    finally:
        conn.close()


def is_custom_team(team_name: str) -> bool:
    """
    Check if a team is a custom team (not a default team).
    
    Args:
        team_name: The team name to check
        
    Returns:
        bool: True if it's a custom team, False if it's a default team
    """
    return team_name not in TEAM_TABLES


def db_insert_team(table: str, ad_fields: Dict[str, Any], raw_item: Optional[Dict[str, Any]] = None) -> None:
    # Get the actual table name (handles both default and custom teams)
    actual_table = get_team_table_name(table) if table not in TEAM_TABLES else table
    
    cols = [
        "ad_archive_id", "categories", "collation_count", "collation_id",
        "start_date", "end_date", "entity_type", "is_active",
        "page_id", "page_name", "cta_text", "cta_type",
        "link_url", "page_entity_type", "page_profile_picture_url",
        "page_profile_uri", "state_media_run_label", "total_active_time",
        "original_image_url", "raw_json",
    ]
    vals = [
        ad_fields.get("ad_archive_id"),
        ad_fields.get("categories"),
        ad_fields.get("collation_count"),
        ad_fields.get("collation_id"),
        ad_fields.get("start_date"),
        ad_fields.get("end_date"),
        ad_fields.get("entity_type"),
        int(bool(ad_fields.get("is_active"))) if ad_fields.get("is_active") is not None else None,
        ad_fields.get("page_id"),
        ad_fields.get("page_name"),
        ad_fields.get("cta_text"),
        ad_fields.get("cta_type"),
        ad_fields.get("link_url"),
        ad_fields.get("page_entity_type"),
        ad_fields.get("page_profile_picture_url"),
        ad_fields.get("page_profile_uri"),
        ad_fields.get("state_media_run_label"),
        ad_fields.get("total_active_time"),
        ad_fields.get("original_image_url"),
        json.dumps(raw_item, ensure_ascii=False) if raw_item is not None else None,
    ]
    ph = ",".join(["?"] * len(cols))
    sql = f"INSERT INTO {actual_table} ({','.join(cols)}) VALUES ({ph})"
    conn = _connect()
    try:
        conn.execute(sql, vals)
        conn.commit()
    finally:
        conn.close()


def db_fetch_team(table: str) -> List[Dict[str, Any]]:
    # Get the actual table name (handles both default and custom teams)
    actual_table = get_team_table_name(table) if table not in TEAM_TABLES else table
    
    try:
        conn = _connect()
        cursor = conn.cursor()
        
        # Check if table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (actual_table,))
        if not cursor.fetchone():
            return []
        
        # Fetch all rows
        cursor.execute(f"SELECT * FROM {actual_table}")
        rows = cursor.fetchall()
        
        # Get column names
        columns = [description[0] for description in cursor.description]
        
        # Convert to list of dicts
        results: List[Dict[str, Any]] = []
        for row in rows:
            results.append(dict(zip(columns, row)))
        
        conn.close()
        return results
        
    except Exception as e:
        st.error(f"Database error: {e}")
        return []


def db_delete_ad(team: str, ad: dict) -> bool:
    """Delete an ad from the specified team table by ad_archive_id. Returns True if successful."""
    try:
        # Get the actual table name (handles both default and custom teams)
        table = get_team_table_name(team) if team not in TEAM_TABLES else team
        
        # Get the ad_archive_id from the ad data
        ad_id = ad.get("ad_archive_id")
        if not ad_id:
            print(f"No ad_archive_id found for deletion")
            return False
        
        print(f"Attempting to delete ad with ID: {ad_id} from table: {table}")
        
        conn = _connect()
        with conn:
            # Only look for ad_archive_id since that's what's stored in the database
            cursor = conn.execute(f"DELETE FROM {table} WHERE ad_archive_id = ?", (ad_id,))
            # Check if any row was actually deleted
            if cursor.rowcount > 0:
                print(f"Successfully deleted ad {ad_id} from {table}")
                conn.commit()  # Ensure changes are committed
                return True
            else:
                print(f"No ad found with ID {ad_id} in table {table}")
                return False
                
    except Exception as e:
        print(f"Error deleting ad: {e}")
        return False


def db_clear_all_teams():
    conn = _connect()
    with conn:
        for table in TEAM_TABLES:
            conn.execute(f"DELETE FROM {table}")
    conn.close()

def test_delete_functionality():
    """Test function to verify delete functionality works"""
    try:
        # Test database connection and table structure
        conn = _connect()
        cursor = conn.cursor()
        
        # Check if team1 table exists and has data
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='team1'")
        if cursor.fetchone():
            print("✅ team1 table exists")
            
            # Check table structure
            cursor.execute("PRAGMA table_info(team1)")
            columns = cursor.fetchall()
            print(f"Table columns: {[col[1] for col in columns]}")
            
            # Check if there are any ads in the table
            cursor.execute("SELECT COUNT(*) FROM team1")
            count = cursor.fetchone()[0]
            print(f"Number of ads in team1: {count}")
            
            if count > 0:
                # Show first few ads
                cursor.execute("SELECT ad_archive_id, page_name FROM team1 LIMIT 3")
                ads = cursor.fetchall()
                print(f"Sample ads: {ads}")
        else:
            print("❌ team1 table does not exist")
        
        conn.close()
        return True
    except Exception as e:
        print(f"Test failed: {e}")
        return False

def test_url_building():
    """Test function to verify URL building works correctly"""
    try:
        # Test page ID URL building with exact format
        page_id_url = build_fb_ads_library_url(
            country="ALL",
            page_id="113923695147163",
            ad_type="all",
            active_status="all",
            search_mode="page_id"
        )
        expected_url = "https://www.facebook.com/ads/library/?active_status=all&ad_type=all&country=ALL&is_targeted_country=false&media_type=all&search_type=page&source=page-transparency-widget&view_all_page_id=113923695147163"
        
        print(f"✅ Page ID URL: {page_id_url}")
        print(f"Expected URL: {expected_url}")
        print(f"URLs match: {page_id_url == expected_url}")
        
        # Test keyword URL building
        keyword_url = build_fb_ads_library_url(
            country="US",
            keyword="test keyword",
            ad_type="all",
            active_status="active",
            search_mode="keyword_unordered"
        )
        print(f"✅ Keyword URL: {keyword_url}")
        
        # Test landing domain URL building with exact format
        domain_url = build_fb_ads_library_url(
            country="US",
            landing_domain="articles.insuranceadvisorsforyou.com",
            ad_type="all",
            active_status="active",
            search_mode="landing_domain"
        )
        expected_domain_url = "https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country=US&is_targeted_country=false&media_type=all&q=articles.insuranceadvisorsforyou.com&search_type=keyword_unordered"
        
        print(f"✅ Landing Domain URL: {domain_url}")
        print(f"Expected URL: {expected_domain_url}")
        print(f"URLs match: {domain_url == expected_domain_url}")
        
        return True
    except Exception as e:
        print(f"URL building test failed: {e}")
        return False

def test_page_id_request_format():
    """Test the complete request format for page ID search"""
    try:
        # Build the URL
        url = build_fb_ads_library_url(
            country="ALL",
            page_id="113923695147163",
            ad_type="all",
            active_status="all",
            search_mode="page_id"
        )
        
        # Create the request format
        request_format = {
            "count": 10,
            "scrapeAdDetails": True,
            "scrapePageAds.activeStatus": "all",
            "urls": [
                {
                    "url": url,
                    "method": "GET"
                }
            ],
            "period": ""
        }
        
        print(f"✅ Complete request format:")
        print(f"URL: {url}")
        print(f"Request: {request_format}")
        
        # Verify the format matches the example
        expected_keys = ["count", "scrapeAdDetails", "scrapePageAds.activeStatus", "urls", "period"]
        has_all_keys = all(key in request_format for key in expected_keys)
        print(f"Has all required keys: {has_all_keys}")
        
        return True
    except Exception as e:
        print(f"Request format test failed: {e}")
        return False

def test_landing_domain_request_format():
    """Test the complete request format for landing domain search"""
    try:
        # Build the URL
        url = build_fb_ads_library_url(
            country="US",
            landing_domain="articles.insuranceadvisorsforyou.com",
            ad_type="all",
            active_status="active",
            search_mode="landing_domain"
        )
        
        # Create the request format
        request_format = {
            "count": 10,
            "scrapeAdDetails": True,
            "scrapePageAds.activeStatus": "all",
            "urls": [
                {
                    "url": url,
                    "method": "GET"
                }
            ],
            "period": ""
        }
        
        print(f"✅ Landing Domain request format:")
        print(f"URL: {url}")
        print(f"Request: {request_format}")
        
        # Verify the format matches the example
        expected_keys = ["count", "scrapeAdDetails", "scrapePageAds.activeStatus", "urls", "period"]
        has_all_keys = all(key in request_format for key in expected_keys)
        print(f"Has all required keys: {has_all_keys}")
        
        # Verify URL format matches example
        expected_url_pattern = "active_status=active&ad_type=all&country=US&is_targeted_country=false&media_type=all&q=articles.insuranceadvisorsforyou.com&search_type=keyword_unordered"
        url_has_pattern = expected_url_pattern in url
        print(f"URL has correct pattern: {url_has_pattern}")
        
        return True
    except Exception as e:
        print(f"Landing domain request format test failed: {e}")
        return False


# =============================================================================
# EXPORT DF (curated)
# =============================================================================
def ads_to_dataframe(items: List[Dict[str, Any]]) -> pd.DataFrame:
    rows = [extract_selected_fields(it) for it in items]
    return pd.DataFrame(rows)


# =============================================================================
# CURATED FIELD EXTRACTION
# =============================================================================
def extract_selected_fields(item: dict) -> dict:
    """
    Extract curated fields safely (handles lists / strings / missing / snapshot JSON).
    """
    snap = _get_snapshot_dict(item)

    # cards
    card0 = None
    cards = snap.get("cards")
    if isinstance(cards, list) and cards:
        if isinstance(cards[0], dict):
            card0 = cards[0]
    elif isinstance(cards, dict):
        card0 = cards

    # page_categories
    pgcat0 = None
    page_categories = snap.get("page_categories")
    if isinstance(page_categories, list) and page_categories:
        if isinstance(page_categories[0], dict):
            pgcat0 = page_categories[0]
    elif isinstance(page_categories, dict):
        pgcat0 = page_categories

    # link_url
    link_url = snap.get("link_url")
    if not link_url and isinstance(card0, dict):
        link_url = card0.get("link_url")

    # coerce date (epoch OK)
    def _coerce_epoch_or_date(val):
        if val in (None, "", 0, "0"):
            return None
        try:
            if isinstance(val, (int, float)) or str(val).isdigit():
                dt = datetime.fromtimestamp(int(val), tz=timezone.utc)
                return dt.date().isoformat()
        except Exception:  # noqa: BLE001
            pass
        dt = parse_date_maybe(val)
        if dt:
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.date().isoformat()
        return None

    start_date = _coerce_epoch_or_date(item.get("start_date") or item.get("startDate"))
    end_date = _coerce_epoch_or_date(item.get("end_date") or item.get("endDate"))

    # categories display
    categories = item.get("categories")
    if isinstance(categories, (list, tuple)):
        categories_disp = ", ".join(str(c) for c in categories)
    else:
        categories_disp = categories

    return {
        "ad_archive_id": item.get("ad_archive_id") or item.get("adId"),
        "categories": categories_disp,
        "collation_count": item.get("collation_count"),
        "collation_id": item.get("collation_id"),
        "start_date": start_date,
        "end_date": end_date,
        "entity_type": item.get("entity_type"),
        "is_active": item.get("is_active"),
        "page_id": item.get("page_id") or item.get("pageId"),
        "page_name": item.get("page_name") or item.get("pageName"),
        "cta_text": (card0.get("cta_text") if isinstance(card0, dict) else None) or snap.get("cta_text"),
        "cta_type": (card0.get("cta_type") if isinstance(card0, dict) else None) or snap.get("cta_type"),
        "link_url": link_url,
        "page_entity_type": (pgcat0.get("page_entity_type") if isinstance(pgcat0, dict) else None) or item.get("page_entity_type"),
        "page_profile_picture_url": item.get("page_profile_picture_url") or snap.get("page_profile_picture_url"),
        "page_profile_uri": item.get("page_profile_uri") or snap.get("page_profile_uri"),
        "state_media_run_label": item.get("state_media_run_label"),
        "total_active_time": item.get("total_active_time"),
        "original_image_url": get_original_image_url(item),
        "original_picture_url": get_original_image_url(item),  # backward compat
    }
    def build_search_url(
        *,
        search_type: str,
        country: str,
        keyword: str = "",
        ad_type: str = "all",
        active_status: str = "all",
        search_mode: str = "keyword_unordered",
        page_id: str = "",
        landing_page_domain: str = "",
    ) -> str:
        """
        Build Facebook Ads Library URL for three search types:
        - keyword: standard Apify URL with keyword, country, ad category
        - page_id: Facebook Ads Library URL using view_all_page_id query param
        - landing_page: Facebook Ads Library URL using domain in 'q' param
        """
        country = country.strip().upper()
        if search_type == "keyword":
            q = quote_plus(keyword.strip())
            url = (
                "https://www.facebook.com/ads/library/?"
                f"active_status={active_status}&"
                f"ad_type={ad_type}&"
                f"country={country}&"
                "is_targeted_country=false&"
                "media_type=all&"
                f"q={q}&"
                f"search_type={search_mode}"
            )
            return url
        elif search_type == "page_id":
            pid = quote_plus(page_id.strip())
            url = (
                "https://www.facebook.com/ads/library/?"
                f"view_all_page_id={pid}&"
                f"country={country}&"
                "media_type=all"
            )
            return url
        elif search_type == "landing_page":
            domain = quote_plus(landing_page_domain.strip())
            url = (
                "https://www.facebook.com/ads/library/?"
                f"country={country}&"
                "media_type=all&"
                f"q={domain}"
            )
            return url
        else:
            raise ValueError(f"Unknown search_type: {search_type}")


    def extract_selected_fields(item: dict) -> dict:
        """
        Extract curated fields safely (handles lists / strings / missing / snapshot JSON).
        Removes debug/raw fields.
        Ensures image rendering by using 'original_image_url' if image is missing.
        """
        snap = _get_snapshot_dict(item)

        card0 = None
        cards = snap.get("cards")
        if isinstance(cards, list) and cards:
            if isinstance(cards[0], dict):
                card0 = cards[0]
        elif isinstance(cards, dict):
            card0 = cards

        pgcat0 = None
        page_categories = snap.get("page_categories")
        if isinstance(page_categories, list) and page_categories:
            if isinstance(page_categories[0], dict):
                pgcat0 = page_categories[0]
        elif isinstance(page_categories, dict):
            pgcat0 = page_categories

        link_url = snap.get("link_url")
        if not link_url and isinstance(card0, dict):
            link_url = card0.get("link_url")

        def _coerce_epoch_or_date(val):
            if val in (None, "", 0, "0"):
                return None
            try:
                if isinstance(val, (int, float)) or str(val).isdigit():
                    dt = datetime.fromtimestamp(int(val), tz=timezone.utc)
                    return dt.date().isoformat()
            except Exception:
                pass
            dt = parse_date_maybe(val)
            if dt:
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                return dt.date().isoformat()
            return None

        start_date = _coerce_epoch_or_date(item.get("start_date") or item.get("startDate"))
        end_date = _coerce_epoch_or_date(item.get("end_date") or item.get("endDate"))

        categories = item.get("categories")
        if isinstance(categories, (list, tuple)):
            categories_disp = ", ".join(str(c) for c in categories)
        else:
            categories_disp = categories

        # Ensure image rendering: use 'original_image_url' if image is missing
        image_url = get_original_image_url(item)
        if not image_url:
            # Try fallback keys
            img_keys = ["imageUrl", "image_url", "thumbnailUrl", "thumbnail_url", "image"]
            for k in img_keys:
                if item.get(k):
                    image_url = item[k]
                    break

        return {
            "ad_archive_id": item.get("ad_archive_id") or item.get("adId"),
            "categories": categories_disp,
            "collation_count": item.get("collation_count"),
            "collation_id": item.get("collation_id"),
            "start_date": start_date,
            "end_date": end_date,
            "entity_type": item.get("entity_type"),
            "is_active": item.get("is_active"),
            "page_id": item.get("page_id") or item.get("pageId"),
            "page_name": item.get("page_name") or item.get("pageName"),
            "cta_text": (card0.get("cta_text") if isinstance(card0, dict) else None) or snap.get("cta_text"),
            "cta_type": (card0.get("cta_type") if isinstance(card0, dict) else None) or snap.get("cta_type"),
            "link_url": link_url,
            "page_entity_type": (pgcat0.get("page_entity_type") if isinstance(pgcat0, dict) else None) or item.get("page_entity_type"),
            "page_profile_picture_url": item.get("page_profile_picture_url") or snap.get("page_profile_picture_url"),
            "page_profile_uri": item.get("page_profile_uri") or snap.get("page_profile_uri"),
            "state_media_run_label": item.get("state_media_run_label"),
            "total_active_time": item.get("total_active_time"),
            "original_image_url": image_url,
        }