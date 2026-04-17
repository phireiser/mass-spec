"""Neural network building blocks for the machine-learning pipeline."""

from torch import nn
import torch
import torch.nn.functional as F

from torch_geometric.nn import global_mean_pool
from torch_geometric.nn import GCNConv
from torch_geometric.data import Batch


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
    Encodes molecule graphs (MOD) into a latent vector using a GNN.
    """

    def __init__(self, d_latent=128):
        super().__init__()
        self.gnn1 = GCNConv(3, 64)
        self.gnn2 = GCNConv(64, d_latent)
        self.global_mean_pool = global_mean_pool

    def forward(self, batch_graphs):
        device = next(self.parameters()).device
        batch = Batch.from_data_list(batch_graphs).to(device)
        x = batch.x.float().to(device)
        edge_index = batch.edge_index.to(device)
        x1 = F.relu(self.gnn1(x, edge_index))
        x2 = self.gnn2(x1, edge_index)
        pooled = self.global_mean_pool(x2, batch.batch.to(device))
        return pooled


class EncFrag(nn.Module):
    """
    Encodes a bag-of-fragments vector into a latent embedding using a GNN.
    """

    def __init__(self, fragment_vocab_size, d_latent=128):
        super().__init__()
        if GCNConv is None:
            raise ImportError("torch_geometric is required for GNN fragment encoder.")
        self.fragment_vocab_size = fragment_vocab_size
        self.d_latent = d_latent
        self.gnn1 = GCNConv(1, 32)
        self.gnn2 = GCNConv(32, d_latent)

    def forward(self, bag: torch.Tensor) -> torch.Tensor:
        outs = []
        for i in range(bag.size(0)):
            x = bag[i].unsqueeze(-1)
            edge_index = torch.arange(self.fragment_vocab_size).unsqueeze(0).repeat(2, 1)
            x1 = F.relu(self.gnn1(x, edge_index))
            x2 = self.gnn2(x1, edge_index)
            outs.append(x2.mean(dim=0))
        return torch.stack(outs, 0)


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


class DecFrag(nn.Module):
    """
    Decodes latent embeddings back into fragment presence probabilities.
    """

    def __init__(self, d_latent, fragment_vocab_size, *, dropout: float = 0.1, norm: str = "layer"):
        super().__init__()
        self.net = mlp(d_latent, 256, fragment_vocab_size, dropout=dropout, norm=norm, residual=True)

    def forward(self, z):
        if z.dim() == 1:
            z = z.unsqueeze(0)
        return torch.sigmoid(self.net(z))


class DecSpec(nn.Module):
    """
    Decodes latent embeddings and fragment information into a predicted spectrum.
    """

    def __init__(self, d_latent, fragment_vocab_size, spectrum_bins_size, *, dropout: float = 0.1, norm: str = "layer"):
        super().__init__()
        self.net = nn.Sequential(
            mlp(d_latent + fragment_vocab_size, 512, 512, dropout=dropout, norm=norm, residual=True),
            mlp(512, 512, spectrum_bins_size, dropout=dropout, norm=norm, residual=False),
        )

    def forward(self, z, frag):
        x = torch.cat([z, frag], -1)
        return F.relu(self.net(x))


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


class TaskHeads(nn.Module):
    """Shared trunk heads for forward and backward tasks."""

    def __init__(self, d_latent=128, d_task=128):
        super().__init__()
        self.fwd = nn.Sequential(nn.Linear(d_latent, d_task), nn.ReLU())
        self.bwd = nn.Sequential(nn.Linear(d_latent, d_task), nn.ReLU())
        self.logvar_spec = nn.Parameter(torch.zeros(1))
        self.logvar_frag = nn.Parameter(torch.zeros(1))
        self.logvar_con = nn.Parameter(torch.zeros(1))

    def forward(self, z):
        return self.fwd(z), self.bwd(z)


__all__ = [
    "EncMol",
    "EncFrag",
    "EncSpec",
    "DecFrag",
    "DecSpec",
    "DecSpecLatent",
    "TaskHeads",
    "ResidualMLP",
    "mlp",
]
