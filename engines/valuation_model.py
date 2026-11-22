def run_valuation_models(market_data: dict, fin_metrics: dict) -> dict:
    summary = market_data["summary"]
    annual = fin_metrics.get("annual_5y", [])

    price = summary.get("current_price") or 0
    shares = summary.get("shares_outstanding") or 0
    market_cap = summary.get("market_cap") or (price * shares)
    beta = summary.get("beta") or 1.15
    market = summary.get("market", "US")

    # Estimate WACC via CAPM
    rf = 0.032 if market == "KR" else 0.042
    erp = 0.055 if market == "KR" else 0.048
    cost_of_equity = rf + beta * erp
    wacc = round(max(0.07, min(0.14, cost_of_equity * 0.90 + 0.045 * 0.10)), 4)
    terminal_growth = 0.025 if market == "KR" else 0.030

    # Latest valid FCF & Net Debt
    latest_fcf = None
    net_debt = 0.0
    hist_growths = []
    for row in annual:
        if row.get("fcf") is not None:
            latest_fcf = row["fcf"]
        if row.get("net_debt") is not None:
            net_debt = row["net_debt"]
        if row.get("revenue_growth_pct") is not None:
            hist_growths.append(row["revenue_growth_pct"] / 100.0)

    if not latest_fcf or latest_fcf <= 0:
        # Fallback to 8% of latest revenue if FCF is temporarily negative
        latest_rev = next((r["revenue"] for r in reversed(annual) if r.get("revenue")), 0)
        latest_fcf = latest_rev * 0.08 if latest_rev else 0

    avg_hist_g = sum(hist_growths[-3:]) / len(hist_growths[-3:]) if hist_growths else 0.10
    base_growth_5y = round(max(0.03, min(0.30, avg_hist_g * 0.85)), 4)

    def dcf_equity_value(fcf_0: float, g_5y: float, discount_rate: float, g_term: float) -> float:
        if fcf_0 <= 0 or discount_rate <= g_term:
            return 0.0
        pv_stage1 = 0.0
        fcf_t = fcf_0
        for t in range(1, 6):
            # Linear fade toward terminal growth in years 4-5
            g_t = g_5y if t <= 3 else g_5y - (g_5y - g_term) * ((t - 3) / 3.0)
            fcf_t = fcf_t * (1 + g_t)
            pv_stage1 += fcf_t / ((1 + discount_rate) ** t)
        tv = (fcf_t * (1 + g_term)) / (discount_rate - g_term)
        pv_tv = tv / ((1 + discount_rate) ** 5)
        ev = pv_stage1 + pv_tv
        return max(0.0, ev - net_debt)

    base_eq_val = dcf_equity_value(latest_fcf, base_growth_5y, wacc, terminal_growth)
    intrinsic_price = round(base_eq_val / shares, 2) if (shares and base_eq_val > 0) else None

    # Reverse DCF: Binary search for 5-year FCF CAGR implied by current market cap
    implied_growth = None
    if market_cap > 0 and latest_fcf > 0:
        low, high = -0.30, 1.00
        for _ in range(60):
            mid = (low + high) / 2.0
            val = dcf_equity_value(latest_fcf, mid, wacc, terminal_growth)
            if val < market_cap:
                low = mid
            else:
                high = mid
        implied_growth = round(((low + high) / 2.0) * 100, 2)

    # Scenario Anchors (12-Month)
    scenarios = {}
    if price > 0:
        base_target = intrinsic_price if intrinsic_price else round(price * 1.08, 2)
        bull_target = round(max(base_target * 1.25, price * 1.28), 2)
        bear_target = round(min(base_target * 0.75, price * 0.78), 2)
        scenarios = {
            "bull": {
                "probability_pct": 25,
                "target_price": bull_target,
                "upside_pct": round(((bull_target / price) - 1) * 100, 1),
            },
            "base": {
                "probability_pct": 50,
                "target_price": base_target,
                "upside_pct": round(((base_target / price) - 1) * 100, 1),
            },
            "bear": {
                "probability_pct": 25,
                "target_price": bear_target,
                "upside_pct": round(((bear_target / price) - 1) * 100, 1),
            },
        }

    return {
        "multiples": {
            "trailing_pe": summary.get("trailing_pe"),
            "forward_pe": summary.get("forward_pe"),
            "ev_to_ebitda": summary.get("ev_to_ebitda"),
            "ev_to_revenue": summary.get("ev_to_revenue"),
            "price_to_sales": summary.get("price_to_sales"),
            "price_to_book": summary.get("price_to_book"),
            "analyst_consensus_target": summary.get("target_mean_price"),
        },
        "dcf_assumptions": {
            "base_fcf_used": latest_fcf,
            "net_debt_used": net_debt,
            "wacc_pct": round(wacc * 100, 2),
            "terminal_growth_pct": round(terminal_growth * 100, 2),
            "assumed_5y_fcf_cagr_pct": round(base_growth_5y * 100, 2),
        },
        "dcf_intrinsic_price": intrinsic_price,
        "reverse_dcf_implied_5y_fcf_cagr_pct": implied_growth,
        "scenarios_12m": scenarios,
    }
