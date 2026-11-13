"""제품 검색: 광고 문구에서 제품명을 찾아 product_id를 돌려준다. (데이터 파일은 읽기만 함)"""
import re
from difflib import SequenceMatcher
from functools import lru_cache
from pathlib import Path

import pandas as pd

# ── 바꿔 쓰는 값 ──────────────────────────────────────────
DATA_DIR = Path(__file__).resolve().parent.parent.parent  # 엑셀·I0030 파일이 있는 폴더
NAME_SIM_REVIEWED = 0.7  # 검수한 24개: 제품명이 광고에 이 비율 이상 들어 있으면 같은 제품
NAME_SIM_ALL = 0.9       # I0030 전체(4만 6천 건): 더 엄격하게
MIN_NAME_LEN = 4         # 검수 24개: 이보다 짧은 제품명은 검색 안 함
MIN_NAME_LEN_ALL = 6     # I0030 전체: "면역 젤리"처럼 흔한 짧은 이름 방지
BIGRAM_SHARE = 0.4       # 빠른 1차 거르기: 두 글자 조각이 이 비율 이상 겹쳐야 정밀 비교
SPAN_SLACK = 1          # 제품명 글자가 광고 안에서 흩어진 정도 허용치
# ─────────────────────────────────────────────────────────


def norm(text):
    """한글·영문·숫자만 남기고 소문자로. (공백·괄호·특수문자 제거)"""
    return re.sub(r"[^0-9a-z가-힣]", "", str(text).lower())


def _bigrams(s):
    return {s[i:i + 2] for i in range(len(s) - 1)}


def _row(pid, name, source, claims, url, checked):
    n = norm(name)
    return {"id": pid, "name": name, "norm": n, "bi": _bigrams(n), "source": source,
            "claims": claims, "source_url": url, "checked_at": checked}


@lru_cache(maxsize=None)
def load_products():
    """(검수 24개, 그 외 I0030 제품) 두 리스트를 돌려준다. 처음 한 번만 읽는다."""
    prods = pd.read_excel(DATA_DIR / "official_products_v2.xlsx", dtype=str)
    claims = pd.read_excel(DATA_DIR / "official_claims_v2.xlsx", dtype=str)  # ingredient 빈칸은 NaN 그대로 둠
    reviewed = []
    for p in prods.itertuples():
        texts = claims.loc[claims.product_id == p.product_id, "official_claim"].dropna().tolist()
        reviewed.append(_row(p.product_id, p.product_name, "official_v2", texts,
                             p.source_url, p.checked_at))
    done = set(prods.report_number.astype(str))
    big = pd.read_csv(DATA_DIR / "I0030.csv.gz", dtype=str,
                      usecols=["PRDLST_REPORT_NO", "PRDLST_NM"])
    # 팀장 결정: I0030은 "신고 목록에 있는 제품인지"만 확인. 기능성 문구는 비교에 쓰지 않음(claims 비움).
    others = [_row(r.PRDLST_REPORT_NO, r.PRDLST_NM, "I0030", [], "", "")
              for r in big.itertuples() if r.PRDLST_REPORT_NO not in done]
    return reviewed, others


def locate(ad, name_norm):
    """광고(정리된 글자) 안에서 제품명이 얼마나 들어 있는지. (비율, 제품명을 뺀 나머지) 또는 None"""
    sm = SequenceMatcher(None, ad, name_norm, autojunk=False)
    blocks = [b for b in sm.get_matching_blocks() if b.size]
    if not blocks:
        return None
    start, end = blocks[0].a, blocks[-1].a + blocks[-1].size
    if end - start > len(name_norm) + SPAN_SLACK:  # 글자가 광고 곳곳에 흩어져 있으면 제외
        return None
    return sum(b.size for b in blocks) / len(name_norm), ad[:start] + ad[end:]


def _best(ad, rows, min_sim, min_len):
    ad_bi, best = _bigrams(ad), None
    for r in rows:
        if len(r["norm"]) < min_len or len(r["bi"] & ad_bi) < BIGRAM_SHARE * len(r["bi"]):
            continue
        hit = locate(ad, r["norm"])
        if hit and hit[0] >= min_sim and (best is None or (hit[0], len(r["norm"])) > best[0]):
            best = ((hit[0], len(r["norm"])), r, hit[1])
    return best


def find_product(ad_text):
    """제품을 찾으면 (제품 dict, 제품명을 뺀 나머지 글자), 못 찾으면 None. 검수 24개를 먼저 본다."""
    reviewed, others = load_products()
    ad = norm(ad_text)
    # ponytail: 같은 이름 제품이 여럿이면 첫 번째를 고름. 제조사 비교는 필요해지면 추가.
    best = _best(ad, reviewed, NAME_SIM_REVIEWED, MIN_NAME_LEN) or _best(ad, others, NAME_SIM_ALL, MIN_NAME_LEN_ALL)
    return (best[1], best[2]) if best else None


def product_by_id(product_id):
    reviewed, others = load_products()
    return next((r for r in reviewed + others if r["id"] == product_id), None)


def find_product_id(ad_text):
    """광고 문구에서 product_id를 찾는다. 못 찾으면 None."""
    hit = find_product(ad_text)
    return hit[0]["id"] if hit else None
