"""Training loops for the machine-learning pipeline."""

from typing import Union

import torch
from torch.utils.data import DataLoader
import torch.nn.functional as F

from src.machine_learning.losses import cosine_loss, wasserstein_1d, info_nce
from src.machine_learning.spectrum import make_parent_mass_mask_batch


def train_epoch_phase_a(
    loader: DataLoader,
    device: torch.device,
    enc_mol: Union[torch.nn.Module, torch.nn.DataParallel],
    enc_spec: Union[torch.nn.Module, torch.nn.DataParallel],
    frag_set_enc: Union[torch.nn.Module, torch.nn.DataParallel],
    heads: torch.nn.Module,
    dec_spec: torch.nn.Module,
    opt: torch.optim.Optimizer,
    mz_min: float = 1.0,
    mz_max: float = 1000.0,
    bin_width: float = 1.0,
    beta_forbidden: float = 0.1,
    alpha_cosine: float = 1.0,
    alpha_wass: float = 0.5,
    lam_cycle: float = 0.1,
    alpha_diversity: float = 0.1,
) -> float:
    """
    Phase A (vocab-agnostic): molecule + fragment set -> spectrum reconstruction.
    Uses derivation_tree backend.

    Returns
    -------
    float
        Average loss over the epoch.
    """
    enc_mol.train()
    frag_set_enc.train()
    dec_spec.train()
    heads.train()
    enc_spec.eval()
    total = 0.0

    for batch_data in loader:
        graph_feats, _frag_graphs, _frag_masses, true_spectrum, smiles, _adj_local, deriv_trees_fwd, _ = batch_data

        true_spectrum = true_spectrum.to(device)
        opt.zero_grad()
        z_m = enc_mol(graph_feats)

        z_f = frag_set_enc(deriv_tree_batch=deriv_trees_fwd)

        z = (z_m + z_f) / 2
        z_fwd, _ = heads(z)
        spec_hat = dec_spec(z_fwd)
        # parent-mass mask (hard) and forbidden-region penalty
        mask = make_parent_mass_mask_batch(smiles, mz_min, mz_max, bin_width, device=device)
        spec_hat_masked = spec_hat * mask
        L_cos = cosine_loss(spec_hat_masked, true_spectrum)
        L_wass = wasserstein_1d(spec_hat_masked, true_spectrum, bin_width=bin_width)
        L_spec = alpha_cosine * L_cos + alpha_wass * L_wass
        L_forb = (spec_hat * (1.0 - mask)).mean()
        # cycle consistency
        z_spec_cycle = enc_spec(spec_hat_masked.detach())
        L_cycle = cosine_loss(z_spec_cycle, z_m)

        # Diversity loss
        L_div = 0.0
        if alpha_diversity > 0 and spec_hat_masked.size(0) > 1:
            spec_norm = F.normalize(spec_hat_masked, dim=-1)
            corr_matrix = spec_norm @ spec_norm.mT
            L_div = torch.mean((corr_matrix ** 2) * (1.0 - torch.eye(spec_hat_masked.size(0), device=device)))

        # learned uncertainty weighting
        L_spec_w = torch.exp(-heads.logvar_spec) * L_spec + heads.logvar_spec
        loss = L_spec_w + beta_forbidden * L_forb + lam_cycle * L_cycle + alpha_diversity * L_div
        loss.backward()
        opt.step()
        total += loss.item() * len(graph_feats)
    return total / len(loader.dataset)


def train_epoch_phase_b(
    loader: DataLoader,
    device: torch.device,
    enc_spec: Union[torch.nn.Module, torch.nn.DataParallel],
    enc_mol: Union[torch.nn.Module, torch.nn.DataParallel],
    heads: torch.nn.Module,
    dec_spec: torch.nn.Module,
    opt: torch.optim.Optimizer,
    mz_min: float = 1.0,
    mz_max: float = 1000.0,
    bin_width: float = 1.0,
    beta_forbidden: float = 0.1,
    lam: float = 0.1,
    alpha_cosine: float = 1.0,
    alpha_wass: float = 0.5,
    lam_cycle: float = 0.1,
    lam_cycle_spec: float = 0.1,
    contrastive_temp: float = 0.07,
    alpha_retrieval: float = 0.1,
) -> float:
    """
    Phase B (vocab-agnostic): align spectrum latent with molecular latent and
    reconstruct spectra from the spectrum latent.
    Uses derivation_tree backend.

    Returns
    -------
    float
        Average loss over the epoch.
    """
    enc_spec.train()
    enc_mol.train()
    dec_spec.train()
    heads.train()
    total = 0.0
    for batch_data in loader:
        graph_feats, _frag_graphs, _frag_masses, spec, smiles, _adj_local, _, _ = batch_data
        spec = spec.to(device)
        opt.zero_grad()
        z_m = enc_mol(graph_feats)
        z_s = enc_spec(spec)
        _, z_bwd = heads(z_s)
        L_con_raw = info_nce(z_bwd, z_m, T=contrastive_temp)
        spec_hat = dec_spec(z_bwd)
        mask = make_parent_mass_mask_batch(smiles, mz_min, mz_max, bin_width, device=device)
        spec_hat_masked = spec_hat * mask
        L_cos = cosine_loss(spec_hat_masked, spec)
        L_wass = wasserstein_1d(spec_hat_masked, spec, bin_width=bin_width)
        L_spec = alpha_cosine * L_cos + alpha_wass * L_wass
        L_forb = (spec_hat * (1.0 - mask)).mean()
        # cycle consistency
        z_mol_cycle = enc_spec(spec_hat_masked.detach())
        L_cycle_mol = cosine_loss(z_mol_cycle, z_s)

        # Retrieval ranking loss
        L_retr = 0.0
        if alpha_retrieval > 0 and z_m.size(0) > 1:
            z_bwd_norm = F.normalize(z_bwd, dim=-1)
            z_m_norm = F.normalize(z_m, dim=-1)
            sim_matrix = z_bwd_norm @ z_m_norm.T / contrastive_temp
            labels = torch.arange(z_m.size(0), device=device)
            L_retr = F.cross_entropy(sim_matrix, labels)
        # Spectrum-to-mol consistency
        L_cycle_spec = info_nce(z_s, z_m, T=contrastive_temp)

        L_spec_w = torch.exp(-heads.logvar_spec) * L_spec + heads.logvar_spec
        L_con = torch.exp(-heads.logvar_con) * L_con_raw + heads.logvar_con
        loss = L_spec_w + lam * L_con + beta_forbidden * L_forb + lam_cycle * L_cycle_mol + lam_cycle_spec * L_cycle_spec + alpha_retrieval * L_retr
        loss.backward()
        opt.step()
        total += loss.item() * len(graph_feats)
    return total / len(loader.dataset)


__all__ = ["train_epoch_phase_a", "train_epoch_phase_b"]
