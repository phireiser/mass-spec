"""Neural network building blocks for the machine-learning pipeline."""

from torch import nn
import torch
import torch.nn.functional as F

from torch_geometric.nn import global_mean_pool, global_max_pool
from torch_geometric.nn import GCNConv, GINEConv
from torch_geometric.data import Batch

from src.machine_learning.featurizers.graph import ATOM_FEATURE_DIM


def _norm_layer(norm: str, dim: int) -> nn.Module:
    norm = norm.lower()
    if norm == "batch":
        return nn.BatchNorm1d(dim)
    if norm == "layer":
        return nn.LayerNorm(dim)
    return nn.Identity()


class ResidualMLP(nn.Module):
    """Two-layer MLP with normalization, dropout, and optional residual."""

    def __init__(self, d_in: int, d_hidden: int, d_out: int, *, dropout: float = 0.1, norm: str = "layer", residual: bool = False):
        super().__init__()
        self.residual = residual and (d_in == d_out)
        self.lin1 = nn.Linear(d_in, d_hidden)
        self.norm1 = _norm_layer(norm, d_hidden)
        self.lin2 = nn.Linear(d_hidden, d_out)
        self.norm2 = _norm_layer(norm, d_out) if norm.lower() != "batch" else nn.Identity()
        self.dropout = nn.Dropout(dropout)

    @staticmethod
    def _apply_norm(norm: nn.Module, x: torch.Tensor, training: bool) -> torch.Tensor:
        if isinstance(norm, nn.BatchNorm1d) and x.size(0) == 1 and training:
            return F.batch_norm(
                x,
                norm.running_mean,
                norm.running_var,
                norm.weight,
                norm.bias,
                training=False,
                momentum=0.0,
                eps=norm.eps,
            )
        if isinstance(norm, nn.BatchNorm1d):
            if x.dim() == 2:
                if x.size(1) == norm.num_features:
                    return norm(x)
                if x.size(0) == norm.num_features:
                    return norm(x.T).T
            elif x.dim() == 3:
                if x.size(1) == norm.num_features:
                    return norm(x)
                if x.size(2) == norm.num_features:
                    return norm(x.permute(0, 2, 1)).permute(0, 2, 1)
        return norm(x)

    def forward(self, x):
        out = self.lin1(x)
        out = self._apply_norm(self.norm1, out, self.training)
        out = F.relu(out)
        out = self.dropout(out)
        out = self.lin2(out)
        out = self._apply_norm(self.norm2, out, self.training)
        if self.residual:
            out = out + x
        return out


def mlp(d_in: int, d_hidden: int, d_out: int, *, dropout: float = 0.1, norm: str = "layer", residual: bool = False) -> nn.Module:
    return ResidualMLP(d_in, d_hidden, d_out, dropout=dropout, norm=norm, residual=residual)


class EncMol(nn.Module):
    """
    Encodes molecule graphs (MOD) into a latent vector using an edge-aware GNN.

    Uses GINEConv layers that consume the bond-order edge features, over the
    rich node features from ``GraphFeaturizerMOD`` (element one-hot + degree,
    aromaticity, incident bond order, charge, radical). This lets the encoder
    represent connectivity/isomer structure rather than collapsing to
    composition (~mass), which a 2-layer GCN over atom identity alone did.
    """

    def __init__(self, d_latent=128, in_feats: int = ATOM_FEATURE_DIM, hidden: int = 128,
                 n_layers: int = 3, dropout: float = 0.1):
        super().__init__()
        self.atom_lin = nn.Linear(in_feats, hidden)
        self.bond_lin = nn.Linear(1, hidden)
        self.convs = nn.ModuleList()
        self.norms = nn.ModuleList()
        for _ in range(n_layers):
            conv_nn = nn.Sequential(nn.Linear(hidden, hidden), nn.ReLU(), nn.Linear(hidden, hidden))
            self.convs.append(GINEConv(conv_nn))
            self.norms.append(nn.LayerNorm(hidden))
        self.dropout = nn.Dropout(dropout)
        # mean+max readout: max-pool preserves the (few) atoms whose local
        # environment distinguishes constitutional isomers, which a mean alone
        # dilutes by 1/n_atoms.
        self.out = nn.Linear(2 * hidden, d_latent)

    def forward(self, batch_graphs):
        device = next(self.parameters()).device
        # Move each graph to the model's device *before* collating: from_data_list
        # concatenates tensors, and mixing CPU + CUDA graphs (e.g. a TRAIN+VAL+TEST
        # ConcatDataset where only the training graphs were cached on GPU) makes the
        # cat inside collate throw a device-mismatch. A trailing .to() cannot fix
        # a batch that fails to build.
        batch = Batch.from_data_list([g.to(device) for g in batch_graphs])
        x = self.atom_lin(batch.x.float())
        edge_index = batch.edge_index
        ea = batch.edge_attr
        if ea is None or ea.numel() == 0:
            e = torch.zeros(edge_index.size(1), self.bond_lin.out_features, device=device)
        else:
            e = self.bond_lin(ea.float().view(-1, 1))
        for conv, norm in zip(self.convs, self.norms):
            h = F.relu(norm(conv(x, edge_index, e)))
            x = x + self.dropout(h)  # residual
        batch_idx = batch.batch.to(device)
        pooled = torch.cat([global_mean_pool(x, batch_idx), global_max_pool(x, batch_idx)], dim=-1)
        return self.out(pooled)


class EncSpec(nn.Module):
    """
    Encodes a binned mass spectrum into latent space with normalization/dropout.
    """

    def __init__(self, spectrum_bins_size, d_latent=128, *, dropout: float = 0.1, norm: str = "layer"):
        super().__init__()
        self.net = nn.Sequential(
            mlp(spectrum_bins_size, 512, 512, dropout=dropout, norm=norm, residual=True),
            mlp(512, 512, d_latent, dropout=dropout, norm=norm, residual=False),
        )

    def forward(self, spec):
        return self.net(spec.float())


class DecSpecLatent(nn.Module):
    """
    Decode a latent vector into a spectrum (no fragment bag input).
    Uses residual MLP blocks with normalization and dropout.
    """

    def __init__(self, d_in: int, spectrum_bins_size: int, *, dropout: float = 0.1, norm: str = "layer"):
        super().__init__()
        self.net = nn.Sequential(
            mlp(d_in, 512, 512, dropout=dropout, norm=norm, residual=False),
            mlp(512, 512, spectrum_bins_size, dropout=dropout, norm=norm, residual=False),
        )

    def forward(self, z: torch.Tensor) -> torch.Tensor:
        if z.dim() == 1:
            z = z.unsqueeze(0)
        return F.relu(self.net(z))


class DecSpecFragment(nn.Module):
    """
    Fragment-grounded spectrum decoder (ICEBERG-style).

    Instead of mapping a pooled latent to a free-form ``[bins]`` vector -- which
    on this data collapses to the dataset-mean spectrum regardless of input --
    this head predicts one intensity *per fragment* from that fragment's
    embedding, its mass, and a global conditioning latent, then scatters those
    intensities onto the m/z bins given by the fragments' own masses. The output
    is therefore a function of the actual fragment set (it cannot collapse to a
    constant) and every peak lands at a physically realizable mass by
    construction.
    """

    def __init__(
        self,
        d_node: int,
        d_cond: int,
        spectrum_bins_size: int,
        mz_min: float,
        mz_max: float,
        bin_width: float,
        *,
        hidden: int = 256,
        dropout: float = 0.1,
    ):
        super().__init__()
        self.bins = int(spectrum_bins_size)
        self.mz_min = float(mz_min)
        self.mz_max = float(mz_max)
        self.bin_width = float(bin_width)
        # LayerNorm inside the head: fragments are not a batch dimension, so
        # BatchNorm over a variable fragment count would be ill-defined.
        self.score = nn.Sequential(
            mlp(d_node + d_cond + 1, hidden, hidden, dropout=dropout, norm="layer", residual=False),
            nn.Linear(hidden, 1),
        )

    def forward(
        self,
        node_embs,
        node_masses,
        z_cond: torch.Tensor,
    ) -> torch.Tensor:
        """
        Parameters
        ----------
        node_embs : list[torch.Tensor]
            Length-B list of per-fragment embeddings ``[n_i, d_node]``.
        node_masses : list[torch.Tensor]
            Length-B list of per-fragment normalized masses ``[n_i]`` (mass / mz_max).
        z_cond : torch.Tensor
            Global conditioning latent ``[B, d_cond]`` (forward or backward head output).

        Returns
        -------
        torch.Tensor
            Predicted spectra ``[B, bins]`` (non-negative, per-row softmax mass over fragments).
        """
        if z_cond.dim() == 1:
            z_cond = z_cond.unsqueeze(0)
        device = z_cond.device
        rows = []
        for i in range(len(node_embs)):
            ne = node_embs[i].to(device)
            n = ne.size(0)
            if n == 0:
                rows.append(torch.zeros(self.bins, device=device))
                continue
            m = node_masses[i].to(device).reshape(n, 1)
            zc = z_cond[i].unsqueeze(0).expand(n, -1)
            feat = torch.cat([ne, zc, m], dim=-1)
            logits = self.score(feat).squeeze(-1)          # [n]
            w = torch.softmax(logits, dim=0)               # intensity share per fragment
            mz = m.squeeze(-1) * self.mz_max
            bin_idx = ((mz - self.mz_min) / self.bin_width).long().clamp_(0, self.bins - 1)
            row = torch.zeros(self.bins, device=device).index_add(0, bin_idx, w)
            rows.append(row)
        return torch.stack(rows, dim=0)


class TaskHeads(nn.Module):
    """Shared trunk heads for forward and backward tasks."""

    def __init__(self, d_latent=128, d_task=128):
        super().__init__()
        self.fwd = nn.Sequential(nn.Linear(d_latent, d_task), nn.ReLU())
        self.bwd = nn.Sequential(nn.Linear(d_latent, d_task), nn.ReLU())
        self.logvar_spec = nn.Parameter(torch.zeros(1))
        self.logvar_con = nn.Parameter(torch.zeros(1))

    def forward(self, z):
        return self.fwd(z), self.bwd(z)


__all__ = [
    "EncMol",
    "EncSpec",
    "DecSpecLatent",
    "DecSpecFragment",
    "TaskHeads",
    "ResidualMLP",
    "mlp",
]
