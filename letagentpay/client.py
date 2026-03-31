"""LetAgentPay API client."""

from __future__ import annotations

import os
from decimal import Decimal
from typing import Any

import httpx

from letagentpay.models import (
    BudgetInfo,
    ConfirmResult,
    PurchaseResult,
    RequestList,
    RequestStatus,
)

_DEFAULT_BASE_URL = "https://api.letagentpay.com/api/v1/agent-api"


class LetAgentPayError(Exception):
    def __init__(self, status: int, detail: str):
        self.status = status
        self.detail = detail
        super().__init__(f"[{status}] {detail}")


class LetAgentPay:
    """Client for the LetAgentPay Agent API.

    Usage::

        client = LetAgentPay(token="agt_...")
        result = client.request_purchase(
            amount=25.00,
            category="groceries",
            merchant_name="SuperMart",
            agent_comment="Need this for meal prep",
        )
        print(result.status)  # "auto_approved" / "pending" / "rejected"
    """

    def __init__(
        self,
        token: str | None = None,
        base_url: str | None = None,
    ):
        resolved_token = token or os.environ.get("LETAGENTPAY_TOKEN")
        if not resolved_token:
            raise ValueError(
                "Token is required. Pass token= or set LETAGENTPAY_TOKEN env var."
            )
        resolved_base_url = (
            base_url or os.environ.get("LETAGENTPAY_BASE_URL") or _DEFAULT_BASE_URL
        )

        self._token = resolved_token
        self._base_url = resolved_base_url.rstrip("/")
        self._client = httpx.Client(
            base_url=self._base_url,
            headers={"Authorization": f"Bearer {resolved_token}"},
            timeout=30,
        )

    def _request(self, method: str, path: str, **kwargs) -> dict[str, Any]:
        resp = self._client.request(method, path, **kwargs)
        if resp.status_code >= 400:
            detail = resp.json().get("detail", resp.text)
            raise LetAgentPayError(resp.status_code, detail)
        return resp.json()

    def request_purchase(
        self,
        amount: float | Decimal,
        category: str,
        merchant_name: str | None = None,
        description: str | None = None,
        agent_comment: str | None = None,
    ) -> PurchaseResult:
        """Create a purchase request."""
        body: dict[str, Any] = {"amount": float(amount), "category": category}
        if merchant_name:
            body["merchant_name"] = merchant_name
        if description:
            body["description"] = description
        if agent_comment:
            body["agent_comment"] = agent_comment
        data = self._request("POST", "/requests", json=body)
        return PurchaseResult.from_dict(data)

    def check_request(self, request_id: str) -> RequestStatus:
        """Check the status of a purchase request."""
        data = self._request("GET", f"/requests/{request_id}")
        return RequestStatus.from_dict(data)

    def confirm_purchase(
        self,
        request_id: str,
        success: bool,
        actual_amount: float | Decimal | None = None,
        receipt_url: str | None = None,
    ) -> ConfirmResult:
        """Confirm a purchase result after approval."""
        body: dict[str, Any] = {"success": success}
        if actual_amount is not None:
            body["actual_amount"] = float(actual_amount)
        if receipt_url:
            body["receipt_url"] = receipt_url
        data = self._request("POST", f"/requests/{request_id}/confirm", json=body)
        return ConfirmResult.from_dict(data)

    def check_budget(self) -> BudgetInfo:
        """Get current budget, spent, and remaining."""
        data = self._request("GET", "/budget")
        return BudgetInfo.from_dict(data)

    def get_policy(self) -> dict[str, Any]:
        """Get the current spending policy."""
        return self._request("GET", "/policy")

    def list_categories(self) -> list[str]:
        """List valid purchase categories."""
        return self._request("GET", "/categories")["categories"]

    def my_requests(
        self,
        status: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> RequestList:
        """List agent's purchase requests."""
        params: dict[str, Any] = {"limit": limit, "offset": offset}
        if status:
            params["status"] = status
        data = self._request("GET", "/requests", params=params)
        return RequestList.from_dict(data)

    def close(self):
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
