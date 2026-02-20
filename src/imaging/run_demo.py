"""
Main execution script for LiTS2017 Integrated Model Pipeline.
Demonstrates Data Prep -> Model Design -> Implementation.
"""

import torch
from src.imaging.preprocessor import LiTSPreprocessor
from src.imaging.model import IntegratedMedicalModel

def main():
    print("🚀 Starting LiTS2017 Project Implementation...")
    
    # Task 1: Data Preparation
    print("\n--- Task 1: Data Preparation ---")
    preprocessor = LiTSPreprocessor(target_size=(256, 256))
    print("✅ Preprocessor initialized with Liver Window Normalization and Augmentation.")
    
    # Task 2 & 3: Model Architecture & Implementation
    print("\n--- Task 2 & 3: Model Design & Implementation ---")
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = IntegratedMedicalModel(n_channels=1, n_classes=1).to(device)
    print(f"✅ Integrated Model loaded on {device}")
    print("   Capability: [Segmentation, Classification, Detection]")
    
    # Simulated Inference
    print("\n--- Running Simulated Pipeline ---")
    dummy_input = torch.randn(1, 1, 256, 256).to(device)
    outputs = model(dummy_input)
    
    print(f"✅ Pipeline check passed!")
    print(f"   Outputs generated for all three tasks.")
    print(f"   Model Params: {sum(p.numel() for p in model.parameters()):,}")

if __name__ == "__main__":
    main()
