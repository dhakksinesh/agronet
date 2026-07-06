import os
import re
import warnings
import logging
from datetime import datetime
os.environ["CREWAI_DISABLE_TELEMETRY"] = "true"

warnings.filterwarnings("ignore", message=".*Event pairing mismatch.*")
warnings.filterwarnings("ignore", message=".*Tried to instantiate class.*__path__.*")
warnings.filterwarnings("ignore", message=".*torch.classes.*")
logging.getLogger("CrewAIEventsBus").setLevel(logging.CRITICAL)

from dotenv import load_dotenv
load_dotenv()
if os.getenv("CREWAI_TRACING_ENABLED", "").lower() == "true":
    os.environ["CREWAI_TRACING_ENABLED"] = "true"

import streamlit as st
from config import get_states, get_districts, get_soil_types, PINECONE_API_KEY, PINECONE_EMBEDDING_MODEL, OPENROUTER_API_KEY, OPENROUTER_MODEL, validate_api_keys
from database import save_farmer_profile, save_query, init_db, get_profiles, delete_profile, get_query_history, get_crop_types, get_crops_by_type, get_crop_type_for_name, update_profile, count_queries, delete_query, DB_PATH
from pathlib import Path
from rag.retriever import get_index_stats
from tools.weather import get_weather_data, get_coordinates
from utils import logger
from rag import auto_ingest_if_needed

st.set_page_config(page_title="AgroNet", page_icon="🌾", layout="wide")
init_db()

@st.cache_resource
def _init_rag():
    return auto_ingest_if_needed()
_init_rag()

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from pydantic import BaseModel
from typing import Optional
from crews import agri_crew, simple_crew

class CropCalendar(BaseModel):
    sow: str
    harvest: str
    duration: str
    tips: Optional[str] = None

class SeasonInfo(BaseModel):
    crops: str
    advisory: Optional[str] = None

_simple_kw = {
    "water", "irrigation", "pour", "daily", "how much", "how often",
    "fertilizer", "compost", "manure", "npk", "nutrient",
    "pest", "insect", "bug", "disease", "fungus", "mite", "aphid",
    "when to", "what to", "which", "variety", "seed",
    "temperature", "weather", "rain", "soil ph",
}

def _fetch_crop_cal(crop: str, state: str) -> CropCalendar | None:
    try:
        llm = ChatOpenAI(
            model=os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini"),
            api_key=os.getenv("OPENROUTER_API_KEY"),
            base_url=os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
            temperature=0.05,
        )
        logger.debug(f"Fetching crop calendar for {crop}, {state}")
        r = llm.invoke([
            HumanMessage(content=(
                f"You are an Indian agriculture expert.\n"
                f"Give the crop calendar for {crop} grown in {state}, India. Use REAL months and durations.\n"
                f"Reply with exactly these 4 lines:\n"
                f"SOW: Jun-Jul\n"
                f"HARVEST: Oct-Nov\n"
                f"DURATION: 120-140 days\n"
                f"TIPS: Real advisory for this crop"
            ))
        ])
        txt = r.content.strip() if r.content else ""
        cal = {}
        for line in txt.split("\n"):
            line = line.strip()
            if line.lower().startswith("sow:"): cal["sow"] = line.split(":", 1)[1].strip()
            elif line.lower().startswith("harvest:"): cal["harvest"] = line.split(":", 1)[1].strip()
            elif line.lower().startswith("duration:"): cal["duration"] = line.split(":", 1)[1].strip()
            elif line.lower().startswith("tips:"): cal["tips"] = line.split(":", 1)[1].strip()
        if cal.get("sow") and cal.get("harvest"):
            logger.debug(f"Crop calendar fetched successfully for {crop}, {state}")
            return CropCalendar(**cal)
        logger.warning(f"Crop calendar: unexpected format: [{txt[:300]}]")
        return None
    except Exception as e:
        logger.warning(f"Crop calendar fetch failed: {type(e).__name__}: {e}")
        return None

def _fetch_season_info(state: str, season: str) -> SeasonInfo | None:
    try:
        llm = ChatOpenAI(
            model=os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini"),
            api_key=os.getenv("OPENROUTER_API_KEY"),
            base_url=os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
            temperature=0.05,
        )
        logger.debug(f"Fetching season info for {season} in {state}")
        r = llm.invoke([
            HumanMessage(content=(
                f"Answer concisely in the exact format requested.\n"
                f"{season} season in {state}, India.\n"
                f"Reply with exactly 2 lines:\n"
                f"Line 1: CROPS: 3-5 major crops grown this season, comma-separated\n"
                f"Line 2: ADVISORY: one practical farming tip for this season"
            ))
        ])
        txt = r.content.strip() if r.content else ""
        info = {}
        for line in txt.split("\n"):
            line = line.strip()
            if line.lower().startswith("crops:"): info["crops"] = line.split(":", 1)[1].strip()
            elif line.lower().startswith("advisory:"): info["advisory"] = line.split(":", 1)[1].strip()
        if info.get("crops"):
            logger.debug(f"Season info fetched successfully for {season} in {state}")
            return SeasonInfo(**info)
        logger.warning(f"Season info: unexpected format: [{txt[:300]}]")
        return None
    except Exception as e:
        logger.warning(f"Season info fetch failed: {type(e).__name__}: {e}")
        return None

@st.cache_data(ttl=1800)
def _cached_weather(lat: float, lon: float) -> dict:
    return get_weather_data.run(lat, lon)

st.markdown("""
<style>
    :root { --primary: #2E8B57; --primary-light: #3CB371; --radius: 12px; }
    * { box-sizing: border-box; }
    .block-container { padding-top: 1rem !important; max-width: 1100px; }
    .header {
        background: linear-gradient(135deg, #1a6b3c 0%, #2E8B57 50%, #3CB371 100%);
        color: white; padding: 1.2rem 1.8rem; border-radius: var(--radius);
        margin-bottom: 1.2rem; box-shadow: 0 4px 12px rgba(46,139,87,0.25);
        display: flex; align-items: center; justify-content: space-between;
    }
    .header h1 { margin: 0; font-size: 1.5rem; font-weight: 700; }
    .header p { margin: 0; opacity: 0.85; font-size: 0.85rem; }
    .card {
        background: #f6faf6; border: 1px solid #dce8dc; border-radius: var(--radius);
        padding: 1.2rem; box-shadow: 0 1px 4px rgba(0,0,0,0.05);
        margin-bottom: 1rem;
    }
    .card-title {
        font-size: 0.85rem; font-weight: 600; text-transform: uppercase;
        letter-spacing: 0.04em; color: #64748b; margin-bottom: 0.75rem;
    }
    .stat-box {
        background: #f0fdf4; border-radius: 10px; padding: 0.8rem; text-align: center;
    }
    .stat-value { font-size: 1.3rem; font-weight: 700; color: #166534; }
    .stat-label { font-size: 0.75rem; color: #64748b; margin-top: 0.2rem; }
    .chat-msg {
        border-radius: 10px !important; margin-bottom: 0.5rem !important;
        border: 1px solid #e8ecef !important; box-shadow: 0 1px 3px rgba(0,0,0,0.04) !important;
    }
    .stChatInputContainer { border: 1px solid #d0d5dd !important; border-radius: 12px !important; }
    .stChatInputContainer:focus-within { border-color: var(--primary) !important; box-shadow: 0 0 0 3px rgba(46,139,87,0.12) !important; }

    div[data-testid="stSidebar"] { background: #fafcfa; }
    div[data-testid="stSidebar"] .stButton button { width: 100%; border-radius: 8px !important; }
    .profile-item {
        display: flex; align-items: center; justify-content: space-between;
        padding: 0.5rem 0.75rem; background: white; border: 1px solid #e8ecef;
        border-radius: 8px; margin-bottom: 0.4rem; cursor: pointer;
    }
    .profile-item.active { border-color: var(--primary); background: #f0fdf4; }
    .profile-name { font-weight: 600; font-size: 0.9rem; }
    .profile-detail { font-size: 0.75rem; color: #64748b; }
    .stTabs [data-baseweb="tab-list"] { gap: 0.5rem; }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0 !important; padding: 0.5rem 1.2rem !important;
        font-weight: 500 !important;
    }
    .history-item {
        padding: 0.75rem; border: 1px solid #e8ecef; border-radius: 8px;
        margin-bottom: 0.5rem; cursor: pointer; background: white;
    }
    .history-item:hover { border-color: var(--primary); }
    .badge {
        display: inline-block; padding: 0.15rem 0.5rem; border-radius: 20px;
        font-size: 0.7rem; font-weight: 600;
    }
    .badge-ok { background: #dcfce7; color: #166534; }
    .badge-missing { background: #fee2e2; color: #991b1b; }
    button[data-testid="stDownloadButton"] { background: none !important; border: none !important; color: var(--primary) !important; text-decoration: underline !important; padding: 0 !important; font-size: 0.9rem !important; font-weight: 500 !important; cursor: pointer !important; box-shadow: none !important; }
    button[data-testid="stDownloadButton"]:hover { color: #166534 !important; background: none !important; }
    @media (max-width: 768px) { .header { flex-direction: column; text-align: center; gap: 0.3rem; } }
</style>
""", unsafe_allow_html=True)

api_key_issues = validate_api_keys()
if api_key_issues:
    st.error("🚨 API keys missing")
    for i in api_key_issues:
        st.markdown(f"- {i}")
    st.code("cp .env.example .env")
    st.stop()

for key, default in [
    ("messages", []), ("profile_set", False), ("profile", None), ("profile_id", None),
    ("export_content", None)
]:
    if key not in st.session_state:
        st.session_state[key] = default

if st.session_state.profile_id is None and get_profiles():
    first = get_profiles()[0]
    st.session_state.profile_id = first["id"]
    st.session_state.profile = first
    st.session_state.profile_set = True

def switch_profile(pid):
    for p in get_profiles():
        if p["id"] == pid:
            st.session_state.profile_id = pid
            st.session_state.profile = p
            st.session_state.profile_set = True
            st.rerun()

st.markdown("""
<div class="header">
    <div><h1>🌾 AgroNet</h1><p>Multi-Agent Crop Advisory System</p></div>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 🌾 AgroNet\n\n*Multi-Agent Crop Advisory System*")
    st.markdown("---")
    if st.session_state.profile:
        p = st.session_state.profile
        st.markdown("### My Profile")
        st.markdown(f"{p.get('name', 'My Farm')} · {p['crop']} · {p['district']}, {p['state']}")
        st.caption("👤 Manage in Profiles tab →")
    else:
        st.markdown("### 🏡 No Profile")
        st.markdown("*Create one in Profiles tab*")

    st.markdown("---")
    or_ok = OPENROUTER_API_KEY and OPENROUTER_API_KEY != ""
    pc_ok = PINECONE_API_KEY and PINECONE_API_KEY != ""
    db_ok = DB_PATH.exists()
    st.markdown(f"""
    <div style="border:1px solid #334155;border-radius:8px;padding:8px 12px;margin-bottom:6px;background:#1e293b;box-shadow:0 1px 3px rgba(0,0,0,0.2);color:#e2e8f0">
        <div style="display:flex;justify-content:space-between;align-items:center">
            <span>🔌 OpenRouter</span>
            <span>{'✅' if or_ok else '❌'}</span>
        </div>
        <div style="opacity:0.5;font-size:0.8rem;margin-top:2px">Model: {OPENROUTER_MODEL}</div>
    </div>
    <div style="border:1px solid #334155;border-radius:8px;padding:8px 12px;margin-bottom:6px;background:#1e293b;box-shadow:0 1px 3px rgba(0,0,0,0.2);color:#e2e8f0">
        <div style="display:flex;justify-content:space-between;align-items:center">
            <span>🗄️ Pinecone</span>
            <span>{'✅' if pc_ok else '❌'}</span>
        </div>
        <div style="opacity:0.5;font-size:0.8rem;margin-top:2px">Embed: {PINECONE_EMBEDDING_MODEL}</div>
    </div>
    <div style="border:1px solid #334155;border-radius:8px;padding:8px 12px;background:#1e293b;box-shadow:0 1px 3px rgba(0,0,0,0.2);color:#e2e8f0">
        <div style="display:flex;justify-content:space-between;align-items:center">
            <span>🗃️ SQLite</span>
            <span>{'✅' if db_ok else '❌'}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

tab_chat, tab_dash, tab_prof, tab_hist, tab_know = st.tabs(["💬 Chat", "📊 Dashboard", "👤 Profiles", "📜 History", "📚 Knowledge"])

with tab_chat:
    if not st.session_state.profile:
        st.info("Please set up a farm profile in the sidebar first.")
    else:
        profile = st.session_state.profile
        profile_id = st.session_state.profile_id

        chat_container = st.container()
        with chat_container:
            for msg in st.session_state.messages:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

            if st.session_state.messages:
                col_a, col_b = st.columns([3, 1])
                with col_a:
                    chat_text = "\n\n".join(
                        f"**{m['role'].title()}**: {m['content']}" for m in st.session_state.messages
                    )
                    st.download_button("📥 Export Chat", chat_text, file_name="agronet_chat.md", mime="text/markdown", use_container_width=True)
                with col_b:
                    if st.button("🔄 New Chat", use_container_width=True):
                        st.session_state.messages = []
                        st.rerun()

        if prompt := st.chat_input("Ask about your crops, weather, or farming practices..."):
            with chat_container:
                st.session_state.messages.append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.markdown(prompt)

                greetings = {"hi", "hello", "hey", "heyy", "helo", "hii", "heyo", "good morning", "good afternoon", "good evening"}
                is_greeting = prompt.strip().lower().rstrip("!.,?") in greetings or re.match(r"^(hi+|hey|hello)\b", prompt.strip().lower())
                farming_keywords = [
                    "crop", "seed", "soil", "fertilizer", "pest", "disease", "weed",
                    "irrigation", "rain", "weather", "temperature", "humidity",
                    "harvest", "plant", "yield", "organic", "compost", "manure",
                    "pesticide", "fungicide", "insect", "farm", "farmer", "field",
                    "wheat", "rice", "maize", "cotton", "sugarcane", "millet",
                    "pulses", "vegetable", "fruit", "plantation", "scheme",
                    "subsidy", "pm-kisan", "pmfby", "insurance", "loan",
                    "market", "price", "sell", "profit", "income", "budget",
                    "kharif", "rabi", "monsoon", "drought", "flood", "cold",
                    "nursery", "graft", "pruning", "mulch", "greenhouse",
                    "animal", "cattle", "goat", "poultry", "dairy", "fishery",
                    "sustainable", "water", "drainage", "ph", "npk", "nutrient",
                ]
                non_farming_keywords = [
                    "restaurant", "eat", "food", "recipe", "cook", "movie", "film",
                    "game", "music", "song", "travel", "hotel", "book", "read",
                    "code", "program", "python", "javascript", "app",
                    "car", "bike", "vehicle", "phone", "laptop", "computer",
                    "doctor", "hospital", "medicine", "health", "fitness",
                    "shop", "store", "buy", "order", "delivery",
                ]
                is_farming = any(kw in prompt.lower() for kw in farming_keywords)

                if is_greeting:
                    msg = (
                        f"👋 Welcome! I'm your **{profile['crop']}** advisor for **{profile['district']}**.\n\n"
                        f"I can help with:\n"
                        f"- 🌱 Crop management & irrigation\n"
                        f"- 🌤️ Weather-based planning\n"
                        f"- 🧪 Pest & disease control\n"
                        f"- 🛡️ Government schemes & subsidies\n"
                        f"- 💧 Fertilizer recommendations\n\n"
                        f"**What would you like to know?**"
                    )
                    with st.chat_message("assistant"):
                        st.markdown(msg)
                    st.session_state.messages.append({"role": "assistant", "content": msg})
                    save_query(profile_id, prompt, msg)

                elif not is_farming:
                    if any(kw in prompt.lower() for kw in non_farming_keywords):
                        is_farming = False
                    else:
                        try:
                            clf_llm = ChatOpenAI(model=os.getenv("OPENROUTER_MODEL"), api_key=os.getenv("OPENROUTER_API_KEY"), base_url=os.getenv("OPENROUTER_BASE_URL"), temperature=0, max_tokens=10)
                            prev = st.session_state.messages[-3:] if len(st.session_state.messages) > 1 else []
                            ctx = "\n".join(f"{m['role']}: {m['content'][:200]}" for m in prev)
                            logger.debug(f"Classifying off-topic query: [{prompt[:100]}]")
                            r = clf_llm.invoke([HumanMessage(content=f"Previous conversation:\n{ctx}\n\nUser: {prompt}\n\nIs this about farming/agriculture? Answer yes or no only.")])
                            ans = r.content.strip().lower() if r.content else ""
                            logger.debug(f"Classification result: {ans}")
                            if ans.startswith("yes"):
                                is_farming = True
                        except Exception as e:
                            logger.warning(f"Classification LLM failed: {type(e).__name__}: {e}")
                            recent = st.session_state.messages[-4:]
                            context_text = " ".join(m["content"].lower() for m in recent)
                            if any(kw in context_text for kw in farming_keywords) and len(prompt) < 50:
                                is_farming = True
                    if not is_farming:
                        warn = "🌾 I'm specialized in agriculture. I can help with crop advice, weather, pests, and government schemes. Could you ask something farming-related?"
                        with st.chat_message("assistant"):
                            st.markdown(warn)
                        st.session_state.messages.append({"role": "assistant", "content": warn})

                if is_farming:
                    with st.chat_message("assistant"):
                        with st.spinner("🤖 Analyzing your query..."):
                            try:
                                history = st.session_state.messages[-6:]
                                conv_history = "\n".join(
                                    f"{'Farmer' if m['role'] == 'user' else 'Advisor'}: {m['content']}"
                                    for m in history[:-1]
                                )
                                _month = datetime.now().month
                                if 6 <= _month <= 9:
                                    _cur_season = "Kharif"
                                elif _month >= 10 or _month <= 3:
                                    _cur_season = "Rabi"
                                else:
                                    _cur_season = "Zaid"
                                _context_for_simple = " ".join(m["content"].lower() for m in st.session_state.messages[-4:])
                                _is_simple = any(kw in prompt.lower() for kw in _simple_kw) or any(kw in _context_for_simple for kw in _simple_kw)
                                _crew = simple_crew if _is_simple else agri_crew
                                crew_output = _crew.kickoff(inputs={
                                    "state": profile["state"],
                                    "district": profile["district"],
                                    "crop": profile["crop"],
                                    "soil_type": profile["soil_type"],
                                    "query": prompt,
                                    "conversation_history": conv_history,
                                    "current_date": datetime.now().strftime("%Y-%m-%d"),
                                    "current_season": _cur_season,
                                })
                                st.markdown(crew_output.raw)
                                st.session_state.messages.append({"role": "assistant", "content": crew_output.raw})
                                save_query(profile_id, prompt, crew_output.raw)
                            except Exception as e:
                                logger.error(f"CrewAI error: {str(e)}")
                                err = f"❌ {str(e)}"
                                st.markdown(err)
                                st.session_state.messages.append({"role": "assistant", "content": err})

with tab_dash:
    if st.session_state.profile:
        p = st.session_state.profile
        col1, col2 = st.columns([1, 1])
        with col1:
            with st.container(border=True):
                st.markdown("🌱 **Farm Profile**")
                st.markdown(f"**Farm:** {p.get('name', 'My Farm')}  \n**Location:** {p['district']}, {p['state']}  \n**Crop:** {p['crop']}  \n**Soil:** {p['soil_type']}")

        with col2:
            with st.container(border=True):
                st.markdown("🌤️ **Weather**")
            try:
                lat, lon = get_coordinates(p["district"], p["state"])
                w = _cached_weather(lat, lon)
                sa, sb, sc, sd = st.columns(4)
                with sa: st.markdown(f"<div class='stat-box'><div class='stat-value'>{w['temperature_max']}°</div><div class='stat-label'>Max</div></div>", unsafe_allow_html=True)
                with sb: st.markdown(f"<div class='stat-box'><div class='stat-value'>{w['temperature_min']}°</div><div class='stat-label'>Min</div></div>", unsafe_allow_html=True)
                with sc: st.markdown(f"<div class='stat-box'><div class='stat-value'>{w['rainfall']}</div><div class='stat-label'>Rain mm</div></div>", unsafe_allow_html=True)
                with sd:
                    h = w['humidity_avg']
                    h_str = f"{h:.0f}%" if isinstance(h, (int, float)) else str(h)
                    st.markdown(f"<div class='stat-box'><div class='stat-value'>{h_str}</div><div class='stat-label'>Humidity</div></div>", unsafe_allow_html=True)
            except:
                st.info("Weather unavailable")

        m = datetime.now().month
        s = "Kharif 🌧️" if 6 <= m <= 9 else "Rabi 🌤️" if m >= 10 or m <= 3 else "Zaid ☀️"
        s_plain = s.split(" ")[0]
        _sk = f"season_{p['state']}_{s_plain}"
        if _sk not in st.session_state or st.session_state[_sk] is None:
            with st.spinner("Loading season info…"):
                st.session_state[_sk] = _fetch_season_info(p["state"], s_plain)
        sinfo = st.session_state[_sk]
        st.markdown("---")
        col_c1, col_c2 = st.columns([1, 1])
        with col_c1:
            with st.container(border=True):
                st.markdown(f"📅 **Current Season:** {s}")
                st.caption(datetime.now().strftime("%A, %d %B %Y"))
                if sinfo:
                    end_map = {"Kharif": (9, 30, 0), "Rabi": (3, 31, 1), "Zaid": (5, 31, 0)}
                    nm, nd, ny_off = end_map.get(s_plain, (12, 31, 0))
                    rem = (datetime(datetime.now().year + (ny_off if datetime.now().month >= 10 else 0), nm, nd) - datetime.now()).days
                    st.markdown(f"⏳ **{rem} days** until {s_plain} ends")
                    st.markdown(f"🌾 **Season crops:** {sinfo.crops}")
                    if sinfo.advisory:
                        st.markdown(f"💡 *{sinfo.advisory}*")
                else:
                    st.caption("Season details unavailable")
        with col_c2:
            with st.container(border=True):
                st.markdown("🌱 **Crop Calendar**")
                _key = f"cal_v4_{p['crop']}_{p['state']}"
                if _key not in st.session_state or st.session_state[_key] is None:
                    with st.spinner("Fetching crop calendar…"):
                        st.session_state[_key] = _fetch_crop_cal(p["crop"], p["state"])
                cal = st.session_state[_key]
                if cal:
                    st.markdown(f"**{p['crop']}** — *{p['state']}*")
                    st.markdown(f"🌿 **Sow:** {cal.sow}")
                    st.markdown(f"🍂 **Harvest:** {cal.harvest}")
                    st.markdown(f"⏳ **Duration:** {cal.duration}")
                    if cal.tips:
                        st.markdown(f"💡 *{cal.tips}*")
                else:
                    st.info("Calendar unavailable")
    else:
        st.info("Create a farm profile in the sidebar to get started.")

with tab_prof:
    st.markdown("## 👤 Farm Profiles")
    profiles = get_profiles()
    per_page = 10
    total_profiles = len(profiles)
    total_pages = max(1, (total_profiles + per_page - 1) // per_page)
    page_key = "prof_page"
    if page_key not in st.session_state:
        st.session_state[page_key] = 1
    elif st.session_state[page_key] > total_pages:
        st.session_state[page_key] = total_pages

    if total_profiles > per_page:
        cols = st.columns([1, 3, 1])
        with cols[0]:
            if st.button("◀ Prev", disabled=st.session_state[page_key] <= 1):
                st.session_state[page_key] -= 1; st.rerun()
        with cols[1]:
            st.markdown(f"<div style='text-align:center'>Page {st.session_state[page_key]} of {total_pages}</div>", unsafe_allow_html=True)
        with cols[2]:
            if st.button("Next ▶", disabled=st.session_state[page_key] >= total_pages):
                st.session_state[page_key] += 1; st.rerun()

    start = (st.session_state[page_key] - 1) * per_page
    page_profiles = profiles[start:start + per_page]

    if page_profiles:
        for p in page_profiles:
            is_active = p["id"] == st.session_state.profile_id
            with st.container(border=True):
                ci, ca = st.columns([5, 2])
                with ci:
                    st.markdown(f"**{'✅ ' if is_active else ''}{p['name']}**")
                    st.markdown(f"{p['crop']} · {p['district']}, {p['state']}  \nSoil: {p['soil_type']}")
                with ca:
                    b1, b2, b3 = st.columns(3, gap="small")
                    with b1:
                        if not is_active and st.button("🔄", key=f"sw_{p['id']}", help="Switch to this profile"):
                            switch_profile(p["id"])
                    with b2:
                        if st.button("✏️", key=f"edit_{p['id']}", help="Edit profile details"):
                            st.session_state[f"editing_{p['id']}"] = not st.session_state.get(f"editing_{p['id']}", False)
                            st.rerun()
                    with b3:
                        if st.button("🗑", key=f"del_{p['id']}", help="Delete this profile"):
                            delete_profile(p["id"])
                            if is_active:
                                st.session_state.profile_id = None
                                st.session_state.profile_set = False
                            st.rerun()
                if st.session_state.get(f"editing_{p['id']}", False):
                    with st.container(border=True):
                        cols_e = st.columns(2)
                        with cols_e[0]:
                            new_name = st.text_input("Name", p["name"], key=f"en_{p['id']}")
                            states = get_states()
                            new_state = st.selectbox("State", states, index=states.index(p["state"]) if p["state"] in states else 0, key=f"es_{p['id']}")
                            new_dist = st.selectbox("District", get_districts(new_state), key=f"ed_{p['id']}")
                        with cols_e[1]:
                            crop_types = get_crop_types()
                            default_type = get_crop_type_for_name(p["crop"]) or crop_types[0]
                            sel_type = st.selectbox("Crop Type", crop_types, index=crop_types.index(default_type) if default_type in crop_types else 0, key=f"ect_{p['id']}")
                            type_crops = get_crops_by_type(sel_type)
                            new_crop = st.selectbox("Crop", type_crops, index=type_crops.index(p["crop"]) if p["crop"] in type_crops else 0, key=f"ec_{p['id']}")
                            soils = get_soil_types()
                            new_soil = st.selectbox("Soil Type", soils, index=soils.index(p["soil_type"]) if p["soil_type"] in soils else 0, key=f"eso_{p['id']}")
                        if st.button("💾 Save Changes", key=f"save_{p['id']}", use_container_width=True):
                            update_profile(p["id"], name=new_name, state=new_state, district=new_dist, crop=new_crop, soil_type=new_soil)
                            del st.session_state[f"editing_{p['id']}"]
                            if is_active:
                                switch_profile(p["id"])
                            st.rerun()
    else:
        st.info("No profiles yet. Create one below.")

    st.markdown("---")
    st.markdown("### ➕ Create New Profile")
    col1, col2 = st.columns(2)
    with col1:
        pf_name = st.text_input("Farm Name", "My Farm", key="pf_name2")
        pf_state = st.selectbox("State", get_states(), key="pf_state2")
        pf_dist = st.selectbox("District", get_districts(pf_state), key="pf_dist2")
    with col2:
        crop_types = get_crop_types()
        pf_crop_type = st.selectbox("Crop Type", crop_types, key="pf_crop_type")
        pf_crop = st.selectbox("Crop", get_crops_by_type(pf_crop_type), key="pf_crop2")
        pf_soil = st.selectbox("Soil Type", get_soil_types(), key="pf_soil2")
    if st.button("💾 Save Profile", type="primary", use_container_width=True):
        pid = save_farmer_profile(pf_state, pf_dist, pf_crop, pf_soil, pf_name)
        switch_profile(pid)

with tab_hist:
    if not st.session_state.profile_id:
        st.info("Select a farm profile to view history.")
    else:
        search = st.text_input("🔍 Search history", placeholder="Search queries or responses...")
        per_page = 10
        total = count_queries(st.session_state.profile_id, search=search)
        total_pages = max(1, (total + per_page - 1) // per_page)
        page_key = "hist_page"
        if page_key not in st.session_state:
            st.session_state[page_key] = 1
        elif st.session_state[page_key] > total_pages:
            st.session_state[page_key] = total_pages

        if total > per_page:
            cols = st.columns([1, 3, 1])
            with cols[0]:
                if st.button("◀ Prev", disabled=st.session_state[page_key] <= 1):
                    st.session_state[page_key] -= 1; st.rerun()
            with cols[1]:
                st.markdown(f"<div style='text-align:center'>Page {st.session_state[page_key]} of {total_pages} ({total} total)</div>", unsafe_allow_html=True)
            with cols[2]:
                if st.button("Next ▶", disabled=st.session_state[page_key] >= total_pages):
                    st.session_state[page_key] += 1; st.rerun()

        offset = (st.session_state[page_key] - 1) * per_page
        history = get_query_history(st.session_state.profile_id, limit=per_page, offset=offset, search=search)
        if not history:
            st.info("No query history yet. Start a conversation in the Chat tab.")
        else:
            for h in history:
                preview = h["query_text"][:100] + ("..." if len(h["query_text"]) > 100 else "")
                with st.expander(f"💬 {preview}"):
                    st.markdown(f"**📅 {h['created_at']}**")
                    st.markdown("**You asked:**")
                    st.markdown(h["query_text"])
                    st.markdown("**Response:**")
                    st.markdown(h["response"])
                    bx, by = st.columns(2, gap="small")
                    with bx:
                        st.download_button(
                            "📥", h["response"],
                            file_name=f"advisory_{h['id']}.md",
                            mime="text/markdown",
                            key=f"dl_{h['id']}",
                            help="Download advisory",
                            use_container_width=True
                        )
                    with by:
                        if st.button("🗑", key=f"del_q_{h['id']}", help="Delete entry", use_container_width=True):
                            delete_query(h["id"])
                            st.rerun()

with tab_know:
    st.markdown("### 📚 Knowledge Base")
    data_path = Path(__file__).parent / "data"
    pdf_files = list(data_path.glob("*.pdf")) if data_path.exists() else []
    st.markdown(f"**PDF Documents:** {len(pdf_files)} found")
    if pdf_files:
        for f in pdf_files:
            sz = f.stat().st_size / (1024 * 1024)
            with open(f, "rb") as fh:
                st.download_button(f"{f.name} ({sz:.2f} MB)", fh, file_name=f.name, key=f.name, type="secondary", help="Open PDF")
    else:
        st.info("No PDF files in data/ folder.")
    st.markdown("---")
    stats = get_index_stats()
    if stats is not None:
        st.markdown(f"**Pinecone Index:** {stats} vectors indexed")
    else:
        st.warning("Pinecone not configured or index not found.")

