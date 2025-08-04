import streamlit as st

CUSTOM_CSS = """
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

/* Global Dark Theme */
.main .block-container {
    background: var(--primary-bg);
    color: var(--text-primary);
}

/* Hide Streamlit elements */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Typography */
* {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

/* Minimalist Buttons */
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
}

.stSelectbox:focus, .stTextInput:focus, .stNumberInput:focus {
    border-color: var(--accent-primary) !important;
    box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.2) !important;
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

/* Cards and Containers */
.fb-card-wrapper {
    position: relative;
    width: 100%;
}

.fb-card {
    width: 100%;
    border: 1px solid var(--border-color);
    border-radius: 12px;
    background: var(--card-bg);
    overflow: hidden;
    box-shadow: var(--shadow-light);
    transition: all 0.2s ease;
    cursor: pointer;
}

.fb-card:hover {
    box-shadow: var(--shadow-medium);
    transform: translateY(-2px);
    border-color: var(--accent-primary);
}

.fb-card-header {
    padding: 16px;
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.fb-card-brand {
    font-weight: 600;
    font-size: 16px;
    line-height: 1.2;
    color: var(--text-primary);
}

.fb-card-sub {
    font-size: 13px;
    color: var(--text-secondary);
}

.fb-card-body {
    padding: 0 16px 16px 16px;
    font-size: 14px;
    color: var(--text-secondary);
    line-height: 1.5;
}

.fb-card-media img {
    width: 100%;
    height: auto;
    display: block;
}

.fb-card-media video {
    width: 100%;
    display: block;
}

.fb-card-badges {
    position: absolute;
    top: 12px;
    left: 12px;
    display: flex;
    gap: 6px;
}

.fb-card-badge {
    padding: 4px 8px;
    font-size: 11px;
    border-radius: 6px;
    background: rgba(16, 185, 129, 0.2);
    color: var(--success-color);
    font-weight: 600;
    backdrop-filter: blur(10px);
}

.fb-card-badge-secondary {
    background: rgba(139, 92, 246, 0.2);
    color: var(--accent-secondary);
}

/* Filter Bar */
.fb-filter-bar {
    width: 100%;
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    align-items: center;
    margin-bottom: 16px;
    padding: 16px;
    background: var(--secondary-bg);
    border-radius: 12px;
    border: 1px solid var(--border-color);
}

.fb-filter-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 6px 12px;
    border: 1px solid var(--border-color);
    border-radius: 20px;
    background: var(--tertiary-bg);
    font-size: 13px;
    color: var(--text-secondary);
    cursor: default;
    transition: all 0.2s ease;
}

.fb-filter-pill:hover {
    background: var(--card-bg);
    border-color: var(--accent-primary);
}

.fb-filter-pill strong {
    font-weight: 600;
    color: var(--text-primary);
}

/* Detail Table */
.fb-detail-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 14px;
    background: var(--card-bg);
    border-radius: 8px;
    overflow: hidden;
}

.fb-detail-table td {
    padding: 12px 16px;
    border-bottom: 1px solid var(--border-color);
    vertical-align: top;
}

.fb-detail-table td:first-child {
    font-weight: 600;
    width: 35%;
    color: var(--text-secondary);
    background: var(--secondary-bg);
}

.fb-detail-table td:last-child {
    color: var(--text-primary);
}

/* Alerts and Messages */
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

/* Success/Error/Warning Messages */
.success-message {
    background: rgba(16, 185, 129, 0.1);
    border: 1px solid var(--success-color);
    color: var(--success-color);
}

.warning-message {
    background: rgba(245, 158, 11, 0.1);
    border: 1px solid var(--warning-color);
    color: var(--warning-color);
}

.error-message {
    background: rgba(239, 68, 68, 0.1);
    border: 1px solid var(--error-color);
    color: var(--error-color);
}

/* Loading Spinner */
.stSpinner > div {
    border-color: var(--accent-primary) !important;
}

/* Sidebar */
.sidebar .sidebar-content {
    background: var(--secondary-bg);
    border-right: 1px solid var(--border-color);
}

/* Responsive Design */
@media (max-width: 768px) {
    .fb-filter-bar {
        flex-direction: column;
        align-items: stretch;
    }
    
    .fb-card {
        margin-bottom: 16px;
    }
}
</style>
"""

def inject_global_css() -> None:
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)