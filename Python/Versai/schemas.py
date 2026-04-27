from __future__ import annotations

import numpy as np
from datetime import datetime, timezone
from pydantic import BaseModel, ConfigDict, Field
from typing import List


# --- NumPy structured dtypes (exact binary match to C++ structs in UE5 NDI)
NEURON_DTYPE = np.dtype(
    [
        ("id", np.int32),
        ("activation", np.float32),
        ("x", np.float32),
        ("y", np.float32),
        ("z", np.float32),
        ("density", np.float32),
        ("gradient_mag", np.float32),
        ("layer_id", np.int32),
    ]
)

CONNECTION_DTYPE = np.dtype(
    [
        ("from_id", np.int32),
        ("to_id", np.int32),
        ("weight", np.float32),
        ("thickness", np.float32),
    ]
)


class NeuronPCGPoint(BaseModel):
    """Pydantic v2 model for a single neuron/PCG point."""

    model_config = ConfigDict(frozen=True, strict=True)

    id: int
    activation: float
    x: float
    y: float
    z: float
    density: float = Field(default=1.0, ge=0.0)
    gradient_mag: float = Field(default=0.0, ge=0.0)
    layer_id: int = Field(default=0, ge=0)


class ConnectionPCG(BaseModel):
    """Pydantic v2 model for a connection/edge (Niagara ribbon)."""

    model_config = ConfigDict(frozen=True, strict=True)

    from_id: int
    to_id: int
    weight: float
    thickness: float = Field(default=1.0, ge=0.0)


class LayerFrame(BaseModel):
    """Complete reduced frame for one training layer - ready for zero-copy shared memory."""

    model_config = ConfigDict(frozen=True, strict=True)

    frame_id: int
    layer_id: int
    neuron_count: int
    connection_count: int
    loss: float
    neurons: List[NeuronPCGPoint]
    connections: List[ConnectionPCG]
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
