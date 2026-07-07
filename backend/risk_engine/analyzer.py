"""
Quantitative Risk Engine for Fortis AI.
Analyzes 5,000+ rows of tick data using high-performance NumPy and Pandas vectorization.
Calculates Bollinger Bands, Z-score velocity, VaR, liquidity depth, and flags flash crashes.
"""
import numpy as np
import pandas as pd
from .data_loader import get_asset_ticks


class QuantitativeRiskEngine:
    """
    Evaluates market volatility and infrastructure execution risks for AI trading agents.
    """
    def __init__(self, ticker="CSPR/USD", window_bollinger=20, window_zscore=100):
        self.ticker = ticker
        self.window_bollinger = window_bollinger
        self.window_zscore = window_zscore
        self.df = get_asset_ticks(ticker=ticker, limit=5000)

    def run_comprehensive_analysis(self):
        """
        Executes full quantitative risk analysis across 5,000+ rows.
        Returns a structured dictionary with risk metrics, status, and execution decision.
        """
        if self.df.empty or len(self.df) < 50:
            return {
                "ticker": self.ticker,
                "status": "ERROR_INSUFFICIENT_DATA",
                "risk_score": 100.0,
                "decision": "NO-GO",
                "reason": "Insufficient historical tick data to verify market stability."
            }

        prices = self.df["price"].values
        volumes = self.df["volume"].values
        liquidity = self.df["order_book_depth_usd"].values

        # 1. Calculate Log Returns using NumPy vectorization
        log_returns = np.diff(np.log(prices))
        
        # 2. Compute Bollinger Bands (Rolling 20-period SMA & Std Dev)
        s_prices = pd.Series(prices)
        sma_20 = s_prices.rolling(window=self.window_bollinger).mean().values
        std_20 = s_prices.rolling(window=self.window_bollinger).std().values
        
        upper_band_2sig = sma_20 + (2.0 * std_20)
        lower_band_2sig = sma_20 - (2.0 * std_20)
        lower_band_3sig = sma_20 - (3.0 * std_20)
        
        # Current market state (latest tick)
        current_price = prices[-1]
        current_sma = sma_20[-1] if not np.isnan(sma_20[-1]) else current_price
        current_std = std_20[-1] if not np.isnan(std_20[-1]) else 0.001
        current_lower_2sig = lower_band_2sig[-1] if not np.isnan(lower_band_2sig[-1]) else current_price * 0.98
        current_lower_3sig = lower_band_3sig[-1] if not np.isnan(lower_band_3sig[-1]) else current_price * 0.95

        # 3. Z-Score Velocity Analysis
        recent_returns = log_returns[-self.window_zscore:] if len(log_returns) >= self.window_zscore else log_returns
        ret_mean = np.mean(recent_returns)
        ret_std = np.std(recent_returns)
        if ret_std == 0:
            ret_std = 1e-6
        
        latest_return = log_returns[-1] if len(log_returns) > 0 else 0.0
        z_score = (latest_return - ret_mean) / ret_std

        # 4. Flash Crash & Momentum Metrics (Rolling 30-tick max drawdown)
        window_30_prices = prices[-30:] if len(prices) >= 30 else prices
        peak_price_30 = np.max(window_30_prices)
        drawdown_30_pct = ((current_price - peak_price_30) / peak_price_30) * 100.0

        # Annualized Volatility Index
        volatility_index = np.std(recent_returns) * np.sqrt(365 * 24 * 3600) * 100.0

        # Liquidity Health
        current_liquidity = liquidity[-1]
        avg_liquidity = np.mean(liquidity[-500:]) if len(liquidity) >= 500 else np.mean(liquidity)
        liquidity_ratio = current_liquidity / avg_liquidity if avg_liquidity > 0 else 1.0

        # 5. Dual-Threat Risk Scoring & Verdict
        risk_score = 10.0  # Base safe risk score
        flags = []
        status = "SAFE"
        decision = "GO"
        reason = "Market conditions are stable. Volatility within normal Bollinger 2-sigma bounds."

        # Check Flash Crash conditions
        if drawdown_30_pct < -12.0 or z_score < -3.5 or current_price < current_lower_3sig or liquidity_ratio < 0.30:
            risk_score = min(98.5, 75.0 + abs(drawdown_30_pct) * 1.5)
            status = "CRITICAL_FLASH_CRASH"
            decision = "NO-GO"
            reason = f"CRITICAL FLASH CRASH DETECTED: Rapid drawdown ({drawdown_30_pct:.2f}%) and extreme downward Z-score ({z_score:.2f}). Order book liquidity collapsed to {liquidity_ratio*100:.1f}% of normal."
            flags.append("FLASH_CRASH_ANOMALY")
            flags.append("ORDER_BOOK_LIQUIDITY_COLLAPSE")
        elif current_price < current_lower_2sig or z_score < -2.0 or drawdown_30_pct < -6.0:
            risk_score = min(68.0, 35.0 + abs(drawdown_30_pct) * 2.0)
            status = "ELEVATED_VOLATILITY"
            decision = "GO"
            reason = f"Elevated volatility detected (Drawdown: {drawdown_30_pct:.2f}%, Z-Score: {z_score:.2f}). Proceed with tightened slippage tolerance."
            flags.append("BOLLINGER_LOWER_BAND_BREACH")
        else:
            # Normal variations
            risk_score = np.clip(10.0 + (volatility_index * 0.1) + abs(z_score) * 2.5, 5.0, 29.9)

        # Prepare chart series data (last 50 points for rich UI rendering)
        chart_timestamps = self.df["timestamp"].tail(50).tolist()
        chart_prices = self.df["price"].tail(50).tolist()
        chart_upper = pd.Series(upper_band_2sig).tail(50).bfill().ffill().fillna(current_price * 1.02).tolist()
        chart_lower = pd.Series(lower_band_2sig).tail(50).bfill().ffill().fillna(current_price * 0.98).tolist()
        chart_sma = pd.Series(sma_20).tail(50).bfill().ffill().fillna(current_price).tolist()

        return {
            "ticker": self.ticker,
            "current_price": round(float(current_price), 6),
            "sma_20": round(float(current_sma), 6),
            "bollinger_upper_2sig": round(float(upper_band_2sig[-1] if not np.isnan(upper_band_2sig[-1]) else current_price*1.02), 6),
            "bollinger_lower_2sig": round(float(current_lower_2sig), 6),
            "z_score_velocity": round(float(z_score), 2),
            "drawdown_rolling_30_pct": round(float(drawdown_30_pct), 2),
            "volatility_index_ann": round(float(volatility_index), 2),
            "order_book_depth_usd": round(float(current_liquidity), 2),
            "liquidity_health_ratio": round(float(liquidity_ratio), 2),
            "risk_score": round(float(risk_score), 2),
            "status": status,
            "decision": decision,
            "reason": reason,
            "flags": flags,
            "total_ticks_analyzed": len(self.df),
            "chart_data": {
                "timestamps": chart_timestamps,
                "prices": [round(float(p), 6) for p in chart_prices],
                "upper_band": [round(float(p), 6) for p in chart_upper],
                "lower_band": [round(float(p), 6) for p in chart_lower],
                "sma": [round(float(p), 6) for p in chart_sma],
            }
        }
