# Reference
## Secret Store
<details><summary><code>client.secret_store.<a href="src/ibee/secret_store/client.py">list_secret_stores</a>(...) -> SecretStoreList</code></summary>
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
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
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
<details><summary><code>client.secret_store.<a href="src/ibee/secret_store/client.py">create_secret_store</a>(...) -> SecretStore</code></summary>
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
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
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

<details><summary><code>client.secret_store.<a href="src/ibee/secret_store/client.py">get_secret_store</a>(...) -> SecretStore</code></summary>
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
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
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

<details><summary><code>client.secret_store.<a href="src/ibee/secret_store/client.py">update_secret_store</a>(...) -> SecretStore</code></summary>
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
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
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

<details><summary><code>client.secret_store.<a href="src/ibee/secret_store/client.py">archive_secret_store</a>(...) -> SecretStore</code></summary>
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
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
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

<details><summary><code>client.secret_store.<a href="src/ibee/secret_store/client.py">list_secrets</a>(...) -> SecretList</code></summary>
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
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
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

<details><summary><code>client.secret_store.<a href="src/ibee/secret_store/client.py">create_secret</a>(...) -> Secret</code></summary>
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
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
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

<details><summary><code>client.secret_store.<a href="src/ibee/secret_store/client.py">get_secret</a>(...) -> Secret</code></summary>
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
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
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

<details><summary><code>client.secret_store.<a href="src/ibee/secret_store/client.py">delete_secret</a>(...) -> Secret</code></summary>
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
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
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

<details><summary><code>client.secret_store.<a href="src/ibee/secret_store/client.py">get_secret_value</a>(...) -> SecretValue</code></summary>
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
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
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

<details><summary><code>client.secret_store.<a href="src/ibee/secret_store/client.py">update_secret_value</a>(...) -> SecretValue</code></summary>
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
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
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
<details><summary><code>client.object_storage.<a href="src/ibee/object_storage/client.py">list_buckets</a>(...) -> BucketList</code></summary>
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
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
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

<details><summary><code>client.object_storage.<a href="src/ibee/object_storage/client.py">create_bucket</a>(...) -> Bucket</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Creates an object storage bucket. `region` is required and must match an Object Storage region identifier configured for the target environment. Do not send a compute `site_id`. Requires scope: object-storage.write.
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
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.object_storage.create_bucket(
    workspace_id="workspace_id",
    name="production-assets",
    region="in-south-2",
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

**region:** `str` — Required Object Storage region identifier. This must match a region configured for the target environment; it is not a compute `site_id` or display name.

</dd>
</dl>

<dl>
<dd>

**is_public:** `typing.Optional[bool]` — Whether the bucket allows unauthenticated read access.

</dd>
</dl>

<dl>
<dd>

**object_lock_enabled:** `typing.Optional[bool]` — Must be `true` when `default_retention` is provided.

</dd>
</dl>

<dl>
<dd>

**default_retention:** `typing.Optional[DefaultRetention]`

</dd>
</dl>

<dl>
<dd>

**tags:** `typing.Optional[typing.List[str]]` — Optional tags stored alongside bucket metadata.

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

<details><summary><code>client.object_storage.<a href="src/ibee/object_storage/client.py">get_bucket</a>(...) -> Bucket</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Returns bucket configuration and usage statistics. Requires scope: object-storage.read.
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
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.object_storage.get_bucket(
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

<details><summary><code>client.object_storage.<a href="src/ibee/object_storage/client.py">delete_bucket</a>(...) -> DeleteResponse</code></summary>
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
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
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

<details><summary><code>client.object_storage.<a href="src/ibee/object_storage/client.py">update_bucket</a>(...) -> Bucket</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Updates mutable bucket settings. Requires scope: object-storage.write.
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
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.object_storage.update_bucket(
    bucket_name="bucket_name",
    workspace_id="workspace_id",
    is_public=True,
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

**is_public:** `bool`

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

<details><summary><code>client.object_storage.<a href="src/ibee/object_storage/client.py">list_s3credentials</a>(...) -> S3CredentialList</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Lists S3-compatible credentials without secret keys. Requires scope: object-storage.read.
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
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.object_storage.list_s3credentials(
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

<details><summary><code>client.object_storage.<a href="src/ibee/object_storage/client.py">create_s3credential</a>(...) -> S3CredentialCreated</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Creates an access key pair. The secret is returned only once. Requires scope: object-storage.write.
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
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.object_storage.create_s3credential(
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

**name:** `typing.Optional[str]`

</dd>
</dl>

<dl>
<dd>

**permission_type:** `typing.Optional[str]`

</dd>
</dl>

<dl>
<dd>

**bucket_scope:** `typing.Optional[CreateS3CredentialRequestBucketScope]`

</dd>
</dl>

<dl>
<dd>

**allowed_buckets:** `typing.Optional[typing.List[str]]`

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

<details><summary><code>client.object_storage.<a href="src/ibee/object_storage/client.py">get_s3credential</a>(...) -> S3Credential</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Returns credential metadata without the secret key. Requires scope: object-storage.read.
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
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.object_storage.get_s3credential(
    access_key_id="access_key_id",
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

**access_key_id:** `str` — S3 access key ID.

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

<details><summary><code>client.object_storage.<a href="src/ibee/object_storage/client.py">revoke_s3credential</a>(...) -> S3CredentialRevoked</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Revokes a credential so it can no longer authenticate S3 requests. Requires scope: object-storage.write.
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
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.object_storage.revoke_s3credential(
    access_key_id="access_key_id",
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

**access_key_id:** `str` — S3 access key ID.

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

## Vpcs
<details><summary><code>client.vpcs.<a href="src/ibee/vpcs/client.py">list_networking_sites</a>(...) -> typing.List[NetworkingSite]</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Lists the site IDs accepted by VPC and Reserved IP creation. Use only entries where `available` is `true`. Requires scope: network.read.
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
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.vpcs.list_networking_sites(
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

<details><summary><code>client.vpcs.<a href="src/ibee/vpcs/client.py">list_vpcs</a>(...) -> typing.List[VpcSummary]</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Lists VPCs in the selected workspace. Requires scope: network.read.
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
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.vpcs.list_vpcs(
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

**site_id:** `typing.Optional[str]` — Optional exact site filter. Copy `site_id` from `GET /networking/sites`.

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

<details><summary><code>client.vpcs.<a href="src/ibee/vpcs/client.py">create_vpc</a>(...) -> VpcDetail</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Creates an isolated virtual network. Requires scope: network.write.
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
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.vpcs.create_vpc(
    workspace_id="workspace_id",
    name="name",
    site_id="68b99bd78a8eda32ff3f16ea",
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

**site_id:** `str` — Required network placement site. Copy `site_id` from `GET /networking/sites` and choose an entry where `available` is `true`. Do not use a region name.

</dd>
</dl>

<dl>
<dd>

**description:** `typing.Optional[str]`

</dd>
</dl>

<dl>
<dd>

**region:** `typing.Optional[str]`

</dd>
</dl>

<dl>
<dd>

**cidr:** `typing.Optional[str]` — RFC1918 IPv4 CIDR with a prefix between /22 and /28.

</dd>
</dl>

<dl>
<dd>

**auto_cidr:** `typing.Optional[bool]`

</dd>
</dl>

<dl>
<dd>

**create_default_subnet:** `typing.Optional[bool]`

</dd>
</dl>

<dl>
<dd>

**default_subnet_cidr:** `typing.Optional[str]`

</dd>
</dl>

<dl>
<dd>

**is_default:** `typing.Optional[bool]`

</dd>
</dl>

<dl>
<dd>

**connectivity_type:** `typing.Optional[CreateVpcRequestConnectivityType]`

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

<details><summary><code>client.vpcs.<a href="src/ibee/vpcs/client.py">get_vpc</a>(...) -> VpcDetail</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Returns a VPC and its subnets, NAT gateways, and attached nodes. Requires scope: network.read.
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
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.vpcs.get_vpc(
    vpc_id="vpc_id",
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

**vpc_id:** `str` — VPC ID.

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

<details><summary><code>client.vpcs.<a href="src/ibee/vpcs/client.py">delete_vpc</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Deletes an empty VPC. Requires scope: network.write.
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
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.vpcs.delete_vpc(
    vpc_id="vpc_id",
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

**vpc_id:** `str` — VPC ID.

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

<details><summary><code>client.vpcs.<a href="src/ibee/vpcs/client.py">update_vpc</a>(...) -> VpcDetail</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Updates mutable VPC metadata. Requires scope: network.write.
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
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.vpcs.update_vpc(
    vpc_id="vpc_id",
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

**vpc_id:** `str` — VPC ID.

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

<details><summary><code>client.vpcs.<a href="src/ibee/vpcs/client.py">list_vpc_subnets</a>(...) -> typing.List[Subnet]</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Lists subnets in a VPC. Requires scope: network.read.
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
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.vpcs.list_vpc_subnets(
    vpc_id="vpc_id",
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

**vpc_id:** `str` — VPC ID.

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

<details><summary><code>client.vpcs.<a href="src/ibee/vpcs/client.py">create_vpc_subnet</a>(...) -> Subnet</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Creates a subnet in a VPC. Requires scope: network.write.
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
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.vpcs.create_vpc_subnet(
    vpc_id="vpc_id",
    workspace_id="workspace_id",
    name="name",
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

**vpc_id:** `str` — VPC ID.

</dd>
</dl>

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

**cidr:** `typing.Optional[str]`

</dd>
</dl>

<dl>
<dd>

**auto_cidr:** `typing.Optional[bool]`

</dd>
</dl>

<dl>
<dd>

**prefix_length:** `typing.Optional[int]`

</dd>
</dl>

<dl>
<dd>

**dns:** `typing.Optional[typing.List[str]]`

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

<details><summary><code>client.vpcs.<a href="src/ibee/vpcs/client.py">get_vpc_subnet</a>(...) -> Subnet</code></summary>
<dl>
<dd>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.vpcs.get_vpc_subnet(
    vpc_id="vpc_id",
    subnet_id="subnet_id",
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

**vpc_id:** `str` — VPC ID.

</dd>
</dl>

<dl>
<dd>

**subnet_id:** `str` — Subnet ID.

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

<details><summary><code>client.vpcs.<a href="src/ibee/vpcs/client.py">delete_vpc_subnet</a>(...)</code></summary>
<dl>
<dd>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.vpcs.delete_vpc_subnet(
    vpc_id="vpc_id",
    subnet_id="subnet_id",
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

**vpc_id:** `str` — VPC ID.

</dd>
</dl>

<dl>
<dd>

**subnet_id:** `str` — Subnet ID.

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

<details><summary><code>client.vpcs.<a href="src/ibee/vpcs/client.py">update_vpc_subnet</a>(...) -> Subnet</code></summary>
<dl>
<dd>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.vpcs.update_vpc_subnet(
    vpc_id="vpc_id",
    subnet_id="subnet_id",
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

**vpc_id:** `str` — VPC ID.

</dd>
</dl>

<dl>
<dd>

**subnet_id:** `str` — Subnet ID.

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

**dns:** `typing.Optional[typing.List[str]]`

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

<details><summary><code>client.vpcs.<a href="src/ibee/vpcs/client.py">list_vpc_nodes</a>(...) -> typing.List[NetworkAllocation]</code></summary>
<dl>
<dd>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.vpcs.list_vpc_nodes(
    vpc_id="vpc_id",
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

**vpc_id:** `str` — VPC ID.

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

<details><summary><code>client.vpcs.<a href="src/ibee/vpcs/client.py">attach_vpc_node</a>(...) -> NetworkAllocation</code></summary>
<dl>
<dd>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.vpcs.attach_vpc_node(
    vpc_id="vpc_id",
    workspace_id="workspace_id",
    vm_id="vm_id",
    subnet_id="subnet_id",
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

**vpc_id:** `str` — VPC ID.

</dd>
</dl>

<dl>
<dd>

**workspace_id:** `str` — The workspace ID to scope this request to.

</dd>
</dl>

<dl>
<dd>

**vm_id:** `str`

</dd>
</dl>

<dl>
<dd>

**subnet_id:** `str`

</dd>
</dl>

<dl>
<dd>

**connectivity:** `typing.Optional[AttachVpcNodeRequestConnectivity]`

</dd>
</dl>

<dl>
<dd>

**reserved_public_ip_id:** `typing.Optional[str]`

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

<details><summary><code>client.vpcs.<a href="src/ibee/vpcs/client.py">detach_vpc_node</a>(...)</code></summary>
<dl>
<dd>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.vpcs.detach_vpc_node(
    vpc_id="vpc_id",
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

**vpc_id:** `str` — VPC ID.

</dd>
</dl>

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

<details><summary><code>client.vpcs.<a href="src/ibee/vpcs/client.py">list_nat_gateways</a>(...) -> typing.List[NatGateway]</code></summary>
<dl>
<dd>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.vpcs.list_nat_gateways(
    vpc_id="vpc_id",
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

**vpc_id:** `str` — VPC ID.

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

<details><summary><code>client.vpcs.<a href="src/ibee/vpcs/client.py">create_nat_gateway</a>(...) -> NatGateway</code></summary>
<dl>
<dd>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.vpcs.create_nat_gateway(
    vpc_id="vpc_id",
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

**vpc_id:** `str` — VPC ID.

</dd>
</dl>

<dl>
<dd>

**workspace_id:** `str` — The workspace ID to scope this request to.

</dd>
</dl>

<dl>
<dd>

**subnet_id:** `typing.Optional[str]`

</dd>
</dl>

<dl>
<dd>

**reserved_public_ip_id:** `typing.Optional[str]`

</dd>
</dl>

<dl>
<dd>

**name:** `typing.Optional[str]`

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

<details><summary><code>client.vpcs.<a href="src/ibee/vpcs/client.py">delete_nat_gateway</a>(...)</code></summary>
<dl>
<dd>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.vpcs.delete_nat_gateway(
    vpc_id="vpc_id",
    nat_gateway_id="nat_gateway_id",
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

**vpc_id:** `str` — VPC ID.

</dd>
</dl>

<dl>
<dd>

**nat_gateway_id:** `str` — NAT gateway ID.

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

<details><summary><code>client.vpcs.<a href="src/ibee/vpcs/client.py">list_nat_port_forwarding_rules</a>(...) -> typing.List[NatPortForwardingRule]</code></summary>
<dl>
<dd>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.vpcs.list_nat_port_forwarding_rules(
    vpc_id="vpc_id",
    nat_gateway_id="nat_gateway_id",
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

**vpc_id:** `str` — VPC ID.

</dd>
</dl>

<dl>
<dd>

**nat_gateway_id:** `str` — NAT gateway ID.

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

<details><summary><code>client.vpcs.<a href="src/ibee/vpcs/client.py">create_nat_port_forwarding_rule</a>(...) -> NatPortForwardingRule</code></summary>
<dl>
<dd>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.vpcs.create_nat_port_forwarding_rule(
    vpc_id="vpc_id",
    nat_gateway_id="nat_gateway_id",
    workspace_id="workspace_id",
    name="name",
    external_port=1,
    internal_ip="internal_ip",
    internal_port=1,
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

**vpc_id:** `str` — VPC ID.

</dd>
</dl>

<dl>
<dd>

**nat_gateway_id:** `str` — NAT gateway ID.

</dd>
</dl>

<dl>
<dd>

**workspace_id:** `str` — The workspace ID to scope this request to.

</dd>
</dl>

<dl>
<dd>

**request:** `CreateNatPortForwardingRuleRequest`

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

<details><summary><code>client.vpcs.<a href="src/ibee/vpcs/client.py">delete_nat_port_forwarding_rule</a>(...)</code></summary>
<dl>
<dd>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.vpcs.delete_nat_port_forwarding_rule(
    vpc_id="vpc_id",
    nat_gateway_id="nat_gateway_id",
    port_forwarding_rule_id="port_forwarding_rule_id",
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

**vpc_id:** `str` — VPC ID.

</dd>
</dl>

<dl>
<dd>

**nat_gateway_id:** `str` — NAT gateway ID.

</dd>
</dl>

<dl>
<dd>

**port_forwarding_rule_id:** `str` — NAT port-forwarding rule ID.

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

<details><summary><code>client.vpcs.<a href="src/ibee/vpcs/client.py">update_nat_port_forwarding_rule</a>(...) -> NatPortForwardingRule</code></summary>
<dl>
<dd>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.vpcs.update_nat_port_forwarding_rule(
    vpc_id="vpc_id",
    nat_gateway_id="nat_gateway_id",
    port_forwarding_rule_id="port_forwarding_rule_id",
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

**vpc_id:** `str` — VPC ID.

</dd>
</dl>

<dl>
<dd>

**nat_gateway_id:** `str` — NAT gateway ID.

</dd>
</dl>

<dl>
<dd>

**port_forwarding_rule_id:** `str` — NAT port-forwarding rule ID.

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

**protocol:** `typing.Optional[UpdateNatPortForwardingRuleRequestProtocol]`

</dd>
</dl>

<dl>
<dd>

**external_port:** `typing.Optional[int]`

</dd>
</dl>

<dl>
<dd>

**internal_ip:** `typing.Optional[str]`

</dd>
</dl>

<dl>
<dd>

**internal_port:** `typing.Optional[int]`

</dd>
</dl>

<dl>
<dd>

**note:** `typing.Optional[str]`

</dd>
</dl>

<dl>
<dd>

**enabled:** `typing.Optional[bool]`

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

## ReservedIps
<details><summary><code>client.reserved_ips.<a href="src/ibee/reserved_ips/client.py">list_reserved_ips</a>(...) -> typing.List[ReservedIp]</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Lists customer-reserved public IP addresses. Requires scope: network.read.
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
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.reserved_ips.list_reserved_ips(
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

**site_id:** `typing.Optional[str]` — Optional exact site filter. Copy `site_id` from `GET /networking/sites`.

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

<details><summary><code>client.reserved_ips.<a href="src/ibee/reserved_ips/client.py">reserve_ip</a>(...) -> ReservedIp</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Reserves an address from a site's public IP pool. Discover an available site with `GET /networking/sites`. Requires scope: network.write.
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
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.reserved_ips.reserve_ip(
    workspace_id="workspace_id",
    site_id="68b99bd78a8eda32ff3f16ea",
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

**site_id:** `str` — Site whose public IP pool allocates the address. Copy an available `site_id` from `GET /networking/sites`; use the target VM or VPC's site when the address will be attached.

</dd>
</dl>

<dl>
<dd>

**label:** `typing.Optional[str]`

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

<details><summary><code>client.reserved_ips.<a href="src/ibee/reserved_ips/client.py">get_reserved_ip</a>(...) -> ReservedIp</code></summary>
<dl>
<dd>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.reserved_ips.get_reserved_ip(
    reserved_ip_id="reserved_ip_id",
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

**reserved_ip_id:** `str` — Reserved IP ID.

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

<details><summary><code>client.reserved_ips.<a href="src/ibee/reserved_ips/client.py">release_reserved_ip</a>(...)</code></summary>
<dl>
<dd>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.reserved_ips.release_reserved_ip(
    reserved_ip_id="reserved_ip_id",
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

**reserved_ip_id:** `str` — Reserved IP ID.

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

<details><summary><code>client.reserved_ips.<a href="src/ibee/reserved_ips/client.py">update_reserved_ip</a>(...) -> ReservedIp</code></summary>
<dl>
<dd>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.reserved_ips.update_reserved_ip(
    reserved_ip_id="reserved_ip_id",
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

**reserved_ip_id:** `str` — Reserved IP ID.

</dd>
</dl>

<dl>
<dd>

**workspace_id:** `str` — The workspace ID to scope this request to.

</dd>
</dl>

<dl>
<dd>

**label:** `typing.Optional[str]`

</dd>
</dl>

<dl>
<dd>

**reverse_dns:** `typing.Optional[str]`

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

<details><summary><code>client.reserved_ips.<a href="src/ibee/reserved_ips/client.py">attach_reserved_ip</a>(...) -> ReservedIp</code></summary>
<dl>
<dd>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.reserved_ips.attach_reserved_ip(
    reserved_ip_id="reserved_ip_id",
    workspace_id="workspace_id",
    vm_id="vm_id",
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

**reserved_ip_id:** `str` — Reserved IP ID.

</dd>
</dl>

<dl>
<dd>

**workspace_id:** `str` — The workspace ID to scope this request to.

</dd>
</dl>

<dl>
<dd>

**request:** `AttachReservedIpRequest`

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

<details><summary><code>client.reserved_ips.<a href="src/ibee/reserved_ips/client.py">detach_reserved_ip</a>(...) -> ReservedIp</code></summary>
<dl>
<dd>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.reserved_ips.detach_reserved_ip(
    reserved_ip_id="reserved_ip_id",
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

**reserved_ip_id:** `str` — Reserved IP ID.

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

<details><summary><code>client.reserved_ips.<a href="src/ibee/reserved_ips/client.py">move_reserved_ip</a>(...) -> ReservedIp</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Atomically moves a Reserved IP to another VM attachment.
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
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.reserved_ips.move_reserved_ip(
    reserved_ip_id="reserved_ip_id",
    workspace_id="workspace_id",
    vm_id="vm_id",
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

**reserved_ip_id:** `str` — Reserved IP ID.

</dd>
</dl>

<dl>
<dd>

**workspace_id:** `str` — The workspace ID to scope this request to.

</dd>
</dl>

<dl>
<dd>

**request:** `AttachReservedIpRequest`

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

## Firewalls
<details><summary><code>client.firewalls.<a href="src/ibee/firewalls/client.py">list_firewall_groups</a>(...) -> typing.List[FirewallGroup]</code></summary>
<dl>
<dd>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.firewalls.list_firewall_groups(
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

<details><summary><code>client.firewalls.<a href="src/ibee/firewalls/client.py">create_firewall_group</a>(...) -> FirewallGroup</code></summary>
<dl>
<dd>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.firewalls.create_firewall_group(
    workspace_id="workspace_id",
    name="name",
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

**is_default:** `typing.Optional[bool]`

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

<details><summary><code>client.firewalls.<a href="src/ibee/firewalls/client.py">get_firewall_group</a>(...) -> FirewallGroup</code></summary>
<dl>
<dd>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.firewalls.get_firewall_group(
    firewall_group_id="firewall_group_id",
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

**firewall_group_id:** `str` — Firewall group ID.

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

<details><summary><code>client.firewalls.<a href="src/ibee/firewalls/client.py">delete_firewall_group</a>(...)</code></summary>
<dl>
<dd>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.firewalls.delete_firewall_group(
    firewall_group_id="firewall_group_id",
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

**firewall_group_id:** `str` — Firewall group ID.

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

<details><summary><code>client.firewalls.<a href="src/ibee/firewalls/client.py">create_firewall_rule</a>(...) -> FirewallGroup</code></summary>
<dl>
<dd>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.firewalls.create_firewall_rule(
    firewall_group_id="firewall_group_id",
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

**firewall_group_id:** `str` — Firewall group ID.

</dd>
</dl>

<dl>
<dd>

**workspace_id:** `str` — The workspace ID to scope this request to.

</dd>
</dl>

<dl>
<dd>

**request:** `CreateFirewallRuleRequest`

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

<details><summary><code>client.firewalls.<a href="src/ibee/firewalls/client.py">delete_firewall_rule</a>(...) -> FirewallGroup</code></summary>
<dl>
<dd>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.firewalls.delete_firewall_rule(
    firewall_group_id="firewall_group_id",
    firewall_rule_id="firewall_rule_id",
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

**firewall_group_id:** `str` — Firewall group ID.

</dd>
</dl>

<dl>
<dd>

**firewall_rule_id:** `str` — Firewall rule ID.

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

<details><summary><code>client.firewalls.<a href="src/ibee/firewalls/client.py">update_firewall_rule</a>(...) -> FirewallGroup</code></summary>
<dl>
<dd>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.firewalls.update_firewall_rule(
    firewall_group_id="firewall_group_id",
    firewall_rule_id="firewall_rule_id",
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

**firewall_group_id:** `str` — Firewall group ID.

</dd>
</dl>

<dl>
<dd>

**firewall_rule_id:** `str` — Firewall rule ID.

</dd>
</dl>

<dl>
<dd>

**workspace_id:** `str` — The workspace ID to scope this request to.

</dd>
</dl>

<dl>
<dd>

**description:** `typing.Optional[str]`

</dd>
</dl>

<dl>
<dd>

**direction:** `typing.Optional[FirewallRuleFieldsDirection]`

</dd>
</dl>

<dl>
<dd>

**protocol:** `typing.Optional[FirewallRuleFieldsProtocol]`

</dd>
</dl>

<dl>
<dd>

**port_start:** `typing.Optional[int]`

</dd>
</dl>

<dl>
<dd>

**port_end:** `typing.Optional[int]`

</dd>
</dl>

<dl>
<dd>

**remote_targets:** `typing.Optional[typing.List[str]]`

</dd>
</dl>

<dl>
<dd>

**action:** `typing.Optional[FirewallRuleFieldsAction]`

</dd>
</dl>

<dl>
<dd>

**priority:** `typing.Optional[int]`

</dd>
</dl>

<dl>
<dd>

**enabled:** `typing.Optional[bool]`

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

<details><summary><code>client.firewalls.<a href="src/ibee/firewalls/client.py">list_firewall_group_attachments</a>(...) -> typing.List[FirewallAttachment]</code></summary>
<dl>
<dd>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.firewalls.list_firewall_group_attachments(
    firewall_group_id="firewall_group_id",
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

**firewall_group_id:** `str` — Firewall group ID.

</dd>
</dl>

<dl>
<dd>

**workspace_id:** `str` — The workspace ID to scope this request to.

</dd>
</dl>

<dl>
<dd>

**limit:** `typing.Optional[int]` — Maximum number of records to return.

</dd>
</dl>

<dl>
<dd>

**skip:** `typing.Optional[int]`

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

<details><summary><code>client.firewalls.<a href="src/ibee/firewalls/client.py">attach_firewall_group</a>(...) -> FirewallGroup</code></summary>
<dl>
<dd>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.firewalls.attach_firewall_group(
    firewall_group_id="firewall_group_id",
    workspace_id="workspace_id",
    vm_id="vm_id",
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

**firewall_group_id:** `str` — Firewall group ID.

</dd>
</dl>

<dl>
<dd>

**workspace_id:** `str` — The workspace ID to scope this request to.

</dd>
</dl>

<dl>
<dd>

**vm_id:** `str`

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

<details><summary><code>client.firewalls.<a href="src/ibee/firewalls/client.py">detach_firewall_group</a>(...) -> FirewallGroup</code></summary>
<dl>
<dd>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.firewalls.detach_firewall_group(
    firewall_group_id="firewall_group_id",
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

**firewall_group_id:** `str` — Firewall group ID.

</dd>
</dl>

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

## LoadBalancers
<details><summary><code>client.load_balancers.<a href="src/ibee/load_balancers/client.py">list_load_balancers</a>(...) -> typing.List[LoadBalancer]</code></summary>
<dl>
<dd>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.load_balancers.list_load_balancers(
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

**status:** `typing.Optional[LoadBalancerStatus]`

</dd>
</dl>

<dl>
<dd>

**layer:** `typing.Optional[ListLoadBalancersRequestLayer]`

</dd>
</dl>

<dl>
<dd>

**protocol:** `typing.Optional[LoadBalancerProtocol]`

</dd>
</dl>

<dl>
<dd>

**limit:** `typing.Optional[int]`

</dd>
</dl>

<dl>
<dd>

**skip:** `typing.Optional[int]`

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

<details><summary><code>client.load_balancers.<a href="src/ibee/load_balancers/client.py">create_l4load_balancer</a>(...) -> LoadBalancer</code></summary>
<dl>
<dd>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from ibee import Ibee, LoadBalancerBackend
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.load_balancers.create_l4load_balancer(
    workspace_id="workspace_id",
    name="name",
    protocol="tcp",
    backends=[
        LoadBalancerBackend(
            target="target",
            port=1,
        )
    ],
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

**protocol:** `CreateL4LoadBalancerRequestProtocol`

</dd>
</dl>

<dl>
<dd>

**backends:** `typing.List[LoadBalancerBackend]`

</dd>
</dl>

<dl>
<dd>

**routing:** `typing.Optional[LoadBalancerRouting]`

</dd>
</dl>

<dl>
<dd>

**tls:** `typing.Optional[LoadBalancerTls]`

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

<details><summary><code>client.load_balancers.<a href="src/ibee/load_balancers/client.py">create_l7load_balancer</a>(...) -> LoadBalancer</code></summary>
<dl>
<dd>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from ibee import Ibee, LoadBalancerBackend
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.load_balancers.create_l7load_balancer(
    workspace_id="workspace_id",
    name="name",
    protocol="http",
    backends=[
        LoadBalancerBackend(
            target="target",
            port=1,
        )
    ],
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

**protocol:** `CreateL7LoadBalancerRequestProtocol`

</dd>
</dl>

<dl>
<dd>

**backends:** `typing.List[LoadBalancerBackend]`

</dd>
</dl>

<dl>
<dd>

**routing:** `typing.Optional[LoadBalancerRouting]`

</dd>
</dl>

<dl>
<dd>

**tls:** `typing.Optional[LoadBalancerTls]`

</dd>
</dl>

<dl>
<dd>

**custom_domain:** `typing.Optional[CreateL7LoadBalancerRequestCustomDomain]`

</dd>
</dl>

<dl>
<dd>

**rules:** `typing.Optional[typing.List[LoadBalancerRule]]`

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

<details><summary><code>client.load_balancers.<a href="src/ibee/load_balancers/client.py">get_load_balancer</a>(...) -> LoadBalancer</code></summary>
<dl>
<dd>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.load_balancers.get_load_balancer(
    load_balancer_id="load_balancer_id",
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

**load_balancer_id:** `str` — Load balancer ID.

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

<details><summary><code>client.load_balancers.<a href="src/ibee/load_balancers/client.py">delete_load_balancer</a>(...)</code></summary>
<dl>
<dd>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.load_balancers.delete_load_balancer(
    load_balancer_id="load_balancer_id",
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

**load_balancer_id:** `str` — Load balancer ID.

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

<details><summary><code>client.load_balancers.<a href="src/ibee/load_balancers/client.py">update_l4load_balancer</a>(...) -> LoadBalancer</code></summary>
<dl>
<dd>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.load_balancers.update_l4load_balancer(
    load_balancer_id="load_balancer_id",
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

**load_balancer_id:** `str` — Load balancer ID.

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

**backends:** `typing.Optional[typing.List[LoadBalancerBackend]]`

</dd>
</dl>

<dl>
<dd>

**routing:** `typing.Optional[LoadBalancerRouting]`

</dd>
</dl>

<dl>
<dd>

**tls:** `typing.Optional[LoadBalancerTls]`

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

<details><summary><code>client.load_balancers.<a href="src/ibee/load_balancers/client.py">update_l7load_balancer</a>(...) -> LoadBalancer</code></summary>
<dl>
<dd>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.load_balancers.update_l7load_balancer(
    load_balancer_id="load_balancer_id",
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

**load_balancer_id:** `str` — Load balancer ID.

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

**backends:** `typing.Optional[typing.List[LoadBalancerBackend]]`

</dd>
</dl>

<dl>
<dd>

**routing:** `typing.Optional[LoadBalancerRouting]`

</dd>
</dl>

<dl>
<dd>

**tls:** `typing.Optional[LoadBalancerTls]`

</dd>
</dl>

<dl>
<dd>

**custom_domain:** `typing.Optional[UpdateL7LoadBalancerRequestCustomDomain]`

</dd>
</dl>

<dl>
<dd>

**rules:** `typing.Optional[typing.List[LoadBalancerRule]]`

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

<details><summary><code>client.load_balancers.<a href="src/ibee/load_balancers/client.py">get_load_balancer_status</a>(...) -> LoadBalancerStatusResponse</code></summary>
<dl>
<dd>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.load_balancers.get_load_balancer_status(
    load_balancer_id="load_balancer_id",
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

**load_balancer_id:** `str` — Load balancer ID.

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

## ComputeCatalog
<details><summary><code>client.compute_catalog.<a href="src/ibee/compute_catalog/client.py">list_compute_sites</a>(...) -> ComputeSiteList</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Lists sites where cloud and GPU VMs can be placed. Requires scope: vm.read.
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
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.compute_catalog.list_compute_sites(
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

<details><summary><code>client.compute_catalog.<a href="src/ibee/compute_catalog/client.py">list_compute_plans</a>(...) -> ComputePlanList</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Lists billable cloud or GPU VM plans. Requires scope: vm.read.
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
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.compute_catalog.list_compute_plans(
    workspace_id="workspace_id",
    vm_type="cloud",
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

**vm_type:** `VmType`

</dd>
</dl>

<dl>
<dd>

**site_id:** `typing.Optional[str]` — Optional exact placement filter. Copy `site_id` from `GET /compute/sites`.

</dd>
</dl>

<dl>
<dd>

**currency:** `typing.Optional[str]`

</dd>
</dl>

<dl>
<dd>

**billing_interval:** `typing.Optional[BillingInterval]`

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

<details><summary><code>client.compute_catalog.<a href="src/ibee/compute_catalog/client.py">list_compute_images</a>(...) -> ComputeImageList</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Lists ready public OS images compatible with cloud or GPU VMs. Requires scope: vm.read.
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
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.compute_catalog.list_compute_images(
    workspace_id="workspace_id",
    vm_type="cloud",
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

**vm_type:** `VmType`

</dd>
</dl>

<dl>
<dd>

**site_id:** `typing.Optional[str]` — Optional exact placement filter. Copy `site_id` from `GET /compute/sites`.

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
<details><summary><code>client.cloud_vms.<a href="src/ibee/cloud_vms/client.py">list_cloud_vms</a>(...) -> typing.List[CloudVm]</code></summary>
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
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
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

<details><summary><code>client.cloud_vms.<a href="src/ibee/cloud_vms/client.py">create_cloud_vm</a>(...) -> OperationAccepted</code></summary>
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
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.cloud_vms.create_cloud_vm(
    workspace_id="workspace_id",
    idempotency_key="X-Idempotency-Key",
    name="web-server-01",
    os_distro="ubuntu",
    os_type="linux",
    template_id="tmpl_ubuntu_2204",
    cpu=2,
    ram_mb=4096,
    plan_id="plan_id",
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

**template_id:** `str` — OS template or image ID returned by the compute catalog.

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

**plan_id:** `str` — Billable compute plan ID returned by the compute catalog.

</dd>
</dl>

<dl>
<dd>

**site_id:** `typing.Optional[str]` — Optional placement site ID. Omit for automatic placement. To pin the VM, copy `site_id` from `GET /compute/sites` and use the same value when filtering plans and images.

</dd>
</dl>

<dl>
<dd>

**disk_gb:** `typing.Optional[int]` — Root disk size in gigabytes.

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

<details><summary><code>client.cloud_vms.<a href="src/ibee/cloud_vms/client.py">get_cloud_vm</a>(...) -> CloudVm</code></summary>
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
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
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

<details><summary><code>client.cloud_vms.<a href="src/ibee/cloud_vms/client.py">delete_cloud_vm</a>(...) -> OperationAccepted</code></summary>
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
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
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

<details><summary><code>client.cloud_vms.<a href="src/ibee/cloud_vms/client.py">start_cloud_vm</a>(...) -> OperationAccepted</code></summary>
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
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
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

<details><summary><code>client.cloud_vms.<a href="src/ibee/cloud_vms/client.py">stop_cloud_vm</a>(...) -> OperationAccepted</code></summary>
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
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
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

<details><summary><code>client.cloud_vms.<a href="src/ibee/cloud_vms/client.py">reboot_cloud_vm</a>(...) -> OperationAccepted</code></summary>
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
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
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

<details><summary><code>client.cloud_vms.<a href="src/ibee/cloud_vms/client.py">get_cloud_vm_metrics</a>(...) -> VmMetrics</code></summary>
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
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
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

<details><summary><code>client.cloud_vms.<a href="src/ibee/cloud_vms/client.py">update_cloud_vm_access</a>(...) -> OperationAccepted</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Adds or removes SSH keys, resets the Linux user password, or changes SSH password authentication without rebooting the VM. Requires scope: vm.write.
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
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.cloud_vms.update_cloud_vm_access(
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

**request:** `VmAccessUpdateRequest`

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

<details><summary><code>client.cloud_vms.<a href="src/ibee/cloud_vms/client.py">precheck_cloud_vm_resize</a>(...) -> VmResizePrecheck</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Evaluates a requested CPU, memory, or root-disk change before starting it. Requires scope: vm.write.
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
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.cloud_vms.precheck_cloud_vm_resize(
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

**request:** `VmResizeRequest`

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

<details><summary><code>client.cloud_vms.<a href="src/ibee/cloud_vms/client.py">resize_cloud_vm</a>(...) -> OperationAccepted</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Changes CPU, memory, and optionally increases the root disk after the same precheck used by the portal. Requires scope: vm.write.
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
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.cloud_vms.resize_cloud_vm(
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

**request:** `VmResizeRequest`

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

<details><summary><code>client.cloud_vms.<a href="src/ibee/cloud_vms/client.py">resize_cloud_vm_plan</a>(...) -> OperationAccepted</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Changes the VM CPU and memory shape. Downgrades require explicit confirmation. Requires scope: vm.write.
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
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.cloud_vms.resize_cloud_vm_plan(
    vm_id="vm_id",
    workspace_id="workspace_id",
    idempotency_key="X-Idempotency-Key",
    cpu=1,
    ram_mb=1,
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

**request:** `VmResizePlanRequest`

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

<details><summary><code>client.cloud_vms.<a href="src/ibee/cloud_vms/client.py">resize_cloud_vm_root_disk</a>(...) -> OperationAccepted</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Increases the root disk size; shrinking is not supported. Requires scope: vm.write.
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
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.cloud_vms.resize_cloud_vm_root_disk(
    vm_id="vm_id",
    workspace_id="workspace_id",
    idempotency_key="X-Idempotency-Key",
    new_size_gb=1,
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

**request:** `VmResizeRootDiskRequest`

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

<details><summary><code>client.cloud_vms.<a href="src/ibee/cloud_vms/client.py">attach_cloud_vm_volume</a>(...) -> OperationAccepted</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Attaches a persistent block volume to the VM. Requires scope: vm.write.
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
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.cloud_vms.attach_cloud_vm_volume(
    vm_id="vm_id",
    workspace_id="workspace_id",
    idempotency_key="X-Idempotency-Key",
    volume_id="volume_id",
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

**request:** `VmAttachVolumeRequest`

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

<details><summary><code>client.cloud_vms.<a href="src/ibee/cloud_vms/client.py">detach_cloud_vm_volume</a>(...) -> OperationAccepted</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Detaches a persistent block volume. Confirm the guest filesystem is unmounted unless force is used. Requires scope: vm.write.
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
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.cloud_vms.detach_cloud_vm_volume(
    vm_id="vm_id",
    workspace_id="workspace_id",
    idempotency_key="X-Idempotency-Key",
    volume_id="volume_id",
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

**request:** `VmDetachVolumeRequest`

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

<details><summary><code>client.cloud_vms.<a href="src/ibee/cloud_vms/client.py">acknowledge_cloud_vm_mount_guidance</a>(...) -> MountGuidanceAcknowledge</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Records that the client has reviewed the guest mount instructions for an attached data volume. Requires scope: vm.write.
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
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.cloud_vms.acknowledge_cloud_vm_mount_guidance(
    vm_id="vm_id",
    workspace_id="workspace_id",
    volume_id="volume_id",
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

**request:** `MountGuidanceAcknowledgeRequest`

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

<details><summary><code>client.cloud_vms.<a href="src/ibee/cloud_vms/client.py">list_cloud_vm_events</a>(...) -> typing.List[VmEvent]</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Returns the VM lifecycle and operation event timeline. Requires scope: vm.read.
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
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.cloud_vms.list_cloud_vm_events(
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

**limit:** `typing.Optional[int]`

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

<details><summary><code>client.cloud_vms.<a href="src/ibee/cloud_vms/client.py">get_cloud_vm_metrics_timeseries</a>(...) -> VmMetricsTimeseries</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Returns rolled-up VM metric series for a supported time range. Requires scope: vm.read.
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
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.cloud_vms.get_cloud_vm_metrics_timeseries(
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

**range:** `typing.Optional[GetCloudVmMetricsTimeseriesRequestRange]`

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

<details><summary><code>client.cloud_vms.<a href="src/ibee/cloud_vms/client.py">get_cloud_vm_bandwidth</a>(...) -> VmBandwidthSummary</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Returns received and transmitted byte totals for a calendar month. Requires scope: vm.read.
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
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.cloud_vms.get_cloud_vm_bandwidth(
    vm_id="vm_id",
    workspace_id="workspace_id",
    month="2026-08",
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

**month:** `str`

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

<details><summary><code>client.cloud_vms.<a href="src/ibee/cloud_vms/client.py">list_cloud_vm_snapshots</a>(...) -> SnapshotSetList</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Lists recovery snapshots for one cloud VM. Requires scope: vm.read.
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
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.cloud_vms.list_cloud_vm_snapshots(
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

**limit:** `typing.Optional[int]` — Maximum number of records to return.

</dd>
</dl>

<dl>
<dd>

**offset:** `typing.Optional[int]`

</dd>
</dl>

<dl>
<dd>

**search:** `typing.Optional[str]`

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

<details><summary><code>client.cloud_vms.<a href="src/ibee/cloud_vms/client.py">create_cloud_vm_snapshot</a>(...) -> SnapshotSet</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Creates a recovery snapshot of the root disk, all attached disks, or selected data disks. Requires scope: vm.write.
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
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.cloud_vms.create_cloud_vm_snapshot(
    vm_id="vm_id",
    workspace_id="workspace_id",
    name="name",
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

**request:** `SnapshotCreateRequest`

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

<details><summary><code>client.cloud_vms.<a href="src/ibee/cloud_vms/client.py">restore_cloud_vm_snapshot</a>(...) -> RecoveryRestore</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Restores a snapshot by replacing a VM, creating a new VM, or restoring one volume. Requires scope: vm.write.
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
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.cloud_vms.restore_cloud_vm_snapshot(
    snapshot_set_id="snapshot_set_id",
    workspace_id="workspace_id",
    vm_id="vm_id",
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

**snapshot_set_id:** `str` — VM snapshot-set ID.

</dd>
</dl>

<dl>
<dd>

**workspace_id:** `str` — The workspace ID to scope this request to.

</dd>
</dl>

<dl>
<dd>

**vm_id:** `str` — Source VM ID for the snapshot.

</dd>
</dl>

<dl>
<dd>

**request:** `RecoveryRestoreRequest`

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

<details><summary><code>client.cloud_vms.<a href="src/ibee/cloud_vms/client.py">get_cloud_vm_snapshot</a>(...) -> SnapshotSet</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Returns one workspace-owned cloud VM snapshot set. Requires scope: vm.read.
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
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.cloud_vms.get_cloud_vm_snapshot(
    snapshot_set_id="snapshot_set_id",
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

**snapshot_set_id:** `str` — VM snapshot-set ID.

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

<details><summary><code>client.cloud_vms.<a href="src/ibee/cloud_vms/client.py">delete_cloud_vm_snapshot</a>(...) -> SnapshotDeleteResult</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Deletes a cloud VM snapshot set when no restore is running. Requires scope: vm.write.
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
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.cloud_vms.delete_cloud_vm_snapshot(
    snapshot_set_id="snapshot_set_id",
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

**snapshot_set_id:** `str` — VM snapshot-set ID.

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

<details><summary><code>client.cloud_vms.<a href="src/ibee/cloud_vms/client.py">get_cloud_vm_snapshot_restore</a>(...) -> RecoveryRestore</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Returns the current status of a cloud VM snapshot restore. Requires scope: vm.read.
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
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.cloud_vms.get_cloud_vm_snapshot_restore(
    restore_id="restore_id",
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

**restore_id:** `str` — Snapshot or backup restore operation ID.

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

<details><summary><code>client.cloud_vms.<a href="src/ibee/cloud_vms/client.py">get_cloud_vm_backup_policy</a>(...) -> BackupPolicy</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Returns the effective automated backup policy, including disabled state. Requires scope: vm.read.
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
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.cloud_vms.get_cloud_vm_backup_policy(
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

<details><summary><code>client.cloud_vms.<a href="src/ibee/cloud_vms/client.py">update_cloud_vm_backup_policy</a>(...) -> BackupPolicy</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Updates the automated backup schedule and retention settings. Requires scope: vm.write.
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
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.cloud_vms.update_cloud_vm_backup_policy(
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

**request:** `BackupPolicyUpdateRequest`

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

<details><summary><code>client.cloud_vms.<a href="src/ibee/cloud_vms/client.py">enable_cloud_vm_backups</a>(...) -> BackupPolicy</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Enables automated backups and creates the VM backup policy. Requires scope: vm.write.
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
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.cloud_vms.enable_cloud_vm_backups(
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

**request:** `BackupPolicyEnableRequest`

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

<details><summary><code>client.cloud_vms.<a href="src/ibee/cloud_vms/client.py">disable_cloud_vm_backups</a>(...) -> BackupPolicy</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Disables future automated backup runs without deleting existing recovery points. Requires scope: vm.write.
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
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.cloud_vms.disable_cloud_vm_backups(
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

**request:** `BackupPolicyDisableRequest`

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

<details><summary><code>client.cloud_vms.<a href="src/ibee/cloud_vms/client.py">reschedule_cloud_vm_backup</a>(...) -> BackupPolicy</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Sets the next automated backup execution time. Requires scope: vm.write.
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
from ibee import Ibee
from ibee.environment import IbeeEnvironment
import datetime

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.cloud_vms.reschedule_cloud_vm_backup(
    vm_id="vm_id",
    workspace_id="workspace_id",
    next_run_at=datetime.datetime.fromisoformat("2024-01-15T09:30:00+00:00"),
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

**request:** `BackupPolicyNextRunRequest`

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

<details><summary><code>client.cloud_vms.<a href="src/ibee/cloud_vms/client.py">list_cloud_vm_backup_runs</a>(...) -> BackupRunList</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Lists backup runs and usable recovery points for one cloud VM. Requires scope: vm.read.
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
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.cloud_vms.list_cloud_vm_backup_runs(
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

**limit:** `typing.Optional[int]` — Maximum number of records to return.

</dd>
</dl>

<dl>
<dd>

**offset:** `typing.Optional[int]`

</dd>
</dl>

<dl>
<dd>

**search:** `typing.Optional[str]`

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

<details><summary><code>client.cloud_vms.<a href="src/ibee/cloud_vms/client.py">create_cloud_vm_backup_run</a>(...) -> BackupRun</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Queues a manual backup using the VM's backup configuration. Requires scope: vm.write.
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
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.cloud_vms.create_cloud_vm_backup_run(
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

**request:** `ManualBackupRunRequest`

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

<details><summary><code>client.cloud_vms.<a href="src/ibee/cloud_vms/client.py">restore_cloud_vm_backup</a>(...) -> RecoveryRestore</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Restores a backup recovery point by replacing a VM, creating a new VM, or restoring one volume. Requires scope: vm.write.
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
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.cloud_vms.restore_cloud_vm_backup(
    vm_id="vm_id",
    workspace_id="workspace_id",
    recovery_point_id="recovery_point_id",
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

**request:** `BackupRestoreRequest`

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

<details><summary><code>client.cloud_vms.<a href="src/ibee/cloud_vms/client.py">get_cloud_vm_backup_run</a>(...) -> BackupRun</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Returns one workspace-owned cloud VM backup run or recovery point. Requires scope: vm.read.
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
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.cloud_vms.get_cloud_vm_backup_run(
    run_id="run_id",
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

**run_id:** `str` — Backup run or recovery-point ID.

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

<details><summary><code>client.cloud_vms.<a href="src/ibee/cloud_vms/client.py">get_cloud_vm_backup_restore</a>(...) -> RecoveryRestore</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Returns the current status of a cloud VM backup restore. Requires scope: vm.read.
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
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.cloud_vms.get_cloud_vm_backup_restore(
    restore_id="restore_id",
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

**restore_id:** `str` — Snapshot or backup restore operation ID.

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

<details><summary><code>client.cloud_vms.<a href="src/ibee/cloud_vms/client.py">get_compute_operation</a>(...) -> OperationStatus</code></summary>
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
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
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
<details><summary><code>client.gpu_vms.<a href="src/ibee/gpu_vms/client.py">list_gpu_vms</a>(...) -> typing.List[GpuVm]</code></summary>
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
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
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

<details><summary><code>client.gpu_vms.<a href="src/ibee/gpu_vms/client.py">create_gpu_vm</a>(...) -> OperationAccepted</code></summary>
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
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.gpu_vms.create_gpu_vm(
    workspace_id="workspace_id",
    idempotency_key="X-Idempotency-Key",
    name="ml-training-01",
    os_distro="ubuntu",
    os_type="linux",
    template_id="tmpl_ubuntu_2204_cuda",
    cpu=8,
    ram_mb=32768,
    gpu_count=1,
    gpu_model="A100",
    plan_id="plan_id",
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

**template_id:** `str` — GPU-compatible template ID returned by the compute catalog.

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

**plan_id:** `str` — Billable GPU plan ID returned by the compute catalog.

</dd>
</dl>

<dl>
<dd>

**site_id:** `typing.Optional[str]` — Optional placement site ID. Omit for automatic placement. To pin the VM, copy `site_id` from `GET /compute/sites` and use the same value when filtering plans and images.

</dd>
</dl>

<dl>
<dd>

**disk_gb:** `typing.Optional[int]` — Root disk size in gigabytes.

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

<details><summary><code>client.gpu_vms.<a href="src/ibee/gpu_vms/client.py">get_gpu_vm</a>(...) -> GpuVm</code></summary>
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
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
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

<details><summary><code>client.gpu_vms.<a href="src/ibee/gpu_vms/client.py">delete_gpu_vm</a>(...) -> OperationAccepted</code></summary>
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
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
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

<details><summary><code>client.gpu_vms.<a href="src/ibee/gpu_vms/client.py">start_gpu_vm</a>(...) -> OperationAccepted</code></summary>
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
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
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

<details><summary><code>client.gpu_vms.<a href="src/ibee/gpu_vms/client.py">stop_gpu_vm</a>(...) -> OperationAccepted</code></summary>
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
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
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

<details><summary><code>client.gpu_vms.<a href="src/ibee/gpu_vms/client.py">reboot_gpu_vm</a>(...) -> OperationAccepted</code></summary>
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
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
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

<details><summary><code>client.gpu_vms.<a href="src/ibee/gpu_vms/client.py">get_gpu_vm_metrics</a>(...) -> VmMetrics</code></summary>
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
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
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

<details><summary><code>client.gpu_vms.<a href="src/ibee/gpu_vms/client.py">update_gpu_vm_access</a>(...) -> OperationAccepted</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Adds or removes SSH keys, resets the Linux user password, or changes SSH password authentication without rebooting the VM. Requires scope: vm.write.
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
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.gpu_vms.update_gpu_vm_access(
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

**request:** `VmAccessUpdateRequest`

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

<details><summary><code>client.gpu_vms.<a href="src/ibee/gpu_vms/client.py">precheck_gpu_vm_resize</a>(...) -> VmResizePrecheck</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Evaluates a requested CPU, memory, or root-disk change before starting it. Requires scope: vm.write.
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
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.gpu_vms.precheck_gpu_vm_resize(
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

**request:** `VmResizeRequest`

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

<details><summary><code>client.gpu_vms.<a href="src/ibee/gpu_vms/client.py">resize_gpu_vm</a>(...) -> OperationAccepted</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Changes CPU, memory, and optionally increases the root disk after the same precheck used by the portal. Requires scope: vm.write.
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
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.gpu_vms.resize_gpu_vm(
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

**request:** `VmResizeRequest`

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

<details><summary><code>client.gpu_vms.<a href="src/ibee/gpu_vms/client.py">resize_gpu_vm_plan</a>(...) -> OperationAccepted</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Changes the VM CPU and memory shape. Downgrades require explicit confirmation. Requires scope: vm.write.
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
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.gpu_vms.resize_gpu_vm_plan(
    vm_id="vm_id",
    workspace_id="workspace_id",
    idempotency_key="X-Idempotency-Key",
    cpu=1,
    ram_mb=1,
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

**request:** `VmResizePlanRequest`

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

<details><summary><code>client.gpu_vms.<a href="src/ibee/gpu_vms/client.py">resize_gpu_vm_root_disk</a>(...) -> OperationAccepted</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Increases the root disk size; shrinking is not supported. Requires scope: vm.write.
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
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.gpu_vms.resize_gpu_vm_root_disk(
    vm_id="vm_id",
    workspace_id="workspace_id",
    idempotency_key="X-Idempotency-Key",
    new_size_gb=1,
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

**request:** `VmResizeRootDiskRequest`

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

<details><summary><code>client.gpu_vms.<a href="src/ibee/gpu_vms/client.py">attach_gpu_vm_volume</a>(...) -> OperationAccepted</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Attaches a persistent block volume to the VM. Requires scope: vm.write.
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
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.gpu_vms.attach_gpu_vm_volume(
    vm_id="vm_id",
    workspace_id="workspace_id",
    idempotency_key="X-Idempotency-Key",
    volume_id="volume_id",
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

**request:** `VmAttachVolumeRequest`

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

<details><summary><code>client.gpu_vms.<a href="src/ibee/gpu_vms/client.py">detach_gpu_vm_volume</a>(...) -> OperationAccepted</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Detaches a persistent block volume. Confirm the guest filesystem is unmounted unless force is used. Requires scope: vm.write.
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
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.gpu_vms.detach_gpu_vm_volume(
    vm_id="vm_id",
    workspace_id="workspace_id",
    idempotency_key="X-Idempotency-Key",
    volume_id="volume_id",
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

**request:** `VmDetachVolumeRequest`

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

<details><summary><code>client.gpu_vms.<a href="src/ibee/gpu_vms/client.py">acknowledge_gpu_vm_mount_guidance</a>(...) -> MountGuidanceAcknowledge</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Records that the client has reviewed the guest mount instructions for an attached data volume. Requires scope: vm.write.
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
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.gpu_vms.acknowledge_gpu_vm_mount_guidance(
    vm_id="vm_id",
    workspace_id="workspace_id",
    volume_id="volume_id",
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

**request:** `MountGuidanceAcknowledgeRequest`

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

<details><summary><code>client.gpu_vms.<a href="src/ibee/gpu_vms/client.py">list_gpu_vm_events</a>(...) -> typing.List[VmEvent]</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Returns the VM lifecycle and operation event timeline. Requires scope: vm.read.
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
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.gpu_vms.list_gpu_vm_events(
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

**limit:** `typing.Optional[int]`

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

<details><summary><code>client.gpu_vms.<a href="src/ibee/gpu_vms/client.py">get_gpu_vm_metrics_timeseries</a>(...) -> VmMetricsTimeseries</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Returns rolled-up VM metric series for a supported time range. Requires scope: vm.read.
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
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.gpu_vms.get_gpu_vm_metrics_timeseries(
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

**range:** `typing.Optional[GetGpuVmMetricsTimeseriesRequestRange]`

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

<details><summary><code>client.gpu_vms.<a href="src/ibee/gpu_vms/client.py">get_gpu_vm_bandwidth</a>(...) -> VmBandwidthSummary</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Returns received and transmitted byte totals for a calendar month. Requires scope: vm.read.
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
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.gpu_vms.get_gpu_vm_bandwidth(
    vm_id="vm_id",
    workspace_id="workspace_id",
    month="2026-08",
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

**month:** `str`

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

<details><summary><code>client.gpu_vms.<a href="src/ibee/gpu_vms/client.py">list_gpu_vm_snapshots</a>(...) -> SnapshotSetList</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Lists recovery snapshots for one GPU VM. Requires scope: vm.read.
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
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.gpu_vms.list_gpu_vm_snapshots(
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

**limit:** `typing.Optional[int]` — Maximum number of records to return.

</dd>
</dl>

<dl>
<dd>

**offset:** `typing.Optional[int]`

</dd>
</dl>

<dl>
<dd>

**search:** `typing.Optional[str]`

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

<details><summary><code>client.gpu_vms.<a href="src/ibee/gpu_vms/client.py">create_gpu_vm_snapshot</a>(...) -> SnapshotSet</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Creates a recovery snapshot of the root disk, all attached disks, or selected data disks. Requires scope: vm.write.
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
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.gpu_vms.create_gpu_vm_snapshot(
    vm_id="vm_id",
    workspace_id="workspace_id",
    name="name",
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

**request:** `SnapshotCreateRequest`

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

<details><summary><code>client.gpu_vms.<a href="src/ibee/gpu_vms/client.py">restore_gpu_vm_snapshot</a>(...) -> RecoveryRestore</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Restores a snapshot by replacing a VM, creating a new VM, or restoring one volume. Requires scope: vm.write.
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
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.gpu_vms.restore_gpu_vm_snapshot(
    snapshot_set_id="snapshot_set_id",
    workspace_id="workspace_id",
    vm_id="vm_id",
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

**snapshot_set_id:** `str` — VM snapshot-set ID.

</dd>
</dl>

<dl>
<dd>

**workspace_id:** `str` — The workspace ID to scope this request to.

</dd>
</dl>

<dl>
<dd>

**vm_id:** `str` — Source GPU VM ID for the snapshot.

</dd>
</dl>

<dl>
<dd>

**request:** `RecoveryRestoreRequest`

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

<details><summary><code>client.gpu_vms.<a href="src/ibee/gpu_vms/client.py">get_gpu_vm_snapshot</a>(...) -> SnapshotSet</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Returns one workspace-owned GPU VM snapshot set. Requires scope: vm.read.
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
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.gpu_vms.get_gpu_vm_snapshot(
    snapshot_set_id="snapshot_set_id",
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

**snapshot_set_id:** `str` — VM snapshot-set ID.

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

<details><summary><code>client.gpu_vms.<a href="src/ibee/gpu_vms/client.py">delete_gpu_vm_snapshot</a>(...) -> SnapshotDeleteResult</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Deletes a GPU VM snapshot set when no restore is running. Requires scope: vm.write.
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
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.gpu_vms.delete_gpu_vm_snapshot(
    snapshot_set_id="snapshot_set_id",
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

**snapshot_set_id:** `str` — VM snapshot-set ID.

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

<details><summary><code>client.gpu_vms.<a href="src/ibee/gpu_vms/client.py">get_gpu_vm_snapshot_restore</a>(...) -> RecoveryRestore</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Returns the current status of a GPU VM snapshot restore. Requires scope: vm.read.
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
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.gpu_vms.get_gpu_vm_snapshot_restore(
    restore_id="restore_id",
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

**restore_id:** `str` — Snapshot or backup restore operation ID.

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

<details><summary><code>client.gpu_vms.<a href="src/ibee/gpu_vms/client.py">get_gpu_vm_backup_policy</a>(...) -> BackupPolicy</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Returns the effective automated backup policy, including disabled state. Requires scope: vm.read.
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
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.gpu_vms.get_gpu_vm_backup_policy(
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

<details><summary><code>client.gpu_vms.<a href="src/ibee/gpu_vms/client.py">update_gpu_vm_backup_policy</a>(...) -> BackupPolicy</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Updates the automated backup schedule and retention settings. Requires scope: vm.write.
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
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.gpu_vms.update_gpu_vm_backup_policy(
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

**request:** `BackupPolicyUpdateRequest`

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

<details><summary><code>client.gpu_vms.<a href="src/ibee/gpu_vms/client.py">enable_gpu_vm_backups</a>(...) -> BackupPolicy</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Enables automated backups and creates the VM backup policy. Requires scope: vm.write.
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
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.gpu_vms.enable_gpu_vm_backups(
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

**request:** `BackupPolicyEnableRequest`

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

<details><summary><code>client.gpu_vms.<a href="src/ibee/gpu_vms/client.py">disable_gpu_vm_backups</a>(...) -> BackupPolicy</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Disables future automated backup runs without deleting existing recovery points. Requires scope: vm.write.
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
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.gpu_vms.disable_gpu_vm_backups(
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

**request:** `BackupPolicyDisableRequest`

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

<details><summary><code>client.gpu_vms.<a href="src/ibee/gpu_vms/client.py">reschedule_gpu_vm_backup</a>(...) -> BackupPolicy</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Sets the next automated backup execution time. Requires scope: vm.write.
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
from ibee import Ibee
from ibee.environment import IbeeEnvironment
import datetime

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.gpu_vms.reschedule_gpu_vm_backup(
    vm_id="vm_id",
    workspace_id="workspace_id",
    next_run_at=datetime.datetime.fromisoformat("2024-01-15T09:30:00+00:00"),
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

**request:** `BackupPolicyNextRunRequest`

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

<details><summary><code>client.gpu_vms.<a href="src/ibee/gpu_vms/client.py">list_gpu_vm_backup_runs</a>(...) -> BackupRunList</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Lists backup runs and usable recovery points for one GPU VM. Requires scope: vm.read.
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
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.gpu_vms.list_gpu_vm_backup_runs(
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

**limit:** `typing.Optional[int]` — Maximum number of records to return.

</dd>
</dl>

<dl>
<dd>

**offset:** `typing.Optional[int]`

</dd>
</dl>

<dl>
<dd>

**search:** `typing.Optional[str]`

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

<details><summary><code>client.gpu_vms.<a href="src/ibee/gpu_vms/client.py">create_gpu_vm_backup_run</a>(...) -> BackupRun</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Queues a manual backup using the VM's backup configuration. Requires scope: vm.write.
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
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.gpu_vms.create_gpu_vm_backup_run(
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

**request:** `ManualBackupRunRequest`

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

<details><summary><code>client.gpu_vms.<a href="src/ibee/gpu_vms/client.py">restore_gpu_vm_backup</a>(...) -> RecoveryRestore</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Restores a backup recovery point by replacing a VM, creating a new VM, or restoring one volume. Requires scope: vm.write.
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
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.gpu_vms.restore_gpu_vm_backup(
    vm_id="vm_id",
    workspace_id="workspace_id",
    recovery_point_id="recovery_point_id",
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

**request:** `BackupRestoreRequest`

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

<details><summary><code>client.gpu_vms.<a href="src/ibee/gpu_vms/client.py">get_gpu_vm_backup_run</a>(...) -> BackupRun</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Returns one workspace-owned GPU VM backup run or recovery point. Requires scope: vm.read.
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
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.gpu_vms.get_gpu_vm_backup_run(
    run_id="run_id",
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

**run_id:** `str` — Backup run or recovery-point ID.

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

<details><summary><code>client.gpu_vms.<a href="src/ibee/gpu_vms/client.py">get_gpu_vm_backup_restore</a>(...) -> RecoveryRestore</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Returns the current status of a GPU VM backup restore. Requires scope: vm.read.
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
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.gpu_vms.get_gpu_vm_backup_restore(
    restore_id="restore_id",
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

**restore_id:** `str` — Snapshot or backup restore operation ID.

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

## VmConsole
<details><summary><code>client.vm_console.<a href="src/ibee/vm_console/client.py">create_vm_console_session</a>(...) -> VmConsoleSession</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Creates a short-lived graphical console session for a cloud or GPU VM. The returned connect URL contains an expiring token; do not log or persist it. Requires scope: vm.write.
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
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.vm_console.create_vm_console_session(
    workspace_id="workspace_id",
    vm_id="vm_id",
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

**vm_id:** `str`

</dd>
</dl>

<dl>
<dd>

**vm_type:** `typing.Optional[VmType]`

</dd>
</dl>

<dl>
<dd>

**console_type:** `typing.Optional[VmConsoleSessionCreateRequestConsoleType]`

</dd>
</dl>

<dl>
<dd>

**requested_by:** `typing.Optional[str]`

</dd>
</dl>

<dl>
<dd>

**user_id:** `typing.Optional[str]`

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

<details><summary><code>client.vm_console.<a href="src/ibee/vm_console/client.py">get_vm_console_session</a>(...) -> VmConsoleSessionStatus</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Returns the status of a workspace-owned console session. Requires scope: vm.read.
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
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.vm_console.get_vm_console_session(
    session_id="session_id",
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

**session_id:** `str` — VM console session ID.

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

<details><summary><code>client.vm_console.<a href="src/ibee/vm_console/client.py">close_vm_console_session</a>(...) -> VmConsoleClose</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Closes a workspace-owned console session and invalidates its connection token. Requires scope: vm.write.
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
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.vm_console.close_vm_console_session(
    session_id="session_id",
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

**session_id:** `str` — VM console session ID.

</dd>
</dl>

<dl>
<dd>

**workspace_id:** `str` — The workspace ID to scope this request to.

</dd>
</dl>

<dl>
<dd>

**reason:** `typing.Optional[str]`

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

## Billing
<details><summary><code>client.billing.<a href="src/ibee/billing/client.py">check_resource_eligibility</a>(...) -> BillingEligibility</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Uses the same centralized billing admission flow as the IBEE portal. Call this endpoint immediately before a billable resource create and continue only when `allowed` is exactly `true`. Product create APIs do not accept or evaluate client-supplied billing state. This point-in-time check does not reserve funds. Requires scope: billing.read.
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
from ibee import Ibee
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.billing.check_resource_eligibility(
    workspace_id="workspace_id",
    sku_code="STANDARD-2-8-50",
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

**sku_code:** `typing.Optional[str]` — Billing catalog SKU for the intended resource. Use the SKU returned by the relevant public catalog; unknown SKUs are denied.

</dd>
</dl>

<dl>
<dd>

**estimated_cost_minor:** `typing.Optional[int]` — Optional cost in the organization's currency minor unit. Only send a value derived from a trusted server-side catalog.

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
