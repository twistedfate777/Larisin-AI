import os
import time
import random
import logging
import pandas as pd
from pytrends.request import TrendReq
from app.core.config import settings

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

def fetch_and_save_trends():
    os.makedirs(settings.TRENDS_CACHE_DIR, exist_ok=True)
    
    trend_queries = {
        "casual_everyday": "Baju Kasual",
        "formal_office": "Kemeja Kantor",
        "modest_modern_fusion": "Gamis Modern",
        "outerwear_heavy": "Jaket Tebal",
        "streetwear_hype": "Baju Oversize",
        "y2k_revival": "Baju Y2K"
    }
    
    pytrend = TrendReq(hl='id-ID', tz=420)
    
    for archetype, keyword in trend_queries.items():
        csv_path = os.path.join(settings.TRENDS_CACHE_DIR, f"{archetype}_trends.csv")
        if os.path.exists(csv_path):
            logger.info(f"Trend data for {archetype} already exists. Skipping.")
            continue
            
        logger.info(f"Fetching Google Trends for '{keyword}' (Archetype: {archetype})...")
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                pytrend.build_payload(kw_list=[keyword], geo='ID', timeframe='today 5-y')
                df = pytrend.interest_over_time()
                
                if df.empty:
                    logger.warning(f"No trend data found for '{keyword}'. Creating dummy flat trend.")
                    dates = pd.date_range(end=pd.Timestamp.today(), periods=260, freq='W')
                    df = pd.DataFrame({"interest": [50]*260}, index=dates)
                else:
                    df = df.rename(columns={keyword: 'interest'})
                    if 'isPartial' in df.columns:
                        df = df.drop(columns=['isPartial'])
                
                df.to_csv(csv_path)
                logger.info(f"Successfully saved trends for {archetype} to {csv_path}")
                break
                
            except Exception as e:
                logger.error(f"Attempt {attempt+1} failed for {keyword}: {e}")
                if attempt < max_retries - 1:
                    sleep_time = random.uniform(15, 30) * (attempt + 1)
                    logger.info(f"Rate limited or error. Retrying in {sleep_time:.2f} seconds...")
                    time.sleep(sleep_time)
                else:
                    logger.error(f"Failed to fetch trends for {keyword} after {max_retries} attempts.")
                    
        sleep_duration = random.uniform(5, 10)
        logger.info(f"Sleeping for {sleep_duration:.2f} seconds before next keyword...")
        time.sleep(sleep_duration)

if __name__ == "__main__":
    fetch_and_save_trends()
