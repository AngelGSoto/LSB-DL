'''
Script to dolownd images form Legacy
Based on the Amanda' script

'''
from pathlib import Path
from astropy.table import Table
import argparse
import os
import numpy as np
import pandas as pd
import requests
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def read_table(file_name):
    try:
        if file_name.endswith('.ecsv'):
            data = Table.read(file_name, format="ascii.ecsv")
        else:
            data = pd.read_csv(file_name)
    except FileNotFoundError:
        logging.error("File not found.")
        return None
    return data

def download_legacy_image(url, file_path):
    response = requests.get(url)
    if response.status_code == 200:
        with open(file_path, 'wb') as file:
            file.write(response.content)
        logging.info(f"Downloaded: {file_path}")
    else:
        logging.error(f"Failed to download: {url}")

def download_legacy(data, out_path, radii_default="default_value_for_radii"):
    for idx, row in data.iterrows():
        try:
            ra = row["ra"]  # Update column name if needed
            dec = row["dec"]  # Update column name if needed
            name = row["ID"]  # Update column name if needed

            if 'radii' in row:
                radii = row['radii']
            else:
                radii = radii_default
        except KeyError as ke:
            logging.error(f'No column name {ke} was found. Please check your table.')
            continue

        logging.info(f"Downloading image for {name}")
        url = f"https://www.legacysurvey.org/viewer/jpeg-cutout?ra={ra}&dec={dec}&size={radii}&layer=ls-dr9&pixscale=0.262&bands=grz"
        file_name = f'{out_path}/{name}_{radii}pix.jpeg'
        download_legacy_image(url, file_name)

def main():
    parser = argparse.ArgumentParser(description="Download images from Legacy")
    parser.add_argument("table", type=str, help="Name of table, taken the prefix ")
    parser.add_argument("--Object", type=str, default=None, help="Id object of a given source")
    parser.add_argument("--legacy", action="store_true", help="make legacy images")
    parser.add_argument("--radii_default", type=str, default="default_value_for_radii", help="Default value for radii if 'radii' column is not found")

    args = parser.parse_args()
    file_name = args.table + (".ecsv" if os.path.exists(args.table + ".ecsv") else ".csv")
    data = read_table(file_name)

    if args.Object is not None:
        object_id = str(args.Object)
        mask = np.array([source in object_id for source in data["ID"]])
        data = data[mask]

    if args.legacy:
        dir_output = Path(".")
        path_legacy = dir_output / 'legacy_color_images'
        
        if not path_legacy.exists():
            path_legacy.mkdir(parents=True, exist_ok=True)
            logging.info(f"Directory '{path_legacy}' created!")
        else:
            logging.info(f"Directory '{path_legacy}' already exists!")
        
        download_legacy(data, path_legacy, args.radii_default)
        logging.info("\nDownload from Legacy Survey finished!")

if __name__ == "__main__":
    main()
