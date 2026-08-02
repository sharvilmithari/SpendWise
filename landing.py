import streamlit as st

# ─────────────────────────────────────────────
#  LANDING PAGE CSS
# ─────────────────────────────────────────────

def inject_landing_css():
    try:
        from pathlib import Path
        css_path = Path(__file__).parent / "styles" / "landing.css"
        with open(css_path, "r", encoding="utf-8") as f:
            css = f.read()
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error loading CSS: {e}")


# ─────────────────────────────────────────────
#  LANDING PAGE COMPONENTS
# ─────────────────────────────────────────────

def _hero_section():
    st.markdown("""
    <div class="sw-hero">
        <div class="sw-hero-orb-1"></div>
        <div class="sw-hero-orb-2"></div>
        <div class="sw-hero-orb-3"></div>
        <div class="sw-badge">
            <div class="sw-badge-dot"></div>
            <span>✨ &nbsp;Introducing</span>
        </div>
        <div class="sw-hero-title">Spend<span>Wise</span></div>
        <div class="sw-hero-sub">
            Track smarter. Save better. Live wiser.<br>
            <strong>Your personal financial manager</strong> for budgeting, bills, goals, and smart tracking.
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
    <div class="sw-section" id="features">
        <div class="sw-section-tag">✦ Features</div>
        <div class="sw-section-title">Everything you need to<br>own your money</div>
        <div class="sw-section-desc">
            A complete financial management platform built for students and professionals in India —
            intelligent, automated, and collaborative.
        </div>
        <div class="sw-features">
            <div class="sw-feature-card">
                <div class="sw-feature-icon" style="background:rgba(129,140,248,0.1);">📊</div>
                <div class="sw-feature-title">Expense & Budget Tracker</div>
                <div class="sw-feature-desc">
                    Track daily income and expenses with automatic category breakdowns, monthly budget limits, and live spending warnings.
                </div>
                <div class="sw-feature-arrow">↗</div>
            </div>
            <div class="sw-feature-card">
                <div class="sw-feature-icon" style="background:rgba(52,211,153,0.1);">👥</div>
                <div class="sw-feature-title">Split Bills Ledger</div>
                <div class="sw-feature-desc">
                    Log shared bills with trip groups or flatmates. Enjoy automated Splitwise-style debt simplification and settlement tracking.
                </div>
                <div class="sw-feature-arrow">↗</div>
            </div>
            <div class="sw-feature-card">
                <div class="sw-feature-icon" style="background:rgba(192,132,252,0.1);">🎯</div>
                <div class="sw-feature-title">Smart Goals Tracker</div>
                <div class="sw-feature-desc">
                    Define financial targets. Model required savings rates, target dates, and real-time progress statistics.
                </div>
                <div class="sw-feature-arrow">↗</div>
            </div>
            <div class="sw-feature-card">
                <div class="sw-feature-icon" style="background:rgba(248,113,113,0.1);">📈</div>
                <div class="sw-feature-title">Analytics & Health Insights</div>
                <div class="sw-feature-desc">
                    Get clear visual pie charts, monthly spending trend graphs, category totals, and total financial control.
                </div>
                <div class="sw-feature-arrow">↗</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def _app_preview_section():
    import base64, os
    from pathlib import Path
    ss_path = Path(__file__).parent / "ss.PNG"
    
    #real dashboard screenshot
    with open(ss_path,"rb") as f:
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
                Take Control of Your Money Today
            </div>
            <div style="max-width:500px;margin:0 auto 32px;font-size:1.05rem;color:#64748b;line-height:1.5;">
                Join thousands of users tracking, splitting, and saving smarter with SpendWise.
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
        <div class="sw-footer-copy">
            © 2026 SpendWise India · All rights reserved
        </div>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  MAIN LANDING PAGE FUNCTION
# ─────────────────────────────────────────────

def show_landing_page():
    inject_landing_css()

    _hero_section()
    _stats_bar()
    _features_section()
    _app_preview_section()
    _why_section()
    _cta_banner()
    _footer()