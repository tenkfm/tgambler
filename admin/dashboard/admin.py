# admin/dashboard/admin.py

from django.contrib import admin
from django.conf import settings
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

# Инициализируем сервис один раз
firebase_service = FirebaseService(api_key=settings.FIREBASE_SERVICE_ACCOUNT_JSON)


class FirebaseChangeList(ChangeList):
    """
    ChangeList, который берёт объекты прямо из self.model_admin._items
    и не пытается ни фильтровать, ни резать их SQL-срезами.
    """
    can_show_all = False
    multi_page   = False

    def get_results(self, request):
        # Список Poxy-моделей сохранил в self.model_admin._items
        items = getattr(self.model_admin, '_items', [])
        # Заполняем то, что нужно шаблону админки
        self.result_list       = items
        self.result_count      = len(items)
        self.full_result_count = self.result_count
        self.multi_page        = False


class FirebaseAdminMixin:
    """
    Общая логика CRUD в Firebase для Django-админки.
    В наследнике указываем PYDANTIC_CLASS и PROXY_MODEL.
    """
    readonly_fields = ('id',)

    def get_changelist(self, request, **kwargs):
        return FirebaseChangeList

    def get_queryset(self, request):
        """
        Загружаем из Firebase, конвертируем в proxy-модели
        и сохраняем в self._items.
        Возвращаем пустой QuerySet — админку список берёт из _items.
        """
        pyd_class = self.PYDANTIC_CLASS
        proxy     = self.PROXY_MODEL

        # 1) Все Pydantic-объекты из Firebase
        pyd_objs = firebase_service.fetch_all(pyd_class)

        # 2) Конвертируем в Django proxy-модели
        items = [proxy(**obj.model_dump()) for obj in pyd_objs]

        # 3) Сохраняем их для ChangeList
        self._items = items

        # 4) Возвращаем пустой QuerySet (мы его не используем для рендера)
        return proxy.objects.none()

    def get_object(self, request, object_id, from_field=None):
        """
        При открытии детали запрашиваем один объект из Firebase.
        """
        pyd = firebase_service.fetch_by_id(self.PYDANTIC_CLASS, object_id)
        return self.PROXY_MODEL(**pyd.model_dump()) if pyd else None

    def save_model(self, request, obj, form, change):
        """
        При сохранении собираем Pydantic-модель и пушим в Firebase.
        """
        data = {k: v for k, v in obj.__dict__.items() if not k.startswith('_')}
        pyd_obj = self.PYDANTIC_CLASS(**data)
        if change:
            firebase_service.update(pyd_obj.id, pyd_obj)
        else:
            firebase_service.add(pyd_obj)

    def delete_model(self, request, obj):
        """
        При удалении — удаляем документ в Firebase.
        """
        firebase_service.delete(self.PYDANTIC_CLASS.collection_name(), obj.id)


@admin.register(UserInfoItem)
class UserInfoAdmin(FirebaseAdminMixin, admin.ModelAdmin):
    PYDANTIC_CLASS = UserInfo
    PROXY_MODEL    = UserInfoItem

    list_display   = (
        'tg_id', 'username', 'first_name', 'last_name',
        'language_code', 'is_premium'
    )
    search_fields  = ('username', 'first_name', 'last_name', 'tg_id')
    readonly_fields= ('id', 'tg_id', 'username')


@admin.register(WalletItem)
class WalletAdmin(FirebaseAdminMixin, admin.ModelAdmin):
    PYDANTIC_CLASS = Wallet
    PROXY_MODEL    = WalletItem

    list_display  = ('user_id', 'balance', 'currency', 'last_updated')
    search_fields = ('user_id',)


@admin.register(TransactionItem)
class TransactionAdmin(FirebaseAdminMixin, admin.ModelAdmin):
    PYDANTIC_CLASS = Transaction
    PROXY_MODEL    = TransactionItem

    list_display  = ('from_wallet_id', 'to_wallet_id', 'amount', 'currency', 'timestamp')
    search_fields = ('from_wallet_id', 'to_wallet_id')


@admin.register(TopUpRequestItem)
class TopUpRequestAdmin(FirebaseAdminMixin, admin.ModelAdmin):
    PYDANTIC_CLASS = TopUpRequest
    PROXY_MODEL    = TopUpRequestItem

    list_display   = (
        'user_id','amount','provider',
        'currency','external_id','status','created_at'
    )
    search_fields  = ('user_id','external_id','status')
    readonly_fields= ('id','created_at')

    # Убираем из формы редактирования поля info и payload
    exclude = ('info', 'payload')