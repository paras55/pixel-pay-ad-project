ad_card_css = """
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

    .ad-card {
        background: var(--card-bg);
        border-radius: 16px;
        padding: 0;
        box-shadow: var(--shadow-light);
        cursor: pointer;
        transition: all 0.3s ease;
        border: 1px solid var(--border-color);
        overflow: hidden;
        height: 100%;
        display: flex;
        flex-direction: column;
        min-height: 400px;
    }
    .ad-card:hover {
        transform: translateY(-4px);
        box-shadow: var(--shadow-heavy);
        border-color: var(--accent-primary);
    }
    .ad-card-image {
        width: 100%;
        height: 220px;
        object-fit: cover;
        object-position: center;
        border-radius: 0;
        background: var(--secondary-bg);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 12px;
        color: var(--text-secondary);
    }
    .ad-card-image:before {
        content: "Loading...";
        display: none;
    }
    .ad-card-image[src*="placeholder"] {
        background: linear-gradient(135deg, var(--accent-primary) 0%, var(--accent-secondary) 100%);
        color: var(--text-primary);
        font-weight: 600;
    }
    .ad-card-content {
        padding: 20px;
        flex: 1;
        display: flex;
        flex-direction: column;
        min-height: 180px;
    }
    .ad-card-header {
        display: flex;
        align-items: center;
        margin-bottom: 16px;
    }
    .ad-brand-icon {
        width: 32px;
        height: 32px;
        border-radius: 8px;
        background: linear-gradient(135deg, var(--accent-primary) 0%, var(--accent-secondary) 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        color: var(--text-primary);
        font-weight: bold;
        margin-right: 12px;
        font-size: 14px;
        flex-shrink: 0;
        box-shadow: var(--shadow-light);
    }
    .ad-page-name {
        font-size: 16px;
        font-weight: 600;
        color: var(--text-primary);
        flex: 1;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }
    .ad-status-badge {
        color: var(--text-primary);
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: 600;
        flex-shrink: 0;
        background: rgba(16, 185, 129, 0.2);
        border: 1px solid var(--success-color);
    }
    .ad-description {
        color: var(--text-secondary);
        margin-bottom: 16px;
        font-size: 14px;
        line-height: 1.5;
        flex: 1;
        overflow: hidden;
        display: -webkit-box;
        -webkit-line-clamp: 3;
        -webkit-box-orient: vertical;
    }
    .ad-footer {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding-top: 16px;
        border-top: 1px solid var(--border-color);
        margin-top: auto;
    }
    .ad-id {
        font-size: 12px;
        color: var(--text-muted);
        font-weight: 500;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        max-width: 60%;
    }
    .ad-platform {
        background: rgba(139, 92, 246, 0.2);
        color: var(--accent-secondary);
        padding: 4px 10px;
        border-radius: 8px;
        font-size: 11px;
        font-weight: 600;
        flex-shrink: 0;
        border: 1px solid var(--accent-secondary);
    }
    
    /* Modal Styles */
    .ad-modal {
        display: none;
        position: fixed;
        z-index: 10000;
        left: 0;
        top: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0,0,0,0.8);
        backdrop-filter: blur(10px);
    }
    .ad-modal-content {
        background-color: var(--card-bg);
        margin: 2% auto;
        padding: 0;
        border-radius: 20px;
        width: 90%;
        max-width: 1200px;
        max-height: 90vh;
        overflow-y: auto;
        position: relative;
        box-shadow: var(--shadow-heavy);
        border: 1px solid var(--border-color);
    }
    .ad-modal-close {
        position: absolute;
        right: 20px;
        top: 20px;
        background: var(--secondary-bg);
        border: 1px solid var(--border-color);
        border-radius: 50%;
        width: 40px;
        height: 40px;
        font-size: 24px;
        cursor: pointer;
        z-index: 10001;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.3s ease;
        color: var(--text-secondary);
    }
    .ad-modal-close:hover {
        background: var(--tertiary-bg);
        transform: scale(1.1);
        color: var(--text-primary);
    }
    .ad-modal-body {
        display: flex;
        min-height: 600px;
    }
    .ad-modal-left {
        flex: 1;
        padding: 30px;
        border-right: 1px solid var(--border-color);
        background: var(--secondary-bg);
    }
    .ad-modal-right {
        flex: 1;
        padding: 30px;
        background: var(--card-bg);
        overflow-y: auto;
        max-height: 80vh;
    }
    .ad-modal-header {
        display: flex;
        align-items: center;
        margin-bottom: 24px;
    }
    .ad-modal-brand-icon {
        width: 44px;
        height: 44px;
        border-radius: 10px;
        background: linear-gradient(135deg, var(--accent-primary) 0%, var(--accent-secondary) 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        color: var(--text-primary);
        font-weight: bold;
        margin-right: 16px;
        font-size: 18px;
        box-shadow: var(--shadow-light);
    }
    .ad-modal-title {
        font-size: 24px;
        font-weight: 700;
        color: var(--text-primary);
        flex: 1;
    }
    .ad-modal-status {
        color: var(--text-primary);
        padding: 6px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        background: rgba(16, 185, 129, 0.2);
        border: 1px solid var(--success-color);
    }
    .ad-modal-image {
        width: 100%;
        height: 300px;
        object-fit: cover;
        object-position: center;
        border-radius: 12px;
        margin-bottom: 20px;
        box-shadow: var(--shadow-medium);
        background: var(--secondary-bg);
    }
    .ad-text-section {
        background: var(--tertiary-bg);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: var(--shadow-light);
        border: 1px solid var(--border-color);
    }
    .ad-text-content {
        color: var(--text-secondary);
        line-height: 1.6;
        font-size: 14px;
    }
    .ad-stats-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 16px;
    }
    .ad-stat-item {
        background: var(--tertiary-bg);
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        box-shadow: var(--shadow-light);
        border: 1px solid var(--border-color);
    }
    .ad-stat-number {
        font-size: 24px;
        font-weight: 700;
        color: var(--accent-primary);
        display: block;
        margin-bottom: 5px;
    }
    .ad-stat-label {
        font-size: 12px;
        color: var(--text-muted);
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Right side details */
    .ad-details-title {
        font-size: 20px;
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: 25px;
        padding-bottom: 15px;
        border-bottom: 2px solid var(--border-color);
    }
    .ad-detail-section {
        margin-bottom: 25px;
        background: var(--secondary-bg);
        border-radius: 12px;
        padding: 20px;
        border: 1px solid var(--border-color);
    }
    .ad-section-title {
        font-size: 16px;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 15px;
        padding-bottom: 8px;
        border-bottom: 1px solid var(--border-color);
    }
    .ad-detail-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px 0;
        border-bottom: 1px solid var(--border-color);
    }
    .ad-detail-row:last-child {
        border-bottom: none;
    }
    .ad-detail-label {
        font-size: 13px;
        color: var(--text-muted);
        font-weight: 500;
        min-width: 120px;
    }
    .ad-detail-value {
        font-size: 13px;
        color: var(--text-primary);
        font-weight: 500;
        text-align: right;
        max-width: 200px;
        word-break: break-word;
    }
    .ad-platform-badge {
        background: rgba(139, 92, 246, 0.2);
        color: var(--accent-secondary);
        padding: 4px 8px;
        border-radius: 6px;
        font-size: 11px;
        font-weight: 600;
        border: 1px solid var(--accent-secondary);
    }
    .ad-category-badge {
        background: rgba(99, 102, 241, 0.2);
        color: var(--accent-primary);
        padding: 4px 8px;
        border-radius: 6px;
        font-size: 11px;
        font-weight: 600;
        max-width: 150px;
        word-break: break-word;
        border: 1px solid var(--accent-primary);
    }
    .ad-action-buttons {
        display: flex;
        flex-direction: column;
        gap: 12px;
        margin-top: 25px;
        padding-top: 20px;
        border-top: 1px solid var(--border-color);
    }
    .ad-btn-primary {
        background: linear-gradient(135deg, var(--accent-primary) 0%, var(--accent-secondary) 100%);
        color: var(--text-primary);
        border: none;
        padding: 14px 24px;
        border-radius: 12px;
        font-size: 14px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        text-decoration: none;
        text-align: center;
        box-shadow: var(--shadow-light);
    }
    .ad-btn-primary:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-medium);
        background: linear-gradient(135deg, var(--accent-secondary) 0%, var(--accent-primary) 100%);
    }
    .ad-btn-secondary {
        background: var(--secondary-bg);
        color: var(--text-secondary);
        border: 1px solid var(--border-color);
        padding: 14px 24px;
        border-radius: 12px;
        font-size: 14px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    .ad-btn-secondary:hover {
        background: var(--tertiary-bg);
        color: var(--text-primary);
        border-color: var(--accent-primary);
    }
    
    /* Download Section */
    .download-section {
        background: var(--secondary-bg);
        border-radius: 12px;
        padding: 20px;
        margin-top: 20px;
        border: 1px solid var(--border-color);
    }
    .download-title {
        font-size: 16px;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 16px;
    }
    .download-buttons {
        display: flex;
        gap: 12px;
        flex-wrap: wrap;
    }
    .download-btn {
        background: linear-gradient(135deg, var(--success-color) 0%, #059669 100%);
        color: var(--text-primary);
        border: none;
        padding: 10px 20px;
        border-radius: 8px;
        font-size: 13px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: var(--shadow-light);
    }
    .download-btn:hover {
        transform: translateY(-1px);
        box-shadow: var(--shadow-medium);
        background: linear-gradient(135deg, #059669 0%, var(--success-color) 100%);
    }
    .action-buttons-section {
        margin-top: 20px;
        padding-top: 20px;
        border-top: 1px solid var(--border-color);
    }
    .action-buttons {
        display: flex;
        gap: 12px;
        flex-wrap: wrap;
    }
    .action-btn {
        background: var(--secondary-bg);
        color: var(--text-secondary);
        border: 1px solid var(--border-color);
        padding: 10px 20px;
        border-radius: 8px;
        font-size: 13px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    .action-btn:hover {
        background: var(--tertiary-bg);
        color: var(--text-primary);
        border-color: var(--accent-primary);
    }
    .action-btn.close-btn {
        background: rgba(239, 68, 68, 0.2);
        color: var(--error-color);
        border-color: var(--error-color);
    }
    .action-btn.close-btn:hover {
        background: rgba(239, 68, 68, 0.3);
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .ad-modal-body {
            flex-direction: column;
        }
        .ad-modal-left {
            border-right: none;
            border-bottom: 1px solid var(--border-color);
        }
        .ad-modal-content {
            width: 95%;
            margin: 1% auto;
        }
        .ad-stats-grid {
            grid-template-columns: 1fr;
        }
        .ad-detail-row {
            flex-direction: column;
            align-items: flex-start;
            gap: 5px;
        }
        .ad-detail-value {
            text-align: left;
            max-width: none;
        }
        .ad-card {
            min-height: 350px;
        }
        .ad-card-image {
            height: 180px;
        }
    }
</style>
"""