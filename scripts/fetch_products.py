"""식품안전나라 Open API(I0030)에서 후보 제품을 받아 우리 CSV 형식으로 저장한다.

사용 (프로젝트 폴더에서):
  .\\.venv\\Scripts\\python.exe scripts\\fetch_products.py --selftest
  .\\.venv\\Scripts\\python.exe scripts\\fetch_products.py --sample            # 키 없이 5건 시험
  .\\.venv\\Scripts\\python.exe scripts\\fetch_products.py --name 홍삼 --n 30   # .env의 키 사용

결과는 data/processed/api_candidates_*.csv 로만 저장한다 (official_*.csv는 건드리지 않음).
source_url은 응답에 상세 페이지 주소가 없어 비워 둔다 -> A가 상세 페이지 주소를 채우고 원문과 대조한다.
"""
import argparse, csv, gzip, json, os, re, sys, urllib.parse, urllib.request
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "processed")
PRODUCT_COLS = ["product_id", "product_name", "manufacturer", "report_number", "product_type", "source_url", "checked_at"]
CLAIM_COLS = ["product_id", "ingredient", "official_claim", "easy_explanation", "source_url", "checked_at"]
REGISTRY_COLS = ["product_name", "manufacturer", "report_number", "product_type", "is_raw"]
MARK = re.compile(r"[①-⑳⑴-⒇]")


def load_key():
    if os.environ.get("FOODSAFETY_API_KEY"):
        return os.environ["FOODSAFETY_API_KEY"].strip()
    path = os.path.join(ROOT, ".env")
    if os.path.exists(path):
        for line in open(path, encoding="utf-8-sig"):
            k, _, v = line.strip().partition("=")
            if k.strip() == "FOODSAFETY_API_KEY":
                return v.strip().strip('"\'')
    sys.exit(".env 에 FOODSAFETY_API_KEY=키 한 줄이 없습니다.")


def split_claims(text):
    """①②③ / ⑴⑵ 번호로 나눈다. 번호가 없으면 통째로 1개. 앞의 [비타민C] 같은 머리말은 각 항목에 붙인다."""
    text = (text or "").strip()
    parts = MARK.split(text)
    if len(parts) == 1:
        return [text] if text else []
    prefix = parts[0].strip()
    out = []
    for p in parts[1:]:
        p = " ".join(p.split())
        if p:
            out.append((prefix + " " + p).strip())
    return out


def is_raw_material(row):
    # ponytail: 섭취방법에 '원료'가 들어가면 원료용으로 본다. 다른 경우는 A가 눈으로 확인.
    return "원료" in (row.get("NTK_MTHD") or "")


def fetch(key, name, n):
    url = f"https://openapi.foodsafetykorea.go.kr/api/{key}/I0030/json/1/{n}"
    if name:
        url += "/PRDLST_NM=" + urllib.parse.quote(name)
    data = json.loads(urllib.request.urlopen(url, timeout=30).read().decode("utf-8"))["I0030"]
    res = data.get("RESULT", {})
    if res.get("CODE") not in (None, "INFO-000"):
        sys.exit(f"API 응답: {res.get('CODE')} {res.get('MSG')}")  # 키는 출력하지 않는다
    return data.get("row", [])


DEFAULT_TYPES = ["홍삼", "프로바이오틱스", "비타민 C", "EPA 및 DHA 함유 유지", "칼슘", "루테인", "밀크씨슬(카르두스 마리아누스) 추출물"]


def pick_from_file(path, types, per_type):
    """받아 둔 I0030.csv(.gz)에서 품목(PRDLST_CDNM)별로 최근 신고순 N개. 원료용·수출용·기능성 빈 것·업체명 빈 것 제외."""
    csv.field_size_limit(10**8)
    op = gzip.open if path.endswith(".gz") else open
    with op(path, "rt", encoding="utf-8-sig", newline="") as f:
        rows = [r for r in csv.DictReader(f)
                if not is_raw_material(r) and "수출" not in (r.get("PRDLST_NM") or "") + (r.get("NTK_MTHD") or "") and (r.get("PRIMARY_FNCLTY") or "").strip() and (r.get("BSSH_NM") or "").strip()]
    out = []
    for t in types:
        got = sorted((r for r in rows if r["PRDLST_CDNM"] == t), key=lambda r: r.get("PRMS_DT") or "", reverse=True)[:per_type]
        print(f"  {t}: {len(got)}개")
        out += got
    return out


def make_registry(path):
    """전체 파일에서 '신고 목록에 있는가' 확인용 작은 CSV를 만든다 (문구 없음, 검수 불필요). is_raw=1은 원료용 의심."""
    csv.field_size_limit(10**8)
    op = gzip.open if path.endswith(".gz") else open
    with op(path, "rt", encoding="utf-8-sig", newline="") as f:
        rows = [[r["PRDLST_NM"], r["BSSH_NM"], r["PRDLST_REPORT_NO"], r["PRDLST_CDNM"], int(is_raw_material(r))] for r in csv.DictReader(f)]
    os.makedirs(OUT, exist_ok=True)
    write(os.path.join(OUT, "registry_index.csv"), REGISTRY_COLS, rows)
    return len(rows)


def convert(rows, id_start, keep_raw):
    today = date.today().isoformat()
    products, claims, skipped, seen = [], [], 0, set()
    for r in rows:
        no = r.get("PRDLST_REPORT_NO")
        if no in seen:
            continue
        seen.add(no)
        if is_raw_material(r) and not keep_raw:
            skipped += 1
            continue
        pid = f"P{id_start + len(products):03d}"
        products.append([pid, r["PRDLST_NM"], r["BSSH_NM"], no, r["PRDLST_CDNM"], "", today])
        for c in split_claims(r.get("PRIMARY_FNCLTY")):
            claims.append([pid, r["PRDLST_CDNM"], c, "", "", today])
    return products, claims, skipped


def write(path, cols, rows):
    with open(path, "w", newline="", encoding="utf-8-sig") as f:  # 엑셀에서 한글이 안 깨지는 UTF-8
        w = csv.writer(f)
        w.writerow(cols)
        w.writerows(rows)


def selftest():
    assert split_claims("①면역력 증진②피로개선") == ["면역력 증진", "피로개선"]
    assert split_claims("⑴ 면역력\n  ⑵ 피로") == ["면역력", "피로"]
    assert split_claims("[비타민C] ①결합 ②철") == ["[비타민C] 결합", "[비타민C] 철"]
    assert split_claims("유산균 증식에 도움") == ["유산균 증식에 도움"]
    assert is_raw_material({"NTK_MTHD": "건강기능식품 원료로 사용"})
    assert not is_raw_material({"NTK_MTHD": "1일 1회 1포"})
    import tempfile
    d = tempfile.mkdtemp(); fp = os.path.join(d, "t.csv")
    lines = ["PRDLST_NM,BSSH_NM,PRDLST_REPORT_NO,PRDLST_CDNM,NTK_MTHD,PRIMARY_FNCLTY,PRMS_DT",
             "a,업체,1,홍삼,1일 1회,면역,20200101", "b,업체,2,홍삼,1일 1회,면역,20240101",
             "c,업체,3,홍삼,원료로 사용,면역,20250101", "d,업체,4,홍삼,1일 1회,,20250101"]
    open(fp, "w", encoding="utf-8").write(chr(10).join(lines))
    assert [r["PRDLST_NM"] for r in pick_from_file(fp, ["홍삼"], 5)] == ["b", "a"]  # 최신순, 원료용·빈 기능성 제외
    print("selftest OK")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", help="제품명에 들어갈 검색어 (예: 홍삼)")
    ap.add_argument("--n", type=int, default=30, help="받을 건수(최대 100)")
    ap.add_argument("--sample", action="store_true", help="키 없이 공개 샘플(5건)로 시험")
    ap.add_argument("--keep-raw", action="store_true", help="원료용도 남김")
    ap.add_argument("--id-start", type=int, default=101, help="product_id 시작 번호 (A의 손입력 P001~과 겹치지 않게 기본 101)")
    ap.add_argument("--from-file", help="받아 둔 I0030.csv.gz 경로. 주면 API 대신 파일에서 품목별로 뽑음")
    ap.add_argument("--types", help="품목명을 쉼표로 (기본: 홍삼,프로바이오틱스,비타민 C,EPA 및 DHA 함유 유지,칼슘,루테인,밀크씨슬...)")
    ap.add_argument("--per-type", type=int, default=5, help="품목당 개수 (기본 5)")
    ap.add_argument("--make-registry", help="I0030.csv.gz 경로. 존재 확인용 registry_index.csv 생성(제품명·업체·신고번호)")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        selftest()
        sys.exit()
    if a.make_registry:
        print("registry_index.csv:", make_registry(a.make_registry), "행 ->", OUT)
        sys.exit()
    if a.from_file:
        rows = pick_from_file(a.from_file, a.types.split(",") if a.types else DEFAULT_TYPES, a.per_type)
    else:
        rows = fetch("sample" if a.sample else load_key(), None if a.sample else a.name, min(a.n, 100))
    products, claims, skipped = convert(rows, a.id_start, a.keep_raw)
    os.makedirs(OUT, exist_ok=True)
    write(os.path.join(OUT, "api_candidates_products.csv"), PRODUCT_COLS, products)
    write(os.path.join(OUT, "api_candidates_claims.csv"), CLAIM_COLS, claims)
    print(f"받은 {len(rows)}건 -> 제품 {len(products)}개, 기능성 {len(claims)}행 (원료용 제외 {skipped}건)")
    print("저장:", OUT)
