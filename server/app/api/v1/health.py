from fastapi import APIRouter, Request

router = APIRouter()

@router.get("/health")
async def health_check(request: Request):
    state = request.app.state
    
    models_loaded = {
        "cnn": getattr(state, "cnn_model", None) is not None,
        "hmm_modest_modern_fusion": getattr(state, "hmm_modest_modern", None) is not None,
        "hmm_heritage_eco": getattr(state, "hmm_heritage_eco", None) is not None,
        "hmm_y2k_revival": getattr(state, "hmm_y2k_revival", None) is not None
    }
    
    return {
        "status": "ok",
        "models_loaded": models_loaded
    }
