import sys
import os
sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..', '..')
    )
)

import requests
import time
import json

from typing import List
from models import CollectionAPIResponse, NFTResponse, PortalsNFT, PortalsCollection
from pydantic import ValidationError
from portals_controller import PortalsController
from container import container

if __name__ == "__main__":
    start_time = time.time()

    print("🚀 Starting Portals Market data fetch...")
    print("Createing PortalsController instance...")
    controller = PortalsController(firebase_service=container.firebase_service)

    groups = controller.fetch_gifts()
    

    print("\n------ Sync Portals Market nfts 🕣 ------")
    for key in groups.keys():
        print(f"Processing group with key: {key}")
        gifts = groups[key]
        nfts = controller.portals_nfts_search(external_collection_number=key)
        if not nfts:
            print(f"No NFTs found for external_collection_number: {key}")
            continue
        
        controller.update_gifts(gifts, nfts)
    
    print("------ Sync Portals Market nfts done ✅ ------\n")
