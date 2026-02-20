"""
Integrated Model Architecture for LiTS2017.
Handles Segmentation, Classification, and Detection.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F

class DoubleConv(nn.Module):
    """(convolution => [BN] => ReLU) * 2"""
    def __init__(self, in_channels, out_channels):
        super().__init__()
        self.double_conv = nn.Sequential(
            nn.Conv2d(in_channels, out_channels, kernel_size=3, padding=1),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
            nn.Conv2d(out_channels, out_channels, kernel_size=3, padding=1),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True)
        )

    def forward(self, x):
        return self.double_conv(x)

class IntegratedMedicalModel(nn.Module):
    """
    Integrated Model for Liver Tumor Analysis.
    Architecture: U-Net with additional heads for Classification and Detection.
    """
    def __init__(self, n_channels=1, n_classes=1):
        super(IntegratedMedicalModel, self).__init__()
        self.n_channels = n_channels
        self.n_classes = n_classes

        # Encoder (Downsampling)
        self.inc = DoubleConv(n_channels, 64)
        self.down1 = nn.Sequential(nn.MaxPool2d(2), DoubleConv(64, 128))
        self.down2 = nn.Sequential(nn.MaxPool2d(2), DoubleConv(128, 256))
        self.down3 = nn.Sequential(nn.MaxPool2d(2), DoubleConv(256, 512))
        self.down4 = nn.Sequential(nn.MaxPool2d(2), DoubleConv(512, 1024))

        # Decoder (Upsampling) for Segmentation
        self.up1 = nn.ConvTranspose2d(1024, 512, kernel_size=2, stride=2)
        self.up_conv1 = DoubleConv(1024, 512)
        self.up2 = nn.ConvTranspose2d(512, 256, kernel_size=2, stride=2)
        self.up_conv2 = DoubleConv(512, 256)
        self.up3 = nn.ConvTranspose2d(256, 128, kernel_size=2, stride=2)
        self.up_conv3 = DoubleConv(256, 128)
        self.up4 = nn.ConvTranspose2d(128, 64, kernel_size=2, stride=2)
        self.up_conv4 = DoubleConv(128, 64)
        
        # Segmentation Head
        self.outc = nn.Conv2d(64, n_classes, kernel_size=1)

        # Classification Head (Tumor Presence)
        self.global_pool = nn.AdaptiveAvgPool2d(1)
        self.classifier = nn.Sequential(
            nn.Linear(1024, 256),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(256, 1),
            nn.Sigmoid()
        )

        # Detection Head (Bounding Box [x, y, w, h])
        self.detector = nn.Sequential(
            nn.Linear(1024, 256),
            nn.ReLU(),
            nn.Linear(256, 4)  # Coordinates
        )

    def forward(self, x):
        # Encoder
        x1 = self.inc(x)
        x2 = self.down1(x1)
        x3 = self.down2(x2)
        x4 = self.down3(x3)
        x5 = self.down4(x4)

        # Segmentation Path
        up1 = self.up1(x5)
        up1 = torch.cat([up1, x4], dim=1)
        up1 = self.up_conv1(up1)
        
        up2 = self.up2(up1)
        up2 = torch.cat([up2, x3], dim=1)
        up2 = self.up_conv2(up2)
        
        up3 = self.up3(up2)
        up3 = torch.cat([up3, x2], dim=1)
        up3 = self.up_conv3(up3)
        
        up4 = self.up4(up3)
        up4 = torch.cat([up4, x1], dim=1)
        up4 = self.up_conv4(up4)
        
        segmentation = self.outc(up4)

        # Feature vector for Classification & Detection
        bottleneck = self.global_pool(x5).view(x5.size(0), -1)
        
        classification = self.classifier(bottleneck)
        detection = self.detector(bottleneck)

        return {
            "segmentation": segmentation,
            "classification": classification,
            "detection": detection
        }

if __name__ == "__main__":
    model = IntegratedMedicalModel()
    test_input = torch.randn(1, 1, 256, 256)
    output = model(test_input)
    print("✅ Model Forward Pass Successful")
    print(f"   Segmentation shape: {output['segmentation'].shape}")
    print(f"   Classification shape: {output['classification'].shape}")
    print(f"   Detection shape: {output['detection'].shape}")
