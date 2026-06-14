import os
import shutil
import cv2
import numpy as np
from pathlib import Path
from glob import glob
from sklearn.model_selection import GroupShuffleSplit
import albumentations as A
import random

def get_group_id(filename):
    """Extracts a unique group ID to prevent data leakage."""
    if filename.startswith('vid_'):
        # Format: vid_real_0_frame_20.jpg -> group is 'vid_real_0'
        parts = filename.split('_')
        return f"{parts[0]}_{parts[1]}_{parts[2]}"
    elif '_' in filename:
        # Oulu-NPU Format: 1_1_36_1_1.jpg -> Subject ID is the 3rd element '36'
        parts = filename.split('_')
        if len(parts) >= 3:
            return f"oulu_subject_{parts[2]}"
    
    # Fallback if unknown format (treat as individual group)
    return filename

def perform_group_split(image_paths, labels, test_size=0.15, val_size=0.15):
    """Splits data ensuring no group crosses between splits."""
    groups = [get_group_id(Path(p).name) for p in image_paths]
    
    # 1. Split into (Train + Val) and Test
    gss = GroupShuffleSplit(n_splits=1, test_size=test_size, random_state=42)
    train_val_idx, test_idx = next(gss.split(image_paths, labels, groups=groups))
    
    train_val_paths = [image_paths[i] for i in train_val_idx]
    train_val_labels = [labels[i] for i in train_val_idx]
    train_val_groups = [groups[i] for i in train_val_idx]
    
    test_paths = [image_paths[i] for i in test_idx]
    test_labels = [labels[i] for i in test_idx]
    
    # Calculate what percentage of (Train + Val) should be Val to get overall 15%
    # If test is 0.15, train_val is 0.85. To get val=0.15 overall, val ratio of remaining = 0.15 / 0.85 ≈ 0.176
    val_ratio = val_size / (1.0 - test_size)
    
    # 2. Split (Train + Val) into Train and Val
    gss2 = GroupShuffleSplit(n_splits=1, test_size=val_ratio, random_state=42)
    train_idx, val_idx = next(gss2.split(train_val_paths, train_val_labels, groups=train_val_groups))
    
    train_paths = [train_val_paths[i] for i in train_idx]
    train_labels = [train_val_labels[i] for i in train_idx]
    
    val_paths = [train_val_paths[i] for i in val_idx]
    val_labels = [train_val_labels[i] for i in val_idx]
    
    return train_paths, train_labels, val_paths, val_labels, test_paths, test_labels

def augment_to_target(train_dir, class_name, target_count=2500):
    """Augments images in the directory to reach the exact target count."""
    class_dir = Path(train_dir) / class_name
    images = list(class_dir.glob("*.jpg"))
    current_count = len(images)
    
    if current_count == 0:
        return
        
    print(f"[{class_name.upper()}] Initial train count: {current_count}. Target: {target_count}")
    
    if current_count >= target_count:
        # Downsample
        images_to_remove = random.sample(images, current_count - target_count)
        for img in images_to_remove:
            img.unlink()
        print(f"[{class_name.upper()}] Downsampled to {target_count}")
        return

    # Augment
    augmentations = A.Compose([
        A.RandomBrightnessContrast(brightness_limit=0.2, contrast_limit=0.2, p=0.7),
        A.GaussNoise(var_limit=(10.0, 50.0), p=0.3),
        A.ImageCompression(quality_lower=70, quality_upper=100, p=0.5),
        A.Rotate(limit=10, border_mode=cv2.BORDER_CONSTANT, p=0.5),
        A.HorizontalFlip(p=0.3),
        A.ShiftScaleRotate(shift_limit=0.05, scale_limit=0.05, rotate_limit=5, p=0.4),
        A.CLAHE(clip_limit=2.0, tile_grid_size=(8,8), p=0.3),
    ])
    
    needed = target_count - current_count
    
    for i in range(needed):
        img_path = images[i % current_count]
        img = cv2.imread(str(img_path))
        if img is None:
            continue
            
        augmented = augmentations(image=img)['image']
        out_name = f"aug_{i:04d}_{img_path.name}"
        cv2.imwrite(str(class_dir / out_name), augmented)
        
    print(f"[{class_name.upper()}] Augmented {needed} images. Final train count: {len(list(class_dir.glob('*.jpg')))}")

def prepare_dataset():
    base_dir = Path(r"c:\Users\habee\Desktop\FRL_DL")
    source_dir = base_dir / "ultimate_liveness_dataset"
    final_dir = base_dir / "dataset"
    
    real_images = list((source_dir / "real").glob("*.jpg"))
    spoof_images = list((source_dir / "spoof").glob("*.jpg"))
    
    all_paths = real_images + spoof_images
    all_labels = ["real"] * len(real_images) + ["spoof"] * len(spoof_images)
    
    print(f"Total source images: {len(all_paths)} (Real: {len(real_images)}, Spoof: {len(spoof_images)})")
    
    # 1. Perform Group Split
    train_p, train_l, val_p, val_l, test_p, test_l = perform_group_split(all_paths, all_labels)
    
    print(f"Split sizes -> Train: {len(train_p)}, Val: {len(val_p)}, Test: {len(test_p)}")
    
    # 2. Copy files to structured directories
    splits = {
        'train': (train_p, train_l),
        'val': (val_p, val_l),
        'test': (test_p, test_l)
    }
    
    if final_dir.exists():
        shutil.rmtree(final_dir)
    
    for split_name, (paths, labels) in splits.items():
        for path, label in zip(paths, labels):
            dest_dir = final_dir / split_name / label
            dest_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, dest_dir / path.name)
            
    # 3. Balance Training Set Only
    print("\nBalancing Training Set to 2500 images per class...")
    augment_to_target(final_dir / "train", "real", 2500)
    augment_to_target(final_dir / "train", "spoof", 2500)
    
    print("\nDataset Preparation Complete!")
    print(f"Final directory structure saved at: {final_dir}")

if __name__ == "__main__":
    prepare_dataset()
