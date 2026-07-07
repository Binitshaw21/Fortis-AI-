"""
Quantitative Data Loader & Tick Data Generator for Fortis AI.
Uses NumPy and Pandas to simulate and ingest high-resolution tick history (5,000+ rows)
with normal market regimes and anomalous flash-crash events.
"""
import os
import time
import numpy as np
import pandas as pd
from pathlib import Path

# Base data storage directory
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)
TICK_FILE_PATH = DATA_DIR / "market_ticks_5000.csv"


def generate_synthetic_tick_data(num_rows=5000, asset="CSPR/USD", base_price=0.035, regime="normal"):
    """
    Generates a realistic tick-by-tick dataset of at least `num_rows` rows using
    Geometric Brownian Motion (GBM) with jump-diffusion for flash crashes.
    """
    np.random.seed(42 if regime == "normal" else 99)
    
    # Time delta between ticks (~1 second per tick)
    dt = 1.0 / (24 * 3600)
    mu = 0.05  # Annual drift
    sigma = 0.45 if regime == "normal" else 0.85  # Annualized volatility
    
    # Generate random shocks using NumPy
    shocks = np.random.normal(loc=(mu - 0.5 * sigma**2) * dt, scale=sigma * np.sqrt(dt), size=num_rows)
    
    # Inject Flash Crash Anomaly if requested
    if regime == "flash_crash" or asset == "CSPR-CRASH/USD":
        # At tick index 4500 to 4600, inject a massive liquidity cascade (-18% drop)
        crash_start = int(num_rows * 0.90)
        crash_end = crash_start + 60
        shocks[crash_start:crash_end] = np.random.normal(loc=-0.0035, scale=0.001, size=(crash_end - crash_start))
        # After crash, slight dead-cat bounce and extreme volatility
        shocks[crash_end:crash_end+40] = np.random.normal(loc=0.001, scale=0.005, size=40)

    # Compute cumulative log returns and prices
    log_returns = np.cumsum(shocks)
    prices = base_price * np.exp(log_returns)
    
    # Simulate bid-ask spread and order book liquidity depth
    spreads = prices * np.random.uniform(0.0005, 0.002, size=num_rows)
    bids = prices - (spreads / 2.0)
    asks = prices + (spreads / 2.0)
    
    # Volume inversely correlated with liquidity during crashes
    base_volumes = np.random.lognormal(mean=9.5, sigma=0.8, size=num_rows)
    if regime == "flash_crash" or asset == "CSPR-CRASH/USD":
        base_volumes[int(num_rows * 0.90):int(num_rows * 0.90)+100] *= 8.5  # Huge volume spike during crash
        
    order_book_depth_usd = np.random.uniform(500000, 2500000, size=num_rows)
    if regime == "flash_crash" or asset == "CSPR-CRASH/USD":
        order_book_depth_usd[int(num_rows * 0.90):int(num_rows * 0.90)+100] *= 0.15  # Liquidity evaporates
        
    # Timestamps ending at current time
    end_time = int(time.time())
    timestamps = np.arange(end_time - num_rows, end_time)
    
    df = pd.DataFrame({
        "timestamp": timestamps,
        "ticker": asset,
        "price": np.round(prices, 6),
        "bid": np.round(bids, 6),
        "ask": np.round(asks, 6),
        "volume": np.round(base_volumes, 2),
        "order_book_depth_usd": np.round(order_book_depth_usd, 2),
        "regime": regime
    })
    
    return df


def load_or_generate_tick_data():
    """
    Loads historical tick dataset from CSV if available, otherwise generates a fresh 5,000+ row dataset.
    Returns a multi-asset DataFrame including normal CSPR, ETH, BTC, and a simulated flash-crash asset.
    """
    if TICK_FILE_PATH.exists():
        try:
            df = pd.read_csv(TICK_FILE_PATH)
            if len(df) >= 5000:
                return df
        except Exception:
            pass

    # Generate multi-asset dataset
    df_cspr = generate_synthetic_tick_data(num_rows=5200, asset="CSPR/USD", base_price=0.035, regime="normal")
    df_eth = generate_synthetic_tick_data(num_rows=5200, asset="ETH/USD", base_price=3450.0, regime="normal")
    df_btc = generate_synthetic_tick_data(num_rows=5200, asset="BTC/USD", base_price=64500.0, regime="normal")
    df_crash = generate_synthetic_tick_data(num_rows=5200, asset="CSPR-CRASH/USD", base_price=0.035, regime="flash_crash")
    
    full_df = pd.concat([df_cspr, df_eth, df_btc, df_crash], ignore_index=True)
    full_df.to_csv(TICK_FILE_PATH, index=False)
    return full_df


def get_asset_ticks(ticker="CSPR/USD", limit=5000):
    """
    Retrieves the most recent `limit` ticks for a specified asset ticker.
    """
    df = load_or_generate_tick_data()
    asset_df = df[df["ticker"].str.upper() == ticker.upper()].copy()
    if asset_df.empty:
        # Fallback to default CSPR/USD if ticker unknown
        asset_df = df[df["ticker"] == "CSPR/USD"].copy()
        
    return asset_df.sort_values("timestamp").tail(limit).reset_index(drop=True)
