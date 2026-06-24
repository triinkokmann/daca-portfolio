# ROLL B: Data Processing (Andmete töötlemine)
# - Duplikaatide eemaldamine
# - Kuupäevade formaadi parandus
# - Nädalate kaupa kalkulatsioonid
# - Tagasta andmed
# - Liida müügi ja kliendi andmed

import logging
import pandas as pd

# 1. Import data_fetcher funktsioonid 
from week8_pipeline.data_fetcher import fetch_sales, fetch_customers, fetch_products

# 2. Setup et näeks laadimisprotsessi 
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


# --- PIPELINE FUNKTSIOONID ---

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Eemalda duplikaadid ja vorminda kuupäevad õigesse formaati (yyyy-mm-dd).
    """
    df_clean = df.drop_duplicates().copy()
    if 'sale_date' in df_clean.columns:
        df_clean['sale_date'] = pd.to_datetime(df_clean['sale_date'], errors='coerce')
    return df_clean


def calculate_weekly_aggregates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Rühmitab andmed 7-päevaste intervallide kaupa ja arvutab kogukäibe,
    unikaalsete tellimuste arvu ning keskmise tellimuse väärtuse.
    """
    if df.empty:
        return df
    
    df_copy = df.copy()
    df_copy['sale_date'] = pd.to_datetime(df_copy['sale_date'], errors='coerce')
    
    # Kaardistame tegeliku 'total_price' veeru arvuliseks tüübiks summeerimise jaoks
    df_copy['total_price'] = pd.to_numeric(df_copy['total_price'], errors='coerce').fillna(0.0)
    
    # Vormindame arve tunnuse tekstiks, et saaksime korrektselt unikaalseid tellimusi loendada
    df_copy['invoice_id'] = df_copy['invoice_id'].astype(str)
    
    # Arvutame näitajad käibe ja tellimuse keskmise väärtuse kohta
    grouped = (
        df_copy
        .set_index('sale_date')
        .resample('7D')
        .agg(
            total_revenue=pd.NamedAgg(column='total_price', aggfunc='sum'),
            total_orders=pd.NamedAgg(column='invoice_id', aggfunc='nunique'),
            avg_order_value=pd.NamedAgg(column='total_price', aggfunc='mean'),
        )
        .reset_index()
    )
    return grouped


def calculate_kpis(df: pd.DataFrame) -> dict[str, float]:
    """
    Arvutab põhikvaliteedinäitajad: kogutulu, unikaalsed kliendid ja keskmise tellimuse väärtuse.
    """
    if df.empty:
        return {'total_revenue': 0.0, 'unique_customers': 0, 'avg_order_value': 0.0}
    
    # Kasutame veergu 'total_price'
    numeric_order_amt = pd.to_numeric(df['total_price'], errors='coerce').fillna(0.0)
    
    total_revenue = numeric_order_amt.sum()
    unique_customers = df['customer_id'].nunique() if 'customer_id' in df.columns else 0
    avg_order_value = numeric_order_amt.mean()
    
    return {
        'total_revenue': float(total_revenue),
        'unique_customers': int(unique_customers),
        'avg_order_value': float(avg_order_value),
    }


def merge_datasets(df_sales: pd.DataFrame, df_customers: pd.DataFrame) -> pd.DataFrame:
    """
    Ühenda müügi- ja kliendiandmed customer_id alusel.
    """
    if df_sales.empty or df_customers.empty:
        return pd.DataFrame()
    
    # Mõlemas tabelis on veerg 'customer_id' olemas!
    merged_df = pd.merge(df_sales, df_customers, on='customer_id', how='left')
    return merged_df


# --- PIPELINE KÄSKUDE BLOCK ---
if __name__ == "__main__":
    print("Alustan andmete importi...")
    
    df_sales_raw = fetch_sales(start_date="2023-01-01", end_date="2024-12-31")
    df_customers_raw = fetch_customers()
    df_products_raw = fetch_products()
    
    print("\n--- Import lõppenud ---")
    print(f"Sales Data:    {df_sales_raw.shape[0]} rows, {df_sales_raw.shape[1]} columns")
    
    print("\nJooksuta pipeline funktsioone...")
    
    # 1. Puhasta andmed
    df_sales_clean = clean_data(df_sales_raw)
    df_customers_clean = clean_data(df_customers_raw)
    
    # 2. Arvuta nädalate koondandmed
    df_weekly = calculate_weekly_aggregates(df_sales_clean)
    
    # 3. Arvuta KPI näitajad
    kpis = calculate_kpis(df_sales_clean)
    
    # 4. Ühenda tabelid
    df_merged = merge_datasets(df_sales_clean, df_customers_clean)
    
    print("\n=== PIPELINE TULEMUSED ===")
    print("\nKPI Näitajad:")
    for kpi, val in kpis.items():
        if kpi == 'unique_customers':
            print(f"  {kpi}: {val}")  
        else:
            print(f"  {kpi}: {val:,.2f}")
        
    print("\nNädala koondandmete algus:")
    # Teeme koopia ja tagame, et tellimuste arv kuvatakse täisarvuna ilma float-tüüpi komata (.0)
    df_weekly_display = df_weekly.copy()
    df_weekly_display['total_orders'] = df_weekly_display['total_orders'].astype(int)
    print(df_weekly_display.head())
    
    print("\nÜhendatud andmestiku kuju:")
    print(f"  {df_merged.shape[0]} rida ja {df_merged.shape[1]} veergu.")