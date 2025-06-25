import requests
import time
from fastapi import HTTPException, Depends
from google.cloud.firestore_v1.base_query import FieldFilter
from common.services.firebase.firebase_service import FirebaseService
from models import CollectionAPIResponse, NFTResponse, PortalsNFT, PortalsCollection

class PortalsController:
    portals_collections: list[PortalsCollection]
    __firebase_service: FirebaseService

    def __init__(self, firebase_service: FirebaseService):
        self.portals_collections = []
        self.__firebase_service = firebase_service

    def __generate_headers(self, reffer: str):
        print("📬 Generating headers for Portals Market API request.")

        return {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-US,en;q=0.9,ru;q=0.8,pl;q=0.7,uk;q=0.6,it;q=0.5,es;q=0.4',
        'authorization': 'tma user=%7B%22id%22%3A311213066%2C%22first_name%22%3A%22Tony%22%2C%22last_name%22%3A%22%22%2C%22username%22%3A%22call_me_anton%22%2C%22language_code%22%3A%22en%22%2C%22is_premium%22%3Atrue%2C%22allows_write_to_pm%22%3Atrue%2C%22photo_url%22%3A%22https%3A%5C%2F%5C%2Ft.me%5C%2Fi%5C%2Fuserpic%5C%2F320%5C%2FiDZCDg1MO0UvVV_IkrhqynLi7jwsa1Kp5_JVJyAaX-U.svg%22%7D&chat_instance=-8288403347152153170&chat_type=sender&auth_date=1750702233&signature=P2LAUejm0IBXw5odsVEOmXBv5DixFmgd3krE5tcpTVvkDuYpSILWh3UG0GeVA5en3Dm-Gl-zLRl5slHXy05zDA&hash=1f24a951be98b779a42813c33bbadeab35289defe5900988f36f0a739b3b9961',
        'cache-control': 'no-cache',
        'pragma': 'no-cache',
        'priority': 'u=1, i',
        'referer': reffer,
        'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-storage-access': 'active',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36'
    }

    def __rename_id_to_underscore_id(self, data: list[dict]) -> list[dict]:
        """
        Renames the 'id' key to '_id' in all collections.
        """
        for collection in data:
            # Для каждого словаря коллекции меняем ключ 'id' на '_id'
            if 'id' in collection:
                collection['portals_id'] = collection.pop('id')
        return data
    
    def __load_portals_nfts(self, collection_id: str, offset: int = 0, limit: int = 100) -> list[PortalsNFT]:
        """
        Fetches NFTs from the Portals Market API for a given collection ID.
        """
        url = f"https://portals-market.com/api/nfts/search?offset={offset}&limit={limit}&collection_id={collection_id}"
        headers = self.__generate_headers(reffer='https://portals-market.com/collection')

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()

            data['results'] = self.__rename_id_to_underscore_id(data['results'])

            api_response = NFTResponse(**data)
            return api_response.results

        except requests.exceptions.HTTPError as err:
            raise Exception(f"❌ load_portals_nfts HTTP error occurred: {err}")
        except requests.exceptions.RequestException as err:
            raise Exception(f"❌ load_portals_nfts Request error occurred: {err}")
        
    #
    # Collection methods
    #

    def fetch_portals_collections(self):
        """
        Fetches collections from the Portals Market API and returns them as a list of Collection objects.
        """
        url = "https://portals-market.com/api/collections?limit=200"
        headers = self.__generate_headers(reffer='https://portals-market.com/')

        try:
            print("🛜 Retrieving collections from Portals Market API...")
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()

            data['collections'] = self.__rename_id_to_underscore_id(data['collections'])

            api_response = CollectionAPIResponse(**data)

            collections_found = len(api_response.collections)
            print(f"ℹ Found {collections_found} collections.")

            if collections_found == 0:
                raise Exception("❌ No collections found.")

            self.portals_collections = api_response.collections

        except requests.exceptions.HTTPError as err:
            raise Exception(f"❌ fetch_portals_collections HTTP error occurred: {err}")
        except requests.exceptions.RequestException as err:
            raise Exception(f"❌ fetch_portals_collections Request error occurred: {err}")

    def update_remote_collections(self):
        """
        Saves the fetched collections to Firebase.
        """
        if not self.portals_collections or len(self.portals_collections) == 0:
            print("❌ No collections to save.")
            raise Exception("No collections to save.")

        print("💽 Fetching collections from Firebase to merge with fetched collections.")        
        firebase_collections = self.__firebase_service.fetch_all(PortalsCollection)

        if not firebase_collections or len(firebase_collections) == 0:
            # Add all collections to Firebase if none exist
            print("✅ No collections found in Firebase, adding all fetched collections.")
            self.__firebase_service.batch_add(objs=self.portals_collections)
            return
        
        print("⛙ Merging fetched collections with Firebase collections.")
        objects_to_add = []
        objects_to_update = []
        objects_ids_to_delete = []

        # Convert firebase collections to a set of portals_ids for easy comparison
        firebase_collections_ids = {col.portals_id for col in firebase_collections}
        # Create a set of portals_ids from self.portals_collections
        portals_collections_ids = {col.portals_id for col in self.portals_collections}
        # Find collections to delete (those in Firebase but not in the current fetched collections)
        collections_to_delete_ports_ids = firebase_collections_ids - portals_collections_ids

        for portals_collection in self.portals_collections:
            # Check if the collection already exists in Firebase
            existing_collection = next(
                (col for col in firebase_collections if col.portals_id == portals_collection.portals_id), None
            )

            if existing_collection:
                # Update existing collection
                existing_collection.merge(portals_collection)
                objects_to_update.append(existing_collection)
            else:
                # Add new collection
                objects_to_add.append(portals_collection)

        # Add delete operation for collections that are in Firebase but not in portals_collections
        for collection_id in collections_to_delete_ports_ids:
            collection_to_delete = next(
                (col for col in firebase_collections if col.portals_id == collection_id), None
            )
            if collection_to_delete:
                objects_ids_to_delete.append(collection_to_delete.id)

        print(f"💾 Starting batch update and add operations for collections.")
        self.__firebase_service.batch_add(objs=objects_to_add)
        self.__firebase_service.batch_update(objs=objects_to_update)
        self.__firebase_service.batch_delete(model_class=PortalsCollection, doc_ids=objects_ids_to_delete)
        print(f"✅ Added {len(objects_to_add)} new collections, updated {len(objects_to_update)} existing collections, and deleted {len(objects_ids_to_delete)} collections.")

    #
    # NFT methods
    #

    def fetch_portals_nfts(self, collection_id: str) -> list[PortalsNFT]:
        """
        Fetches NFTs for a given collection ID from the Portals Market API.
        """

        offset = 0
        limit = 100
        all_nfts = []

        while True:
            try:
                print(f"🛜 Fetching NFTs for collection {collection_id} from Portals Market API...")
                nfts = self.__load_portals_nfts(collection_id=collection_id, offset=offset, limit=limit)
                if len(nfts) == 0:
                    print("No more NFTs found.")
                    break
                
                all_nfts.extend(nfts)
                print(f"🧵 Fetched {len(nfts)} NFTs of collection {collection_id} from offset {offset}.")
            except Exception as e:
                print(f"❌ Error fetching NFTs: {e}")
                break
            offset += limit
            time.sleep(3)

        print(f"✅ Fetched {len(all_nfts)} NFTs of collection {collection_id}")
        return all_nfts

    def update_remote_nfts(self, collection_id: str, portals_nfts: list[PortalsNFT]):
        """
        Merges and updates NFTs in Firebase for a given collection ID.
        """

        if not portals_nfts or len(portals_nfts) == 0:
            raise Exception("❌ No NFTs to sync.")

        print("💽 Fetching NFTs from Firebase to merge with fetched NFTs.")
        firebase_nfts = self.__firebase_service.fetch_all(
            PortalsNFT,
            filters=[FieldFilter("collection_id", "==", collection_id)]
        )

        if not firebase_nfts or len(firebase_nfts) == 0:
            # Add all NFTs to Firebase if none exist
            print("✅ No NFTs found in Firebase, adding all fetched NFTs.")
            self.__firebase_service.batch_add(objs=portals_nfts)
            return

        print("⛙ Merging fetched NFTs with Firebase NFTs.")
        objects_to_add = []
        objects_to_update = []
        objects_ids_to_delete = []

        # Convert firebase collections to a set of portals_ids for easy comparison
        firebase_nfts_ids = {col.portals_id for col in firebase_nfts}
        portals_nfts_ids = {col.portals_id for col in portals_nfts}
        nfts_to_delete_ports_ids = firebase_nfts_ids - portals_nfts_ids

        for portals_nft in portals_nfts:
            # Check if the NFT already exists in Firebase
            existing_nft = next(
                (nft for nft in firebase_nfts if nft.portals_id == portals_nft.portals_id), None
            )

            if existing_nft:
                # Update existing NFT
                existing_nft.merge(portals_nft)
                objects_to_update.append(existing_nft)
            else:
                # Add new NFT
                objects_to_add.append(portals_nft)

        # Add delete operation for nfts that are in Firebase but not in portals_nfts
        for nft_id in nfts_to_delete_ports_ids:
            nft_to_delete = next(
                (col for col in firebase_nfts if col.portals_id == nft_id), None
            )
            if nft_to_delete:
                objects_ids_to_delete.append(nft_to_delete.id)

        print(f"💾 Starting batch update and add operations for NFTs.")
        self.__firebase_service.batch_add(objs=objects_to_add)
        self.__firebase_service.batch_update(objs=objects_to_update)
        self.__firebase_service.batch_delete(model_class=PortalsNFT, doc_ids=objects_ids_to_delete)
        print(f"✅ Added {len(objects_to_add)} new nfts, updated {len(objects_to_update)} existing nfts, and deleted {len(objects_ids_to_delete)} collections.")