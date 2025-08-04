import streamlit as st
import logic
import json
import streamlit.components.v1 as components
import uuid

def _make_detail_table_html(rows):
    cells = []
    for label, value in rows:
        val = value if value not in (None, "", [], {}) else "–"
        cells.append(f"<tr><td>{label}</td><td>{val}</td></tr>")
    return f"<table class='fb-detail-table'>{''.join(cells)}</table>"

def _db_row_to_item(row: dict) -> dict:
    """
    Convert DB row -> item-like dict for extract_selected_fields/media helpers.
    Uses raw_json if stored; otherwise constructs minimal snapshot.
    """
    if isinstance(row.get("raw_json"), dict):
        return row["raw_json"]

    snap = {
        "link_url": row.get("link_url"),
        "cards": {
            "cta_text": row.get("cta_text"),
            "cta_type": row.get("cta_type"),
            "link_url": row.get("link_url"),
        },
        "page_categories": {
            "page_entity_type": row.get("page_entity_type"),
        },
        "images": {
            "original_image_url": row.get("original_image_url"),
        },
        "page_profile_picture_url": row.get("page_profile_picture_url"),
        "page_profile_uri": row.get("page_profile_uri"),
    }

    return {
        "ad_archive_id": row.get("ad_archive_id"),
        "categories": row.get("categories"),
        "collation_count": row.get("collation_count"),
        "collation_id": row.get("collation_id"),
        "start_date": row.get("start_date"),
        "end_date": row.get("end_date"),
        "entity_type": row.get("entity_type"),
        "is_active": bool(row.get("is_active")),
        "page_id": row.get("page_id"),
        "page_name": row.get("page_name"),
        "state_media_run_label": row.get("state_media_run_label"),
        "total_active_time": row.get("total_active_time"),
        "snapshot": snap,
    }
    
def render_saved_ad_detail(db_row: dict):
    item_like = _db_row_to_item(db_row)
    f = logic.extract_selected_fields(item_like)

    page_name = f.get("page_name") or "(no page name)"
    ad_archive_id = f.get("ad_archive_id") or "–"

    img_from_snapshot = f.get("original_image_url") or f.get("original_picture_url")
    if img_from_snapshot:
        media_type, media_url = "image", img_from_snapshot
    else:
        media_type, media_url = logic.extract_primary_media(item_like)

    st.markdown("---")
    st.markdown(
        f"<h3 style='margin-bottom:0;'>{page_name}</h3>"
        f"<div style='color:#666;font-size:0.9rem;'>Ad Archive ID: {ad_archive_id}</div>",
        unsafe_allow_html=True,
    )

    left, right = st.columns([3, 1], gap="large")
    with left:
        if media_url:
            if media_type == "image":
                st.image(media_url, use_column_width=True)
            elif media_type == "video":
                st.video(media_url)
        if f.get("link_url"):
            st.markdown(f"[Ad Destination URL]({f['link_url']})")
        if f.get("page_profile_uri"):
            st.markdown(f"[Page Profile]({f['page_profile_uri']})")

    with right:
        st.markdown("### Details")
        info_rows = [
            ("ad_archive_id", f.get("ad_archive_id")),
            ("categories", f.get("categories")),
            ("collation_count", f.get("collation_count")),
            ("collation_id", f.get("collation_id")),
            ("start_date", f.get("start_date")),
            ("end_date", f.get("end_date")),
            ("entity_type", f.get("entity_type")),
            ("is_active", f.get("is_active")),
            ("page_id", f.get("page_id")),
            ("page_name", f.get("page_name")),
            ("cta_text", f.get("cta_text")),
            ("cta_type", f.get("cta_type")),
            ("page_entity_type", f.get("page_entity_type")),
            ("page_profile_picture_url", f.get("page_profile_picture_url")),
            ("page_profile_uri", f.get("page_profile_uri")),
            ("state_media_run_label", f.get("state_media_run_label")),
            ("total_active_time", f.get("total_active_time")),
            ("original_image_url", f.get("original_image_url")),
        ]
        st.markdown(_make_detail_table_html(info_rows), unsafe_allow_html=True)

    raw = db_row.get("raw_json")
    if isinstance(raw, dict):
        with st.expander("All fields (raw JSON from DB)"):
            st.json(raw)
    else:
        with st.expander("DB row"):
            st.json(db_row)

    with st.expander("Debug: Extracted fields"):
        st.json(f)

    
