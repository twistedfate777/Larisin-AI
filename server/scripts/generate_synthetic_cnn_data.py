import os
import logging
from openai import OpenAI
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SYNTHETIC_PROMPT_TEMPLATE = """
Buat 20 deskripsi atribut visual pakaian yang termasuk kategori tren
"{archetype_name}" untuk konteks fesyen Indonesia. Setiap deskripsi
harus spesifik dan bisa dipakai sebagai kriteria label engineering
untuk memetakan dataset DeepFashion ke kategori ini.

Archetype: {archetype_description}

Format output: daftar bullet point, satu atribut per baris.
"""

def generate_synthetic_data():
    client = OpenAI(
        base_url=settings.GROQ_API_BASE,
        api_key=settings.GROQ_API_KEY,
    )
    
    archetypes = {
        "Modest-Modern Fusion": "Pakaian muslim/modest dengan gaya modern, warna pastel/bumi, dan potongan elegan.",
        "Heritage Eco": "Pakaian yang menginkorporasikan elemen tradisional seperti batik, tenun, dipadukan dengan konsep ramah lingkungan.",
        "Y2K Retro Revival": "Gaya pakaian ala tahun 2000-an yang kembali populer, seperti celana kargo, crop top, dan warna neon."
    }
    
    # Path relatif berdasarkan struktur data
    output_file = os.path.join(settings.HMM_MODELS_DIR, "..", "label_mapping_synthetic_reference.md")
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    results = []
    
    for name, desc in archetypes.items():
        prompt = SYNTHETIC_PROMPT_TEMPLATE.format(
            archetype_name=name,
            archetype_description=desc
        )
        
        logger.info("Generating data untuk archetype: %s", name)
        try:
            response = client.chat.completions.create(
                model=settings.GROQ_MODEL_PRIMARY,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
            )
            content = response.choices[0].message.content
            results.append(f"## {name}\n\n{content}\n")
        except Exception as e:
            logger.error("Error primary model untuk %s: %s. Mencoba fallback.", name, e)
            try:
                response = client.chat.completions.create(
                    model=settings.GROQ_MODEL_FALLBACK,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                )
                content = response.choices[0].message.content
                results.append(f"## {name}\n\n{content}\n")
            except Exception as e2:
                logger.error("Error fallback model untuk %s: %s", name, e2)
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("# Label Mapping Synthetic Reference\n\n")
        f.write("\n".join(results))
        
    logger.info("Selesai. Hasil augmentasi disave ke %s", output_file)

if __name__ == "__main__":
    generate_synthetic_data()
