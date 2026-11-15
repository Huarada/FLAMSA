from datetime import date

from psi_fire.application.quota import (
    GLOBAL_ENV,
    PER_USER_ENV,
    DailyQuota,
    QuotaVerdict,
    global_limit_from_env,
    limit_from_env,
)


class Clock:
    def __init__(self) -> None:
        self.day = date(2026, 11, 15)

    def __call__(self) -> date:
        return self.day


def test_each_visitor_gets_four_questions_and_the_fifth_is_refused():
    quota = DailyQuota(4)
    first = [quota.consume("203.0.113.5") for _ in range(5)]
    assert first == [QuotaVerdict.ALLOWED] * 4 + [QuotaVerdict.USER_LIMIT]
    assert quota.remaining("203.0.113.5") == 0
    assert quota.remaining("198.51.100.7") == 4 and quota.consume("198.51.100.7") == QuotaVerdict.ALLOWED


def test_the_global_ceiling_stops_everyone_even_visitors_with_questions_left():
    quota = DailyQuota(4, global_limit=5)
    assert [quota.consume(f"ip{i}") for i in range(5)] == [QuotaVerdict.ALLOWED] * 5
    assert quota.consume("ip99") == QuotaVerdict.GLOBAL_LIMIT and quota.remaining("ip99") == 0


def test_counts_return_the_next_utc_day_and_a_new_process_starts_from_zero():
    clock = Clock()
    quota = DailyQuota(4, today=clock)
    for _ in range(4):
        quota.consume("a")
    assert quota.remaining("a") == 0
    clock.day = date(2026, 11, 16)
    assert quota.remaining("a") == 4
    assert DailyQuota(4).remaining("a") == 4  # what a new release does


def test_unset_zero_or_bad_values_mean_unlimited_and_never_lock_the_app():
    assert not DailyQuota(0).enabled and DailyQuota(0).consume("a") == QuotaVerdict.ALLOWED
    assert limit_from_env({}) == 0 and limit_from_env({PER_USER_ENV: "4"}) == 4 and limit_from_env({PER_USER_ENV: "four"}) == 0
    assert global_limit_from_env({GLOBAL_ENV: " 100 "}) == 100 and global_limit_from_env({GLOBAL_ENV: "-3"}) == 0


def test_concurrent_requests_never_exceed_the_limits():
    from concurrent.futures import ThreadPoolExecutor

    quota = DailyQuota(4, global_limit=10)
    with ThreadPoolExecutor(max_workers=16) as pool:
        verdicts = list(pool.map(lambda i: quota.consume(f"ip{i % 3}"), range(64)))
    assert verdicts.count(QuotaVerdict.ALLOWED) <= 10
