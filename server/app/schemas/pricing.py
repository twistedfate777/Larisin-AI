from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class ArchetypeClassification(BaseModel):
    label: str
    probabilities: Dict[str, float]

class TrendForecast(BaseModel):
    rising: float
    peak: float
    declining: float

class TrendPhase(BaseModel):
    current_state: str
    forecast_4_weeks: TrendForecast

class PriceComparison(BaseModel):
    price: float
    expected_value: float

class PricingDetails(BaseModel):
    recommended_price: float
    expected_value: float
    comparison: List[PriceComparison]

class AdvisorDetails(BaseModel):
    model_used: str
    explanation: str
    listing_caption_draft: str

class PriceRecommendationResponse(BaseModel):
    product: str = "Larisin AI"
    archetype_classification: ArchetypeClassification
    trend_phase: Optional[TrendPhase] = None
    pricing: PricingDetails
    advisor: AdvisorDetails
