"""Presentation helpers. Escape all data before placing it in HTML."""
from html import escape
import streamlit as st

def page_style():
    st.markdown('''<style>
    :root {--ink:#203c35;--muted:#4f6158;--accent:#26735b;--line:#dce6de;}
    .stApp {background:#f5f7f2;color:var(--ink);}
    [data-testid="stHeader"] {background:transparent;}
    .stAppDeployButton {display:none;}
    .block-container {max-width:1180px;padding:2.3rem 2.5rem 3rem;}
    html,body,button,textarea,input,[data-testid="stText"] {font-family:"Malgun Gothic","Apple SD Gothic Neo",sans-serif;}
    [data-testid="stMarkdownContainer"] p,[data-testid="stText"] {font-size:18px;line-height:1.8;color:#30473f;}
    [data-testid="stWidgetLabel"] p {font-size:17px !important;font-weight:600;color:#344e44;}
    h1,h2,h3 {color:var(--ink);letter-spacing:-.05em;}
    h2 {font-size:26px !important;padding-top:0 !important;}
    h3 {font-size:22px !important;}
    [data-testid="stCaptionContainer"] p {font-size:14px;color:#4f6158;line-height:1.7;}
    textarea {font-size:19px !important;line-height:1.75 !important;}
    [data-baseweb="textarea"],[data-baseweb="select"]>div {border-radius:12px !important;background:#fafcf9 !important;}
    textarea:focus {box-shadow:none !important;}
    .stButton button,.stLinkButton a {border-radius:10px;min-height:46px;font-weight:600;}
    .stButton button p,.stLinkButton a p {font-size:16px;}
    .stButton button[kind="primary"] {background:#26735b;border-color:#26735b;color:white;}
    .stButton button[kind="primary"] p {color:white !important;}
    .stButton button[kind="primary"]:hover {background:#19583f;border-color:#19583f;}
    [data-testid="stFileUploader"] {padding:16px;background:#f3f7f1;border:1px dashed #bccdbd;border-radius:14px;}
    [data-testid="stExpander"] {background:white;border-radius:12px;border-color:var(--line);}
    [data-testid="stAlert"] {border-radius:12px;}
    .st-key-input_card,.st-key-product_card,.st-key-result_card {background:white;border:1px solid var(--line);border-radius:20px;padding:28px;margin-top:16px;box-shadow:0 6px 24px #183b2a04;}
    .st-key-ad_card,.st-key-official_card {border:1px solid var(--line);border-radius:16px;padding:24px;height:100%;}
    .st-key-ad_card {background:#fcfaf5;}
    .st-key-official_card {background:#f2f8f3;}
    .brand {display:flex;align-items:center;gap:12px;margin-bottom:34px;color:#294a3e;font-size:17px;font-weight:700;}
    .brand-mark {display:grid;place-items:center;background:#26735b;color:white;border-radius:11px;width:36px;height:36px;font-size:22px;}
    .brand-note {margin-left:auto;font-size:13px;color:#4f6158;font-weight:400;}
    .hero {display:flex;justify-content:space-between;gap:32px;align-items:center;padding:2px 0 26px;}
    .eyebrow {font-size:12px;font-weight:700;letter-spacing:.15em;color:#4f6158;margin:0 0 14px;}
    .hero h1 {font-size:42px !important;font-weight:750;line-height:1.35;letter-spacing:-.055em;margin:0 0 16px;padding:0;}
    .hero h1 span {color:#26735b;}
    .hero p {font-size:17px !important;margin:0;color:#4f6158;}
    .hero-note {background:#e8efe4;border:1px solid #dae4d4;border-radius:18px;padding:22px;min-width:220px;max-width:280px;transform:rotate(2deg);}
    .hero-note .note-label {font-size:12px;letter-spacing:.08em;color:#4f6158;}
    .hero-note strong {display:block;font-size:20px;line-height:1.6;margin:10px 0;color:#3f5f43;}
    .hero-note small {font-size:13px;color:#4f6158;line-height:1.7;display:block;}
    .steps {display:flex;gap:10px;margin:8px 0 22px;}
    .step {flex:1;display:flex;align-items:center;gap:11px;padding:14px 17px;background:#eaf0e7;border:1px solid #e0e8dc;border-radius:12px;color:#4f6158;font-size:15px;}
    .step b {display:grid;place-items:center;border-radius:50%;background:white;width:26px;height:26px;font-size:12px;}
    .step.active {background:#e0eee4;border-color:#b8d4bf;color:#21583e;font-weight:700;}
    .section-kicker {font-size:12px;letter-spacing:.12em;font-weight:700;color:#4f6158;margin-bottom:6px;}
    .section-hint {font-size:16px;color:#4f6158;line-height:1.7;margin-top:-6px;margin-bottom:24px;}
    .mini-title {font-size:19px;font-weight:700;color:#294a3e;margin:0 0 8px;}
    .mini-copy {font-size:14px;color:#4f6158;margin-bottom:18px;line-height:1.65;}
    .result-banner {padding:20px 24px;border-radius:14px;background:#eef4ed;margin:4px 0 22px;border-left:4px solid #61936d;}
    .result-banner.review {background:#fbf3e4;border-left-color:#c39641;}
    .result-banner strong {display:block;font-size:23px;letter-spacing:-.03em;margin-bottom:8px;}
    .result-banner p {font-size:16px !important;margin:0;line-height:1.75;}
    .tag {display:inline-block;padding:6px 11px;margin:4px 6px 8px 0;border-radius:8px;background:#f3e6c8;color:#745622;font-size:14px;font-weight:700;}
    .evidence {font-size:18px;color:#614e2b;line-height:1.7;margin-bottom:12px;}
    .product-meta {display:flex;gap:24px;flex-wrap:wrap;padding:16px 20px;background:#f2f6ef;border-radius:12px;margin:12px 0;}
    .product-meta span {font-size:12px;color:#4f6158;display:block;margin-bottom:4px;}
    .product-meta strong {font-size:17px;color:#34513c;}
    .footer {font-size:15px;color:#4f6158;line-height:1.8;padding:24px 2px 0;}
    @media(max-width:700px){.block-container{padding:1.5rem 1rem;} .hero h1{font-size:30px !important;} .hero-note,.brand-note{display:none;} .steps{gap:5px;} .step{font-size:12px;padding:10px 7px;gap:5px;} .st-key-input_card,.st-key-product_card,.st-key-result_card{padding:19px;} }
    </style>''',unsafe_allow_html=True)

def hero():
    active=3 if st.session_state.get('result') else (2 if 'candidates' in st.session_state else 1)
    st.markdown('''<div class="brand"><div class="brand-mark">✓</div>건강기능식품 광고 확인 도우미<span class="brand-note">구매 전, 함께 살펴보는 공식 표시</span></div>
    <div class="hero"><div><div class="eyebrow">CHECK BEFORE YOU CHOOSE</div>
    <h1>광고 속 한 문장,<br><span>공식 표시와 함께 확인해요.</span></h1>
    <p>사진을 올리거나 문구를 입력하면,<br>선택한 제품의 공식 기능성 표시를 나란히 보여드려요.</p></div>
    <div class="hero-note"><div class="note-label">살펴볼 때 기억해 주세요</div><strong>“도움을 줄 수 있음”과<br>“반드시 좋아짐”은<br>다른 표현이에요.</strong><small>표현의 차이와 출처를<br>직접 확인할 수 있도록 도와드려요.</small></div></div>''',unsafe_allow_html=True)
    st.markdown('<div class="steps">'+''.join(f'<div class="step {"active" if i==active else ""}"><b>{i:02}</b>{label}</div>' for i,label in enumerate(['문구 준비','제품 확인','표시 비교'],1))+'</div>',unsafe_allow_html=True)

def section(number,title,hint):
    st.markdown(f'<div class="section-kicker">STEP {number:02}</div>',unsafe_allow_html=True)
    st.header(title)
    st.markdown(f'<div class="section-hint">{escape(hint)}</div>',unsafe_allow_html=True)

def banner(title,note,review=False):
    st.markdown(f'<div class="result-banner {"review" if review else ""}"><strong>{escape(title)}</strong><p>{escape(note)}</p></div>',unsafe_allow_html=True)

def product_meta(p):
    st.markdown('<div class="product-meta">'+''.join(f'<div><span>{label}</span><strong>{escape(str(p[key]))}</strong></div>' for label,key in [('제품명','name'),('업체명','manufacturer'),('신고번호','report_number')])+'</div>',unsafe_allow_html=True)

def evidence_tag(tag,expressions):
    st.markdown(f'<span class="tag">{escape(tag)}</span><div class="evidence">{escape(expressions)}</div>',unsafe_allow_html=True)
