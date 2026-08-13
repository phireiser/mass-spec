"""
Derivation graph storage helpers with a small interface for SOLID compliance.

Dump files are compressed through :mod:`codec` (zstd by default, ~25x here). Two
consequences shape the code below:

* mod's API is path-based, not stream-based -- ``dg.dump()`` and ``DG.load(f=...)`` both
  take filenames -- so the ``.dmp`` is written uncompressed to node-local scratch and
  compressed from there, and is decompressed back to scratch before loading. The pickle
  has no such constraint and streams straight into/out of the compressed file.
* Reads fall back to legacy uncompressed dumps, so the pre-compression corpus still
  loads. See :mod:`codec` for why that fallback is load-bearing.
"""
from __future__ import annotations
import pickle
from typing import List, Tuple, Protocol
from pathlib import Path
import mod

from . import codec
from .dump_naming import DONE_SUFFIX, write_done_marker


class DefaultDGStore:
    def dump(
            self,
            dg: mod.DG,
            rule_list: List[mod.Rule],
            name: str,
            smiles: str,
            path: Path
            ) -> None:
        path.mkdir(parents=True, exist_ok=True)
        dmp_base = path / (name + ".dmp")
        pkl_base = path / (name + ".pkl")

        # mod writes the dump itself and only to a plain path, so it goes to scratch
        # first and is compressed from there. Scratch is node-local, which also keeps
        # the (large, uncompressed) intermediate off the shared filesystem.
        with codec.scratch_dir() as scratch:
            # dg.dump returns the filename it actually wrote; use it rather than
            # assuming, so a name mod adjusts is still the file that gets compressed.
            requested = scratch / "dg.dmp"
            written = Path(dg.dump(str(requested)) or requested)
            dmp_bytes = codec.compress_file(written, dmp_base)

        graph_database = [obj.getGMLString() for obj in dg.graphDatabase]
        rule_database = [obj.getGMLString() for obj in rule_list]
        with codec.open_write(pkl_base) as f:
            pickle.dump((smiles, graph_database, rule_database), f)
        pkl_bytes = codec.resolve_read_path(pkl_base).stat().st_size

        # A rewrite of a legacy dump would otherwise leave the uncompressed original
        # sitting beside the new compressed one, saving nothing.
        codec.drop_stale_variants(dmp_base)
        codec.drop_stale_variants(pkl_base)

        # Written last: presence of the marker == a complete dump. It carries the
        # *uncompressed* sizes because cost_model reads them as a proxy for DG size.
        write_done_marker(path, name, dmp_bytes=dmp_bytes, pkl_bytes=pkl_bytes)

    def load(
            self,
            name: str,
            path: Path
            ) -> mod.DG:
        with codec.open_read(path / (name + ".pkl")) as f:
            data = pickle.load(f)
        if len(data) == 3:
            (_smiles, graph_list, rule_list) = data
        elif len(data) == 4:
            (_smiles, graph_list, rule_list, _true_spectrum) = data
        else:
            raise RuntimeError(f"Failed to load pickle file {path / (name + '.pkl')}: Unexpected data format (length {len(data)})")
        graph_database = [mod.Graph.fromGMLString(gml) for gml in graph_list]
        rule_database = [mod.Rule.fromGMLString(gml) for gml in rule_list]

        # materialize is a no-op for a legacy uncompressed dump and expands a compressed
        # one into scratch, which it removes on exit -- safe because DG.load is eager.
        with codec.materialize(path / (name + ".dmp")) as dmp:
            return mod.DG.load(graphDatabase=graph_database, ruleDatabase=rule_database,
                               f=str(dmp))


def dump_derivation_graph(
        dg: mod.DG,
        rule_list: List[mod.Rule],
        name: str,
        smiles: str,
        path: Path | str
        ) -> None:
    store = DefaultDGStore()
    store.dump(dg, rule_list, name, smiles, Path(path))


def load_derivation_graph(
        name: str,
        path: Path | str
        ) -> mod.DG:
    store = DefaultDGStore()
    return store.load(name, Path(path))


def dump_is_complete(
        name: str,
        path: Path | str
        ) -> bool:
    """True iff a completion marker exists for ``name`` (dump finished writing)."""
    return (Path(path) / (name + DONE_SUFFIX)).exists()


def dump_is_loadable(
        name: str,
        path: Path | str
        ) -> bool:
    """True iff the dump for ``name`` under ``path`` can be fully loaded.

    Stronger (and costlier) than :func:`dump_is_complete`: it actually loads the
    graph, catching a truncated/corrupt ``.dmp``/``.pkl`` that a killed job left
    behind.
    """
    try:
        load_derivation_graph(name, path)
        return True
    except Exception:
        return False


# Public API re-exported by ``data_generation.utils``.
__all__ = [
    "dump_derivation_graph",
    "load_derivation_graph",
    "dump_is_complete",
    "dump_is_loadable",
]
