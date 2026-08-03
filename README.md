# IBEE Solutions Python SDK

Official Python SDK for the IBEE Solutions API. Manage cloud VMs, GPU VMs,
VPC networking, Reserved IPs, firewalls, load balancers, object storage, and
secrets programmatically.

## Installation

```bash
pip install ibee
```

## Usage

```python
from ibee import Ibee

client = Ibee(token="ibee_prod_key_xxxxxxxxxxxx")

# List cloud VMs
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

## Secret Store lifecycle

Secret Store exposes 35 platform-token control-plane operations with matching
synchronous and asynchronous clients. Every request is scoped by
`workspace_id`; use the workspace that owns the store, secret, identity, or
scope ID. An ID from another workspace correctly returns `FORBIDDEN` and a
message such as "does not belong to workspace".

The complete method surface is:

- Stores (7): `list_secret_stores`, `create_secret_store`,
  `get_secret_store`, `update_secret_store`, `archive_secret_store`,
  `unarchive_secret_store`, and `permanently_delete_secret_store`.
- Secrets and versions (14): `list_secrets`, `create_secret`,
  `batch_create_secrets`, `get_secret`, `delete_secret`, `get_secret_value`,
  `update_secret_value`, `patch_secret_value`, `undelete_secret`,
  `destroy_secret_versions`, `permanently_delete_secret`,
  `list_secret_versions`, `get_secret_version`, and `rollback_secret`.
- Application identities and scopes (14): `list_secret_identities`,
  `create_secret_identity`, `get_secret_identity`, `update_secret_identity`,
  `disable_secret_identity`, `enable_secret_identity`,
  `get_secret_identity_access`, `rotate_secret_identity_secret_id`,
  `revoke_secret_identity_sessions`, `list_secret_identity_scopes`,
  `create_secret_identity_scope`, `update_secret_identity_scope`,
  `delete_secret_identity_scope`, and `delete_secret_identity`.

The following example creates a store and a versioned secret, reads its
metadata separately from its value, updates it, and inspects its versions:

```python
import os

from ibee import Ibee
from ibee.environment import IbeeEnvironment

workspace_id = os.environ["IBEE_WORKSPACE_ID"]
client = Ibee(
    token=os.environ["IBEE_TOKEN"],
    environment=IbeeEnvironment.DEVELOPMENT,
)

store = client.secret_store.create_secret_store(
    workspace_id=workspace_id,
    name="payments",
    description="Secrets used by the payments service",
)
secret = client.secret_store.create_secret(
    store.id,
    workspace_id=workspace_id,
    secret_name="database",
    value={"username": "payments", "password": os.environ["DATABASE_PASSWORD"]},
)

metadata = client.secret_store.get_secret(secret.id, workspace_id=workspace_id)
current_value = client.secret_store.get_secret_value(secret.id, workspace_id=workspace_id)

client.secret_store.patch_secret_value(
    secret.id,
    workspace_id=workspace_id,
    value={"username": "payments-v2"},
)
versions = client.secret_store.list_secret_versions(secret.id, workspace_id=workspace_id)
first_version = client.secret_store.get_secret_version(
    secret.id,
    1,
    workspace_id=workspace_id,
)
client.secret_store.rollback_secret(secret.id, workspace_id=workspace_id, version=1)
```

`get_secret` returns metadata only; `get_secret_value` and
`get_secret_version` return secret material. Do not log those responses.
Use `update_secret_value(..., cas=<current version>)` to replace the complete
value with a compare-and-set guard, or `patch_secret_value` to merge selected
keys. Batch import is available through `batch_create_secrets`.

Application identities allow a workload to access Secret Store without using
your platform API token. Creating an identity grants its initial store scope;
additional store scopes can be added explicitly:

```python
identity = client.secret_store.create_secret_identity(
    store.id,
    workspace_id=workspace_id,
    auth_method="approle",
    name="payments-api",
    token_policy_mode="read_write",
)

# This call returns a fresh AppRole secret_id. Capture it securely and do not log it.
access = client.secret_store.get_secret_identity_access(
    identity.id,
    workspace_id=workspace_id,
)

archive_store = client.secret_store.create_secret_store(
    workspace_id=workspace_id,
    name="payments-archive",
)
scope = client.secret_store.create_secret_identity_scope(
    identity.id,
    workspace_id=workspace_id,
    store_id=archive_store.id,
    access_mode="read_only",
    allow_version_read=True,
)
scopes = client.secret_store.list_secret_identity_scopes(
    identity.id,
    workspace_id=workspace_id,
)
```

For Kubernetes workloads, use `auth_method="kubernetes"` and provide both
`k8s_namespace` and `k8s_service_account`. AppRole `secret_id` values can be
rotated with `rotate_secret_identity_secret_id`; active sessions can be
revoked independently with `revoke_secret_identity_sessions`.

Cleanup is deliberately explicit. Permanent deletion cannot be undone:

```python
client.secret_store.delete_secret_identity_scope(scope.id, workspace_id=workspace_id)
client.secret_store.delete_secret_identity(identity.id, workspace_id=workspace_id)

client.secret_store.delete_secret(secret.id, workspace_id=workspace_id)
client.secret_store.permanently_delete_secret(secret.id, workspace_id=workspace_id)

client.secret_store.archive_secret_store(archive_store.id, workspace_id=workspace_id)
client.secret_store.permanently_delete_secret_store(
    archive_store.id,
    workspace_id=workspace_id,
)
client.secret_store.archive_secret_store(store.id, workspace_id=workspace_id)
client.secret_store.permanently_delete_secret_store(store.id, workspace_id=workspace_id)
```

Soft-deleted secret versions can be restored with `undelete_secret`; selected
historical versions can be irreversibly erased with
`destroy_secret_versions`. Stores can be restored before permanent deletion
with `unarchive_secret_store`.

To create a VM from portal-style choices, pass the selected IDs:

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

## Environments

The client defaults to the production API (`https://api.ibee.ai/v1`). Use it
with production tokens only. Development and testing use
`https://api.ibee.co.in/v1`:

```python
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(token="IBEE_DEV_TOKEN", environment=IbeeEnvironment.DEVELOPMENT)
```

Requires Python 3.10+.

## Async usage

```python
import asyncio
from ibee import AsyncIbee

async def main():
    client = AsyncIbee(token="ibee_prod_key_xxxxxxxxxxxx")
    vms = await client.cloud_vms.list_cloud_vms(workspace_id="907479")
    print(vms)

asyncio.run(main())
```

## Authentication

Generate a platform API token from the IBEE portal under Settings > Platform API Tokens. Use the token with the `token` parameter when creating the client.

## Documentation

Full API reference: [https://docs.ibee.co.in/docs/api-reference](https://docs.ibee.co.in/docs/api-reference)

## License

MIT
