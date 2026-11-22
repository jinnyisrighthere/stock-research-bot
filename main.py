import os
import sys
import json
from dotenv import load_dotenv

from collectors.market_router import fetch_market_data
from collectors.kr_dart import fetch_kr_dart_data
from collectors.us_sec import fetch_us_sec_data
from engines.financial_metrics import compute_financial_metrics
from engines.valuation_model import run_valuation_models
from engines.chart_analyzer import analyze_and_plot_chart
from builders.report_builder import build_reports


def prepare(ticker: str):
    load_dotenv()
    os.makedirs("output", exist_ok=True)
    t_clean = ticker.strip().upper()

    print(f"[1/4] 시세 및 기본 재무 데이터 수집 중: {t_clean} ...")
    market_data = fetch_market_data(t_clean)
    market = market_data["summary"]["market"]
    raw_ticker = market_data["summary"]["raw_ticker"]

    print(f"[2/4] 공시 원문 데이터 수집 중 ({'OpenDART' if market == 'KR' else 'SEC EDGAR'}) ...")
    if market == "KR":
        filing_data = fetch_kr_dart_data(raw_ticker)
    else:
        filing_data = fetch_us_sec_data(raw_ticker)

    print("[3/4] 5년/8분기 재무비율 및 Reverse DCF 내재 성장률 계산 중 ...")
    fin_metrics = compute_financial_metrics(market_data, filing_data)
    valuation = run_valuation_models(market_data, fin_metrics)

    print("[4/4] 이동평균선·매물대 분석 및 주가 차트 생성 중 ...")
    chart_path = os.path.join("output", f"{raw_ticker}_chart.png")
    chart_analysis = analyze_and_plot_chart(market_data, chart_path)

    fact_sheet = {
        "summary": market_data["summary"],
        "filings": filing_data,
        "financial_metrics": fin_metrics,
        "valuation": valuation,
        "technical_chart": chart_analysis,
    }

    fact_path = os.path.join("output", f"{raw_ticker}_fact_sheet.json")
    with open(fact_path, "w", encoding="utf-8") as f:
        json.dump(fact_sheet, f, ensure_ascii=False, indent=2)

    print(f"\n[완료] 정량 팩트시트 저장됨: {fact_path}")
    print(f"[완료] 차트 이미지 저장됨: {chart_path}")


def build(ticker: str):
    raw_ticker = ticker.strip().upper().split(".")[0]
    res = build_reports(raw_ticker, output_dir="output")
    print(f"\n[최종 보고서 생성 완료]")
    print(f" - Word (.docx): {res['docx']}")
    print(f" - PDF  (.pdf) : {res['pdf']}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("사용법:")
        print("  python main.py prepare <종목코드_또는_티커>   (예: python main.py prepare NVDA)")
        print("  python main.py build <종목코드_또는_티커>     (예: python main.py build NVDA)")
        sys.exit(1)

    cmd = sys.argv[1].lower()
    target = sys.argv[2]

    if cmd == "prepare":
        prepare(target)
    elif cmd == "build":
        build(target)
    else:
        print(f"알 수 없는 명령어입니다: {cmd} (prepare 또는 build 사용)")
        sys.exit(1)
