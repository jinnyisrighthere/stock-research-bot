def _pick(d: dict, keys: list):
    for k in keys:
        if k in d and d[k] is not None:
            return d[k]
    return None


def compute_financial_metrics(market_data: dict, filing_data: dict) -> dict:
    yf_stmt = market_data.get("yf_statements", {})
    ann_inc = yf_stmt.get("annual_income", {})
    ann_bal = yf_stmt.get("annual_balance", {})
    ann_cf = yf_stmt.get("annual_cashflow", {})

    q_inc = yf_stmt.get("quarterly_income", {})
    q_bal = yf_stmt.get("quarterly_balance", {})
    q_cf = yf_stmt.get("quarterly_cashflow", {})

    annual_series = _build_period_series(ann_inc, ann_bal, ann_cf, is_quarterly=False)
    quarterly_series = _build_period_series(q_inc, q_bal, q_cf, is_quarterly=True)

    return {
        "annual_5y": annual_series,
        "quarterly_recent": quarterly_series,
        "dart_raw_annual": filing_data.get("annual_financials", {}) if market_data["summary"]["market"] == "KR" else {},
        "dart_raw_quarterly": filing_data.get("quarterly_financials", {}) if market_data["summary"]["market"] == "KR" else {},
    }


def _build_period_series(inc_map: dict, bal_map: dict, cf_map: dict, is_quarterly: bool) -> list:
    periods = sorted(list(inc_map.keys()))
    rows = []
    prev_rev = None
    prev_shares = None
    prev_assets = None

    for p in periods:
        inc = inc_map.get(p, {})
        bal = bal_map.get(p, {})
        cf = cf_map.get(p, {})

        rev = _pick(inc, ["Total Revenue", "Operating Revenue", "Revenue"])
        cogs = _pick(inc, ["Cost Of Revenue", "Reconciled Cost Of Revenue"])
        gp = _pick(inc, ["Gross Profit"])
        op_inc = _pick(inc, ["Operating Income", "Total Operating Income As Reported"])
        net_inc = _pick(inc, ["Net Income", "Net Income Common Stockholders"])
        ebitda = _pick(inc, ["EBITDA", "Normalized EBITDA"])
        eps = _pick(inc, ["Diluted EPS", "Basic EPS"])
        interest_exp = _pick(inc, ["Interest Expense", "Interest Expense Non Operating"])
        shares = _pick(inc, ["Diluted Average Shares", "Basic Average Shares"])

        ocf = _pick(cf, ["Operating Cash Flow", "Cash Flow From Continuing Operating Activities"])
        capex_raw = _pick(cf, ["Capital Expenditure", "Purchase Of PPE"])
        capex = abs(capex_raw) if capex_raw is not None else None
        fcf = (ocf - capex) if (ocf is not None and capex is not None) else _pick(cf, ["Free Cash Flow"])
        sbc = _pick(cf, ["Stock Based Compensation"])
        buybacks = _pick(cf, ["Repurchase Of Capital Stock", "Common Stock Payments"])
        dividends = _pick(cf, ["Cash Dividends Paid", "Common Stock Dividend Paid"])

        cash = _pick(bal, ["Cash Cash Equivalents And Short Term Investments", "Cash And Cash Equivalents"])
        total_debt = _pick(bal, ["Total Debt", "Long Term Debt And Capital Lease Obligation"])
        net_debt = (total_debt - cash) if (total_debt is not None and cash is not None) else None
        inventory = _pick(bal, ["Inventory"])
        ar = _pick(bal, ["Accounts Receivable", "Receivables"])
        ap = _pick(bal, ["Accounts Payable", "Payables"])
        total_assets = _pick(bal, ["Total Assets"])
        total_equity = _pick(bal, ["Stockholders Equity", "Total Equity Gross Minority Interest"])

        days = 90.0 if is_quarterly else 365.0
        dio = round((inventory / cogs) * days, 1) if (inventory and cogs and cogs > 0) else None
        dso = round((ar / rev) * days, 1) if (ar and rev and rev > 0) else None
        dpo = round((ap / cogs) * days, 1) if (ap and cogs and cogs > 0) else None
        ccc = round(dio + dso - dpo, 1) if (dio is not None and dso is not None and dpo is not None) else None

        rev_growth = round(((rev - prev_rev) / abs(prev_rev)) * 100, 2) if (rev is not None and prev_rev not in (None, 0)) else None
        share_dilution = round(((shares - prev_shares) / prev_shares) * 100, 2) if (shares and prev_shares) else None

        gpm = round((gp / rev) * 100, 2) if (gp is not None and rev) else None
        opm = round((op_inc / rev) * 100, 2) if (op_inc is not None and rev) else None
        npm = round((net_inc / rev) * 100, 2) if (net_inc is not None and rev) else None
        fcf_margin = round((fcf / rev) * 100, 2) if (fcf is not None and rev) else None

        # ROIC approximation (annualized if quarterly)
        roic = None
        if op_inc is not None and total_equity is not None and total_debt is not None:
            invested_cap = total_equity + total_debt - (cash or 0)
            if invested_cap > 0:
                nopat = op_inc * (1 - 0.21) * (4 if is_quarterly else 1)
                roic = round((nopat / invested_cap) * 100, 2)

        # Accruals Ratio = (Net Income - OCF) / Avg Total Assets
        accruals_ratio = None
        if net_inc is not None and ocf is not None and total_assets:
            avg_assets = ((total_assets + prev_assets) / 2) if prev_assets else total_assets
            if avg_assets > 0:
                accruals_ratio = round(((net_inc - ocf) / avg_assets) * 100, 2)

        rows.append({
            "period": p,
            "revenue": rev,
            "revenue_growth_pct": rev_growth,
            "gross_profit": gp,
            "gpm_pct": gpm,
            "operating_income": op_inc,
            "opm_pct": opm,
            "net_income": net_inc,
            "npm_pct": npm,
            "diluted_eps": eps,
            "ebitda": ebitda,
            "ocf": ocf,
            "capex": capex,
            "fcf": fcf,
            "fcf_margin_pct": fcf_margin,
            "cash_and_sti": cash,
            "total_debt": total_debt,
            "net_debt": net_debt,
            "interest_expense": interest_exp,
            "inventory": inventory,
            "accounts_receivable": ar,
            "accounts_payable": ap,
            "dio_days": dio,
            "dso_days": dso,
            "dpo_days": dpo,
            "ccc_days": ccc,
            "sbc": sbc,
            "sbc_pct_of_rev": round((sbc / rev) * 100, 2) if (sbc is not None and rev) else None,
            "shares_outstanding": shares,
            "share_change_pct": share_dilution,
            "buybacks": abs(buybacks) if buybacks is not None else None,
            "dividends": abs(dividends) if dividends is not None else None,
            "roic_pct": roic,
            "accruals_ratio_pct": accruals_ratio,
        })

        prev_rev = rev
        prev_shares = shares
        prev_assets = total_assets

    return rows
