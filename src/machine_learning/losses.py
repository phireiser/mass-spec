"""Loss functions and similarity metrics for the machine-learning pipeline."""

import torch
import torch.nn.functional as F


def cosine_loss(x, y):
    """
    Computes 1 - mean cosine similarity between two tensors.

    Parameters
    ----------
    x, y : torch.Tensor
        Input tensors of identical shape.

    Returns
    -------
    torch.Tensor
        Scalar loss value.
    """
    x_n = F.normalize(x, dim=-1)
    y_n = F.normalize(y, dim=-1)
    return 1.0 - (x_n * y_n).sum(dim=-1).mean()


def wasserstein_1d(pred: torch.Tensor, target: torch.Tensor, bin_width: float = 1.0) -> torch.Tensor:
    """1D Wasserstein/EMD for spectra assuming bins are ordered along m/z.

    Computes mean absolute cumulative difference scaled by bin_width.

    Parameters
    ----------
    pred : torch.Tensor
        Predicted spectrum [N, spectrum_bins].
    target : torch.Tensor
        Target spectrum [N, spectrum_bins].
    bin_width : float
        Width of each m/z bin.

    Returns
    -------
    torch.Tensor
        Scalar loss value.
    """
    pred_cum = torch.cumsum(pred, dim=-1)
    target_cum = torch.cumsum(target, dim=-1)
    return (torch.abs(pred_cum - target_cum).mean(dim=-1) * bin_width).mean()


def info_nce(z_q, z_k, T=0.07):
    """
    InfoNCE contrastive loss between query and key embeddings.

    Parameters
    ----------
    z_q, z_k : torch.Tensor
        Query and key embeddings of shape [N, d].
    T : float
        Temperature scaling factor.

    Returns
    -------
    torch.Tensor
        Scalar contrastive loss.
    """
    z_q = F.normalize(z_q, dim=-1)
    z_k = F.normalize(z_k, dim=-1)
    logits = z_q @ z_k.T / T
    labels = torch.arange(z_q.size(0), device=z_q.device)
    return F.cross_entropy(logits, labels)


def jaccard_binary(a, b, eps=1e-6):
    """
    Computes Jaccard similarity between two binary fragment vectors.

    Parameters
    ----------
    a, b : torch.Tensor
        Binary or count-based vectors.
    eps : float
        Small value to avoid division by zero.

    Returns
    -------
    torch.Tensor
        Jaccard similarity.
    """
    inter = (a * b).sum(dim=-1)
    union = (a + b - a * b).sum(dim=-1) + eps
    return inter / union


__all__ = ["cosine_loss", "wasserstein_1d", "info_nce", "jaccard_binary"]
