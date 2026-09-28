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

- **Portal-parity VMs** (cloud and GPU, sync and async). `create_*_vm` resolves
  the plan (must be selectable and priced) and image for `site_id`, takes
  cpu/ram_mb/disk_gb (and GPU fields) from the plan and os fields from the image,
  and builds `billing_catalog` for `billing_term` (`HOURLY`/`MONTHLY`/`YEARLY`;
  cloud defaults to `HOURLY`, GPU sends the plan SKU as the portal does). New
  create parameters: `billing_term`, `billing_catalog`, `windows_license`,
  `ssh_keys`, `firewall_group_ids`, `vpc_id`, `subnet_id`,
  `network_connectivity`, `reserved_public_ip_id`, `requested_by`,
  `preflight_billing`. Passing `billing_catalog` with the full shape skips the
  lookups (one request).
- `delete_*_vm(public_ip_action=..., reserved_ip_label=..., reserved_ip_billing_catalog=...)`:
  the VM is read and an auto-assigned public IP is released by default, or kept
  as a Reserved IP (portal delete dialog).
- `resize_*_vm(plan_id=..., billing_term=..., billing_catalog=..., windows_license=...)`
  runs the precheck and only resizes when it is `in_place`; the new plan SKU is
  sent so billing follows the resize (Windows VMs keep their licence).
  `precheck_*_vm_resize(plan_id=...)`, `resize_*_vm_plan(plan_id=..., billing_catalog=...)`,
  `resize_*_vm_root_disk(billing_catalog=...)`.
- `check_state` on power, access, resize, delete, attach/detach, snapshot and
  restore methods (portal state matrix).
- `list_all_cloud_vms` / `list_all_gpu_vms`; VM records expose the API's `_id` as `id`.
- Recovery: `billing_catalog` on `create_*_vm_snapshot`, `enable_*_vm_backups`,
  `update_*_vm_backup_policy` and `create_*_vm_backup_run` (the API requires it;
  it cannot be listed publicly yet); `target_billing_catalog`,
  `target_volume_names` on restores and `vpc_id`/`subnet_id`/
  `network_connectivity`/`ssh_key_ids` on snapshot restores, with the new-VM
  plan, names and SKU resolved like the portal; `restorable_only` on
  `list_*_vm_backup_runs`; `preflight_billing` on snapshot create.
- New: `delete_cloud_vm_backup_run` / `delete_gpu_vm_backup_run` and
  `list_all_cloud_vm_backup_runs` / `list_all_gpu_vm_backup_runs` (not yet part
  of the published API contract); waiters `wait_for_*_vm_snapshot`,
  `wait_for_*_vm_snapshot_restore`, `wait_for_*_vm_backup_restore`,
  `wait_for_*_vm_backup_run`; `wait_for_operation` alias.
- `attach_*_vm_volume` reads the volume and sends its Block Storage SKU as
  `billing_catalog`; `vm_console.create_vm_console_session(check_state=...)`.
- Errors: `ResizeBlockedError` (409 with a precheck decision),
  `RecoveryFailedError`, `RecoveryRestoreFailedError`.
- Rules in `ibee.validation` (now a package; imports unchanged): VM ids, names and
  batches, SSH public keys, billing SKUs and terms (`build_vm_billing_catalog`,
  `billing_catalog_for_term`, `with_attached_billing_skus`), VPC placement, state
  matrix, public-IP choice on delete, access updates, resize ranges, metrics,
  snapshot/backup schedules, restore modes and naming. `IbeeValidationError` has
  `details`.

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

- **VM rules are checked before sending.** VM ids must be 24 hexadecimal
  characters and operation ids `op_` + 24 hex characters (blocks operator-only
  paths such as `gpu-vms/all`); `site_id` is required on VM create (the API
  answers 422 without it); `cpu`, `ram_mb`, `os_type`, `os_distro`, `gpu_count`
  and `gpu_model` are now optional on create (taken from the plan/image) but must
  match them when given; `disk_gb` is always sent (0.3.0 left it to a 50/140 GB
  server default).
- VM access updates, `resize_*`, `resize_*_vm_plan` and `resize_*_vm_root_disk`
  read the VM first by default (`check_state=False` skips it); resize also runs
  the precheck. Backup enable/update read the saved policy.
- Snapshot create, backup enable and manual backup run raise
  `IbeeValidationError` without `billing_catalog` (0.3.0 always got 422).
  Backup schedules are `daily` or `weekly` only (weekly needs `day_of_week`),
  with a valid IANA time zone; `next_run_at` must be timezone-aware.
- `detach_*_vm_volume` needs `confirm_unmounted=True` or `force=True`.
- Snapshot restores send `auto_start=True` by default; backup restores no longer
  send `auto_start` (the API ignores it).
- Console sessions are cloud-only (`vm_type="gpu"` is rejected locally).
- `get_*_vm_bandwidth` defaults `month` to the current UTC month.
- VM creates are never retried automatically, even with an idempotency key.

### Fixed

- Creates replayed after a committed first attempt no longer retry into a 409.
- VM and firewall-group lists no longer cap at 10 items.
- VM creates now send `billing_catalog` (0.3.0 creates always failed with 422).
- Deleting a VM with an auto-assigned public IP no longer fails with 400.
- Resizes now move billing to the target plan's SKU.
- VM `id` is no longer `None` for records the API returns with `_id`.

### Deprecated

- `ibee.billing.admission` (`enforce_billing_eligibility`,
  `enforce_compute_plan_eligibility`) is unused and will be removed in 0.5.0. Use
  `client.billing.require_resource_eligibility` instead.
