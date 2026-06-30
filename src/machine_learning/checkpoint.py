"""Checkpoint save/load for the machine-learning pipeline.

The fragment-set encoder ``frag_set_enc`` holds the molecule encoder
``enc_mol`` as a shared submodule (``FragSetEncoderWrapper.enc_mol``), so
``enc_mol``'s weights are already nested inside ``frag_set_enc.state_dict()``
under the ``enc_mol.*`` prefix. We therefore do *not* serialize ``enc_mol``
separately: restoring ``frag_set_enc`` restores the shared ``enc_mol`` with it.
Keeping save and load in one place means the on-disk schema can't drift.
"""

from pathlib import Path
from typing import Any, Dict, Optional, Union

import torch
from torch import nn

_PathLike = Union[str, Path]


def save_checkpoint(
    path: _PathLike,
    *,
    frag_set_enc: nn.Module,
    enc_spec: nn.Module,
    dec_spec: nn.Module,
    heads: nn.Module,
    args: Optional[Dict[str, Any]] = None,
) -> None:
    """Write the model checkpoint to ``path``.

    ``enc_mol`` is intentionally absent — its weights live inside
    ``frag_set_enc`` (see module docstring).
    """
    ckpt = {
        "frag_set_enc": frag_set_enc.state_dict(),
        "enc_spec": enc_spec.state_dict(),
        "dec_spec": dec_spec.state_dict(),
        "heads": heads.state_dict(),
        "args": args or {},
    }
    torch.save(ckpt, path)


def load_checkpoint(
    path: _PathLike,
    *,
    frag_set_enc: nn.Module,
    enc_spec: nn.Module,
    dec_spec: nn.Module,
    heads: nn.Module,
    map_location: Optional[Union[str, torch.device]] = None,
    strict: bool = False,
) -> Dict[str, Any]:
    """Load a checkpoint into already-constructed modules, in place.

    Construct ``frag_set_enc`` from the same ``enc_mol`` object you intend to
    use downstream; loading ``frag_set_enc`` restores that shared ``enc_mol``
    too, so there is no separate ``enc_mol`` load.

    ``strict=False`` by default so checkpoints written by older code load
    cleanly — e.g. ones that still carry the removed ``heads.logvar_frag``
    parameter, or the now-dropped top-level ``enc_mol`` entry (simply ignored).

    Returns
    -------
    dict
        The saved ``args`` (empty dict if the checkpoint predates arg saving).
    """
    # weights_only=False: these are first-party checkpoints and ``args`` may
    # contain non-tensor objects (e.g. a Path), which weights_only=True rejects.
    ckpt = torch.load(path, map_location=map_location, weights_only=False)
    frag_set_enc.load_state_dict(ckpt["frag_set_enc"], strict=strict)
    enc_spec.load_state_dict(ckpt["enc_spec"], strict=strict)
    dec_spec.load_state_dict(ckpt["dec_spec"], strict=strict)
    heads.load_state_dict(ckpt["heads"], strict=strict)
    return ckpt.get("args", {})


__all__ = ["save_checkpoint", "load_checkpoint"]
