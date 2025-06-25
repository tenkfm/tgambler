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
# import concurrent.futures

def test(external_collection_number: int):
    url = f"https://portals-market.com/api/nfts/search?offset=0&limit=100&external_collection_number={external_collection_number}&status=listed"

    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-US,en;q=0.9,ru;q=0.8,pl;q=0.7,uk;q=0.6,it;q=0.5,es;q=0.4',
        'authorization': 'tma user=%7B%22id%22%3A311213066%2C%22first_name%22%3A%22Tony%22%2C%22last_name%22%3A%22%22%2C%22username%22%3A%22call_me_anton%22%2C%22language_code%22%3A%22en%22%2C%22is_premium%22%3Atrue%2C%22allows_write_to_pm%22%3Atrue%2C%22photo_url%22%3A%22https%3A%5C%2F%5C%2Ft.me%5C%2Fi%5C%2Fuserpic%5C%2F320%5C%2FiDZCDg1MO0UvVV_IkrhqynLi7jwsa1Kp5_JVJyAaX-U.svg%22%7D&chat_instance=-8288403347152153170&chat_type=sender&auth_date=1750702233&signature=P2LAUejm0IBXw5odsVEOmXBv5DixFmgd3krE5tcpTVvkDuYpSILWh3UG0GeVA5en3Dm-Gl-zLRl5slHXy05zDA&hash=1f24a951be98b779a42813c33bbadeab35289defe5900988f36f0a739b3b9961',
        'cache-control': 'no-cache',
        'pragma': 'no-cache',
        'priority': 'u=1, i',
        'referer': 'https://portals-market.com/',
        'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-storage-access': 'active',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        print(data)
    except requests.exceptions.HTTPError as err:
        print(f"HTTP error occurred: {err}")
    except requests.exceptions.RequestException as err:
        print(f"Request error occurred: {err}")


def load_collections() -> List[PortalsCollection]:
    """
    Fetches collections from the Portals Market API and returns them as a list of Collection objects.
    """
    url = "https://portals-market.com/api/collections?limit=200"

    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-US,en;q=0.9,ru;q=0.8,pl;q=0.7,uk;q=0.6,it;q=0.5,es;q=0.4',
        'authorization': 'tma user=%7B%22id%22%3A311213066%2C%22first_name%22%3A%22Tony%22%2C%22last_name%22%3A%22%22%2C%22username%22%3A%22call_me_anton%22%2C%22language_code%22%3A%22en%22%2C%22is_premium%22%3Atrue%2C%22allows_write_to_pm%22%3Atrue%2C%22photo_url%22%3A%22https%3A%5C%2F%5C%2Ft.me%5C%2Fi%5C%2Fuserpic%5C%2F320%5C%2FiDZCDg1MO0UvVV_IkrhqynLi7jwsa1Kp5_JVJyAaX-U.svg%22%7D&chat_instance=-8288403347152153170&chat_type=sender&auth_date=1750702233&signature=P2LAUejm0IBXw5odsVEOmXBv5DixFmgd3krE5tcpTVvkDuYpSILWh3UG0GeVA5en3Dm-Gl-zLRl5slHXy05zDA&hash=1f24a951be98b779a42813c33bbadeab35289defe5900988f36f0a739b3b9961',
        'cache-control': 'no-cache',
        'pragma': 'no-cache',
        'priority': 'u=1, i',
        'referer': 'https://portals-market.com/',
        'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-storage-access': 'active',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        api_response = CollectionAPIResponse(**data)

        collections_found = len(api_response.collections)
        print(f"Found {collections_found} collections.")

        if collections_found == 0:
            #TODO: Handle error
            print("No collections found.")
            return []

        return api_response.collections

    except requests.exceptions.HTTPError as err:
        #TODO: Handle error
        print(f"HTTP error occurred: {err}")
    except requests.exceptions.RequestException as err:
        #TODO: Handle error
        print(f"Request error occurred: {err}")

def load_collection(collection_id: str, offset: int = 0, limit: int = 20) -> List[PortalsNFT]:
    url = f"https://portals-market.com/api/nfts/search?offset={offset}&limit={limit}&collection_id={collection_id}"

    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-US,en;q=0.9,ru;q=0.8,pl;q=0.7,uk;q=0.6,it;q=0.5,es;q=0.4',
        'authorization': 'tma user=%7B%22id%22%3A311213066%2C%22first_name%22%3A%22Tony%22%2C%22last_name%22%3A%22%22%2C%22username%22%3A%22call_me_anton%22%2C%22language_code%22%3A%22en%22%2C%22is_premium%22%3Atrue%2C%22allows_write_to_pm%22%3Atrue%2C%22photo_url%22%3A%22https%3A%5C%2F%5C%2Ft.me%5C%2Fi%5C%2Fuserpic%5C%2F320%5C%2FiDZCDg1MO0UvVV_IkrhqynLi7jwsa1Kp5_JVJyAaX-U.svg%22%7D&chat_instance=-8288403347152153170&chat_type=sender&auth_date=1750703050&signature=0FT1fhjhygbmNP8w--ohhMKsIv3Am51348aHRLqLGR2RJpNEQqzlBZuLEtbOczbk00lVjCRTzU_fLrCCkB1mDg&hash=8268547a20dbe338b16d1fb2c1b600c56abde5515828c2e6ccb82cf3e352a653',
        'cache-control': 'no-cache',
        'pragma': 'no-cache',
        'priority': 'u=1, i',
        'referer': 'https://portals-market.com/collection',
        'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-storage-access': 'active',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()

        print(f"Fetched - {data}")

        try:
            nft_response = NFTResponse(**data)
        except ValidationError as e:
            print(f"⚠️ Validation error: {e}")
            for idx, item in enumerate(data.get("results", [])):
                try:
                    PortalsNFT(**item)
                except ValidationError as ve:
                    print(f"❌ Skipping NFT at index {idx} due to validation error:\n{ve}")
                    print("⚠️ Offending object:")
                    print(json.dumps(item, indent=2, ensure_ascii=False))


        results_count = len(nft_response.results)

        if results_count == 0:
            # Last page 
            return []

        return nft_response.results

    except requests.exceptions.HTTPError as err:
        print(f"HTTP error occurred: {err}")
    except requests.exceptions.RequestException as err:
        print(f"Request error occurred: {err}")

def fetch_collection_nfts(collection_id: str, limit: int = 20) -> List[PortalsNFT]:
    offset = 0
    all_nfts = []

    while True:
        print(f"🛜 Fetching NFTs for offset {offset}.")
        nfts = load_collection(collection_id=collection_id, offset=offset, limit=limit)
        if nfts is None or len(nfts) == 0:
            print("No more NFTs found or an error occurred.")
            break

        print(f"✅ Fetched {len(nfts)} NFTs from offset {offset}.")
        all_nfts.extend(nfts)
        offset += limit
        
        time.sleep(3)

    return all_nfts


# Define the function that fetches NFTs for a specific collection
def fetch_nfts_for_collection(controller, collection):
    print(f"\n------ Sync Portals Market nfts for {collection.name} 🕣 ------")
    nfts = controller.fetch_portals_nfts(collection_id=collection.portals_id)
    controller.update_remote_nfts(collection.portals_id, nfts)
    print(f"------ Sync Portals Market nfts done for {collection.name} ✅ ------\n")


if __name__ == "__main__":

    test(external_collection_number=1111)
    exit(0)

    start_time = time.time()

    print("🚀 Starting Portals Market data fetch...")
    print("Createing PortalsController instance...")
    controller = PortalsController(firebase_service=container.firebase_service)
    
    print("\n------ Sync Portals Market collections 🕣 ------")
    controller.fetch_portals_collections()
    controller.update_remote_collections()
    print("------ Sync Portals Market collections done ✅ ------\n")

    for collection in controller.portals_collections:
        fetch_nfts_for_collection(controller, collection)

    end_time = time.time()  # Засекаем время окончания
    elapsed_time = end_time - start_time  # Время работы скрипта
    print(f"Worker execution time: {elapsed_time:.2f} seconds")

    # with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    #     futures = []
        
    #     # Submit tasks to the thread pool for each collection
    #     for collection in controller.portals_collections:
    #         future = executor.submit(fetch_nfts_for_collection, controller, collection)
    #         futures.append(future)

    #     # Wait for all futures to complete
    #     for future in concurrent.futures.as_completed(futures):
    #         print("------ Sync Portals Market NFTs ✅ ------\n")
    #         pass  # You can add additional logic here to handle results or exceptions