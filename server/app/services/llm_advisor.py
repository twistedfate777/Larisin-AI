import json
import logging
from openai import OpenAI
from app.core.config import settings

logger = logging.getLogger(__name__)

client = OpenAI(
    base_url=settings.GROQ_API_BASE,
    api_key=settings.GROQ_API_KEY,
)

import base64

def validate_clothing_image(image_bytes: bytes) -> bool:
    base64_image = base64.b64encode(image_bytes).decode('utf-8')
    prompt = (
        "Kategorikan objek UTAMA yang ada di dalam gambar ini ke dalam salah satu kategori berikut:\n"
        "1. CLOTHING (Baju, celana, jaket, gaun, pakaian di hanger, pakaian di manekin)\n"
        "2. VEHICLE (Mobil, motor, sepeda)\n"
        "3. DOCUMENT (Teks tulisan, screenshot lowongan kerja, dokumen)\n"
        "4. ANIMAL (Kucing, anjing, burung)\n"
        "5. OTHER (Benda mati lainnya seperti gelas, meja, pemandangan)\n\n"
        "Jawab HANYA dengan SATU KATA nama kategorinya (CLOTHING, VEHICLE, DOCUMENT, ANIMAL, atau OTHER)."
    )
    
    import re
        
    try:
        response = client.chat.completions.create(
            model="qwen/qwen3.6-27b",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            temperature=0.1,
            max_tokens=500
        )
        raw_answer = response.choices[0].message.content.strip().upper()
        clean_answer = re.sub(r'<THINK>.*?</THINK>', '', raw_answer, flags=re.DOTALL)
        return "CLOTHING" in clean_answer
    except Exception as e:
        logger.error(f"L0 Vision Validation Failed: {e}. Bypassing filter.")
        return True

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
