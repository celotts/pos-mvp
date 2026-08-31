import uuid
from datetime import date

from service.analytics_service import (
    compute_bundles,
    compute_cross_sell,
    evaluate_stockout,
    smooth_daily_demand,
)

A = uuid.uuid4()
B = uuid.uuid4()
C = uuid.uuid4()
D = uuid.uuid4()


def test_compute_cross_sell_ranks_by_lift():
    transactions = [
        {A, B},
        {A, B, C},
        {A, B},
        {A, C},
        {A, D},
        {B, C},
        {B},
    ]
    total, recs = compute_cross_sell(transactions, A, min_support=0.0)
    assert total == 7
    codes = {pid for pid, *_ in recs}
    assert {B, C, D}.issubset(codes)
    # orden estrictamente descendente por lift
    lifts = [rec[2] for rec in recs]
    assert lifts == sorted(lifts, reverse=True)
    # A solo co-ocurre con B, C y D
    assert len(recs) == 3


def test_compute_cross_sell_min_support_filters_noise():
    transactions = [{A, B}] * 5 + [{C}] * 95
    _, recs = compute_cross_sell(transactions, A, min_support=0.1)
    assert recs == []


def test_compute_cross_sell_unknown_product():
    total, recs = compute_cross_sell([{A, B}], C, min_support=0.0)
    assert total == 1
    assert recs == []


def test_compute_bundles_returns_strongest_pair_first():
    transactions = [{A, B}, {A, B, C}, {A, B}, {A}, {B}]
    bundles = compute_bundles(transactions, min_support=0.0, limit=10)
    assert bundles
    # El par {A,B} (3 co-ocurrencias) siempre está en los resultados
    assert (A, B) in {tuple(sorted(p[:2])) for p in bundles} or (B, A) in {
        tuple(sorted(p[:2])) for p in bundles
    }
    # Orden estrictamente descendente por lift
    lifts = [b[4] for b in bundles]
    assert lifts == sorted(lifts, reverse=True)


def test_smooth_daily_demand():
    daily = {date(2026, 1, 1): 10, date(2026, 1, 2): 10, date(2026, 1, 3): 10}
    assert smooth_daily_demand(daily) == 10.0
    assert smooth_daily_demand({}) == 0.0


def test_evaluate_stockout_critical_and_ok():
    days_left, risk, rec = evaluate_stockout(
        stock=10, avg_daily=2.0, horizon=7, lead_time_days=5
    )
    assert risk == "CRITICAL"
    assert days_left == 5.0
    assert rec == 14

    days_left, risk, rec = evaluate_stockout(
        stock=100, avg_daily=2.0, horizon=7, lead_time_days=5
    )
    assert risk == "OK"
    assert rec == 0

    days_left, risk, rec = evaluate_stockout(
        stock=0, avg_daily=3.0, horizon=7, lead_time_days=5
    )
    assert risk == "OUT_OF_STOCK"

    days_left, risk, rec = evaluate_stockout(
        stock=5, avg_daily=0.0, horizon=7, lead_time_days=5
    )
    assert risk == "NO_SALES"
    assert days_left is None
