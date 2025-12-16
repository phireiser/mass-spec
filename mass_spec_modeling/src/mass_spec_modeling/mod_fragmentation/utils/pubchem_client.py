"""
PubChem client abstraction for CID lookup and data fetching.
"""
from typing import Optional, Dict, Any
from urllib.parse import quote
import requests

class PubChemClient:
    def __init__(self, session: Optional[requests.Session] = None, base_url: str = "https://pubchem.ncbi.nlm.nih.gov", timeout: float = 8.0):
        self.session = session or requests.Session()
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def smiles_to_cid(self, smiles: str) -> int:
        pug_pre_url = f"{self.base_url}/rest/pug/compound/smiles/"
        encoded_smiles = quote(smiles, safe='')
        url = f"{pug_pre_url}{encoded_smiles}/cids/JSON"
        resp = self.session.get(url, timeout=self.timeout)
        resp.raise_for_status()
        cids = resp.json().get('IdentifierList', {}).get('CID', [])
        if not cids:
            raise ValueError(f"No PubChem CID found for SMILES: {smiles}")
        if len(cids) > 1:
            raise RuntimeError(f"Multiple PubChem CIDs found for SMILES: {smiles} -> {cids}")
        return int(cids[0])

    def fetch_compound_view(self, cid: int) -> Dict[str, Any]:
        url = f"{self.base_url}/rest/pug_view/data/compound/{cid}/JSON/"
        resp = self.session.get(url, timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()
