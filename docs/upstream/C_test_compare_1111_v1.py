"""시험 문구 20개를 analyze_claim으로 돌려 expected_status와 비교하고 C_test_results_1111_v1.csv로 저장."""
import sys
from pathlib import Path

import pandas as pd

from C_compare_1111_v1 import analyze_claim

HERE = Path(__file__).resolve().parent
CASES = HERE.parent.parent / "D_synthetic_cases_1111_v3.xlsx"  # D가 올릴 v3 시험 파일 (제품 번호 P001~P024)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    cases = pd.read_excel(CASES, dtype=str)
    rows = []
    for c in cases.itertuples():
        r = analyze_claim(c.ad_text)
        rows.append({
            "case_id": c.case_id, "group": c.group, "ad_text": c.ad_text,
            "expected_status": c.expected_status, "actual_status": r["status"],
            "결과": "맞음" if r["status"] == c.expected_status else "틀림",
            "expected_product_id": c.expected_product_id if isinstance(c.expected_product_id, str) else "",
            "actual_product_id": r["product_id"] or "",
            "product_name": r["product_name"], "review_tags": ", ".join(r["review_tags"]),
            "message": r["message"],
        })
    out = pd.DataFrame(rows)
    out.to_csv(HERE / "C_test_results_1111_v1.csv", index=False, encoding="utf-8-sig")
    print(out[["case_id", "expected_status", "actual_status", "결과", "expected_product_id",
               "actual_product_id", "product_name"]].to_string(index=False))
    print(f"\n시험 {len(out)}개 중 {(out['결과'] == '맞음').sum()}개 통과")


if __name__ == "__main__":
    main()
