"""Daily cap on paid language-model questions (a cost guard for a public deployment). In memory on purpose:
the counter starts again whenever the process starts, which includes every new release."""

import threading
from collections.abc import Callable, Mapping
from datetime import UTC, date, datetime

DAILY_LIMIT_ENV = "PSI_DAILY_MODEL_LIMIT"  # 0 or unset = unlimited (local use); the deployment sets it


def limit_from_env(env: Mapping[str, str]) -> int:
    """A missing, malformed or negative value means no limit, so a typo can never lock the app."""
    try:
        return max(0, int(env.get(DAILY_LIMIT_ENV, "0").strip() or "0"))
    except ValueError:
        return 0


def _utc_today() -> date:
    return datetime.now(UTC).date()


class DailyQuota:
    def __init__(self, limit: int, today: Callable[[], date] = _utc_today) -> None:
        self.limit = max(0, limit)
        self._today, self._day, self._used = today, today(), 0
        self._lock = threading.Lock()  # Streamlit sessions run in threads of one process

    @property
    def enabled(self) -> bool:
        return self.limit > 0

    def _roll(self) -> None:
        if self._today() != self._day:
            self._day, self._used = self._today(), 0

    def remaining(self) -> int:
        with self._lock:
            self._roll()
            return max(0, self.limit - self._used)

    def try_consume(self) -> bool:
        """Takes one question from today's allowance; False when none is left. Always True when unlimited."""
        if not self.enabled:
            return True
        with self._lock:
            self._roll()
            if self._used >= self.limit:
                return False
            self._used += 1
            return True
