import csv,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.ocr import read_text
from src.products import search_candidates
from src.compare import analyze_claim
cases={c['case_id']:c for c in csv.DictReader((ROOT/'data/processed/synthetic_cases.csv').open(encoding='utf-8-sig'))}
rows=[]
for path in sorted((ROOT/'data/synthetic/sample_ads').glob('*.png')):
    t=time.monotonic();ocr=read_text(path.read_bytes());c=cases[path.stem[:3]]
    cs=search_candidates(ocr['text'])
    pid=c['expected_product_id'] if any(p['id']==c['expected_product_id'] for p in cs) else (cs[0]['id'] if cs else None)
    r=analyze_claim(ocr['text'],pid)
    rows.append(dict(case_id=c['case_id'],image=path.name,ocr_text=ocr['text'],ocr_status=ocr['status'],error=ocr['error'],seconds=round(time.monotonic()-t,2),
                     actual_status=r['status'],expected_status=c['expected_status'],status_pass=r['status']==c['expected_status'],
                     actual_product_id=r['product_id'] or '',expected_product_id=c['expected_product_id'],
                     product_pass=(r['product_id'] or '')==c['expected_product_id'],actual_tags=' | '.join(r['review_tags']),
                     tag_pass=c['expected_tag'] in r['review_tags'] if c['expected_tag'] else not r['review_tags'],
                     source_url=r['source_url'],checked_at=r['checked_at']))
    print(path.name,r['status'],flush=True)
with (ROOT/'docs/ocr_test_results.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
