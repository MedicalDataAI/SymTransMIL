import os
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torchvision import transforms
from sklearn.metrics import (roc_auc_score, roc_curve, auc, precision_score,recall_score, f1_score, confusion_matrix)
import matplotlib.pyplot as plt
import pandas as pd
from tqdm import tqdm
from dataset import MyDataSet, test_dataset
from model import SymmetryEnhancedResNet18
import numpy as np

def set_seed(seed):
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False


def main():

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    bs = 1

    transform = transforms.Compose([
        transforms.Grayscale(1),
        transforms.ToTensor(),
        transforms.Normalize((0.5,), (0.5,))
    ])


    ais_dir = './ais'
    sm_dir = './sm'
    val_set = test_dataset(ais_dir, sm_dir)
    val_dataset = MyDataSet(val_set, transform=transform)
    val_loader = DataLoader(val_dataset, batch_size=bs, shuffle=False, num_workers=8)

    model = SymmetryEnhancedResNet18(num_classes=2).to(device)


    model_path = ''
    model.load_state_dict(torch.load(model_path))

    save_path = ''
    os.makedirs(save_path, exist_ok=True)


    model.eval()
    val_correct = 0
    val_total = 0

    all_labels = []
    all_probs = []
    all_predictions = []
    all_sample_results = []

    with torch.no_grad():
        for images, labels, patient_ids in tqdm(val_loader, desc="Evaluating"):
            images = images.to(device)
            labels = labels.to(device)

            predictions, _, _ = model(images)

            _, predicted = torch.max(predictions, 1)

            all_labels.extend(labels.cpu().numpy())
            all_probs.extend(torch.softmax(predictions, dim=1)[:, 1].cpu().numpy())
            all_predictions.extend(predicted.cpu().numpy())

            for i in range(len(labels)):
                all_sample_results.append({
                    'Patient ID': patient_ids[i],
                    'True Label': labels[i].item(),
                    'Predicted Label': predicted[i].item(),
                    'Predicted Probability': torch.softmax(predictions[i], dim=0)[1].item(),
                })
            val_total += labels.size(0)
            val_correct += (predicted == labels).sum().item()


    val_acc = val_correct / val_total

    auc_score = roc_auc_score(all_labels, all_probs)


    fpr, tpr, _ = roc_curve(all_labels, all_probs)
    roc_auc = auc(fpr, tpr)


    plt.figure()
    plt.plot(fpr, tpr, color='darkorange', lw=2, label='ROC curve (area = %0.2f)' % roc_auc)
    plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Receiver Operating Characteristic')
    plt.legend(loc="lower right")
    plt.savefig(os.path.join(save_path, 'roc_curve.png'))


    all_predictions = np.array(all_predictions)
    all_predictions = np.where(all_predictions > 1, 1, all_predictions)

    precision = precision_score(all_labels, all_predictions)
    recall = recall_score(all_labels, all_predictions)
    f1 = f1_score(all_labels, all_predictions)
    conf_matrix = confusion_matrix(all_labels, all_predictions)

    tn, fp, fn, tp = conf_matrix.ravel()
    sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0

    summary_results = {
        'Accuracy': val_acc,
        'AUC Score': auc_score,
        'Precision': precision,
        'Recall': recall,
        'F1 Score': f1,
        'Sensitivity': sensitivity,
        'Specificity': specificity,
    }

    results_df = pd.DataFrame([summary_results])


    detailed_results_df = pd.DataFrame(all_sample_results)

    results_df.to_csv(os.path.join(save_path, 'Metrics.csv'), index=False)

    detailed_results_df.to_csv(os.path.join(save_path, 'Predictions.csv'), index=False)

if __name__ == "__main__":
    main()
