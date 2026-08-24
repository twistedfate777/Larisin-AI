from fastapi import APIRouter, Request, UploadFile, File, Form, HTTPException
from app.schemas.pricing import PriceRecommendationResponse
from app.services import cnn_classifier, hmm_engine, monte_carlo, llm_advisor
from datetime import datetime
import logging

logger = logging.getLogger("larisin_ai")
logger.setLevel(logging.INFO)

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
        logger.error("CNN Model is not available in app state.")
        raise HTTPException(status_code=503, detail="CNN Model is not available.")
        
    logger.info("L0: Validating image content via Groq/Qwen Vision...")
    is_clothing = llm_advisor.validate_clothing_image(file_bytes)
    if not is_clothing:
        logger.warning("L0: Image rejected. Not recognized as clothing.")
        raise HTTPException(status_code=400, detail="Sistem AI kami mendeteksi bahwa gambar yang Anda unggah BUKAN pakaian/fashion (atau tidak terdeteksi). Silakan unggah foto baju yang valid.")
    logger.info("L0: Image validated as clothing. Proceeding to CNN...")
    
    logger.info("L1: Starting CNN Image Classification...")
    classification = cnn_classifier.classify_image(file_bytes, cnn_model)
    archetype_label = classification["label"]
    logger.info(f"L1: Image classified as '{archetype_label}'")
    
    trend_phase = None
    forecast_probs = {"rising": 0.33, "peak": 0.34, "declining": 0.33}
    
    archetype_keys_map = {
        "Casual Everyday": "casual_everyday",
        "Formal Office": "formal_office",
        "Modest-Modern Fusion": "modest_modern_fusion",
        "Outerwear Heavy": "outerwear_heavy",
        "Smart Casual Shirts": "smart_casual_shirts",
        "Sportswear & Swimwear": "sportswear_swimwear",
        "Streetwear Hype": "streetwear_hype",
        "Y2K Retro Revival": "y2k_revival"
    }
    
    archetype_key = archetype_keys_map[archetype_label]
    state_key = f"hmm_{archetype_key}"
    hmm_model = getattr(request.app.state, state_key, None)
    
    if not hmm_model:
        logger.error(f"HMM Model for {archetype_label} is not available.")
        raise HTTPException(status_code=503, detail=f"HMM Model for {archetype_label} is not available.")
        
    logger.info(f"L2a: Running HMM Trend Forecasting for '{archetype_label}'...")
    dummy_recent_observations = [1, 2, 2, 1]
    
    decoded = hmm_engine.decode_trend(hmm_model, dummy_recent_observations)
    forecast = hmm_engine.forecast_trend(decoded["current_state_prob"], decoded["transmat"], 4)
    
    trend_phase = {
        "current_state": decoded["current_state"],
        "forecast_4_weeks": forecast
    }
    forecast_probs = forecast
    logger.info(f"L2a: Trend forecasted as '{decoded['current_state']}'")
        
    logger.info("L2b: Running Monte Carlo Price Optimization...")
    pricing = monte_carlo.optimize_price(base_price, forecast_probs)
    logger.info(f"L2b: Monte Carlo recommended price: Rp{pricing['recommended_price']}")
    
    advisor_context = {
        "archetype": archetype_label,
        "trend_phase": trend_phase["current_state"] if trend_phase else "Generic",
        "base_price": base_price,
        "recommended_price": pricing["recommended_price"],
        "expected_value": pricing["expected_value"]
    }
    
    logger.info("L3: Requesting Groq LLM Advisor for reasoning and caption...")
    advisor = llm_advisor.generate_advisor_response(advisor_context)
    logger.info("L3: Groq LLM Advisor responded successfully.")
    
    logger.info("Pipeline completed. Returning JSON response to client.")
    return {
        "product": "Larisin AI",
        "archetype_classification": classification,
        "trend_phase": trend_phase,
        "pricing": pricing,
        "advisor": advisor
    }
