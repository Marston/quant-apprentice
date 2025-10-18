import os
import yfinance as yf
from fredapi import Fred
import pandas as pd


def get_stock_fundamentals(ticker_symbol: str) -> dict:
    """
    Fetches key fundamental data for a given stock ticker using yfinance.

    Args:
        ticker_symbol: The stock ticker symbol (e.g., 'AAPL').

    Returns:
        A dictionary containing fundamental data or an error message.
    """
    print(f"--- [Tool Action]: Fetching fundamental data for {ticker_symbol}... ---")
    try:
        stock = yf.Ticker(ticker_symbol)
        info = stock.info

        # Extracting a curated list of important metrics
        fundamentals = {
            "ticker": ticker_symbol,
            "companyName": info.get("longName"),
            "sector": info.get("sector"),
            "industry": info.get("industry"),
            "marketCap": info.get("marketCap"),
            "enterpriseValue": info.get("enterpriseValue"),
            "trailingPE": info.get("trailingPE"),
            "forwardPE": info.get("forwardPE"),
            "trailingEps": info.get("trailingEps"),
            "priceToBook": info.get("priceToBook"),
            "dividendYield": info.get("dividendYield"),
            "payoutRatio": info.get("payoutRatio"),
        }
        print(f"--- [Tool Success]: Successfully fetched fundamentals for {ticker_symbol}. ---")
        return fundamentals
    except Exception as e:
        error_message = f"Could not fetch data for {ticker_symbol}. Ticker might be invalid. Details: {e}"
        print(f"--- [Tool Error]: {error_message} ---")
        return {"error": error_message}


def get_macro_economic_data(api_key: str) -> dict:
    """
    Fetches key US macroeconomic indicators from the FRED API.

    Args:
        api_key: Your FRED API key.

    Returns:
        A dictionary of key macroeconomic indicators or an error message.
    """
    print("--- [Tool Action]: Fetching macroeconomic data from FRED... ---")
    try:
        fred = Fred(api_key=api_key)
        
        series_ids = {
            "GDP_Growth": "GDP",
            "UnemploymentRate": "UNRATE",
            "InflationRate_CPI": "CPIAUCSL",
            "EffectiveFedFundsRate": "FEDFUNDS",
        }

        macro_data = {}
        for name, series_id in series_ids.items():
            data = fred.get_series_latest_release(series_id)
            macro_data[name] = data.iloc[-1]

        print("--- [Tool Success]: Successfully fetched macroeconomic data. ---")
        return macro_data
    except Exception as e:
        error_message = f"Could not fetch FRED data. Check API key or connection. Details: {e}"
        print(f"--- [Tool Error]: {error_message} ---")
        return {"error": error_message}