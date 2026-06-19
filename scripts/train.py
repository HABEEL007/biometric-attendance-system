import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, WeightedRandomSampler
import albumentations as A
from albumentations.pytorch import ToTensorV2
import cv2
from tqdm import tqdm
from glob import glob
from pathlib import Path
import os
from model import LivenessModel

class LivenessDataset(torch.utils.data.Dataset):
    def __init__(self, image_paths, labels, is_train=True):
        self.image_paths = image_paths
        self.labels = labels
        self.is_train = is_train
        
        # Heavy augmentations for training to prevent overfitting
        if is_train:
            self.transform = A.Compose([
                A.Resize(224, 224),
                A.RandomBrightnessContrast(brightness_limit=0.2, contrast_limit=0.2, p=0.7),
                A.GaussianBlur(blur_limit=(3, 7), p=0.3),
                A.ImageCompression(quality_range=(75, 100), p=0.4),
                A.Rotate(limit=10, p=0.4),
                A.HorizontalFlip(p=0.3),
                A.Affine(scale=(0.95, 1.05), translate_percent=(-0.05, 0.05), rotate=(-5, 5), p=0.3),
                A.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
                ToTensorV2()
            ])
        else:
            self.transform = A.Compose([
                A.Resize(224, 224),
                A.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
                ToTensorV2()
            ])
    
    def __len__(self):
        return len(self.image_paths)
    
    def __getitem__(self, idx):
        path = self.image_paths[idx]
        image = cv2.imread(str(path))
        if image is None:
            # Fallback if image is corrupted
            image = np.zeros((224, 224, 3), dtype=np.uint8)
        else:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
        augmented = self.transform(image=image)
        return augmented['image'], self.labels[idx]

def train():
    base_dir = Path(__file__).resolve().parent.parent / "dataset"
    
    # 1. Load Data Paths
    train_real = list((base_dir / 'train' / 'real').glob('*.jpg'))
    train_spoof = list((base_dir / 'train' / 'spoof').glob('*.jpg'))
    val_real = list((base_dir / 'val' / 'real').glob('*.jpg'))
    val_spoof = list((base_dir / 'val' / 'spoof').glob('*.jpg'))
    
    print(f"Train Real: {len(train_real)}, Train Spoof: {len(train_spoof)}")
    print(f"Val Real: {len(val_real)}, Val Spoof: {len(val_spoof)}")
    
    train_paths = train_real + train_spoof
    train_labels = [0]*len(train_real) + [1]*len(train_spoof)
    
    val_paths = val_real + val_spoof
    val_labels = [0]*len(val_real) + [1]*len(val_spoof)
    
    # 2. Handle Class Imbalance with Sampler (even though we balanced the data, this adds extra safety)
    class_counts = [len(train_real), len(train_spoof)]
    # Protect against divide by zero if a class is empty
    class_weights = [1.0 / c if c > 0 else 0 for c in class_counts]
    sample_weights = [class_weights[l] for l in train_labels]
    sampler = WeightedRandomSampler(sample_weights, len(sample_weights))
    
    # 3. DataLoaders
    train_dataset = LivenessDataset(train_paths, train_labels, is_train=True)
    val_dataset = LivenessDataset(val_paths, val_labels, is_train=False)
    
    train_loader = DataLoader(train_dataset, batch_size=32, sampler=sampler, num_workers=4)
    val_loader = DataLoader(val_dataset, batch_size=32, shuffle=False, num_workers=4)
    
    # 4. Initialize Model
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    
    model = LivenessModel()
    model = model.to(device)
    
    # Loss & Optimizer
    criterion = nn.CrossEntropyLoss(label_smoothing=0.1)
    optimizer = optim.AdamW(model.parameters(), lr=1e-4, weight_decay=1e-4)
    scheduler = optim.lr_scheduler.CosineAnnealingWarmRestarts(optimizer, T_0=10, T_mult=2)
    
    # 5. Training Loop
    epochs = 50
    best_val_acc = 0
    patience_counter = 0
    patience_limit = 10
    
    save_dir = Path(__file__).resolve().parent.parent / "models"
    save_dir.mkdir(exist_ok=True)
    best_model_path = save_dir / "best_liveness_model.pth"
    
    for epoch in range(epochs):
        model.train()
        train_loss = 0
        train_correct = 0
        
        # We wrap the train_loader in tqdm for a progress bar
        train_pbar = tqdm(train_loader, desc=f"Epoch {epoch+1}/{epochs} [Train]")
        for images, labels in train_pbar:
            images, labels = images.to(device), labels.to(device)
            
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            
            train_loss += loss.item()
            _, predicted = torch.max(outputs, 1)
            train_correct += (predicted == labels).sum().item()
            
            train_pbar.set_postfix({"loss": f"{loss.item():.4f}"})
            
        train_acc = train_correct / len(train_dataset)
        
        # Validation
        model.eval()
        val_correct = 0
        val_loss = 0
        
        with torch.no_grad():
            for images, labels in val_loader:
                images, labels = images.to(device), labels.to(device)
                outputs = model(images)
                loss = criterion(outputs, labels)
                val_loss += loss.item()
                
                _, predicted = torch.max(outputs, 1)
                val_correct += (predicted == labels).sum().item()
                
        val_acc = val_correct / len(val_dataset)
        val_loss_avg = val_loss / len(val_loader)
        
        print(f"-> Train Acc: {train_acc:.4f} | Val Acc: {val_acc:.4f} | Val Loss: {val_loss_avg:.4f}")
        
        # Save best model logic
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            torch.save(model.state_dict(), str(best_model_path))
            print(f"[*] New best model saved with Val Acc: {best_val_acc:.4f}")
            patience_counter = 0
        else:
            patience_counter += 1
            if patience_counter >= patience_limit:
                print("Early stopping triggered due to no improvement.")
                break
                
        scheduler.step()

    print(f"Training Complete! Best Validation Accuracy: {best_val_acc:.4f}")
    print(f"Model saved at: {best_model_path}")
    
    # 6. Final Test Evaluation
    test_real = list((base_dir / 'test' / 'real').glob('*.jpg'))
    test_spoof = list((base_dir / 'test' / 'spoof').glob('*.jpg'))
    if test_real or test_spoof:
        print("\n--- Running Final Evaluation on Test Dataset ---")
        test_paths = test_real + test_spoof
        test_labels = [0]*len(test_real) + [1]*len(test_spoof)
        test_dataset = LivenessDataset(test_paths, test_labels, is_train=False)
        test_loader = DataLoader(test_dataset, batch_size=32, shuffle=False, num_workers=4)
        
        # Load best model
        model.load_state_dict(torch.load(str(best_model_path)))
        model.eval()
        
        test_correct = 0
        with torch.no_grad():
            for images, labels in test_loader:
                images, labels = images.to(device), labels.to(device)
                outputs = model(images)
                _, predicted = torch.max(outputs, 1)
                test_correct += (predicted == labels).sum().item()
                
        test_acc = test_correct / len(test_dataset)
        print(f"Final Test Accuracy: {test_acc*100:.2f}% (on {len(test_dataset)} completely unseen images)")

if __name__ == "__main__":
    # Required for Windows multi-processing (num_workers > 0)
    import multiprocessing
    multiprocessing.freeze_support()
    train()
