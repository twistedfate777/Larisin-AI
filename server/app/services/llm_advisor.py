import json
import logging
from openai import OpenAI
from app.core.config import settings

logger = logging.getLogger(__name__)

client = OpenAI(
    base_url=settings.GROQ_API_BASE,
    api_key=settings.GROQ_API_KEY,
)

def build_advisor_prompt(context: dict) -> str:
    prompt = (
        "Anda adalah AI asisten untuk penjual fesyen di Indonesia.\n"
        "Berikan penjelasan strategi harga dan draf caption media sosial berdasarkan konteks berikut:\n"
        f"- Archetype tren: {context.get('archetype', 'Generic')}\n"
        f"- Fase saat ini: {context.get('trend_phase', 'N/A')}\n"
        f"- Harga modal: Rp{context.get('base_price', 0)}\n"
        f"- Harga rekomendasi: Rp{context.get('recommended_price', 0)}\n"
        f"- Expected value: Rp{context.get('expected_value', 0)}\n\n"
        "Kembalikan response DALAM FORMAT JSON DENGAN STRUKTUR BERIKUT:\n"
        "{\n"
        '  "explanation": "Penjelasan alasan harga...",\n'
        '  "listing_caption_draft": "Draf caption sosmed..."\n'
        "}\n"
    )
    return prompt

def generate_advisor_response(pricing_context: dict) -> dict:
    prompt = build_advisor_prompt(pricing_context)
    
    try:
        response = client.chat.completions.create(
            model=settings.GROQ_MODEL_PRIMARY,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.7,
        )
        model_used = settings.GROQ_MODEL_PRIMARY
    except Exception as e:
        logger.warning(f"Primary LLM failed: {e}. Switching to fallback model.")
        response = client.chat.completions.create(
            model=settings.GROQ_MODEL_FALLBACK,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.7,
        )
        model_used = settings.GROQ_MODEL_FALLBACK
        
    content = response.choices[0].message.content
    
    try:
        parsed_data = json.loads(content)
    except json.JSONDecodeError:
        parsed_data = {
            "explanation": "Gagal mengurai respons dari AI.",
            "listing_caption_draft": ""
        }
        
    parsed_data["model_used"] = model_used
    
    return parsed_data
