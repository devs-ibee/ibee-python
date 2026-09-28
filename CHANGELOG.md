# Changelog

## 0.4.0

Portal-parity foundations shared by every resource: typed errors, client-side
validation, safe retries with idempotency keys, operation waiting, and
auto-paging.

### Added

- `ibee.IbeeValidationError` (subclass of `ValueError` and the new `ibee.errors.IbeeError`)
  with a stable `code` and `field`, raised before any HTTP request. New module
  `ibee.validation` holds every client-side rule.
- Typed HTTP errors, each subclassing the 0.3.0 class for its status:
  `InvalidWorkspaceError`, `InsufficientScopeError`, `WorkspaceNotAllowedError`,
  `ApiKeyInactiveError`, `RouteNotAvailableError`, `OrganizationRestrictedError`,
  `BillingForbiddenError`, `BillingDeniedError`, `BillingAdmissionError`,
  `PayloadTooLargeError`, `UnprocessableEntityError`, `OrganizationSuspendedError`,
  `TooManyRequestsError`, `InternalServerError`, `GatewayTimeoutError`, plus
  `ibee.errors.error_from_response` and `ibee.errors.is_payment_block_error`.
- `ApiError` now exposes `code` (stable, lower-case), `raw_code`, `message`,
  `reason`, `raw_body`, `details`, `required_scope`, `billing_sku_code`,
  `admission_context_id`, `request_id`, `retry_after`, `idempotency_key` and
  `retryable`, parsed from every error body shape the API returns.
- `client.billing.require_resource_eligibility(...)` (sync and async): the portal's
  billing preflight. Returns the decision only when `allowed` is exactly `True`,
  raises `BillingDeniedError` (402, portal wording, `topup_allowed`) or
  `BillingAdmissionError` (502, `invalid_billing_decision`).
- `check_resource_eligibility` accepts `operation` (not yet part of the published
  API contract) and validates `sku_code` (1-64 characters, blank omitted) and
  `estimated_cost_minor` (>= 0, floats rounded).
- `BillingEligibility` types the full decision: `service_enforcement_state`,
  `enforcement_revision`, `enforcement_source`, `enforcement_reason_code`,
  `operation`, `allowed_operations`, `resource_limits`.
- `ibee.billing` helpers: `billing_block_message`, `is_billing_topup_allowed`,
  `estimate_eligibility_cost_minor` (731-hour estimate for hourly plans),
  `minimum_topup_minor`, `CREATE_TYPE_LABELS`, `is_payment_block_error`.
- `wait_for_compute_operation` on `cloud_vms` and `gpu_vms` (sync and async) and
  `ibee.wait_for_compute_operation(client, ...)` /
  `ibee.wait_for_compute_operation_async`: default timeout 1200 s, poll interval
  5 s, raises `OperationFailedError` or `OperationTimeoutError`. Generic engine
  `ibee.operations.poll_until` / `apoll_until`.
- `gpu_vms.get_compute_operation` (same route as `cloud_vms.get_compute_operation`).
- `iter_cloud_vms`, `iter_gpu_vms`, `iter_firewall_groups` (async iterators on the
  async client) and the `ibee.pagination` helpers `paginate_offset` / `paginate_pages`.
- `list_cloud_vms` / `list_gpu_vms` accept `limit`, `offset`, `search`, `sort_by`,
  `sort_direction`; `list_firewall_groups` accepts `limit`, `offset` (these
  paging parameters are not yet part of the published API contract).
- `ibee.build_idempotency_key` / `build_stable_idempotency_key` (the portal's key
  format), and the retry policy helpers in `ibee.retry`.
- `IbeeEnvironment.from_name("dev" | "development" | "prod" | "production")`.
- `block_storage.delete_block_volume(..., idempotency_key=...)` (query parameter;
  not yet part of the published API contract).
- `__version__` is exported from `ibee`.

### Changed

- **Retries.** Only `GET`/`HEAD`/`OPTIONS` requests, and writes carrying an
  idempotency key on a route that honours it, are retried, and only on 429, 502,
  503 and 504. 0.3.0 also retried 408, 409 and every 5xx for every method,
  including unkeyed creates. `Retry-After` is honoured up to 30 s (was 60 s).
  Connections that could not be opened are still retried for any method; read
  timeouts and dropped connections are retried only for retry-safe requests.
- **Idempotency keys are optional and auto-filled.** On the 22 cloud/GPU VM write
  methods `idempotency_key` is now `Optional` (it was required); when omitted the
  SDK generates a portal-style key, reuses it on every retry and records it on
  errors. Block-storage create/attach/detach/resize/delete also auto-fill keys.
  Caller keys must be 1-128 printable ASCII characters without spaces.
- **Lists return everything.** `list_cloud_vms`, `list_gpu_vms` and
  `list_firewall_groups` called without `limit`/`offset` now page through all
  results (100 per request, de-duplicated); 0.3.0 silently returned only the
  server's first 10.
- **Typed errors from every method.** All error responses are raised by the
  transport as the typed classes above (for example a 404 on `list_*` is now a
  `NotFoundError`, a 422 an `UnprocessableEntityError`). All remain `ApiError`
  subclasses.
- **Token/environment check.** A development token used against
  `api.ibee.ai`, or a production token against `api.ibee.co.in`, raises
  `IbeeValidationError(code="token_environment_mismatch")`; empty tokens or tokens
  with line breaks raise `invalid_token`.
- **Base URL validation.** `base_url` must be an absolute `https://` URL (`http://`
  only for localhost) without credentials, query, fragment or dot segments.
- `workspace_id` errors are `IbeeValidationError(code="invalid_workspace_id")`
  (still `ValueError`, same message); a positive `int` is accepted.
- Path parameters are percent-encoded, so an identifier cannot alter the request path.
- `X-Organization-Id`, `X-Workspace-Id` and `X-Project-Id` headers are never sent.
- Billable create bodies over 64 KiB raise `IbeeValidationError(code="request_body_too_large")`
  before sending (the API would answer 413).

### Fixed

- Creates replayed after a committed first attempt no longer retry into a 409.
- VM and firewall-group lists no longer cap at 10 items.

### Deprecated

- `ibee.billing.admission` (`enforce_billing_eligibility`,
  `enforce_compute_plan_eligibility`) is unused and will be removed in 0.5.0. Use
  `client.billing.require_resource_eligibility` instead.
