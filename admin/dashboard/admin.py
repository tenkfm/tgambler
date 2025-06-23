# admin/dashboard/admin.py

import json
from django import forms
from django.contrib import admin
from django.conf import settings
from django.db import models
from django.db.models.query import QuerySet
from django.forms import Textarea
from django.contrib.admin.views.main import ChangeList

from common.services.firebase.firebase_service import FirebaseService
from common.models.domain.user       import UserInfo
from common.models.domain.wallet     import Wallet, Transaction, TopUpRequest
from common.models.domain.case      import Case, CaseOpening
from common.models.domain.gift      import Gift
from common.models.domain.inventory import Inventory

from .models import (
    UserInfoItem,
    WalletItem,
    TransactionItem,
    TopUpRequestItem,
    CaseItem,
    CaseOpeningItem,
    GiftItem,
    InventoryItem
)

firebase_service = FirebaseService(api_key=settings.FIREBASE_SERVICE_ACCOUNT_JSON)


class FirebaseChangeList(ChangeList):
    can_show_all = False
    multi_page   = False

    def get_results(self, request):
        items = getattr(self.model_admin, '_items', [])
        self.result_list       = items
        self.result_count      = len(items)
        self.full_result_count = self.result_count
        self.multi_page        = False


class FirebaseAdminMixin:
    readonly_fields = ('id',)

    def get_changelist(self, request, **kwargs):
        return FirebaseChangeList

    def _load_items(self, search_term=None):
        pyd_objs = firebase_service.fetch_all(self.PYDANTIC_CLASS)

        if search_term:
            term = search_term.lower()
            pyd_objs = [
                obj for obj in pyd_objs
                if any(
                    term in str(getattr(obj, fld, "")).lower()
                    for fld in self.search_fields
                )
            ]

        proxy = self.PROXY_MODEL
        self._items = [proxy(**obj.model_dump()) for obj in pyd_objs]

    def get_queryset(self, request):
        self._load_items()
        return self.PROXY_MODEL.objects.none()

    def get_search_results(self, request, queryset, search_term):
        self._load_items(search_term)
        return self.PROXY_MODEL.objects.none(), False

    def get_object(self, request, object_id, from_field=None):
        """
        Загружает один объект из Firebase и превращает в Django-модель.
        НЕ конвертируем все datetime в строки!
        Только поля info/payload, если они есть.
        """
        pyd_obj = firebase_service.fetch_by_id(self.PYDANTIC_CLASS, object_id)
        if not pyd_obj:
            return None

        data = pyd_obj.model_dump()

        # Все остальные поля (включая datetime) оставляем как есть,
        # чтобы Django понял их как datetime и не пытался вызвать .utcoffset() на строке.
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
    list_display   = ('tg_id','username','first_name','last_name','language_code','is_premium')
    search_fields  = ('username','first_name','last_name','tg_id')
    readonly_fields= ('id','tg_id','username')


@admin.register(WalletItem)
class WalletAdmin(FirebaseAdminMixin, admin.ModelAdmin):
    PYDANTIC_CLASS = Wallet
    PROXY_MODEL    = WalletItem
    list_display   = ('user_id','balance','currency','last_updated')
    search_fields  = ('user_id',)


@admin.register(TransactionItem)
class TransactionAdmin(FirebaseAdminMixin, admin.ModelAdmin):
    PYDANTIC_CLASS = Transaction
    PROXY_MODEL    = TransactionItem
    list_display   = ('from_wallet_id','to_wallet_id','amount','currency','timestamp')
    search_fields  = ('from_wallet_id','to_wallet_id')


@admin.register(TopUpRequestItem)
class TopUpRequestAdmin(FirebaseAdminMixin, admin.ModelAdmin):
    PYDANTIC_CLASS = TopUpRequest
    PROXY_MODEL    = TopUpRequestItem
    list_display   = ('user_id','amount','provider','currency','external_id','status','created_at')
    search_fields  = ('user_id','external_id','status')
    readonly_fields= ('id','created_at')
    exclude        = ('info','payload')
    formfield_overrides = {
        models.JSONField: {'widget': Textarea(attrs={'rows':3,'cols':60})},
    }


@admin.register(CaseItem)
class CaseAdmin(FirebaseAdminMixin, admin.ModelAdmin):
    PYDANTIC_CLASS = Case
    PROXY_MODEL    = CaseItem
    list_display   = ('name','costf','is_active')
    search_fields  = ('name',)
    readonly_fields= ('id',)

    # costf() — метод Pydantic, можно показать его в списке:
    def costf(self, obj):
        return obj.cost / 100.0
    costf.short_description = 'Cost (USD)'


@admin.register(CaseOpeningItem)
class CaseOpeningAdmin(FirebaseAdminMixin, admin.ModelAdmin):
    PYDANTIC_CLASS = CaseOpening
    PROXY_MODEL    = CaseOpeningItem
    list_display   = ('user_id','case_id','gift_id','gift_type','gift_volume','status','open_at')
    search_fields  = ('user_id','case_id','gift_id','status')
    readonly_fields= ('id','open_at')

    # Преобразуем gift_volume в человеческий вид
    def gift_volumef(self, obj):
        return obj.gift_volume / 100.0
    gift_volumef.short_description = 'Gift Vol.'

@admin.register(GiftItem)
class GiftAdmin(FirebaseAdminMixin, admin.ModelAdmin):
    PYDANTIC_CLASS = Gift
    PROXY_MODEL    = GiftItem

    list_display   = ('case_id','name','volumef','probf','is_active','type')
    search_fields  = ('name','case_id')
    readonly_fields= ('id',)

    def volumef(self, obj):
        return obj.volume / 100.0
    volumef.short_description = 'Volume'

    def probf(self, obj):
        return obj.prob / 100.0
    probf.short_description = 'Probability'

    def save_model(self, request, obj, form, change):
        # собираем данные
        data = {k: v for k, v in obj.__dict__.items() if not k.startswith('_')}

        # нормализуем поле type:
        raw = data.get('type')
        if isinstance(raw, str):
            # если пришло "GiftType.GIFT" или "GIFT", оставляем только после точки
            data['type'] = raw.split('.')[-1]
        # либо можно явно в Enum:
        # data['type'] = GiftType(data['type']).value

        # создаём и сохраняем Pydantic-объект
        pyd = self.PYDANTIC_CLASS(**data)
        if change:
            firebase_service.update(pyd.id, pyd)
        else:
            firebase_service.add(pyd)

@admin.register(InventoryItem)
class InventoryAdmin(FirebaseAdminMixin, admin.ModelAdmin):
    PYDANTIC_CLASS = Inventory
    PROXY_MODEL    = InventoryItem

    list_display   = ('user_id', 'gift_id', 'volume_fixation', 'created_at')
    search_fields  = ('user_id', 'gift_id')
    readonly_fields= ('id',)