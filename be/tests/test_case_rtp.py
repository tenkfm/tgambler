import random
import pytest

from functools import lru_cache

from app.controllers.case_controller import CaseController
from app.services.firebase.firebase_service import FirebaseService
from app.models.domain.case import Case
from app.models.domain.gift import Gift
from tests.utils.firebase_cache import CachedFirebaseService
from app.settings import Settings

@lru_cache()
def get_settings():
    return Settings()


@pytest.mark.slow
def test_case_rtp_simulation():
    # Setup function to initialize the FirebaseService and CachedFirebaseService.
    settings = get_settings()

    firebase = FirebaseService(api_key=settings.firebase_api_token)
    cached_firebase_service = CachedFirebaseService(firebase)
    controller = CaseController(firebase_service=cached_firebase_service)

    # Set initial data
    case_id = "y5ww90KVqg2OVPpTKLJe"
    random.seed(123456)

    # Test
    case: Case = controller.get_case_by_id(case_id)
    gifts: list[Gift] = controller.get_case_gifts(case_id)

    assert case, "Кейс не найден"
    assert gifts, "Нет подарков для кейса"

    cost_float = case.costf()
    rtp_theoretical = (
        sum(g.probf() * g.volumef() for g in gifts)
        / cost_float
        / 100
    )

    trials = 100_000
    total_volume = sum(controller.open_case(case_id).volumef() for _ in range(trials))
    rtp_empirical = total_volume / (trials * case.costf())

    print(f"Теоретический RTP: {rtp_theoretical:.4f}")
    print(f"Эмпирический RTP:  {rtp_empirical:.4f}")

    # ── Проверка
    assert abs(rtp_empirical - rtp_theoretical) < 0.015, (
        f"RTP mismatch: theoretical={rtp_theoretical:.4f}, empirical={rtp_empirical:.4f}"
    )