import logging
import numpy as np
from hmmlearn import hmm

logger = logging.getLogger(__name__)

STATES = ["Rising", "Peak", "Declining"]

def decode_trend(model: hmm.CategoricalHMM, recent_observations: list) -> dict:
    obs_array = np.array(recent_observations).reshape(-1, 1)
    
    try:
        logprob, states = model.decode(obs_array, algorithm="viterbi")
        
        posterior_probs = model.predict_proba(obs_array)
        last_prob = posterior_probs[-1]
        
        current_state_idx = states[-1]
        current_state_name = STATES[current_state_idx]
        
        return {
            "current_state": current_state_name,
            "current_state_prob": last_prob.tolist(),
            "transmat": model.transmat_.tolist()
        }
        
    except Exception as e:
        logger.error(f"Error during Viterbi decoding: {e}")
        raise

def forecast_trend(current_state_prob: list, transmat: list, horizon_weeks: int = 4) -> dict:
    pi = np.array(current_state_prob)
    A = np.array(transmat)
    
    A_H = np.linalg.matrix_power(A, horizon_weeks)
    
    pi_H = np.dot(pi, A_H)
    
    return {
        "rising": round(pi_H[0], 4),
        "peak": round(pi_H[1], 4),
        "declining": round(pi_H[2], 4)
    }
