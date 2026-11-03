import os
import SimpleITK as sitk
import torch
from torch.utils.data import Dataset
import numpy as np
from PIL import Image


class MyDataSet(Dataset):

    def __init__(self, image_labels, transform=None):
        self.image_labels = list(image_labels)
        self.transform = transform

    def __len__(self):
        return len(self.image_labels)

    def __getitem__(self, idx):
        img_path, label, patient_id = self.image_labels[idx]


        image = sitk.ReadImage(os.fspath(img_path))
        image = sitk.GetArrayFromImage(image)
        if image.ndim != 3 or any(size == 0 for size in image.shape):
            raise ValueError(f"Expected a non-empty 3D volume, got {image.shape}: {img_path}")

        # Preserve the existing clipping and caller-supplied intensity transform.
        image = np.clip(image, 0, 80)
        if self.transform is None:
            image_tensor = torch.from_numpy(np.ascontiguousarray(image)).float().unsqueeze(0)
        else:
            slices = []
            for slice_image in image:
                tensor = self.transform(Image.fromarray(slice_image))
                if not isinstance(tensor, torch.Tensor) or tensor.ndim != 3 or tensor.shape[0] != 1:
                    raise ValueError("Each slice transform must return a [1, H, W] tensor")
                slices.append(tensor)
            image_tensor = torch.stack(slices, dim=1).float()

        return image_tensor.contiguous(), label, patient_id


def get_nii_file_paths(directory, label):
    directory = os.fspath(directory)
    if not os.path.isdir(directory):
        raise NotADirectoryError(f"Inference directory does not exist: {directory}")
    return [
        (os.path.join(directory, name), label, name)
        for name in sorted(os.listdir(directory))
        if name.lower().endswith((".nii", ".nii.gz"))
        and os.path.isfile(os.path.join(directory, name))
    ]

def test_dataset(ais_dir, nip_dir):
    samples = get_nii_file_paths(ais_dir, 1) + get_nii_file_paths(nip_dir, 0)
    if not samples:
        raise ValueError("No .nii or .nii.gz files found in the inference directories")
    return samples


