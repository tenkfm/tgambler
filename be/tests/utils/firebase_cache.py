from typing import Any, Type
from google.cloud.firestore_v1.base_query import FieldFilter

class CachedFirebaseService:
    def __init__(self, wrapped_service):
        self._service = wrapped_service
        self._all_cache = {}
        self._by_id_cache = {}

    def fetch_all(self, *, model_class: Type[Any], filters: list[FieldFilter] = []):
        key = (model_class.__name__, tuple((f.field, f.op, f.value) for f in filters))
        if key in self._all_cache:
            return self._all_cache[key]

        result = self._service.fetch_all(model_class=model_class, filters=filters)
        self._all_cache[key] = result
        return result

    def fetch_by_id(self, *, model_class: Type[Any], doc_id: str):
        key = (model_class.__name__, doc_id)
        if key in self._by_id_cache:
            return self._by_id_cache[key]

        result = self._service.fetch_by_id(model_class=model_class, doc_id=doc_id)
        self._by_id_cache[key] = result
        return result

    def add(self, obj):
        # При добавлении сбрасываем кэш для этой коллекции
        self._all_cache.clear()
        return self._service.add(obj)

    def reset_cache(self):
        self._all_cache.clear()
        self._by_id_cache.clear()
