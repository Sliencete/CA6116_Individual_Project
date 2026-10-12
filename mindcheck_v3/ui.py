import streamlit as st
CSS="""<style>
:root{--ink:#16212f;--muted:#6f7b86;--paper:#fbfaf7;--line:#e7e4de}
.stApp{background:var(--paper);color:var(--ink)}.block-container{max-width:1040px;padding-top:1.3rem;padding-bottom:3rem}[data-testid="stSidebar"]{background:#f4f2ed;border-right:1px solid var(--line)}
.page-title{font-size:2.5rem;margin:1.2rem 0 .35rem}.page-subtitle{color:var(--muted);font-size:1.03rem;margin-bottom:1.4rem}.hero-title{font-size:3.1rem;line-height:1.03}.hero-title span{color:#7c8791}.hero-copy{font-size:1.12rem;color:#52606c;max-width:760px}.eyebrow{font-weight:800;font-size:.78rem;letter-spacing:.14em;color:#64726b}
.entry-card,.question-card,.feedback-card,.scope-summary,.code-card,.evidence-card{border:1px solid var(--line);border-radius:18px;background:#fff;padding:1.2rem 1.3rem;margin:.8rem 0 1rem;box-shadow:0 5px 18px rgba(25,30,35,.035)}
.entry-card{min-height:160px}.question-label{color:#6e7f75;font-size:.75rem;font-weight:800;letter-spacing:.1em;margin-bottom:.5rem}.question-text{font-size:1.15rem;line-height:1.55;font-weight:650}.paused-note{color:#557263;font-size:.93rem;text-align:right}.feedback-card.green,.code-card{background:#edf6ef}.feedback-card.warm{background:#fff3df}.feedback-title{font-weight:800}.scope-chip{display:inline-block;background:#edf6ef;border-radius:999px;padding:.45rem .75rem;color:#4c6d5b;font-size:.86rem}.check-code{font-size:2.15rem;font-weight:850;letter-spacing:.12em;text-align:center}
.progress-track{height:6px;background:#e2e5e2;border-radius:20px}.progress-bar{height:100%;background:#69b58d;border-radius:20px}.progress-meta{display:flex;justify-content:space-between;color:#7b858e;font-size:.78rem}.level-strong{color:#34865f;font-weight:800}.level-developing{color:#d38b29;font-weight:800}.level-limited{color:#b85b55;font-weight:800}.level-unavailable{color:#6f7b86;font-weight:800}
.stButton>button{min-height:46px;border-radius:12px;background:#fff!important;color:#16212f!important;border:1px solid #d9ddd9!important}.stButton>button p,.stButton>button span{color:#16212f!important}.stButton>button[kind="primary"]{background:#1f2b37!important;color:#fff!important}.stButton>button[kind="primary"] p,.stButton>button[kind="primary"] span{color:#fff!important}
[data-testid="stTextInput"] input,[data-testid="stTextArea"] textarea{background:#fff!important;color:#16212f!important;caret-color:#16212f!important}[data-testid="stTextInput"] input::placeholder,[data-testid="stTextArea"] textarea::placeholder{color:#9aa3aa!important;opacity:1!important}

/* Form readability */
[data-testid="stWidgetLabel"], [data-testid="stWidgetLabel"] p, .stMarkdown p, .stCaptionContainer, .stCaptionContainer p{color:#52606c!important}
[data-testid="stTextInput"] input,[data-testid="stTextArea"] textarea{border:1px solid #d8ddd8!important;border-radius:12px!important}
[data-testid="stTextInput"] input:focus,[data-testid="stTextArea"] textarea:focus{border-color:#7bb394!important;box-shadow:0 0 0 1px #7bb394!important}
.setup-section{display:flex;gap:.8rem;align-items:flex-start;margin:1.65rem 0 .55rem}.setup-number{width:28px;height:28px;min-width:28px;border-radius:50%;background:#e8f3eb;color:#3f7057;display:flex;align-items:center;justify-content:center;font-size:.82rem;font-weight:800}.setup-title{font-size:1.08rem;font-weight:800;color:#16212f;line-height:1.2}.setup-help{font-size:.91rem;color:#6f7b86;margin-top:.2rem;line-height:1.45}.optional-tag{font-size:.66rem;letter-spacing:.08em;background:#f0f1ef;color:#78817c;border-radius:999px;padding:.2rem .42rem;margin-left:.35rem;vertical-align:middle}.teacher-note{border:1px solid #dbe8df;background:#f1f7f3;border-radius:15px;padding:1rem 1.1rem;margin:1.5rem 0;color:#466052;line-height:1.55}
[data-testid="stSlider"]{padding-top:.25rem}.stAlert{border-radius:12px}

/* V3.2 robust text visibility across Streamlit versions */
html,body,.stApp{font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
.stApp{color:#16212f!important}
label, label p, [data-testid="stWidgetLabel"], [data-testid="stWidgetLabel"] p,
[data-testid="stMarkdownContainer"] p, [data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p,
.stCaptionContainer, .stCaptionContainer p{color:#52606c!important;opacity:1!important}
[data-testid="stTextInput"] input,[data-testid="stTextArea"] textarea{color:#16212f!important;-webkit-text-fill-color:#16212f!important;background:#fff!important}
[data-testid="stTextInput"] input::placeholder,[data-testid="stTextArea"] textarea::placeholder{color:#8b959d!important;-webkit-text-fill-color:#8b959d!important;opacity:1!important}
[data-testid="stSelectSlider"] p,[data-testid="stSlider"] p{color:#52606c!important}
.join-heading{display:flex;gap:.8rem;align-items:flex-start;margin:1.5rem 0 .55rem}.join-icon{width:28px;height:28px;min-width:28px;border-radius:50%;background:#e8f3eb;color:#3f7057;display:flex;align-items:center;justify-content:center;font-size:.82rem;font-weight:800}.join-title{font-size:1.06rem;font-weight:800;color:#16212f}.join-help{font-size:.91rem;color:#6f7b86;margin-top:.2rem;line-height:1.45}.student-note{border:1px solid #dbe8df;background:#f1f7f3;border-radius:15px;padding:1rem 1.1rem;margin:1.5rem 0;color:#466052;line-height:1.55}

.profile-divider{height:1px;background:#e7e4de;margin:1.2rem 0}.detail-card{border:1px solid #e7e4de;border-radius:16px;background:#fff;padding:1.1rem 1.2rem;margin:.8rem 0}.detail-head{display:flex;justify-content:space-between;align-items:center;font-size:1.08rem;font-weight:800;margin-bottom:.9rem}.detail-level{color:#52606c}.detail-grid{display:grid;grid-template-columns:1fr 1fr;gap:1rem;padding:.8rem 0;border-top:1px solid #f0eee9;border-bottom:1px solid #f0eee9}.detail-row{padding-top:.8rem;line-height:1.5}.unavailable-card{background:#f7f6f2;color:#59636c}
/* Hide Streamlit chrome that distracts during peer testing */
#MainMenu{visibility:hidden} footer{visibility:hidden}
</style>"""
def inject_css():st.markdown(CSS,unsafe_allow_html=True)
def sidebar_nav(page):
    with st.sidebar:
        st.markdown("## ◉ mindcheck");st.caption("Teacher-configurable post-AI check");st.markdown("---")
        st.write("Teacher" if page.startswith("teacher") else ("Home" if page=="home" else "Student"))
def top_progress(step,total):
    p=int(step/total*100);st.markdown(f'<div class="progress-meta"><span>{step} / {total}</span><span>Understanding Check</span></div><div class="progress-track"><div class="progress-bar" style="width:{p}%"></div></div>',unsafe_allow_html=True)
def evidence_badge(t,l,f):
    c={"Strong":"level-strong","Developing":"level-developing","Limited":"level-limited","Unavailable":"level-unavailable"}.get(l,"level-unavailable")
    st.markdown(f'<div class="evidence-card"><h3>{t}</h3><div class="{c}">{l}</div><p>{f}</p></div>',unsafe_allow_html=True)
