"""Heatmap generation utilities for visualization."""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray


def generate_mock_heatmap(width: int, height: int) -> NDArray[np.float_]:
    """Generate a simple gradient heatmap to represent artifact intensity."""
    x = np.linspace(0, 1, width)
    y = np.linspace(0, 1, height)
    heatmap: NDArray[np.float_] = np.outer(y, x)
    return heatmap
