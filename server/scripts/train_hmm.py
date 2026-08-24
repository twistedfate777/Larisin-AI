import os
import json
import logging
import pandas as pd
import numpy as np
from hmmlearn import hmm
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def bin_interest(value):
    if value <= 33:
        return 0
    elif value <= 66:
        return 1
    else:
        return 2

def train_and_save_hmm():
    os.makedirs(settings.HMM_MODELS_DIR, exist_ok=True)
    
    archetypes = [
        "casual_everyday",
        "formal_office",
        "modest_modern_fusion",
        "outerwear_heavy",
        "smart_casual_shirts",
        "sportswear_swimwear",
        "streetwear_hype",
        "y2k_revival"
    ]
    
    for archetype in archetypes:
        csv_path = os.path.join(settings.TRENDS_CACHE_DIR, f"{archetype}_trends.csv")
        
        if not os.path.exists(csv_path):
            logger.warning(f"Trend data for {archetype} not found at {csv_path}. Skipping.")
            continue
            
        logger.info(f"Training HMM for {archetype}...")
        df = pd.read_csv(csv_path)
        
        if 'interest' not in df.columns:
            logger.error(f"'interest' column missing in {csv_path}. Skipping.")
            continue
            
        df['observation'] = df['interest'].apply(bin_interest)
        
        X = df['observation'].values.reshape(-1, 1)
        
        model = hmm.CategoricalHMM(n_components=3, n_iter=100, random_state=42)
        model.fit(X)
        
        expected_values = np.zeros(3)
        for i in range(3):
            expected_values[i] = sum(model.emissionprob_[i, k] * k for k in range(3))
            
        sorted_indices = np.argsort(expected_values)
        idx_declining = sorted_indices[0]
        idx_rising = sorted_indices[1]
        idx_peak = sorted_indices[2]
        
        new_order = [idx_rising, idx_peak, idx_declining]
        
        startprob_new = model.startprob_[new_order]
        
        transmat_new = model.transmat_[new_order, :]
        transmat_new = transmat_new[:, new_order]
        
        emissionprob_new = model.emissionprob_[new_order, :]
        
        model_data = {
            "startprob": startprob_new.tolist(),
            "transmat": transmat_new.tolist(),
            "emissionprob": emissionprob_new.tolist()
        }
        
        out_path = os.path.join(settings.HMM_MODELS_DIR, f"hmm_{archetype}.json")
        with open(out_path, "w") as f:
            json.dump(model_data, f, indent=2)
            
        logger.info(f"Successfully trained and saved {archetype} HMM to {out_path}")

if __name__ == "__main__":
    train_and_save_hmm()
