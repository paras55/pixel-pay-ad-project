from __future__ import annotations
import streamlit as st
import logic
from typing import Optional, List, Dict, Any
from components.dbtoItem import _db_row_to_item
from components.adCard import render_ad_card
from components.dbtoItem import render_saved_ad_detail

def render_saved_ads_page(team: str, rows: List[Dict[str, Any]], card_image_key: Optional[str] = None, footer_format: bool = False):
    st.header(f"Saved Ads — {team}")
    if not rows:
        st.info("No ads saved yet.")
        return

    items = [_db_row_to_item(r) for r in rows]

    # Card grid
    cols_per_row = 3
    for row_start in range(0, len(items), cols_per_row):
        cols = st.columns(cols_per_row, gap="large")
        for i, col in enumerate(cols):
            idx = row_start + i
            if idx >= len(items):
                continue
            ad = items[idx]
            with col:
                render_ad_card(
                    ad,
                    idx,
                    variant="saved",
                    team=team,
                    raw_item=ad,
                    image_url=ad.get(card_image_key) if card_image_key else None,
                    footer=(
                        f"**{ad.get('page_name', '')}** – {ad.get('impressions', '')}, {ad.get('spend', '')}"
                        if footer_format else None
                    ),
                )
                # --- Styled Delete Button with Confirmation ---
                delete_btn = st.button(
                    "🗑️ Remove this Ad",
                    key=f"delete_{team}_{idx}",
                    use_container_width=True,
                    help="Remove this ad from saved ads."
                )
                st.markdown("""
                <style>
                .stButton > button[data-testid^='button'][key^='delete_'] {
                    background: linear-gradient(90deg, #ef4444 60%, #b91c1c 100%) !important;
                    color: #fff !important;
                    border-radius: 8px !important;
                    font-weight: 700 !important;
                    margin-top: 10px !important;
                    margin-bottom: 10px !important;
                    box-shadow: 0 2px 8px rgba(239,68,68,0.10);
                }
                .stButton > button[data-testid^='button'][key^='delete_']:hover {
                    background: linear-gradient(90deg, #b91c1c 60%, #ef4444 100%) !important;
                    color: #fff !important;
                }
                </style>
                """, unsafe_allow_html=True)
                
                # Handle delete button click
                if delete_btn:
                    st.session_state[f"delete_pending_{team}_{idx}"] = True
                    # Debug info
                    ad_id = ad.get("ad_archive_id") or ad.get("adId") or ad.get("id")
                    print(f"Delete button clicked for ad {ad_id} in team {team}")
                
                # Handle delete confirmation
                if st.session_state.get(f"delete_pending_{team}_{idx}", False):
                    st.warning("⚠️ Are you sure you want to remove this ad?")
                    col1, col2 = st.columns([1, 1])
                    with col1:
                        if st.button("✅ Yes, Delete", key=f"confirm_yes_{team}_{idx}", type="primary"):
                            try:
                                # Debug: Print the ad data being deleted
                                ad_id = ad.get("ad_archive_id")
                                print(f"Deleting ad with ID: {ad_id}")
                                print(f"Full ad data: {ad}")
                                
                                # Delete from database
                                success = logic.db_delete_ad(team, ad)
                                # Clear session state
                                st.session_state.pop(f"delete_pending_{team}_{idx}", None)
                                
                                if success:
                                    # Show success message
                                    st.success(f"✅ Ad successfully removed from {team}!")
                                    # Rerun to refresh the page
                                    st.rerun()
                                else:
                                    # Show error message
                                    st.error(f"❌ Failed to delete ad from {team}. Ad may not exist in database.")
                            except Exception as e:
                                st.error(f"❌ Error deleting ad: {str(e)}")
                    with col2:
                        if st.button("❌ Cancel", key=f"confirm_no_{team}_{idx}"):
                            st.session_state.pop(f"delete_pending_{team}_{idx}", None)
                            st.rerun()

    # Detail panel
    sel_key = f"saved_selected_idx_{team}"
    sel_idx = st.session_state.get(sel_key)
    if sel_idx is not None and 0 <= sel_idx < len(rows):
        render_saved_ad_detail(rows[sel_idx])

        # =============================================================================
        # FOOTER DRAWER FOR AD DETAILS
        # =============================================================================
        def render_footer_drawer(item: dict, idx: int):
            f = logic.extract_selected_fields(item)
            page_name = f.get("page_name") or item.get("pageName") or "(no page name)"
            ad_archive_id = f.get("ad_archive_id") or item.get("adId") or item.get("id") or f"#{idx}"
            status = logic.detect_status(item)
            running_days = logic.compute_running_days(item)
            cta_text = f.get("cta_text") or "–"
            format_ = f.get("entity_type") or "–"
            niche = ", ".join(f.get("categories") or []) if f.get("categories") else "–"
            platforms = "Facebook, Instagram"  # Placeholder, adjust if available
            landing_page = f.get("link_url") or "–"
            product_category = f.get("page_entity_type") or "–"
            target_market = f.get("country_code") or "–"
            img_url = f.get("original_image_url") or f.get("original_picture_url")

            st.markdown("""
            <style>
            .fb-footer-drawer {
                position: fixed;
                left: 0; right: 0; bottom: 0;
                background: #fff;
                box-shadow: 0 -2px 16px rgba(0,0,0,0.12);
                border-top: 2px solid #e0e0e0;
                z-index: 9999;
                padding: 1.5rem 2rem;
                max-width: 900px;
                margin: 0 auto;
                border-radius: 16px 16px 0 0;
                font-size: 1rem;
            }
            .fb-footer-drawer .fb-footer-img {
                float: left;
                width: 120px;
                height: 120px;
                object-fit: cover;
                border-radius: 8px;
                margin-right: 1.5rem;
                border: 1px solid #eee;
            }
            .fb-footer-drawer .fb-footer-fields {
                display: grid;
                grid-template-columns: repeat(2, minmax(180px, 1fr));
                gap: 0.5rem 2rem;
            }
            .fb-footer-drawer .fb-footer-label {
                font-weight: 600;
                color: #555;
                margin-right: 0.5rem;
            }
            .fb-footer-drawer .fb-footer-value {
                color: #222;
            }
            .fb-footer-close {
                position: absolute;
                top: 12px; right: 24px;
                font-size: 1.5rem;
                color: #888;
                cursor: pointer;
                background: none;
                border: none;
            }
            </style>
            """, unsafe_allow_html=True)

            close_btn = st.button("×", key=f"footer_close_{idx}", help="Close", args=(), kwargs={}, type="secondary")
            if close_btn:
                st.session_state.pop("footer_drawer_idx", None)

            st.markdown(f"""
            <div class="fb-footer-drawer">
                <img src="{img_url}" class="fb-footer-img"/>
                <div style="margin-bottom:1rem;">
                    <span style="font-size:1.2rem;font-weight:700;">{page_name}</span>
                    <span style="margin-left:1rem;color:#888;">Archive ID: {ad_archive_id}</span>
                </div>
                <div class="fb-footer-fields">
                    <div><span class="fb-footer-label">Status:</span> <span class="fb-footer-value">{status}</span></div>
                    <div><span class="fb-footer-label">Time Running:</span> <span class="fb-footer-value">{running_days or '–'} days</span></div>
                    <div><span class="fb-footer-label">CTA:</span> <span class="fb-footer-value">{cta_text}</span></div>
                    <div><span class="fb-footer-label">Format:</span> <span class="fb-footer-value">{format_}</span></div>
                    <div><span class="fb-footer-label">Niche:</span> <span class="fb-footer-value">{niche}</span></div>
                    <div><span class="fb-footer-label">Platforms:</span> <span class="fb-footer-value">{platforms}</span></div>
                    <div><span class="fb-footer-label">Landing Page:</span> <span class="fb-footer-value">{landing_page}</span></div>
                    <div><span class="fb-footer-label">Product Category:</span> <span class="fb-footer-value">{product_category}</span></div>
                    <div><span class="fb-footer-label">Target Market:</span> <span class="fb-footer-value">{target_market}</span></div>
                </div>
            </div>
            """, unsafe_allow_html=True)