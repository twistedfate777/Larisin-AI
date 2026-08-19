from fastapi import APIRouter, Request, UploadFile, File, Form, HTTPException
from app.schemas.pricing import PriceRecommendationResponse
from app.services import cnn_classifier, hmm_engine, monte_carlo, llm_advisor
from datetime import datetime

router = APIRouter()

@router.post("/price-recommendation", response_model=PriceRecommendationResponse)
async def get_price_recommendation(
    request: Request,
    image: UploadFile = File(...),
    base_price: float = Form(...),
    stock_entry_date: str = Form(...)
):
    if image.content_type not in ["image/jpeg", "image/png", "image/jpg"]:
        raise HTTPException(status_code=400, detail="Invalid file type. Only JPEG and PNG are allowed.")
    
    file_bytes = await image.read()
    if len(file_bytes) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File size too large. Maximum size is 5MB.")
        
    cnn_model = getattr(request.app.state, "cnn_model", None)
    if not cnn_model:
        raise HTTPException(status_code=503, detail="CNN Model is not available.")
        
    classification = cnn_classifier.classify_image(file_bytes, cnn_model)
    archetype_label = classification["label"]
    
    trend_phase = None
    forecast_probs = {"rising": 0.33, "peak": 0.34, "declining": 0.33}
    
    archetype_keys_map = {
        "Modest-Modern Fusion": "modest_modern",
        "Heritage Eco": "heritage_eco",
        "Y2K Retro Revival": "y2k_revival"
    }
    
    if archetype_label != "Generic":
        archetype_key = archetype_keys_map[archetype_label]
        state_key = f"hmm_{archetype_key}"
        hmm_model = getattr(request.app.state, state_key, None)
        
        if not hmm_model:
            raise HTTPException(status_code=503, detail=f"HMM Model for {archetype_label} is not available.")
            
        dummy_recent_observations = [1, 2, 2, 1]
        
        decoded = hmm_engine.decode_trend(hmm_model, dummy_recent_observations)
        forecast = hmm_engine.forecast_trend(decoded["current_state_prob"], decoded["transmat"], 4)
        
        trend_phase = {
            "current_state": decoded["current_state"],
            "forecast_4_weeks": forecast
        }
        forecast_probs = forecast
    else:
        try:
            entry_date = datetime.strptime(stock_entry_date, "%Y-%m-%d")
            days_in_stock = (datetime.now() - entry_date).days
            if days_in_stock < 30:
                current_state = "Rising"
                forecast_probs = {"rising": 0.60, "peak": 0.30, "declining": 0.10}
            elif days_in_stock < 90:
                current_state = "Peak"
                forecast_probs = {"rising": 0.10, "peak": 0.60, "declining": 0.30}
            else:
                current_state = "Declining"
                forecast_probs = {"rising": 0.05, "peak": 0.15, "declining": 0.80}
        except ValueError:
            current_state = "Unknown"
            
        trend_phase = {
            "current_state": current_state,
            "forecast_4_weeks": forecast_probs
        }
        
    pricing = monte_carlo.optimize_price(base_price, forecast_probs)
    
    advisor_context = {
        "archetype": archetype_label,
        "trend_phase": trend_phase["current_state"] if trend_phase else "Generic",
        "base_price": base_price,
        "recommended_price": pricing["recommended_price"],
        "expected_value": pricing["expected_value"]
    }
    
    advisor = llm_advisor.generate_advisor_response(advisor_context)
    
    return {
        "product": "Larisin AI",
        "archetype_classification": classification,
        "trend_phase": trend_phase,
        "pricing": pricing,
        "advisor": advisor
    }
