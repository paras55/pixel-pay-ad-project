from __future__ import annotations
import streamlit as st
import logic
from typing import Optional, Dict, Any

from components.dbtoItem import _db_row_to_item

def render_sidebar_search(extra_input: Optional[Dict[str, Any]] = None, search_mode: Optional[str] = None):
    st.sidebar.header("Query Parameters")

    # Country select
    country_labels = [n for n, _ in logic.COMMON_COUNTRIES] + ["Custom…"]
    country_label_sel = st.sidebar.selectbox("Country", options=country_labels, index=0, key="search_country_sel")
    if country_label_sel == "Custom…":
        country_code = st.sidebar.text_input("ISO country code", value="", key="search_country_custom").strip().upper() or "US"
        country_label = country_code
    else:
        country_code = dict(logic.COMMON_COUNTRIES)[country_label_sel]
        country_label = country_label_sel

    # Keyword input
    keyword_input = st.sidebar.text_input("Keyword", value="", key="search_keyword")

    # Ad Category radio
    ad_category_label = st.sidebar.radio(
        "Ad category", options=list(logic.CATEGORY_LABEL_TO_ADTYPE.keys()), index=0, key="search_category"
    )
    ad_type_param = logic.CATEGORY_LABEL_TO_ADTYPE[ad_category_label]

    # Active status radio
    active_status_label = st.sidebar.radio(
        "Active status", options=list(logic.ACTIVE_STATUS_LABEL_TO_PARAM.keys()), index=0, key="search_status"
    )
    active_status_param = logic.ACTIVE_STATUS_LABEL_TO_PARAM[active_status_label]

    # Search mode select
    search_mode_label = st.sidebar.selectbox(
        "Search matching", options=list(logic.SEARCH_MODE_LABEL_TO_PARAM.keys()), index=0, key="search_match"
    )
    search_mode_param = logic.SEARCH_MODE_LABEL_TO_PARAM[search_mode_label]

    # Number of ads
    count = st.sidebar.number_input(
        "Number of ads", min_value=1, max_value=1000, value=100, step=1, key="search_count"
    )

    # Install hint if apify-client missing
    ApifyClient, import_err = logic._import_apify_client()
    if import_err or ApifyClient is None:
        st.sidebar.warning("`apify-client` not installed. Run: `pip install apify-client`.")

    # Fetch button
    fetch_clicked = st.sidebar.button("Fetch ads", type="primary", key="search_fetch_btn")

    # Prepare filter dict
    kw_raw = keyword_input.strip()
    kw_display = f'"{kw_raw}"' if search_mode_param == "keyword_exact" and not (kw_raw.startswith('"') and kw_raw.endswith('"')) else kw_raw

    filters = {
        "country_code": country_code,
        "country_label": country_label,
        "keyword_raw": kw_raw,
        "keyword_display": kw_display,
        "ad_category": ad_category_label,
        "ad_type_param": ad_type_param,
        "active_status_label": active_status_label,
        "active_status_param": active_status_param,
        "search_mode_label": search_mode_label,
        "search_mode_param": search_mode_param,
        "count": int(count),
    }

    # --- Input Validation ---
    validation_error = None
    if search_mode:
        if search_mode == "Keyword Search":
            if not kw_raw:
                validation_error = "Please enter a keyword to search."
        elif search_mode == "Page ID Search":
            if not kw_raw and not extra_input.get("page_id"):
                validation_error = "Please enter a Page ID."
        elif search_mode == "Landing Page Domain Search":
            if not kw_raw and not extra_input.get("landing_domain"):
                validation_error = "Please enter a landing page domain."
    if count < 1:
        validation_error = "Please enter a valid number of ads to fetch."

    if validation_error:
        st.sidebar.warning(validation_error)
        fetch_clicked = False

    return filters, fetch_clicked

def render_sidebar_saved_mode():
    st.sidebar.header("Saved Ads")
    team_choice = st.sidebar.selectbox(
        "Select team table",
        options=["(choose)"] + logic.get_all_teams(),
        index=0,
        key="saved_team_sel",
    )
    return None if team_choice == "(choose)" else team_choice


def render_filter_bar(*, country_label: str, ad_category_label: str, keyword: str, active_status_label: str):
    st.markdown(
        f"""
        <div class='fb-filter-bar'>
            <div class='fb-filter-pill'><strong>{country_label}</strong></div>
            <div class='fb-filter-pill'><strong>{ad_category_label}</strong></div>
            <div class='fb-filter-pill'>"{keyword}"</div>
            <div class='fb-filter-pill fb-filter-pill-status'><strong>{active_status_label}</strong></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _card_save_ui(idx: int, ad_fields: dict, raw_item: dict):
    table = st.selectbox("Save to team", options=logic.get_all_teams(), key=f"save_select_{idx}")
    if st.button("Confirm save", key=f"confirm_save_{idx}"):
        logic.db_insert_team(table, ad_fields, raw_item)
        st.success(f"Saved to {table}!")
        st.session_state.pop("save_pending_idx", None)