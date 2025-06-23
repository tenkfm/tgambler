from django.db import models

class UserInfoItem(models.Model):
    id               = models.CharField(max_length=100, primary_key=True)
    tg_id            = models.BigIntegerField()
    username         = models.CharField(max_length=150)
    first_name       = models.CharField(max_length=150)
    last_name        = models.CharField(max_length=150, null=True, blank=True)
    language_code    = models.CharField(max_length=10)
    photo_url        = models.URLField(max_length=500)
    is_premium       = models.BooleanField()
    tgWebAppPlatform = models.CharField(max_length=100)
    tgWebAppVersion  = models.CharField(max_length=100)
    auth_date        = models.DateTimeField()
    chat_instance    = models.CharField(max_length=200)
    signature        = models.CharField(max_length=255)
    referral_id      = models.CharField(max_length=100, blank=True)

    class Meta:
        managed = True
        verbose_name = "User Info"
        verbose_name_plural = "User Infos"

    def __str__(self):
        return f"{self.username} ({self.tg_id})"


class WalletItem(models.Model):
    id           = models.CharField(max_length=100, primary_key=True)
    user_id      = models.CharField(max_length=100)
    balance      = models.BigIntegerField()
    currency     = models.CharField(max_length=10)
    last_updated = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = True
        verbose_name = "Wallet"
        verbose_name_plural = "Wallets"

    def __str__(self):
        return f"{self.user_id} [{self.currency}] : {self.balance}"


class TransactionItem(models.Model):
    id             = models.CharField(max_length=100, primary_key=True)
    from_wallet_id = models.CharField(max_length=100)
    to_wallet_id   = models.CharField(max_length=100)
    amount         = models.BigIntegerField()
    currency       = models.CharField(max_length=10)
    timestamp      = models.DateTimeField()
    description    = models.TextField()

    class Meta:
        managed = True
        verbose_name = "Transaction"
        verbose_name_plural = "Transactions"

    def __str__(self):
        return f"{self.from_wallet_id} → {self.to_wallet_id} : {self.amount}"


class TopUpRequestItem(models.Model):
    id          = models.CharField(max_length=100, primary_key=True)
    user_id     = models.CharField(max_length=100)
    amount      = models.BigIntegerField()
    provider    = models.CharField(max_length=100)
    currency    = models.CharField(max_length=10)
    external_id = models.CharField(max_length=100)
    status      = models.CharField(max_length=20)
    payload     = models.TextField(null=True, blank=True)
    info        = models.JSONField(null=True, blank=True)
    created_at  = models.DateTimeField()

    class Meta:
        managed = True
        verbose_name = "Top-Up Request"
        verbose_name_plural = "Top-Up Requests"

    def __str__(self):
        return f"{self.user_id} : {self.amount} [{self.status}]"


# Новые прокси-модели для Case и CaseOpening

class CaseItem(models.Model):
    id        = models.CharField(max_length=100, primary_key=True)
    name      = models.CharField(max_length=200)
    cost      = models.BigIntegerField()
    image_url = models.URLField(max_length=500)
    is_active = models.BooleanField(default=True)

    class Meta:
        managed = True
        verbose_name = "Case"
        verbose_name_plural = "Cases"

    def __str__(self):
        return f"{self.name} ({self.cost/100:.2f})"
    

class CaseOpeningItem(models.Model):
    id           = models.CharField(max_length=100, primary_key=True)
    user_id      = models.CharField(max_length=100)
    case_id      = models.CharField(max_length=100)
    gift_id      = models.CharField(max_length=100)
    gift_type    = models.CharField(max_length=100)
    gift_volume  = models.BigIntegerField()
    status       = models.CharField(max_length=50)
    open_at      = models.DateTimeField()

    class Meta:
        managed = True
        verbose_name = "Case Opening"
        verbose_name_plural = "Case Openings"

    def __str__(self):
        return f"{self.user_id} opened {self.case_id} → {self.gift_id}"


class GiftItem(models.Model):
    id         = models.CharField(max_length=100, primary_key=True)
    # вместо CharField case_id добавляем ForeignKey на CaseItem
    case = models.ForeignKey(
        CaseItem,
        on_delete=models.DO_NOTHING,
        db_column="case_id",
        to_field="id",
        related_name="gifts",
        null=True,
        blank=True
    )
    name       = models.CharField(max_length=200)
    image_url  = models.URLField(max_length=500)
    background = models.URLField(max_length=500)
    volume     = models.BigIntegerField()
    prob       = models.BigIntegerField()
    is_active  = models.BooleanField(default=True)
    type       = models.CharField(max_length=20)

    class Meta:
        managed = True
        verbose_name = "Gift"
        verbose_name_plural = "Gifts"

    def __str__(self):
        return f"{self.name} ({self.case_id})"
    
class InventoryItem(models.Model):
    id               = models.CharField(max_length=100, primary_key=True)
    user_id          = models.CharField(max_length=100)
    gift_id          = models.CharField(max_length=100)
    volume_fixation  = models.BigIntegerField()
    created_at       = models.CharField(max_length=100)  # храним ISO-строку

    class Meta:
        managed = True
        verbose_name        = "Inventory"
        verbose_name_plural = "Inventories"

    def __str__(self):
        return f"{self.user_id} – {self.gift_id} @ {self.created_at}"