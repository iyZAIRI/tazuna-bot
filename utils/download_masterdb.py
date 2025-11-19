"""
Download master.mdb file from GitHub repository.
"""
import os
import requests
from pathlib import Path
import logging

logger = logging.getLogger('UmaMusumeBot.Downloader')

# GitHub raw content URLs for master.mdb files
MASTER_MDB_URL = "https://github.com/SimpleSandman/UmaMusumeMetaMasterMDB/raw/master/master/master.mdb"
META_FILE_URL = "https://github.com/SimpleSandman/UmaMusumeMetaMasterMDB/raw/master/meta"

def download_file(url: str, destination: Path) -> bool:
    """
    Download a file from a URL to a destination path.

    Args:
        url: URL to download from
        destination: Path to save the file

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        logger.info(f"Downloading from {url}...")
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()

        # Create parent directories if they don't exist
        destination.parent.mkdir(parents=True, exist_ok=True)

        # Write file in chunks
        with open(destination, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        logger.info(f"Successfully downloaded to {destination}")
        return True

    except requests.RequestException as e:
        logger.error(f"Failed to download {url}: {e}")
        return False
    except IOError as e:
        logger.error(f"Failed to write file {destination}: {e}")
        return False

def download_master_mdb(data_dir: str = "./data") -> bool:
    """
    Download the master.mdb file from GitHub.

    Args:
        data_dir: Directory to save the database file

    Returns:
        bool: True if successful, False otherwise
    """
    data_path = Path(data_dir)
    master_mdb_path = data_path / "master.mdb"
    meta_path = data_path / "meta"

    logger.info("Starting master.mdb download...")

    # Download master.mdb
    if not download_file(MASTER_MDB_URL, master_mdb_path):
        return False

    # Download meta file
    if not download_file(META_FILE_URL, meta_path):
        logger.warning("Meta file download failed, but master.mdb was successful")

    logger.info("Download complete!")
    return True

def main():
    """Main function for CLI usage."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    if download_master_mdb():
        print("✅ Successfully downloaded master.mdb!")
        print("📁 Location: ./data/master.mdb")
    else:
        print("❌ Failed to download master.mdb")
        print("Please check your internet connection and try again.")

if __name__ == "__main__":
    main()
