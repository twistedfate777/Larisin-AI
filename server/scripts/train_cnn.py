import os
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import models, datasets
from torch.utils.data import DataLoader
from app.core.config import settings
from app.core.vision import get_shared_transforms

NUM_CLASSES = 8

def build_model():
    model = models.mobilenet_v2(weights=models.MobileNet_V2_Weights.DEFAULT)
    
    for param in model.parameters():
        param.requires_grad = False
        
    model.classifier[1] = nn.Sequential(
        nn.Linear(model.classifier[1].in_features, 512),
        nn.ReLU(),
        nn.Dropout(0.2),
        nn.Linear(512, NUM_CLASSES)
    )
    return model

def train_model(data_dir: str, num_epochs: int = 5):
    device = torch.device("cpu")
    model = build_model().to(device)
    
    transform = get_shared_transforms()
    
    dataset = datasets.ImageFolder(data_dir, transform=transform)
    dataloader = DataLoader(dataset, batch_size=32, shuffle=True)
    
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.classifier.parameters(), lr=0.001)
    
    model.train()
    for epoch in range(num_epochs):
        running_loss = 0.0
        for inputs, labels in dataloader:
            inputs = inputs.to(device)
            labels = labels.to(device)
            
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            
            running_loss += loss.item() * inputs.size(0)
            
    os.makedirs(os.path.dirname(settings.CNN_MODEL_PATH), exist_ok=True)
    torch.save(model.state_dict(), settings.CNN_MODEL_PATH)

if __name__ == "__main__":
    DATASET_DIR = "data/raw/fashionpedia_subset/" 
    if os.path.exists(DATASET_DIR):
        train_model(DATASET_DIR)
