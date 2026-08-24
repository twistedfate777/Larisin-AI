from fastapi import APIRouter, Request

router = APIRouter()

@router.get("/health")
async def health_check(request: Request):
    state = request.app.state
    
    models_loaded = {
        "cnn": getattr(state, "cnn_model", None) is not None,
        "hmm_casual_everyday": getattr(state, "hmm_casual_everyday", None) is not None,
        "hmm_formal_office": getattr(state, "hmm_formal_office", None) is not None,
        "hmm_modest_modern_fusion": getattr(state, "hmm_modest_modern_fusion", None) is not None,
        "hmm_outerwear_heavy": getattr(state, "hmm_outerwear_heavy", None) is not None,
        "hmm_streetwear_hype": getattr(state, "hmm_streetwear_hype", None) is not None,
        "hmm_y2k_revival": getattr(state, "hmm_y2k_revival", None) is not None
    }
    
    return {
        "status": "ok",
        "models_loaded": models_loaded
    }
