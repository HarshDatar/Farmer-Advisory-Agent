"""
app.py — Kisan Saathi Dashboard
Run: streamlit run app.py
"""
from __future__ import annotations
import json
from pathlib import Path
import streamlit as st
from FarmerAgent import FarmerProfile, AgentSetupError, DISTRICTS, KNOWN_SOIL_TYPES, load_agent

st.set_page_config(
    page_title="Kisan Saathi",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── DB ────────────────────────────────────────────────────────
DB_PATH = Path(__file__).resolve().parent / "farmers_db.json"

def db_load() -> list[dict]:
    if DB_PATH.exists():
        try:
            return json.loads(DB_PATH.read_text(encoding="utf-8"))
        except Exception:
            return []
    return []

def db_save(farmers: list[dict]) -> None:
    DB_PATH.write_text(json.dumps(farmers, indent=2), encoding="utf-8")


# ── CSS ───────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');

html, body, [data-testid="stAppViewContainer"] {
    background: #F4F8F4 !important;
    color: #3E2723 !important;
    font-family: 'Outfit', sans-serif !important;
}
#MainMenu { display: none !important; }
footer { display: none !important; }
.stAppDeployButton { display: none !important; }
[data-testid="stDecoration"] { display: none !important; }

[data-testid="stHeader"] {
    background: transparent !important;
}

/* ── Fix sidebar toggle — always show the arrow button ── */
[data-testid="collapsedControl"] {
    display: flex !important;
    visibility: visible !important;
    background: #4CAF50 !important;
    color: #fff !important;
    border-radius: 0 8px 8px 0 !important;
}
[data-testid="collapsedControl"] svg { fill: #fff !important; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #EAF2EB !important;
    border-right: 1.5px solid #C8DDC8 !important;
}
/* All text brown/black on light green sidebar */
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] div,
[data-testid="stSidebar"] small { color: #3E2723 !important; }
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 { color: #2E1C0C !important; }

/* Sidebar buttons — brown text, light green bg */
[data-testid="stSidebar"] .stButton > button {
    background: #D8EAD9 !important;
    border: 1px solid #B8D4B9 !important;
    color: #3E2723 !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-family: 'Outfit', sans-serif !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: #C8DCC9 !important;
    color: #2E1C0C !important;
}

/* Sidebar selectbox */
[data-testid="stSidebar"] .stSelectbox > div > div {
    background: #FFFFFF !important;
    color: #3E2723 !important;
    border: 1px solid #B8D4B9 !important;
}

/* ── Main content headings ── */
h1, h2, h3 {
    color: #3E2723 !important;
    font-family: 'Outfit', sans-serif;
    font-weight: 700;
}

/* ── Chat bubbles ── */
.chat-farmer {
    background: #FAF6F0;
    border-right: 3px solid #8D6E63;
    border-radius: 10px 0 10px 10px;
    padding: 12px 16px;
    margin: 10px 0 10px 80px;
    color: #3E2723;
    font-size: 0.95rem;
    line-height: 1.6;
    box-shadow: 0 1px 4px rgba(141,110,99,0.08);
}
.chat-agent {
    background: #EAF4EB;
    border-left: 3px solid #4CAF50;
    border-radius: 0 10px 10px 10px;
    padding: 12px 16px;
    margin: 10px 80px 10px 0;
    color: #1E251E;
    font-size: 0.95rem;
    line-height: 1.6;
    box-shadow: 0 1px 4px rgba(46,125,50,0.08);
}
.msg-lbl {
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: 4px;
}
.lbl-farmer { color: #8D6E63; }
.lbl-agent  { color: #2E7D32; }

/* ── Tool chips ── */
.tool-chip {
    display: inline-block;
    background: #D8EAD9;
    color: #2E7D32;
    border: 1px solid #B8D4B9;
    border-radius: 20px;
    padding: 2px 10px;
    font-size: 0.7rem;
    font-weight: 600;
    margin: 4px 3px 0 0;
}

/* Quick question suggestions styling */
.quick-area .stButton > button {
    background: #FFFFFF !important;
    border: 1.5px solid #C8DDC8 !important;
    color: #3E2723 !important;
    border-radius: 12px !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    padding: 12px 14px !important;
    height: auto !important;
    white-space: normal !important;
    word-wrap: break-word !important;
    box-shadow: 0 2px 6px rgba(0,0,0,0.02) !important;
    line-height: 1.3 !important;
    font-family: 'Outfit', sans-serif !important;
}
.quick-area .stButton > button:hover {
    background: #EAF4EB !important;
    border-color: #2E7D32 !important;
    color: #2E7D32 !important;
    box-shadow: 0 4px 10px rgba(46,125,50,0.1) !important;
}

/* Sidebar chat items */
.sidebar-chat-btn .stButton > button {
    background: transparent !important;
    border: none !important;
    color: #3E2723 !important;
    text-align: left !important;
    justify-content: flex-start !important;
    font-weight: 500 !important;
    font-size: 0.88rem !important;
    padding: 8px 12px !important;
    border-radius: 8px !important;
    width: 100% !important;
    display: block !important;
    font-family: 'Outfit', sans-serif !important;
}
.sidebar-chat-btn .stButton > button:hover {
    background: #D8EAD9 !important;
    color: #1B5E20 !important;
}
/* Active chat item */
.sidebar-chat-btn-active .stButton > button {
    background: #C8DCC9 !important;
    border: none !important;
    color: #1B5E20 !important;
    font-weight: 600 !important;
    text-align: left !important;
    justify-content: flex-start !important;
    font-size: 0.88rem !important;
    padding: 8px 12px !important;
    border-radius: 8px !important;
    width: 100% !important;
    display: block !important;
    font-family: 'Outfit', sans-serif !important;
}

/* Login Card styling */
.login-card {
    background: #FFFFFF;
    border: 1.5px solid #C8DDC8;
    border-radius: 16px;
    padding: 30px;
    margin-top: 50px;
    box-shadow: 0 4px 15px rgba(46,125,50,0.04);
}
</style>
""", unsafe_allow_html=True)


# ── Session state ─────────────────────────────────────────────
def _init():
    defs = {
        "farmers":          db_load(),
        "logged_in_farmer": None,
        # Map farmer name to list of chats: { farmer_name: [ { "id": str, "title": str, "messages": list }, ... ] }
        "farmer_chats":     {},
        "current_chat_id":  None,
        "show_form":        False,
        "_pending":         None,
    }
    for k, v in defs.items():
        if k not in st.session_state:
            st.session_state[k] = v
_init()

# ── Helper functions for Chats ───────────────────────────────
def get_chats() -> list:
    name = st.session_state.logged_in_farmer
    if not name:
        return []
    if name not in st.session_state.farmer_chats:
        import uuid
        default_chat = {
            "id": str(uuid.uuid4()),
            "title": "New Chat",
            "messages": []
        }
        st.session_state.farmer_chats[name] = [default_chat]
        st.session_state.current_chat_id = default_chat["id"]
    return st.session_state.farmer_chats[name]

def get_active_chat() -> dict | None:
    chats = get_chats()
    active_id = st.session_state.current_chat_id
    if not active_id and chats:
        st.session_state.current_chat_id = chats[0]["id"]
        active_id = chats[0]["id"]
    for c in chats:
        if c["id"] == active_id:
            return c
    if chats:
        st.session_state.current_chat_id = chats[0]["id"]
        return chats[0]
    return None

def add_chat() -> None:
    name = st.session_state.logged_in_farmer
    if not name:
        return
    import uuid
    new_id = str(uuid.uuid4())
    new_chat = {
        "id": new_id,
        "title": "New Chat",
        "messages": []
    }
    if name not in st.session_state.farmer_chats:
        st.session_state.farmer_chats[name] = []
    st.session_state.farmer_chats[name].insert(0, new_chat)
    st.session_state.current_chat_id = new_id


# ── Load agent ────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def _load():
    try:
        return load_agent(), None
    except AgentSetupError as e:
        return None, str(e)

agent, agent_err = _load()


# ── Agent error ───────────────────────────────────────────────
if agent_err:
    st.error(f"⚠️ Could not load models: {agent_err}\n\nPlace `.pkl` files in the `models/` folder.")
    st.stop()


# ── LOGIN / REGISTER PAGE ─────────────────────────────────────
if not st.session_state.logged_in_farmer:
    # Render logged-out sidebar state
    with st.sidebar:
        st.markdown("## 🌾 Kisan Saathi")
        st.markdown("*Your farming advisor*")
        st.markdown("---")
        st.markdown("### 🔒 Session Locked")
        st.markdown("Please log in or register a profile on the main screen to start your session.")
        st.markdown("---")
        st.markdown("<small>Built for Maharashtra farmers.<br>Data stays on your device.</small>",
                    unsafe_allow_html=True)

    # If registration form is active
    if st.session_state.show_form:
        st.markdown("## ➕ Create Farmer Profile")
        c1, c2 = st.columns(2)
        with c1:
            new_name = st.text_input("Name *", placeholder="e.g. Ramesh Patil")
            new_dist = st.selectbox("District", DISTRICTS)
        with c2:
            new_soil = st.selectbox("Soil Type", KNOWN_SOIL_TYPES)
            new_size = st.number_input("Farm Size (acres)", min_value=0.1,
                                       max_value=500.0, value=2.0, step=0.5)
        new_ph = st.slider("Soil pH", 4.0, 9.0, 6.5, 0.1,
                           help="6.0–7.5 is ideal for most crops")

        sa, ca = st.columns([1, 5])
        with sa:
            if st.button("✅ Save", use_container_width=True):
                if not new_name.strip():
                    st.warning("Please enter a name.")
                elif any(f["name"] == new_name.strip() for f in st.session_state.farmers):
                    st.warning("A farmer with this name already exists.")
                else:
                    profile = {
                        "name": new_name.strip(), "district": new_dist,
                        "soil_type": new_soil, "farm_size": new_size, "soil_ph": new_ph,
                    }
                    st.session_state.farmers.append(profile)
                    db_save(st.session_state.farmers)
                    st.session_state.logged_in_farmer = new_name.strip()
                    st.session_state.show_form = False
                    add_chat()  # Start first chat session
                    st.rerun()
        with ca:
            if st.button("Cancel"):
                st.session_state.show_form = False
                st.rerun()
        st.stop()

    # Show Login Page
    c_left, c_mid, c_right = st.columns([1, 2, 1])
    with c_mid:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        st.markdown("""
        <div style="text-align:center; margin-bottom: 20px;">
            <h2 style="margin:0;color:#3E2723;font-size:2.2rem;font-weight:700;">🌾 Kisan Saathi</h2>
            <p style="margin:8px 0 0;color:#5D4037;font-size:1.05rem;">
                Personalized AI Farming Advisor for Maharashtra
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        farmers_list = st.session_state.farmers
        if farmers_list:
            names = [f["name"] for f in farmers_list]
            selected_farmer = st.selectbox("Select your profile to log in:", names)
            
            c_login, c_reg = st.columns(2)
            with c_login:
                if st.button("🚪 Log In", use_container_width=True):
                    st.session_state.logged_in_farmer = selected_farmer
                    add_chat()  # Ensure at least one chat exists
                    st.rerun()
            with c_reg:
                if st.button("➕ Register Profile", use_container_width=True):
                    st.session_state.show_form = True
                    st.rerun()
        else:
            st.warning("No farmer profiles found. Please register a profile to get started.")
            if st.button("➕ Register First Profile", use_container_width=True):
                st.session_state.show_form = True
                st.rerun()
                
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()


# ── Add/Edit Farmer Form (Logged In) ───────────────────────────
if st.session_state.logged_in_farmer and st.session_state.show_form:
    st.markdown("## ✏️ Edit Farmer Profile")
    fd = next((f for f in st.session_state.farmers if f["name"] == st.session_state.logged_in_farmer), None)
    if not fd:
        st.session_state.show_form = False
        st.rerun()
        
    c1, c2 = st.columns(2)
    with c1:
        new_name = st.text_input("Name *", value=fd["name"], placeholder="e.g. Ramesh Patil")
        new_dist = st.selectbox("District", DISTRICTS, index=DISTRICTS.index(fd["district"]) if fd["district"] in DISTRICTS else 0)
    with c2:
        new_soil = st.selectbox("Soil Type", KNOWN_SOIL_TYPES, index=KNOWN_SOIL_TYPES.index(fd["soil_type"]) if fd["soil_type"] in KNOWN_SOIL_TYPES else 0)
        new_size = st.number_input("Farm Size (acres)", min_value=0.1,
                                   max_value=500.0, value=float(fd["farm_size"]), step=0.5)
    new_ph = st.slider("Soil pH", 4.0, 9.0, float(fd["soil_ph"]), 0.1,
                       help="6.0–7.5 is ideal for most crops")

    sa, ca = st.columns([1, 5])
    with sa:
        if st.button("✅ Save", use_container_width=True):
            if not new_name.strip():
                st.warning("Please enter a name.")
            else:
                old_name = fd["name"]
                st.session_state.farmers = [f for f in st.session_state.farmers if f["name"] != old_name]
                
                profile = {
                    "name": new_name.strip(), "district": new_dist,
                    "soil_type": new_soil, "farm_size": new_size, "soil_ph": new_ph,
                }
                st.session_state.farmers.append(profile)
                db_save(st.session_state.farmers)
                
                if old_name != new_name.strip():
                    if old_name in st.session_state.farmer_chats:
                        st.session_state.farmer_chats[new_name.strip()] = st.session_state.farmer_chats.pop(old_name)
                    st.session_state.logged_in_farmer = new_name.strip()
                    
                st.session_state.show_form = False
                st.rerun()
    with ca:
        if st.button("Cancel"):
            st.session_state.show_form = False
            st.rerun()
    st.stop()


# ── Active farmer loading ─────────────────────────────────────
fd = next((f for f in st.session_state.farmers if f["name"] == st.session_state.logged_in_farmer), None)
if not fd:
    st.session_state.logged_in_farmer = None
    st.rerun()

farmer = FarmerProfile(
    name      = fd["name"],
    district  = fd["district"],
    soil_type = fd["soil_type"],
    farm_size = fd["farm_size"],
    soil_ph   = fd["soil_ph"],
)


# ── Sidebar ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🌾 Kisan Saathi")
    st.markdown("*Your farming advisor*")
    st.markdown("---")

    # Start new chat button
    if st.button("➕ New Chat", use_container_width=True):
        add_chat()
        st.rerun()
    
    st.markdown("### 💬 Conversations")
    chats = get_chats()
    active_chat = get_active_chat()
    active_id = active_chat["id"] if active_chat else None

    # Render chats list with delete buttons
    for c in chats:
        is_active = (c["id"] == active_id)
        btn_class = "sidebar-chat-btn-active" if is_active else "sidebar-chat-btn"
        
        c_btn, c_del = st.columns([6, 1])
        with c_btn:
            st.markdown(f'<div class="{btn_class}">', unsafe_allow_html=True)
            if st.button(f"💬 {c['title']}", key=f"chat_nav_{c['id']}", use_container_width=True):
                st.session_state.current_chat_id = c["id"]
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        with c_del:
            if len(chats) > 1:
                if st.button("🗑️", key=f"chat_del_{c['id']}", help="Delete chat", use_container_width=True):
                    st.session_state.farmer_chats[st.session_state.logged_in_farmer] = [
                        chat for chat in chats if chat["id"] != c["id"]
                    ]
                    if active_id == c["id"]:
                        st.session_state.current_chat_id = st.session_state.farmer_chats[st.session_state.logged_in_farmer][0]["id"]
                    st.rerun()

    # Active Farmer Card and Controls in Sidebar bottom
    ph_label = ("Good" if 6.0 <= fd["soil_ph"] <= 7.5
                else ("Acidic" if fd["soil_ph"] < 6.0 else "Alkaline"))
    st.markdown("---")
    st.markdown("### 👨‍🌾 Profile")
    st.markdown(f"""
    <div style="background:#FFFFFF;border-radius:10px;padding:12px;border:1.5px solid #C8DDC8;margin-bottom:12px;box-shadow:0 1px 3px rgba(0,0,0,0.03);">
        <h4 style="margin:0;color:#3E2723;font-size:0.95rem;font-weight:600;">{fd['name']}</h4>
        <div style="font-size:0.8rem;color:#5D4037;margin-top:6px;line-height:1.4;">
            🌾 <b>{fd['farm_size']} acres</b><br>
            📍 {fd['district']} District<br>
            🌱 {fd['soil_type']} Soil (pH {fd['soil_ph']} - {ph_label})
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    c_edit, c_logout = st.columns(2)
    with c_edit:
        if st.button("✏️ Edit", use_container_width=True):
            st.session_state.show_form = True
            st.rerun()
    with c_logout:
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in_farmer = None
            st.session_state.current_chat_id = None
            if agent:
                agent.clear_memory()
            st.rerun()

    st.markdown("---")
    st.markdown("<small>Built for Maharashtra farmers.<br>Data stays on your device.</small>",
                unsafe_allow_html=True)


# ── Chat Header ───────────────────────────────────────────────
col_title, col_info, col_actions = st.columns([2, 2, 1])
with col_title:
    st.markdown(f"""
    <h2 style="margin: 0; font-size: 1.6rem; color: #3E2723; line-height: 1.2;">🌾 Kisan Saathi</h2>
    <p style="margin: 2px 0 0; font-size: 0.82rem; color: #5D4037;">Personal Farming Advisor</p>
    """, unsafe_allow_html=True)

with col_info:
    ph_label = ("Good" if 6.0 <= fd["soil_ph"] <= 7.5
                else ("Acidic" if fd["soil_ph"] < 6.0 else "Alkaline"))
    st.markdown(f"""
    <div style="background:#EAF2EB; border-radius:8px; padding:6px 12px; border:1px solid #C8DDC8; font-size:0.8rem; color:#3E2723; line-height:1.3;">
        👤 <b>{farmer.name}</b> &nbsp;·&nbsp; 📍 {farmer.district}<br>
        🌱 {farmer.soil_type} soil &nbsp;·&nbsp; pH {farmer.soil_ph} ({ph_label})
    </div>
    """, unsafe_allow_html=True)

with col_actions:
    if st.button("🚪 Logout", key="main_logout", use_container_width=True):
        st.session_state.logged_in_farmer = None
        st.session_state.current_chat_id = None
        if agent:
            agent.clear_memory()
        st.rerun()

st.markdown("---")


# ── Chat Area ─────────────────────────────────────────────────
active_chat = get_active_chat()
if not active_chat:
    st.write("Please start or select a chat.")
    st.stop()

thread = active_chat["messages"]

# Welcome State with Suggestions
if not thread:
    st.markdown(f"""
    <div style="text-align: center; margin: 35px 0 20px;">
        <h3 style="font-size: 1.35rem; font-weight: 500; color: #3E2723;">
            Namaste {farmer.name}! How can I help you today?
        </h3>
        <p style="color: #5D4037; font-size: 0.85rem; margin-top: 5px;">
            Select one of the suggestion topics below or type your question in the chat bar.
        </p>
    </div>
    """, unsafe_allow_html=True)

    quick_qs = [
        "Which crop is best for me this kharif?",
        "How can I improve my soil health?",
        "When should I sow cotton?",
        "What fertiliser is good for my soil?",
        "How is the monsoon weather this year?",
        "What pests should I watch for?",
    ]
    st.markdown('<div class="quick-area">', unsafe_allow_html=True)
    qc = st.columns(3)
    for i, q in enumerate(quick_qs):
        with qc[i % 3]:
            if st.button(q, key=f"qq_{i}", use_container_width=True):
                st.session_state._pending = q
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# Render Chat History
if thread:
    chat_html = ""
    for role, text, tools in thread:
        if role == "farmer":
            chat_html += (
                f'<div class="chat-farmer">'
                f'<div class="msg-lbl lbl-farmer">🧑‍🌾 {farmer.name}</div>'
                f'{text}'
                f'</div>'
            )
        else:
            clean_tools = [t for t in tools if t not in ("✨ Gemini AI", "💻 Local AI")]
            chips_html = ""
            if clean_tools:
                chips = "".join(f'<span class="tool-chip">{t}</span>' for t in clean_tools)
                chips_html = f'<div style="margin-top:8px">{chips}</div>'

            chat_html += (
                f'<div class="chat-agent">'
                f'<div class="msg-lbl lbl-agent">🌿 Kisan Saathi</div>'
                f'{text}'
                f'{chips_html}'
                f'</div>'
            )
    st.markdown(
        f'<div style="background:#FFFFFF;border-radius:14px;border:1px solid #E1EFE2;'
        f'padding:20px;max-height:450px;overflow-y:auto;margin-bottom:12px;'
        f'box-shadow:0 2px 10px rgba(0,0,0,0.02)">'
        f'{chat_html}</div>',
        unsafe_allow_html=True,
    )

    if agent and agent.last_source == "error" and agent.last_error:
        st.error(f"⚠️ **Gemini API Error details:** {agent.last_error}")
    elif agent and agent.last_source == "fallback":
        st.info("ℹ️ AI advisor is temporarily offline. Answers are based on your farm's ML model data.", icon="🌾")


# Input Box using Streamlit's native chat input
user_input = st.chat_input("Ask anything about farming in " + farmer.district + "...")

# Run query
pending = st.session_state._pending
st.session_state._pending = None
query   = pending or (user_input.strip() if user_input and user_input.strip() else "")

if query:
    # Rename chat title if it's the first message
    if not thread:
        title = query.strip()
        if len(title) > 25:
            title = title[:22] + "..."
        active_chat["title"] = title

    thread.append(("farmer", query, []))
    with st.spinner("Thinking…"):
        try:
            tools_used = agent.tools_labels(query)
            reply, source = agent.answer(query, farmer=farmer)
            thread.append(("agent", reply, tools_used))
        except Exception as e:
            thread.append(("agent", f"Sorry, something went wrong: {e}", []))
    st.rerun()

# ── Footer ────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<center><small style='color:#8D6E63'>Kisan Saathi &nbsp;·&nbsp; "
    "Personal Farming Advisor for Maharashtra Farmers</small></center>",
    unsafe_allow_html=True,
)