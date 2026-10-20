# IBEE Solutions Python SDK

Official Python SDK for the IBEE Solutions API: cloud and GPU VMs, VPC networking,
Reserved IPs, firewalls, load balancers, object storage, Block Storage, CDN,
Secret Store and Container Registry.

The SDK is generated from the public API contract
([reference](https://ibee.ai/docs/api-reference)); every operation is one method,
sync (`Ibee`) and async (`AsyncIbee`). A small hand-written layer adds configuration
from the environment, safe retries, automatic idempotency keys and errors that carry
the server's answer unchanged. The server decides everything else (prices,
eligibility, limits, states).

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
`https` (`http` only for localhost). A development token is not sent to production,
or a production token to development.

## Example

```python
from ibee import Ibee

client = Ibee()  # IBEE_API_TOKEN and IBEE_WORKSPACE_ID from the environment

sites = client.compute_catalog.list_compute_sites()
plans = client.compute_catalog.list_compute_plans(vm_type="cloud", site_id="site-1")

operation = client.cloud_vms.create_cloud_vm(
    name="web-1",
    site_id="site-1",
    plan_id=plans.plans[0].plan_id,
    template_id="ubuntu-24-04",
    billing_term="HOURLY",
    ssh_keys=["ssh-ed25519 AAAA... me"],
)
status = client.cloud_vms.get_compute_operation(operation.operation_id)
print(status.status)  # accepted, running, ..., succeeded, failed
```

Until the server resolves VM SKUs itself, `create_cloud_vm` and `create_gpu_vm` look
up the plan and image to fill `cpu`, `ram_mb`, `disk_gb`, `os_type`, `os_distro` and
the plan's `billing_catalog` for `billing_term`. The other temporary behaviours are
listed in [`src/ibee/held.py`](src/ibee/held.py) and the CHANGELOG.

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

Every HTTP error raises the status-named class from `ibee.errors`
(`BadRequestError`, `UnauthorizedError`, `PaymentRequiredError`, `ForbiddenError`,
`NotFoundError`, `ConflictError`, `UnprocessableEntityError`, `LockedError`,
`TooManyRequestsError`, `BadGatewayError`, `ServiceUnavailableError`,
`GatewayTimeoutError`), or `ApiError` for any other status. All of them subclass
`ibee.core.api_error.ApiError` and carry the server's answer as received:

```python
from ibee.core.api_error import ApiError

try:
    client.cloud_vms.create_cloud_vm(name="web-1", plan_id="p1", template_id="t1")
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
URL, a token for the other environment) raises `ibee.client.IbeeValidationError`, a
`ValueError`, before anything is sent.

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
hand-written files are listed in `src/ibee/.fernignore`. Regenerate with
`scripts/regenerate.sh` (Fern CLI 5.45.3 and Docker). Run the tests with
`pip install -e . pytest && pytest -q`.

CI checks every pull request:

- `scripts/check_generated.sh`: regenerating from `contract/ibee-cloud.yaml` gives the
  committed `src/ibee` (the hand-written files aside).
- `scripts/check_contract_calls.py`: the hand-written files call only operations and
  paths of `contract/ibee-cloud.yaml`.

A pull request that changes `contract/**` gets the regenerated code pushed to its
branch (`.github/workflows/regenerate.yml`).

## License

MIT
