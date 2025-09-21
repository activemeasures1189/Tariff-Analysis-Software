


# Module Imports for GUI and data visualization

import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


#  Functions 


# def load_consumption_data(file_path):
#     df = pd.read_csv(file_path, parse_dates=['timestamp'])
#     return df

def load_consumption_data(file_path):
    # Load CSV/ Excel file
    df = pd.read_csv(file_path)

    
    for col in df.columns:
        if col.strip().lower() == "timestamp":
            df.rename(columns={col: "timestamp"}, inplace=True)
            break

    # Convert to datetime
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

    # Drop rows where timestamp couldn’t be parsed
    if df["timestamp"].isna().any():
        print("Warning: Some rows had invalid timestamps and were dropped.")
        df = df.dropna(subset=["timestamp"])

    return df


def calculate_flat_rate_from_data(df, rate_per_kwh, fixed_fee=0):
    total_kwh = df['kWh'].sum()
    return (total_kwh * rate_per_kwh) + fixed_fee

def classify_period(hour):
    if 18 <= hour < 22:     # Peak period
        return "Peak"
    elif 22 <= hour or hour < 7:  # Off-Peak period
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


# GUI + Visualize charts


consumption_df = None

def load_file():
    global consumption_df
    file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    if file_path:
        try:
            consumption_df = load_consumption_data(file_path)
            messagebox.showinfo("File Loaded", f"Data loaded from {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file: {e}")

def calculate_bill():
    global consumption_df
    if consumption_df is None:
        messagebox.showerror("Error", "Please load a consumption CSV file first.")
        return
    try:
        flat_rate = float(entry_flat_rate.get())
        fixed_fee = float(entry_fixed_fee.get())

        # Example tariffs
        tou_rates = {"Peak": 0.40, "Shoulder": 0.25, "Off-Peak": 0.15}
        tiered_tiers = [(100, 0.20), (300, 0.30), (float('inf'), 0.40)]

        results = compare_tariffs_from_data(consumption_df, flat_rate, tou_rates, tiered_tiers, fixed_fee)
        
        # Show results 
        msg = "\n".join([f"{k}: ${v:.2f}" for k, v in results.items()])
        messagebox.showinfo("Bill Comparison", msg)

        # Visualize Charts
        plot_charts(consumption_df, results)

    except ValueError:
        messagebox.showerror("Input Error", "Please enter valid numbers.")

def plot_charts(df, results):
    # Create figure
    fig, axes = plt.subplots(2, 1, figsize=(6, 6))

    # Line Chart: usage trend
    df_sorted = df.sort_values('timestamp')
    axes[0].plot(df_sorted['timestamp'], df_sorted['kWh'], color="blue")
    axes[0].set_title("Electricity Usage Trend")
    axes[0].set_xlabel("Time")
    axes[0].set_ylabel("kWh")

    # Bar Chart: tariff comparison
    axes[1].bar(results.keys(), results.values(), color=["orange", "green", "purple"])
    axes[1].set_title("Bill Comparison")
    axes[1].set_ylabel("Cost ($)")

    plt.tight_layout()

    # Embed figure in Tkinter
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.draw()
    canvas.get_tk_widget().grid(row=5, columnspan=2, pady=10)

# Build Tkinter UI
root = tk.Tk()
root.title("XPower Household Tariff Analysis")

tk.Button(root, text="Load Consumption File", command=load_file).grid(row=0, columnspan=2, pady=5)

tk.Label(root, text="Flat Rate ($/kWh):").grid(row=1, column=0)
entry_flat_rate = tk.Entry(root)
entry_flat_rate.insert(0, "0.25")
entry_flat_rate.grid(row=1, column=1)

tk.Label(root, text="Fixed Fee ($):").grid(row=2, column=0)
entry_fixed_fee = tk.Entry(root)
entry_fixed_fee.insert(0, "10")
entry_fixed_fee.grid(row=2, column=1)

tk.Button(root, text="Calculate Bills", command=calculate_bill).grid(row=3, columnspan=2, pady=10)

root.mainloop()
