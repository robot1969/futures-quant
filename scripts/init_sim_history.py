import sys
import os
# Add project root to path
sys.path.append(os.path.expanduser('~/futures_quant'))

from market.feeder import MarketDataFeeder

def main():
    print("🚀 Starting Full Market History Initialization...")
    # Initialize feeder with specified directory
    feeder = MarketDataFeeder(base_dir="data/simulated_history/")
    
    # Trigger full generation (365 days of 1m data -> resampled to all)
    # This will populate data/simulated_history/
    feeder._generate_full_market_library(days=365)
    
    print("\n✅ Initialization Complete!")
    print("📂 Data stored in: data/simulated_history/")
    print("📊 Timeframes generated: 1m, 15m, 1h, 4h, 1d, 1w, 1M")

if __name__ == "__main__":
    main()
