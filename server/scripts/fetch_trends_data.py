import os
import time
import logging

from app.core.config import settings
from pytrends.request import TrendReq

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fetch_and_cache_trends():
    os.makedirs(settings.TRENDS_CACHE_DIR, exist_ok=True)
    
    archetypes = {
        "modest_modern": ["tunik modern"],
        "heritage_eco": ["baju batik"],
        "y2k_revival": ["celana cargo"]
    }
    
    try:
        pytrend = TrendReq(hl='id-ID', tz=420)
    except Exception as e:
        logger.error("Gagal menginisialisasi pytrends: %s", e)
        return

    for archetype, keywords in archetypes.items():
        max_retries = 3
        for attempt in range(max_retries):
            try:
                logger.info("Mengambil data tren untuk: %s (Attempt %d/%d)", archetype, attempt + 1, max_retries)
                pytrend.build_payload(kw_list=keywords, cat=0, timeframe='today 5-y', geo='ID')
                data = pytrend.interest_over_time()
                
                if not data.empty:
                    if 'isPartial' in data.columns:
                        data = data.drop(columns=['isPartial'])
                    
                    data['interest'] = data[keywords].mean(axis=1)
                    
                    file_path = os.path.join(settings.TRENDS_CACHE_DIR, f"{archetype}_trends.csv")
                    data[['interest']].to_csv(file_path)
                    logger.info("Berhasil menyimpan data tren ke %s", file_path)
                else:
                    logger.warning("Data tren kosong untuk %s", archetype)
                    
                time.sleep(10)  # Increased base sleep to prevent 429
                break  # Berhasil, keluar dari retry loop
                
            except Exception as e:
                if "429" in str(e) and attempt < max_retries - 1:
                    wait_time = 60 * (attempt + 1)
                    logger.warning("Terkena rate limit (429) untuk %s. Menunggu %d detik...", archetype, wait_time)
                    time.sleep(wait_time)
                else:
                    logger.error("Terjadi kesalahan saat mengambil tren untuk %s: %s", archetype, e)
                    break


if __name__ == "__main__":
    fetch_and_cache_trends()
