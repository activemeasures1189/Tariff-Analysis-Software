# -------------------------------
# 1. Imports
# -------------------------------
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import datetime

# -------------------------------
# 2. Core Functions (Business Logic)
# -------------------------------

def load_consumption_data(file_path):
    df = pd.read_csv(file_path, parse_dates=['timestamp'])
    return df

def calculate_flat_rate_from_data(df, rate_per_kwh, fixed_fee=0):
    total_kwh = df['kWh'].sum()
    return (total_kwh * rate_per_kwh) + fixed_fee

def classify_period(hour):
    if 18 <= hour < 22:     # Peak
        return "Peak"
    elif 22 <= hour or hour < 7:  # Off-Peak
        return "Off-Peak"
    else:
        return "Shoulder"

def calculate_tou_from_data(df, rates, fixed_fee=0):
    df['period'] = df['timestamp'].dt.hour.apply(classify_period)
    total_cost = 0
    for period, group in df.groupby('period'):
        if period in rates:
            total_cost += group['kWh'].sum() * rates[period]
    return total_cost + fixed_fee

def calculate_tiered_from_data(df, tiers, fixed_fee=0):
    total_kwh = df['kWh'].sum()
    total_cost = 0
    remaining = total_kwh
    last_threshold = 0
    for threshold, rate in tiers:
        if remaining <= 0:
            break
        block = min(remaining, threshold - last_threshold)
        total_cost += block * rate
        remaining -= block
        last_threshold = threshold
    return total_cost + fixed_fee

def compare_tariffs_from_data(df, flat_rate, tou_rates, tiered_tiers, fixed_fee=0):
    return {
        "Flat Rate": calculate_flat_rate_from_data(df, flat_rate, fixed_fee),
        "Time-of-Use": calculate_tou_from_data(df, tou_rates, fixed_fee),
        "Tiered": calculate_tiered_from_data(df, tiered_tiers, fixed_fee)
    }