# IBEE Solutions Python SDK

Official Python SDK for the IBEE Cloud API. Manage cloud VMs, GPU VMs, object storage, and secrets programmatically.

## Installation

```bash
pip install ibeesolutions
```

## Usage

```python
from ibeesolutions import IbeeSolutions

client = IbeeSolutions(token="ibee_live_xxxxxxxxxxxx")

# List cloud VMs
vms = client.cloud_vms.list(workspace_id="907479")

# Create a cloud VM
vm = client.cloud_vms.create(
    workspace_id="907479",
    name="web-server",
    os_distro="ubuntu",
    os_type="22.04",
    cpu=2,
    ram_mb=4096,
)

# List GPU VMs
gpu_vms = client.gpu_vms.list(workspace_id="907479")

# Manage secrets
stores = client.secret_store.list_secret_stores(workspace_id="907479")

# List object storage buckets
buckets = client.object_storage.list_buckets(workspace_id="907479")
```

## Async usage

```python
import asyncio
from ibeesolutions import AsyncIbeeSolutions

async def main():
    client = AsyncIbeeSolutions(token="ibee_live_xxxxxxxxxxxx")
    vms = await client.cloud_vms.list(workspace_id="907479")
    print(vms)

asyncio.run(main())
```

## Authentication

Generate a platform API token from the IBEE portal under Settings > Platform API Tokens. Use the token with the `token` parameter when creating the client.

## Documentation

Full API reference: [https://docs.ibee.co.in/docs/api-reference](https://docs.ibee.co.in/docs/api-reference)

## License

MIT
