from pathlib import Path
from unittest.mock import patch
from streamlit.testing.v1 import AppTest
ROOT=Path(__file__).resolve().parents[1]
GOOD='홍삼정 스틱 면역력 증진 피로개선에 도움을 줄 수 있음'

def button(at,label):
    return next(b for b in at.button if b.label==label)

def search(at,text):
    at.text_area(key='ad_text').input(text).run()
    button(at,'이 문구로 제품 찾기').click().run()
    assert not at.exception

def choose(at,pid):
    at.selectbox(key='selected_product').select(pid).run()
    button(at,'선택한 제품으로 비교').click().run()
    assert not at.exception

def test_direct_input_and_stale_result():
    at=AppTest.from_file(str(ROOT/'app.py'),default_timeout=30).run()
    search(at,GOOD)
    assert at.selectbox(key='selected_product').value is None
    assert button(at,'선택한 제품으로 비교').disabled
    choose(at,'P001')
    assert at.session_state['result']['status']=='matched'
    search(at,'없는제품ABC123')
    assert any('특정하지 못해' in w.value for w in at.warning)
    assert 'result' not in at.session_state

def test_registry_screen():
    at=AppTest.from_file(str(ROOT/'app.py'),default_timeout=30).run()
    search(at,'홍삼정 앰플 프라임 면역력 증진에 도움')
    choose(at,at.session_state['candidates'][0]['id'])
    assert at.session_state['result']['status']=='no_official_data'
    assert any('기록 없음' in m.value for m in at.markdown)

def test_ocr_failure_then_direct_input():
    at=AppTest.from_file(str(ROOT/'app.py'),default_timeout=30).run()
    at.session_state['sample_bytes']=b'invalid png'
    at.session_state['sample_name']='invalid.png'
    at.run()
    button(at,'사진에서 글자 읽기').click().run()
    assert any('정확히 읽지 못했습니다' in w.value for w in at.warning)
    search(at,GOOD);choose(at,'P001')
    assert at.session_state['result']['status']=='matched'

def test_ocr_model_failure_then_direct_input():
    at=AppTest.from_file(str(ROOT/'app.py'),default_timeout=30).run()
    at.session_state['sample_bytes']=(ROOT/'data/synthetic/sample_ads/S01_close.png').read_bytes()
    at.session_state['sample_name']='S01_close.png'
    at.run()
    with patch('src.ocr.get_reader',side_effect=RuntimeError('test model init failure')):
        button(at,'사진에서 글자 읽기').click().run()
    assert at.session_state['ocr_result']['error']=='RuntimeError'
    search(at,GOOD);choose(at,'P001')
    assert at.session_state['result']['status']=='matched'
