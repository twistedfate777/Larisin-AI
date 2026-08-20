import io
import torch
import torch.nn as nn
from torchvision import models
from PIL import Image
from app.core.vision import get_shared_transforms

NUM_CLASSES = 3
CLASS_NAMES = ["generic", "modest_modern_fusion", "y2k_revival"]

def build_cnn_model():
    model = models.mobilenet_v2(weights=None)
    num_ftrs = model.classifier[1].in_features
    model.classifier[1] = nn.Sequential(
        nn.Linear(num_ftrs, 512),
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
        "generic": "Generic",
        "modest_modern_fusion": "Modest-Modern Fusion",
        "y2k_revival": "Y2K Retro Revival"
    }
    
    return {
        "label": label_mapping[predicted_label],
        "probabilities": {
            "generic": round(probabilities[0], 4),
            "modest_modern_fusion": round(probabilities[1], 4),
            "y2k_revival": round(probabilities[2], 4)
        }
    }
