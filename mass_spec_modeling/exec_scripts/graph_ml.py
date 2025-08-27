"""machine learning calls"""

import mod
import sys
sys.path.append("/home/mescalin/reiserp/Nextcloud/studium/computationalScience/thesis/mol/mass_spec_modeling/src/")

from mass_spec_modeling.machine_learning.config import Cfg
from mass_spec_modeling.machine_learning.featurizers.dg_hypergraph import DGHypergraphFeaturizer
from mass_spec_modeling.machine_learning.models.encoder import GraphEncoder
from mass_spec_modeling.machine_learning.utils_mod import inspect_hg
import mass_spec_modeling.mod_fragmentation.utils as utils


def main():
    """execute"""
    molecule = mod.smiles("CCCC=O", "butanal")
    dg, _ = utils.load_derivation_graph(
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
