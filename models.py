def compute_baseline_price(row, alpha=5):
    return 10 + alpha * (row['Occupancy'] / row['Capacity'])

def compute_demand_price(row, alpha=0.4, beta=0.3, gamma=0.2, delta=0.1, epsilon=0.5):
    try:
        traffic = float(row['TrafficConditionNearby'])  # 🔧 convert to float safely
    except:
        traffic = 0.0  # or np.nan or raise an error depending on your need

    demand = (
        alpha * (row['Occupancy'] / row['Capacity']) +
        beta * row['QueueLength'] -
        gamma * traffic +
        delta * row['IsSpecialDay'] +
        epsilon * row.get('VehicleTypeWeight', 1)
    )
    norm_demand = max(0.5, min(2, demand))
    return 10 * norm_demand


def compute_dynamic_price(current_lot, df_all, base_price=10):
    from utils import haversine_distance
    df_all = df_all.copy()
    df_all['Distance'] = df_all.apply(
        lambda row: haversine_distance(current_lot['Latitude'], current_lot['Longitude'],
                                       row['Latitude'], row['Longitude']), axis=1)
    nearby = df_all[(df_all['Distance'] < 1) & (df_all['ID'] != current_lot['ID'])]
    nearby['price'] = 10 + (nearby['Occupancy'] / nearby['Capacity']) * 10
    avg_price = nearby['price'].mean() if not nearby.empty else base_price
    occ_ratio = current_lot['Occupancy'] / current_lot['Capacity']

    if occ_ratio > 0.9 and avg_price < base_price:
        return max(base_price - 2, 5)
    elif occ_ratio < 0.4 and avg_price > base_price:
        return min(base_price + 2, 20)
    else:
        return base_price + occ_ratio * 5
