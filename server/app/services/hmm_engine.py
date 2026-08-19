import os
import json
import logging
import numpy as np
from hmmlearn import hmm
from app.core.config import settings

logger = logging.getLogger(__name__)

STATES = ["Rising", "Peak", "Declining"]

class HMMEngine:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(HMMEngine, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        self.models = {}
        self.is_loaded = False
        
        archetypes = ["modest_modern", "heritage_eco", "y2k_revival"]
        
        models_loaded = 0
        for archetype in archetypes:
            model_path = os.path.join(settings.HMM_MODELS_DIR, f"hmm_{archetype}.json")
            if os.path.exists(model_path):
                try:
                    with open(model_path, 'r') as f:
                        params = json.load(f)
                        
                    model = hmm.MultinomialHMM(n_components=3, init_params="")
                    model.startprob_ = np.array(params['startprob'])
                    model.transmat_ = np.array(params['transmat'])
                    model.emissionprob_ = np.array(params['emissionprob'])
                    
                    self.models[archetype] = model
                    models_loaded += 1
                except Exception as e:
                    logger.error(f"Failed to load HMM for {archetype}: {e}")
            else:
                logger.warning(f"HMM model file not found for {archetype} at {model_path}")
                
        if models_loaded == len(archetypes):
            self.is_loaded = True
            logger.info("All HMM models loaded successfully.")
            
    def get_model(self, archetype_key: str):
        if archetype_key not in self.models:
            raise ValueError(f"HMM model for {archetype_key} not available.")
        return self.models[archetype_key]

    def decode_trend(self, archetype_key: str, recent_observations: list) -> dict:
        if archetype_key not in self.models:
            return {
                "current_state": "Peak",
                "current_state_prob": [0.1, 0.8, 0.1],
                "transmat": [[0.5, 0.4, 0.1], [0.1, 0.5, 0.4], [0.4, 0.1, 0.5]]
            }
            
        model = self.models[archetype_key]
        
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

    def forecast_trend(self, current_state_prob: list, transmat: list, horizon_weeks: int = 4) -> dict:
        pi = np.array(current_state_prob)
        A = np.array(transmat)
        
        A_H = np.linalg.matrix_power(A, horizon_weeks)
        
        pi_H = np.dot(pi, A_H)
        
        return {
            "rising": round(pi_H[0], 4),
            "peak": round(pi_H[1], 4),
            "declining": round(pi_H[2], 4)
        }

hmm_engine = HMMEngine()
