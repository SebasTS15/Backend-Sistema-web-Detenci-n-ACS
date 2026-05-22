from typing import Any

import numpy as np
import torch


EXPECTED_SAMPLES = 3840
EXPECTED_CHANNELS = 3


def prepare_signal(signals: list[list[float]], normalize: bool = True) -> tuple[torch.Tensor, dict[str, Any]]:
    array = np.asarray(signals, dtype=np.float32)

    if array.ndim != 2:
        raise ValueError("signals debe ser una matriz 2D con forma [muestras, canales].")

    original_shape = list(array.shape)
    array = _fit_channels(array, EXPECTED_CHANNELS)
    array = _fit_samples(array, EXPECTED_SAMPLES)

    if normalize:
        array = _normalize_per_channel(array)

    tensor = torch.from_numpy(array.T).unsqueeze(0).float()
    info = {
        "original_shape": original_shape,
        "processed_shape": [EXPECTED_SAMPLES, EXPECTED_CHANNELS],
        "normalized": normalize,
    }
    return tensor, info


def _fit_channels(array: np.ndarray, expected_channels: int) -> np.ndarray:
    current_channels = array.shape[1]
    if current_channels == expected_channels:
        return array
    if current_channels > expected_channels:
        return array[:, :expected_channels]

    padding = np.zeros((array.shape[0], expected_channels - current_channels), dtype=np.float32)
    return np.concatenate([array, padding], axis=1)


def _fit_samples(array: np.ndarray, expected_samples: int) -> np.ndarray:
    current_samples = array.shape[0]
    if current_samples == expected_samples:
        return array
    if current_samples > expected_samples:
        return array[:expected_samples, :]

    padding = np.zeros((expected_samples - current_samples, array.shape[1]), dtype=np.float32)
    return np.concatenate([array, padding], axis=0)


def _normalize_per_channel(array: np.ndarray) -> np.ndarray:
    mean = array.mean(axis=0, keepdims=True)
    std = array.std(axis=0, keepdims=True)
    std = np.where(std < 1e-6, 1.0, std)
    return (array - mean) / std
