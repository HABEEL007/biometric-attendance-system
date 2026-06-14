import torch
import torch.nn as nn
import timm

class LivenessModel(nn.Module):
    """
    EfficientNet-B0 based Liveness Detection Model.
    Using EfficientNet-B0 provides a great balance of high accuracy and reasonable inference speed.
    """
    def __init__(self, dropout_rate=0.3):
        super().__init__()
        # Load pretrained EfficientNet-B0
        self.backbone = timm.create_model('efficientnet_b0', pretrained=True)
        
        # Remove the original classifier head
        in_features = self.backbone.classifier.in_features
        self.backbone.classifier = nn.Identity()
        
        # Build our custom robust liveness head
        self.classifier = nn.Sequential(
            nn.Dropout(dropout_rate),
            nn.Linear(in_features, 512),
            nn.BatchNorm1d(512),
            nn.ReLU(),
            nn.Dropout(dropout_rate),
            nn.Linear(512, 256),
            nn.BatchNorm1d(256),
            nn.ReLU(),
            nn.Linear(256, 2)  # 2 output classes: [Real, Spoof]
        )
        
    def forward(self, x):
        features = self.backbone(x)
        return self.classifier(features)

class MobileNetLiveness(nn.Module):
    """
    MobileNetV3 based Liveness Model (Alternative).
    Use this if ultra-fast real-time inference (<30ms) is required.
    """
    def __init__(self):
        super().__init__()
        self.backbone = timm.create_model('mobilenetv3_large_100', pretrained=True)
        in_features = self.backbone.classifier.in_features
        self.backbone.classifier = nn.Identity()
        self.classifier = nn.Linear(in_features, 2)
        
    def forward(self, x):
        return self.classifier(self.backbone(x))

if __name__ == "__main__":
    # Quick shape verification test
    model = LivenessModel()
    dummy_input = torch.randn(1, 3, 224, 224)
    out = model(dummy_input)
    print(f"Model output shape: {out.shape}")  # Expected: [1, 2]
