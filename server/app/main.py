import os
import json
import torch
import numpy as np
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from hmmlearn import hmm
from app.core.config import settings
from app.services.cnn_classifier import build_cnn_model
from app.api.v1 import health, price_recommendation
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    device = torch.device("cpu")
    cnn_model = None
    if os.path.exists(settings.CNN_MODEL_PATH):
        try:
            cnn_model = build_cnn_model()
            cnn_model.load_state_dict(torch.load(settings.CNN_MODEL_PATH, map_location=device, weights_only=True))
            cnn_model.to(device)
            cnn_model.eval()
        except Exception:
            cnn_model = None
            
    app.state.cnn_model = cnn_model

    archetypes = {
        "casual_everyday": "hmm_casual_everyday",
        "formal_office": "hmm_formal_office",
        "modest_modern_fusion": "hmm_modest_modern_fusion",
        "outerwear_heavy": "hmm_outerwear_heavy",
        "streetwear_hype": "hmm_streetwear_hype",
        "y2k_revival": "hmm_y2k_revival"
    }
    
    for arc_key, state_key in archetypes.items():
        hmm_model = None
        model_path = os.path.join(settings.HMM_MODELS_DIR, f"hmm_{arc_key}.json")
        if os.path.exists(model_path):
            try:
                with open(model_path, 'r') as f:
                    params = json.load(f)
                hmm_model = hmm.CategoricalHMM(n_components=3, init_params="")
                hmm_model.startprob_ = np.array(params['startprob'])
                hmm_model.transmat_ = np.array(params['transmat'])
                hmm_model.emissionprob_ = np.array(params['emissionprob'])
            except Exception:
                hmm_model = None
        setattr(app.state, state_key, hmm_model)
        
    yield
    
    app.state.cnn_model = None
    for state_key in archetypes.values():
        setattr(app.state, state_key, None)

app = FastAPI(title="Larisin AI", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api/v1", tags=["Health"])
app.include_router(price_recommendation.router, prefix="/api/v1", tags=["Pricing"])
