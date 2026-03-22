"""
Отправка данных в 1С (REST / OData): заглушка до настройки публикации и метода создания документов.
"""

from __future__ import annotations

from typing import Any

import httpx

from src.config.settings import Settings


class OneCPushService:
    """Публикация заказов/движений в 1С — расширяйте под вашу HTTP-сервисную обработку."""

    def __init__(self, settings: Settings):
        self._settings = settings

    async def push_orders(
        self,
        orders: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """
        orders: например [{"product_external_id": "...", "warehouse_external_id": "...", "quantity": 10}, ...]
        """
        base = self._settings.INTEGRATION_1C_BASE_URL
        if not base:
            return {
                "status": "skipped",
                "reason": "INTEGRATION_1C_BASE_URL не задан",
                "count": len(orders),
            }

        push_url = self._settings.INTEGRATION_1C_PUSH_ORDERS_URL
        if not push_url:
            return {
                "status": "not_configured",
                "detail": "Задайте INTEGRATION_1C_PUSH_ORDERS_URL для реальной отправки",
                "count": len(orders),
            }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                push_url,
                json={"orders": orders},
                auth=(
                    self._settings.INTEGRATION_1C_USERNAME or "",
                    self._settings.INTEGRATION_1C_PASSWORD or "",
                ),
            )
            response.raise_for_status()
            return {"status": "ok", "response": response.json()}
