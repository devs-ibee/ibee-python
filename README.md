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

# Product create methods send one write request. VM creates first read the plan
# and image (see "Complete VM lifecycle"). The public API edge checks billing
# authoritatively before routing billable creates. Applications can optionally
# call client.billing.require_resource_eligibility(...) first (see "Billing preflight").

# List cloud VMs (every page)
vms = client.cloud_vms.list_cloud_vms(workspace_id="907479")

# Create a cloud VM like the portal: the SDK looks up the plan and image for the
# site, takes cpu/RAM/disk from the plan and builds the plan's billing_catalog
# for the chosen term (HOURLY by default). site_id is required.
vm = client.cloud_vms.create_cloud_vm(
    workspace_id="907479",
    name="web-server",
    site_id="site_blr_01",
    plan_id="plan_standard_2c_4g",
    template_id="tmpl_ubuntu_2204",
    billing_term="MONTHLY",
    ssh_keys=["ssh-ed25519 AAAAC3Nza... me@laptop"],
)
client.cloud_vms.wait_for_compute_operation(vm.operation_id, workspace_id="907479")

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
    permission_type="object_rw",  # admin_rw (default) keys cannot be limited to buckets
    bucket_scope="specific",
    allowed_buckets=["production-assets"],
)

# Create an isolated VPC (private by default in the portal) and reserve a public IP
vpc = client.vpcs.create_vpc(
    workspace_id="907479",
    name="production",
    site_id="site_blr_01",
    cidr="10.20.0.0/24",  # RFC1918, aligned, /22-/28
    connectivity_type="private",
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

The `vpcs` resource also manages subnets, VM attachments, NAT gateways,
port-forwarding rules and virtual IPs. `reserved_ips` includes attach, move,
detach and convert; `firewalls` and `load_balancers` provide their complete
public lifecycle. Synchronous and async clients expose matching methods; see
"Networking" below for the portal rules the SDK applies.

To create a VM, pass the site, plan and image you selected. `site_id` is
required (list sites with `compute_catalog.list_compute_sites`); the SDK reads
the plan and image, fills the shape from them and builds `billing_catalog` for
the billing term, like the portal:

```python
vm = client.cloud_vms.create_cloud_vm(
    workspace_id="907479",
    name="web-server-01",
    site_id="site_blr_01",
    plan_id="plan_standard_2c_4g",
    template_id="tmpl_ubuntu_2204",
    billing_term="MONTHLY",          # default HOURLY; the plan must offer it
    ssh_keys=["ssh-ed25519 AAAAC3Nza... me@laptop"],
    tags=["prod", "web"],
)
```

`plan_id` is the selected instance plan and `template_id` the selected OS
template or image. `cpu`, `ram_mb`, `disk_gb`, `os_type` and `os_distro` are
optional: they default to the plan and image and, when given, must match them.
For a single-request create without the plan and image lookups, pass
`billing_catalog` together with the full shape (`cpu`, `ram_mb`, `disk_gb`,
`os_type`, `os_distro`, and `gpu_count` for GPU VMs). With an API token prefer
`ssh_keys` (public keys) over `ssh_key_ids`.

## Secret Store lifecycle

The synchronous and asynchronous Secret Store clients expose the complete store,
secret-version, application-identity, and identity-scope lifecycle. Every call
is scoped with `workspace_id` (a 2-128 digit id for Secret Store); value and
identity-access responses can contain sensitive credentials and should never be
logged.

```python
store = client.secret_store.create_secret_store(
    workspace_id="710995",
    name="payments",
    preflight_billing=True,  # deprecated no-op; upstream decides admission
    if_exists="return",      # return the existing store instead of raising on 409
)
secret = client.secret_store.create_secret(
    store.id,
    workspace_id="710995",
    secret_name="Database",  # trimmed and lower-cased -> "database"
    value={"username": "payments", "password": "replace-me"},
    preflight_billing=True,
)
client.secret_store.patch_secret_value(
    secret.id,
    workspace_id="710995",
    value={"username": "payments-v2", "legacy_key": None},  # None deletes a key
)
versions = client.secret_store.list_secret_versions(
    secret.id, workspace_id="710995"
)
client.secret_store.rollback_secret(
    secret.id, workspace_id="710995", version=1
)
every_store = client.secret_store.list_all_secret_stores(workspace_id="710995")
```

Stores support archive, unarchive, and explicit permanent deletion. Secrets
support batch creation, soft deletion, undelete, version destruction, rollback,
and permanent deletion. Workload identities support AppRole or Kubernetes
authentication, credential rotation, session revocation, and per-store scopes.
Permanent-delete and version-destroy operations are irreversible.

The client applies the portal's rules before sending anything
(`IbeeValidationError`):

* store names are trimmed, 1-128 characters, and need a letter or digit;
  `update_secret_store` needs `name` or `description`;
* secret names are trimmed and lower-cased, then must be 2-64 characters of
  `a-z`, `0-9` and `-`, starting with a letter or digit;
* secret values are objects with at least one key; keys are trimmed and must not
  be blank or collide, string values must not be empty;
* bodies are limited to 64 KiB (`ibee.validation.chunk_batch_secrets` splits a
  large batch); batches hold 1-500 items; version lists 1-100 integers >= 1;
  `cas` is an integer >= 0; `page` >= 1 and `limit` 1-200; `q` at most 128 characters;
* identities: `token_policy_mode` defaults to `read_only` and is always sent;
  Kubernetes identities need `k8s_namespace` and `k8s_service_account`;
  `update_secret_identity` needs `token_policy_mode`;
* scopes default to `read_only` with version reads allowed; rollback and destroy
  need `read_write`.

Portal pre-steps: `rollback_secret` refuses the current, unknown or destroyed
version (`check_target=True` by default); `rotate_secret_identity_secret_id(check_auth_method=True)`
refuses Kubernetes or disabled identities; `create_secret_identity_scope(check_store=True)`
refuses a store that is not active or already granted; `undelete_secret` without
`versions` restores the current version. Each pre-step is skipped with a warning
when the token lacks the read scope it needs.

Secret Store answers most refusals with HTTP 403, so the SDK picks the error
class from the message (all subclasses of the 0.3.0 classes):
`ResourceNotFoundError` (missing or other-workspace store, secret, identity or
scope), `OrganizationLifecycleError` (`state`, `operation`), `StoreNotActiveError`,
`IdentityDisabledError`, `AuthMethodMismatchError`, `ScopePermissionError`,
`StoreArchivedError` / `StoreDeletingError` (409), `SecretValueNotFoundError`
(404), `ScopeValidationError` (422), `CasConflictError` (502 after `cas`) and
`DeletionIncompleteError` (503, `failed_steps`; repeating the delete is safe).

`get_secret_identity_access` and `rotate_secret_identity_secret_id` issue a new
AppRole secret ID on every call (earlier ones stay valid), so they are never
retried automatically; neither is any Secret Store create or value write.
Runtime workload access (AppRole/Kubernetes login and runtime secret reads) is
not part of the public API yet.

## Complete VM lifecycle

Cloud and GPU VM clients expose matching power, access, resize, volume,
monitoring, snapshot, and backup operations, and apply the same rules the IBEE
portal applies before sending anything. A rule that fails raises
`IbeeValidationError` (a `ValueError`) with a stable `code` and `field`, before
any request. VM writes take an optional `idempotency_key`; the SDK generates one
when you omit it (see "Retries & idempotency"). VM ids are 24 hexadecimal
characters; list and get results expose them as `id`.

```python
WS = "907479"
VM = "66f0c2a1b4d3e5f601234567"

# Create: plan/image lookups, plan shape, billing SKU for the term, VPC placement.
op = client.cloud_vms.create_cloud_vm(
    workspace_id=WS,
    name="app-1",                   # letters, digits and hyphens
    site_id="site_blr_01",          # required
    plan_id="plan_standard_2c_4g",  # must be selectable and priced
    template_id="tmpl_ubuntu_2204",
    billing_term="HOURLY",          # HOURLY (default) | MONTHLY | YEARLY
    ssh_keys=["ssh-ed25519 AAAAC3Nza... me@laptop"],  # preferred over ssh_key_ids for API tokens
    firewall_group_ids=["fw_123"],  # at most one
    vpc_id="vpc_1", subnet_id="subnet_1", network_connectivity="private",  # private | nat | public_ip
    preflight_billing=True,         # deprecated no-op; upstream decides admission
)
# Windows images need the Windows licence SKU (not listed by the public API yet):
#   windows_license={"sku_id": ..., "sku_code": ..., "billing_options": [...]}
# GPU VMs take gpu_count/gpu_model from the plan and must use Linux images.

# Delete: an auto-assigned public IP is released by default, or kept as a Reserved IP.
client.cloud_vms.delete_cloud_vm(VM, workspace_id=WS)  # public_ip_action="release"
client.cloud_vms.delete_cloud_vm(
    VM,
    workspace_id=WS,
    public_ip_action="reserve",
    reserved_ip_billing_catalog=existing_reserved_ip.billing_catalog,  # Reserved IP SKU, same site
)

# Power and access. check_state=True applies the portal state rule first
# (start only when stopped, stop/reboot only when running).
client.cloud_vms.stop_cloud_vm(VM, workspace_id=WS, check_state=True)
client.cloud_vms.update_cloud_vm_access(  # running Linux VMs only
    VM,
    workspace_id=WS,
    ssh_key_mode="add",
    ssh_keys=["ssh-ed25519 AAAAC3Nza... me@laptop"],
)

# Resize to a plan: the precheck must say in_place, and billing moves to the new SKU.
decision = client.cloud_vms.precheck_cloud_vm_resize(VM, workspace_id=WS, plan_id="plan_4c_8g")
client.cloud_vms.resize_cloud_vm(VM, workspace_id=WS, plan_id="plan_4c_8g", billing_term="MONTHLY")
client.cloud_vms.resize_cloud_vm_plan(VM, workspace_id=WS, cpu=2, ram_mb=4096, confirm_downgrade=True)
client.cloud_vms.resize_cloud_vm_root_disk(VM, workspace_id=WS, new_size_gb=100)  # grow only

# Volumes: attach reads the volume's Block Storage SKU and checks state and site.
op = client.cloud_vms.attach_cloud_vm_volume(VM, workspace_id=WS, volume_id="66f0c2a1b4d3e5f601234999")
client.cloud_vms.wait_for_compute_operation(op.operation_id, workspace_id=WS, poll_interval=2, timeout=120)
client.cloud_vms.detach_cloud_vm_volume(VM, workspace_id=WS, volume_id="66f0c2a1b4d3e5f601234999", confirm_unmounted=True)

# Monitoring
events = client.cloud_vms.list_cloud_vm_events(VM, workspace_id=WS, limit=100)      # 1-500
series = client.cloud_vms.get_cloud_vm_metrics_timeseries(VM, workspace_id=WS, range="24h")
usage = client.cloud_vms.get_cloud_vm_bandwidth(VM, workspace_id=WS)  # current UTC month

# Snapshots. billing_catalog is the snapshot_storage SKU (SNAPSHOT-STD); the public
# API cannot list it yet, so copy it from an existing snapshot set.
snapshot = client.cloud_vms.create_cloud_vm_snapshot(
    VM, workspace_id=WS, name="before-upgrade", mode="root_only", billing_catalog=snapshot_sku
)
client.cloud_vms.wait_for_cloud_vm_snapshot(snapshot.snapshot_set_id, workspace_id=WS, vm_id=VM)
restore = client.cloud_vms.restore_cloud_vm_snapshot(
    snapshot.snapshot_set_id, workspace_id=WS, vm_id=VM, target_mode="new_vm"  # plan, names, SKU resolved
)
client.cloud_vms.wait_for_cloud_vm_snapshot_restore(restore.restore_id, workspace_id=WS)

# Backups. billing_catalog is the backup_storage SKU (BACKUP-STD).
client.cloud_vms.enable_cloud_vm_backups(
    VM,
    workspace_id=WS,
    schedule={"frequency": "weekly", "day_of_week": 6, "hour": 2, "timezone": "Asia/Kolkata"},
    billing_catalog=backup_sku,
)
run = client.cloud_vms.create_cloud_vm_backup_run(VM, workspace_id=WS, reason="pre-upgrade", billing_catalog=backup_sku)
client.cloud_vms.wait_for_cloud_vm_backup_run(run.run_id, workspace_id=WS)
points = client.cloud_vms.list_cloud_vm_backup_runs(VM, workspace_id=WS, restorable_only=True)
workspace_backups = client.cloud_vms.list_all_cloud_vm_backup_runs(workspace_id=WS)  # succeeded; status="all" for every run
client.cloud_vms.restore_cloud_vm_backup(VM, workspace_id=WS, recovery_point_id=run.recovery_point_id)
client.cloud_vms.delete_cloud_vm_backup_run(run.run_id, workspace_id=WS)
# list_all_*_vm_backup_runs and delete_*_vm_backup_run need the backend release that provides them
# (available on the development environment; production answers 404/405 until then).

# Short-lived graphical console session (cloud VMs only). Treat connect_url as a
# secret: do not log or persist it, and close the session when finished.
session = client.vm_console.create_vm_console_session(workspace_id=WS, vm_id=VM, vm_type="cloud")
client.vm_console.close_vm_console_session(session.session_id, workspace_id=WS, reason="finished")
```

Use the corresponding `gpu_vms` methods for GPU instances. The async client
provides the same method names and arguments.

Pre-steps are read-only requests (`vm.read`, and `block-storage.read` for attach).
Methods that can check the portal's VM state rules take `check_state`. The
state rules (for example "start needs a stopped VM") run only when you pass
`check_state=True`, as in 0.3.0 and the TypeScript SDK. A few reads are part of
the request itself and run by default: `update_*_access` (access rules),
`resize_*_vm_plan` (no-op and downgrade check), `resize_*_vm_root_disk` (grow
only), `delete_*_vm` (public IP choice; skipped for `public_ip_action="release"`) and
attach (the volume's SKU and site). Pass `check_state=False` to skip the reads
that are not needed to build the request.
The rules live in `ibee.validation` (for example `validate_vm_id`,
`resolve_delete_public_ip_action`, `build_vm_billing_catalog`,
`validate_backup_schedule`) and can be used directly.

Not available through the public API yet (so not in the SDK): listing the Windows
licence, snapshot, backup and Reserved IP SKUs; plan capacity checks; VM-side
public-network and VPC-attachment actions; GPU monitoring; password reveal; SSH
key management; ISO installs; workspace-wide snapshot lists; converting backups
to snapshots.

## Networking

Networking methods apply the portal's rules before sending and raise
`IbeeValidationError` when one fails. Methods that need the current state (for
example the VPC's CIDR and subnets) read it first; pass `check_state=False` to
skip those reads. When the token lacks the read scope (for example a key with
only `network.write`) those checks are skipped and the API enforces the rules;
pass `check_state=True` to require them. Methods marked "not yet part of the
published API contract" in their docstrings may change.

```python
from ibee import Ibee, IbeeValidationError

client = Ibee(token="YOUR_TOKEN")
ws = "907479"

# NAT gateway VPC. The NAT gateway is billed with the NAT-GATEWAY SKU; the public
# API cannot list it yet, so copy billing_catalog from an existing NAT gateway.
vpc = client.vpcs.create_vpc(
    workspace_id=ws, name="edge", site_id="site_blr_01", cidr="10.20.0.0/24", connectivity_type="nat_gateway",
    nat_billing_catalog=nat_catalog,  # omitted -> IbeeBillingWarning
)

# Subnets are checked against the VPC CIDR, existing subnets and the 10-subnet quota.
subnet = client.vpcs.create_vpc_subnet(vpc.vpc_id, workspace_id=ws, name="apps", cidr="10.20.0.128/25")

# Allocate a specific private IP (not the network, broadcast or gateway address).
client.vpcs.attach_vpc_node(vpc.vpc_id, workspace_id=ws, vm_id=vm_id, subnet_id=subnet.subnet_id,
                            requested_private_ip="10.20.0.140")

# Port forwarding: single ports 1-65535; duplicates and the target are checked first.
gw = client.vpcs.list_nat_gateways(vpc.vpc_id, workspace_id=ws)[0]
client.vpcs.create_nat_port_forwarding_rule(
    vpc.vpc_id, gw.nat_gateway_id, workspace_id=ws,
    name="ssh", external_port=2222, internal_ip="10.20.0.140", internal_port=22,
)

# MetalLB virtual IP announced by NAT-connected nodes, exposed through a Reserved IP.
vip = client.vpcs.create_vpc_virtual_ip(vpc.vpc_id, workspace_id=ws, subnet_id=subnet.subnet_id,
                                        private_ip="10.20.0.200", announcer_vm_ids=[vm_id])
client.reserved_ips.attach_reserved_ip_to_virtual_ip(reserved_ip_id, workspace_id=ws,
                                                     virtual_ip_id=vip.virtual_ip_id)

# Delete the NAT gateway (keep or release its address) and wait until it is gone.
client.vpcs.delete_nat_gateway(vpc.vpc_id, gw.nat_gateway_id, workspace_id=ws,
                               public_ip_action="release", wait=True)
# Or let delete_vpc remove the gateway first:
client.vpcs.delete_vpc(vpc.vpc_id, workspace_id=ws, delete_nat_gateway=True)

# Keep a VM's current public IPv4 as a Reserved IP (billing is checked first).
client.reserved_ips.convert_vm_public_ip_to_reserved_ip(workspace_id=ws, vm_id=vm_id, site_id="site_blr_01")

# Firewall rules: tcp/udp need a port; remote targets are IPv4 (default 0.0.0.0/0).
client.firewalls.create_firewall_rule(group_id, workspace_id=ws, protocol="tcp", port_start=443,
                                      remote_targets=["203.0.113.0/24"])

# Load balancers: HTTPS gets a managed certificate; policy and health checks are validated.
client.load_balancers.create_l7load_balancer(
    workspace_id=ws, name="web", protocol="https",
    backends=[{"type": "ip", "target": "10.20.0.140", "port": 8080}],
    policy={"timeout_ms": 30000, "retries": {"attempts": 3}},
    health_check={"active": {"type": "http", "path": "/health"}},
)
```

Not available in the public API yet: the portal's VM-side VPC attachment (NIC
hot-plug), listing NAT / Reserved IP prices and billing catalogs, attaching a
held Reserved IP to a VM without a VPC attachment (raises
`ReservedIpTargetUnsupportedError`), custom load-balancer certificates, and
reading back load-balancer routing, policy and health-check settings.

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

`is_payment_block_error(error)` tells whether an error is a payment or wallet
wall. It checks, in order: the billing error classes; a missing scope (never a
payment wall); HTTP 402; a structured code or billing reason
(`billing_denied`, `payment_required`, `insufficient_balance`,
`insufficient_funds` or a billing denial reason such as
`initial_topup_required`); and only when the error carries no code of its own,
whole phrases in the server message ("insufficient balance", "payment
required", "add a payment method", "top up").

### Error codes

Errors raised by the SDK itself extend `IbeeError` and carry a stable `code`.
The Python and TypeScript SDKs raise the same codes for the same conditions.
Unless the class column says otherwise the class is `IbeeValidationError`,
raised before the request is sent, with `field` naming the argument.

A code of the form `invalid_<field>` means the argument `<field>` (its
snake_case API name) is missing, malformed, out of range, or not allowed with
the other arguments, for example `invalid_workspace_id`, `invalid_limit`,
`invalid_cidr`, `invalid_prefix_length`, `invalid_ssh_key_mode`,
`invalid_target_mode`, `invalid_rules`. Other codes:

| Code | Class | Meaning |
| --- | --- | --- |
| `ibee_error` | `IbeeError` | Base code; not raised on its own |
| `operation_failed` | `OperationFailedError` | An awaited operation ended `failed`, `cancelled` or `timed_out` |
| `operation_wait_timeout` | `OperationTimeoutError` | A wait (operation, volume, CDN custom domain) ran out of time |
| `recovery_failed` | `RecoveryFailedError` | An awaited snapshot or backup run failed |
| `recovery_restore_failed` | `RecoveryRestoreFailedError` | An awaited snapshot or backup restore failed |
| `cdn_purge_failed` | `CdnPurgeFailedError` (TypeScript: `IbeeCdnPurgeError`) | The API accepted a CDN purge but reported it failed |
| `nat_gateway_deleting` | `IbeeError` | The NAT gateway delete was accepted but the gateway is still listed; retry the VPC delete shortly |
| `reserved_ip_target_unsupported` | `ReservedIpTargetUnsupportedError` | Reserved IP attach/move to a VM without a VPC attachment (404) |
| `no_changes` | | An update carries no field, or the requested value equals the current one |
| `confirmation_required` | | A confirmation flag is needed (`confirm_unmounted`/`force` on detach, `confirm_downgrade` on resize) |
| `request_body_too_large` | | The request body exceeds the API limit |
| `token_environment_mismatch` | | The token belongs to the other environment |
| `invalid_base_url`, `invalid_environment`, `invalid_token` | | Client configuration is invalid |
| `forbidden_field` | | A server-managed field was passed in a request object (TypeScript only) |
| `invalid_request` | | The request argument is not an object (TypeScript only) |
| `billing_catalog_required` | | A billing SKU object is required and cannot be resolved |
| `invalid_billing_term`, `unsupported_billing_term` | | The billing term is unknown, or the plan does not offer it |
| `windows_license_required`, `windows_license_not_allowed` | | Windows VMs need a licence SKU; other VMs must not send one |
| `plan_not_found`, `plan_not_selectable`, `invalid_plan` | | The plan is not offered in the site, not selectable or unpriced, or incomplete |
| `image_not_found`, `image_not_compatible` | | The image is not offered in the site, or not for this VM type |
| `shape_mismatch` | | An explicit cpu, ram_mb, os or GPU value differs from the plan or image |
| `duplicate_vm_names` | | VM names in one batch are not unique |
| `invalid_vm_state` | | The VM's status does not allow the action |
| `vm_not_linux` | | SSH key and password-login changes need a Linux VM |
| `ssh_key_required` | | Password login cannot be turned off without an SSH key |
| `console_not_supported` | | Console sessions are for cloud VMs only |
| `invalid_resize_target` | | Pass either `plan_id` or explicit cpu/ram_mb/disk_gb |
| `resize_not_in_place` | | The resize precheck did not return `in_place` |
| `root_disk_grow_only` | | A root disk can only grow |
| `vpc_required`, `subnet_required` | | The network choice needs a VPC or a subnet |
| `vpc_unavailable`, `vpc_site_mismatch`, `subnet_mismatch`, `vpc_connectivity_mismatch` | | The VPC is not available, is in another site, does not own the subnet, or has the wrong connectivity type |
| `reserved_ip_required` | | Public IP connectivity in a private VPC needs a Reserved IP |
| `reserved_ip_billing_catalog_required`, `vm_site_unavailable` | | Keeping a VM's public IP needs the RESERVED-IP SKU and a known VM site |
| `recovery_point_not_ready` | | The snapshot or backup has not succeeded, or the backup has no recovery point ID |
| `backups_disabled` | | Backups are not enabled for the VM |
| `backup_not_completed` | | Only a completed backup can be deleted |
| `snapshot_busy` | | The snapshot is being restored |
| `restore_disk_too_small` | | The restore target disk is smaller than the captured root disk |
| `invalid_restore_plan` | | The restore target plan is not eligible |
| `invalid_restore_request` | | A restore field is not used with the chosen `target_mode` |
| `volume_not_in_recovery_point` | | `selected_volume_id` is not part of the snapshot or backup |
| `volume_not_attached`, `volume_attached`, `volume_busy` | | The volume is not attached here, is already attached, or is busy |
| `volume_unreadable` | | The volume could not be read to take its billing SKU |
| `ambiguous_attachment`, `attachment_without_vm` | | The attachment to detach cannot be identified; pass `vm_id` or `node_name` |
| `vm_type_mismatch`, `site_mismatch` | | The volume belongs to another VM type or site |
| `resize_shrink_not_supported`, `resize_requires_offline` | | Volumes only grow; an attached volume needs a stopped VM or `allow_online` |
| `unknown_site_id`, `site_unavailable` | | The site is unknown or not available |
| `cidr_required` | | `auto_cidr=False` needs `cidr` |
| `subnet_outside_vpc`, `subnet_overlap`, `subnet_quota_exceeded` | | The subnet is outside the VPC CIDR, overlaps another subnet, or exceeds 10 per VPC |
| `address_outside_subnet`, `address_not_usable`, `address_is_gateway` | | The requested private IP is outside the subnet, a network/broadcast address, or the gateway |
| `vpc_has_nodes`, `vpc_has_nat_gateway`, `vpc_has_virtual_ips` | | The VPC still has attached nodes, a NAT gateway, or virtual IPs |
| `vpc_not_nat_gateway`, `nat_gateway_unavailable`, `nat_gateway_not_found` | | NAT needs a `nat_gateway` VPC with an available gateway; the gateway is not in the VPC |
| `duplicate_external_port` | | The protocol and external port are already forwarded |
| `virtual_ip_has_rules`, `virtual_ip_has_reserved_ip` | | Port-forwarding rules or a Reserved IP still use the virtual IP |
| `reserved_ip_attached`, `reserved_ip_attached_to_service`, `reserved_ip_not_attached`, `reserved_ip_same_target` | | The Reserved IP is attached (to a NAT gateway or virtual IP), is not attached, or is already on that target |
| `reserved_ip_not_movable`, `reserved_ip_converted_active`, `reserved_ip_not_user_reserved`, `reserved_ip_unavailable`, `reserved_ip_site_mismatch` | | The Reserved IP cannot be used this way |
| `duplicate_name` | | A firewall group with this name exists |
| `system_managed_rule` | | System-managed firewall rules cannot be changed |
| `firewall_attach_unsupported` | | The VM's network cannot take firewall groups |
| `bucket_not_empty`, `bucket_object_lock` | | Delete the objects first; Object Lock buckets cannot be deleted |
| `origin_not_public` | | Only public buckets can be CDN origins |
| `auth_method_mismatch`, `identity_disabled` | | Secret-ID rotation needs an enabled AppRole identity |
| `scope_already_exists`, `scope_permission_denied`, `store_not_active`, `store_not_found` | | The identity scope cannot be granted |
| `rollback_to_current`, `unknown_version`, `version_destroyed` | | The rollback target is not a restorable older version |

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

VM creates (cloud and GPU) are never retried automatically, even with an
idempotency key: a replayed create is rejected as a name conflict. Retry a
create yourself only after checking whether the first attempt created the VM.

Generated keys follow the portal's format (`cloud-vm-start-<vm id>-<hash>-<random>`).
The same key is reused on every automatic retry and is recorded on any raised
error as `error.idempotency_key`, so you can retry the logical call safely:

```python
from ibee import build_idempotency_key

key = build_idempotency_key("cloud-vm-reboot", "65f1c2a9e4b0a1b2c3d4e5f6")
client.cloud_vms.reboot_cloud_vm("65f1c2a9e4b0a1b2c3d4e5f6", workspace_id="907479", idempotency_key=key)
```

A caller-supplied key must be 1-128 printable ASCII characters without spaces.
Networking, snapshot, backup, object-storage and Secret Store writes do not
deduplicate keys yet, so the SDK never retries them. The Secret Store identity
access read (`get_secret_identity_access`) is not retried either, because every
call issues a new credential.

## Waiting for operations

VM creates, deletes, power actions, access updates, resizes and volume
attach/detach return an operation. Wait for it to finish:

```python
from ibee.errors import OperationFailedError, OperationTimeoutError

accepted = client.cloud_vms.start_cloud_vm("65f1c2a9e4b0a1b2c3d4e5f6", workspace_id="907479")
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

## Billing and lifecycle authority

All product mutations go to the upstream API for fresh Billing and lifecycle decisions.
The SDK does not query eligibility, estimate prices, or veto writes based on a diagnostic decision.
Catalog shape, selected term, tenant/workspace, scope, resource state, and destructive-action checks remain in place.
Upstream billing denial, restriction, suspension, and inactive-token errors propagate to callers.

`preflight_billing`, `billing_preflight`, `check_billing`, and `billing_check` are deprecated compatibility no-ops on product methods, for both true and false values.
They do not require `billing.read`. This applies to compute, recovery, networking, storage, CDN and secrets.

Use `client.billing.check_resource_eligibility(...)` for an explicit diagnostic query.
It returns `allowed: false` as data and supports `REVOKE_CREDENTIAL` and `SECURITY_RECOVERY`.
The explicitly invoked `require_resource_eligibility` convenience method retains its throwing contract for compatibility; product methods never call it.
An explicit query does not authorize or reserve funds for a later mutation.
Legacy estimate/minimum-top-up utilities are deprecated display/calculation helpers only; they are not authoritative prices or admission rules.

## Storage: Block Storage, Object Storage and CDN

The storage clients apply the portal's rules before sending anything and raise
`IbeeValidationError` when a value would be refused.

```python
from ibee import CdnPurgeFailedError, Ibee

client = Ibee(token="YOUR_TOKEN")
ws = "907479"

# Block Storage. Names: 3-255 lowercase letters, numbers and hyphens; size 10-10000 GB.
# Billing uses the site's Block Storage plan; site_name is filled from the compute sites.
created = client.block_storage.create_block_volume(
    workspace_id=ws, name="app-data", size_gb=100, site_id="site-1", vm_type="cloud"
)
volume_id = created["volume"]["id"]

# Attach to a VM like the portal: the volume is read, the VM must be in its site and of
# its vm_type, and its Block Storage SKU is sent. wait=True polls every 2 s for up to 2 min.
done = client.block_storage.attach_block_volume_to_vm(volume_id, "VM_ID", workspace_id=ws, wait=True)

# Detach: unmount inside the server first (the portal's mandatory confirmation).
client.block_storage.detach_block_volume_from_vm(volume_id, workspace_id=ws, confirm_unmounted=True, wait=True)

# Grow (never shrink); an attached volume needs vm_state="stopped" or allow_online=True.
client.block_storage.resize_block_volume(volume_id, workspace_id=ws, new_size_gb=200)
# Delete refuses an attached volume unless force=True (which detaches and erases it).
client.block_storage.delete_block_volume(volume_id, workspace_id=ws)
every_volume = client.block_storage.list_all_block_volumes(workspace_id=ws, vm_type="cloud")

# Object Storage. Bucket names: 3-63 lowercase letters, numbers and hyphens.
# region defaults to in-south-1 (api.ibee.ai) or in-south-2 (api.ibee.co.in).
client.object_storage.create_bucket(
    workspace_id=ws, name="audit-logs", default_retention={"mode": "COMPLIANCE", "days": 30}
)  # Object Lock is enabled automatically for retention
client.object_storage.delete_bucket("audit-logs", workspace_id=ws)  # empty, unlocked buckets only
key = client.object_storage.create_s3credential(workspace_id=ws)  # admin_rw "Default Key"
print(key.secret_access_key)  # shown once; the request is never retried
client.object_storage.delete_s3credential(key.access_key_id, workspace_id=ws)  # permanent

# CDN: only public buckets can be origins; cache_policy is static-assets, media, short or no-cache.
dist = client.cdn.create_cdn_distribution(workspace_id=ws, name="assets", origin_id="public-assets",
                                          check_origin_public=True)
domain = client.cdn.create_cdn_custom_domain(dist["id"], workspace_id=ws, domain="cdn.example.com")
client.cdn.wait_for_cdn_custom_domain(dist["id"], "cdn.example.com", workspace_id=ws)  # after adding the CNAME
try:
    client.cdn.purge_cdn_cache(dist["id"], workspace_id=ws, mode="prefix", prefixes=["/img/"])
except CdnPurgeFailedError as error:  # the CDN answered success: false
    print(error.mode, error.message)
```

Notes:

- Making a bucket private (`update_bucket(..., is_public=False)`) disables its
  public URL and deletes any CDN distribution that uses it as origin.
- `revoke_s3credential` and `delete_s3credential` permanently delete the key;
  the public API has no "revoked but kept" state.
- The node-level `attach_block_volume` / `detach_block_volume` only record a
  storage-node attachment; use the `*_to_vm` / `*_from_vm` methods for VMs.
- `cdn.list_cdn_cache_policies` and `cdn.get_cdn_distribution_metrics` are not
  yet part of the published API contract; behaviour may change.
- Not available through the public API yet: Block Storage plan and price
  discovery, bucket emptying, CORS/lifecycle/notification settings, object
  operations (use the S3 endpoint with S3 credentials), region discovery and CDN
  custom origins.

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
