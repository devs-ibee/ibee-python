# Hand-written (listed in .fernignore).
from __future__ import annotations

import typing

from ..core.client_wrapper import AsyncClientWrapper, SyncClientWrapper
from ..core.pydantic_utilities import parse_obj_as
from ..core.request_options import RequestOptions
from ..errors.billing_errors import BillingAdmissionError, BillingDeniedError
from .models import BillingEligibility
from .raw_client import AsyncRawBillingClient, RawBillingClient, eligibility_request_body

_OPERATION_NOTE = "Not yet part of the published API contract; behaviour may change."


def _invalid_decision(message: str, payload: typing.Any) -> BillingAdmissionError:
    return BillingAdmissionError(
        {"error": "invalid_billing_decision", "message": message}, decision=payload
    )


def _decision_from_response(response: typing.Any, *, sku_code: typing.Optional[str]) -> BillingEligibility:
    """Validate a 200 eligibility body like the API edge does, then parse it."""
    try:
        payload = response.json()
    except Exception:
        raise _invalid_decision("Billing returned a decision that is not JSON.", None)
    if not isinstance(payload, dict):
        raise _invalid_decision("Billing returned a decision that is not a JSON object.", payload)
    if not isinstance(payload.get("allowed"), bool):
        raise _invalid_decision("Billing returned a decision without a boolean 'allowed'.", payload)
    for field in ("organization_id", "reason"):
        value = payload.get(field)
        if not isinstance(value, str) or not value.strip():
            raise _invalid_decision(f"Billing returned a decision without '{field}'.", payload)
    if sku_code is not None:
        actual = payload.get("sku_code")
        if not isinstance(actual, str) or actual.strip().upper() != sku_code.strip().upper():
            raise _invalid_decision("Billing did not confirm the requested SKU.", payload)
    try:
        return typing.cast(BillingEligibility, parse_obj_as(type_=BillingEligibility, object_=payload))  # type: ignore
    except Exception:
        raise _invalid_decision("Billing returned a decision that could not be parsed.", payload)


def _require_allowed(decision: BillingEligibility, resource_type: typing.Optional[str]) -> BillingEligibility:
    if decision.allowed is not True:
        raise BillingDeniedError(decision=decision, create_type=resource_type or "resource")
    return decision


class BillingClient:
    def __init__(self, *, client_wrapper: SyncClientWrapper):
        self._raw_client = RawBillingClient(client_wrapper=client_wrapper)

    @property
    def with_raw_response(self) -> RawBillingClient:
        return self._raw_client

    def check_resource_eligibility(
        self,
        *,
        workspace_id: str,
        sku_code: typing.Optional[str] = None,
        estimated_cost_minor: typing.Optional[typing.Union[int, float]] = None,
        operation: typing.Optional[str] = None,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> BillingEligibility:
        """
        Check whether billing permits a prospective resource create. Requires scope: billing.read.

        This is a read-only query: a denied decision is returned (``allowed`` is
        ``False``), not raised. Use ``require_resource_eligibility`` to raise instead.
        Product create methods do not call it; the API edge enforces billing on the
        create itself.

        Parameters
        ----------
        workspace_id : str
            The workspace ID to scope this request to.
        sku_code : typing.Optional[str]
            SKU to price (1-64 characters after trimming; blank is omitted). Billing
            compares it case-insensitively.
        estimated_cost_minor : typing.Optional[int]
            Estimated cost in minor currency units (>= 0; floats are rounded). See
            ``ibee.billing.estimate_eligibility_cost_minor``.
        operation : typing.Optional[str]
            Operation to evaluate, default ``CREATE_RESOURCE`` (one of
            ``CREATE_RESOURCE``, ``CREATE_CREDENTIAL``, ``INCREASE_CAPACITY``,
            ``MUTATE_RESOURCE``, ``READ_RESOURCE``, ``DELETE_RESOURCE``,
            ``REVOKE_CREDENTIAL``, ``SECURITY_RECOVERY``). Not yet part of the published
            API contract; behaviour may change.
        """
        return self._raw_client.check_resource_eligibility(
            workspace_id=workspace_id,
            sku_code=sku_code,
            estimated_cost_minor=estimated_cost_minor,  # type: ignore[arg-type]
            operation=operation,
            request_options=request_options,
        ).data

    def require_resource_eligibility(
        self,
        *,
        workspace_id: str,
        sku_code: typing.Optional[str] = None,
        estimated_cost_minor: typing.Optional[typing.Union[int, float]] = None,
        operation: typing.Optional[str] = None,
        resource_type: typing.Optional[str] = "resource",
        request_options: typing.Optional[RequestOptions] = None,
    ) -> BillingEligibility:
        """
        Portal-style billing preflight: return the decision only when ``allowed`` is exactly ``True``.

        Raises ``BillingDeniedError`` (HTTP 402, ``code="billing_denied"``) with the
        portal's message for ``resource_type`` (for example ``vm``, ``gpu_vm``,
        ``block_storage``) and ``topup_allowed``, which is true only when upstream lists
        ``billing_topup`` in ``allowed_operations``.
        Raises ``BillingAdmissionError`` (502, ``code="invalid_billing_decision"``) when
        billing returns an incomplete decision or prices a different SKU. The API edge
        repeats this check on the real create; the preflight never reserves funds.
        ``operation`` is not yet part of the published API contract; behaviour may change.
        """
        body = eligibility_request_body(
            sku_code=sku_code, estimated_cost_minor=estimated_cost_minor, operation=operation
        )
        response = self._raw_client._post_eligibility(
            workspace_id=workspace_id, body=body, request_options=request_options
        )
        decision = _decision_from_response(response, sku_code=body.get("sku_code"))
        return _require_allowed(decision, resource_type)


class AsyncBillingClient:
    def __init__(self, *, client_wrapper: AsyncClientWrapper):
        self._raw_client = AsyncRawBillingClient(client_wrapper=client_wrapper)

    @property
    def with_raw_response(self) -> AsyncRawBillingClient:
        return self._raw_client

    async def check_resource_eligibility(
        self,
        *,
        workspace_id: str,
        sku_code: typing.Optional[str] = None,
        estimated_cost_minor: typing.Optional[typing.Union[int, float]] = None,
        operation: typing.Optional[str] = None,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> BillingEligibility:
        """
        Check whether billing permits a prospective resource create (read-only query).

        Same parameters and semantics as ``BillingClient.check_resource_eligibility``.
        ``operation`` is not yet part of the published API contract; behaviour may change.
        """
        response = await self._raw_client.check_resource_eligibility(
            workspace_id=workspace_id,
            sku_code=sku_code,
            estimated_cost_minor=estimated_cost_minor,  # type: ignore[arg-type]
            operation=operation,
            request_options=request_options,
        )
        return response.data

    async def require_resource_eligibility(
        self,
        *,
        workspace_id: str,
        sku_code: typing.Optional[str] = None,
        estimated_cost_minor: typing.Optional[typing.Union[int, float]] = None,
        operation: typing.Optional[str] = None,
        resource_type: typing.Optional[str] = "resource",
        request_options: typing.Optional[RequestOptions] = None,
    ) -> BillingEligibility:
        """
        Portal-style billing preflight; see ``BillingClient.require_resource_eligibility``.
        ``operation`` is not yet part of the published API contract; behaviour may change.
        """
        body = eligibility_request_body(
            sku_code=sku_code, estimated_cost_minor=estimated_cost_minor, operation=operation
        )
        response = await self._raw_client._post_eligibility(
            workspace_id=workspace_id, body=body, request_options=request_options
        )
        decision = _decision_from_response(response, sku_code=body.get("sku_code"))
        return _require_allowed(decision, resource_type)
