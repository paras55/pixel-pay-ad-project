import streamlit as st
import streamlit.components.v1 as components

# Page config
st.set_page_config(
    page_title="Simple Popup Demo",
    page_icon="🎯",
    layout="wide"
)

st.title("🎯 Simple Popup Demo")
st.markdown("Click the buttons below to see different popup styles!")

# Method 1: Using HTML/CSS/JS with components.html
st.header("Method 1: Custom HTML Popup")

components.html("""
<style>
    .popup-btn {
        background: #4CAF50;
        color: white;
        padding: 10px 20px;
        border: none;
        border-radius: 5px;
        cursor: pointer;
        font-size: 16px;
        margin: 10px;
    }
    
    .popup-btn:hover {
        background: #45a049;
    }
    
    .modal {
        display: none;
        position: fixed;
        z-index: 1000;
        left: 0;
        top: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0,0,0,0.5);
    }
    
    .modal-content {
        background-color: white;
        margin: 15% auto;
        padding: 20px;
        border-radius: 10px;
        width: 400px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        animation: slideIn 0.3s ease-out;
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(-50px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .close {
        color: #aaa;
        float: right;
        font-size: 28px;
        font-weight: bold;
        cursor: pointer;
    }
    
    .close:hover {
        color: black;
    }
</style>

<button class="popup-btn" onclick="openModal()">Open Simple Popup</button>

<div id="myModal" class="modal">
    <div class="modal-content">
        <span class="close" onclick="closeModal()">&times;</span>
        <h2>Hello from Popup! 👋</h2>
        <p>This is a simple popup created with HTML, CSS, and JavaScript.</p>
        <p><strong>Features:</strong></p>
        <ul>
            <li>Smooth animation</li>
            <li>Click outside to close</li>
            <li>Responsive design</li>
        </ul>
        <button class="popup-btn" onclick="closeModal()">Close</button>
    </div>
</div>

<script>
    function openModal() {
        document.getElementById('myModal').style.display = 'block';
    }
    
    function closeModal() {
        document.getElementById('myModal').style.display = 'none';
    }
    
    // Close when clicking outside
    window.onclick = function(event) {
        const modal = document.getElementById('myModal');
        if (event.target == modal) {
            modal.style.display = 'none';
        }
    }
    
    // Close with ESC key
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape') {
            closeModal();
        }
    });
</script>
""", height=100)

st.markdown("---")

# Method 2: Using Streamlit session state for popup-like behavior
st.header("Method 2: Streamlit Session State Popup")

if 'show_popup' not in st.session_state:
    st.session_state.show_popup = False

col1, col2 = st.columns(2)

with col1:
    if st.button("Show Streamlit Popup", type="primary"):
        st.session_state.show_popup = True

with col2:
    if st.button("Hide Popup"):
        st.session_state.show_popup = False

if st.session_state.show_popup:
    st.markdown("""
    <div style="
        position: fixed; 
        top: 50%; 
        left: 50%; 
        transform: translate(-50%, -50%); 
        background: white; 
        padding: 20px; 
        border-radius: 10px; 
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        z-index: 1000;
        border: 2px solid #4CAF50;
        min-width: 300px;
        text-align: center;
    ">
        <h3 style="color: #4CAF50; margin-top: 0;">🎉 Streamlit Popup!</h3>
        <p>This popup uses Streamlit's session state.</p>
        <p>Click "Hide Popup" to close it.</p>
    </div>
    
    <div style="
        position: fixed; 
        top: 0; 
        left: 0; 
        width: 100%; 
        height: 100%; 
        background: rgba(0,0,0,0.5); 
        z-index: 999;
    "></div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Method 3: Advanced popup with form
st.header("Method 3: Interactive Popup with Form")

components.html("""
<style>
    .form-popup-btn {
        background: linear-gradient(45deg, #667eea, #764ba2);
        color: white;
        padding: 12px 24px;
        border: none;
        border-radius: 8px;
        cursor: pointer;
        font-size: 16px;
        font-weight: 600;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        transition: all 0.3s ease;
    }
    
    .form-popup-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.3);
    }
    
    .form-modal {
        display: none;
        position: fixed;
        z-index: 1000;
        left: 0;
        top: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0,0,0,0.6);
        backdrop-filter: blur(5px);
    }
    
    .form-modal-content {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        margin: 5% auto;
        padding: 30px;
        border-radius: 15px;
        width: 500px;
        max-width: 90%;
        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        animation: popIn 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55);
    }
    
    @keyframes popIn {
        0% {
            opacity: 0;
            transform: scale(0.5) translateY(-50px);
        }
        100% {
            opacity: 1;
            transform: scale(1) translateY(0);
        }
    }
    
    .form-close {
        color: #666;
        float: right;
        font-size: 28px;
        font-weight: bold;
        cursor: pointer;
        background: none;
        border: none;
        padding: 5px;
        border-radius: 50%;
        width: 35px;
        height: 35px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .form-close:hover {
        background: rgba(0,0,0,0.1);
        color: #333;
    }
    
    .form-group {
        margin-bottom: 20px;
    }
    
    .form-group label {
        display: block;
        margin-bottom: 5px;
        font-weight: 600;
        color: #333;
    }
    
    .form-group input, .form-group textarea {
        width: 100%;
        padding: 10px;
        border: 2px solid #ddd;
        border-radius: 8px;
        font-size: 14px;
        transition: border-color 0.3s ease;
        box-sizing: border-box;
    }
    
    .form-group input:focus, .form-group textarea:focus {
        outline: none;
        border-color: #667eea;
    }
    
    .submit-btn {
        background: #667eea;
        color: white;
        padding: 12px 30px;
        border: none;
        border-radius: 8px;
        cursor: pointer;
        font-size: 16px;
        font-weight: 600;
        width: 100%;
        transition: all 0.3s ease;
    }
    
    .submit-btn:hover {
        background: #5a67d8;
        transform: translateY(-1px);
    }
</style>

<button class="form-popup-btn" onclick="openFormModal()">📝 Open Contact Form</button>

<div id="formModal" class="form-modal">
    <div class="form-modal-content">
        <button class="form-close" onclick="closeFormModal()">&times;</button>
        <h2 style="margin-top: 0; color: #333; text-align: center;">✨ Contact Us</h2>
        <form onsubmit="handleSubmit(event)">
            <div class="form-group">
                <label for="name">Name:</label>
                <input type="text" id="name" name="name" required>
            </div>
            <div class="form-group">
                <label for="email">Email:</label>
                <input type="email" id="email" name="email" required>
            </div>
            <div class="form-group">
                <label for="message">Message:</label>
                <textarea id="message" name="message" rows="4" required></textarea>
            </div>
            <button type="submit" class="submit-btn">Send Message 🚀</button>
        </form>
    </div>
</div>

<script>
    function openFormModal() {
        document.getElementById('formModal').style.display = 'block';
    }
    
    function closeFormModal() {
        document.getElementById('formModal').style.display = 'none';
    }
    
    function handleSubmit(event) {
        event.preventDefault();
        const name = document.getElementById('name').value;
        const email = document.getElementById('email').value;
        const message = document.getElementById('message').value;
        
        alert(`Thank you ${name}! Your message has been received.\\n\\nEmail: ${email}\\nMessage: ${message}`);
        closeFormModal();
        
        // Reset form
        event.target.reset();
    }
    
    // Close when clicking outside
    window.onclick = function(event) {
        const modal = document.getElementById('formModal');
        if (event.target == modal) {
            closeFormModal();
        }
    }
</script>
""", height=100)

st.markdown("---")

# Method 4: Card-based popup
st.header("Method 4: Card-Based Popup")

# Sample data
cards_data = [
    {"id": 1, "title": "Product A", "description": "Amazing product with great features", "price": "$99"},
    {"id": 2, "title": "Product B", "description": "Another fantastic product", "price": "$149"},
    {"id": 3, "title": "Product C", "description": "The best product in our lineup", "price": "$199"}
]

components.html(f"""
<style>
    .cards-container {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 20px;
        margin: 20px 0;
    }}
    
    .card {{
        background: white;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        cursor: pointer;
        transition: all 0.3s ease;
        border: 2px solid transparent;
    }}
    
    .card:hover {{
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        border-color: #667eea;
    }}
    
    .card-title {{
        font-size: 18px;
        font-weight: 600;
        margin-bottom: 10px;
        color: #333;
    }}
    
    .card-description {{
        color: #666;
        margin-bottom: 15px;
        font-size: 14px;
    }}
    
    .card-price {{
        font-size: 20px;
        font-weight: 700;
        color: #667eea;
    }}
    
    .card-modal {{
        display: none;
        position: fixed;
        z-index: 1000;
        left: 0;
        top: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0,0,0,0.7);
    }}
    
    .card-modal-content {{
        background: white;
        margin: 10% auto;
        padding: 30px;
        border-radius: 15px;
        width: 600px;
        max-width: 90%;
        position: relative;
        animation: cardSlideIn 0.3s ease-out;
    }}
    
    @keyframes cardSlideIn {{
        from {{
            opacity: 0;
            transform: scale(0.8) translateY(-100px);
        }}
        to {{
            opacity: 1;
            transform: scale(1) translateY(0);
        }}
    }}
    
    .card-modal-close {{
        position: absolute;
        right: 15px;
        top: 15px;
        background: none;
        border: none;
        font-size: 24px;
        cursor: pointer;
        color: #666;
        padding: 5px;
        border-radius: 50%;
        width: 35px;
        height: 35px;
        display: flex;
        align-items: center;
        justify-content: center;
    }}
    
    .card-modal-close:hover {{
        background: #f0f0f0;
        color: #333;
    }}
    
    .modal-header {{
        border-bottom: 2px solid #f0f0f0;
        padding-bottom: 20px;
        margin-bottom: 20px;
    }}
    
    .modal-title {{
        font-size: 24px;
        font-weight: 700;
        color: #333;
        margin: 0;
    }}
    
    .modal-price {{
        font-size: 28px;
        font-weight: 700;
        color: #667eea;
        margin: 10px 0;
    }}
    
    .buy-btn {{
        background: linear-gradient(45deg, #667eea, #764ba2);
        color: white;
        padding: 15px 30px;
        border: none;
        border-radius: 8px;
        cursor: pointer;
        font-size: 16px;
        font-weight: 600;
        width: 100%;
        margin-top: 20px;
        transition: all 0.3s ease;
    }}
    
    .buy-btn:hover {{
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.2);
    }}
</style>

<div class="cards-container">
    {' '.join([f'''
    <div class="card" onclick="openCardModal({card['id']})">
        <div class="card-title">{card['title']}</div>
        <div class="card-description">{card['description']}</div>
        <div class="card-price">{card['price']}</div>
    </div>
    ''' for card in cards_data])}
</div>

{' '.join([f'''
<div id="cardModal{card['id']}" class="card-modal">
    <div class="card-modal-content">
        <button class="card-modal-close" onclick="closeCardModal({card['id']})">&times;</button>
        <div class="modal-header">
            <h2 class="modal-title">{card['title']}</h2>
            <div class="modal-price">{card['price']}</div>
        </div>
        <p style="font-size: 16px; line-height: 1.6; color: #666;">
            {card['description']} - This is a detailed description of the product with all its amazing features and benefits. 
            Perfect for customers who want the best quality and value.
        </p>
        <ul style="color: #666; margin: 20px 0;">
            <li>Premium quality materials</li>
            <li>30-day money-back guarantee</li>
            <li>Free shipping worldwide</li>
            <li>24/7 customer support</li>
        </ul>
        <button class="buy-btn" onclick="handlePurchase('{card['title']}', '{card['price']}')">
            🛒 Buy Now - {card['price']}
        </button>
    </div>
</div>
''' for card in cards_data])}

<script>
    function openCardModal(cardId) {{
        document.getElementById('cardModal' + cardId).style.display = 'block';
    }}
    
    function closeCardModal(cardId) {{
        document.getElementById('cardModal' + cardId).style.display = 'none';
    }}
    
    function handlePurchase(title, price) {{
        alert(`Thank you for your interest in ${{title}} (${{price}})!\\n\\nRedirecting to checkout...`);
        // Close all modals
        {'; '.join([f"closeCardModal({card['id']})" for card in cards_data])};
    }}
    
    // Close when clicking outside
    window.onclick = function(event) {{
        {' '.join([f'''
        const modal{card['id']} = document.getElementById('cardModal{card['id']}');
        if (event.target == modal{card['id']}) {{
            closeCardModal({card['id']});
        }}
        ''' for card in cards_data])}
    }}
</script>
""", height=400)

st.markdown("---")

st.markdown("""
### 💡 Tips for Using Popups in Streamlit:

1. **Method 1 (HTML/CSS/JS)**: Most flexible, full control over styling and behavior
2. **Method 2 (Session State)**: Pure Streamlit, but limited styling options
3. **Method 3 (Interactive Forms)**: Great for collecting user input
4. **Method 4 (Card-based)**: Perfect for product catalogs or content galleries

**Best Practices:**
- Always provide a way to close the popup (X button, ESC key, click outside)
- Use smooth animations for better user experience
- Make popups responsive for mobile devices
- Keep content concise and focused
- Test on different screen sizes
""")