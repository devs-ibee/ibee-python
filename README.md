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

client = Ibee(token="YOUR_TOKEN")

# Billable create methods automatically fail closed unless billing returns an
# affirmative decision. Product services repeat the check authoritatively
# immediately before provisioning. You can still call
# client.billing.check_resource_eligibility(...) for an earlier UI preflight.

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
bucket = client.object_storage.create_bucket(
    workspace_id="907479",
    name="production-assets",
    # region is optional when the environment has one configured region
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

## Environments

The client defaults to the production API (`https://api.ibee.ai/v1`).
`IbeeEnvironment.PRODUCTION` is an explicit alias for that default. Use
`IbeeEnvironment.DEVELOPMENT` for the development API (`https://api.ibee.co.in/v1`):

```python
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(token="IBEE_DEV_TOKEN", environment=IbeeEnvironment.DEVELOPMENT)
```

All ten billable creates perform automatic preflight: secret stores, secrets,
buckets, S3 credentials, NAT gateways, Reserved IPs, L4 and L7 load balancers,
Cloud VMs, and GPU VMs. Compute creates resolve the selected `plan_id` through
the compute catalog and submit its confirmed SKU and price. NAT gateways and
Reserved IPs currently use the platform's workspace billing-state decision
because those resources do not yet have dedicated catalog SKUs.

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
