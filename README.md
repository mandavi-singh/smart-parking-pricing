# smart-parking-pricing
# 🅿️ Smart Parking Pricing Models

This project implements dynamic and competitive pricing strategies for smart city parking. It helps determine optimal parking prices based on real-time data such as occupancy, traffic, and proximity to other lots.

🔗 **Live Demo**: [smart-parking-pricing.streamlit.app](https://smart-parking-pricing-e88vip36arb5x6hbvnczhf.streamlit.app)

---

## 📌 Overview

This app compares three different pricing models:
1. **Baseline Linear Model**  
2. **Demand-Based Model**
3. **Competitive Pricing Model**

Developed and deployed as part of a **Summer Analytics Project** using:
- ✅ Streamlit (for web app)
- ✅ Python (Pandas, NumPy,Matplotlib)
- ✅ GitHub + Colab (for collaboration and version control)

---

## 🧠 Pricing Models Explained

### 🔹 Model 1: Baseline Linear Pricing
Simple formula:Price(t+1) = Price(t) + α × (Occupancy / Capacity)
This model assumes price should increase linearly as more slots are occupied.

---

### 🔹 Model 2: Demand-Based Pricing
Takes into account multiple demand factors:
Demand = α × (Occupancy / Capacity)+ β × QueueLength− γ × Traffic+ δ × IsSpecialDay+ ε × VehicleTypeWeight

Price(t) = BasePrice × (1 + λ × NormalizedDemand)

---

### 🔹 Model 3: Competitive Pricing (Location-Aware)
Adjusts price based on nearby lots within 1km using Haversine distance:
- 🔼 Raise price if nearby lots are more expensive and you’re underused.
- 🔽 Lower price if nearby cheaper lots are less full.

---

## 📊 Features

- 📈 Visual comparison of pricing models per lot
- 📍 Interactive map with all lot locations
- 📆 Filter by timestamp and lot ID
- 📥 Download filtered and full datasets
- 📘 Expandable model explanation section

---
## 📂 Project Structure
smart-parking-pricing

├── app.py                             # Main Streamlit app

├── models.py                          # Contains price computation functions

├── utils.py                           # Utility functions (e.g., distance calculation)

├── dataset.csv                        # Sample parking dataset

├── requirements.txt                   # Python dependencies

├── Parking_Pricing_Models_Comparison.ipynb  # Colab notebook for EDA and model testing

└── README.md                          # Project documentation


---

## ⚙️ Run Locally

```bash
git clone https://github.com/mandavi-singh/smart-parking-pricing.git
cd smart-parking-pricing
pip install -r requirements.txt
streamlit run app.py
```


## 👩‍💻 Author
Mandavi Singh
📍 IIT Guwahati | BSc (Hons) Data Science & AI


