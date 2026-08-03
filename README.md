# IBEE Solutions Python SDK

Official Python SDK for the IBEE Solutions API. Manage compute, object storage,
secrets, VPCs, reserved IPs, firewalls, and load balancers programmatically.

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
    plan_id="plan_standard_2c_4g",
    template_id="tmpl_ubuntu_2204",
    os_distro="ubuntu",
    os_type="linux",
    cpu=2,
    ram_mb=4096,
)

# List GPU VMs
gpu_vms = client.gpu_vms.list_gpu_vms(workspace_id="907479")

# Manage secrets
stores = client.secret_store.list_secret_stores(workspace_id="907479")

# List object storage buckets
buckets = client.object_storage.list_buckets(workspace_id="907479")

# Create a bucket in the workspace's default site and region
bucket = client.object_storage.create_bucket(
    workspace_id="907479",
    name="application-assets",
)

# Discover networking sites, then manage VPC resources
sites = client.vpcs.list_networking_sites(workspace_id="907479")
vpcs = client.vpcs.list_vpcs(workspace_id="907479")
reserved_ips = client.reserved_ips.list_reserved_ips(workspace_id="907479")
firewalls = client.firewalls.list_firewall_groups(workspace_id="907479")
load_balancers = client.load_balancers.list_load_balancers(workspace_id="907479")
```

Pass `region="in-south-1"` only when you need to override the workspace default.

To create a VM from portal-style choices, pass the selected IDs:

```python
vm = client.cloud_vms.create_cloud_vm(
    workspace_id="907479",
    idempotency_key="create-web-server-01",
    name="web-server-01",
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
VM placement is automatic when `site_id` is omitted; pass a site ID from
`client.compute_catalog.list_compute_sites(...)` only when you need a specific site.
In the current SDK, `cpu` and `ram_mb` are still required fallback fields even
when `plan_id` is provided.

## Environments

The client defaults to the production API (`https://api.ibee.ai/v1`). To use the development environment:

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
