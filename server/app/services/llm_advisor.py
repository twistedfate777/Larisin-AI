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
import io
from PIL import Image

def validate_clothing_image(image_bytes: bytes) -> bool:
    try:
        img = Image.open(io.BytesIO(image_bytes))
        if img.mode != 'RGB':
            img = img.convert('RGB')
        img.thumbnail((512, 512))
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=85)
        compressed_bytes = buffer.getvalue()
    except Exception as e:
        logger.error(f"Gagal memproses gambar dengan PIL: {e}")
        compressed_bytes = image_bytes

    base64_image = base64.b64encode(compressed_bytes).decode('utf-8')
    prompt = (
        "Kategorikan wujud FISIK dari objek UTAMA yang ada di dalam gambar ini ke dalam salah satu kategori berikut:\n"
        "1. CLOTHING (Wujud fisik sepotong baju, celana, jaket, gaun, pakaian di hanger, pakaian di manekin)\n"
        "2. VEHICLE (Mobil, motor, sepeda)\n"
        "3. DOCUMENT (Teks tulisan, screenshot aplikasi, diagram, bagan, flowchart, grafik, logo, dokumen)\n"
        "4. ANIMAL (Kucing, anjing, burung)\n"
        "5. OTHER (Benda mati lainnya seperti gelas, meja, pemandangan)\n\n"
        "ATURAN SUPER KETAT: Jika gambar tersebut adalah sebuah BAGAN, DIAGRAM, GRAFIK, atau TEKS (seperti diagram alur yang Anda lihat sekarang), Anda WAJIB menjawab DOCUMENT, tidak peduli apakah teks di dalam diagram tersebut membahas tentang fashion, baju, atau Y2K.\n\n"
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
        logger.info(f"L0 Vision Raw Output: '{raw_answer}'")
        clean_answer = re.sub(r'<THINK>.*?</THINK>', '', raw_answer, flags=re.DOTALL)
        
        categories = ["CLOTHING", "VEHICLE", "DOCUMENT", "ANIMAL", "OTHER"]
        final_category = None
        last_index = -1
        
        for cat in categories:
            idx = clean_answer.rfind(cat)
            if idx > last_index:
                last_index = idx
                final_category = cat
                
        logger.info(f"L0 Vision Final Category Evaluated: {final_category}")
        return final_category == "CLOTHING"
        
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
