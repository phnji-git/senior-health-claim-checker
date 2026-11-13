from pathlib import Path
from io import BytesIO
import hashlib
import streamlit as st
from PIL import Image
from src.products import search_candidates, product_by_id
from src.compare import analyze_claim
from src.ocr import read_text

st.set_page_config(page_title='건강기능식품 광고 확인 도우미', layout='wide')
from src.ui import page_style, hero, section, banner, product_meta, evidence_tag
page_style()
hero()

def clear_result():
    for key in ['searched_text','candidates','result','selected_product']:
        st.session_state.pop(key, None)

def clear_image():
    st.session_state.pop('ocr_result',None)
    st.session_state.pop('ocr_running',None)
    clear_result()

def start_ocr():
    # 클릭 콜백은 다음 화면을 그리기 전에 실행되므로, OCR 중에는 버튼이 비활성으로 그려진다
    st.session_state['ocr_running'] = True

with st.container(key='input_card'):
    section(1,'어떤 광고를 보셨나요?','사진으로 시작해도, 문구를 직접 적어도 괜찮아요.')
    image_col, text_col = st.columns([1,1.15],gap='large')
    with image_col:
        upload = st.file_uploader('광고 캡처 JPG / PNG (최대 10MB)',type=['jpg','jpeg','png'],max_upload_size=10,on_change=clear_image)
        payload = upload.getvalue() if upload else None
        with st.expander('합성 광고로 시연하기 (실제 광고 아님)'):
            sample = st.selectbox('시험 이미지', ['선택 안 함'] + [p.name for p in sorted((Path(__file__).parent/'data/synthetic/sample_ads').glob('*.png'))])
            if st.button('시험 이미지 불러오기') and sample != '선택 안 함':
                st.session_state['sample_bytes'] = (Path(__file__).parent/'data/synthetic/sample_ads'/sample).read_bytes()
                st.session_state['sample_name'] = sample
                clear_image()
            if st.button('시험 이미지 지우기'):
                st.session_state.pop('sample_bytes',None)
                clear_image()
        if payload is None:
            payload = st.session_state.get('sample_bytes')
            if payload:
                st.caption('synthetic_example · '+st.session_state['sample_name'])
        if payload:
            image_id=hashlib.sha256(payload).hexdigest()
            if st.session_state.get('image_id') != image_id:
                clear_image()
                st.session_state['image_id']=image_id
            try:
                preview = Image.open(BytesIO(payload))
                st.image(preview, caption='문구와 제품명을 확인해 주세요',width=580)
            except Exception:
                st.warning('이미지 미리보기를 열 수 없습니다. 직접 입력으로 계속할 수 있습니다.')
            running = st.session_state.get('ocr_running', False)
            st.button('사진에서 글자 읽기', on_click=start_ocr, disabled=running)
            st.caption('처음 읽을 때는 1분 가까이 걸릴 수 있어요. 버튼은 한 번만 눌러 주세요.')
            if running:
                clear_result()
                with st.spinner('사진의 글자를 읽고 있습니다… 잠시만 기다려 주세요.'):
                    ocr = read_text(payload)
                st.session_state['ocr_result'] = ocr
                st.session_state['ad_text'] = ocr['text']
                st.session_state['ocr_running'] = False
                st.rerun()
            if 'ocr_result' in st.session_state:
                ocr=st.session_state['ocr_result']
                if ocr['status'] != 'ok':
                    st.warning('사진에서 글자를 정확히 읽지 못했습니다. 아래에서 문구를 고치거나 제품명을 직접 입력해 주세요.')
                else:
                    st.info('인식한 문구에 오타가 있을 수 있습니다. 이미지와 대조하고 아래에서 수정해 주세요.')
                if ocr.get('low_conf'):
                    st.warning('특히 다시 확인할 부분: '+' / '.join(ocr['low_conf']))
                    st.caption('글자가 흐리게 읽힌 부분입니다. 여기에 없는 부분도 틀렸을 수 있어요.')
                if ocr.get('error'):
                    st.caption('OCR 처리 상태: '+ocr['error']+' · README의 모델 준비 안내를 확인하세요.')

    with text_col:
        st.markdown('<div class="mini-title">광고 문구를 확인해 주세요</div><div class="mini-copy">사진에서 읽은 글자는 틀릴 수 있어요. 제품명과 표현을 고친 뒤 검색해 주세요.</div>',unsafe_allow_html=True)
        ad=st.text_area('광고 문구 (직접 입력하거나 인식 문구 수정)',key='ad_text',height=160,on_change=clear_result,
                        placeholder='예: 홍삼정 스틱 면역력 증진, 피로개선에 도움을 줄 수 있음')
        if st.button('이 문구로 제품 찾기',type='primary'):
            clear_result()
            if not ad.strip():
                st.warning('광고 문구 또는 제품명·신고번호를 입력해 주세요.')
            else:
                try:
                    st.session_state['candidates']=search_candidates(ad)
                    st.session_state['searched_text']=ad
                    st.rerun()
                except (OSError, ValueError, KeyError) as e:
                    st.error('제품 자료를 읽지 못했습니다. data/processed 파일과 README를 확인해 주세요.')
                    st.caption(type(e).__name__)

if 'candidates' in st.session_state:
    with st.container(key='product_card'):
        candidates=st.session_state['candidates']
        section(2,'같은 제품인지 확인해 주세요','제품 이름뿐 아니라 업체명과 신고번호까지 포장과 대조해 주세요.')
        if not candidates:
            st.warning('제품을 특정하지 못해 공식 표시를 비교하지 못했습니다. 제품명이나 품목 신고번호를 확인해 주세요.')
            st.write('오타를 고치거나 포장의 정확한 제품명·신고번호로 다시 검색하세요. 현재 저장된 자료 범위 밖일 수도 있습니다.')
            st.caption('출처: 제품을 특정하지 못함 · 확인일: 해당 없음')
        else:
            st.caption('비슷한 이름의 후보를 최대 10개 보여드려요. 제품은 직접 선택해 주세요.')
            labels={r['id']:f"{r['name']} | {r['manufacturer']} | 신고번호 {r['report_number']}" for r in candidates}
            selected=st.selectbox('확인한 제품',list(labels),format_func=labels.get,index=None,
                                  placeholder='제품을 직접 선택해 주세요',key='selected_product',
                                  on_change=lambda:st.session_state.pop('result',None))
            if selected:
                p=product_by_id(selected)
                product_meta(p)
                if p['source']=='I0030':
                    st.warning('신고 목록에서만 찾은 후보입니다. 공식 기능성 원문을 확보한 제품이 아닙니다.')
            if st.button('선택한 제품으로 비교',disabled=not selected,type='primary'):
                st.session_state['result']=analyze_claim(st.session_state['searched_text'],selected)
                st.rerun()

if st.session_state.get('result'):
    with st.container(key='result_card'):
        r=st.session_state['result']
        section(3,'두 문장을 함께 살펴보세요','광고의 표현과 공식 원문을 비교하고, 출처에서 한 번 더 확인하세요.')
        banner({'matched':'관련 공식 문구를 찾았습니다','needs_review':'확인할 표현이 있습니다',
               'no_official_data':'공식 기능성 자료가 없습니다','no_product':'제품을 찾지 못했습니다'}[r['status']],r['difference_note'],r['status']!='matched')
        left,right=st.columns(2)
        with left, st.container(key='ad_card'):
            st.subheader('입력한 광고 문구')
            st.text(r['ad_text'])
            st.subheader('확인할 표현')
            if r['review_tags']:
                if not r['official_claims']:
                    st.caption('공식 원문과 대조하지 않고 광고 문구만 본 점검입니다.')
                for evidence in r.get('review_evidence',[]):
                    evidence_tag(evidence['tag'],' / '.join(evidence['expressions']) or '유사한 표현을 감지했습니다. 문구 전체를 확인하세요.')
            elif not r['official_claims']:
                st.write('규칙으로 찾은 표현 없음. 공식 원문이 없어 원문과의 비교는 하지 못했습니다.')
            else:
                st.write('규칙으로 찾은 표현 없음 (문제없다는 의미는 아닙니다)')
        with right, st.container(key='official_card'):
            st.subheader('공식 기능성 표시 · 원문')
            for row in r['official_claim_rows']:
                if row['ingredient']:
                    st.caption(row['ingredient'])
                st.text(row['official_claim'])
                if row['source_url']:
                    st.link_button('이 원문의 출처 열기',row['source_url'])
                else:
                    st.write('이 원문의 출처 URL: 기록 없음')
                st.caption('원문 확인일: '+(row['checked_at'] or '기록 없음'))
            if not r['official_claims']:
                st.write('현재 자료에 공식 원문 없음')
        st.subheader('출처와 확인일')
        if r['source_url']:
            st.link_button('식품안전나라 제품 상세 보기',r['source_url'])
        else:
            st.write('제품 상세 출처 URL: 기록 없음')
            st.link_button('식품안전나라에서 직접 검색', 'https://www.foodsafetykorea.go.kr/portal/healthyfoodlife/searchHomeHF.do?menu_grp=MENU_NEW04&menu_no=2805')
        st.write('확인일: '+(r['checked_at'] or '기록 없음'))
        st.caption('확인일은 팀의 저장된 출처 기록 기준이며 실시간 조회일이 아닙니다.')
        with st.expander('팀 작성 쉬운 설명 · 검수 전 초안 (공식 원문 아님)'):
            for row in r['official_claim_rows']:
                if row['easy_explanation']:
                    st.text(row['easy_explanation'])
            if not r['official_claim_rows']:
                st.write('작성된 설명 없음')

st.markdown('<div class="footer">이 도우미는 표현의 차이와 자료 범위를 안내합니다. 제품 진위·위법 여부·치료 효과를 판정하거나 복용·구매를 추천하지 않습니다.<br>공식 문구 24개 제품 · 125행 / 신고 목록은 후보 검색에만 사용 / 카카오톡·영상 링크 분석은 지원하지 않습니다.</div>',unsafe_allow_html=True)
