from django.shortcuts import render, redirect
import uuid
import math
from functools import reduce
from .models import ModelWrapper
from operator import attrgetter
from .container import container
from enum import Enum
from typing import Iterable, Tuple, List
from common.models.domain.user import UserInfo
from common.models.domain.wallet import Wallet, Transaction, TopUpRequest
from common.models.domain.case import CaseOpening, Case
from common.models.domain.gift import Gift, PortalsNFT, GiftType, TONReward
from google.cloud.firestore_v1.base_query import FieldFilter
from .models import build_form_class, save_object_from_form
from .controllers.portals_controller import PortalsController

def home(request):
    return render(request, "app/home.html")

#
# Users
#
def users(request):
    users = container.firebase_service.fetch_all(UserInfo)
    wrapper = ModelWrapper(
        UserInfo,
        include_fields=['id', 'tg_id', 'username', 'first_name', 'auth_date', 'is_premium']
    )
    cols = wrapper.get_table_columns()
    rows = wrapper.get_table_data(users)
    return render(request, 'app/users.html', {
        'columns': cols,
        'rows': rows,
    })

def user(request, id):
    uw = ModelWrapper(UserInfo)
    UserForm = build_form_class(
        uw,
        required_fields=['username', 'first_name'],
        readonly_fields=['tg_id', 'id', 'username']
        )
    user = container.firebase_service.fetch_by_id(UserInfo, id)

    if request.method == 'POST':
        form = UserForm(request.POST)
        response = save_object_from_form(
            form=form,
            obj=user,
            readonly_fields=['tg_id', 'id', 'username'],
            save_fn=lambda o: container.firebase_service.update(id=id, obj=o),
            success_redirect_name='users'
        )
        if response:
            return response
        return render(request, "app/user.html", {'form': form})
    else:
        # заполняем начальные значения из obj
        init = {
            field['name']: getattr(user, field['name']) for field in uw.fields
        }
        form = UserForm(initial=init)

    return render(request, "app/user.html", {'form': form})


#
# Wallets
#
def wallets(request):
    objs = container.firebase_service.fetch_all(Wallet)
    wrapper = ModelWrapper(
        Wallet
    )
    cols = wrapper.get_table_columns()
    rows = wrapper.get_table_data(objs)
    return render(request, 'app/wallets.html', {
        'columns': cols,
        'rows': rows,
    })

def wallet(request, id):
    uw = ModelWrapper(Wallet)
    Form = build_form_class(
        uw,
        readonly_fields=['id'],
        required_fields=['id'],
    )
    obj = container.firebase_service.fetch_by_id(Wallet, id)

    if request.method == 'POST':
        form = Form(request.POST)
        response = save_object_from_form(
            form=form,
            obj=obj,
            readonly_fields=['id'],
            save_fn=lambda o: container.firebase_service.update(id=id, obj=o),
            success_redirect_name='wallets'
        )
        if response:
            return response
        return render(request, "app/wallet.html", {'form': form})
    else:
        init = {}
        for f in uw.fields:
            name = f['name']
            val = getattr(obj, name)
            # если это Enum, используем его .value, иначе сам val
            if isinstance(val, Enum):
                init[name] = val.value
            else:
                init[name] = val
        form = Form(initial=init)
    return render(request, "app/wallet.html", {'form': form})


#
# Transactions
#
def transactions(request):
    objs = container.firebase_service.fetch_all(Transaction)
    wrapper = ModelWrapper(
        Transaction,
        include_fields=['id', 'from_wallet_id', 'to_wallet_id', 'amount', 'currency']
    )
    cols = wrapper.get_table_columns()
    rows = wrapper.get_table_data(objs)
    return render(request, 'app/transactions.html', {
        'columns': cols,
        'rows': rows,
    })

def transaction(request, id):
    uw = ModelWrapper(Transaction)
    Form = build_form_class(
        uw,
        readonly_fields=['id'],
        required_fields=['id'],
    )
    obj = container.firebase_service.fetch_by_id(Transaction, id)

    if request.method == 'POST':
        form = Form(request.POST)
        response = save_object_from_form(
            form=form,
            obj=obj,
            readonly_fields=['id'],
            save_fn=lambda o: container.firebase_service.update(id=id, obj=o),
            success_redirect_name='transactions'
        )
        if response:
            return response
        return render(request, "app/transaction.html", {'form': form})
    else:
        init = {}
        for f in uw.fields:
            name = f['name']
            val = getattr(obj, name)
            # если это Enum, используем его .value, иначе сам val
            if isinstance(val, Enum):
                init[name] = val.value
            else:
                init[name] = val
        form = Form(initial=init)
    return render(request, "app/transaction.html", {'form': form})


#
# Topup Requests
#
def topup_requests(request):
    objs = container.firebase_service.fetch_all(TopUpRequest)
    wrapper = ModelWrapper(
        TopUpRequest,
        include_fields=['id', 'user_id', 'amount', 'provider', 'external_id', 'status']
    )
    cols = wrapper.get_table_columns()
    rows = wrapper.get_table_data(objs)
    return render(request, 'app/topup_requests.html', {
        'columns': cols,
        'rows': rows,
    })

def topup_request(request, id):
    uw = ModelWrapper(TopUpRequest)
    Form = build_form_class(
        uw,
        readonly_fields=['id'],
        required_fields=['id'],
    )
    obj = container.firebase_service.fetch_by_id(TopUpRequest, id)

    if request.method == 'POST':
        form = Form(request.POST)
        response = save_object_from_form(
            form=form,
            obj=obj,
            readonly_fields=['id'],
            save_fn=lambda o: container.firebase_service.update(id=id, obj=o),
            success_redirect_name='topup_requests'
        )
        if response:
            return response
        return render(request, "app/topup_request.html", {'form': form})
    else:
        init = {}
        for f in uw.fields:
            name = f['name']
            val = getattr(obj, name)
            # если это Enum, используем его .value, иначе сам val
            if isinstance(val, Enum):
                init[name] = val.value
            else:
                init[name] = val
        form = Form(initial=init)
    return render(request, "app/topup_request.html", {'form': form})


#
# Case Openings
#
def case_openings(request):
    objs = container.firebase_service.fetch_all(CaseOpening)
    wrapper = ModelWrapper(
        CaseOpening
    )
    cols = wrapper.get_table_columns()
    rows = wrapper.get_table_data(objs)
    return render(request, 'app/case_openings.html', {
        'columns': cols,
        'rows': rows,
    })

def case_opening(request, id):
    uw = ModelWrapper(CaseOpening)
    Form = build_form_class(
        uw,
        readonly_fields=['id'],
        required_fields=['id'],
    )
    obj = container.firebase_service.fetch_by_id(CaseOpening, id)

    if request.method == 'POST':
        form = Form(request.POST)
        response = save_object_from_form(
            form=form,
            obj=obj,
            readonly_fields=['id'],
            save_fn=lambda o: container.firebase_service.update(id=id, obj=o),
            success_redirect_name='case_openings'
        )
        if response:
            return response
        return render(request, "app/case_opening.html", {'form': form})
    else:
        init = {}
        for f in uw.fields:
            name = f['name']
            val = getattr(obj, name)
            # если это Enum, используем его .value, иначе сам val
            if isinstance(val, Enum):
                init[name] = val.value
            else:
                init[name] = val
        form = Form(initial=init)
    return render(request, "app/case_opening.html", {'form': form})


def cases(request):
    cases = container.firebase_service.fetch_all(Case)
    return render(request, "app/cases.html", {'cases': cases})

def case(request, id):
    uw = ModelWrapper(Case)
    Form = build_form_class(
        uw,
        readonly_fields=['id'],
        required_fields=['id'],
    )
    obj = container.firebase_service.fetch_by_id(Case, id)

    if request.method == 'POST':
        form = Form(request.POST)
        response = save_object_from_form(
            form=form,
            obj=obj,
            readonly_fields=['id'],
            save_fn=lambda o: container.firebase_service.update(id=id, obj=o),
            success_redirect_name='cases'
        )
        if response:
            return response
        return render(request, "app/case.html", {'form': form})
    else:
        init = {}
        for f in uw.fields:
            name = f['name']
            val = getattr(obj, name)
            # если это Enum, используем его .value, иначе сам val
            if isinstance(val, Enum):
                init[name] = val.value
            else:
                init[name] = val
        form = Form(initial=init)
    return render(request, "app/case.html", {'form': form})

def case_gifts(request, id):
    external_collection_number = ""
    portals_gifts = []
    
    if request.method == 'POST':
        # Load gifts from Portals
        if 'external_collection_number' in request.POST and request.POST['external_collection_number'] != "":
            external_collection_number = request.POST['external_collection_number']
            print(f"🔍 Searching gifts for external_collection_number: {external_collection_number}")
            portals_gifts = __gifts_search(request, external_collection_number)
        
        # Delete gift from case
        if 'delete_gift_id' in request.POST:
            gift_id = request.POST['delete_gift_id']
            print("🗑️ Deleting gift with ID:", gift_id)
            try: 
                container.firebase_service.delete(model_class=Gift, document_id=gift_id)
            except Exception as e:
                print(f"❌ Error deleting gift: {e}")
                return redirect('case_gifts', id=id)
            
        # Change gift probability
        if 'change_prob' in request.POST:
            gift_id = request.POST['gift_id']
            prob = request.POST['prob']
            __update_gift_prob(gift_id, int(prob))

        #Change gift is active
        if 'change_is_active' in request.POST:
            gift_id = request.POST['gift_id']
            if 'is_active' in request.POST:
                is_active = True
            else:
                is_active = False
            print(f"🔄 Changing is_active for gift with ID: {gift_id} to {is_active}")
            __update_gift_is_active(gift_id, is_active)

        # Add gift to case
        if 'gift_portals_id' in request.POST:
            gift_portals_id = request.POST['gift_portals_id']
            print(f"➕ Adding gift with Portals ID: {gift_portals_id} to case {id}")
            __add_gift_to_case(id, portals_gifts, gift_portals_id)

        # Add ton to case
        if 'add_ton' in request.POST:
            ton_reward_name = request.POST['ton_reward_name']
            ton_reward_volume_cents = int(request.POST['ton_reward_volume_cents'])
            ton_reward_image_url = request.POST['ton_reward_image_url']

            print(f"➕ Adding TON reward to case {id}: {ton_reward_name}, Volume: {ton_reward_volume_cents}, Image URL: {ton_reward_image_url}")
            __add_ton_to_case(id, ton_reward_name, ton_reward_volume_cents, ton_reward_image_url)

        # Set linear probabilities for gifts in the case
        if 'set_linear_prob' in request.POST:
            desired_rtp = request.POST['desired_rtp']
            if not desired_rtp:
                print("❌ No desired RTP provided for linear probabilities.")
                return redirect('case_gifts', id=id)
            print("📈 Setting linear probabilities for gifts in the case")
            case, case_gifts = __load_case(request, id)
            try:
                __calculate_exponential_probabilities(
                    cost=case.cost,
                    gifts=case_gifts,
                    desired_rtp=int(desired_rtp)  # Assuming we want to set linear probabilities for 100% RTP
                )
            except ValueError as e:
                print(f"❌ Error calculating probabilities: {e}")
                return redirect('case_gifts', id=id)

    case, case_gifts = __load_case(request, id)
    sorted_case_gifts = sorted(case_gifts, key=lambda obj: obj.volume, reverse=False)
    total_prob, rtp = __case_gifts_general_info(case, case_gifts)

    # Remove gifts that are added already to the case
    ids_to_remove = {
        p.id
        for o in case_gifts
        if (p := o.payload) is not None
    }
    filtered_portals_gifts = [o for o in portals_gifts if o.id not in ids_to_remove]

    # Render the page
    return render(request, "app/case_gifts.html", {
        'case': case,
        'case_gifts': sorted_case_gifts,
        'total_prob': total_prob,
        'rtp': rtp,
        'external_collection_number': external_collection_number,
        'portals_gifts': filtered_portals_gifts
        }
    )

def __update_gift_is_active(gift_id: str, is_active: bool):
    gift = container.firebase_service.fetch_by_id(Gift, gift_id)
    if not gift:
        print(f"❌ Gift with ID {gift_id} not found.")
        return

    gift.is_active = is_active
    container.firebase_service.update(id=gift_id, obj=gift)
    print(f"✅ Updated gift with ID {gift_id} is_active to {is_active}.")


def __update_gift_prob(gift_id: str, prob: int):
    gift = container.firebase_service.fetch_by_id(Gift, gift_id)
    if not gift:
        print(f"❌ Gift with ID {gift_id} not found.")
        return
    
    if prob < 0 or prob > 10000:
        print(f"❌ Invalid probability value: {prob}. It should be between 0 and 100.")
        return

    gift.prob = prob
    container.firebase_service.update(id=gift_id, obj=gift)
    print(f"✅ Updated gift with ID {gift_id} probability to {prob}.")


def __add_gift_to_case(case_id: str, portals_gifts: List[PortalsNFT], gift_portals_id: str, prob: int = 0):
    filtered_portals_gifts = [g for g in portals_gifts if g.id == gift_portals_id]
    if not filtered_portals_gifts or len(filtered_portals_gifts) == 0:
        print(f"❌ Gift with Portals ID {gift_portals_id} not found in the list of Portals gifts.")
        return
    
    portals_gift = filtered_portals_gifts[0]

    gift = Gift(
        case_id=case_id,
        name= portals_gift.name,
        prob=prob,
        volume=int(float(portals_gift.price) * 100),
        is_active=False,
        type=GiftType.PORTALS_GIFT,
        payload=portals_gift
    )

    container.firebase_service.add(gift)

def __add_ton_to_case(id: str, ton_reward_name: str, ton_reward_volume_cents: int, ton_reward_image_url: str):
    """
    Adds a TON reward to the case with the given ID.
    """

    payload = TONReward(
        id=str(uuid.uuid4()),
        name=ton_reward_name,
        volume=ton_reward_volume_cents / 100,  # Convert cents to integer
        photo_url=ton_reward_image_url
    )

    gift = Gift(
        case_id=id,
        name=ton_reward_name,
        prob=0,  # Default probability for TON rewards
        volume=ton_reward_volume_cents,
        is_active=False,
        type=GiftType.BALANCE,
        payload=payload
    )
    
    container.firebase_service.add(gift)
    print(f"✅ Added TON reward '{ton_reward_name}' to case {id}.")


def __gifts_search(request, external_collection_number) -> List[PortalsNFT]:
    print("🔍 Loading gifts for external_collection_number:", external_collection_number)
    # Load gifts from Portals
    controller = PortalsController(container.firebase_service)
    portals_gifts = controller.portals_nfts_search(external_collection_number=external_collection_number)
    
    portals_gifts = sorted(portals_gifts, key=lambda nft: nft.pricef, reverse=False)

    return portals_gifts

def __load_case(request, id):
    case = container.firebase_service.fetch_by_id(Case, id)
    case_gifts = container.firebase_service.fetch_all(
        Gift,
        [FieldFilter('case_id', '==', id)]
    )
    return case, case_gifts

def __case_gifts_general_info(case, case_gifts: Iterable) -> Tuple[float, float]:
    """
    Возвращает:
      - total_prob: сумма вероятностей всех активных подарков (в тех же единицах, что и gift.prob), float
      - rtp: ожидаемое возвратное отношение (RTP) в процентах, float, округлено до 0.001
    """
    # 1) Отбираем только активные подарки
    active = [g for g in case_gifts if g.is_active]

    # 2) Сумма «сырых» вероятностей
    total_prob = float(sum(g.prob for g in active))

    # 3) Ожидаемая ценность: предполагаем, что g.probf — вероятность в долях (0.0–1.0)
    #    и g.volume — выигрыш в тех же единицах, что и case.cost
    expected_value = sum((g.probf) * float(g.volume) for g in active)

    # 4) Стоимость открытия кейса как float
    cost = float(case.cost)

    # 5) RTP: отношение ожидаемой ценности к стоимости, перевод в проценты
    rtp = expected_value / cost

    # 6) Округляем до 0.001%
    rtp = round(rtp, 3)
    return total_prob, rtp



def __calculate_exponential_probabilities(
    cost: int,
    gifts: Iterable[Gift],
    desired_rtp: float,
) -> List[float]:
    """
    cost        — цена кейса в центах (int)
    gifts       — итерируемые объекты Gift с полями .is_active (bool) и .volume (int, центы)
    desired_rtp — желаемый RTP в процентах (0–100)

    Возвращает:
      List[p_i] — дробные вероятности выпадения активных подарков (sum(p_i)=1).
    Параллельно обновляет gift.prob (0–10000) и делает batch_update.
    """
    # 1) Фильтруем только активные подарки
    active = [g for g in gifts if g.is_active]
    volumes = [g.volume for g in active]

    n = len(volumes)
    if n == 0:
        raise ValueError("Нет активных подарков для расчёта вероятностей")

    # 2) Целевой средний выигрыш E
    E = cost * desired_rtp / 100.0

    # 3) Проверяем достижимость E
    v_min, v_max = min(volumes), max(volumes)
    if not (v_min <= E <= v_max):
        raise ValueError(f"Target return {E} out of achievable range [{v_min}–{v_max}]")

    # 4) Функция для вычисления (ожидание, распределение) при заданном β
    def compute_expectation(beta: float) -> Tuple[float, List[float]]:
        exps = [math.exp(-beta * v) for v in volumes]
        Z = sum(exps)
        ps = [e / Z for e in exps]
        return sum(p * v for p, v in zip(ps, volumes)), ps

    # 5) Ищем β бинпоиском, чтобы expectation(β) ≈ E
    beta_lo, beta_hi = 0.0, 1.0
    exp_lo, _ = compute_expectation(beta_lo)
    exp_hi, _ = compute_expectation(beta_hi)
    while exp_hi > E:
        beta_hi *= 2
        exp_hi, _ = compute_expectation(beta_hi)

    for _ in range(50):
        mid = 0.5 * (beta_lo + beta_hi)
        exp_mid, _ = compute_expectation(mid)
        if exp_mid > E:
            beta_lo = mid
        else:
            beta_hi = mid

    _, probs = compute_expectation(0.5 * (beta_lo + beta_hi))

    # 6) Масштабируем в целые 0–10000, гарантируя минимум 3 для каждого подарка
    scale = 10000
    base = 2
    remaining = scale - n * base

    # рассчитываем дополнительную «часть» для распределения
    raw_extra = [p * remaining for p in probs]
    floors_extra = [int(x) for x in raw_extra]
    fracs = [(x - int(x), i) for i, x in enumerate(raw_extra)]
    missing_extra = remaining - sum(floors_extra)

    # распределяем недостающие единицы по наибольшим дробным частям
    for _, idx in sorted(fracs, key=lambda x: x[0], reverse=True)[:missing_extra]:
        floors_extra[idx] += 1

    # собираем итоговые целые вероятности (каждый ≥3)
    floors = [base + e for e in floors_extra]

    # 7) Сохраняем в gift.prob и вызываем batch_update
    updates = []
    for gift, cnt in zip(active, floors):
        gift.prob = cnt  # теперь min(cnt) = 3
        updates.append(gift)
    container.firebase_service.batch_update(updates)

    print(f"🔍 Final integer probs (min=3): {floors} (sum={sum(floors)})")
    return probs