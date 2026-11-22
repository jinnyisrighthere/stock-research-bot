import os
import io
import json
import zipfile
import xml.etree.ElementTree as ET
from datetime import datetime
import requests

CACHE_DIR = os.path.join("output", "cache")


def _get_corp_code(stock_code: str, api_key: str) -> str:
    os.makedirs(CACHE_DIR, exist_ok=True)
    cache_file = os.path.join(CACHE_DIR, "dart_corp_codes.json")

    mapping = {}
    if os.path.exists(cache_file):
        with open(cache_file, "r", encoding="utf-8") as f:
            mapping = json.load(f)

    if stock_code not in mapping:
        url = f"https://opendart.fss.or.kr/api/corpCode.xml?crtfc_key={api_key}"
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
            xml_bytes = zf.read("CORPCODE.xml")
        root = ET.fromstring(xml_bytes)
        for item in root.findall("list"):
            sc = (item.findtext("stock_code") or "").strip()
            cc = (item.findtext("corp_code") or "").strip()
            if sc and cc:
                mapping[sc] = cc
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(mapping, f, ensure_ascii=False)

    if stock_code not in mapping:
        raise ValueError(f"OpenDART에서 종목코드({stock_code})에 해당하는 고유번호를 찾을 수 없습니다.")
    return mapping[stock_code]


def fetch_kr_dart_data(stock_code: str) -> dict:
    api_key = os.getenv("DART_API_KEY", "").strip()
    if not api_key or "여기에" in api_key:
        return {
            "status": "SKIPPED",
            "reason": "DART_API_KEY가 .env에 설정되지 않아 yfinance 보조 데이터만 사용합니다."
        }

    try:
        corp_code = _get_corp_code(stock_code, api_key)
        company_info = _dart_get("company.json", {"crtfc_key": api_key, "corp_code": corp_code})
        major_holders = _dart_get("hyslrSttus.json", {
            "crtfc_key": api_key, "corp_code": corp_code,
            "bsns_year": str(datetime.now().year - 1), "reprt_code": "11011"
        })

        current_year = datetime.now().year
        annual_reports = {}
        for yr in range(current_year - 5, current_year):
            res = _dart_get("fnlttSinglAcntAll.json", {
                "crtfc_key": api_key,
                "corp_code": corp_code,
                "bsns_year": str(yr),
                "reprt_code": "11011",
                "fs_div": "CFS"
            })
            if res.get("status") == "000" and res.get("list"):
                annual_reports[str(yr)] = _simplify_dart_accounts(res["list"])

        # Recent quarterly/semi-annual reports for last 2 years
        quarterly_reports = {}
        reprt_codes = [("11013", "Q1"), ("11012", "Q2"), ("11014", "Q3"), ("11011", "Q4_ANNUAL")]
        for yr in [current_year - 2, current_year - 1, current_year]:
            for r_code, label in reprt_codes:
                res = _dart_get("fnlttSinglAcntAll.json", {
                    "crtfc_key": api_key,
                    "corp_code": corp_code,
                    "bsns_year": str(yr),
                    "reprt_code": r_code,
                    "fs_div": "CFS"
                })
                if res.get("status") == "000" and res.get("list"):
                    quarterly_reports[f"{yr}_{label}"] = _simplify_dart_accounts(res["list"])

        # Recent disclosures list
        disclosures = _dart_get("list.json", {
            "crtfc_key": api_key,
            "corp_code": corp_code,
            "bgn_de": f"{current_year - 1}0101",
            "page_count": "20"
        })

        return {
            "status": "OK",
            "corp_code": corp_code,
            "company_info": company_info,
            "major_shareholders": major_holders.get("list", [])[:10],
            "annual_financials": annual_reports,
            "quarterly_financials": quarterly_reports,
            "recent_disclosures": disclosures.get("list", [])[:15],
        }
    except Exception as e:
        return {"status": "ERROR", "reason": str(e)}


def _dart_get(endpoint: str, params: dict) -> dict:
    url = f"https://opendart.fss.or.kr/api/{endpoint}"
    r = requests.get(url, params=params, timeout=20)
    r.raise_for_status()
    return r.json()


def _simplify_dart_accounts(items: list) -> dict:
    extracted = {}
    for row in items:
        acct_nm = (row.get("account_nm") or "").strip()
        sj_div = (row.get("sj_div") or "").strip()
        val_str = (row.get("thstrm_amount") or "").replace(",", "").strip()
        try:
            val = float(val_str)
            extracted[f"{sj_div}:{acct_nm}"] = val
        except ValueError:
            continue
    return extracted
