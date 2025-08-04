from __future__ import annotations
import streamlit as st
import logic
from typing import Optional, Dict, Any

def render_ad_card(item: Dict[str, Any], idx: int, variant: str, *,
                   team: Optional[str] = None,
                   raw_item: Optional[Dict[str, Any]] = None,
                   image_url: Optional[str] = None,
                   footer: Optional[str] = None):

    f = logic.extract_selected_fields(item)

    page_name = f.get("page_name") or item.get("pageName") or "(no page name)"
    ad_text = item.get("adText") or item.get("ad_text") or item.get("text") or ""
    short_text = logic.summarize_text(ad_text, 200)
    ad_archive_id = f.get("ad_archive_id") or item.get("adId") or item.get("id") or f"#{idx}"
    status = logic.detect_status(item)
    running_days = logic.compute_running_days(item)

    # Prefer provided image, fallback to logic
    media_url = image_url
    media_type = "image" if media_url else None
    if not media_url:
        snapshot_url = f.get("original_image_url") or f.get("original_picture_url")
        if snapshot_url:
            media_type, media_url = "image", snapshot_url
        else:
            media_type, media_url = logic.extract_primary_media(item)

    with st.container():
        st.markdown("<div class='fb-card-wrapper'>", unsafe_allow_html=True)

        if media_url:
            if media_type == "image":
                st.markdown(
                    f"<div class='fb-card-media'><img src='{media_url}'/></div>",
                    unsafe_allow_html=True,
                )
            elif media_type == "video":
                st.video(media_url)

        st.markdown(
            f"""
            <div class='fb-card'>
                <div class='fb-card-badges'>
                    <span class='fb-card-badge'>{status}</span>
                    <span class='fb-card-badge fb-card-badge-secondary'>{running_days or '–'}D</span>
                </div>
                <div class='fb-card-header'>
                    <div class='fb-card-brand'>{page_name}</div>
                    <div class='fb-card-sub'>Archive ID: {ad_archive_id}</div>
                </div>
                <div class='fb-card-body'>{short_text}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if footer:
            st.markdown(f"<div class='fb-card-footer'>{footer}</div>", unsafe_allow_html=True)

        if variant == "search":
            c1, c2 = st.columns(2)
            if c1.button("See Ad Details", key=f"detail_{idx}"):
                st.session_state["selected_ad_idx"] = idx
            if c2.button("Save", key=f"save_{idx}"):
                st.session_state["save_pending_idx"] = idx
            # if st.session_state.get("save_pending_idx") == idx:
            #     _card_save_ui(idx, f, raw_item or item)

        elif variant == "saved":
            if st.button("See Ad Details", key=f"saved_detail_{team}_{idx}"):
                st.session_state[f"saved_selected_idx_{team}"] = idx

        st.markdown("</div>", unsafe_allow_html=True)