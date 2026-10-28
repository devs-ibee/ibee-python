# IBEE Solutions Python SDK

Official Python SDK for the IBEE Solutions API: cloud and GPU VMs, VPC networking,
Reserved IPs, firewalls, load balancers, object storage, Block Storage, CDN,
Secret Store and Container Registry.

The SDK is the client generated from the public API contract
([reference](https://ibee.ai/docs/api-reference)): every operation is one method,
sync (`Ibee`) and async (`AsyncIbee`), and the request is sent as you pass it. The
only hand-written code is configuration from the environment, safe retries,
automatic idempotency keys and error fields that read the server's answer unchanged.
The server decides everything else (prices, eligibility, limits, states): the SDK
looks nothing up, fills in no defaults and validates no request.

## Install

```bash
pip install ibee
```

Python 3.10 or later.

## Authenticate

Create a platform API token in the portal under Settings > API Tokens.

```python
from ibee import Ibee

client = Ibee(token="ibee_prod_key_...", workspace_id="710995")
```

Or from the environment, first match wins:

| Setting | Argument | Environment |
| --- | --- | --- |
| Token | `token=` | `IBEE_API_TOKEN`, then `IBEE_TOKEN` |
| Workspace | `workspace_id=` (each call may pass its own) | `IBEE_WORKSPACE_ID` |
| Endpoint | `base_url=`, `environment=IbeeEnvironment.DEVELOPMENT` | `IBEE_BASE_URL`, `IBEE_ENDPOINT`, then `IBEE_ENV` (`dev` or `prod`) |

The default endpoint is production, `https://api.ibee.ai/v1`. A base URL must be
`https` (`http` only for localhost).

## Example: create a VM

VM create needs `billing_catalog`, the contract's `ComputeBillingSelection`: copy the
chosen plan's `billing_catalog` from `list_compute_plans` and merge in the whole
`billing_options` entry of the term you choose (`billing_interval`, `committed`,
`commitment_period`, `commitment_months`, `committed_hours`, `price_unit`,
`unit_price_minor`), keeping its `price_currency`. The SDK does not build it for you;
this is the recipe:

```python
from ibee import Ibee

client = Ibee()  # IBEE_API_TOKEN and IBEE_WORKSPACE_ID from the environment

site = client.compute_catalog.list_compute_sites().sites[0]
plan = client.compute_catalog.list_compute_plans(vm_type="cloud", site_id=site.site_id).plans[0]
image = client.compute_catalog.list_compute_images(vm_type="cloud", site_id=site.site_id).images[0]

# HOURLY (pay as you go), or MONTHLY: a one-month commitment, during which delete and
# resize answer 409 VM_COMMITTED.
option = next(o for o in plan.billing_catalog["billing_options"] if o["billing_interval"] == "HOURLY")
billing_catalog = {**plan.billing_catalog, **option}

operation = client.cloud_vms.create_cloud_vm(
    name="web-1",
    site_id=site.site_id,
    plan_id=plan.plan_id,
    template_id=image.template_id,
    os_type=image.os_type,
    os_distro=image.os_distro,
    cpu=plan.cpu,
    ram_mb=plan.ram_mb,
    disk_gb=plan.disk_gb,
    billing_catalog=billing_catalog,
    ssh_keys=["ssh-ed25519 AAAA... me"],
)
status = client.cloud_vms.get_compute_operation(operation.operation_id)
print(status.status)  # accepted, running, ..., succeeded, failed
```

Without a term the server answers 400 `compute_billing_term_required`; a partial or
changed entry gets 400 `invalid_compute_billing_selection`. GPU VMs work the same way
with `vm_type="gpu"`, `create_gpu_vm`, `gpu_count` and `gpu_model`.

A few calls to know:

- Resize is `resize_cloud_vm(vm_id, cpu=..., ram_mb=..., disk_gb=...)`
  (`precheck_cloud_vm_resize` first is optional).
- `disable_cloud_vm_backups(vm_id, request={})` / `disable_gpu_vm_backups`: the
  service needs the empty JSON body.
- Snapshot create and backup enable take a `billing_catalog` from
  `compute_catalog.list_snapshot_storage_plans()` / `list_backup_storage_plans()`.
- VM delete sends `public_ip_action` only when you pass it; for a VM with an
  automatically assigned public IP the server answers 400 until you pass `release` or
  `reserve`.
- Lists return the page the server sends (`limit`/`offset` where the contract has
  them).
- S3 keys: `revoke_s3credential` (`POST .../revoke`, the record stays) and
  `delete_s3credential` (`DELETE`, permanent).
- `get_bucket_cors` raises `ibee.core.parse_error.ParsingError` while the server
  returns S3-cased keys (`AllowedOrigins`, ...); the response is on the error's `body`.

### Container Registry

```python
registry = client.container_registry.create_container_registry(
    registry_name="acme-apps",
    confirm_registry_name="acme-apps",
    billing_catalog={"sku_code": "REGISTRY-STORAGE-250GB"},
)
# 202 while provisioning: poll get_container_registry until observed_state is ACTIVE.

token = client.container_registry.create_container_registry_access_token(
    registry.registry_id, token_name="ci-push", permission="PULL_PUSH", expires_in_days=30
)
# token.username and token.secret are returned once (docker login registry.ibee.ai).
```

The registry service asks Billing and answers; the SDK sends the request as given.
`upgrade_container_registry_package` gets a random `Idempotency-Key` when you pass no
`idempotency_key`, like the other keyed writes.

The full method list is in [`src/ibee/reference.md`](src/ibee/reference.md).

## Errors

Every HTTP error raises the status-named class from `ibee.errors` for the statuses
the contract declares (`BadRequestError`, `UnauthorizedError`, `PaymentRequiredError`,
`ForbiddenError`, `NotFoundError`, `ConflictError`, `UnprocessableEntityError`,
`LockedError`, `ServiceUnavailableError`), or `ApiError` for any other status
(429, 500, 502, 504, ...). All of them subclass
`ibee.core.api_error.ApiError` and carry the server's answer as received:

```python
from ibee.core.api_error import ApiError

try:
    client.cloud_vms.start_cloud_vm("vm-1")
except ApiError as error:
    print(error.status_code)           # 402
    print(error.code)                  # "billing_denied" (the gateway's error, or detail.code)
    print(error.billing_reason)        # "resource_limit_reached"
    print(error.message)               # the server's message, or None when it sent none
    print(error.admission_context_id)  # billing admission context, when present
    print(error.request_id)            # the x-request-id response header
    print(error.body)                  # the body exactly as received
    print(error.idempotency_key)       # the key sent, to retry the same write
```

The SDK adds no wording of its own. Bad configuration (a missing token, an unsafe base
URL, an unknown `IBEE_ENV`) raises `ibee.client.IbeeValidationError`, a `ValueError`,
before anything is sent; requests themselves are never validated by the SDK.

## Retries and idempotency

- Where the contract has the `X-Idempotency-Key` header (or `Idempotency-Key`, on
  Container Registry plan upgrade) and you pass no `idempotency_key`, the SDK sends a
  random one and reuses it on every retry.
- Reads (GET, HEAD, OPTIONS) are retried on 429, 502, 503 and 504.
- Writes are retried only when they carry an idempotency key, and only on 429 and
  503. VM creates (cloud and GPU) are never retried.
- A response with a billing or admission answer (`billing_reason`,
  `admission_context_id`, or a billing, admission, catalog or quote code) is never
  retried, and neither is any other status.
- A failed connection is retried; other network errors follow the rules above.
- At most `max_retries` retries (default 2; `Ibee(max_retries=0)` or
  `request_options={"max_retries": 0}` turns them off), with exponential backoff that
  honours `Retry-After`.

## Async

```python
import asyncio
from ibee import AsyncIbee

async def main() -> None:
    client = AsyncIbee()
    print(await client.cloud_vms.list_cloud_vms())

asyncio.run(main())
```

## Development

`src/ibee` is generated by Fern from `contract/ibee-cloud.yaml`, an exact copy of
`fern/openapi/ibee-cloud.yaml` in platform-docs, with the settings in `fern/`. The
hand-written files are listed in `src/ibee/.fernignore`; `fern/overrides.yml` makes
the workspace and idempotency headers optional (the SDK fills them) and declares the
body of backups disable, which contract 0.6.2 leaves out. Regenerate with
`scripts/regenerate.sh` (Fern CLI 5.45.3 and Docker). Run the tests with
`pip install -e . pytest && pytest -q`.

CI checks every pull request:

- `scripts/check_generated.sh`: regenerating from `contract/ibee-cloud.yaml` gives the
  committed `src/ibee` (the hand-written files aside).
- `scripts/check_contract_calls.py`: the hand-written files wrap no generated
  operation and name only paths of `contract/ibee-cloud.yaml`.

A pull request that changes `contract/**` gets the regenerated code pushed to its
branch (`.github/workflows/regenerate.yml`).

## License

MIT
