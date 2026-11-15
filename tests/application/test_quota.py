from datetime import date

from psi_fire.application.quota import DAILY_LIMIT_ENV, DailyQuota, limit_from_env


class Clock:
    def __init__(self) -> None:
        self.day = date(2026, 11, 15)

    def __call__(self) -> date:
        return self.day


def test_the_daily_limit_blocks_the_fifth_question_and_comes_back_the_next_day():
    clock = Clock()
    quota = DailyQuota(4, today=clock)
    assert [quota.try_consume() for _ in range(5)] == [True, True, True, True, False]
    assert quota.remaining() == 0
    clock.day = date(2026, 11, 16)
    assert quota.remaining() == 4 and quota.try_consume()


def test_a_new_quota_object_starts_from_zero_which_is_what_a_new_release_does():
    first = DailyQuota(4)
    for _ in range(4):
        first.try_consume()
    assert first.remaining() == 0 and DailyQuota(4).remaining() == 4


def test_zero_or_unset_means_unlimited_and_a_bad_value_never_locks_the_app():
    assert not DailyQuota(0).enabled and all(DailyQuota(0).try_consume() for _ in range(10))
    assert limit_from_env({}) == 0 and limit_from_env({DAILY_LIMIT_ENV: ""}) == 0
    assert limit_from_env({DAILY_LIMIT_ENV: "4"}) == 4 and limit_from_env({DAILY_LIMIT_ENV: " 4 "}) == 4
    assert limit_from_env({DAILY_LIMIT_ENV: "four"}) == 0 and limit_from_env({DAILY_LIMIT_ENV: "-3"}) == 0


def test_concurrent_sessions_never_get_more_than_the_limit():
    from concurrent.futures import ThreadPoolExecutor

    quota = DailyQuota(4)
    with ThreadPoolExecutor(max_workers=16) as pool:
        granted = list(pool.map(lambda _: quota.try_consume(), range(64)))
    assert sum(granted) == 4
