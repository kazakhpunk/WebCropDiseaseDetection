import torch
import torch.nn as nn
from torchvision.models import resnet18

class Model(nn.Module):
    """
    Model class using ResNet18 architecture for crop disease classification.
    This matches the model architecture from your notebook.
    """
    def __init__(self, num_classes=42):  # Change from 30 to 42 to match pre-trained weights
        super(Model, self).__init__()
        
        # Load the pretrained ResNet18 model
        self.model = resnet18(pretrained=True)
        
        # Replace the final fully connected layer with a new one
        # The input features to the final layer are 512 for ResNet18
        in_features = self.model.fc.in_features
        self.model.fc = nn.Linear(in_features, num_classes)
        
    def forward(self, x):
        """Forward pass through the network"""
        return self.model(x)