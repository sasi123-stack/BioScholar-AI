"""
Medical Image Preprocessing for LiTS2017 Dataset.
Handles resizing, normalization, and augmentation.
"""

import numpy as np
import cv2
import nibabel as nib
import albumentations as A
from albumentations.pytorch import ToTensorV2
from pathlib import Path
from typing import Tuple, Dict, Any

class LiTSPreprocessor:
    """Preprocesses LiTS2017 CT scans and masks."""
    
    def __init__(self, target_size: Tuple[int, int] = (256, 256)):
        self.target_size = target_size
        
        # Define augmentation pipeline
        self.augmentation = A.Compose([
            A.HorizontalFlip(p=0.5),
            A.VerticalFlip(p=0.5),
            A.RandomRotate90(p=0.5),
            A.ElasticTransform(alpha=1, sigma=50, alpha_affine=50, p=0.2),
            A.RandomBrightnessContrast(p=0.2),
            ToTensorV2()
        ])
    
    def load_nifti(self, file_path: str) -> np.ndarray:
        """Load NIfTI file and return numpy array."""
        img = nib.load(file_path)
        return img.get_fdata()
    
    def normalize(self, volume: np.ndarray) -> np.ndarray:
        """Normalize CT Hounsfield Units (HU) to [0, 1].
        Typical liver window: [-100, 400]
        """
        min_hu = -100
        max_hu = 400
        volume = np.clip(volume, min_hu, max_hu)
        volume = (volume - min_hu) / (max_hu - min_hu)
        return volume.astype(np.float32)
    
    def resize_slice(self, image_slice: np.ndarray) -> np.ndarray:
        """Resize a single 2D slice."""
        return cv2.resize(image_slice, self.target_size, interpolation=cv2.INTER_LINEAR)
    
    def preprocess_sample(self, image_volume: np.ndarray, mask_volume: np.ndarray = None) -> Dict[str, np.ndarray]:
        """Preprocess a full 3D volume (slice by slice)."""
        processed_slices = []
        processed_masks = []
        
        for i in range(image_volume.shape[2]):
            img_slice = image_volume[:, :, i]
            img_slice = self.resize_slice(img_slice)
            img_slice = self.normalize(img_slice)
            processed_slices.append(img_slice)
            
            if mask_volume is not None:
                mask_slice = mask_volume[:, :, i]
                mask_slice = cv2.resize(mask_slice, self.target_size, interpolation=cv2.INTER_NEAREST)
                processed_masks.append(mask_slice)
        
        result = {"image": np.stack(processed_slices, axis=0)}
        if mask_volume is not None:
            result["mask"] = np.stack(processed_masks, axis=0)
            
        return result

    def apply_augmentation(self, image_slice: np.ndarray, mask_slice: np.ndarray = None):
        """Apply augmentations to a 2D slice."""
        if mask_slice is not None:
            augmented = self.augmentation(image=image_slice, mask=mask_slice)
            return augmented['image'], augmented['mask']
        else:
            augmented = self.augmentation(image=image_slice)
            return augmented['image']

if __name__ == "__main__":
    print("✅ LiTS Preprocessor module initialized")
