import re
from datetime import datetime
import yfinance as yf
import pandas as pd


def detect_market(ticker: str) -> dict:
    clean = ticker.strip().upper()
    if re.fullmatch(r"\d{6}", clean):
        return {"market": "KR", "raw_ticker": clean, "yf_candidates": [f"{clean}.KS", f"{clean}.KQ"]}
    if clean.endswith(".KS") or clean.endswith(".KQ"):
        return {"market": "KR", "raw_ticker": clean.split(".")[0], "yf_candidates": [clean]}
    return {"market": "US", "raw_ticker": clean, "yf_candidates": [clean]}


def fetch_market_data(ticker: str) -> dict:
    route = detect_market(ticker)
    selected_yf = None
    info = {}
    hist = pd.DataFrame()

    for cand in route["yf_candidates"]:
        try:
            t_obj = yf.Ticker(cand)
            h = t_obj.history(period="2y", interval="1d")
            if not h.empty:
                selected_yf = cand
                hist = h
                info = t_obj.info or {}
                break
        except Exception:
            continue

    if hist.empty:
        raise ValueError(f"주가 데이터를 불러올 수 없습니다: {ticker} (후보: {route['yf_candidates']})")

    hist = hist.reset_index()
    hist["Date"] = pd.to_datetime(hist["Date"]).dt.strftime("%Y-%m-%d")
    records = hist[["Date", "Open", "High", "Low", "Close", "Volume"]].to_dict(orient="records")

    # Extract yfinance financial statements as fallback / supplement
    t_obj = yf.Ticker(selected_yf)
    yf_financials = _extract_yf_statements(t_obj)

    summary = {
        "market": route["market"],
        "raw_ticker": route["raw_ticker"],
        "yf_ticker": selected_yf,
        "as_of_date": datetime.now().strftime("%Y-%m-%d"),
        "company_name": info.get("longName") or info.get("shortName") or route["raw_ticker"],
        "sector": info.get("sector"),
        "industry": info.get("industry"),
        "currency": info.get("currency", "KRW" if route["market"] == "KR" else "USD"),
        "current_price": info.get("currentPrice") or info.get("regularMarketPrice") or float(hist["Close"].iloc[-1]),
        "market_cap": info.get("marketCap"),
        "enterprise_value": info.get("enterpriseValue"),
        "trailing_pe": info.get("trailingPE"),
        "forward_pe": info.get("forwardPE"),
        "price_to_sales": info.get("priceToSalesTrailing12Months"),
        "price_to_book": info.get("priceToBook"),
        "ev_to_ebitda": info.get("enterpriseToEbitda"),
        "ev_to_revenue": info.get("enterpriseToRevenue"),
        "beta": info.get("beta"),
        "fifty_two_week_high": info.get("fiftyTwoWeekHigh"),
        "fifty_two_week_low": info.get("fiftyTwoWeekLow"),
        "shares_outstanding": info.get("sharesOutstanding"),
        "held_percent_institutions": info.get("heldPercentInstitutions"),
        "held_percent_insiders": info.get("heldPercentInsiders"),
        "target_mean_price": info.get("targetMeanPrice"),
        "target_high_price": info.get("targetHighPrice"),
        "target_low_price": info.get("targetLowPrice"),
        "recommendation_key": info.get("recommendationKey"),
        "number_of_analyst_opinions": info.get("numberOfAnalystOpinions"),
        "business_summary": info.get("longBusinessSummary"),
    }

    return {
        "summary": summary,
        "price_history": records,
        "yf_statements": yf_financials,
    }


def _extract_yf_statements(t_obj) -> dict:
    def df_to_clean_dict(df):
        if df is None or df.empty:
            return {}
        out = {}
        for col in df.columns:
            col_key = str(col)[:10]
            out[col_key] = {}
            for idx, val in df[col].items():
                if pd.notna(val):
                    out[col_key][str(idx)] = float(val)
        return out

    try:
        return {
            "annual_income": df_to_clean_dict(t_obj.financials),
            "quarterly_income": df_to_clean_dict(t_obj.quarterly_financials),
            "annual_balance": df_to_clean_dict(t_obj.balance_sheet),
            "quarterly_balance": df_to_clean_dict(t_obj.quarterly_balance_sheet),
            "annual_cashflow": df_to_clean_dict(t_obj.cashflow),
            "quarterly_cashflow": df_to_clean_dict(t_obj.quarterly_cashflow),
        }
    except Exception:
        return {}
