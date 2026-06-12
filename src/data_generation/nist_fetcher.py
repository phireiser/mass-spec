#!/usr/bin/env python3
"""
CLI tool to fetch NIST mass spectra using compound names from CSV files.
Based on the bash script but adapted for Python with name-based lookup.

Original Author Manuel Uhlir
adapted from orignial by Philipp
"""

import time
import os
import re
import argparse
from urllib.parse import quote
import requests
import pandas as pd

from project_paths import shared_path

def get_cas_from_pubchem(smiles):
    """
    Get CAS number from PubChem by searching for the SMILES string.
    Returns a single CAS string or None.
    """

    smiles = smiles.strip()
    encoded_smiles = quote(smiles, safe="")  # encode #, /, +, (, ),  etc.

    try:
        # 1. SMILES → CID
        cid_url = (
            "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/smiles/"
            f"{encoded_smiles}/cids/JSON"
        )
        cid_resp = requests.get(cid_url, timeout=30)
        cid_resp.raise_for_status()
        cid = cid_resp.json()["IdentifierList"]["CID"][0]

        # 2. CID → Synonyms
        syn_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/synonyms/JSON"
        syn_resp = requests.get(syn_url, timeout=30)
        syn_resp.raise_for_status()
        synonyms = syn_resp.json()["InformationList"]["Information"][0]["Synonym"]

    except requests.exceptions.RequestException as e:
        print(f"  Error fetching CAS number from PubChem: {e}")
        return None

    # 3. Extract CAS number pattern (xx-xx-x or xx-xxx-x etc.)
    cas_pattern = re.compile(r"^\d{2,7}-\d{2}-\d$")
    cas_numbers = [s for s in synonyms if cas_pattern.match(s)]

    if not cas_numbers:
        print("  No CAS number found in PubChem synonyms")
        return None

    cas = cas_numbers[0]
    print(f"  Found CAS number from PubChem: {cas}")
    return cas

def get_cas_number_from_name(compound_name):
    """
    Get CAS number from NIST WebBook by searching with compound name.

    Args:
        compound_name (str): Name of the compound

    Returns:
        str: CAS number if found, None otherwise
    """
    encoded_name = quote(compound_name)
    url = f"https://webbook.nist.gov/cgi/cbook.cgi?Name={encoded_name}&Units=SI&cMS=on"

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()

    except requests.exceptions.RequestException as e:
        print(f"  Error fetching CAS number: {e}")
        return None

    # Look for CAS Registry Number in the HTML
    cas_pattern = r"CAS Registry Number:</strong>\s*(\d+-\d+-\d+)"
    match = re.search(cas_pattern, response.text)

    if match:
        cas_number = match.group(1)
        print(f"  Found CAS number: {cas_number}")
        return cas_number
    else:
        print("  No CAS number found in HTML")
        return None


def fetch_nist_spectrum_simple(compound_name, compound_smiles, output_dir="spectra"):
    """
    Simple function to fetch NIST mass spectrum using two-step process:
    1. Get CAS number from name search
    2. Fetch spectrum using CAS number

    Returns:
        bool: True if successful, False otherwise
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Clean compound name for filename
    safe_name = compound_name.replace(" ", "_").replace("/", "_").replace("\\", "_")
    output_file = os.path.join(output_dir, f"{safe_name}-Mass.jdx")

    print(f"Fetching MS spectrum for compound {compound_name}")

    # Step 1: Get CAS number from name search
    print("  Step 1: Getting CAS number from name search...")
    cas_nist = get_cas_number_from_name(compound_name)
    cas_pubchem = get_cas_from_pubchem(compound_smiles)

    cas_number = cas_nist if cas_nist else cas_pubchem

    if not cas_number:
        print(f"Could not find CAS number for {compound_name}")
        return False

    # Step 2: Fetch spectrum using CAS number
    print(f"  Step 2: Fetching spectrum using CAS number {cas_number}...")
    cas_clean = cas_number.replace("-", "")
    url = f"https://webbook.nist.gov/cgi/cbook.cgi?JCAMP=C{cas_clean}&Index=0&Type=Mass"
    print(f"  URL: {url}")

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        # Check if we got actual spectral data
        if "##TITLE=" in response.text or "##JCAMP-DX=" in response.text:
            with open(output_file, "w") as f:
                f.write(response.text)
            print(f"Successfully saved spectrum to: {output_file}")
            return True
        else:
            print("No spectral data found in response")
            return False

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False


def fetch_from_csv(csv_file, output_dir="spectra", name_column="name", smiles_column="smiles"):
    """
    Fetch spectra for all compounds in a CSV file.

    Args:
        csv_file (str): Path to CSV file
        output_dir (str): Directory to save spectra
        name_column (str): Name of the column containing compound names
    """
    try:
        df = pd.read_csv(csv_file)
        print(f"Loaded {len(df)} compounds from {csv_file}")

        if name_column not in df.columns:
            print(f"Error: Column '{name_column}' not found in CSV file.")
            print(f"Available columns: {list(df.columns)}")
            return

        if smiles_column not in df.columns:
            print(f"Error: Column '{smiles_column}' not found in CSV file.")
            print(f"Available columns: {list(df.columns)}")
            return

        successful = 0
        failed = 0

        for idx, row in df.iterrows():
            compound_name = row[name_column]
            compound_smiles = row[smiles_column]

            print(f"\n--- Processing {idx + 1}/{len(df)}: {compound_name} ---")

            if fetch_nist_spectrum_simple(compound_name, compound_smiles, output_dir):
                successful += 1
            else:
                failed += 1

            # Be polite to the server
            time.sleep(1)

        print(f"  Successful: {successful}")
        print(f"  Failed: {failed}")
        print(f"  Total: {len(df)}")
        print(f"  Success rate: {successful / len(df) * 100:.1f}%")

    except FileNotFoundError:
        print(f"Error: CSV file '{csv_file}' not found.")
    except Exception as e:
        print(f"Error reading CSV file: {e}")


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="Fetch NIST mass spectra using compound names",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                                    # Fetch default compounds
  %(prog)s -c compounds.csv                   # Fetch from CSV file
  %(prog)s -c compounds.csv -o my_spectra     # Custom output directory
        """,
    )

    parser.add_argument("-c", "--csv", help="CSV file containing compound names")

    parser.add_argument(
        "-o",
        "--output",
        default=shared_path("C_NIST"),
        help="Output directory for spectra",
    )

    args = parser.parse_args()

    fetch_from_csv(args.csv, args.output)


if __name__ == "__main__":
    main()
