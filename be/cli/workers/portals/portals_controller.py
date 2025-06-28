import requests
from collections import defaultdict
from pydantic import BaseModel
from typing import List, Dict, Optional
from google.cloud.firestore_v1.base_query import FieldFilter
from common.services.firebase.firebase_service import FirebaseService
from common.models.domain.gift import PortalsNFT, Gift, GiftType

class NFTResponse(BaseModel):
    results: List[PortalsNFT]
    total_count: int

class PortalsController:
    __firebase_service: FirebaseService

    def __init__(self, firebase_service: FirebaseService):
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


    def fetch_gifts(self) -> List[Gift]:
        gifts = self.__firebase_service.fetch_all(
            model_class=Gift,
            filters=[FieldFilter('type', '==', GiftType.PORTALS_GIFT)]
        )

        # Group gifts by external_collection_number
        groups = defaultdict(list)
        for gift in gifts:
            key = getattr(gift.payload, 'external_collection_number', None)
            groups[key].append(gift)

        return groups


    def portals_nfts_search(self, external_collection_number: str) -> List[PortalsNFT]:
        """
        Fetches a single NFT by its portals_id from the Portals Market API.
        """

        url = f"https://portals-market.com/api/nfts/search?offset=0&limit=100&external_collection_number={external_collection_number}&status=listed"
        headers = self.__generate_headers(reffer='https://portals-market.com/')

        try:
            print(f"🛜 Search NFTs for {external_collection_number} from Portals Market API...")
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            api_response = NFTResponse(**data)
            return api_response.results

        except requests.exceptions.HTTPError as err:
            raise Exception(f"❌ fetch_portals_nfts_by_id HTTP error occurred: {err}")
        except requests.exceptions.RequestException as err:
            raise Exception(f"❌ fetch_portals_nfts_by_id Request error occurred: {err}")
        
    def update_gifts(self, gifts: List[Gift], nfts: List[PortalsNFT]):
        """
        Updates gifts with the provided NFTs.
        """
        updated_gifts = []
        for gift in gifts:
            if not gift.payload or not isinstance(gift.payload, PortalsNFT):
                print(f"❌ Gift {gift.id} has no valid payload.")
                continue
            
            portals_nft = next((nft for nft in nfts if nft.external_collection_number == gift.payload.external_collection_number), None)
            if not portals_nft:
                print(f"❌ No matching NFT found for gift {gift.id} with external_collection_number {gift.payload.external_collection_number}.")
                continue
            

            gift.update_payload(payload=portals_nft)
            updated_gifts.append(gift)
        
        self.__firebase_service.batch_update(updated_gifts)
        print(f"✅ Updated {len(updated_gifts)} gifts by NFTs from Portals Market API.")