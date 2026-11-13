"""Presentation helpers. Escape all data before placing it in HTML."""
from html import escape
import streamlit as st

def page_style():
    st.markdown('''<style>
    :root {--ink:#1f2421;--muted:#555b56;--accent:#2f5d50;--line:#d8d5cb;--paper:#fbfaf7;}
    .stApp {background:var(--paper);color:var(--ink);}
    [data-testid="stHeader"] {background:transparent;}
    .stAppDeployButton {display:none;}
    .block-container {max-width:1080px;padding:2rem 2rem 3rem;}
    html,body,button,textarea,input,[data-testid="stText"] {font-family:"Malgun Gothic","Apple SD Gothic Neo",sans-serif;}
    [data-testid="stMarkdownContainer"] p,[data-testid="stText"] {font-size:17px;line-height:1.75;color:var(--ink);}
    [data-testid="stWidgetLabel"] p {font-size:16px !important;font-weight:600;color:var(--ink);}
    h1,h2,h3 {color:var(--ink);letter-spacing:-.02em;}
    h2 {font-size:24px !important;padding-top:0 !important;}
    h3 {font-size:20px !important;}
    [data-testid="stCaptionContainer"] p {font-size:14px;color:var(--muted);line-height:1.7;}
    textarea {font-size:18px !important;line-height:1.7 !important;}
    [data-baseweb="textarea"],[data-baseweb="select"]>div {border-radius:4px !important;background:white !important;}
    textarea:focus {box-shadow:none !important;}
    .stButton button,.stLinkButton a {border-radius:4px;min-height:44px;font-weight:600;}
    .stButton button p,.stLinkButton a p {font-size:16px;}
    .stButton button[kind="primary"] {background:var(--accent);border-color:var(--accent);color:white;}
    .stButton button[kind="primary"] p {color:white !important;}
    .stButton button[kind="primary"]:hover {background:#244a40;border-color:#244a40;}
    [data-testid="stFileUploader"] {padding:12px;background:white;border:1px dashed #b9b5a8;border-radius:4px;}
    [data-testid="stExpander"] {background:white;border-radius:4px;border-color:var(--line);}
    [data-testid="stAlert"] {border-radius:4px;}
    .st-key-input_card,.st-key-product_card,.st-key-result_card {border-top:2px solid var(--ink);padding:20px 0 8px;margin-top:28px;}
    .st-key-ad_card,.st-key-official_card {border:1px solid var(--line);border-radius:4px;padding:20px;height:100%;background:white;}
    .masthead {display:flex;justify-content:space-between;align-items:baseline;border-bottom:1px solid var(--line);padding-bottom:10px;margin-bottom:28px;font-size:15px;color:var(--muted);}
    .masthead b {color:var(--ink);font-size:16px;}
    .hero h1 {font-size:34px !important;font-weight:700;line-height:1.4;letter-spacing:-.03em;margin:0 0 12px;padding:0;}
    .hero p {font-size:17px !important;margin:0 0 14px;color:var(--muted);}
    .hero .remember {border-left:3px solid var(--accent);padding:2px 0 2px 14px;font-size:16px;color:var(--ink);margin-top:18px;}
    .steps {display:flex;gap:28px;margin:22px 0 4px;font-size:15px;color:var(--muted);}
    .step {padding-bottom:6px;border-bottom:2px solid transparent;}
    .step.active {color:var(--ink);font-weight:700;border-bottom-color:var(--ink);}
    .section-kicker {font-size:14px;font-weight:700;color:var(--accent);margin-bottom:2px;}
    .section-hint {font-size:16px;color:var(--muted);line-height:1.7;margin-top:-6px;margin-bottom:20px;}
    .mini-title {font-size:18px;font-weight:700;margin:0 0 6px;}
    .mini-copy {font-size:14px;color:var(--muted);margin-bottom:14px;line-height:1.65;}
    .result-banner {padding:16px 20px;background:#f1efe8;margin:4px 0 20px;border-left:4px solid var(--accent);}
    .result-banner.review {background:#f8f0dc;border-left-color:#a9791f;}
    .result-banner strong {display:block;font-size:21px;margin-bottom:6px;}
    .result-banner p {font-size:16px !important;margin:0;line-height:1.7;}
    .tag {display:inline-block;padding:2px 8px;margin:4px 6px 6px 0;border:1px solid #a9791f;color:#6b4b0f;font-size:14px;font-weight:700;}
    .evidence {font-size:17px;color:var(--ink);line-height:1.7;margin-bottom:12px;}
    .product-meta {display:flex;gap:28px;flex-wrap:wrap;padding:12px 0;border-top:1px solid var(--line);border-bottom:1px solid var(--line);margin:12px 0;}
    .product-meta span {font-size:13px;color:var(--muted);display:block;margin-bottom:2px;}
    .product-meta strong {font-size:16px;}
    .footer {font-size:14px;color:var(--muted);line-height:1.8;padding:24px 0 0;border-top:1px solid var(--line);margin-top:36px;}
    @media(max-width:700px){.block-container{padding:1.2rem 1rem;} .hero h1{font-size:26px !important;} .masthead span{display:none;} .steps{gap:14px;font-size:13px;}}
    </style>''',unsafe_allow_html=True)

def hero():
    active=3 if st.session_state.get('result') else (2 if 'candidates' in st.session_state else 1)
    st.markdown('''<div class="masthead"><b>건강기능식품 광고 확인 도우미</b><span>공식 표시와 대조해 보는 도구</span></div>
    <div class="hero"><h1>광고 문구를 공식 기능성 표시와 나란히 비교합니다</h1>
    <p>광고 사진을 올리거나 문구를 입력한 뒤 제품을 고르면, 식약처에 신고된 공식 표시를 함께 보여 줍니다.</p>
    <div class="remember">“도움을 줄 수 있음”과 “반드시 좋아짐”은 다른 표현입니다.</div></div>''',unsafe_allow_html=True)
    st.markdown('<div class="steps">'+''.join(f'<div class="step {"active" if i==active else ""}">{i}. {label}</div>' for i,label in enumerate(['문구 입력','제품 확인','표시 비교'],1))+'</div>',unsafe_allow_html=True)

def section(number,title,hint):
    st.markdown(f'<div class="section-kicker">{number}단계</div>',unsafe_allow_html=True)
    st.header(title)
    st.markdown(f'<div class="section-hint">{escape(hint)}</div>',unsafe_allow_html=True)

def banner(title,note,review=False):
    st.markdown(f'<div class="result-banner {"review" if review else ""}"><strong>{escape(title)}</strong><p>{escape(note)}</p></div>',unsafe_allow_html=True)

def product_meta(p):
    st.markdown('<div class="product-meta">'+''.join(f'<div><span>{label}</span><strong>{escape(str(p[key]))}</strong></div>' for label,key in [('제품명','name'),('업체명','manufacturer'),('신고번호','report_number')])+'</div>',unsafe_allow_html=True)

def evidence_tag(tag,expressions):
    st.markdown(f'<span class="tag">{escape(tag)}</span><div class="evidence">{escape(expressions)}</div>',unsafe_allow_html=True)
