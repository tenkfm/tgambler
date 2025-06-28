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

    gift_groups = controller.fetch_gifts()
    
    print("\n------ Sync Portals Market nfts 🕣 ------")
    for external_collection_number in gift_groups.keys():
        print(f"\n------ Start sync {external_collection_number} nfts 🕣 ------")
        print(f"Processing group with external_collection_number: {external_collection_number}")
        gifts = gift_groups[external_collection_number]
        nfts = controller.portals_nfts_search(external_collection_number=external_collection_number)
        if not nfts:
            print(f"No NFTs found for external_collection_number: {external_collection_number}")
            continue
        
        controller.update_gifts(gifts, nfts)
        print(f"------ Sync {external_collection_number} nfts done ✅ ------")
    
    print("n------ Sync Portals Market nfts done 🏁 ------\n")
