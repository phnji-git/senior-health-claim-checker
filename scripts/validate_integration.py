"""D v3: explicit selection simulated separately from top-1 retrieval measurement."""
import csv, json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.products import search_candidates
from src.compare import analyze_claim

def validate():
    rows=[]
    for c in csv.DictReader((ROOT/'data/processed/synthetic_cases.csv').open(encoding='utf-8-sig')):
        candidates=search_candidates(c['ad_text'])
        expected=c['expected_product_id']
        # Simulate the user's known fixture choice; top1 is reported independently.
        selected=expected if expected and any(p['id']==expected for p in candidates) else (candidates[0]['id'] if candidates else None)
        r=analyze_claim(c['ad_text'],selected)
        tags=r['review_tags']
        source_ok=(bool(r['source_url']) and bool(r['checked_at']) and r['product_id']==expected
                   and all(x['source_url'] and x['checked_at'] for x in r['official_claim_rows'])) if expected else (not r['source_url'] and not r['checked_at'])
        row=dict(c,actual_status=r['status'],actual_product_id=r['product_id'] or '',
                 actual_tag=' | '.join(tags),actual_source_url=r['source_url'],actual_checked_at=r['checked_at'],
                 top1_id=candidates[0]['id'] if candidates else '',
                 status_pass=r['status']==c['expected_status'],
                 product_pass=r['product_id']==expected if expected else '',
                 candidate_pass=any(p['id']==expected for p in candidates) if expected else '',
                 tag_pass=c['expected_tag'] in tags if c['expected_tag'] else not tags,
                 source_pass=bool(source_ok),
                 notes='태그는 기대 태그 포함 여부; 추가 태그는 actual_tag에서 확인. 출처 없음은 결측 상태가 기대와 일치함을 뜻하며 출처 확보 성공이 아님.')
        row['pass']=all(row[k] for k in ['status_pass','tag_pass','source_pass']) and row['product_pass'] is not False
        rows.append(row)
    with (ROOT/'docs/test_results.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
    summary={k:sum(r[k] is True for r in rows) for k in ['status_pass','product_pass','candidate_pass','tag_pass','source_pass','pass']}
    summary['top1_pass']=sum(r['expected_product_id']==r['top1_id'] for r in rows if r['expected_product_id'])
    summary['product_denominator']=sum(bool(r['expected_product_id']) for r in rows)
    summary['cases']=len(rows)
    (ROOT/'docs/test_summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    print(json.dumps(summary))
    for r in rows:
        if not r['pass']: print(r['case_id'],r['actual_status'],r['actual_product_id'],r['actual_tag'])
    return rows
if __name__=='__main__':validate()
