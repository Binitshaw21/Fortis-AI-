#!/usr/bin/env python
"""
Standalone generator script for Fortis AI quantitative tick dataset.
Generates 5,000+ rows of tick data for CSPR, ETH, BTC, and synthetic flash crash scenarios.
"""
import sys
import os
from pathlib import Path

# Add project backend to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

try:
    from risk_engine.data_loader import load_or_generate_tick_data
except ImportError:
    print("Error: Could not import risk_engine. Ensure NumPy and Pandas are installed.")
    sys.exit(1)

if __name__ == "__main__":
    print("Initializing Fortis AI Quantitative Risk Dataset...")
    df = load_or_generate_tick_data()
    print(f"Successfully generated/loaded {len(df)} rows of tick data!")
    print("\nAsset breakdown:")
    print(df["ticker"].value_counts())
    print(f"\nSaved location: {Path(__file__).resolve().parent.parent / 'data' / 'market_ticks_5000.csv'}")
