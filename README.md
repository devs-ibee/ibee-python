# IBEE Solutions Python SDK

Official Python SDK for the IBEE Solutions API. Manage cloud VMs, GPU VMs,
VPC networking, Reserved IPs, firewalls, load balancers, object storage,
Block Storage, CDN, and secrets programmatically.

## Installation

```bash
pip install ibee
```

## Usage

```python
from ibee import Ibee

client = Ibee(token="YOUR_TOKEN")

# Product create methods send one request. The public API edge checks billing
# authoritatively before routing billable creates. Applications can optionally
# call client.billing.require_resource_eligibility(...) first (see "Billing preflight").

# List cloud VMs (every page)
vms = client.cloud_vms.list_cloud_vms(workspace_id="907479")

# Create a cloud VM
vm = client.cloud_vms.create_cloud_vm(
    workspace_id="907479",
    idempotency_key="create-web-server-01",
    name="web-server",
    site_id="site_blr_01",
    plan_id="plan_standard_2c_4g",
    template_id="tmpl_ubuntu_2204",
    os_distro="ubuntu",
    os_type="linux",
    cpu=2,
    ram_mb=4096,
)

# List GPU VMs
gpu_vms = client.gpu_vms.list_gpu_vms(workspace_id="907479")

# Discover typed sites, plans, and images before creating a VM
sites = client.compute_catalog.list_compute_sites(workspace_id="907479")
plans = client.compute_catalog.list_compute_plans(
    workspace_id="907479",
    vm_type="cloud",
    site_id="site_blr_01",
    currency="INR",
    billing_interval="MONTHLY",
)
images = client.compute_catalog.list_compute_images(
    workspace_id="907479",
    vm_type="cloud",
    site_id="site_blr_01",
)

# Manage secrets
stores = client.secret_store.list_secret_stores(workspace_id="907479")

# List object storage buckets
buckets = client.object_storage.list_buckets(workspace_id="907479")
bucket = client.object_storage.create_bucket(
    workspace_id="907479",
    name="production-assets",
    region="in-south-1",
    is_public=False,
)
credential = client.object_storage.create_s3credential(
    workspace_id="907479",
    name="application-key",
    bucket_scope="specific",
    allowed_buckets=["production-assets"],
)

# Create an isolated VPC and reserve a public IP
vpc = client.vpcs.create_vpc(
    workspace_id="907479",
    name="production",
    site_id="site_blr_01",
    cidr="10.20.0.0/24",
)
reserved_ip = client.reserved_ips.reserve_ip(
    workspace_id="907479",
    site_id="site_blr_01",
    label="production-ingress",
)

# Firewall and load-balancer APIs use the same workspace scope
firewall_groups = client.firewalls.list_firewall_groups(workspace_id="907479")
load_balancers = client.load_balancers.list_load_balancers(workspace_id="907479")
```

The `vpcs` resource also manages subnets, VM attachments, NAT gateways, and
port-forwarding rules. `reserved_ips` includes attach, move, and detach;
`firewalls` and `load_balancers` provide their complete public lifecycle.
Synchronous and async clients expose matching methods.

To create a VM with explicit placement, pass the selected IDs. Omit `site_id`
to let IBEE select an available site automatically:

```python
vm = client.cloud_vms.create_cloud_vm(
    workspace_id="907479",
    idempotency_key="create-web-server-01",
    name="web-server-01",
    site_id="site_blr_01",
    os_distro="ubuntu",
    os_type="linux",
    template_id="tmpl_ubuntu_2204",
    plan_id="plan_standard_2c_4g",
    cpu=2,
    ram_mb=4096,
    disk_gb=80,
    ssh_key_ids=["ssh_key_123"],
    tags=["prod", "web"],
)
```

`plan_id` is the selected instance plan. `template_id` is the selected OS
template or image. `ssh_key_ids` are the SSH keys to inject at first boot.
In the current SDK, `cpu` and `ram_mb` are still required fallback fields even
when `plan_id` is provided.

## Secret Store lifecycle

The synchronous and asynchronous Secret Store clients expose the complete store,
secret-version, application-identity, and identity-scope lifecycle. Every call
is scoped with `workspace_id`; value and identity-access responses can contain
sensitive credentials and should never be logged.

```python
store = client.secret_store.create_secret_store(
    workspace_id="710995", name="payments"
)
secret = client.secret_store.create_secret(
    store.id,
    workspace_id="710995",
    secret_name="database",
    value={"username": "payments", "password": "replace-me"},
)
client.secret_store.patch_secret_value(
    secret.id,
    workspace_id="710995",
    value={"username": "payments-v2"},
)
versions = client.secret_store.list_secret_versions(
    secret.id, workspace_id="710995"
)
client.secret_store.rollback_secret(
    secret.id, workspace_id="710995", version=1
)
```

Stores support archive, unarchive, and explicit permanent deletion. Secrets
support batch creation, soft deletion, undelete, version destruction, rollback,
and permanent deletion. Workload identities support AppRole or Kubernetes
authentication, credential rotation, session revocation, and per-store scopes.
Permanent-delete and version-destroy operations are irreversible.

## Complete VM lifecycle

Cloud and GPU VM clients expose matching power, access, resize, volume,
monitoring, snapshot, and backup operations. VM writes take an optional
`idempotency_key`; the SDK generates one when you omit it (see
"Retries & idempotency"):

```python
# Power and access
operation = client.cloud_vms.stop_cloud_vm(
    "vm_123",
    workspace_id="907479",
    idempotency_key="stop-vm-123-01",
)
client.cloud_vms.update_cloud_vm_access(
    "vm_123",
    workspace_id="907479",
    idempotency_key="rotate-access-vm-123-01",
    ssh_key_ids=["ssh_key_456"],
    ssh_key_mode="add",
)

# Precheck and apply a resize
decision = client.cloud_vms.precheck_cloud_vm_resize(
    "vm_123", workspace_id="907479", cpu=4, ram_mb=8192
)
operation = client.cloud_vms.resize_cloud_vm(
    "vm_123",
    workspace_id="907479",
    idempotency_key="resize-vm-123-01",
    cpu=4,
    ram_mb=8192,
)

# Volumes, events, and time-series metrics
client.cloud_vms.attach_cloud_vm_volume(
    "vm_123",
    workspace_id="907479",
    idempotency_key="attach-volume-789-01",
    volume_id="volume_789",
)
events = client.cloud_vms.list_cloud_vm_events("vm_123", workspace_id="907479")
metrics = client.cloud_vms.get_cloud_vm_metrics_timeseries(
    "vm_123", workspace_id="907479", range="24h"
)

# Snapshots and backups
snapshot = client.cloud_vms.create_cloud_vm_snapshot(
    "vm_123", workspace_id="907479", name="before-upgrade", mode="root_only"
)
policy = client.cloud_vms.enable_cloud_vm_backups(
    "vm_123", workspace_id="907479", retention_days=14
)
backup = client.cloud_vms.create_cloud_vm_backup_run(
    "vm_123", workspace_id="907479", reason="before-upgrade"
)

# Short-lived graphical console session. Treat connect_url as a secret: do not
# log or persist it, and close the session when finished.
session = client.vm_console.create_vm_console_session(
    workspace_id="907479", vm_id="vm_123", vm_type="cloud"
)
client.vm_console.close_vm_console_session(
    session.session_id, workspace_id="907479", reason="finished"
)
```

Use the corresponding `gpu_vms` methods for GPU instances. Snapshot and backup
item/status methods use family-specific public routes, so cloud and GPU recovery
records cannot be mixed accidentally. The async client provides the same method
names and arguments.

## Environments & tokens

The client defaults to the production API (`https://api.ibee.ai/v1`).
`IbeeEnvironment.PRODUCTION` is an explicit alias for that default. Use
`IbeeEnvironment.DEVELOPMENT` for the development API (`https://api.ibee.co.in/v1`):

```python
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(token="IBEE_DEV_TOKEN", environment=IbeeEnvironment.DEVELOPMENT)

# Resolve an environment name, for example from the IBEE_ENV variable:
env = IbeeEnvironment.from_name("dev")  # dev/development or prod/production
```

An explicit `base_url` wins over `environment`. The base URL must be an absolute
`https://` URL (plain `http://` is accepted only for `localhost`, `127.0.0.1` and
`::1`) without credentials, a query string, a fragment, or `.`/`..` segments.

Tokens are checked before anything is sent: a token must be non-empty and must
not contain line breaks, and a development token (`ibee_dev_key_...`) cannot be
used against the production host, nor a production token (`ibee_prod_key_...`)
against the development host. String tokens are checked when the client is
created; callable and async tokens on every request. Violations raise
`IbeeValidationError` with `code == "token_environment_mismatch"` or
`"invalid_token"`.

`workspace_id` must be a positive numeric string such as `"710995"` (a positive
`int` is also accepted). It is validated before every request.

## Errors

Client-side validation failures raise `ibee.IbeeValidationError` (a subclass of
`ValueError`) before any HTTP request, with a stable `code` (for example
`invalid_workspace_id`, `invalid_idempotency_key`, `request_body_too_large`) and
the offending `field`.

Every HTTP error response raises a typed subclass of `ibee.core.api_error.ApiError`.
Each class subclasses the 0.3.0 class for its status code, so existing `except`
clauses keep working:

| Status | Class | Notes |
| --- | --- | --- |
| 400 | `BadRequestError`, `InvalidWorkspaceError` | |
| 401 | `UnauthorizedError` | invalid, revoked, or other-environment token |
| 402 | `PaymentRequiredError`, `BillingDeniedError` | `reason`, `sku_code`, `topup_allowed`, portal message |
| 403 | `ForbiddenError`, `InsufficientScopeError`, `WorkspaceNotAllowedError`, `ApiKeyInactiveError`, `RouteNotAvailableError`, `OrganizationRestrictedError`, `BillingForbiddenError` | `required_scope` on scope errors |
| 404 | `NotFoundError` | |
| 409 | `ConflictError` | never retried |
| 413 | `PayloadTooLargeError` | |
| 422 | `UnprocessableEntityError` | `message` lists `field: problem` |
| 423 | `OrganizationSuspendedError` | |
| 429 | `TooManyRequestsError` | `retry_after` |
| 500 | `InternalServerError` | |
| 502 | `BadGatewayError`, `BillingAdmissionError` | |
| 503 | `ServiceUnavailableError` | |
| 504 | `GatewayTimeoutError` | |

Every `ApiError` exposes `status_code`, `code` (stable, lower-case), `message`,
`reason`, `raw_body`, `details`, `request_id` (from `x-request-id`),
`retry_after`, `idempotency_key` and `retryable`. `body` keeps its 0.3.0 type.

```python
from ibee.errors import BillingDeniedError, InsufficientScopeError, is_payment_block_error

try:
    client.cloud_vms.create_cloud_vm(...)
except BillingDeniedError as exc:
    print(exc.message)          # portal wording, e.g. "Add at least ₹2,000 ..."
    if exc.topup_allowed:
        print("Add credits in the IBEE portal (Billing > Add Credits), then retry.")
except InsufficientScopeError as exc:
    print(f"token is missing scope {exc.required_scope}")
```

## Retries & idempotency

The SDK retries a request only when repeating it cannot create or change
anything twice: `GET`/`HEAD`/`OPTIONS` requests, and writes that carry an
idempotency key on a route that honours it. Those requests are retried on HTTP
429, 502, 503 and 504 (up to `max_retries`, default 2), honouring `Retry-After`
up to 30 seconds. HTTP 408, 409, 500 and other 4xx responses are never retried.
A connection that could not be opened is retried for any method.

Routes that honour idempotency keys, and fill one automatically when you omit it:

* the 22 cloud/GPU VM writes (create, delete, start, stop, reboot, access,
  resize, resize-plan, resize-root-disk, attach-volume, detach-volume) through
  the `X-Idempotency-Key` header;
* block-storage volume create, attach, detach and resize (body `idempotency_key`)
  and delete (query `idempotency_key`).

Generated keys follow the portal's format (`cloud-vm-start-<vm id>-<hash>-<random>`).
The same key is reused on every automatic retry and is recorded on any raised
error as `error.idempotency_key`, so you can retry the logical call safely:

```python
from ibee import build_idempotency_key

key = build_idempotency_key("cloud-vm-reboot", "vm_123")
client.cloud_vms.reboot_cloud_vm("vm_123", workspace_id="907479", idempotency_key=key)
```

A caller-supplied key must be 1-128 printable ASCII characters without spaces.
Networking, snapshot, backup and object-storage writes do not deduplicate keys
yet, so the SDK never retries them.

## Waiting for operations

VM creates, deletes, power actions, access updates, resizes and volume
attach/detach return an operation. Wait for it to finish:

```python
from ibee.errors import OperationFailedError, OperationTimeoutError

accepted = client.cloud_vms.start_cloud_vm("vm_123", workspace_id="907479")
try:
    operation = client.cloud_vms.wait_for_compute_operation(
        accepted.operation_id,
        workspace_id="907479",
        timeout=1200,       # seconds, 1-7200
        poll_interval=5,    # seconds, 1-60
    )
except OperationFailedError as exc:      # failed, cancelled or timed_out on the server
    print(exc.status, exc.error_code, exc.error_message)
except OperationTimeoutError as exc:     # still running when the client stopped waiting
    print(f"still {exc.last_status}; resume with operation {exc.operation_id}")
```

`client.gpu_vms.wait_for_compute_operation`, `ibee.wait_for_compute_operation(client, ...)`
and the async client offer the same helper. Two consecutive transient poll
failures (429/502/503/504 or a network error) are tolerated; a 404 stops
immediately. Pass `raise_on_failure=False` to get the failed operation back
instead of an exception, and `on_update=` to observe each poll.

## Pagination

`list_cloud_vms`, `list_gpu_vms` and `list_firewall_groups` return every item:
without `limit`/`offset` they fetch all pages (100 per request) and drop
duplicates. Pass `limit` (1-100) and/or `offset` for a single page, and use
`search`, `sort_by` (`created_at`, `name`, `status`, `os_type`) and
`sort_direction` (`asc`, `desc`) on the VM lists. These paging parameters are not
yet part of the published API contract; behaviour may change.

```python
for vm in client.cloud_vms.iter_cloud_vms(workspace_id="907479", sort_by="name", sort_direction="asc"):
    print(vm.name)

first_page = client.gpu_vms.list_gpu_vms(workspace_id="907479", limit=10)
```

The async client's `iter_*` methods return async iterators (`async for`).

## Billing preflight

Billable creates are admitted at the public API edge before the request reaches
the product service. This applies equally to raw REST, the Python and
TypeScript SDKs, and the CLI, so create methods send exactly one request. To
check billing first, as the portal does:

```python
from ibee.billing import estimate_eligibility_cost_minor

cost = estimate_eligibility_cost_minor("MONTHLY", 12500, count=1)  # HOURLY uses 731 hours
decision = client.billing.require_resource_eligibility(
    workspace_id="907479",
    sku_code="STANDARD-2-8-50",
    estimated_cost_minor=cost,
    resource_type="vm",
)
```

`require_resource_eligibility` returns the decision only when `allowed` is exactly
`True`, raises `BillingDeniedError` (402) with the portal's message otherwise, and
raises `BillingAdmissionError` (502) if billing returns an incomplete decision.
`check_resource_eligibility` returns the decision without raising. The decision
includes `billing_state`, `service_enforcement_state`, `effective_balance_minor`
or `credit_headroom_minor`, `allowed_operations` and `resource_limits`. Neither
call reserves funds; the edge repeats the check on the real create. Wallet
top-ups are only available in the IBEE portal (Billing > Add Credits); use
`ibee.billing.is_billing_topup_allowed(decision)` to decide whether to suggest one.

## Block Storage and CDN

Block Storage is exposed at `client.block_storage` with list, create, get,
delete, operations, attach, detach, and resize methods. CDN is exposed at
`client.cdn` with distribution, static-website, custom-domain, URL-generation,
verification, and cache-purge methods.

Requires Python 3.10+.

## Async usage

```python
import asyncio
from ibee import AsyncIbee

async def main():
    client = AsyncIbee(token="YOUR_TOKEN")
    vms = await client.cloud_vms.list_cloud_vms(workspace_id="907479")
    print(vms)

asyncio.run(main())
```

## Authentication

Generate a platform API token from the IBEE portal under Settings > Platform API Tokens. Use the token with the `token` parameter when creating the client.

## Documentation

Production API reference: [https://ibee.ai/docs/api-reference](https://ibee.ai/docs/api-reference)

## License

MIT
