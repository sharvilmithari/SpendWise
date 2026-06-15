import streamlit as st

# ─────────────────────────────────────────────
#  LANDING PAGE CSS
# ─────────────────────────────────────────────

def inject_landing_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700&display=swap');

    #MainMenu, footer, header { visibility: hidden; }

    html, body, [class*="css"] {
        font-family: 'Space Grotesk', sans-serif;
        scroll-behavior: smooth;
    }

    .stApp {
        background: #05070f !important;
        color: #e2e8f0;
    }

    .block-container {
        padding: 0 !important;
        max-width: 100% !important;
    }

    /* ── NOISE OVERLAY ── */
    .stApp::before {
        content: '';
        position: fixed;
        inset: 0;
        background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.03'/%3E%3C/svg%3E");
        pointer-events: none;
        z-index: 0;
        opacity: 0.4;
    }

    /* ── HIDE STREAMLIT CHROME ── */
    [data-testid="stDecoration"] { display: none; }
    [data-testid="stToolbar"] { display: none; }
    section[data-testid="stSidebar"] { display: none; }

    /* ── BUTTONS ── */
    .stButton > button {
        font-family: 'DM Sans', sans-serif !important;
        font-weight: 600 !important;
        border-radius: 10px !important;
        transition: all 0.22s ease !important;
        letter-spacing: 0.1px !important;
    }

    /* Primary CTA button */
    div[data-testid="column"]:nth-of-type(1) .stButton > button,
    .cta-primary-col .stButton > button {
        background: linear-gradient(135deg, #4f7cff 0%, #6a5cff 50%, #8b5cf6 100%) !important;
        color: #fff !important;
        border: none !important;
        height: 52px !important;
        font-size: 1rem !important;
        box-shadow: 0 8px 30px rgba(91,78,248,0.4) !important;
    }
    div[data-testid="column"]:nth-of-type(1) .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 14px 40px rgba(91,78,248,0.55) !important;
    }

    /* Secondary button */
    div[data-testid="column"]:nth-of-type(2) .stButton > button {
        background: rgba(79,124,255,0.12) !important;
        color: #dbe4ff !important;
        border: 1px solid rgba(139,92,246,0.35) !important;
        height: 52px !important;
        font-size: 1rem !important;
        box-shadow: none !important;
    }
    div[data-testid="column"]:nth-of-type(2) .stButton > button:hover {
        background: rgba(255,255,255,0.08) !important;
        color: #e2e8f0 !important;
        border-color: rgba(255,255,255,0.2) !important;
        transform: translateY(-1px) !important;
    }

    /* ── SCROLL ANIMATIONS ── */
    @keyframes fadeUp {
        from { opacity: 0; transform: translateY(30px); }
        to   { opacity: 1; transform: translateY(0); }
    }
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-12px); }
    }
    @keyframes pulse-glow {
        0%, 100% { box-shadow: 0 0 40px rgba(91,78,248,0.3); }
        50% { box-shadow: 0 0 80px rgba(91,78,248,0.6), 0 0 120px rgba(139,92,246,0.3); }
    }
    @keyframes spin-slow {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    @keyframes shimmer {
        0% { background-position: -200% center; }
        100% { background-position: 200% center; }
    }

    /* ── NAV ── */
    .sw-nav {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 24px 60px;
        position: sticky;
        top: 0;
        z-index: 100;
        background: rgba(5,7,15,0.85);
        backdrop-filter: blur(20px);
        border-bottom: 1px solid rgba(255,255,255,0.05);
    }
    .sw-nav-logo {
        font-family: 'Syne', sans-serif;
        font-size: 1.4rem;
        font-weight: 800;
        background: linear-gradient(135deg, #818cf8, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        letter-spacing: -0.5px;
    }
    .sw-nav-logo-wrap {
        display: flex;
        align-items: center;
    }
    .sw-nav-logo-wrap img {
        height: 40px;
        max-width: 180px;
        object-fit: contain;
        display: block;
        filter: drop-shadow(0 0 10px rgba(129,140,248,0.25));
    }
    .sw-nav-links {
        display: flex;
        gap: 36px;
        font-size: 0.875rem;
        color: #64748b;
        font-weight: 500;
    }

    /* ── HERO ── */
    .sw-hero {
        position: relative;
        min-height: 92vh;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        padding: 80px 40px 60px;
        overflow: hidden;
        animation: fadeUp 0.8s ease both;
    }
    .sw-hero-orb-1 {
        position: absolute;
        width: 700px; height: 700px;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(91,78,248,0.18) 0%, transparent 70%);
        top: -200px; left: 50%;
        transform: translateX(-50%);
        pointer-events: none;
        filter: blur(40px);
    }
    .sw-hero-orb-2 {
        position: absolute;
        width: 400px; height: 400px;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(139,92,246,0.12) 0%, transparent 70%);
        bottom: 0; right: 10%;
        pointer-events: none;
        filter: blur(60px);
    }
    .sw-hero-orb-3 {
        position: absolute;
        width: 300px; height: 300px;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(34,211,238,0.08) 0%, transparent 70%);
        bottom: 20%; left: 5%;
        pointer-events: none;
        filter: blur(50px);
    }
    .sw-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: rgba(91,78,248,0.1);
        border: 1px solid rgba(91,78,248,0.3);
        border-radius: 99px;
        padding: 6px 18px;
        font-size: 0.78rem;
        font-weight: 600;
        color: #a5b4fc;
        margin-bottom: 32px;
        letter-spacing: 0.5px;
        animation: fadeUp 0.6s 0.1s ease both;
    }
    .sw-badge-dot {
        width: 7px; height: 7px;
        border-radius: 50%;
        background: #818cf8;
        animation: pulse-glow 2s infinite;
        box-shadow: 0 0 8px rgba(129,140,248,0.8);
    }
    .sw-hero-title {
        font-family: 'Syne', sans-serif;
        font-size: clamp(3.2rem, 7vw, 6rem);
        font-weight: 800;
        line-height: 1.05;
        letter-spacing: -2px;
        background: linear-gradient(135deg, #f1f5f9 20%, #94a3b8 80%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 8px;
        animation: fadeUp 0.7s 0.2s ease both;
    }
    .sw-hero-title span {
        background: linear-gradient(135deg, #818cf8, #c084fc, #38bdf8);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: shimmer 4s linear infinite;
    }
    .sw-hero-sub {
        font-size: clamp(1rem, 2vw, 1.3rem);
        color: #475569;
        max-width: 580px;
        margin: 0 auto 48px;
        line-height: 1.65;
        font-weight: 400;
        animation: fadeUp 0.7s 0.35s ease both;
    }
    .sw-hero-sub strong { color: #94a3b8; font-weight: 600; }

    .sw-hero-btns {
        display: flex;
        gap: 16px;
        justify-content: center;
        flex-wrap: wrap;
        animation: fadeUp 0.7s 0.5s ease both;
    }

    /* ── STATS BAR ── */
    .sw-stats {
        display: flex;
        justify-content: center;
        gap: 60px;
        padding: 32px 40px;
        border-top: 1px solid rgba(255,255,255,0.05);
        border-bottom: 1px solid rgba(255,255,255,0.05);
        background: rgba(255,255,255,0.01);
        animation: fadeUp 0.7s 0.7s ease both;
    }
    .sw-stat { text-align: center; }
    .sw-stat-val {
        font-family: 'Syne', sans-serif;
        font-size: 2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #818cf8, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .sw-stat-label { font-size: 0.78rem; color: #475569; font-weight: 500; margin-top: 4px; letter-spacing: 0.5px; }

    /* ── SECTION ── */
    .sw-section {
        padding: 100px 60px;
        max-width: 1200px;
        margin: 0 auto;
    }
    .sw-section-tag {
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 3px;
        color: #818cf8;
        margin-bottom: 16px;
    }
    .sw-section-title {
        font-family: 'Syne', sans-serif;
        font-size: clamp(2rem, 4vw, 3rem);
        font-weight: 800;
        line-height: 1.1;
        letter-spacing: -1px;
        color: #f1f5f9;
        margin-bottom: 16px;
    }
    .sw-section-desc {
        font-size: 1rem;
        color: #475569;
        max-width: 520px;
        line-height: 1.7;
    }

    /* ── FEATURES GRID ── */
    .sw-features {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 20px;
        margin-top: 60px;
    }
    .sw-feature-card {
        background: linear-gradient(145deg, #0c0f1a, #101523);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 20px;
        padding: 36px 32px;
        position: relative;
        overflow: hidden;
        transition: transform 0.25s ease, border-color 0.25s ease, box-shadow 0.25s ease;
    }
    .sw-feature-card::before {
        content: '';
        position: absolute;
        inset: 0;
        background: radial-gradient(ellipse at top left, rgba(91,78,248,0.05), transparent 60%);
        pointer-events: none;
    }
    .sw-feature-card:hover {
        transform: translateY(-6px);
        border-color: rgba(91,78,248,0.25);
        box-shadow: 0 30px 80px rgba(0,0,0,0.5), 0 0 0 1px rgba(91,78,248,0.1);
    }
    .sw-feature-icon {
        width: 52px; height: 52px;
        border-radius: 14px;
        display: flex; align-items: center; justify-content: center;
        font-size: 1.5rem;
        margin-bottom: 24px;
    }
    .sw-feature-title {
        font-family: 'Syne', sans-serif;
        font-size: 1.15rem;
        font-weight: 700;
        color: #e2e8f0;
        margin-bottom: 10px;
        letter-spacing: -0.3px;
    }
    .sw-feature-desc {
        font-size: 0.9rem;
        color: #475569;
        line-height: 1.65;
    }
    .sw-feature-arrow {
        position: absolute;
        bottom: 28px; right: 28px;
        font-size: 1.1rem;
        color: rgba(129,140,248,0.3);
        transition: color 0.2s, transform 0.2s;
    }
    .sw-feature-card:hover .sw-feature-arrow {
        color: rgba(129,140,248,0.8);
        transform: translate(3px, -3px);
    }

    /* ── APP PREVIEW ── */
    .sw-preview-section {
        padding: 60px 60px 100px;
        text-align: center;
        position: relative;
        overflow: hidden;
    }
    .sw-preview-section::before {
        content: '';
        position: absolute;
        width: 800px; height: 400px;
        background: radial-gradient(ellipse, rgba(91,78,248,0.1) 0%, transparent 70%);
        top: 0; left: 50%; transform: translateX(-50%);
        pointer-events: none;
        filter: blur(40px);
    }
    .sw-mockup {
        max-width: 880px;
        margin: 60px auto 0;
        background: linear-gradient(145deg, #0c0f1a, #0f1420);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 24px;
        overflow: hidden;
        box-shadow: 0 60px 120px rgba(0,0,0,0.7), 0 0 0 1px rgba(255,255,255,0.04), 0 0 60px rgba(91,78,248,0.15);
        animation: float 6s ease-in-out infinite, pulse-glow 4s ease-in-out infinite;
        position: relative;
    }
    .sw-mockup-topbar {
        background: rgba(255,255,255,0.03);
        border-bottom: 1px solid rgba(255,255,255,0.06);
        padding: 14px 20px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .sw-mockup-dot { width: 12px; height: 12px; border-radius: 50%; }
    .sw-mockup-url {
        flex: 1;
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 6px;
        padding: 5px 14px;
        font-size: 0.75rem;
        color: #334155;
        text-align: center;
        font-family: 'DM Sans', monospace;
    }
    .sw-mockup-body {
        display: grid;
        grid-template-columns: 200px 1fr;
        min-height: 380px;
    }
    .sw-mockup-sidebar {
        background: rgba(255,255,255,0.015);
        border-right: 1px solid rgba(255,255,255,0.05);
        padding: 28px 16px;
        display: flex;
        flex-direction: column;
        gap: 8px;
    }
    .sw-mockup-nav-item {
        padding: 10px 14px;
        border-radius: 10px;
        font-size: 0.78rem;
        color: #334155;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .sw-mockup-nav-item.active {
        background: linear-gradient(135deg, rgba(91,78,248,0.2), rgba(139,92,246,0.12));
        color: #a5b4fc;
        border: 1px solid rgba(91,78,248,0.2);
    }
    .sw-mockup-content {
        padding: 28px;
        display: flex;
        flex-direction: column;
        gap: 18px;
    }
    .sw-mockup-title-row {
        font-family: 'Syne', sans-serif;
        font-size: 1.1rem;
        font-weight: 700;
        color: #94a3b8;
    }
    .sw-mockup-cards {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 12px;
    }
    .sw-mockup-card {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 12px;
        padding: 16px;
    }
    .sw-mockup-card-label { font-size: 0.62rem; color: #334155; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 8px; }
    .sw-mockup-card-val { font-size: 1.1rem; font-weight: 700; font-family: monospace; }
    .sw-mockup-bar {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.05);
        border-radius: 12px;
        padding: 16px;
        display: flex;
        flex-direction: column;
        gap: 10px;
    }
    .sw-bar-row { display: flex; align-items: center; gap: 12px; }
    .sw-bar-label { font-size: 0.72rem; color: #475569; min-width: 60px; }
    .sw-bar-track { flex: 1; height: 6px; background: rgba(255,255,255,0.05); border-radius: 99px; overflow: hidden; }
    .sw-bar-fill { height: 100%; border-radius: 99px; }
    .sw-bar-amt { font-size: 0.72rem; color: #64748b; min-width: 50px; text-align: right; }

    /* ── WHY SECTION ── */
    .sw-why-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 24px;
        margin-top: 60px;
    }
    .sw-why-card {
        text-align: center;
        padding: 44px 28px;
        background: linear-gradient(160deg, #0c0f1a, #0f1420);
        border: 1px solid rgba(255,255,255,0.05);
        border-radius: 20px;
        transition: transform 0.25s, border-color 0.25s;
    }
    .sw-why-card:hover {
        transform: translateY(-5px);
        border-color: rgba(129,140,248,0.2);
    }
    .sw-why-num {
        font-family: 'Syne', sans-serif;
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(135deg, #818cf8, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        line-height: 1;
        margin-bottom: 20px;
    }
    .sw-why-title { font-size: 1rem; font-weight: 700; color: #e2e8f0; margin-bottom: 10px; font-family: 'Syne', sans-serif; }
    .sw-why-desc { font-size: 0.87rem; color: #475569; line-height: 1.65; }

    /* ── FOOTER ── */
    .sw-footer {
        border-top: 1px solid rgba(255,255,255,0.05);
        padding: 60px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .sw-footer-logo {
        font-family: 'Syne', sans-serif;
        font-size: 1.2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #818cf8, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .sw-footer-links { display: flex; gap: 32px; font-size: 0.82rem; color: #334155; font-weight: 500; }
    .sw-footer-copy { font-size: 0.78rem; color: #1e293b; }
    .sw-footer-credit { font-size: 0.78rem; color: #334155; }
    .sw-footer-credit span { color: #4f46e5; font-weight: 600; }

    /* ── SCROLLBAR ── */
    ::-webkit-scrollbar { width: 5px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: rgba(91,78,248,0.3); border-radius: 99px; }

    </style>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  LANDING PAGE COMPONENTS
# ─────────────────────────────────────────────

def _hero_section():
    # ── CSS: style real Streamlit buttons to look premium ──
    st.markdown("""
    <style>
    @keyframes btn-shimmer {
        0%   { background-position: 200%% center; }
        100% { background-position: -200%% center; }
    }
    @keyframes btn-glow-pulse {
        0%, 100%% { box-shadow: 0 0 24px rgba(99,102,241,0.5), 0 0 60px rgba(139,92,246,0.2), inset 0 1px 0 rgba(255,255,255,0.15); }
        50%%      { box-shadow: 0 0 40px rgba(99,102,241,0.8), 0 0 90px rgba(139,92,246,0.4), inset 0 1px 0 rgba(255,255,255,0.2); }
    }

    /* ── Wrapper that centers the two columns ── */
    .sw-hero-btns-wrap {
        display: flex;
        justify-content: center;
        padding: 0 0 32px;
    }
    .sw-hero-btns-wrap > div[data-testid="stHorizontalBlock"] {
        max-width: 540px;
        width: 100%%;
        gap: 16px !important;
    }

    /* ── PRIMARY: Get Started button ── */
    div[data-testid="stButton"] button[data-testid="baseButton-secondary"][id="btn_getstarted"],
    .sw-hero-btns-wrap div[data-testid="column"]:nth-of-type(1) button {
        position: relative !important;
        height: 60px !important;
        width: 100%% !important;
        font-family: 'Space Grotesk', sans-serif !important;
        font-size: 1rem !important;
        font-weight: 700 !important;
        color: #ffffff !important;
        letter-spacing: 0.3px !important;
        border-radius: 16px !important;
        border: none !important;
        cursor: pointer !important;
        background: linear-gradient(
            135deg,
            #6366f1 0%%, #8b5cf6 30%%,
            #a78bfa 50%%, #8b5cf6 70%%,
            #6366f1 100%%
        ) !important;
        background-size: 300%% auto !important;
        animation: btn-shimmer 4s linear infinite, btn-glow-pulse 3s ease-in-out infinite !important;
        transition: transform 0.2s ease, filter 0.2s ease !important;
        overflow: hidden !important;
    }
    .sw-hero-btns-wrap div[data-testid="column"]:nth-of-type(1) button:hover {
        transform: translateY(-4px) scale(1.02) !important;
        filter: brightness(1.12) !important;
    }
    .sw-hero-btns-wrap div[data-testid="column"]:nth-of-type(1) button:active {
        transform: translateY(-1px) scale(0.99) !important;
    }
    /* Gloss sheen via pseudo - override with gradient overlay using outline trick */
    .sw-hero-btns-wrap div[data-testid="column"]:nth-of-type(1) button::after {
        content: '' !important;
        position: absolute !important;
        top: 0; left: 0; right: 0 !important;
        height: 50%% !important;
        background: linear-gradient(to bottom, rgba(255,255,255,0.18), transparent) !important;
        border-radius: 16px 16px 0 0 !important;
        pointer-events: none !important;
    }

    /* ── SECONDARY: Login button ── */
    .sw-hero-btns-wrap div[data-testid="column"]:nth-of-type(2) button {
        position: relative !important;
        height: 60px !important;
        width: 100%% !important;
        font-family: 'Space Grotesk', sans-serif !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
        color: #c4b5fd !important;
        letter-spacing: 0.2px !important;
        border-radius: 16px !important;
        cursor: pointer !important;
        background: rgba(99,102,241,0.08) !important;
        backdrop-filter: blur(16px) !important;
        -webkit-backdrop-filter: blur(16px) !important;
        border: 1px solid rgba(139,92,246,0.45) !important;
        box-shadow:
            0 0 0 1px rgba(99,102,241,0.1),
            inset 0 1px 0 rgba(255,255,255,0.07),
            0 8px 32px rgba(0,0,0,0.3) !important;
        transition: all 0.25s ease !important;
    }
    .sw-hero-btns-wrap div[data-testid="column"]:nth-of-type(2) button:hover {
        color: #e2e8f0 !important;
        background: rgba(99,102,241,0.18) !important;
        border-color: rgba(139,92,246,0.75) !important;
        box-shadow:
            0 0 24px rgba(99,102,241,0.35),
            0 0 70px rgba(139,92,246,0.18),
            inset 0 1px 0 rgba(255,255,255,0.1),
            0 14px 40px rgba(0,0,0,0.4) !important;
        transform: translateY(-3px) !important;
    }
    .sw-hero-btns-wrap div[data-testid="column"]:nth-of-type(2) button:active {
        transform: translateY(-1px) !important;
    }

    /* Also style the bottom CTA button */
    .sw-cta-bottom-wrap div[data-testid="column"]:nth-of-type(1) button {
        position: relative !important;
        height: 60px !important;
        width: 100%% !important;
        font-family: 'Space Grotesk', sans-serif !important;
        font-size: 1.05rem !important;
        font-weight: 700 !important;
        color: #ffffff !important;
        border-radius: 16px !important;
        border: none !important;
        background: linear-gradient(135deg,#6366f1 0%%,#8b5cf6 35%%,#a78bfa 50%%,#8b5cf6 70%%,#6366f1 100%%) !important;
        background-size: 300%% auto !important;
        animation: btn-shimmer 4s linear infinite, btn-glow-pulse 3s ease-in-out infinite !important;
        transition: transform 0.2s ease, filter 0.2s ease !important;
    }
    .sw-cta-bottom-wrap div[data-testid="column"]:nth-of-type(1) button:hover {
        transform: translateY(-4px) scale(1.02) !important;
        filter: brightness(1.12) !important;
    }
    </style>

    <div class="sw-hero">
        <div class="sw-hero-orb-1"></div>
        <div class="sw-hero-orb-2"></div>
        <div class="sw-hero-orb-3"></div>
        <div class="sw-hero-title">Spend<span>Wise</span></div>
        <div class="sw-hero-sub">
            Track smarter. Save better.<br>
            <strong>Control your finances</strong> with clarity, every rupee, every day.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Real Streamlit buttons inside a centered wrapper div
    st.markdown('<div class="sw-hero-btns-wrap">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✦  Get Started — It's Free", key="cta_get_started", use_container_width=True):
            st.session_state["page"] = "login"
            st.session_state["login_tab"] = "signup"
            st.rerun()
    with col2:
        if st.button("🔒︎  Login to Account", key="cta_login", use_container_width=True):
            st.session_state["page"] = "login"
            st.session_state["login_tab"] = "login"
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)


def _stats_bar():
    st.markdown("""
    <div class="sw-stats">
        <div class="sw-stat">
            <div class="sw-stat-val">₹10L+</div>
            <div class="sw-stat-label">Tracked across users</div>
        </div>
        <div class="sw-stat">
            <div class="sw-stat-val">5K+</div>
            <div class="sw-stat-label">Transactions logged</div>
        </div>
        <div class="sw-stat">
            <div class="sw-stat-val">9+</div>
            <div class="sw-stat-label">Expense categories</div>
        </div>
        <div class="sw-stat">
            <div class="sw-stat-val">100%</div>
            <div class="sw-stat-label">Secure & private</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def _features_section():
    st.markdown("""
    <div class="sw-section">
        <div class="sw-section-tag">✦ Features</div>
        <div class="sw-section-title">Everything you need to<br>own your money</div>
        <div class="sw-section-desc">
            A complete financial toolkit built for students and professionals in India —
            no spreadsheets, no confusion.
        </div>
        <div class="sw-features">
            <div class="sw-feature-card">
                <div class="sw-feature-icon" style="background:rgba(52,211,153,0.1);">⌕</div>
                <div class="sw-feature-title">Expense Tracking</div>
                <div class="sw-feature-desc">
                    Log every rupee in seconds. Categorise food, travel, rent, recharge —
                    with full history and instant search.
                </div>
                <div class="sw-feature-arrow">↗</div>
            </div>
            <div class="sw-feature-card">
                <div class="sw-feature-icon" style="background:rgba(91,78,248,0.1);">ⓘ</div>
                <div class="sw-feature-title">Smart Analytics</div>
                <div class="sw-feature-desc">
                    Visual charts that reveal where your money actually goes —
                    monthly trends, category breakdowns, and surplus tracking.
                </div>
                <div class="sw-feature-arrow">↗</div>
            </div>
            <div class="sw-feature-card">
                <div class="sw-feature-icon" style="background:rgba(192,132,252,0.1);">🗓</div>
                <div class="sw-feature-title">Budget Planning</div>
                <div class="sw-feature-desc">
                    Set monthly budgets and daily limits. Get warned before you overspend —
                    stay disciplined without thinking about it.
                </div>
                <div class="sw-feature-arrow">↗</div>
            </div>
            <div class="sw-feature-card">
                <div class="sw-feature-icon" style="background:rgba(56,189,248,0.1);">☁</div>
                <div class="sw-feature-title">Secure Cloud Storage</div>
                <div class="sw-feature-desc">
                    Your data lives in Supabase cloud — encrypted, backed up, and accessible
                    from any device, anywhere you go.
                </div>
                <div class="sw-feature-arrow">↗</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def _app_preview_section():
    import base64, os
    #real dashboard screenshot
    with open("ss.PNG","rb") as f:
                _ss_b64 = base64.b64encode(f.read()).decode()
                
    st.markdown(f"""      
    <div class="sw-preview-section">
        <div class="sw-section-tag" style="text-align:center;">✦ App Preview</div>
        <div class="sw-section-title" style="text-align:center;">See it in action</div>
        <div class="sw-section-desc" style="text-align:center;margin:0 auto 48px;">
            A clean, dark interface designed to surface what matters — your money, your control.
        </div>
        <div class="sw-mockup">
            <div class="sw-mockup-topbar">
                <div class="sw-mockup-dot" style="background:#ff5f57;"></div>
                <div class="sw-mockup-dot" style="background:#ffbd2e;"></div>
                <div class="sw-mockup-dot" style="background:#28c840;"></div>
                <div class="sw-mockup-url">spendwise.streamlit.app · Dashboard</div>
            </div>
            <div style="padding:0;line-height:0;">
                <img
                    src="data:image/png;base64,{_ss_b64}"
                    style="width:100%;display:block;border-radius:0 0 22px 22px;object-fit:cover;"
                    alt="SpendWise Dashboard Preview"
                />
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def _why_section():
    st.markdown("""
    <div class="sw-section" style="padding-top:40px;">
        <div class="sw-section-tag">✦ Why SpendWise</div>
        <div class="sw-section-title">Built different.<br>Because you deserve better.</div>
        <div class="sw-section-desc">
            Most finance apps are complicated or ugly. SpendWise is neither —
            it's minimal, fast, and actually enjoyable to use.
        </div>
        <div class="sw-why-grid">
            <div class="sw-why-card">
                <div class="sw-why-num">01</div>
                <div class="sw-why-title">Made for India</div>
                <div class="sw-why-desc">
                    Built with ₹ in mind. Indian categories, Indian context —
                    food, recharge, rent, stipend. Not a copy of a Western app.
                </div>
            </div>
            <div class="sw-why-card">
                <div class="sw-why-num">02</div>
                <div class="sw-why-title">Zero friction</div>
                <div class="sw-why-desc">
                    Log a transaction in 3 clicks. No bloated menus, no onboarding hell.
                    Open the app and start tracking — that's it.
                </div>
            </div>
            <div class="sw-why-card">
                <div class="sw-why-num">03</div>
                <div class="sw-why-title">Actually private</div>
                <div class="sw-why-desc">
                    Your data never gets sold. No ads, no tracking, no creepy recommendations.
                    Powered by Supabase with row-level security.
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def _cta_banner():
    st.markdown("""
    <div style="padding:20px 60px 80px;">
        <div style="
            background: linear-gradient(135deg, #0c0f1a, #101523);
            border: 1px solid rgba(91,78,248,0.2);
            border-radius: 24px;
            padding: 70px 60px 48px;
            text-align: center;
            position: relative;
            overflow: hidden;
            box-shadow: 0 30px 80px rgba(0,0,0,0.4), 0 0 60px rgba(91,78,248,0.08);
        ">
            <div style="position:absolute;inset:0;background:radial-gradient(ellipse at center top,rgba(91,78,248,0.12),transparent 60%);pointer-events:none;"></div>
            <div style="font-family:'Syne',sans-serif;font-size:2.4rem;font-weight:800;color:#f1f5f9;letter-spacing:-1px;margin-bottom:16px;line-height:1.1;">
                Ready to take control?
            </div>
            <div style="font-size:1rem;color:#475569;max-width:440px;margin:0 auto 36px;line-height:1.6;">
                Join thousands tracking their finances with SpendWise. Free, always.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Real Streamlit button centered and styled via .sw-cta-bottom-wrap CSS
    st.markdown('<div class="sw-cta-bottom-wrap">', unsafe_allow_html=True)
    _, col, _ = st.columns([2.5, 1.5, 2.5])
    with col:
        if st.button("✦  Get Started Free", key="cta_bottom", use_container_width=True):
            st.session_state["page"] = "login"
            st.session_state["login_tab"] = "signup"
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)


def _footer():
    st.markdown("""
    <div class="sw-footer">
        <div>
            <div class="sw-footer-logo">SpendWise</div>
            <div class="sw-footer-credit" style="margin-top:8px;">
                Developed by <span>Sharvil Mithari</span> · India 2026
            </div>
        </div>
        <div class="sw-footer-links">
            <span>Features</span>
            <span>Analytics</span>
            <span>Security</span>
            <span>Contact</span>
        </div>
        <div class="sw-footer-copy">
            © 2026 SpendWise India · All rights reserved
        </div>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  MAIN LANDING PAGE FUNCTION
# ─────────────────────────────────────────────

def show_landing_page():
    import base64, os
    inject_landing_css()

    # ── Load logo as base64 (same approach as show_login) ──
    logo_b64 = ""
    if os.path.exists("logo.png"):
        with open("logo.png", "rb") as f:
            logo_b64 = base64.b64encode(f.read()).decode()

    if logo_b64:
        nav_logo_html = f'<img src="data:image/png;base64,{logo_b64}" style="height:40px;max-width:160px;object-fit:contain;display:block;" alt="SpendWise">'
    else:
        nav_logo_html = '<span class="sw-nav-logo">💰 SpendWise</span>'

    # Navbar
    st.markdown(f"""
    <div class="sw-nav">
        <div class="sw-nav-logo-wrap">{nav_logo_html}</div>
        <div class="sw-nav-links">
            <span>Features</span>
            <span>Analytics</span>
            <span>Security</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    _hero_section()
    _stats_bar()
    _features_section()
    _app_preview_section()
    _why_section()
    _cta_banner()
    _footer()