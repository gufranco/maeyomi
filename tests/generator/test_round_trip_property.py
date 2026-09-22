"""The property that decides whether the generator can be trusted.

For every request the solver declares solvable, decoding the barcode it
returned must reproduce the request. A failure here means the inverter and the
decoder disagree, which is the one defect class the round trip exists to catch.
"""

from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from barcode_battler.decoder.decode import decode
from barcode_battler.generator.quarantine import takes_quarantined_branch
from barcode_battler.generator.solve import mismatches, solve
from barcode_battler.models.card_request import CardRequest
from barcode_battler.models.constraint import Constraint
from barcode_battler.models.race import Race

FIGHTERS = [race for race in Race if race.is_fighter]

requests = st.builds(
    CardRequest,
    hp=st.integers(min_value=0, max_value=999).map(lambda units: Constraint.exactly(units * 100)),
    st=st.integers(min_value=0, max_value=99).map(lambda units: Constraint.exactly(units * 100)),
    df=st.integers(min_value=0, max_value=99).map(lambda units: Constraint.exactly(units * 100)),
    race=st.sampled_from(FIGHTERS),
    job=st.integers(min_value=0, max_value=9),
    special=st.integers(min_value=0, max_value=99),
)


@given(requests)
@settings(max_examples=400, deadline=None, suppress_health_check=[HealthCheck.too_slow])
def test_a_solved_request_always_decodes_back_to_itself(request: CardRequest) -> None:
    outcome = solve(request)

    if outcome.barcode is None:
        return

    assert mismatches(request, decode(outcome.barcode)) == ()


@given(requests)
@settings(max_examples=400, deadline=None, suppress_health_check=[HealthCheck.too_slow])
def test_a_solved_request_never_rests_on_an_unresolved_branch(request: CardRequest) -> None:
    outcome = solve(request)

    if outcome.barcode is None:
        return

    assert not takes_quarantined_branch(outcome.barcode)


@given(requests)
@settings(max_examples=200, deadline=None, suppress_health_check=[HealthCheck.too_slow])
def test_an_unsolved_request_always_carries_a_reason(request: CardRequest) -> None:
    outcome = solve(request)

    if outcome.barcode is not None:
        return

    assert outcome.blockers
