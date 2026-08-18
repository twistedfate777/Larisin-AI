import os
import io
import logging
import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image

from app.core.config import settings

logger = logging.getLogger(__name__)

NUM_CLASSES = 4
CLASS_NAMES = ["modest_modern", "heritage_eco", "y2k_revival", "generic"]

class CNNClassifier:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CNNClassifier, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        self.device = torch.device("cpu") # MVP is CPU bound as per spec
        self.model = self._build_model()
        self.is_loaded = False
        
        self.transform = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])
        
        if os.path.exists(settings.CNN_MODEL_PATH):
            try:
                # Load weights
                self.model.load_state_dict(torch.load(settings.CNN_MODEL_PATH, map_location=self.device, weights_only=True))
                self.model.to(self.device)
                self.model.eval()
                self.is_loaded = True
                logger.info(f"CNN Model loaded successfully from {settings.CNN_MODEL_PATH}")
            except Exception as e:
                logger.error(f"Failed to load CNN Model: {e}")
        else:
            logger.warning(f"CNN Model file not found at {settings.CNN_MODEL_PATH}. Inference will fail or return mock data.")

    def _build_model(self):
        # We must build the exact same architecture as train_cnn.py
        model = models.mobilenet_v2(weights=None)
        num_ftrs = model.classifier[1].in_features
        model.classifier[1] = nn.Sequential(
            nn.Linear(num_ftrs, 512),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(512, NUM_CLASSES)
        )
        return model

    def classify_image(self, image_bytes: bytes) -> dict:
        if not self.is_loaded:
            # Fallback for when model isn't trained yet during development
            return {
                "label": "Generic",
                "probabilities": {
                    "modest_modern": 0.25,
                    "heritage_eco": 0.25,
                    "y2k_revival": 0.25,
                    "generic": 0.25
                }
            }

        try:
            image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
            input_tensor = self.transform(image).unsqueeze(0).to(self.device)
            
            with torch.no_grad():
                output = self.model(input_tensor)
                probabilities = torch.nn.functional.softmax(output[0], dim=0).tolist()
                
            pred_idx = probabilities.index(max(probabilities))
            predicted_label = CLASS_NAMES[pred_idx]
            
            # Map for human readable label based on spec
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
        except Exception as e:
            logger.error(f"Error during image classification: {e}")
            raise

# Create a singleton instance to be imported by the API router
cnn_classifier = CNNClassifier()
