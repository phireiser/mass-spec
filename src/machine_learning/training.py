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
    alpha_spec_con: float = 1.0,
    contrastive_temp: float = 0.07,
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

        z_f, node_embs, node_masses = frag_set_enc(deriv_tree_batch=deriv_trees_fwd, return_nodes=True)

        z = (z_m + z_f) / 2
        z_fwd, _ = heads(z)
        # fragment-grounded decoder: intensity per fragment, scattered onto its m/z
        spec_hat = dec_spec(node_embs, node_masses, z_fwd)
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

        # Spectral contrastive: spec_hat_i must match true_i over the (mass-bucketed,
        # hence near-isobaric) other spectra in the batch. Forces predictions to encode
        # the fragment pattern that distinguishes isobaric molecules, not just mass.
        L_spec_con = 0.0
        if alpha_spec_con > 0 and spec_hat_masked.size(0) > 1:
            L_spec_con = info_nce(spec_hat_masked, true_spectrum, T=contrastive_temp)

        # learned uncertainty weighting
        L_spec_w = torch.exp(-heads.logvar_spec) * L_spec + heads.logvar_spec
        loss = (L_spec_w + beta_forbidden * L_forb + lam_cycle * L_cycle
                + alpha_diversity * L_div + alpha_spec_con * L_spec_con)
        loss.backward()
        opt.step()
        total += loss.item() * len(graph_feats)
    return total / len(loader.dataset)


def train_epoch_phase_b(
    loader: DataLoader,
    device: torch.device,
    enc_spec: Union[torch.nn.Module, torch.nn.DataParallel],
    enc_mol: Union[torch.nn.Module, torch.nn.DataParallel],
    frag_set_enc: Union[torch.nn.Module, torch.nn.DataParallel],
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
    frag_set_enc.train()
    dec_spec.train()
    heads.train()
    total = 0.0
    for batch_data in loader:
        graph_feats, _frag_graphs, _frag_masses, spec, smiles, _adj_local, deriv_trees_fwd, _ = batch_data
        spec = spec.to(device)
        opt.zero_grad()
        z_m = enc_mol(graph_feats)
        z_s = enc_spec(spec)
        _, z_bwd = heads(z_s)
        L_con_raw = info_nce(z_bwd, z_m, T=contrastive_temp)
        # fragment-grounded reconstruction from the spectrum latent, conditioned
        # on the paired molecule's fragments (available at train time)
        _z_f, node_embs, node_masses = frag_set_enc(deriv_tree_batch=deriv_trees_fwd, return_nodes=True)
        spec_hat = dec_spec(node_embs, node_masses, z_bwd)
        mask = make_parent_mass_mask_batch(smiles, mz_min, mz_max, bin_width, device=device)
        spec_hat_masked = spec_hat * mask
        L_cos = cosine_loss(spec_hat_masked, spec)
        L_wass = wasserstein_1d(spec_hat_masked, spec, bin_width=bin_width)
        L_spec = alpha_cosine * L_cos + alpha_wass * L_wass
        L_forb = (spec_hat * (1.0 - mask)).mean()
        # cycle consistency
        z_mol_cycle = enc_spec(spec_hat_masked.detach())
        L_cycle_mol = cosine_loss(z_mol_cycle, z_s)

        # NOTE: the former L_retr term was InfoNCE(z_bwd, z_m) -- identical to
        # L_con_raw above -- so it has been dropped as a duplicate. `alpha_retrieval`
        # is retained in the signature for launch-script / HPO compatibility but the
        # single (uncertainty-weighted) L_con below now carries the retrieval signal;
        # with mass-bucketed batches its in-batch negatives are near-isobaric.
        # Spectrum-to-mol consistency
        L_cycle_spec = info_nce(z_s, z_m, T=contrastive_temp)

        L_spec_w = torch.exp(-heads.logvar_spec) * L_spec + heads.logvar_spec
        L_con = torch.exp(-heads.logvar_con) * L_con_raw + heads.logvar_con
        loss = L_spec_w + lam * L_con + beta_forbidden * L_forb + lam_cycle * L_cycle_mol + lam_cycle_spec * L_cycle_spec
        loss.backward()
        opt.step()
        total += loss.item() * len(graph_feats)
    return total / len(loader.dataset)


__all__ = ["train_epoch_phase_a", "train_epoch_phase_b"]
