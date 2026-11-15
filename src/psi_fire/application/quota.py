"""Daily caps on copilot questions (a cost guard for a public deployment): per visitor and, as a safety ceiling,
in total. In memory on purpose: the counters start again whenever the process starts, which includes every release."""

import threading
from collections import Counter
from collections.abc import Callable, Mapping
from datetime import UTC, date, datetime
from enum import StrEnum

PER_USER_ENV = "PSI_DAILY_MODEL_LIMIT"    # questions per visitor per UTC day; 0 or unset = unlimited (local use)
GLOBAL_ENV = "PSI_DAILY_GLOBAL_LIMIT"     # questions per UTC day across all visitors; 0 or unset = no ceiling


def _limit(env: Mapping[str, str], name: str) -> int:
    """A missing, malformed or negative value means no limit, so a typo can never lock the app."""
    try:
        return max(0, int(env.get(name, "0").strip() or "0"))
    except ValueError:
        return 0


def limit_from_env(env: Mapping[str, str]) -> int:
    return _limit(env, PER_USER_ENV)


def global_limit_from_env(env: Mapping[str, str]) -> int:
    return _limit(env, GLOBAL_ENV)


class QuotaVerdict(StrEnum):
    ALLOWED = "allowed"
    USER_LIMIT = "user_limit"
    GLOBAL_LIMIT = "global_limit"


def _utc_today() -> date:
    return datetime.now(UTC).date()


class DailyQuota:
    def __init__(self, limit: int, today: Callable[[], date] = _utc_today, global_limit: int = 0) -> None:
        self.limit, self.global_limit = max(0, limit), max(0, global_limit)
        self._today, self._day = today, today()
        self._used: Counter[str] = Counter()
        self._lock = threading.Lock()  # Streamlit sessions run in threads of one process

    @property
    def enabled(self) -> bool:
        return self.limit > 0 or self.global_limit > 0

    def _roll(self) -> None:
        if self._today() != self._day:
            self._day = self._today()
            self._used.clear()

    def _total(self) -> int:
        return sum(self._used.values())

    def remaining(self, user: str) -> int:
        """Questions this visitor can still ask today, counting the ceiling for everyone."""
        with self._lock:
            self._roll()
            options = []
            if self.limit > 0:
                options.append(self.limit - self._used[user])
            if self.global_limit > 0:
                options.append(self.global_limit - self._total())
            return max(0, min(options)) if options else 0

    def consume(self, user: str) -> QuotaVerdict:
        """Takes one question from this visitor's allowance. Always ALLOWED when no limit is set."""
        if not self.enabled:
            return QuotaVerdict.ALLOWED
        with self._lock:
            self._roll()
            if self.limit > 0 and self._used[user] >= self.limit:
                return QuotaVerdict.USER_LIMIT
            if self.global_limit > 0 and self._total() >= self.global_limit:
                return QuotaVerdict.GLOBAL_LIMIT
            self._used[user] += 1
            return QuotaVerdict.ALLOWED
