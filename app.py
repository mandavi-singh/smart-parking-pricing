import streamlit as st
import pandas as pd
import altair as alt
import numpy as np
from models import compute_baseline_price, compute_demand_price, compute_dynamic_price
from utils import haversine_distance

# -------------------------------
# Page Config
# -------------------------------
st.set_page_config(page_title="Smart Parking Pricing", layout="wide", page_icon="🅿️")

# -------------------------------
# Load and preprocess dataset
# -------------------------------
df = pd.read_csv("dataset.csv")
df['Timestamp'] = pd.to_datetime(df['LastUpdatedDate'] + ' ' + df['LastUpdatedTime'], dayfirst=True)
df['TrafficConditionNearby'] = pd.to_numeric(df['TrafficConditionNearby'], errors='coerce')
df['LotID'] = df['SystemCodeNumber']
df = df.dropna(subset=['Occupancy', 'Capacity', 'Latitude', 'Longitude'])

# -------------------------------
# Compute Prices for Earliest Snapshot
# -------------------------------
sample_time = df['Timestamp'].min()
df_sample = df[df['Timestamp'] == sample_time].copy()

df_sample['BaselinePrice'] = df_sample.apply(compute_baseline_price, axis=1)
df_sample['DemandPrice'] = df_sample.apply(compute_demand_price, axis=1)
df_sample['DynamicPrice'] = df_sample.apply(lambda row: compute_dynamic_price(row, df_sample), axis=1)
df_sample['occ_ratio'] = df_sample['Occupancy'] / df_sample['Capacity']

# Merge prices back to full data
df = df.merge(df_sample[['LotID', 'BaselinePrice', 'DemandPrice', 'DynamicPrice']], on='LotID', how='left')

# -------------------------------
# Sidebar Filters
# -------------------------------
st.sidebar.title("🔧 Filters")
all_times = df['Timestamp'].dropna().sort_values().unique()
selected_time = st.sidebar.selectbox("Select Timestamp", all_times)

selected_models = st.sidebar.multiselect(
    "Select Models to Display",
    ['BaselinePrice', 'DemandPrice', 'DynamicPrice'],
    default=['BaselinePrice', 'DemandPrice', 'DynamicPrice']
)

lot_ids = df['LotID'].unique()
selected_lot = st.sidebar.selectbox("Select Lot (Optional)", ["All"] + list(lot_ids))

# Filter based on timestamp and lot
filtered_df = df[df['Timestamp'] == selected_time]
if selected_lot != "All":
    filtered_df = filtered_df[filtered_df['LotID'] == selected_lot]

# -------------------------------
# Dashboard Title
# -------------------------------
st.title("🅿️ Smart Parking Pricing Models")
# -------------------------------
# Model Descriptions
# -------------------------------
with st.expander("📘 Model Descriptions", expanded=False):
    st.markdown("#### 🧮 Model 1: Baseline Linear Model")
    st.markdown("""
A simple model where price increases linearly as occupancy increases.

**Formula:**  Price(t+1) = Price(t) + α × (Occupancy / Capacity)
                """)

    st.markdown("#### 📈 Model 2: Demand-Based Price Function")
    st.markdown("""
Constructs a demand function using key features:

- Occupancy rate  
- Queue length  
- Traffic level  
- Special day  
- Vehicle type  

**Demand Function:**  Demand = α × (Occupancy / Capacity) + β × QueueLength − γ × Traffic + δ × IsSpecialDay + ε × VehicleTypeWeight

**Price Adjustment:** Price(t) = BasePrice × (1 + λ × NormalizedDemand) 

Prices are smoothed and bounded (e.g., not more than 2× or less than 0.5× base).
""")

    st.markdown("#### 🌍 Model 3: Competitive Pricing Model")
    st.markdown("""This model simulates **real-world competition** by using **location intelligence** and **proximity-based pricing**.

- Calculate geographic distance between lots using latitude and longitude  
- Consider competitor prices in a 1 km radius  
- Adjust your own price based on neighborhood trends


**Logic:**

- If your lot is **full** and nearby lots are **cheaper** → suggest rerouting or reduce price  
- If nearby lots are **more expensive** → increase your price (you are still competitive)  
- Encourages creativity and mimics dynamic urban pricing

**Pseudocode:**
```python
nearby_lots = get_lots_within_radius(lat, lon, radius=1.0)
avg_nearby_price = np.mean([lot['price'] for lot in nearby_lots])

if occ_ratio > 0.9 and avg_nearby_price < base_price:
    price = max(base_price - 2, 5)
elif avg_nearby_price > base_price:
    price = min(base_price + 2, 20)
else:
    price = base_price + occ_ratio * 5

""")




st.markdown(f"### 📅 Price Comparison at: `{selected_time}`")
st.markdown("---")

# -------------------------------
# First Chart: Dynamic Price with Occupancy Ratio (Only for earliest timestamp)
# -------------------------------
st.subheader("📈 Dynamic Price per Parking Lot")
chart1 = alt.Chart(df_sample).mark_bar().encode(
    x=alt.X('LotID:N', sort='-y', title='Lot ID'),
    y=alt.Y('DynamicPrice:Q', title='Dynamic Price ($)'),
    color=alt.Color('occ_ratio:Q', scale=alt.Scale(scheme='blues'), title='Occupancy Ratio'),
    tooltip=['LotID', 'DynamicPrice', 'Occupancy', 'Capacity']
).properties(width=1000, height=400)

st.altair_chart(chart1, use_container_width=True)

# -------------------------------
# Second Chart: Selected Models
# -------------------------------
if not filtered_df.empty and selected_models:
    st.subheader("📊 Selected Models Price Comparison")
    chart2 = alt.Chart(filtered_df).transform_fold(
        selected_models,
        as_=['Model', 'Price']
    ).mark_bar().encode(
        x=alt.X('LotID:N', title='Lot ID'),
        y=alt.Y('Price:Q', title='Price ($)'),
        color='Model:N',
        tooltip=['LotID:N', 'Model:N', 'Price:Q']
    ).properties(width=1000, height=400).interactive()

    st.altair_chart(chart2, use_container_width=True)
else:
    st.warning("No data available for selected filters or no models selected.")

# -------------------------------
# Summary Stats
# -------------------------------
st.subheader("📊 Summary Stats")
col1, col2, col3 = st.columns(3)
col1.metric("Total Lots", df['LotID'].nunique())
col2.metric("Avg. Baseline Price", round(df['BaselinePrice'].mean(), 2))
col3.metric("Avg. Demand Price", round(df['DemandPrice'].mean(), 2))
col3.metric("Avg. Dynamic Price", round(df['DynamicPrice'].mean(), 2))

# -------------------------------
# Map View
# -------------------------------
st.subheader("🗺️ Lot Locations")
map_df = filtered_df.rename(columns={'Latitude': 'latitude', 'Longitude': 'longitude'})
st.map(map_df[['latitude', 'longitude']])

# -------------------------------
# Download Buttons
# -------------------------------
st.subheader("📥 Download Data")
csv_filtered = filtered_df.to_csv(index=False)
csv_full = df.to_csv(index=False)

st.download_button("⬇️ Download Filtered Data as CSV", csv_filtered, "filtered_data.csv", "text/csv")
st.download_button("⬇️ Download Full Data as CSV", csv_full, "parking_pricing_data.csv", "text/csv")

# -------------------------------
# Footer
# -------------------------------
st.markdown("---")
st.caption("🚀 Built by Mandavi Singh | Summer Analytics Project 2025")
