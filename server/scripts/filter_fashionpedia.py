import os
import json
import requests

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
    
    y2k_kw = ['crop (top)', 'crop (jacket)', 'halter (top)', 'tube (top)', 'track (jacket)', 'windbreaker']
    streetwear_kw = ['hoodie', 'oversized', 'bomber (jacket)', 'letters, numbers']
    formal_kw = ['blazer', 'tuxedo (jacket)']
    outerwear_kw = ['puffer (jacket)', 'puffer (coat)', 'parka', 'shearling (coat)', 'teddy bear (coat)', 'trench (coat)', 'biker (jacket)']
    
    short_kw = ['mini (length)', 'micro (length)', 'short (length)', 'above-the-knee (length)', 'above-the-hip (length)']
    modest_kw = ['knee (length)', 'below the knee (length)', 'midi']
    long_kw = ['maxi (length)', 'floor (length)']
    
    y2k_ids = get_target_attribute_ids(attributes, y2k_kw)
    streetwear_ids = get_target_attribute_ids(attributes, streetwear_kw)
    formal_ids = get_target_attribute_ids(attributes, formal_kw)
    outerwear_ids = get_target_attribute_ids(attributes, outerwear_kw)
    
    short_ids = get_target_attribute_ids(attributes, short_kw)
    modest_ids = get_target_attribute_ids(attributes, modest_kw)
    long_ids = get_target_attribute_ids(attributes, long_kw)
    
    classes = [
        "casual_everyday",
        "formal_office",
        "modest_modern_fusion",
        "outerwear_heavy",
        "streetwear_hype",
        "y2k_revival"
    ]
    
    for cls_name in classes:
        os.makedirs(os.path.join(output_root, cls_name), exist_ok=True)
        
    img_to_url = {img['id']: img.get('original_url') for img in images if img.get('original_url')}
    class_counts = {cls: 0 for cls in classes}
    
    valid_top_cats = [0, 1, 2, 3, 4, 5, 9, 10, 11]
    
    images_data = {}
    for ann in annotations:
        img_id = ann.get('image_id')
        cat_id = ann.get('category_id')
        attr_ids = set(ann.get('attribute_ids', []))
        
        if not img_id or not cat_id:
            continue
            
        if img_id not in images_data:
            images_data[img_id] = {'cat_ids': set(), 'attr_ids': set()}
            
        images_data[img_id]['cat_ids'].add(cat_id)
        images_data[img_id]['attr_ids'].update(attr_ids)
        
    for img_id, data in images_data.items():
        if all(count >= max_per_class for count in class_counts.values()):
            break
            
        if img_id not in img_to_url:
            continue
            
        cats = data['cat_ids']
        attrs = data['attr_ids']
        
        if not any(c in valid_top_cats for c in cats):
            continue
            
        is_very_open = (7 in cats) or bool(attrs & short_ids)
        is_modest_bottom = (8 in cats) or bool(attrs & modest_ids)
        is_heavy_bottom = (6 in cats) or (15 in cats) or bool(attrs & long_ids)
        
        if attrs & formal_ids:
            assigned_class = 'formal_office'
            
        elif (attrs & outerwear_ids) or ((4 in cats or 9 in cats) and 15 in cats):
            assigned_class = 'outerwear_heavy'
            
        elif (attrs & long_ids) and (10 in cats):
            assigned_class = 'modest_modern_fusion'
            
        elif is_very_open:
            if attrs & y2k_ids:
                assigned_class = 'y2k_revival'
            elif attrs & streetwear_ids:
                assigned_class = 'streetwear_hype'
            else:
                assigned_class = 'casual_everyday'
                
        elif attrs & streetwear_ids:
            assigned_class = 'streetwear_hype'
        elif attrs & y2k_ids:
            assigned_class = 'y2k_revival'
        else:
            assigned_class = 'casual_everyday'
            
        if not assigned_class or class_counts[assigned_class] >= max_per_class:
            continue
            
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
