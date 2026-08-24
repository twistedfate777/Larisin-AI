import os
import json
import requests
import shutil

def download_file(url, local_path):
    if not os.path.exists(local_path):
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(local_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

def get_target_attribute_ids(attributes, keywords):
    target_ids = set()
    for attr in attributes:
        attr_name = attr.get('name', '').lower()
        if any(kw in attr_name for kw in keywords):
            target_ids.add(attr['id'])
    return target_ids

def filter_dataset(json_path, output_root, max_per_class=100):
    with open(json_path, 'r') as f:
        data = json.load(f)
        
    attributes = data.get('attributes', [])
    images = data.get('images', [])
    annotations = data.get('annotations', [])
    
    modest_attr_keywords = ['long', 'maxi', 'midi']
    modest_attr_ids = get_target_attribute_ids(attributes, modest_attr_keywords)
    
    streetwear_attr_keywords = ['print', 'graphic', 'hood', 'loose', 'pocket']
    streetwear_attr_ids = get_target_attribute_ids(attributes, streetwear_attr_keywords)
    
    classes = [
        "casual_everyday",
        "formal_office",
        "modest_modern_fusion",
        "outerwear_heavy",
        "smart_casual_shirts",
        "sportswear_swimwear",
        "streetwear_hype",
        "y2k_revival"
    ]
    
    for cls_name in classes:
        os.makedirs(os.path.join(output_root, cls_name), exist_ok=True)
        
    img_to_url = {img['id']: img.get('original_url') for img in images if img.get('original_url')}
    class_counts = {cls: 0 for cls in classes}
    
    for ann in annotations:
        if all(count >= max_per_class for count in class_counts.values()):
            break
            
        img_id = ann.get('image_id')
        cat_id = ann.get('category_id')
        attr_ids = set(ann.get('attribute_ids', []))
        
        if not img_id or img_id not in img_to_url or not cat_id:
            continue
            
        assigned_class = None
        
        if cat_id in [13, 14]:
            assigned_class = 'y2k_revival'
        elif cat_id in [11, 21, 26]:
            assigned_class = 'sportswear_swimwear'
        elif cat_id in [4, 5]:
            assigned_class = 'formal_office'
        elif cat_id == 18:
            if attr_ids & streetwear_attr_ids:
                assigned_class = 'streetwear_hype'
            else:
                assigned_class = 'formal_office'
        elif cat_id in [6, 7, 8]:
            assigned_class = 'outerwear_heavy'
        elif cat_id == 3:
            if attr_ids & streetwear_attr_ids:
                assigned_class = 'streetwear_hype'
            else:
                assigned_class = 'outerwear_heavy'
        elif cat_id in [9, 10]:
            if attr_ids & modest_attr_ids:
                assigned_class = 'modest_modern_fusion'
            else:
                assigned_class = 'casual_everyday'
        elif cat_id in [1, 12]:
            assigned_class = 'smart_casual_shirts'
        elif cat_id in [2, 20]:
            if attr_ids & streetwear_attr_ids:
                assigned_class = 'streetwear_hype'
            else:
                assigned_class = 'casual_everyday'
                
        if not assigned_class or class_counts[assigned_class] >= max_per_class:
            continue
            
        url = img_to_url[img_id]
        ext = url.split('.')[-1]
        if len(ext) > 4:
            ext = 'jpg'
            
        save_path = os.path.join(output_root, assigned_class, f"{img_id}.{ext}")
        if os.path.exists(save_path):
            continue
            
        try:
            resp = requests.get(url, timeout=5)
            if resp.status_code == 200:
                with open(save_path, 'wb') as out_f:
                    out_f.write(resp.content)
                class_counts[assigned_class] += 1
                del img_to_url[img_id] 
        except Exception:
            pass

if __name__ == "__main__":
    DATA_DIR = "data/raw"
    JSON_URL = "https://s3.amazonaws.com/ifashionist-dataset/annotations/instances_attributes_val2020.json"
    JSON_PATH = os.path.join(DATA_DIR, "instances_attributes_val2020.json")
    OUTPUT_DIR = os.path.join(DATA_DIR, "fashionpedia_subset")
    
    os.makedirs(DATA_DIR, exist_ok=True)
    download_file(JSON_URL, JSON_PATH)
    filter_dataset(JSON_PATH, OUTPUT_DIR)
