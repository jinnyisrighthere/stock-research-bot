import os
import json
import requests

CACHE_DIR = os.path.join("output", "cache")


def _sec_headers() -> dict:
    ua = os.getenv("SEC_USER_AGENT", "StockResearchBot research@example.com").strip()
    return {"User-Agent": ua, "Accept-Encoding": "gzip, deflate"}


def _get_cik(ticker: str) -> str:
    os.makedirs(CACHE_DIR, exist_ok=True)
    cache_file = os.path.join(CACHE_DIR, "sec_tickers.json")
    mapping = {}

    if os.path.exists(cache_file):
        with open(cache_file, "r", encoding="utf-8") as f:
            mapping = json.load(f)

    t_upper = ticker.upper()
    if t_upper not in mapping:
        url = "https://www.sec.gov/files/company_tickers.json"
        resp = requests.get(url, headers=_sec_headers(), timeout=20)
        resp.raise_for_status()
        data = resp.json()
        for _, entry in data.items():
            sym = entry.get("ticker", "").upper()
            cik_str = str(entry.get("cik_str", "")).zfill(10)
            if sym:
                mapping[sym] = cik_str
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(mapping, f)

    if t_upper not in mapping:
        raise ValueError(f"SEC EDGAR에서 티커({ticker})의 CIK 번호를 찾을 수 없습니다.")
    return mapping[t_upper]


def fetch_us_sec_data(ticker: str) -> dict:
    try:
        cik = _get_cik(ticker)
        sub_url = f"https://data.sec.gov/submissions/CIK{cik}.json"
        sub_resp = requests.get(sub_url, headers=_sec_headers(), timeout=20)
        sub_resp.raise_for_status()
        sub_data = sub_resp.json()

        recent = sub_data.get("filings", {}).get("recent", {})
        filings = []
        forms = recent.get("form", [])
        dates = recent.get("filingDate", [])
        acc_nums = recent.get("accessionNumber", [])
        primary_docs = recent.get("primaryDocument", [])

        for i in range(min(len(forms), 60)):
            if forms[i] in ("10-K", "10-Q", "8-K", "DEF 14A"):
                acc_clean = acc_nums[i].replace("-", "")
                cik_int = str(int(cik))
                doc_url = f"https://www.sec.gov/Archives/edgar/data/{cik_int}/{acc_clean}/{primary_docs[i]}"
                filings.append({
                    "form": forms[i],
                    "filing_date": dates[i],
                    "url": doc_url
                })
            if len(filings) >= 15:
                break

        return {
            "status": "OK",
            "cik": cik,
            "entity_name": sub_data.get("name"),
            "sic_description": sub_data.get("sicDescription"),
            "fiscal_year_end": sub_data.get("fiscalYearEnd"),
            "recent_filings": filings,
        }
    except Exception as e:
        return {"status": "ERROR", "reason": str(e)}
