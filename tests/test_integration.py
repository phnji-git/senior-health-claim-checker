from io import BytesIO
from unittest.mock import patch
from pathlib import Path
import pytest
from PIL import Image
from src.compare import analyze_claim
from src.products import search_candidates,load_products
from src.ocr import read_text
from scripts.validate_integration import validate

@pytest.mark.parametrize('text,tag',[
 ('홍삼정 스틱 면역력 증진 피로개선에 도움을 줄 수 없음','부정 표현'),
 ('홍삼정 스틱 100% 면역력 증진 피로개선에 도움을 줄 수 있음','과장'),
])
def test_semantic_guards(text,tag):
    r=analyze_claim(text,'P001')
    assert r['status']=='needs_review' and tag in r['review_tags']
    assert any(e['tag']==tag and e['expressions'] for e in r['review_evidence'])

def test_selection_required():
    r=analyze_claim('홍삼정 스틱 면역력 증진')
    assert r['selection_required'] and r['product_id'] is None and r['status']!='matched'
    assert r['product_candidates']

def test_registry_scope():
    candidates=search_candidates('홍삼정 앰플 프라임 면역력 증진에 도움')
    r=analyze_claim('홍삼정 앰플 프라임 면역력 증진에 도움',candidates[0]['id'])
    assert r['status']=='no_official_data'
    assert not r['source_url'] and not r['checked_at'] and not r['official_claims']

def test_bad_id():
    assert analyze_claim('홍삼정 스틱','missing')['status']=='no_product'

def test_ocr_empty_broken_and_init_failure():
    assert read_text(b'')['error']=='empty_image'
    assert read_text(b'bad bytes')['error']=='invalid_image'
    b=BytesIO();Image.new('RGB',(100,100),'white').save(b,format='PNG')
    with patch('src.ocr.get_reader',side_effect=RuntimeError('model unavailable')):
        assert read_text(b.getvalue())['error']=='RuntimeError'
    with patch('src.ocr.get_reader') as reader:
        reader.return_value.readtext.return_value=[]
        assert read_text(b.getvalue())['error']=='empty_result'

def test_data_integrity():
    reviewed,_=load_products()
    assert len(reviewed)==24
    assert sum(len(r['claims']) for r in reviewed)==125
    assert all(r['source_url'] and r['checked_at']=='2026-11-11' for r in reviewed)

def test_d_v3():
    rows=validate()
    assert len(rows)==20
    assert all(r['pass'] for r in rows)
