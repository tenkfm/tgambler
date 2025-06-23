# admin/dashboard/admin.py

import json
from django.contrib import admin
from django.conf import settings
from django.db import models
from django.db.models.query import QuerySet
from django.forms import Textarea
from django.contrib.admin.views.main import ChangeList

from common.services.firebase.firebase_service import FirebaseService
from common.models.domain.user       import UserInfo
from common.models.domain.wallet     import Wallet, Transaction, TopUpRequest
from .models import (
    UserInfoItem,
    WalletItem,
    TransactionItem,
    TopUpRequestItem,
)

# Инициализируем FirebaseService один раз
firebase_service = FirebaseService(api_key=settings.FIREBASE_SERVICE_ACCOUNT_JSON)


class FirebaseChangeList(ChangeList):
    can_show_all = False
    multi_page   = False

    def get_results(self, request):
        # Берём items, которые мы сохранили в mixin
        items = getattr(self.model_admin, '_items', [])
        self.result_list       = items
        self.result_count      = len(items)
        self.full_result_count = self.result_count
        self.multi_page        = False


class FirebaseAdminMixin:
    """
    Общая логика CRUD + поиск через Firebase.
    В наследнике определяются PYDANTIC_CLASS и PROXY_MODEL.
    """
    readonly_fields = ('id',)

    def get_changelist(self, request, **kwargs):
        return FirebaseChangeList

    def _load_items(self, search_term=None):
        # 1) Загрузить все объекты из Firebase
        pyd_objs = firebase_service.fetch_all(self.PYDANTIC_CLASS)

        # 2) Если есть search_term — выполнить фильтрацию по заданным полям
        if search_term:
            term = search_term.lower()
            filtered = []
            for obj in pyd_objs:
                for fld in self.search_fields:
                    val = getattr(obj, fld, "")
                    if val and term in str(val).lower():
                        filtered.append(obj)
                        break
            pyd_objs = filtered

        # 3) Конвертировать в Django-прокси
        proxy = self.PROXY_MODEL
        self._items = [proxy(**obj.model_dump()) for obj in pyd_objs]

    def get_queryset(self, request):
        # Подгружаем без фильтрации
        self._load_items()
        # Возвращаем пустой QuerySet — данные берутся из self._items
        return self.PROXY_MODEL.objects.none()

    def get_search_results(self, request, queryset, search_term):
        # При поиске — подгружаем и фильтруем
        self._load_items(search_term)
        return self.PROXY_MODEL.objects.none(), False

    def get_object(self, request, object_id, from_field=None):
        pyd_obj = firebase_service.fetch_by_id(self.PYDANTIC_CLASS, object_id)
        if not pyd_obj:
            return None
        data = pyd_obj.model_dump()

        # Если есть JSON-поля или нестандартные даты — конвертим в строки
        info = data.get('info')
        if isinstance(info, dict):
            data['info'] = {
                k: (v.isoformat() if hasattr(v, 'isoformat') else v)
                for k, v in info.items()
            }
        payload = data.get('payload')
        if payload is not None and not isinstance(payload, str):
            data['payload'] = json.dumps(payload, default=str)

        return self.PROXY_MODEL(**data)

    def save_model(self, request, obj, form, change):
        data    = {k: v for k, v in obj.__dict__.items() if not k.startswith('_')}
        pyd_obj = self.PYDANTIC_CLASS(**data)
        if change:
            firebase_service.update(pyd_obj.id, pyd_obj)
        else:
            firebase_service.add(pyd_obj)

    def delete_model(self, request, obj):
        firebase_service.delete(self.PYDANTIC_CLASS.collection_name(), obj.id)


@admin.register(UserInfoItem)
class UserInfoAdmin(FirebaseAdminMixin, admin.ModelAdmin):
    PYDANTIC_CLASS = UserInfo
    PROXY_MODEL    = UserInfoItem

    list_display    = (
        'tg_id', 'username', 'first_name', 'last_name',
        'language_code', 'is_premium'
    )
    search_fields   = ('username', 'first_name', 'last_name', 'tg_id', 'id')
    readonly_fields = ('id', 'tg_id', 'username')


@admin.register(WalletItem)
class WalletAdmin(FirebaseAdminMixin, admin.ModelAdmin):
    PYDANTIC_CLASS = Wallet
    PROXY_MODEL    = WalletItem

    list_display   = ('user_id', 'balance', 'currency', 'last_updated')
    search_fields  = ('user_id',)


@admin.register(TransactionItem)
class TransactionAdmin(FirebaseAdminMixin, admin.ModelAdmin):
    PYDANTIC_CLASS = Transaction
    PROXY_MODEL    = TransactionItem

    list_display   = ('from_wallet_id', 'to_wallet_id', 'amount', 'currency', 'timestamp')
    search_fields  = ('from_wallet_id', 'to_wallet_id')


@admin.register(TopUpRequestItem)
class TopUpRequestAdmin(FirebaseAdminMixin, admin.ModelAdmin):
    PYDANTIC_CLASS = TopUpRequest
    PROXY_MODEL    = TopUpRequestItem

    list_display    = (
        'user_id', 'amount', 'provider', 'currency',
        'external_id', 'status', 'created_at'
    )
    search_fields   = ('user_id', 'external_id', 'status')
    readonly_fields = ('id', 'created_at')
    exclude         = ('info', 'payload')
    formfield_overrides = {
        models.JSONField: {'widget': Textarea(attrs={'rows': 3, 'cols': 60})},
    }
