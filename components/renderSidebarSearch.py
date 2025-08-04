import streamlit as st

def render_sidebar_search(extra_input: dict = None, search_mode: str = "Keyword Search"):
    extra_input = extra_input or {}

    st.sidebar.markdown("#### Filters")

    # Country
    country_code = st.sidebar.selectbox(
        "Country",
        ["US", "CA", "GB", "AU", "IN"],
        index=0,
        key="country_code_select"
    )

    # Ad type
    ad_type_param = st.sidebar.selectbox(
        "Ad Type",
        ["All", "Political and Issue Ads", "Non-Political Ads"],
        index=0,
        key="ad_type_select"
    )

    # Ad status
    active_status_param = st.sidebar.selectbox(
        "Ad Status",
        ["Active", "Inactive", "All"],
        index=0,
        key="ad_status_select"
    )

    # Count
    count = st.sidebar.slider(
        "Number of Ads to Fetch",
        min_value=10,
        max_value=100,
        step=10,
        value=20,
        key="ad_count_slider"
    )

    # Fetch button
    fetch_clicked = st.sidebar.button("Fetch Ads", key="fetch_ads_btn")

    # Merge all filters
    filters = {
    "country_code": country_code,
    "ad_type_param": (
        "ALL" if ad_type_param == "All"
        else "POLITICAL_AND_ISSUE" if ad_type_param.startswith("Political")
        else "NON_POLITICAL"
    ),
    "active_status_param": active_status_param.lower() if active_status_param != "All" else "all",
    "count": count,
    "search_mode": search_mode
}

    filters.update(extra_input)

    return filters, fetch_clicked

