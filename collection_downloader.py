import logging
from huggingface_hub import get_collection
from huggingface_hub.utils import HfHubHTTPError
from typing import List, Optional

class CollectionDownloader:
    def __init__(self, logger: logging.Logger):
        self.logger = logger

    def extract_slug_from_url(self, collection_url: str) -> str:
        """Extracts the collection slug from a full URL."""
        if collection_url.startswith("http"):
            parts = collection_url.strip("/").split("/")
            if len(parts) >= 3 and parts[-3] == "collections":
                namespace = parts[-2]
                slug_id = parts[-1]
                slug = f"{namespace}/{slug_id}"
                self.logger.debug(f"Extracted slug '{slug}' from URL.")
                return slug
        self.logger.debug(f"Input '{collection_url}' is not a full URL. Assuming it's already a slug.")
        return collection_url

    def get_model_ids_from_collection(self, collection_slug: str, use_auth: bool) -> Optional[List[str]]:
        """Fetches a collection and returns a list of all model IDs within it."""
        self.logger.info(f"🔍 Fetching collection with slug: '{collection_slug}'...")
        # if use_auth is False, token is None which forces a public request.
        # if use_auth is True, token is True which uses the cached token.
        auth_token = use_auth

        try:
            collection = get_collection(collection_slug, token=auth_token)
            self.logger.info(f"✅ Successfully fetched collection: '{collection.title}'")
            model_ids = [item.item_id for item in collection.items if item.item_type == "model"]
            if not model_ids:
                self.logger.warning("Collection was found, but it contains no models.")
                return []
            self.logger.info(f"Found {len(model_ids)} models in the collection.")
            return model_ids

        except HfHubHTTPError as e:
            if e.response.status_code == 401:
                self.logger.error("❌ Authentication failed (401 Unauthorized).")
                self.logger.error("💡 If this is a private collection, your HF token may be invalid or missing.")
            elif e.response.status_code == 404:
                self.logger.error(f"❌ Collection not found (404). Please check the URL or slug.")
            else:
                self.logger.error(f"❌ An HTTP error occurred: {e}")
            return None
        except Exception as e:
            self.logger.error(f"❌ An unexpected error occurred while fetching the collection: {e}")
            return None 