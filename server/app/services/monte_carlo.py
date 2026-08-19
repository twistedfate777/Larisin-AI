import numpy as np
from app.core.config import settings

def optimize_price(base_price: float, forecast: dict) -> dict:
    np.random.seed(settings.MONTE_CARLO_SEED)
    
    candidates = np.linspace(0.5 * base_price, 1.5 * base_price, 11)
    
    baseline = {
        "rising": 0.65,
        "peak": 0.80,
        "declining": 0.30
    }
    
    gamma = 0.9
    clearance_ratio = 0.4
    storage_cost_ratio = 0.05
    
    p_clearance = clearance_ratio * base_price
    c_storage = storage_cost_ratio * base_price
    
    state_names = ["rising", "peak", "declining"]
    state_probs = [forecast["rising"], forecast["peak"], forecast["declining"]]
    
    expected_values = []
    
    for p in candidates:
        total_reward = 0.0
        
        sampled_states = np.random.choice(state_names, size=settings.MONTE_CARLO_SIMULATIONS, p=state_probs)
        
        for state in sampled_states:
            p_sell = baseline[state] - gamma * ((p - base_price) / base_price)
            p_sell = max(0.0, min(1.0, p_sell))
            
            is_sold = np.random.random() < p_sell
            
            if is_sold:
                total_reward += p
            else:
                total_reward += (p_clearance - c_storage)
                
        avg_reward = total_reward / settings.MONTE_CARLO_SIMULATIONS
        expected_values.append({
            "price": float(round(p, 2)),
            "expected_value": float(round(avg_reward, 2))
        })
        
    best_candidate = max(expected_values, key=lambda x: x["expected_value"])
    
    return {
        "recommended_price": best_candidate["price"],
        "expected_value": best_candidate["expected_value"],
        "comparison": expected_values
    }
