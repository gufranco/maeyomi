"""The inverter proposes only candidates that verify.

The solver verifies every candidate before returning it, so a wrong proposal is
never printed. That makes wrongness invisible, and an inverter that proposes
mostly-wrong candidates would still pass every other test while doing far more
work than it should. These tests assert exactness directly.
"""

import itertools

from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from barcode_battler.generator.front_solver import iter_front_candidates
from barcode_battler.generator.solve import verify
from barcode_battler.models.card_request import CardRequest
from barcode_battler.models.constraint import Constraint
from barcode_battler.models.race import Race

FIGHTERS = [race for race in Race if race.is_fighter]

fighter_requests = st.builds(
    CardRequest,
    hp=st.integers(min_value=0, max_value=999).map(lambda units: Constraint.exactly(units * 100)),
    st=st.integers(min_value=0, max_value=99).map(lambda units: Constraint.exactly(units * 100)),
    df=st.integers(min_value=0, max_value=99).map(lambda units: Constraint.exactly(units * 100)),
    race=st.sampled_from(FIGHTERS),
    job=st.integers(min_value=0, max_value=9),
    special=st.integers(min_value=0, max_value=99),
)


@given(fighter_requests)
@settings(max_examples=300, deadline=None, suppress_health_check=[HealthCheck.too_slow])
def test_every_fighter_candidate_verifies(request: CardRequest) -> None:
    candidates = list(itertools.islice(iter_front_candidates(request), 20))

    rejected = [code for code in candidates if verify(request, code) is None]

    assert rejected == []


item_requests = st.builds(
    CardRequest,
    st=st.integers(min_value=0, max_value=99).map(lambda units: Constraint.exactly(units * 100)),
    race=st.sampled_from([Race.WEAPON, Race.SINGLE_USE_WEAPON]),
    special=st.integers(min_value=0, max_value=99),
)


@given(item_requests)
@settings(max_examples=200, deadline=None, suppress_health_check=[HealthCheck.too_slow])
def test_every_weapon_candidate_verifies(request: CardRequest) -> None:
    candidates = list(itertools.islice(iter_front_candidates(request), 20))

    rejected = [code for code in candidates if verify(request, code) is None]

    assert rejected == []


support_requests = st.builds(
    CardRequest,
    hp=st.integers(min_value=0, max_value=50).map(lambda units: Constraint.exactly(units * 100)),
    race=st.just(Race.SUPPORT_ITEM),
    job=st.integers(min_value=0, max_value=4),
    special=st.integers(min_value=0, max_value=29),
)


@given(support_requests)
@settings(max_examples=200, deadline=None, suppress_health_check=[HealthCheck.too_slow])
def test_every_support_item_candidate_verifies(request: CardRequest) -> None:
    candidates = list(itertools.islice(iter_front_candidates(request), 20))

    rejected = [code for code in candidates if verify(request, code) is None]

    assert rejected == []
