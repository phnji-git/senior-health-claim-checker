"""광고 문구와 공식 표시 문구 비교. 진짜/가짜·불법을 판정하지 않고 비교 결과만 돌려준다."""
import re
from difflib import SequenceMatcher

from C_products_1111_v1 import find_product, locate, norm, product_by_id

# ── 바꿔 쓰는 값 ──────────────────────────────────────────
CLAIM_MATCH_SIM = 0.8   # 광고 기능 문구가 공식 문구에 이 비율 이상 들어 있으면 matched
MIN_BLOCK = 2           # 한 글자씩 우연히 겹치는 것은 세지 않음
WORD_SIM = 0.67         # OCR 오타 허용: 3글자 이상 표현어는 이 정도 비슷하면 같은 것으로 봄
DISEASE_WORDS = ["치료", "예방", "완치", "약대신", "처방"]          # 공식 문구에 없으면 needs_review
DISEASE_PATTERN = re.compile(r"병에(좋|도움|효과)")                 # "~병에 좋다"
TAG_WORDS = {"100": "과장", "무조건": "과장", "완벽": "과장", "확실": "단정 표현",
             "책임": "단정 표현", "혈관청소": "혈관 청소·과장", "후기": "후기·체험담",
             "먹고": "후기·체험담"}                                  # 점검 표시일 뿐 판정이 아님
HEALTH_WORDS = ["면역력", "항산화", "영양제", "건강기능식품", "식약처인증", "기능성"]
NOTICE = re.compile(r"\(?\s*시험용.*$")                             # 맨 끝 "시험용 가상 광고입니다 (실제 광고 아님)"
# ─────────────────────────────────────────────────────────

NO_PRODUCT_NOTE = ("식품안전나라 건강기능식품 신고 자료에서 이 제품을 찾지 못했어요. "
                   "제품명이 다르게 적혔거나 글자 인식이 틀렸을 수도 있어요. "
                   "판매처나 포장의 신고번호로 식품안전나라에서 직접 확인해 보세요.")


def _result(status, ad_text, product=None, claims=(), tags=(), words=(), message=""):
    """반환 dict를 만드는 유일한 곳. 필드 이름을 바꿀 때는 여기만 고친다."""
    return {
        "status": status,
        "ad_text": ad_text,
        "product_id": product["id"] if product else None,
        "product_name": product["name"] if product else "",
        "official_claims": list(claims),
        "review_tags": list(tags),
        "health_claim_words": list(words),
        "message": message,
        "source": product["source"] if product else "",
        "source_url": product["source_url"] if product else "",
        "checked_at": product["checked_at"] if product else "",
    }


def _has_word(ad, word):
    """OCR 오타를 조금 허용해서 표현어가 있는지 본다. (2글자 이하는 정확히 일치해야 함)"""
    if word in ad:
        return True
    n = len(word)
    if n < 3:
        return False
    return any(SequenceMatcher(None, ad[i:i + n], word).ratio() >= WORD_SIM
               for i in range(max(len(ad) - n + 1, 1)))


def _coverage(part, official):
    """광고 문구(part)의 글자 중 공식 문구에 같은 순서로 들어 있는 비율."""
    if not part:
        return 0.0
    sm = SequenceMatcher(None, part, norm(official), autojunk=False)
    return sum(b.size for b in sm.get_matching_blocks() if b.size >= MIN_BLOCK) / len(part)


def analyze_claim(ad_text, product_id=None):
    """광고 문구 -> 비교 결과 dict (status: matched / needs_review / no_product / no_official_data)"""
    clean = NOTICE.sub("", str(ad_text))
    ad = norm(clean)
    words = [w for w in HEALTH_WORDS if w in ad]

    if product_id:  # 제품을 이미 골랐을 때
        product = product_by_id(product_id)
        found = product and locate(ad, product["norm"])
        hit = (product, found[1] if found else ad) if product else None
    else:
        hit = find_product(clean)
    if not hit:
        note = NO_PRODUCT_NOTE if words else "제품을 찾지 못했어요. 제품명을 확인해 주세요."
        return _result("no_product", ad_text, words=words, message=note)

    product, rest = hit
    claims = product["claims"]
    if not claims:
        return _result("no_official_data", ad_text, product, words=words,
                       message="제품은 찾았지만 비교할 공식 기능성 문구가 없어요.")

    official_all = norm(" ".join(claims))
    disease = [w for w in DISEASE_WORDS if w not in official_all and _has_word(ad, w)]
    if DISEASE_PATTERN.search(ad) and "병에" not in official_all:
        disease.append("병에 좋다")
    tags = list(dict.fromkeys(disease + [t for k, t in TAG_WORDS.items() if k in ad]))

    score = max(_coverage(rest, c) for c in claims)
    if disease:
        status = "needs_review"
        msg = "질병을 치료·예방한다는 표현이 있어요. 공식 표시에는 없는 표현이니 아래 공식 문구와 비교해 확인해 보세요."
    elif score >= CLAIM_MATCH_SIM:
        status, msg = "matched", "광고 문구가 식약처 공식 표시와 같거나 거의 같아요."
    else:
        status = "needs_review"
        msg = "공식 표시와 다르거나 더 강한 표현이 있어요. 아래 공식 문구와 비교해 직접 확인해 보세요."
    return _result(status, ad_text, product, claims, tags, words, msg)
