# Facebook Ads Explorer - Code Flow Analysis

## 📋 Table of Contents
1. [User Input Flow](#user-input-flow)
2. [URL Building Process](#url-building-process)
3. [API Request Flow](#api-request-flow)
4. [Data Extraction & Processing](#data-extraction--processing)
5. [Frontend Rendering](#frontend-rendering)
6. [Sample Data Structures](#sample-data-structures)
7. [Debug Information](#debug-information)

---

## 🔄 User Input Flow

### 1. **App Entry Point** (`app.py`)
```python
# User selects search mode from sidebar
SEARCH_MODES = {
    "Keyword Search": {
        "label": "Keyword",
        "input_key": "keyword_raw",
        "placeholder": "Enter keyword (e.g. shoes)",
    },
    "Page ID Search": {
        "label": "Page ID", 
        "input_key": "page_id",
        "placeholder": "Enter Facebook Page ID",
    },
    "Landing Page Domain Search": {
        "label": "Landing Page Domain",
        "input_key": "landing_domain", 
        "placeholder": "Enter domain (e.g. example.com)",
    },
}
```

### 2. **Sidebar Input Collection** (`components/siderbar.py`)
```python
# User provides these inputs:
- Country selection (US, CA, GB, AU, IN, etc.)
- Keyword input (for keyword search)
- Ad category (All ads, Political, Properties, etc.)
- Active status (Active, Inactive, All)
- Search matching (Broad, Exact phrase)
- Number of ads to fetch (1-1000)
```

### 3. **Input Processing** (`app.py`)
```python
# Input gets processed into filters dict:
filters = {
    "country_code": "US",
    "country_label": "United States", 
    "keyword_raw": "shoes",
    "keyword_display": "shoes",
    "ad_category": "All ads",
    "ad_type_param": "all",
    "active_status_label": "Active ads",
    "active_status_param": "active",
    "search_mode_label": "Broad (any words)",
    "search_mode_param": "keyword_unordered",
    "count": 100
}
```

---

## 🌐 URL Building Process

### 1. **URL Builder Function** (`logic.py`)
```python
def build_fb_ads_library_url(*, country: str, keyword: str, ad_type: str, active_status: str, search_mode: str) -> str:
    country = country.strip().upper()
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
```

### 2. **Generated URLs by Search Type**

#### **Keyword Search:**
```
https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country=US&is_targeted_country=false&media_type=all&q=shoes&search_type=keyword_unordered
```

#### **Page ID Search:**
```
https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country=US&is_targeted_country=false&media_type=all&q=123456789&search_type=page_id
```

#### **Landing Page Domain Search:**
```
https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country=US&is_targeted_country=false&media_type=all&q=example.com&search_type=landing_domain
```

---

## 🔌 API Request Flow

### 1. **Apify Token Resolution** (`logic.py`)
```python
def resolve_apify_token() -> str:
    # Priority order:
    # 1. Streamlit secrets (.streamlit/secrets.toml)
    # 2. Environment variable (APIFY_TOKEN)
    # 3. Empty string (will show error)
    
    tok = safe_get_streamlit_secret("APIFY_TOKEN")
    if tok:
        return tok
    env_tok = os.getenv("APIFY_TOKEN")
    if env_tok:
        return env_tok
    return ""
```

### 2. **Apify Scrape Request** (`logic.py`)
```python
@st.cache_data(show_spinner=False)
def run_apify_scrape(token: str, url: str, count: int, active_status: str) -> list[dict]:
    client = ApifyClient(token)
    run_input = {
        "urls": [{"url": url}],
        "count": int(count),
        "scrapePageAds.activeStatus": active_status,
        "period": "",
    }
    
    # Apify Actor: "curious_coder/facebook-ads-library-scraper"
    run = client.actor("curious_coder/facebook-ads-library-scraper").call(run_input=run_input)
    ds_id = run.get("defaultDatasetId")
    items = list(client.dataset(ds_id).iterate_items())
    return items
```

### 3. **Apify Request Payload**
```json
{
    "urls": [
        {
            "url": "https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country=US&is_targeted_country=false&media_type=all&q=shoes&search_type=keyword_unordered"
        }
    ],
    "count": 100,
    "scrapePageAds.activeStatus": "active",
    "period": ""
}
```

---

## 📊 Data Extraction & Processing

### 1. **Raw API Response Structure**
```json
{
    "adId": "123456789",
    "pageId": "987654321",
    "pageName": "Nike",
    "adText": "Get the latest Nike shoes...",
    "startDate": "2024-01-01",
    "endDate": "2024-12-31",
    "Active": true,
    "Publisher_Platform": "Facebook",
    "snapshot": {
        "cards": [
            {
                "link_url": "https://nike.com/shoes",
                "cta_text": "Shop Now",
                "cta_type": "SHOP_NOW"
            }
        ],
        "page_categories": [
            {
                "page_entity_type": "Retail"
            }
        ]
    },
    "categories": ["Fashion", "Sports"],
    "collation_count": 5,
    "total_active_time": "365 days",
    "state_media_run_label": "N/A",
    "political_countries": "N/A"
}
```

### 2. **Field Extraction** (`logic.py`)
```python
def extract_selected_fields(item: dict) -> dict:
    snap = _get_snapshot_dict(item)
    
    # Extract from snapshot
    card0 = snap.get("cards", [{}])[0] if snap.get("cards") else {}
    pgcat0 = snap.get("page_categories", [{}])[0] if snap.get("page_categories") else {}
    
    return {
        "ad_archive_id": item.get("ad_archive_id") or item.get("adId"),
        "page_id": item.get("page_id") or item.get("pageId"),
        "page_name": item.get("page_name") or item.get("pageName"),
        "start_date": _coerce_epoch_or_date(item.get("start_date") or item.get("startDate")),
        "end_date": _coerce_epoch_or_date(item.get("end_date") or item.get("endDate")),
        "cta_text": card0.get("cta_text") or snap.get("cta_text"),
        "cta_type": card0.get("cta_type") or snap.get("cta_type"),
        "link_url": card0.get("link_url") or snap.get("link_url"),
        "categories": categories_disp,
        "collation_count": item.get("collation_count"),
        "entity_type": item.get("entity_type"),
        "page_entity_type": pgcat0.get("page_entity_type"),
        "page_profile_picture_url": item.get("page_profile_picture_url"),
        "page_profile_uri": item.get("page_profile_uri"),
        "state_media_run_label": item.get("state_media_run_label"),
        "total_active_time": item.get("total_active_time"),
        "original_image_url": get_original_image_url(item),
    }
```

### 3. **Image URL Extraction** (`logic.py`)
```python
def get_original_image_url(item: dict) -> str | None:
    snap = _get_snapshot_dict(item)
    
    # Try multiple image sources
    image_url = (
        snap.get("original_picture_url") or
        snap.get("original_image_url") or
        snap.get("picture_url") or
        snap.get("image_url")
    )
    
    return image_url
```

---

## 🎨 Frontend Rendering

### 1. **Main Search Page** (`components/mainSearchPage.py`)
```python
def render_main_search_page(ads_items: list[dict], params: dict | None, card_image_key: str | None = None):
    # 1. Display header with result count
    # 2. Show statistics (active/inactive counts, platforms, etc.)
    # 3. Export options (JSON, CSV, Summary Report)
    # 4. Filter and sort controls
    # 5. Render ad cards in grid layout
```

### 2. **Ad Card Rendering** (`components/adCard.py`)
```python
def render_ad_card(item: dict, idx: int, variant: str, **kwargs):
    # 1. Extract core data (page_name, ad_text, status, etc.)
    # 2. Get image URL with fallback
    # 3. Generate HTML with CSS for card display
    # 4. Create modal popup with detailed information
    # 5. Add JavaScript for modal interactions
```

### 3. **Card Data Mapping**
```python
# Input: Raw API item
# Output: Card display data
card_data = {
    "page_name": item.get("pageName") or item.get("Page_Name"),
    "ad_text": item.get("adText") or item.get("ad_text"),
    "short_text": logic.summarize_text(ad_text, 150),
    "ad_archive_id": item.get("adId") or item.get("id"),
    "status": "Active" if item.get("Active") else "Inactive",
    "media_url": extracted_image_url,
    "running_days": logic.compute_running_days(item),
    "publisher_platform": item.get("Publisher_Platform", "Facebook")
}
```

---

## 📋 Sample Data Structures

### 1. **Complete Ad Item Structure**
```json
{
    "adId": "123456789",
    "pageId": "987654321", 
    "pageName": "Nike",
    "adText": "Get the latest Nike shoes with amazing comfort and style. Limited time offer!",
    "startDate": "2024-01-01T00:00:00Z",
    "endDate": "2024-12-31T23:59:59Z",
    "Active": true,
    "Publisher_Platform": "Facebook",
    "Categories": ["Fashion", "Sports"],
    "Collation_Count": 5,
    "Entity_Type": "Commercial",
    "Political_Countries": "N/A",
    "Total_Active_Time": "365 days",
    "State_Media_Run_Label": "N/A",
    "snapshot": {
        "cards": [
            {
                "link_url": "https://nike.com/shoes",
                "cta_text": "Shop Now",
                "cta_type": "SHOP_NOW"
            }
        ],
        "page_categories": [
            {
                "page_entity_type": "Retail"
            }
        ],
        "original_picture_url": "https://example.com/ad-image.jpg",
        "page_profile_picture_url": "https://example.com/page-profile.jpg",
        "page_profile_uri": "https://facebook.com/nike"
    }
}
```

### 2. **Extracted Fields for Display**
```json
{
    "ad_archive_id": "123456789",
    "page_id": "987654321",
    "page_name": "Nike",
    "start_date": "2024-01-01",
    "end_date": "2024-12-31",
    "cta_text": "Shop Now",
    "cta_type": "SHOP_NOW",
    "link_url": "https://nike.com/shoes",
    "categories": "Fashion, Sports",
    "collation_count": 5,
    "entity_type": "Commercial",
    "page_entity_type": "Retail",
    "page_profile_picture_url": "https://example.com/page-profile.jpg",
    "page_profile_uri": "https://facebook.com/nike",
    "state_media_run_label": "N/A",
    "total_active_time": "365 days",
    "original_image_url": "https://example.com/ad-image.jpg"
}
```

---

## 🐛 Debug Information

### 1. **Session State Variables**
```python
# Available in st.session_state:
- "last_query_url": "https://www.facebook.com/ads/library/?..."
- "last_query_params": {filters dict}
- "ads_items": [list of ad items]
- "selected_ad_idx": selected ad index
- "save_pending_idx": ad being saved
```

### 2. **Debug Expander** (`app.py`)
```python
with st.expander("Debug info"):
    st.write("Mode:", mode)
    st.write("Last query params:", st.session_state.get("last_query_params"))
    st.write("Last query URL:", st.session_state.get("last_query_url"))
```

### 3. **Common Error Points**
```python
# 1. Missing Apify token
if not apify_token:
    st.error("Apify API token not configured...")

# 2. Apify scrape failure
try:
    items = logic.run_apify_scrape(...)
except Exception as e:
    st.error(f"Apify scrape failed: {e}")

# 3. No results
if not ads_items:
    st.info("No ads found matching your criteria")
```

---

## 🔧 Frontend Customization Points

### 1. **Card Styling** (`components/adCard.py`)
- Modify CSS classes for different card appearances
- Change image dimensions and fitting
- Adjust color schemes and animations

### 2. **Modal Content** (`components/adCard.py`)
- Reorganize detail sections
- Add/remove fields from popup
- Customize action buttons

### 3. **Grid Layout** (`components/mainSearchPage.py`)
- Change columns per row
- Adjust card spacing and sizing
- Modify responsive breakpoints

### 4. **Filter Options** (`components/siderbar.py`)
- Add new filter criteria
- Modify filter options
- Change default values

### 5. **Export Formats** (`components/mainSearchPage.py`)
- Add new export formats
- Modify CSV/JSON structure
- Customize summary reports

---

## 📝 Notes for Frontend Development

1. **Image Handling**: Always provide fallback images for missing ad images
2. **Responsive Design**: Test on mobile devices and different screen sizes
3. **Performance**: Large datasets may need pagination or lazy loading
4. **Error Handling**: Gracefully handle missing data and API failures
5. **User Experience**: Provide clear feedback for loading states and errors
6. **Accessibility**: Ensure proper alt text and keyboard navigation
7. **Caching**: Leverage Streamlit's caching for better performance

This flow analysis should help you understand the complete data pipeline and make informed frontend modifications! 