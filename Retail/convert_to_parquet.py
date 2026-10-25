"""Run once next to retail_clean.csv:  python convert_to_parquet.py"""
import pandas as pd

df = pd.read_csv("retail_clean.csv", parse_dates=["InvoiceDate"])
df["Invoice"] = df["Invoice"].astype(str)
df["StockCode"] = df["StockCode"].astype(str)
df["Quantity"] = pd.to_numeric(df["Quantity"], errors="coerce").astype("int32")
df["LineTotal"] = pd.to_numeric(df["LineTotal"], errors="coerce").astype("float32")
df.to_parquet("retail_clean.parquet", index=False, compression="zstd")
print("Saved retail_clean.parquet:", len(df), "rows")
