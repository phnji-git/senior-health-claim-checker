"""광고 문구와 공식 표시 문구 비교. 진짜/가짜·불법을 판정하지 않고 비교 결과만 돌려준다."""
import re
from difflib import SequenceMatcher

from src.products import locate, norm, product_by_id, search_candidates

# ── 바꿔 쓰는 값 ──────────────────────────────────────────
CLAIM_MATCH_SIM = 0.8   # 광고 기능 문구가 공식 문구에 이 비율 이상 들어 있으면 matched
MIN_BLOCK = 2           # 한 글자씩 우연히 겹치는 것은 세지 않음
WORD_SIM = 0.67         # OCR 오타 허용: 3글자 이상 표현어는 이 정도 비슷하면 같은 것으로 봄
DISEASE_WORDS = ["치료", "예방", "완치", "치유", "약대신", "처방"]  # 공식 문구에 없으면 needs_review
DISEASE_PATTERN = re.compile(r"병에(좋|도움|효과)")                 # "~병에 좋다"
# 공식 문구에 없는 병·증상 이름. "암"처럼 한 글자는 다른 낱말에 섞이므로 붙여 쓰는 꼴로만 적는다.
DISEASE_NAMES = ["고혈압", "혈압", "당뇨", "치매", "관절염", "골다공증", "백내장", "녹내장", "간염",
                 "항암", "암예방", "암세포", "암환자", "심장병", "뇌졸중", "우울증", "불면증"]
COMPARE = r"(?:타|다른)\s*[^,.!?\n]{0,12}?제품\s*(?:에\s*비해|보다)"     # "타 다이어트 제품에 비해"
NO_CLAIMS_TAG_NOTE = " 아래 '확인할 표현'은 공식 문구와 대조하지 않고 광고 문구만 본 점검입니다."
TAG_WORDS = {"무조건": "과장", "완벽": "과장", "최상": "과장", "확실": "단정 표현",
             "책임": "단정 표현", "보장": "단정 표현", "틀림없": "단정 표현",
             "혈관청소": "혈관 청소·과장", "후기": "후기·체험담",
             "먹고": "후기·체험담"}                                  # 점검 표시일 뿐 판정이 아님
HUNDRED = r"100\s*(?:[%％]|프로|퍼센트)|백\s*퍼센트"                  # "100%", "100프로", "백 퍼센트"
SIDE_EFFECT = re.compile(r"부작용(?:이|은|도|전혀|걱정|하나)*(?:없|제로|zero|0)")  # 정리된 글자 기준
# "없/않"이 들어가도 반대 뜻이 아닌 말. 반대·부정 문장 탐지에서 뺀다. (틀림없 = 단정 표현으로 따로 잡음)
NEG_OK = ["걱정없", "부담없", "상관없", "빠짐없", "아낌없", "끊임없", "남김없", "어김없", "틀림없", "못지않"]
NEG_PATTERN = r"없|않|아니|못|불가|안됨|안되|안돼"
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
        "difference_note": message,
        "product_candidates": [],
        "official_claim_rows": product.get('claim_rows', []) if product else [],
        "selection_required": False,
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


def _strip_benign(text):
    """정리된 글자에서 '부작용 없음'과 반대 뜻이 아닌 '없/않' 낱말을 지운다."""
    text = SIDE_EFFECT.sub("", text)
    for w in NEG_OK:
        text = text.replace(w, "")
    return text


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

    candidates = search_candidates(clean)
    if product_id:  # 제품을 이미 골랐을 때
        product = product_by_id(product_id)
        found = product and locate(ad, product["norm"])
        hit = (product, found[1] if found else ad) if product else None
    else:
        result = _result('needs_review' if candidates else 'no_product', ad_text,
                         message='후보의 제품명·업체명·신고번호를 확인하고 선택해 주세요.' if candidates else NO_PRODUCT_NOTE)
        result.update(product_candidates=candidates, selection_required=bool(candidates))
        return result
    if not hit:
        note = NO_PRODUCT_NOTE if words else "제품을 찾지 못했어요. 제품명을 확인해 주세요."
        return _result("no_product", ad_text, words=words, message=note)

    product, rest = hit
    claims = product["claims"]
    # 공식 문구가 없어도(신고 목록 후보) 표현 점검은 한다. 이때 official_all은 빈 글자라 질병 낱말을 빼 주지 못한다.
    official_all = norm(" ".join(claims))
    disease = [w for w in DISEASE_WORDS if w not in official_all and _has_word(ad, w)]
    if DISEASE_PATTERN.search(ad) and "병에" not in official_all:
        disease.append("병에 좋다")
    names = [w for w in DISEASE_NAMES if w in ad and w not in official_all]
    tags = list(dict.fromkeys(disease + [t for k, t in TAG_WORDS.items() if k in ad]))
    if names:
        tags.append('질병명 언급')
    if re.search(HUNDRED, clean):
        tags.append('과장')
    if SIDE_EFFECT.search(ad):
        tags.append('부작용 없음 주장')
    if re.search(NEG_PATTERN, _strip_benign(rest)):
        tags.append('반대·부정 문장')
    if any(w in ad for w in ['완전','하루만에','확좋아','즉시','반드시']):
        tags.append('과장')
    if '약대신' in ad:
        tags.append('약 대체')
    if re.search(COMPARE, clean):
        tags.append('다른 제품과 비교')
    if disease:
        tags = [t for t in tags if t not in DISEASE_WORDS]
        if any(t != '약대신' for t in disease):
            tags.append('질병 예방·치료')
    tags = list(dict.fromkeys(tags))

    score = max((_coverage(rest, c) for c in claims), default=0.0)
    if not claims:
        status = "no_official_data"
        msg = ("신고 목록에서 찾은 후보입니다. 이 목록은 기능성 원문을 검수한 자료가 아닙니다. 현재 자료에 비교할 공식 문구가 없으며, 상세 출처 URL·확인일도 기록되어 있지 않습니다. 포장의 신고번호로 식품안전나라에서 확인해 주세요. 미검색은 불법 판정이 아닙니다."
               + (NO_CLAIMS_TAG_NOTE if tags else ""))
    elif tags:
        status = "needs_review"
        msg = "부정·단정·치료·체험담 등 확인할 표현이 있습니다. 표시한 표현과 공식 원문을 함께 확인해 주세요. 표현 탐지는 제한된 규칙이며 이 비교만으로 위법 여부나 효과를 판단할 수 없습니다."
    elif score >= CLAIM_MATCH_SIM:
        status, msg = "matched", "선택한 제품의 공식 표시에서 관련 기능성 내용을 찾았습니다. 문자상 관련성에 따른 안내이며 의미가 같다는 판정은 아닙니다. 광고 문구와 공식 표현을 함께 살펴보세요."
    else:
        status = "needs_review"
        msg = "공식 표시와 다르거나 더 강한 표현이 있어요. 아래 공식 문구와 비교해 직접 확인해 보세요."
    result = _result(status, ad_text, product, claims, tags, words, msg)
    result['product_candidates'] = candidates
    evidence=[]
    patterns = {
        '반대·부정 문장':r'[^,.!?\n]{0,16}(?:없\w*|않\w*|아니\w*|못\w*|불가|안됨|안되\w*|안돼\w*)',
        '과장':HUNDRED + r'|무조건|완벽|완전|하루\s*만에|확\s*좋아\w*|즉시|반드시|최상\w*',
        '다른 제품과 비교':COMPARE,
        '단정 표현':r'확실\w*|책임\w*|보장\w*|틀림\s*없\w*',
        '혈관 청소·과장':r'혈관\s*청소',
        '후기·체험담':r'후기|먹고',
        '약 대체':r'약\s*대신',
        '질병 예방·치료':r'치료\w*|예방\w*|완치\w*|치유\w*|처방\w*',
        '질병명 언급':'|'.join(r'\s*'.join(map(re.escape, w)) for w in names) or r'(?!)',
        '부작용 없음 주장':r'부작용[^,.!?\n]{0,8}?(?:없\w*|제로|zero|0)',
    }
    for tag in tags:
        matches=re.findall(patterns.get(tag,r'(?!)'),clean)
        if tag == '반대·부정 문장':  # 부작용 없음·걱정 없는 같은 구절은 근거에서 뺀다
            matches = [m for m in matches if re.search(NEG_PATTERN, _strip_benign(norm(m)))]
        evidence.append({'tag':tag,'expressions':list(dict.fromkeys(m.strip() for m in matches))})
    result['review_evidence']=evidence
    return result
