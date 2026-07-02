# Reference
## Secret Store
<details><summary><code>client.secret_store.<a href="src/ibeesolutions/secret_store/client.py">list_secret_stores</a>(...) -> SecretStoreList</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Lists secret stores in a workspace. Requires scope: secret-store.read.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from ibeesolutions import IbeeSolutions
from ibeesolutions.environment import IbeeSolutionsEnvironment

client = IbeeSolutions(
    token="<token>",
    environment=IbeeSolutionsEnvironment.DEFAULT,
)

client.secret_store.list_secret_stores(
    workspace_id="workspace_id",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**workspace_id:** `str` — The workspace ID to scope this request to.
    
</dd>
</dl>

<dl>
<dd>

**page:** `typing.Optional[int]` — Page number.
    
</dd>
</dl>

<dl>
<dd>

**limit:** `typing.Optional[int]` — Maximum number of records to return.
    
</dd>
</dl>

<dl>
<dd>

**include_archived:** `typing.Optional[bool]` — Include archived stores in the result.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.secret_store.<a href="src/ibeesolutions/secret_store/client.py">create_secret_store</a>(...) -> SecretStore</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Creates a secret store in a workspace. Requires scope: secret-store.write.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from ibeesolutions import IbeeSolutions
from ibeesolutions.environment import IbeeSolutionsEnvironment

client = IbeeSolutions(
    token="<token>",
    environment=IbeeSolutionsEnvironment.DEFAULT,
)

client.secret_store.create_secret_store(
    workspace_id="workspace_id",
    name="production-secrets",
    description="Secrets for production workloads",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**workspace_id:** `str` — The workspace ID to scope this request to.
    
</dd>
</dl>

<dl>
<dd>

**name:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**description:** `typing.Optional[str]` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.secret_store.<a href="src/ibeesolutions/secret_store/client.py">get_secret_store</a>(...) -> SecretStore</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Gets one secret store. Requires scope: secret-store.read.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from ibeesolutions import IbeeSolutions
from ibeesolutions.environment import IbeeSolutionsEnvironment

client = IbeeSolutions(
    token="<token>",
    environment=IbeeSolutionsEnvironment.DEFAULT,
)

client.secret_store.get_secret_store(
    store_id="019f1e4b-3edd-72cf-b90e-26864ba2f283",
    workspace_id="workspace_id",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**store_id:** `str` — Secret store ID.
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `str` — The workspace ID to scope this request to.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.secret_store.<a href="src/ibeesolutions/secret_store/client.py">update_secret_store</a>(...) -> SecretStore</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Updates store name or description. Requires scope: secret-store.write.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from ibeesolutions import IbeeSolutions
from ibeesolutions.environment import IbeeSolutionsEnvironment

client = IbeeSolutions(
    token="<token>",
    environment=IbeeSolutionsEnvironment.DEFAULT,
)

client.secret_store.update_secret_store(
    store_id="019f1e4b-3edd-72cf-b90e-26864ba2f283",
    workspace_id="workspace_id",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**store_id:** `str` — Secret store ID.
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `str` — The workspace ID to scope this request to.
    
</dd>
</dl>

<dl>
<dd>

**name:** `typing.Optional[str]` 
    
</dd>
</dl>

<dl>
<dd>

**description:** `typing.Optional[str]` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.secret_store.<a href="src/ibeesolutions/secret_store/client.py">archive_secret_store</a>(...) -> SecretStore</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Archives a secret store. Requires scope: secret-store.write.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from ibeesolutions import IbeeSolutions
from ibeesolutions.environment import IbeeSolutionsEnvironment

client = IbeeSolutions(
    token="<token>",
    environment=IbeeSolutionsEnvironment.DEFAULT,
)

client.secret_store.archive_secret_store(
    store_id="019f1e4b-3edd-72cf-b90e-26864ba2f283",
    workspace_id="workspace_id",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**store_id:** `str` — Secret store ID.
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `str` — The workspace ID to scope this request to.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.secret_store.<a href="src/ibeesolutions/secret_store/client.py">list_secrets</a>(...) -> SecretList</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Lists secret metadata in a store. Secret values are not returned. Requires scope: secret-store.read.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from ibeesolutions import IbeeSolutions
from ibeesolutions.environment import IbeeSolutionsEnvironment

client = IbeeSolutions(
    token="<token>",
    environment=IbeeSolutionsEnvironment.DEFAULT,
)

client.secret_store.list_secrets(
    store_id="019f1e4b-3edd-72cf-b90e-26864ba2f283",
    workspace_id="workspace_id",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**store_id:** `str` — Secret store ID.
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `str` — The workspace ID to scope this request to.
    
</dd>
</dl>

<dl>
<dd>

**q:** `typing.Optional[str]` — Optional search query.
    
</dd>
</dl>

<dl>
<dd>

**page:** `typing.Optional[int]` — Page number.
    
</dd>
</dl>

<dl>
<dd>

**limit:** `typing.Optional[int]` — Maximum number of records to return.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.secret_store.<a href="src/ibeesolutions/secret_store/client.py">create_secret</a>(...) -> Secret</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Creates a secret in a store. Requires scope: secret-store.write.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from ibeesolutions import IbeeSolutions
from ibeesolutions.environment import IbeeSolutionsEnvironment

client = IbeeSolutions(
    token="<token>",
    environment=IbeeSolutionsEnvironment.DEFAULT,
)

client.secret_store.create_secret(
    store_id="019f1e4b-3edd-72cf-b90e-26864ba2f283",
    workspace_id="workspace_id",
    secret_name="database-url",
    value={
        "url": "postgres://user:pass@host:5432/mydb"
    },
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**store_id:** `str` — Secret store ID.
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `str` — The workspace ID to scope this request to.
    
</dd>
</dl>

<dl>
<dd>

**secret_name:** `str` — Unique name for the secret within the store. Lowercase alphanumeric and hyphens only.
    
</dd>
</dl>

<dl>
<dd>

**value:** `typing.Dict[str, typing.Any]` — Key-value pairs containing the secret data.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.secret_store.<a href="src/ibeesolutions/secret_store/client.py">get_secret</a>(...) -> Secret</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Gets one secret metadata record. Secret value is not returned. Requires scope: secret-store.read.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from ibeesolutions import IbeeSolutions
from ibeesolutions.environment import IbeeSolutionsEnvironment

client = IbeeSolutions(
    token="<token>",
    environment=IbeeSolutionsEnvironment.DEFAULT,
)

client.secret_store.get_secret(
    secret_id="019f1e4b-4a2c-71d0-a8b3-c5f92e7d1a4b",
    workspace_id="workspace_id",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**secret_id:** `str` — Secret ID.
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `str` — The workspace ID to scope this request to.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.secret_store.<a href="src/ibeesolutions/secret_store/client.py">delete_secret</a>(...) -> Secret</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Soft-deletes a secret. Requires scope: secret-store.write.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from ibeesolutions import IbeeSolutions
from ibeesolutions.environment import IbeeSolutionsEnvironment

client = IbeeSolutions(
    token="<token>",
    environment=IbeeSolutionsEnvironment.DEFAULT,
)

client.secret_store.delete_secret(
    secret_id="019f1e4b-4a2c-71d0-a8b3-c5f92e7d1a4b",
    workspace_id="workspace_id",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**secret_id:** `str` — Secret ID.
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `str` — The workspace ID to scope this request to.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.secret_store.<a href="src/ibeesolutions/secret_store/client.py">get_secret_value</a>(...) -> SecretValue</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Gets the latest value for a secret. Requires scope: secret-store.read.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from ibeesolutions import IbeeSolutions
from ibeesolutions.environment import IbeeSolutionsEnvironment

client = IbeeSolutions(
    token="<token>",
    environment=IbeeSolutionsEnvironment.DEFAULT,
)

client.secret_store.get_secret_value(
    secret_id="019f1e4b-4a2c-71d0-a8b3-c5f92e7d1a4b",
    workspace_id="workspace_id",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**secret_id:** `str` — Secret ID.
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `str` — The workspace ID to scope this request to.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.secret_store.<a href="src/ibeesolutions/secret_store/client.py">update_secret_value</a>(...) -> SecretValue</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Creates a new version of the secret value. Requires scope: secret-store.write.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from ibeesolutions import IbeeSolutions
from ibeesolutions.environment import IbeeSolutionsEnvironment

client = IbeeSolutions(
    token="<token>",
    environment=IbeeSolutionsEnvironment.DEFAULT,
)

client.secret_store.update_secret_value(
    secret_id="019f1e4b-4a2c-71d0-a8b3-c5f92e7d1a4b",
    workspace_id="workspace_id",
    value={
        "url": "postgres://user:updated@host:5432/mydb"
    },
    cas=1,
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**secret_id:** `str` — Secret ID.
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `str` — The workspace ID to scope this request to.
    
</dd>
</dl>

<dl>
<dd>

**value:** `typing.Dict[str, typing.Any]` — Key-value pairs containing the new secret data. Creates a new version.
    
</dd>
</dl>

<dl>
<dd>

**cas:** `typing.Optional[int]` — Check-and-set: only update if the current version matches this number. Prevents overwriting concurrent changes.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

## Object Storage
<details><summary><code>client.object_storage.<a href="src/ibeesolutions/object_storage/client.py">list_buckets</a>(...) -> BucketList</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Lists object storage buckets in a workspace. Requires scope: object-storage.read.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from ibeesolutions import IbeeSolutions
from ibeesolutions.environment import IbeeSolutionsEnvironment

client = IbeeSolutions(
    token="<token>",
    environment=IbeeSolutionsEnvironment.DEFAULT,
)

client.object_storage.list_buckets(
    workspace_id="workspace_id",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**workspace_id:** `str` — The workspace ID to scope this request to.
    
</dd>
</dl>

<dl>
<dd>

**limit:** `typing.Optional[int]` — Maximum number of buckets to return.
    
</dd>
</dl>

<dl>
<dd>

**continuation_token:** `typing.Optional[str]` — Pagination token from the previous response.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.object_storage.<a href="src/ibeesolutions/object_storage/client.py">create_bucket</a>(...) -> Bucket</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Creates an object storage bucket. Requires scope: object-storage.write.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from ibeesolutions import IbeeSolutions
from ibeesolutions.environment import IbeeSolutionsEnvironment

client = IbeeSolutions(
    token="<token>",
    environment=IbeeSolutionsEnvironment.DEFAULT,
)

client.object_storage.create_bucket(
    workspace_id="workspace_id",
    name="production-assets",
    is_public=False,
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**workspace_id:** `str` — The workspace ID to scope this request to.
    
</dd>
</dl>

<dl>
<dd>

**name:** `str` — Unique bucket name within the workspace.
    
</dd>
</dl>

<dl>
<dd>

**is_public:** `typing.Optional[bool]` — Whether the bucket allows unauthenticated read access.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.object_storage.<a href="src/ibeesolutions/object_storage/client.py">delete_bucket</a>(...) -> DeleteResponse</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Deletes a bucket and all of its contents. Requires scope: object-storage.delete.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from ibeesolutions import IbeeSolutions
from ibeesolutions.environment import IbeeSolutionsEnvironment

client = IbeeSolutions(
    token="<token>",
    environment=IbeeSolutionsEnvironment.DEFAULT,
)

client.object_storage.delete_bucket(
    bucket_name="bucket_name",
    workspace_id="workspace_id",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**bucket_name:** `str` — Logical bucket name.
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `str` — The workspace ID to scope this request to.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

## CloudVms
<details><summary><code>client.cloud_vms.<a href="src/ibeesolutions/cloud_vms/client.py">list_cloud_vms</a>(...) -> typing.List[CloudVm]</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Returns all cloud VMs in the workspace. Requires scope: vm.read.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from ibeesolutions import IbeeSolutions
from ibeesolutions.environment import IbeeSolutionsEnvironment

client = IbeeSolutions(
    token="<token>",
    environment=IbeeSolutionsEnvironment.DEFAULT,
)

client.cloud_vms.list_cloud_vms(
    workspace_id="workspace_id",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**workspace_id:** `str` — The workspace ID to scope this request to.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.cloud_vms.<a href="src/ibeesolutions/cloud_vms/client.py">create_cloud_vm</a>(...) -> OperationAccepted</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Creates a cloud VM. Returns an operation you can poll for status. Requires scope: vm.write.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from ibeesolutions import IbeeSolutions
from ibeesolutions.environment import IbeeSolutionsEnvironment

client = IbeeSolutions(
    token="<token>",
    environment=IbeeSolutionsEnvironment.DEFAULT,
)

client.cloud_vms.create_cloud_vm(
    workspace_id="workspace_id",
    idempotency_key="X-Idempotency-Key",
    name="web-server-01",
    os_distro="ubuntu",
    os_type="linux",
    cpu=2,
    ram_mb=4096,
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**workspace_id:** `str` — The workspace ID to scope this request to.
    
</dd>
</dl>

<dl>
<dd>

**idempotency_key:** `str` — Unique key used to safely retry write operations.
    
</dd>
</dl>

<dl>
<dd>

**name:** `str` — Display name for the virtual machine.
    
</dd>
</dl>

<dl>
<dd>

**os_distro:** `str` — Operating system distribution (e.g. ubuntu, centos, debian, rocky, windows).
    
</dd>
</dl>

<dl>
<dd>

**os_type:** `CreateCloudVmRequestOsType` — Operating system family.
    
</dd>
</dl>

<dl>
<dd>

**cpu:** `int` — Number of vCPUs.
    
</dd>
</dl>

<dl>
<dd>

**ram_mb:** `int` — RAM in megabytes.
    
</dd>
</dl>

<dl>
<dd>

**template_id:** `typing.Optional[str]` — OS template or image ID.
    
</dd>
</dl>

<dl>
<dd>

**disk_gb:** `typing.Optional[int]` — Root disk size in gigabytes.
    
</dd>
</dl>

<dl>
<dd>

**plan_id:** `typing.Optional[str]` — Pre-configured plan ID. Overrides cpu, ram_mb, and disk_gb when set.
    
</dd>
</dl>

<dl>
<dd>

**ssh_key_ids:** `typing.Optional[typing.List[str]]` — SSH key IDs to inject into the VM.
    
</dd>
</dl>

<dl>
<dd>

**tags:** `typing.Optional[typing.List[str]]` — Arbitrary tags for filtering and organization.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.cloud_vms.<a href="src/ibeesolutions/cloud_vms/client.py">get_cloud_vm</a>(...) -> CloudVm</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Returns a single cloud VM. Requires scope: vm.read.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from ibeesolutions import IbeeSolutions
from ibeesolutions.environment import IbeeSolutionsEnvironment

client = IbeeSolutions(
    token="<token>",
    environment=IbeeSolutionsEnvironment.DEFAULT,
)

client.cloud_vms.get_cloud_vm(
    vm_id="vm_id",
    workspace_id="workspace_id",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**vm_id:** `str` — Virtual machine ID.
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `str` — The workspace ID to scope this request to.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.cloud_vms.<a href="src/ibeesolutions/cloud_vms/client.py">delete_cloud_vm</a>(...) -> OperationAccepted</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Deletes a cloud VM. Returns an operation you can poll for status. Requires scope: vm.write.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from ibeesolutions import IbeeSolutions
from ibeesolutions.environment import IbeeSolutionsEnvironment

client = IbeeSolutions(
    token="<token>",
    environment=IbeeSolutionsEnvironment.DEFAULT,
)

client.cloud_vms.delete_cloud_vm(
    vm_id="vm_id",
    workspace_id="workspace_id",
    idempotency_key="X-Idempotency-Key",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**vm_id:** `str` — Virtual machine ID.
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `str` — The workspace ID to scope this request to.
    
</dd>
</dl>

<dl>
<dd>

**idempotency_key:** `str` — Unique key used to safely retry write operations.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.cloud_vms.<a href="src/ibeesolutions/cloud_vms/client.py">update_cloud_vm</a>(...) -> CloudVm</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Updates mutable properties of a cloud VM. Requires scope: vm.write.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from ibeesolutions import IbeeSolutions
from ibeesolutions.environment import IbeeSolutionsEnvironment

client = IbeeSolutions(
    token="<token>",
    environment=IbeeSolutionsEnvironment.DEFAULT,
)

client.cloud_vms.update_cloud_vm(
    vm_id="vm_id",
    workspace_id="workspace_id",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**vm_id:** `str` — Virtual machine ID.
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `str` — The workspace ID to scope this request to.
    
</dd>
</dl>

<dl>
<dd>

**request:** `UpdateVmRequest` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.cloud_vms.<a href="src/ibeesolutions/cloud_vms/client.py">start_cloud_vm</a>(...) -> OperationAccepted</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Starts a stopped cloud VM. Requires scope: vm.write.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from ibeesolutions import IbeeSolutions
from ibeesolutions.environment import IbeeSolutionsEnvironment

client = IbeeSolutions(
    token="<token>",
    environment=IbeeSolutionsEnvironment.DEFAULT,
)

client.cloud_vms.start_cloud_vm(
    vm_id="vm_id",
    workspace_id="workspace_id",
    idempotency_key="X-Idempotency-Key",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**vm_id:** `str` — Virtual machine ID.
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `str` — The workspace ID to scope this request to.
    
</dd>
</dl>

<dl>
<dd>

**idempotency_key:** `str` — Unique key used to safely retry write operations.
    
</dd>
</dl>

<dl>
<dd>

**request:** `PowerActionRequest` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.cloud_vms.<a href="src/ibeesolutions/cloud_vms/client.py">stop_cloud_vm</a>(...) -> OperationAccepted</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Stops a running cloud VM. Requires scope: vm.write.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from ibeesolutions import IbeeSolutions
from ibeesolutions.environment import IbeeSolutionsEnvironment

client = IbeeSolutions(
    token="<token>",
    environment=IbeeSolutionsEnvironment.DEFAULT,
)

client.cloud_vms.stop_cloud_vm(
    vm_id="vm_id",
    workspace_id="workspace_id",
    idempotency_key="X-Idempotency-Key",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**vm_id:** `str` — Virtual machine ID.
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `str` — The workspace ID to scope this request to.
    
</dd>
</dl>

<dl>
<dd>

**idempotency_key:** `str` — Unique key used to safely retry write operations.
    
</dd>
</dl>

<dl>
<dd>

**request:** `PowerActionRequest` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.cloud_vms.<a href="src/ibeesolutions/cloud_vms/client.py">reboot_cloud_vm</a>(...) -> OperationAccepted</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Reboots a cloud VM. Requires scope: vm.write.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from ibeesolutions import IbeeSolutions
from ibeesolutions.environment import IbeeSolutionsEnvironment

client = IbeeSolutions(
    token="<token>",
    environment=IbeeSolutionsEnvironment.DEFAULT,
)

client.cloud_vms.reboot_cloud_vm(
    vm_id="vm_id",
    workspace_id="workspace_id",
    idempotency_key="X-Idempotency-Key",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**vm_id:** `str` — Virtual machine ID.
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `str` — The workspace ID to scope this request to.
    
</dd>
</dl>

<dl>
<dd>

**idempotency_key:** `str` — Unique key used to safely retry write operations.
    
</dd>
</dl>

<dl>
<dd>

**request:** `PowerActionRequest` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.cloud_vms.<a href="src/ibeesolutions/cloud_vms/client.py">get_cloud_vm_metrics</a>(...) -> VmMetrics</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Returns current resource-usage metrics for a cloud VM. Requires scope: vm.read.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from ibeesolutions import IbeeSolutions
from ibeesolutions.environment import IbeeSolutionsEnvironment

client = IbeeSolutions(
    token="<token>",
    environment=IbeeSolutionsEnvironment.DEFAULT,
)

client.cloud_vms.get_cloud_vm_metrics(
    vm_id="vm_id",
    workspace_id="workspace_id",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**vm_id:** `str` — Virtual machine ID.
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `str` — The workspace ID to scope this request to.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.cloud_vms.<a href="src/ibeesolutions/cloud_vms/client.py">list_cloud_vm_network_interfaces</a>(...) -> typing.List[NetworkInterface]</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Returns network interfaces attached to a cloud VM. Requires scope: vm.read.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from ibeesolutions import IbeeSolutions
from ibeesolutions.environment import IbeeSolutionsEnvironment

client = IbeeSolutions(
    token="<token>",
    environment=IbeeSolutionsEnvironment.DEFAULT,
)

client.cloud_vms.list_cloud_vm_network_interfaces(
    vm_id="vm_id",
    workspace_id="workspace_id",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**vm_id:** `str` — Virtual machine ID.
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `str` — The workspace ID to scope this request to.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.cloud_vms.<a href="src/ibeesolutions/cloud_vms/client.py">attach_cloud_vm_network</a>(...) -> NetworkInterface</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Attaches a network to a cloud VM. Requires scope: vm.write.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from ibeesolutions import IbeeSolutions
from ibeesolutions.environment import IbeeSolutionsEnvironment

client = IbeeSolutions(
    token="<token>",
    environment=IbeeSolutionsEnvironment.DEFAULT,
)

client.cloud_vms.attach_cloud_vm_network(
    vm_id="vm_id",
    workspace_id="workspace_id",
    idempotency_key="X-Idempotency-Key",
    network_id="net_456",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**vm_id:** `str` — Virtual machine ID.
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `str` — The workspace ID to scope this request to.
    
</dd>
</dl>

<dl>
<dd>

**idempotency_key:** `str` — Unique key used to safely retry write operations.
    
</dd>
</dl>

<dl>
<dd>

**request:** `AttachNetworkRequest` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.cloud_vms.<a href="src/ibeesolutions/cloud_vms/client.py">detach_cloud_vm_network</a>(...) -> DeleteResponse</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Detaches a network interface from a cloud VM. Requires scope: vm.write.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from ibeesolutions import IbeeSolutions
from ibeesolutions.environment import IbeeSolutionsEnvironment

client = IbeeSolutions(
    token="<token>",
    environment=IbeeSolutionsEnvironment.DEFAULT,
)

client.cloud_vms.detach_cloud_vm_network(
    vm_id="vm_id",
    interface_id="interface_id",
    workspace_id="workspace_id",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**vm_id:** `str` — Virtual machine ID.
    
</dd>
</dl>

<dl>
<dd>

**interface_id:** `str` — Network interface ID.
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `str` — The workspace ID to scope this request to.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.cloud_vms.<a href="src/ibeesolutions/cloud_vms/client.py">get_compute_operation</a>(...) -> OperationStatus</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Returns the status of an async compute operation (create, delete, start, stop, reboot). Works for both cloud VM and GPU VM operations. Requires scope: vm.read.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from ibeesolutions import IbeeSolutions
from ibeesolutions.environment import IbeeSolutionsEnvironment

client = IbeeSolutions(
    token="<token>",
    environment=IbeeSolutionsEnvironment.DEFAULT,
)

client.cloud_vms.get_compute_operation(
    operation_id="operation_id",
    workspace_id="workspace_id",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**operation_id:** `str` — Operation ID returned by a create, delete, or power-action request.
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `str` — The workspace ID to scope this request to.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

## GpuVms
<details><summary><code>client.gpu_vms.<a href="src/ibeesolutions/gpu_vms/client.py">list_gpu_vms</a>(...) -> typing.List[GpuVm]</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Returns all GPU VMs in the workspace. Requires scope: vm.read.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from ibeesolutions import IbeeSolutions
from ibeesolutions.environment import IbeeSolutionsEnvironment

client = IbeeSolutions(
    token="<token>",
    environment=IbeeSolutionsEnvironment.DEFAULT,
)

client.gpu_vms.list_gpu_vms(
    workspace_id="workspace_id",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**workspace_id:** `str` — The workspace ID to scope this request to.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.gpu_vms.<a href="src/ibeesolutions/gpu_vms/client.py">create_gpu_vm</a>(...) -> OperationAccepted</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Creates a GPU VM. Returns an operation you can poll for status. Requires scope: vm.write.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from ibeesolutions import IbeeSolutions
from ibeesolutions.environment import IbeeSolutionsEnvironment

client = IbeeSolutions(
    token="<token>",
    environment=IbeeSolutionsEnvironment.DEFAULT,
)

client.gpu_vms.create_gpu_vm(
    workspace_id="workspace_id",
    idempotency_key="X-Idempotency-Key",
    name="ml-training-01",
    os_distro="ubuntu",
    os_type="linux",
    cpu=8,
    ram_mb=32768,
    gpu_count=1,
    gpu_model="A100",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**workspace_id:** `str` — The workspace ID to scope this request to.
    
</dd>
</dl>

<dl>
<dd>

**idempotency_key:** `str` — Unique key used to safely retry write operations.
    
</dd>
</dl>

<dl>
<dd>

**name:** `str` — Display name for the virtual machine.
    
</dd>
</dl>

<dl>
<dd>

**os_distro:** `str` — Operating system distribution (e.g. ubuntu, centos, debian, rocky).
    
</dd>
</dl>

<dl>
<dd>

**os_type:** `CreateGpuVmRequestOsType` — Operating system family.
    
</dd>
</dl>

<dl>
<dd>

**cpu:** `int` — Number of vCPUs.
    
</dd>
</dl>

<dl>
<dd>

**ram_mb:** `int` — RAM in megabytes.
    
</dd>
</dl>

<dl>
<dd>

**gpu_count:** `int` — Number of GPUs to attach.
    
</dd>
</dl>

<dl>
<dd>

**gpu_model:** `str` — GPU model (e.g. A100, H100, L40S, RTX4090).
    
</dd>
</dl>

<dl>
<dd>

**template_id:** `typing.Optional[str]` — OS template or image ID with GPU drivers pre-installed.
    
</dd>
</dl>

<dl>
<dd>

**disk_gb:** `typing.Optional[int]` — Root disk size in gigabytes.
    
</dd>
</dl>

<dl>
<dd>

**plan_id:** `typing.Optional[str]` — Pre-configured GPU plan ID.
    
</dd>
</dl>

<dl>
<dd>

**ssh_key_ids:** `typing.Optional[typing.List[str]]` — SSH key IDs to inject into the VM.
    
</dd>
</dl>

<dl>
<dd>

**tags:** `typing.Optional[typing.List[str]]` — Arbitrary tags for filtering and organization.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.gpu_vms.<a href="src/ibeesolutions/gpu_vms/client.py">get_gpu_vm</a>(...) -> GpuVm</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Returns a single GPU VM. Requires scope: vm.read.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from ibeesolutions import IbeeSolutions
from ibeesolutions.environment import IbeeSolutionsEnvironment

client = IbeeSolutions(
    token="<token>",
    environment=IbeeSolutionsEnvironment.DEFAULT,
)

client.gpu_vms.get_gpu_vm(
    vm_id="vm_id",
    workspace_id="workspace_id",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**vm_id:** `str` — Virtual machine ID.
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `str` — The workspace ID to scope this request to.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.gpu_vms.<a href="src/ibeesolutions/gpu_vms/client.py">delete_gpu_vm</a>(...) -> OperationAccepted</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Deletes a GPU VM. Returns an operation you can poll for status. Requires scope: vm.write.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from ibeesolutions import IbeeSolutions
from ibeesolutions.environment import IbeeSolutionsEnvironment

client = IbeeSolutions(
    token="<token>",
    environment=IbeeSolutionsEnvironment.DEFAULT,
)

client.gpu_vms.delete_gpu_vm(
    vm_id="vm_id",
    workspace_id="workspace_id",
    idempotency_key="X-Idempotency-Key",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**vm_id:** `str` — Virtual machine ID.
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `str` — The workspace ID to scope this request to.
    
</dd>
</dl>

<dl>
<dd>

**idempotency_key:** `str` — Unique key used to safely retry write operations.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.gpu_vms.<a href="src/ibeesolutions/gpu_vms/client.py">update_gpu_vm</a>(...) -> GpuVm</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Updates mutable properties of a GPU VM. Requires scope: vm.write.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from ibeesolutions import IbeeSolutions
from ibeesolutions.environment import IbeeSolutionsEnvironment

client = IbeeSolutions(
    token="<token>",
    environment=IbeeSolutionsEnvironment.DEFAULT,
)

client.gpu_vms.update_gpu_vm(
    vm_id="vm_id",
    workspace_id="workspace_id",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**vm_id:** `str` — Virtual machine ID.
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `str` — The workspace ID to scope this request to.
    
</dd>
</dl>

<dl>
<dd>

**request:** `UpdateVmRequest` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.gpu_vms.<a href="src/ibeesolutions/gpu_vms/client.py">start_gpu_vm</a>(...) -> OperationAccepted</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Starts a stopped GPU VM. Requires scope: vm.write.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from ibeesolutions import IbeeSolutions
from ibeesolutions.environment import IbeeSolutionsEnvironment

client = IbeeSolutions(
    token="<token>",
    environment=IbeeSolutionsEnvironment.DEFAULT,
)

client.gpu_vms.start_gpu_vm(
    vm_id="vm_id",
    workspace_id="workspace_id",
    idempotency_key="X-Idempotency-Key",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**vm_id:** `str` — Virtual machine ID.
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `str` — The workspace ID to scope this request to.
    
</dd>
</dl>

<dl>
<dd>

**idempotency_key:** `str` — Unique key used to safely retry write operations.
    
</dd>
</dl>

<dl>
<dd>

**request:** `PowerActionRequest` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.gpu_vms.<a href="src/ibeesolutions/gpu_vms/client.py">stop_gpu_vm</a>(...) -> OperationAccepted</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Stops a running GPU VM. Requires scope: vm.write.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from ibeesolutions import IbeeSolutions
from ibeesolutions.environment import IbeeSolutionsEnvironment

client = IbeeSolutions(
    token="<token>",
    environment=IbeeSolutionsEnvironment.DEFAULT,
)

client.gpu_vms.stop_gpu_vm(
    vm_id="vm_id",
    workspace_id="workspace_id",
    idempotency_key="X-Idempotency-Key",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**vm_id:** `str` — Virtual machine ID.
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `str` — The workspace ID to scope this request to.
    
</dd>
</dl>

<dl>
<dd>

**idempotency_key:** `str` — Unique key used to safely retry write operations.
    
</dd>
</dl>

<dl>
<dd>

**request:** `PowerActionRequest` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.gpu_vms.<a href="src/ibeesolutions/gpu_vms/client.py">reboot_gpu_vm</a>(...) -> OperationAccepted</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Reboots a GPU VM. Requires scope: vm.write.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from ibeesolutions import IbeeSolutions
from ibeesolutions.environment import IbeeSolutionsEnvironment

client = IbeeSolutions(
    token="<token>",
    environment=IbeeSolutionsEnvironment.DEFAULT,
)

client.gpu_vms.reboot_gpu_vm(
    vm_id="vm_id",
    workspace_id="workspace_id",
    idempotency_key="X-Idempotency-Key",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**vm_id:** `str` — Virtual machine ID.
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `str` — The workspace ID to scope this request to.
    
</dd>
</dl>

<dl>
<dd>

**idempotency_key:** `str` — Unique key used to safely retry write operations.
    
</dd>
</dl>

<dl>
<dd>

**request:** `PowerActionRequest` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.gpu_vms.<a href="src/ibeesolutions/gpu_vms/client.py">get_gpu_vm_metrics</a>(...) -> VmMetrics</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Returns current resource-usage metrics for a GPU VM. Requires scope: vm.read.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from ibeesolutions import IbeeSolutions
from ibeesolutions.environment import IbeeSolutionsEnvironment

client = IbeeSolutions(
    token="<token>",
    environment=IbeeSolutionsEnvironment.DEFAULT,
)

client.gpu_vms.get_gpu_vm_metrics(
    vm_id="vm_id",
    workspace_id="workspace_id",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**vm_id:** `str` — Virtual machine ID.
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `str` — The workspace ID to scope this request to.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.gpu_vms.<a href="src/ibeesolutions/gpu_vms/client.py">list_gpu_vm_network_interfaces</a>(...) -> typing.List[NetworkInterface]</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Returns network interfaces attached to a GPU VM. Requires scope: vm.read.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from ibeesolutions import IbeeSolutions
from ibeesolutions.environment import IbeeSolutionsEnvironment

client = IbeeSolutions(
    token="<token>",
    environment=IbeeSolutionsEnvironment.DEFAULT,
)

client.gpu_vms.list_gpu_vm_network_interfaces(
    vm_id="vm_id",
    workspace_id="workspace_id",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**vm_id:** `str` — Virtual machine ID.
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `str` — The workspace ID to scope this request to.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.gpu_vms.<a href="src/ibeesolutions/gpu_vms/client.py">attach_gpu_vm_network</a>(...) -> NetworkInterface</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Attaches a network to a GPU VM. Requires scope: vm.write.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from ibeesolutions import IbeeSolutions
from ibeesolutions.environment import IbeeSolutionsEnvironment

client = IbeeSolutions(
    token="<token>",
    environment=IbeeSolutionsEnvironment.DEFAULT,
)

client.gpu_vms.attach_gpu_vm_network(
    vm_id="vm_id",
    workspace_id="workspace_id",
    idempotency_key="X-Idempotency-Key",
    network_id="net_456",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**vm_id:** `str` — Virtual machine ID.
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `str` — The workspace ID to scope this request to.
    
</dd>
</dl>

<dl>
<dd>

**idempotency_key:** `str` — Unique key used to safely retry write operations.
    
</dd>
</dl>

<dl>
<dd>

**request:** `AttachNetworkRequest` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.gpu_vms.<a href="src/ibeesolutions/gpu_vms/client.py">detach_gpu_vm_network</a>(...) -> DeleteResponse</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Detaches a network interface from a GPU VM. Requires scope: vm.write.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from ibeesolutions import IbeeSolutions
from ibeesolutions.environment import IbeeSolutionsEnvironment

client = IbeeSolutions(
    token="<token>",
    environment=IbeeSolutionsEnvironment.DEFAULT,
)

client.gpu_vms.detach_gpu_vm_network(
    vm_id="vm_id",
    interface_id="interface_id",
    workspace_id="workspace_id",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**vm_id:** `str` — Virtual machine ID.
    
</dd>
</dl>

<dl>
<dd>

**interface_id:** `str` — Network interface ID.
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `str` — The workspace ID to scope this request to.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

