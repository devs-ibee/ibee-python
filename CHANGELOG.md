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

- **Portal-parity networking** (sync and async; methods marked "not yet part of
  the published API contract" may change):
  - VPCs: `create_vpc` checks the name (1-80), a custom `cidr` (RFC1918, aligned,
    /22-/28; the error suggests the aligned network) and sends `auto_cidr=false`
    with it; `connectivity_type` accepts `private` (the portal default);
    `nat_billing_catalog` for `nat_gateway` VPCs; `check_site`. `delete_vpc`
    refuses while nodes are attached or a NAT gateway exists, and
    `delete_nat_gateway=True` deletes the gateway first and waits for it.
    `list_networking_sites(available_only=True)`.
  - Subnets: `create_vpc_subnet` reads the VPC and checks containment, overlap,
    the 10-subnet quota and `prefix_length`; DNS lists must be IPv4.
  - Nodes: `attach_vpc_node(requested_private_ip=...)` (checked against the
    subnet: not the network, broadcast or gateway address) and connectivity rules
    with `check_state=True`.
  - NAT gateways: `create_nat_gateway(billing_catalog=..., preflight_billing=...)`
    (only for `nat_gateway` VPCs; Reserved IP eligibility);
    `delete_nat_gateway(public_ip_action="reserve"|"release", billing_catalog=..., wait=...)`;
    new `replace_nat_gateway_public_ip` and `wait_for_nat_gateway_absent`.
  - Port forwarding: `target_type` (`vm`/`vip`) and `target_vm_ids`; ports must be
    1-65535; duplicate protocol/external port, gateway availability and the
    target (NAT-connected node or MetalLB virtual IP) are checked first.
  - New virtual-IP methods: `list_vpc_virtual_ips`, `get_vpc_virtual_ip`,
    `create_vpc_virtual_ip`, `delete_vpc_virtual_ip`.
  - Reserved IPs: `reserve_ip(billing_catalog=..., check_billing=...)`; label and
    reverse-DNS rules; release, attach, move and detach read the IP first and
    apply the portal's rules (`attach_reserved_ip(detach_from_service=True)` moves
    an IP off a NAT gateway or virtual IP). New
    `convert_vm_public_ip_to_reserved_ip` (with a RESERVED-IP billing check) and
    `attach_reserved_ip_to_virtual_ip`. New `ReservedIpTargetUnsupportedError`
    (a `NotFoundError`) explains attach/move to a VM without a VPC attachment.
  - Firewalls: new `list_firewall_group_summaries`; `create_firewall_group`
    rejects duplicate names (any case) and `is_default=True`; rule create/update
    check protocol, ports and IPv4 remote targets like the portal and send its
    defaults (tcp, ingress, allow, `0.0.0.0/0`); system-managed rules cannot be
    changed or deleted; attachment `limit` 1-500.
  - Load balancers: `policy`, `health_check` and `observability` on create and
    update; `tls` defaults to managed passthrough/terminate for
    `tls_passthrough`/`https`; custom certificates, sticky sessions on L4 and
    custom domains on non-HTTPS are rejected; backends, rules and custom domains
    are validated; `include_deleted` on list and get; `check_billing` preflight.
  - Types: `VpcVirtualIp`, `FirewallGroupSummary`, `LoadBalancerCustomDomain`;
    `NatGateway.public_ip_source`/`billing_catalog`/..., `NatPortForwardingRule.target_type`/...,
    `ReservedIp.allocation_method`/`attached_allocation_id`/`attached_network_id`/...,
    `LoadBalancer.custom_domain`/`activated_at`/`deleted_at`/`deleted_by`.
  - `ibee.IbeeBillingWarning`; `NAT_GATEWAY_SKU_CODE`/`RESERVED_IP_SKU_CODE`;
    the networking rules in `ibee.validation` (CIDR, host-in-subnet, ports, remote
    targets, reverse DNS, load-balancer bodies) and flows in `ibee.networking_workflows`.

- Storage (Block Storage, Object Storage, CDN) follows the portal:
  - `block_storage.attach_block_volume_to_vm` / `detach_block_volume_from_vm`:
    attach a volume to (or detach it from) a cloud or GPU VM the way the portal
    does. The SDK reads the volume, picks the VM endpoint from its `vm_type`,
    sends its Block Storage SKU as `billing_catalog`, and with `wait=True` polls
    the operation (every 2 s, up to 120 s) and re-reads the volume.
  - `block_storage.wait_for_volume_operation`, `iter_block_volumes` and
    `list_all_block_volumes`; `list_block_volumes` takes `site_id`, `vm_type`,
    `limit` (1-1000) and `offset`; `list_block_volume_operations` takes `limit`
    (1-200).
  - `create_block_volume` accepts `vm_type` and `delete_on_termination` (not yet
    part of the published API contract), fills `site_name` from the compute
    sites (`resolve_site_name=True`, needs `vm.read`, skipped when not allowed)
    and sends its idempotency key in the body and as `X-Idempotency-Key`.
  - `delete_block_volume` and `resize_block_volume` take `check_state`;
    `attach_block_volume` (node level) takes `check_state`.
  - `object_storage.iter_buckets` / `list_all_buckets` (follow
    `next_continuation_token`) and `object_storage.delete_s3credential`, an alias
    of `revoke_s3credential` named after what the API does (a permanent delete).
  - `create_bucket(preflight_billing=)`, `create_s3credential(preflight_billing=)`,
    `cdn.create_cdn_distribution(preflight_billing=, check_origin_public=)` and
    `cdn.create_cdn_custom_domain(preflight_billing=)` run the portal's billing
    check first (OBJECTST-STD; CDN without a SKU; CUSTOMDO-STD with 19 900 minor
    units).
  - `object_storage.delete_bucket(skip_preflight=, check_state=)`.
  - `cdn.list_cdn_cache_policies` and `cdn.get_cdn_distribution_metrics(range=)`
    (not yet part of the published API contract; behaviour may change) and
    `cdn.wait_for_cdn_custom_domain` (verify every 15 s, up to 600 s).
  - `ibee.CdnPurgeFailedError` (subclass of `ApiError`).
  - Types: `BillingCatalogSelection` / `BillingSkuReference`;
    `S3Credential.organization_id`, `workspace_id`, `permission_type`,
    `bucket_scope`, `allowed_buckets` and `created_by_user_id`.
  - The storage rules in `ibee.validation` (`validate_block_volume_name`,
    `validate_bucket_name`, `build_s3_credential_body`, `build_cdn_purge_body`,
    `resolve_object_storage_region`, `validate_cdn_index_document`,
    `normalize_cdn_domain`, ...) and flows in `ibee.storage_workflows`.

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

- **Networking rules are checked before sending**, and several networking writes
  read current state first (pass `check_state=False` to skip): `delete_vpc`,
  `create_vpc_subnet`, `create_nat_gateway`, `create_nat_port_forwarding_rule`,
  `update_nat_port_forwarding_rule` (when ports change or it is enabled),
  `release_reserved_ip`, `attach_reserved_ip`, `move_reserved_ip`,
  `detach_reserved_ip`, `create_firewall_group`, `update_firewall_rule` and
  `delete_firewall_rule`. `detach_reserved_ip` on an unattached IP returns it
  without a request.
- VPC `cidr` outside /22-/28 or RFC1918 space is rejected locally (the API
  answered 422). `create_firewall_group(is_default=True)` raises (such groups were
  hidden from lists). Firewall rules default to `0.0.0.0/0` and send the portal's
  explicit defaults. `connectivity_type="public"` emits `DeprecationWarning`;
  a NAT gateway (or `nat_gateway` VPC) created without a billing catalog emits
  `IbeeBillingWarning`.
- `delete_nat_gateway` returns `True`/`False` with `wait=True` (otherwise `None`).
- The raw clients (`with_raw_response`) keep the 0.3.0 request bodies; use the
  high-level methods for the new fields and checks.

- **Block Storage checks (portal rules).** Volume ids must be 24 hexadecimal
  characters. Create: name 3-255 lowercase letters, numbers and hyphens (the
  error suggests a valid name; nothing is renamed silently), size a whole number
  of GB from 10 to 10000, non-blank `site_id`, `volume_class`, `replica_count`
  1-5, and `sku_code` upper-cased (root-disk SKUs rejected). Delete refuses an
  attached or busy volume unless `force=True`. Resize refuses shrinking, and an
  attached volume needs `vm_state="stopped"`/`"suspended"` or
  `allow_online=True`. Node-level detach needs `confirm_unmounted`, `force` or a
  stopped/suspended `vm_state`; `node_name` is now optional (the volume's only
  attachment is used).
- **VM volume attach/detach.** `attach_*_vm_volume` also refuses a volume created
  for the other VM type, and without `block-storage.read` asks for an explicit
  `billing_catalog`; the VM checks are skipped when the token lacks `vm.read`.
  `detach_*_vm_volume` volume ids must be 24 hexadecimal characters.
- **Object Storage.** `create_bucket` checks the portal's name rule (upper-case is
  rejected), `region` is now optional (defaults to `in-south-1` on
  https://api.ibee.ai and `in-south-2` on https://api.ibee.co.in; required for
  other base URLs), sends `object_lock_enabled=true` with `default_retention`,
  and checks the retention mode and days (1-36500) or years (1-100).
  `delete_bucket` reads the bucket first and refuses one with Object Lock or with
  objects (the API never deleted contents; the old docstring was wrong).
  `create_s3credential` always sends `permission_type` (default `admin_rw`),
  `bucket_scope` and `allowed_buckets`; `specific` scope needs `object_rw`/
  `object_ro` and at least one bucket; names are 1-100 characters. It is never
  retried automatically (the secret is returned once). `revoke_s3credential` is
  documented as a permanent delete.
- **CDN.** Distribution names (1-128), cache policies (`static-assets`, `media`,
  `short`, `no-cache`), origins, website `index_document`, custom domains
  (trimmed, lower-cased, host name with a subdomain), generate-URL options and
  purge selectors are checked before sending. `update_cdn_distribution` needs at
  least one field. `purge_cdn_cache` raises `CdnPurgeFailedError` when the API
  answers `success: false` (pass `raise_on_failure=False` for the 0.3.0
  behaviour). CDN and Block Storage errors are now typed `ApiError` subclasses.

### Fixed

- Creates replayed after a committed first attempt no longer retry into a 409.
- VM and firewall-group lists no longer cap at 10 items.
- VM creates now send `billing_catalog` (0.3.0 creates always failed with 422).
- Deleting a VM with an auto-assigned public IP no longer fails with 400.
- Resizes now move billing to the target plan's SKU.
- VM `id` is no longer `None` for records the API returns with `_id`.
- HTTPS and TLS-passthrough load balancers no longer fail with 422 when `tls` is
  omitted; custom certificates are refused before they cause a server error.
- Firewall rules without a port for tcp/udp, with `port_end < port_start` or with
  IPv6 targets are refused before they cause a server error.
- `load_balancers.list_load_balancers(status="deleted")` now returns deleted
  load balancers (sends `include_deleted=true`).

- VM volume attach through `attach_*_vm_volume` / `attach_block_volume_to_vm`
  no longer fails with 422 (the Block Storage SKU is sent).
- `create_s3credential` no longer fails with 422 when `permission_type` is
  omitted.
- A purge the CDN did not perform is no longer reported as a success.

### Deprecated

- `ibee.billing.admission` (`enforce_billing_eligibility`,
  `enforce_compute_plan_eligibility`) is unused and will be removed in 0.5.0. Use
  `client.billing.require_resource_eligibility` instead.
