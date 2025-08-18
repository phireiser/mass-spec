"""machine learning calls"""
import os
import sys
import ctypes

sys.setdlopenflags(sys.getdlopenflags() | ctypes.RTLD_GLOBAL)
# Optionally export MOD_LIB64 env var instead of hardcoding paths.
MOD_LIB = os.environ.get("MOD_LIB64", "/home/talax/xtof/local/Mod/lib64/")
if os.path.isdir(MOD_LIB) and MOD_LIB not in sys.path:
    sys.path.append(MOD_LIB)

import mod
from machine_learning.config import Cfg
from machine_learning.featurizers.dg_hypergraph import DGHypergraphFeaturizer
from machine_learning.models.encoder import GraphEncoder
from machine_learning.utils_mod import inspect_hg
import mod_fragmentation.utils as utils


def main():
    molecule = mod.smiles("CCCC=O", "butanal")
    molecule_term = utils.term_from_graph(molecule)
    dg, rule_list = utils.load_derivation_graph(
        molecule.name,
        path=("/home/mescalin/reiserp/Nextcloud/"
              "studium/computationalScience/thesis/mol/dump/")
    )
    cfg = Cfg()
    featurizer = DGHypergraphFeaturizer(cfg, GraphEncoder, GraphEncoder)
    hg = featurizer(dg)
    inspect_hg(hg)


if __name__ == "__main__":
    main()
