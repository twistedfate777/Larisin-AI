import io
import torch
import torch.nn as nn
from torchvision import models
from PIL import Image
from app.core.vision import get_shared_transforms

NUM_CLASSES = 4
CLASS_NAMES = ["modest_modern", "heritage_eco", "y2k_revival", "generic"]

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
        "modest_modern": "Modest-Modern Fusion",
        "heritage_eco": "Heritage Eco",
        "y2k_revival": "Y2K Retro Revival",
        "generic": "Generic"
    }
    
    return {
        "label": label_mapping[predicted_label],
        "probabilities": {
            "modest_modern": round(probabilities[0], 4),
            "heritage_eco": round(probabilities[1], 4),
            "y2k_revival": round(probabilities[2], 4),
            "generic": round(probabilities[3], 4)
        }
    }
