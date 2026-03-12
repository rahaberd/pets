import pandas as pd
import numpy as np

def calculate_returns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates daily simple returns, log returns, and rolling volatility.
    Uses pure vectorized operations for C-level execution speed.
    """
    # Create a copy to prevent SettingWithCopy warnings
    df = df.copy()
    
    # 1. Daily Simple Returns (Percentage change from yesterday)
    df['Daily_Return'] = df['Adj Close'].pct_change()
    
    # 2. Log Returns (Preferred by quants for statistical time-series modeling)
    df['Log_Return'] = np.log(df['Adj Close'] / df['Adj Close'].shift(1))
    
    # 3. Annualized Rolling Volatility (21 trading days = ~1 month)
    # Volatility mathematically scales with the square root of time.
    df['Rolling_Vol_21d'] = df['Daily_Return'].rolling(window=21).std() * np.sqrt(252)
    
    # Drop the first 21 rows which now have NaNs due to the rolling window calculation
    df.dropna(inplace=True)
    
    return df

def calculate_sharpe(df: pd.DataFrame, risk_free_rate: float = 0.0) -> float:
    """
    Calculates the annualized Sharpe Ratio of the asset or strategy.
    Formula: (Expected Return - Risk Free Rate) / Standard Deviation of Return
    """
    annualized_return = df['Daily_Return'].mean() * 252
    annualized_vol = df['Daily_Return'].std() * np.sqrt(252)
    
    if annualized_vol == 0:
        return 0.0
        
    sharpe_ratio = (annualized_return - risk_free_rate) / annualized_vol
    return sharpe_ratio

# --- TESTING BLOCK ---
if __name__ == "__main__":
    # We import the data handler strictly for local testing
    from data_handler import fetch_data
    
    print("[*] Testing Analytics Module...")
    try:
        # 1. Fetch the raw data using our previously built module
        raw_data = fetch_data("SPY", "2020-01-01", "2024-01-01")
        
        # 2. Pass it through our math engine
        analyzed_data = calculate_returns(raw_data)
        
        print("\n[*] First 5 rows of Analyzed Data:")
        print(analyzed_data[['Adj Close', 'Daily_Return', 'Log_Return', 'Rolling_Vol_21d']].head())
        
        # 3. Calculate the ultimate Quant metric
        sharpe = calculate_sharpe(analyzed_data)
        print(f"\n[*] S&P 500 (SPY) Buy & Hold Sharpe Ratio (2020-2024): {sharpe:.2f}")
        
    except Exception as e:
        print(f"Analytics Error: {e}")