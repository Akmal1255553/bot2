from __future__ import annotations

import asyncio
import time
from contextlib import asynccontextmanager
from datetime import date
from collections import deque

from config import get_settings
from database.models import Plan

from bot.services.exceptions import AccessDeniedError


class GenerationGuard:
    def __init__(self) -> None:
        settings = get_settings()
        self.settings = settings
        self._global_sem = asyncio.Semaphore(settings.global_generation_concurrency)
        self._by_plan_sem = {
            Plan.FREE: asyncio.Semaphore(1),
            Plan.BASIC: asyncio.Semaphore(1),
            Plan.PRO: asyncio.Semaphore(2),
        }
        self._priority_wait_seconds = {
            Plan.FREE: 1.0,
            Plan.BASIC: 0.3,
            Plan.PRO: 0.0,
        }
        self._daily_lock = asyncio.Lock()
        self._daily_day = date.today()
        self._daily_count = 0
        self._rate_lock = asyncio.Lock()
        self._user_last_seen: dict[int, float] = {}
        self._global_rate_lock = asyncio.Lock()
        self._global_request_times: deque[float] = deque()

    async def _sync_day(self) -> None:
        today = date.today()
        if today != self._daily_day:
            self._daily_day = today
            self._daily_count = 0

    async def ensure_daily_capacity(self) -> None:
        async with self._daily_lock:
            await self._sync_day()
            if self._daily_count >= self.settings.daily_global_generation_cap:
                raise AccessDeniedError("Daily generation cap reached. Please try again tomorrow.")
            self._daily_count += 1

    async def ensure_user_rate_limit(self, user_id: int) -> None:
        now = time.monotonic()
        async with self._rate_lock:
            prev = self._user_last_seen.get(user_id)
            if prev is not None and (now - prev) < self.settings.per_user_rate_limit_seconds:
                raise AccessDeniedError(
                    f"Please wait {self.settings.per_user_rate_limit_seconds} seconds "
                    "before the next generation request."
                )
            self._user_last_seen[user_id] = now

    async def ensure_global_rate_limit(self) -> None:
        now = time.monotonic()
        period = self.settings.global_rate_limit_period_seconds
        limit = self.settings.global_rate_limit_requests
        async with self._global_rate_lock:
            cutoff = now - period
            while self._global_request_times and self._global_request_times[0] < cutoff:
                self._global_request_times.popleft()
            if len(self._global_request_times) >= limit:
                raise AccessDeniedError(
                    "Global generation rate limit reached. Please retry in a few seconds."
                )
            self._global_request_times.append(now)

    @asynccontextmanager
    async def acquire(self, plan: Plan):
        wait_seconds = self._priority_wait_seconds[plan]
        if wait_seconds:
            await asyncio.sleep(wait_seconds)
        plan_sem = self._by_plan_sem[plan]
        async with plan_sem:
            async with self._global_sem:
                yield
