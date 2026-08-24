import io
import torch
import torch.nn as nn
from torchvision import models
from PIL import Image
from app.core.vision import get_shared_transforms

NUM_CLASSES = 8
CLASS_NAMES = [
    "casual_everyday",
    "formal_office",
    "modest_modern_fusion",
    "outerwear_heavy",
    "smart_casual_shirts",
    "sportswear_swimwear",
    "streetwear_hype",
    "y2k_revival"
]

def build_cnn_model():
    model = models.mobilenet_v2(weights=None)
    model.classifier[1] = nn.Sequential(
        nn.Linear(model.classifier[1].in_features, 512),
        nn.ReLU(),
        nn.Dropout(0.2),
        nn.Linear(512, NUM_CLASSES)
    )
    return model

def classify_image(image_bytes: bytes, model: nn.Module) -> dict:
    device = torch.device("cpu")
    transform = get_shared_transforms()
    
    image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
    input_tensor = transform(image).unsqueeze(0).to(device)
    
    with torch.no_grad():
        output = model(input_tensor)
        probabilities = torch.nn.functional.softmax(output[0], dim=0).tolist()
        
    pred_idx = probabilities.index(max(probabilities))
    predicted_label = CLASS_NAMES[pred_idx]
    
    label_mapping = {
        "casual_everyday": "Casual Everyday",
        "formal_office": "Formal Office",
        "modest_modern_fusion": "Modest-Modern Fusion",
        "outerwear_heavy": "Outerwear Heavy",
        "smart_casual_shirts": "Smart Casual Shirts",
        "sportswear_swimwear": "Sportswear & Swimwear",
        "streetwear_hype": "Streetwear Hype",
        "y2k_revival": "Y2K Retro Revival"
    }
    
    probs_dict = {name: round(probabilities[i], 4) for i, name in enumerate(CLASS_NAMES)}
    
    return {
        "label": label_mapping[predicted_label],
        "probabilities": probs_dict
    }
