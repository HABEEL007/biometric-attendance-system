import os
import shutil
import random
from pathlib import Path

def prepare_dataset():
    base_dir = Path(__file__).resolve().parent.parent
    source_dir = base_dir / "experiments_and_datasets" / "ultimate_liveness_dataset"
    target_dir = base_dir / "dataset"
    
    # Define paths
    categories = ['real', 'spoof']
    splits = ['train', 'val', 'test']
    
    # Create target directories
    for split in splits:
        for cat in categories:
            (target_dir / split / cat).mkdir(parents=True, exist_ok=True)
            
    # Process each category
    for cat in categories:
        src_cat_dir = source_dir / cat
        if not src_cat_dir.exists():
            print(f"Source directory not found: {src_cat_dir}")
            continue
            
        # Get all image files
        files = []
        for ext in ['*.jpg', '*.png', '*.jpeg']:
            files.extend(list(src_cat_dir.glob(ext)))
            
        if not files:
            print(f"No images found in {src_cat_dir}")
            continue
            
        print(f"Found {len(files)} images in {cat}")
        
        # Shuffle
        random.seed(42)
        random.shuffle(files)
        
        # 70/15/15 split
        train_idx = int(len(files) * 0.7)
        val_idx = train_idx + int(len(files) * 0.15)
        
        train_files = files[:train_idx]
        val_files = files[train_idx:val_idx]
        test_files = files[val_idx:]
        
        print(f"Copying {len(train_files)} to train/{cat}, {len(val_files)} to val/{cat}, and {len(test_files)} to test/{cat}...")
        
        for f in train_files:
            shutil.copy2(f, target_dir / 'train' / cat / f.name)
            
        for f in val_files:
            shutil.copy2(f, target_dir / 'val' / cat / f.name)
            
        for f in test_files:
            shutil.copy2(f, target_dir / 'test' / cat / f.name)
            
    print("Dataset preparation complete!")

if __name__ == "__main__":
    prepare_dataset()
