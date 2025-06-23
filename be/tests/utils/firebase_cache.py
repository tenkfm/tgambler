from typing import Type
from google.cloud.firestore_v1.base_query import FieldFilter
from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import Optional

# Abstract base class for Firebase object
class FirebaseObject(ABC, BaseModel):
    id: Optional[str] = None
    
    @staticmethod
    @abstractmethod
    def collection_name():
        pass

class CachedFirebaseService:
    def __init__(self, wrapped_service):
        self._service = wrapped_service
        # Кэш для fetch_all: ключ = (model_name, filters_repr)
        self._all_cache: dict[tuple[str, tuple[str, ...]], list[FirebaseObject]] = {}
        # Кэш для fetch_by_id: ключ = (model_name, id)
        self._by_id_cache: dict[tuple[str, str], FirebaseObject] = {}

    def fetch_all(self, *, model_class: Type[FirebaseObject], filters: list[FieldFilter] = []) -> list[FirebaseObject]:
        key = (model_class.__name__, tuple(repr(f) for f in filters))
        if key in self._all_cache:
            return self._all_cache[key]

        result = self._service.fetch_all(model_class=model_class, filters=filters)
        self._all_cache[key] = list(result)
        return result

    def fetch_by_id(self, *, model_class: Type[FirebaseObject], doc_id: str) -> FirebaseObject:
        key = (model_class.__name__, doc_id)
        if key in self._by_id_cache:
            return self._by_id_cache[key]

        result = self._service.fetch_by_id(model_class=model_class, doc_id=doc_id)
        self._by_id_cache[key] = result
        return result

    def add(self, obj: FirebaseObject) -> FirebaseObject:
        """
        Добавляем объект FirebaseObject в кэш вместо записи во внешний сервис.
        """
        model_name = obj.__class__.__name__
        obj_id = getattr(obj, 'id', None)
        # Обновляем кэш fetch_by_id
        if obj_id is not None:
            self._by_id_cache[(model_name, obj_id)] = obj

        # Обновляем кэш fetch_all: добавляем объект во все списки этого типа
        for (m_name, _), items in self._all_cache.items():
            if m_name == model_name:
                items.append(obj)

        return obj

    def reset_cache(self) -> None:
        self._all_cache.clear()
        self._by_id_cache.clear()
