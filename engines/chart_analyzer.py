import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def analyze_and_plot_chart(market_data: dict, chart_path: str) -> dict:
    df = pd.DataFrame(market_data["price_history"])
    df["Date_dt"] = pd.to_datetime(df["Date"])
    df = df.sort_values("Date_dt").reset_index(drop=True)

    df["SMA20"] = df["Close"].rolling(20).mean()
    df["SMA50"] = df["Close"].rolling(50).mean()
    df["SMA200"] = df["Close"].rolling(200).mean()

    # RSI 14
    delta = df["Close"].diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta.clip(upper=0)).rolling(14).mean()
    rs = gain / loss.replace(0, np.nan)
    df["RSI14"] = 100 - (100 / (1 + rs))

    latest = df.iloc[-1]
    close = float(latest["Close"])
    sma20 = float(latest["SMA20"]) if pd.notna(latest["SMA20"]) else None
    sma50 = float(latest["SMA50"]) if pd.notna(latest["SMA50"]) else None
    sma200 = float(latest["SMA200"]) if pd.notna(latest["SMA200"]) else None
    rsi14 = round(float(latest["RSI14"]), 1) if pd.notna(latest["RSI14"]) else None

    recent_252 = df.tail(252)
    high_52w = float(recent_252["High"].max())
    low_52w = float(recent_252["Low"].min())
    pos_52w = round(((close - low_52w) / (high_52w - low_52w)) * 100, 1) if high_52w > low_52w else 50.0

    # Volume Profile (12 price bins over last 252 trading days)
    bins = np.linspace(low_52w, high_52w, 13)
    bin_vols = []
    for i in range(12):
        mask = (recent_252["Close"] >= bins[i]) & (recent_252["Close"] <= bins[i + 1])
        vol_sum = float(recent_252.loc[mask, "Volume"].sum())
        mid_p = round((bins[i] + bins[i + 1]) / 2.0, 2)
        bin_vols.append({"price_range": f"{round(bins[i], 2)} ~ {round(bins[i+1], 2)}", "mid_price": mid_p, "volume": vol_sum})

    top_nodes = sorted(bin_vols, key=lambda x: x["volume"], reverse=True)[:3]
    supports = [n["mid_price"] for n in top_nodes if n["mid_price"] <= close]
    resistances = [n["mid_price"] for n in top_nodes if n["mid_price"] > close]

    # Plot 1-year chart
    plot_df = recent_252.copy()
    os.makedirs(os.path.dirname(chart_path), exist_ok=True)
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 5.5), gridspec_kw={"height_ratios": [3, 1]}, sharex=True)

    ax1.plot(plot_df["Date_dt"], plot_df["Close"], label="Close", color="#111827", linewidth=1.6)
    ax1.plot(plot_df["Date_dt"], plot_df["SMA20"], label="20D MA", color="#2563EB", linewidth=1.0, alpha=0.85)
    ax1.plot(plot_df["Date_dt"], plot_df["SMA50"], label="50D MA", color="#D97706", linewidth=1.1, alpha=0.85)
    ax1.plot(plot_df["Date_dt"], plot_df["SMA200"], label="200D MA", color="#DC2626", linewidth=1.3, alpha=0.9)

    for node in top_nodes:
        ax1.axhline(node["mid_price"], color="#6B7280", linestyle="--", linewidth=0.8, alpha=0.6)

    ticker_label = market_data["summary"]["raw_ticker"]
    ax1.set_title(f"{ticker_label} - 1Y Price, Moving Averages & Volume Profile Zones", fontsize=11, fontweight="bold")
    ax1.legend(loc="upper left", fontsize=8)
    ax1.grid(True, alpha=0.25)

    ax2.bar(plot_df["Date_dt"], plot_df["Volume"], color="#9CA3AF", width=1.2)
    ax2.set_ylabel("Volume", fontsize=8)
    ax2.grid(True, alpha=0.25)

    plt.tight_layout()
    plt.savefig(chart_path, dpi=150)
    plt.close(fig)

    avg_vol_20d = float(df["Volume"].tail(20).mean())
    latest_vol = float(latest["Volume"])

    return {
        "latest_close": round(close, 2),
        "sma_20": round(sma20, 2) if sma20 else None,
        "sma_50": round(sma50, 2) if sma50 else None,
        "sma_200": round(sma200, 2) if sma200 else None,
        "disparity_200d_pct": round(((close / sma200) - 1) * 100, 2) if sma200 else None,
        "rsi_14": rsi14,
        "high_52w": round(high_52w, 2),
        "low_52w": round(low_52w, 2),
        "position_in_52w_range_pct": pos_52w,
        "volume_ratio_vs_20d_avg": round(latest_vol / avg_vol_20d, 2) if avg_vol_20d > 0 else None,
        "high_volume_nodes": top_nodes,
        "key_support_levels": sorted(supports, reverse=True) or [round(low_52w, 2)],
        "key_resistance_levels": sorted(resistances) or [round(high_52w, 2)],
        "chart_image_path": chart_path,
    }
