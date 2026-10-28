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
    workspace_id="710995",
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

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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
    workspace_id="710995",
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

**name:** `str` — Display name of the store (1-128 characters). Its URL-safe form becomes `store_key`.
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
</dd>
</dl>

<dl>
<dd>

**description:** `typing.Optional[str]` — Optional description.
    
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
    workspace_id="710995",
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

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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
    workspace_id="710995",
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

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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

<details><summary><code>client.secret_store.<a href="src/ibee/secret_store/client.py">unarchive_secret_store</a>(...) -> SecretStore</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Reactivates an archived secret store. Requires scope: secret-store.write.
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

client.secret_store.unarchive_secret_store(
    store_id="019f1e4b-3edd-72cf-b90e-26864ba2f283",
    workspace_id="710995",
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

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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

<details><summary><code>client.secret_store.<a href="src/ibee/secret_store/client.py">permanently_delete_secret_store</a>(...) -> SecretLifecycleStatus</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Irreversibly deletes a store and all store-scoped secrets, versions, identities, and policies. Requires scope: secret-store.write.
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

client.secret_store.permanently_delete_secret_store(
    store_id="019f1e4b-3edd-72cf-b90e-26864ba2f283",
    workspace_id="710995",
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

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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
    workspace_id="710995",
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

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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
    workspace_id="710995",
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

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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

<details><summary><code>client.secret_store.<a href="src/ibee/secret_store/client.py">batch_create_secrets</a>(...) -> BatchCreateSecretsResponse</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Creates up to 500 secrets without overwriting existing names. Requires scope: secret-store.write.
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
from ibee import Ibee, BatchCreateSecretItem
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.secret_store.batch_create_secrets(
    store_id="019f1e4b-3edd-72cf-b90e-26864ba2f283",
    workspace_id="710995",
    secrets=[
        BatchCreateSecretItem(
            secret_name="database-url",
            value={
                "url": "postgres://user:pass@host:5432/app"
            },
        ),
        BatchCreateSecretItem(
            secret_name="api-key",
            value={
                "key": "replace-with-your-value"
            },
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

**store_id:** `str` — Secret store ID.
    
</dd>
</dl>

<dl>
<dd>

**secrets:** `typing.List[BatchCreateSecretItem]` — Secrets to create (1-500).
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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
    workspace_id="710995",
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

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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
    workspace_id="710995",
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

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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
    workspace_id="710995",
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

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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
    workspace_id="710995",
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

**value:** `typing.Dict[str, typing.Any]` — Key-value pairs containing the new secret data. Creates a new version.
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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

<details><summary><code>client.secret_store.<a href="src/ibee/secret_store/client.py">undelete_secret</a>(...) -> Secret</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Restores specified soft-deleted versions and reactivates the secret. Requires scope: secret-store.write.
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

client.secret_store.undelete_secret(
    secret_id="019f1e4b-4a2c-71d0-a8b3-c5f92e7d1a4b",
    workspace_id="710995",
    versions=[
        2
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

**secret_id:** `str` — Secret ID.
    
</dd>
</dl>

<dl>
<dd>

**request:** `SecretVersionsRequest` 
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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

<details><summary><code>client.secret_store.<a href="src/ibee/secret_store/client.py">destroy_secret_versions</a>(...) -> SecretLifecycleStatus</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Irreversibly destroys specified secret versions. Requires scope: secret-store.write.
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

client.secret_store.destroy_secret_versions(
    secret_id="019f1e4b-4a2c-71d0-a8b3-c5f92e7d1a4b",
    workspace_id="710995",
    versions=[
        1
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

**secret_id:** `str` — Secret ID.
    
</dd>
</dl>

<dl>
<dd>

**request:** `SecretVersionsRequest` 
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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

<details><summary><code>client.secret_store.<a href="src/ibee/secret_store/client.py">permanently_delete_secret</a>(...) -> SecretLifecycleStatus</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Irreversibly deletes all versions and metadata for a secret. Requires scope: secret-store.write.
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

client.secret_store.permanently_delete_secret(
    secret_id="019f1e4b-4a2c-71d0-a8b3-c5f92e7d1a4b",
    workspace_id="710995",
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

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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

<details><summary><code>client.secret_store.<a href="src/ibee/secret_store/client.py">list_secret_versions</a>(...) -> SecretVersions</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Returns version metadata without secret values. Requires scope: secret-store.read.
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

client.secret_store.list_secret_versions(
    secret_id="019f1e4b-4a2c-71d0-a8b3-c5f92e7d1a4b",
    workspace_id="710995",
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

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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

<details><summary><code>client.secret_store.<a href="src/ibee/secret_store/client.py">get_secret_version</a>(...) -> SecretVersion</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Returns the value and metadata for one secret version. Requires scope: secret-store.read.
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

client.secret_store.get_secret_version(
    secret_id="019f1e4b-4a2c-71d0-a8b3-c5f92e7d1a4b",
    version=1,
    workspace_id="710995",
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

**version:** `int` — Positive secret version number.
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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

<details><summary><code>client.secret_store.<a href="src/ibee/secret_store/client.py">rollback_secret</a>(...) -> SecretValue</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Copies a previous version into a new current version. Requires scope: secret-store.write.
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

client.secret_store.rollback_secret(
    secret_id="019f1e4b-4a2c-71d0-a8b3-c5f92e7d1a4b",
    workspace_id="710995",
    version=1,
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

**version:** `int` — Previous version to copy into a new current version.
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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

<details><summary><code>client.secret_store.<a href="src/ibee/secret_store/client.py">list_secret_identities</a>(...) -> SecretIdentityList</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Lists AppRole and Kubernetes identities bound to a store. Requires scope: secret-store.read.
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

client.secret_store.list_secret_identities(
    store_id="019f1e4b-3edd-72cf-b90e-26864ba2f283",
    workspace_id="710995",
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

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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

<details><summary><code>client.secret_store.<a href="src/ibee/secret_store/client.py">create_secret_identity</a>(...) -> SecretIdentity</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Creates an AppRole or Kubernetes identity with an initial scope for this store. Requires scope: secret-store.write.
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

client.secret_store.create_secret_identity(
    store_id="019f1e4b-3edd-72cf-b90e-26864ba2f283",
    workspace_id="710995",
    auth_method="approle",
    name="payments-api",
    token_policy_mode="read_only",
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

**auth_method:** `CreateSecretIdentityRequestAuthMethod` — Authentication method used by the application.
    
</dd>
</dl>

<dl>
<dd>

**name:** `str` — Display name of the identity (1-128 characters).
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
</dd>
</dl>

<dl>
<dd>

**token_policy_mode:** `typing.Optional[CreateSecretIdentityRequestTokenPolicyMode]` 

Default access mode for the identity's tokens.
- `read_only` (default)
- `read_write`
    
</dd>
</dl>

<dl>
<dd>

**k8s_namespace:** `typing.Optional[str]` — Required when auth_method is kubernetes.
    
</dd>
</dl>

<dl>
<dd>

**k8s_service_account:** `typing.Optional[str]` — Required when auth_method is kubernetes.
    
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

<details><summary><code>client.secret_store.<a href="src/ibee/secret_store/client.py">get_secret_identity</a>(...) -> SecretIdentity</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Gets one application identity without credentials. Requires scope: secret-store.read.
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

client.secret_store.get_secret_identity(
    identity_id="identity_id",
    workspace_id="710995",
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

**identity_id:** `str` — Secret Store application identity ID.
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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

<details><summary><code>client.secret_store.<a href="src/ibee/secret_store/client.py">delete_secret_identity</a>(...) -> SecretIdentityActionStatus</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Permanently removes the identity, its scopes, role, policy, and sessions. Requires scope: secret-store.write.
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

client.secret_store.delete_secret_identity(
    identity_id="identity_id",
    workspace_id="710995",
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

**identity_id:** `str` — Secret Store application identity ID.
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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

<details><summary><code>client.secret_store.<a href="src/ibee/secret_store/client.py">disable_secret_identity</a>(...) -> SecretIdentity</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Disables an identity and revokes its active sessions. Requires scope: secret-store.write.
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

client.secret_store.disable_secret_identity(
    identity_id="identity_id",
    workspace_id="710995",
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

**identity_id:** `str` — Secret Store application identity ID.
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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

<details><summary><code>client.secret_store.<a href="src/ibee/secret_store/client.py">enable_secret_identity</a>(...) -> SecretIdentity</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Re-enables a disabled identity. Requires scope: secret-store.write.
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

client.secret_store.enable_secret_identity(
    identity_id="identity_id",
    workspace_id="710995",
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

**identity_id:** `str` — Secret Store application identity ID.
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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

<details><summary><code>client.secret_store.<a href="src/ibee/secret_store/client.py">get_secret_identity_access</a>(...) -> SecretIdentityAccess</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Returns Kubernetes binding details or generates fresh AppRole credentials. Treat secret_id as sensitive. Each call for an AppRole identity mints a new credential, so the gateway treats this GET as a write. Requires scope: secret-store.write.
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

client.secret_store.get_secret_identity_access(
    identity_id="identity_id",
    workspace_id="710995",
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

**identity_id:** `str` — Secret Store application identity ID.
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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

<details><summary><code>client.secret_store.<a href="src/ibee/secret_store/client.py">rotate_secret_identity_secret_id</a>(...) -> SecretIdentityAccess</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Generates fresh AppRole credentials. Available only for AppRole identities. Requires scope: secret-store.write.
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

client.secret_store.rotate_secret_identity_secret_id(
    identity_id="identity_id",
    workspace_id="710995",
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

**identity_id:** `str` — Secret Store application identity ID.
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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

<details><summary><code>client.secret_store.<a href="src/ibee/secret_store/client.py">revoke_secret_identity_sessions</a>(...) -> SecretIdentityActionStatus</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Revokes active sessions without deleting or disabling the identity. Requires scope: secret-store.write.
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

client.secret_store.revoke_secret_identity_sessions(
    identity_id="identity_id",
    workspace_id="710995",
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

**identity_id:** `str` — Secret Store application identity ID.
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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

<details><summary><code>client.secret_store.<a href="src/ibee/secret_store/client.py">list_secret_identity_scopes</a>(...) -> SecretIdentityScopeList</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Lists the stores and permissions available to an identity. Requires scope: secret-store.read.
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

client.secret_store.list_secret_identity_scopes(
    identity_id="identity_id",
    workspace_id="710995",
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

**identity_id:** `str` — Secret Store application identity ID.
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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

<details><summary><code>client.secret_store.<a href="src/ibee/secret_store/client.py">create_secret_identity_scope</a>(...) -> SecretIdentityScope</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Grants an identity access to another store. Requires scope: secret-store.write.
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

client.secret_store.create_secret_identity_scope(
    identity_id="identity_id",
    workspace_id="710995",
    store_id="019f1e4b-3edd-72cf-b90e-26864ba2f283",
    access_mode="read_only",
    allow_version_read=True,
    allow_rollback=False,
    allow_destroy=False,
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

**identity_id:** `str` — Secret Store application identity ID.
    
</dd>
</dl>

<dl>
<dd>

**store_id:** `str` — Store the identity gets access to.
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
</dd>
</dl>

<dl>
<dd>

**access_mode:** `typing.Optional[CreateSecretIdentityScopeRequestAccessMode]` 

- `read_only`: the identity can read secrets in the store.
- `read_write`: the identity can also create and update them.
Default `read_only`.
    
</dd>
</dl>

<dl>
<dd>

**allow_version_read:** `typing.Optional[bool]` — Whether the identity may read non-current versions of a secret.
    
</dd>
</dl>

<dl>
<dd>

**allow_rollback:** `typing.Optional[bool]` — Whether the identity may roll a secret back to an earlier version.
    
</dd>
</dl>

<dl>
<dd>

**allow_destroy:** `typing.Optional[bool]` — Whether the identity may destroy secret versions.
    
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

<details><summary><code>client.secret_store.<a href="src/ibee/secret_store/client.py">delete_secret_identity_scope</a>(...) -> SecretIdentityActionStatus</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Removes a store permission from an identity. Requires scope: secret-store.write.
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

client.secret_store.delete_secret_identity_scope(
    scope_id="scope_id",
    workspace_id="710995",
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

**scope_id:** `str` — Secret Store identity scope ID.
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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
    workspace_id="710995",
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

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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
    workspace_id="710995",
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

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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
    workspace_id="710995",
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

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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
    workspace_id="710995",
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

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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
    workspace_id="710995",
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

**is_public:** `bool` — Whether the bucket allows unauthenticated read access.
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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

<details><summary><code>client.object_storage.<a href="src/ibee/object_storage/client.py">get_bucket_lifecycle</a>(...) -> BucketLifecycleConfiguration</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Returns the bucket's lifecycle rules, as the portal's Settings › Lifecycle tab shows them. Requires scope: object-storage.read.
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

client.object_storage.get_bucket_lifecycle(
    bucket_name="bucket_name",
    workspace_id="710995",
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

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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

<details><summary><code>client.object_storage.<a href="src/ibee/object_storage/client.py">set_bucket_lifecycle</a>(...) -> DeleteResponse</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Replaces every lifecycle rule of the bucket. Each rule expires objects after a number of days or on a date, optionally only under a prefix. Requires scope: object-storage.write.
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
from ibee import Ibee, BucketLifecycleRule
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.object_storage.set_bucket_lifecycle(
    bucket_name="bucket_name",
    workspace_id="710995",
    rules=[
        BucketLifecycleRule(
            status="Enabled",
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

**bucket_name:** `str` — Logical bucket name.
    
</dd>
</dl>

<dl>
<dd>

**request:** `BucketLifecycleConfiguration` 
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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

<details><summary><code>client.object_storage.<a href="src/ibee/object_storage/client.py">delete_bucket_lifecycle</a>(...) -> DeleteResponse</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Removes every lifecycle rule from the bucket. Requires scope: object-storage.write.
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

client.object_storage.delete_bucket_lifecycle(
    bucket_name="bucket_name",
    workspace_id="710995",
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

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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

<details><summary><code>client.object_storage.<a href="src/ibee/object_storage/client.py">get_bucket_cors</a>(...) -> BucketCorsConfiguration</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Returns the bucket's CORS rules, as the portal's Settings › CORS tab shows them. Requires scope: object-storage.read.
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

client.object_storage.get_bucket_cors(
    bucket_name="bucket_name",
    workspace_id="710995",
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

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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

<details><summary><code>client.object_storage.<a href="src/ibee/object_storage/client.py">set_bucket_cors</a>(...) -> DeleteResponse</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Replaces every CORS rule of the bucket. Requires scope: object-storage.write.
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
from ibee import Ibee, BucketCorsRule
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.object_storage.set_bucket_cors(
    bucket_name="bucket_name",
    workspace_id="710995",
    rules=[
        BucketCorsRule(
            allowed_origins=[
                "allowed_origins"
            ],
            allowed_methods=[
                "GET"
            ],
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

**bucket_name:** `str` — Logical bucket name.
    
</dd>
</dl>

<dl>
<dd>

**request:** `BucketCorsConfiguration` 
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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

<details><summary><code>client.object_storage.<a href="src/ibee/object_storage/client.py">delete_bucket_cors</a>(...) -> DeleteResponse</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Removes every CORS rule from the bucket. Requires scope: object-storage.write.
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

client.object_storage.delete_bucket_cors(
    bucket_name="bucket_name",
    workspace_id="710995",
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

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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

<details><summary><code>client.object_storage.<a href="src/ibee/object_storage/client.py">get_bucket_object_lock</a>(...) -> BucketObjectLockConfiguration</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Returns the default retention of a bucket created with object lock, as the portal's Settings › Lock tab shows it. Answers 404 when the bucket has no object lock. Requires scope: object-storage.read.
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

client.object_storage.get_bucket_object_lock(
    bucket_name="bucket_name",
    workspace_id="710995",
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

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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

<details><summary><code>client.object_storage.<a href="src/ibee/object_storage/client.py">set_bucket_object_lock</a>(...) -> DeleteResponse</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Changes the default retention applied to new objects in a bucket that has object lock. Send `rule: null` to remove the default. Requires scope: object-storage.write.
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

client.object_storage.set_bucket_object_lock(
    bucket_name="bucket_name",
    workspace_id="710995",
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

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
</dd>
</dl>

<dl>
<dd>

**rule:** `typing.Optional[DefaultRetention]` — New default retention, or null to remove it.
    
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

<details><summary><code>client.object_storage.<a href="src/ibee/object_storage/client.py">get_bucket_notifications</a>(...) -> BucketNotificationConfiguration</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Returns the webhook notification rules of the bucket, as the portal's Settings › Event notifications tab shows them. Requires scope: object-storage.read.
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

client.object_storage.get_bucket_notifications(
    bucket_name="bucket_name",
    workspace_id="710995",
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

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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

<details><summary><code>client.object_storage.<a href="src/ibee/object_storage/client.py">set_bucket_notifications</a>(...) -> DeleteResponse</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Replaces every notification rule of the bucket. Each rule posts `upload` or `delete` events, optionally filtered by prefix or suffix, to a webhook URL. Requires scope: object-storage.write.
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
from ibee import Ibee, BucketNotificationConfig
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.object_storage.set_bucket_notifications(
    bucket_name="bucket_name",
    workspace_id="710995",
    configs=[
        BucketNotificationConfig(
            events=[
                "upload"
            ],
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

**bucket_name:** `str` — Logical bucket name.
    
</dd>
</dl>

<dl>
<dd>

**request:** `BucketNotificationConfiguration` 
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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

<details><summary><code>client.object_storage.<a href="src/ibee/object_storage/client.py">delete_bucket_notifications</a>(...) -> DeleteResponse</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Removes every notification rule from the bucket. Requires scope: object-storage.write.
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

client.object_storage.delete_bucket_notifications(
    bucket_name="bucket_name",
    workspace_id="710995",
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

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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

<details><summary><code>client.object_storage.<a href="src/ibee/object_storage/client.py">get_bucket_custom_domains</a>(...) -> BucketCustomDomainConfig</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Returns the bucket's custom domains with their status and the CNAME target to point them at, as the portal's Settings › Custom domains tab shows. Requires scope: object-storage.read.
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

client.object_storage.get_bucket_custom_domains(
    bucket_name="bucket_name",
    workspace_id="710995",
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

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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

<details><summary><code>client.object_storage.<a href="src/ibee/object_storage/client.py">add_bucket_custom_domain</a>(...) -> BucketCustomDomain</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Adds a custom hostname that serves the bucket. Create the CNAME record shown in `cname_target`, then check `status` on the list. Requires scope: object-storage.write.
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

client.object_storage.add_bucket_custom_domain(
    bucket_name="bucket_name",
    workspace_id="710995",
    domain="domain",
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

**domain:** `str` — Hostname to serve the bucket from, for example `assets.example.com`.
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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

<details><summary><code>client.object_storage.<a href="src/ibee/object_storage/client.py">remove_bucket_custom_domain</a>(...) -> BucketCustomDomainRemoved</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Removes a custom hostname from the bucket. Requires scope: object-storage.write.
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

client.object_storage.remove_bucket_custom_domain(
    bucket_name="bucket_name",
    domain="domain",
    workspace_id="710995",
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

**domain:** `str` — Hostname to remove.
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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

<details><summary><code>client.object_storage.<a href="src/ibee/object_storage/client.py">get_bucket_metrics</a>(...) -> BucketMetrics</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Returns request and storage metrics of the bucket for the last 24 hours or 7 days, as the portal's Metrics tab shows them. Requires scope: object-storage.read.
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

client.object_storage.get_bucket_metrics(
    bucket_name="bucket_name",
    workspace_id="710995",
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

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
</dd>
</dl>

<dl>
<dd>

**range:** `typing.Optional[GetBucketMetricsRequestRange]` — Time range. Default `24h`.
    
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
    workspace_id="710995",
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

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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
    workspace_id="710995",
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

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
</dd>
</dl>

<dl>
<dd>

**name:** `typing.Optional[str]` — Display name of the key pair. Default `Default Key`.
    
</dd>
</dl>

<dl>
<dd>

**permission_type:** `typing.Optional[str]` — Permission level: `admin_rw`, `admin_ro`, `object_rw` or `object_ro`. Default `admin_rw`.
    
</dd>
</dl>

<dl>
<dd>

**bucket_scope:** `typing.Optional[CreateS3CredentialRequestBucketScope]` 

- `all`: the key may use every bucket in the workspace (default).
- `specific`: only the buckets in `allowed_buckets`.
    
</dd>
</dl>

<dl>
<dd>

**allowed_buckets:** `typing.Optional[typing.List[str]]` — Bucket names the key may use when `bucket_scope` is `specific`.
    
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
    workspace_id="710995",
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

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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

<details><summary><code>client.object_storage.<a href="src/ibee/object_storage/client.py">delete_s3credential</a>(...) -> S3CredentialRevoked</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Deletes a credential record permanently. Revoke it first with POST /object-storage/credentials/{access_key_id}/revoke; the portal deletes revoked credentials only. Requires scope: object-storage.write.
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

client.object_storage.delete_s3credential(
    access_key_id="access_key_id",
    workspace_id="710995",
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

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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

Revokes a credential so it can no longer authenticate S3 requests. The record stays listed as revoked, as in the portal; delete it afterwards with DELETE /object-storage/credentials/{access_key_id}. Requires scope: object-storage.write.
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
    workspace_id="710995",
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

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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
    workspace_id="710995",
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

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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
    workspace_id="710995",
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

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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
    workspace_id="710995",
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

**name:** `str` — Display name of the VPC.
    
</dd>
</dl>

<dl>
<dd>

**site_id:** `str` — Required network placement site. Copy `site_id` from `GET /networking/sites` and choose an entry where `available` is `true`. Do not use a region name.
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
</dd>
</dl>

<dl>
<dd>

**description:** `typing.Optional[str]` — Optional description.
    
</dd>
</dl>

<dl>
<dd>

**region:** `typing.Optional[str]` — Optional region label stored with the VPC.
    
</dd>
</dl>

<dl>
<dd>

**cidr:** `typing.Optional[str]` — RFC1918 IPv4 CIDR with a prefix between /22 and /28.
    
</dd>
</dl>

<dl>
<dd>

**auto_cidr:** `typing.Optional[bool]` — Let the service choose a free CIDR when `cidr` is omitted. Default true.
    
</dd>
</dl>

<dl>
<dd>

**create_default_subnet:** `typing.Optional[bool]` — Create a first subnet together with the VPC. Default true.
    
</dd>
</dl>

<dl>
<dd>

**default_subnet_cidr:** `typing.Optional[str]` — CIDR for that first subnet; chosen automatically when omitted.
    
</dd>
</dl>

<dl>
<dd>

**is_default:** `typing.Optional[bool]` — Mark the VPC as the workspace's default VPC. Default false.
    
</dd>
</dl>

<dl>
<dd>

**connectivity_type:** `typing.Optional[CreateVpcRequestConnectivityType]` — The VPC's internet model; the server uses `public` when this is omitted. `public` keeps dedicated public IPs available to its VMs. `private` has no shared public edge, but a VM can still be given a Reserved IP. `nat_gateway` is a private VPC with managed outbound NAT and refuses dedicated public IPs.
    
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
    workspace_id="710995",
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

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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
    workspace_id="710995",
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

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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
    workspace_id="710995",
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

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
</dd>
</dl>

<dl>
<dd>

**name:** `typing.Optional[str]` — New display name.
    
</dd>
</dl>

<dl>
<dd>

**description:** `typing.Optional[str]` — New description.
    
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
    workspace_id="710995",
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

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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
    workspace_id="710995",
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

**name:** `str` — Display name of the subnet.
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
</dd>
</dl>

<dl>
<dd>

**cidr:** `typing.Optional[str]` — IPv4 CIDR inside the VPC range. Chosen automatically when omitted and `auto_cidr` is true.
    
</dd>
</dl>

<dl>
<dd>

**auto_cidr:** `typing.Optional[bool]` — Let the service choose a free CIDR when `cidr` is omitted. Default true.
    
</dd>
</dl>

<dl>
<dd>

**prefix_length:** `typing.Optional[int]` — Prefix length to use for an automatically chosen CIDR.
    
</dd>
</dl>

<dl>
<dd>

**dns:** `typing.Optional[typing.List[str]]` — DNS resolvers handed to instances in the subnet. Default `1.1.1.1` and `8.8.8.8`.
    
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

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Returns one subnet in a VPC, including its CIDR range, gateway, and DNS settings. Requires scope: network.read.
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

client.vpcs.get_vpc_subnet(
    vpc_id="vpc_id",
    subnet_id="subnet_id",
    workspace_id="710995",
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

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Deletes a subnet from a VPC. Requires scope: network.write.
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

client.vpcs.delete_vpc_subnet(
    vpc_id="vpc_id",
    subnet_id="subnet_id",
    workspace_id="710995",
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

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Lists the VMs attached to a VPC. Requires scope: network.read.
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

client.vpcs.list_vpc_nodes(
    vpc_id="vpc_id",
    workspace_id="710995",
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

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Attaches a VM to a VPC subnet so it can reach other VMs on the private network, optionally with a reserved public IP. Requires scope: network.write.
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

client.vpcs.attach_vpc_node(
    vpc_id="vpc_id",
    workspace_id="710995",
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

**vm_id:** `str` — ID of the VM to attach.
    
</dd>
</dl>

<dl>
<dd>

**subnet_id:** `str` — Subnet of the VPC to attach the VM to.
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
</dd>
</dl>

<dl>
<dd>

**connectivity:** `typing.Optional[AttachVpcNodeRequestConnectivity]` 

How the VM reaches the internet from this subnet.
- `private`: no internet path.
- `public_ip`: a Reserved IP is attached to the allocation.
- `nat`: outbound traffic goes through the VPC's NAT gateway.

Default `private`.
    
</dd>
</dl>

<dl>
<dd>

**requested_private_ip:** `typing.Optional[str]` — Private IPv4 address to give the VM in the subnet. Chosen automatically when omitted.
    
</dd>
</dl>

<dl>
<dd>

**reserved_public_ip_id:** `typing.Optional[str]` — Reserved IP to attach to the VM. Only valid with `public_ip` connectivity.
    
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

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Detaches a VM from a VPC. Requires scope: network.write.
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

client.vpcs.detach_vpc_node(
    vpc_id="vpc_id",
    vm_id="vm_id",
    workspace_id="710995",
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

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Lists the managed NAT gateways in a VPC. Requires scope: network.read.
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

client.vpcs.list_nat_gateways(
    vpc_id="vpc_id",
    workspace_id="710995",
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

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Creates a managed NAT gateway that gives VMs in a VPC outbound internet access without public IPs of their own. Requires scope: network.write.
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

client.vpcs.create_nat_gateway(
    vpc_id="vpc_id",
    workspace_id="710995",
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

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
</dd>
</dl>

<dl>
<dd>

**subnet_id:** `typing.Optional[str]` — Subnet the gateway is placed in; chosen by the service when omitted.
    
</dd>
</dl>

<dl>
<dd>

**reserved_public_ip_id:** `typing.Optional[str]` — Reserved IP to use as the gateway's public address; a platform-assigned address is used when omitted.
    
</dd>
</dl>

<dl>
<dd>

**name:** `typing.Optional[str]` — Display name of the gateway. Default `NAT Gateway`.
    
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

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Deletes a NAT gateway from a VPC. VMs that relied on it lose outbound internet access. Requires scope: network.write.
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

client.vpcs.delete_nat_gateway(
    vpc_id="vpc_id",
    nat_gateway_id="nat_gateway_id",
    workspace_id="710995",
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

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
</dd>
</dl>

<dl>
<dd>

**public_ip_action:** `typing.Optional[NatGatewayDeleteRequestPublicIpAction]` 

What to do with the gateway's public IP.
- `release`: give the address back.
- `reserve`: keep it as a Reserved IP in the workspace.
Omitted: platform-assigned addresses are released; customer Reserved IPs are detached and kept.
    
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

<details><summary><code>client.vpcs.<a href="src/ibee/vpcs/client.py">update_nat_gateway_public_ip</a>(...) -> NatGateway</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Replaces the NAT gateway's public IP with a Reserved IP, keeping the port-forwarding rules, as the portal's NAT card does. Requires scope: network.write.
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

client.vpcs.update_nat_gateway_public_ip(
    vpc_id="vpc_id",
    nat_gateway_id="nat_gateway_id",
    workspace_id="710995",
    reserved_public_ip_id="reserved_public_ip_id",
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

**reserved_public_ip_id:** `str` — Reserved IP to put on the gateway. Port-forwarding rules are preserved.
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Lists the port-forwarding rules on a NAT gateway. Requires scope: network.read.
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

client.vpcs.list_nat_port_forwarding_rules(
    vpc_id="vpc_id",
    nat_gateway_id="nat_gateway_id",
    workspace_id="710995",
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

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Adds a port-forwarding rule that sends traffic arriving on a NAT gateway port to a private IP and port inside the VPC. Requires scope: network.write.
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

client.vpcs.create_nat_port_forwarding_rule(
    vpc_id="vpc_id",
    nat_gateway_id="nat_gateway_id",
    workspace_id="710995",
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

**request:** `CreateNatPortForwardingRuleRequest` 
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Removes a port-forwarding rule from a NAT gateway. Requires scope: network.write.
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

client.vpcs.delete_nat_port_forwarding_rule(
    vpc_id="vpc_id",
    nat_gateway_id="nat_gateway_id",
    port_forwarding_rule_id="port_forwarding_rule_id",
    workspace_id="710995",
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

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Changes a NAT port-forwarding rule's ports, target, protocol, or enabled state. Requires scope: network.write.
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

client.vpcs.update_nat_port_forwarding_rule(
    vpc_id="vpc_id",
    nat_gateway_id="nat_gateway_id",
    port_forwarding_rule_id="port_forwarding_rule_id",
    workspace_id="710995",
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

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
</dd>
</dl>

<dl>
<dd>

**name:** `typing.Optional[str]` — Display name of the rule.
    
</dd>
</dl>

<dl>
<dd>

**protocol:** `typing.Optional[UpdateNatPortForwardingRuleRequestProtocol]` 

- `tcp`
- `udp`
    
</dd>
</dl>

<dl>
<dd>

**external_port:** `typing.Optional[int]` — Port on the gateway's public address (1-65535).
    
</dd>
</dl>

<dl>
<dd>

**internal_ip:** `typing.Optional[str]` — Private IPv4 address of the VM inside the VPC that receives the traffic.
    
</dd>
</dl>

<dl>
<dd>

**internal_port:** `typing.Optional[int]` — Port on the VM that receives the traffic (1-65535).
    
</dd>
</dl>

<dl>
<dd>

**target_type:** `typing.Optional[UpdateNatPortForwardingRuleRequestTargetType]` — `vm`: forward to one VM's private IP. `vip`: forward to a Virtual IP announced by the VMs in `target_vm_ids`.
    
</dd>
</dl>

<dl>
<dd>

**target_vm_ids:** `typing.Optional[typing.List[str]]` — VMs that announce the Virtual IP. Required with `vip`, must be empty with `vm`.
    
</dd>
</dl>

<dl>
<dd>

**note:** `typing.Optional[str]` — Free-text note stored with the rule.
    
</dd>
</dl>

<dl>
<dd>

**enabled:** `typing.Optional[bool]` — Whether the rule is applied.
    
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
    workspace_id="710995",
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

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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
    workspace_id="710995",
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

**site_id:** `str` — Site whose public IP pool allocates the address. Copy an available `site_id` from `GET /networking/sites`; use the target VM or VPC's site when the address will be attached.
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
</dd>
</dl>

<dl>
<dd>

**label:** `typing.Optional[str]` — Optional label for the address (up to 120 characters), shown as its name in the portal.
    
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

<details><summary><code>client.reserved_ips.<a href="src/ibee/reserved_ips/client.py">convert_reserved_ip</a>(...) -> ReservedIp</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Turns the automatically assigned public IPv4 of a VM into a Reserved IP that survives the VM, as the portal's Convert Existing IP does. The address stays on the VM. Billing for the Reserved IP starts now. Requires scope: network.write.
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

client.reserved_ips.convert_reserved_ip(
    workspace_id="710995",
    vm_id="vm_id",
    site_id="site_id",
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

**vm_id:** `str` — VM whose current public IPv4 becomes a Reserved IP.
    
</dd>
</dl>

<dl>
<dd>

**site_id:** `str` — The VM's site, from `GET /networking/sites`.
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
</dd>
</dl>

<dl>
<dd>

**label:** `typing.Optional[str]` — Optional label for the Reserved IP.
    
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

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Returns a reserved public IPv4 address, including its label, reverse DNS, and the VM it is attached to. Requires scope: network.read.
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

client.reserved_ips.get_reserved_ip(
    reserved_ip_id="reserved_ip_id",
    workspace_id="710995",
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

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Releases a reserved public IPv4 address from your workspace. Requires scope: network.write.
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

client.reserved_ips.release_reserved_ip(
    reserved_ip_id="reserved_ip_id",
    workspace_id="710995",
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

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Changes a reserved IP's label or reverse DNS (PTR) record. Requires scope: network.write.
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

client.reserved_ips.update_reserved_ip(
    reserved_ip_id="reserved_ip_id",
    workspace_id="710995",
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

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
</dd>
</dl>

<dl>
<dd>

**label:** `typing.Optional[str]` — New label (the portal's **Name**).
    
</dd>
</dl>

<dl>
<dd>

**reverse_dns:** `typing.Optional[str]` — Reverse DNS hostname for the address, as a fully qualified domain name.
    
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

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Attaches a reserved public IP to a VM, optionally through a VPC subnet. Requires scope: network.write.
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

client.reserved_ips.attach_reserved_ip(
    reserved_ip_id="reserved_ip_id",
    workspace_id="710995",
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

**request:** `AttachReservedIpRequest` 
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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

<details><summary><code>client.reserved_ips.<a href="src/ibee/reserved_ips/client.py">attach_reserved_ip_direct</a>(...) -> ReservedIp</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Attaches the Reserved IP to the VM's direct public interface, for VMs that are not in a VPC. Use `attach` for VMs with a VPC interface. Requires scope: network.write.
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

client.reserved_ips.attach_reserved_ip_direct(
    reserved_ip_id="reserved_ip_id",
    workspace_id="710995",
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

**vm_id:** `str` — VM to attach the address to, on its direct public interface.
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
</dd>
</dl>

<dl>
<dd>

**network_id:** `typing.Optional[str]` — Provider network of the VM. Resolved automatically when the VM has one.
    
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

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Detaches a reserved public IP from its VM. The address stays reserved in your workspace. Requires scope: network.write.
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

client.reserved_ips.detach_reserved_ip(
    reserved_ip_id="reserved_ip_id",
    workspace_id="710995",
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

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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
    workspace_id="710995",
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

**request:** `AttachReservedIpRequest` 
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Lists one page of the firewall groups in a workspace: 10 by default, at most 100 per page. Use `limit` and `offset` to page through the rest. Requires scope: firewall.read.
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

client.firewalls.list_firewall_groups(
    workspace_id="710995",
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

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
</dd>
</dl>

<dl>
<dd>

**limit:** `typing.Optional[int]` — Maximum number of records to return. The server returns 10 when this is omitted; use `offset` to read further pages.
    
</dd>
</dl>

<dl>
<dd>

**offset:** `typing.Optional[int]` — Number of records to skip before the first one returned.
    
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

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Creates a firewall group, a reusable set of inbound and outbound rules you can apply to VMs. Requires scope: firewall.write.
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

client.firewalls.create_firewall_group(
    workspace_id="710995",
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

**name:** `str` — Display name of the group.
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
</dd>
</dl>

<dl>
<dd>

**description:** `typing.Optional[str]` — Optional description.
    
</dd>
</dl>

<dl>
<dd>

**is_default:** `typing.Optional[bool]` — Mark the group as the workspace's default group. Default false.
    
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

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Returns a firewall group with its rules. Requires scope: firewall.read.
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

client.firewalls.get_firewall_group(
    firewall_group_id="firewall_group_id",
    workspace_id="710995",
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

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Deletes a firewall group. Requires scope: firewall.write.
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

client.firewalls.delete_firewall_group(
    firewall_group_id="firewall_group_id",
    workspace_id="710995",
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

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Adds a rule to a firewall group, with its direction, protocol, port range, remote targets, action, and priority. Requires scope: firewall.write.
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

client.firewalls.create_firewall_rule(
    firewall_group_id="firewall_group_id",
    workspace_id="710995",
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

**request:** `CreateFirewallRuleRequest` 
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Removes a rule from a firewall group. Requires scope: firewall.write.
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

client.firewalls.delete_firewall_rule(
    firewall_group_id="firewall_group_id",
    firewall_rule_id="firewall_rule_id",
    workspace_id="710995",
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

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Changes an existing rule in a firewall group. Requires scope: firewall.write.
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

client.firewalls.update_firewall_rule(
    firewall_group_id="firewall_group_id",
    firewall_rule_id="firewall_rule_id",
    workspace_id="710995",
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

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
</dd>
</dl>

<dl>
<dd>

**description:** `typing.Optional[str]` — Optional description of the rule.
    
</dd>
</dl>

<dl>
<dd>

**direction:** `typing.Optional[FirewallRuleFieldsDirection]` 

- `ingress`: traffic into the VM (default).
- `egress`: traffic out of the VM.
    
</dd>
</dl>

<dl>
<dd>

**protocol:** `typing.Optional[FirewallRuleFieldsProtocol]` 

- `tcp` (default)
- `udp`
- `icmp`
- `any`: all protocols.
    
</dd>
</dl>

<dl>
<dd>

**port_start:** `typing.Optional[int]` — First port of the range (1-65535). Required for `tcp` and `udp`; ignored for other protocols.
    
</dd>
</dl>

<dl>
<dd>

**port_end:** `typing.Optional[int]` — Last port of the range (1-65535). Defaults to `port_start`.
    
</dd>
</dl>

<dl>
<dd>

**remote_targets:** `typing.Optional[typing.List[str]]` — Remote IPv4 addresses or CIDRs the rule matches, for example `0.0.0.0/0`.
    
</dd>
</dl>

<dl>
<dd>

**action:** `typing.Optional[FirewallRuleFieldsAction]` 

- `allow`: let matching traffic through (default).
- `drop`: discard matching traffic.
    
</dd>
</dl>

<dl>
<dd>

**priority:** `typing.Optional[int]` — Evaluation priority of the rule.
    
</dd>
</dl>

<dl>
<dd>

**enabled:** `typing.Optional[bool]` — Whether the rule is applied.
    
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

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Lists the VMs a firewall group is applied to. Requires scope: firewall.read.
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

client.firewalls.list_firewall_group_attachments(
    firewall_group_id="firewall_group_id",
    workspace_id="710995",
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

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
</dd>
</dl>

<dl>
<dd>

**limit:** `typing.Optional[int]` — Maximum number of records to return.
    
</dd>
</dl>

<dl>
<dd>

**skip:** `typing.Optional[int]` — Number of items to skip before the first returned item. Default 0.
    
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

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Applies a firewall group's rules to a VM. Requires scope: firewall.write.
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

client.firewalls.attach_firewall_group(
    firewall_group_id="firewall_group_id",
    workspace_id="710995",
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

**vm_id:** `str` — ID of the VM.
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Removes a firewall group from a VM. Its rules no longer apply to that VM. Requires scope: firewall.write.
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

client.firewalls.detach_firewall_group(
    firewall_group_id="firewall_group_id",
    vm_id="vm_id",
    workspace_id="710995",
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

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Lists the L4 and L7 load balancers in a workspace. Requires scope: load-balancer.read.
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

client.load_balancers.list_load_balancers(
    workspace_id="710995",
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

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
</dd>
</dl>

<dl>
<dd>

**status:** `typing.Optional[LoadBalancerStatus]` — Return only load balancers in this status.
    
</dd>
</dl>

<dl>
<dd>

**layer:** `typing.Optional[ListLoadBalancersRequestLayer]` 

Return only load balancers of this layer.
- `l4`
- `l7`
    
</dd>
</dl>

<dl>
<dd>

**protocol:** `typing.Optional[LoadBalancerProtocol]` — Return only load balancers that accept this protocol.
    
</dd>
</dl>

<dl>
<dd>

**limit:** `typing.Optional[int]` — Maximum number of items to return (1-500). Default 100.
    
</dd>
</dl>

<dl>
<dd>

**skip:** `typing.Optional[int]` — Number of items to skip before the first returned item. Default 0.
    
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

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Creates a layer 4 (TCP/UDP) load balancer that spreads connections across backend VMs, with optional TLS. Requires scope: load-balancer.write.
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
from ibee import Ibee, LoadBalancerBackend
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.load_balancers.create_l4load_balancer(
    workspace_id="710995",
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

**name:** `str` — Display name of the load balancer.
    
</dd>
</dl>

<dl>
<dd>

**protocol:** `CreateL4LoadBalancerRequestProtocol` 

- `tcp`
- `tls_passthrough`
    
</dd>
</dl>

<dl>
<dd>

**backends:** `typing.List[LoadBalancerBackend]` — Backends to send traffic to.
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
</dd>
</dl>

<dl>
<dd>

**routing:** `typing.Optional[LoadBalancerRouting]` 
    
</dd>
</dl>

<dl>
<dd>

**health_check:** `typing.Optional[LoadBalancerHealthCheck]` 
    
</dd>
</dl>

<dl>
<dd>

**policy:** `typing.Optional[LoadBalancerPolicy]` 
    
</dd>
</dl>

<dl>
<dd>

**observability:** `typing.Optional[LoadBalancerObservability]` 
    
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

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Creates a layer 7 (HTTP/HTTPS) load balancer with routing rules, optional TLS, and an optional custom domain. Requires scope: load-balancer.write.
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
from ibee import Ibee, LoadBalancerBackend
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.load_balancers.create_l7load_balancer(
    workspace_id="710995",
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

**name:** `str` — Display name of the load balancer.
    
</dd>
</dl>

<dl>
<dd>

**protocol:** `CreateL7LoadBalancerRequestProtocol` 

- `http`
- `https`
    
</dd>
</dl>

<dl>
<dd>

**backends:** `typing.List[LoadBalancerBackend]` — Default backends for requests no rule matches.
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
</dd>
</dl>

<dl>
<dd>

**routing:** `typing.Optional[LoadBalancerRouting]` 
    
</dd>
</dl>

<dl>
<dd>

**health_check:** `typing.Optional[LoadBalancerHealthCheck]` 
    
</dd>
</dl>

<dl>
<dd>

**policy:** `typing.Optional[LoadBalancerPolicy]` 
    
</dd>
</dl>

<dl>
<dd>

**observability:** `typing.Optional[LoadBalancerObservability]` 
    
</dd>
</dl>

<dl>
<dd>

**tls:** `typing.Optional[LoadBalancerTls]` 
    
</dd>
</dl>

<dl>
<dd>

**custom_domain:** `typing.Optional[CreateL7LoadBalancerRequestCustomDomain]` — Custom hostname to serve. Point its DNS CNAME at the load balancer's endpoint host.
    
</dd>
</dl>

<dl>
<dd>

**rules:** `typing.Optional[typing.List[LoadBalancerRule]]` — Path- and header-based routing rules.
    
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

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Returns a load balancer's configuration, including its backends, routing, and TLS settings. Requires scope: load-balancer.read.
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

client.load_balancers.get_load_balancer(
    load_balancer_id="load_balancer_id",
    workspace_id="710995",
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

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Deletes a load balancer. The backend VMs are not deleted. Requires scope: load-balancer.write.
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

client.load_balancers.delete_load_balancer(
    load_balancer_id="load_balancer_id",
    workspace_id="710995",
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

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Changes an L4 load balancer's backends, routing, or TLS settings. Requires scope: load-balancer.write.
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

client.load_balancers.update_l4load_balancer(
    load_balancer_id="load_balancer_id",
    workspace_id="710995",
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

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
</dd>
</dl>

<dl>
<dd>

**name:** `typing.Optional[str]` — New display name.
    
</dd>
</dl>

<dl>
<dd>

**backends:** `typing.Optional[typing.List[LoadBalancerBackend]]` — Replacement backend list.
    
</dd>
</dl>

<dl>
<dd>

**routing:** `typing.Optional[LoadBalancerRouting]` 
    
</dd>
</dl>

<dl>
<dd>

**health_check:** `typing.Optional[LoadBalancerHealthCheck]` 
    
</dd>
</dl>

<dl>
<dd>

**policy:** `typing.Optional[LoadBalancerPolicy]` 
    
</dd>
</dl>

<dl>
<dd>

**observability:** `typing.Optional[LoadBalancerObservability]` 
    
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

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Changes an L7 load balancer's backends, routing rules, TLS settings, or custom domain. Requires scope: load-balancer.write.
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

client.load_balancers.update_l7load_balancer(
    load_balancer_id="load_balancer_id",
    workspace_id="710995",
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

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
</dd>
</dl>

<dl>
<dd>

**name:** `typing.Optional[str]` — New display name.
    
</dd>
</dl>

<dl>
<dd>

**backends:** `typing.Optional[typing.List[LoadBalancerBackend]]` — Replacement default backend list.
    
</dd>
</dl>

<dl>
<dd>

**routing:** `typing.Optional[LoadBalancerRouting]` 
    
</dd>
</dl>

<dl>
<dd>

**health_check:** `typing.Optional[LoadBalancerHealthCheck]` 
    
</dd>
</dl>

<dl>
<dd>

**policy:** `typing.Optional[LoadBalancerPolicy]` 
    
</dd>
</dl>

<dl>
<dd>

**observability:** `typing.Optional[LoadBalancerObservability]` 
    
</dd>
</dl>

<dl>
<dd>

**tls:** `typing.Optional[LoadBalancerTls]` 
    
</dd>
</dl>

<dl>
<dd>

**custom_domain:** `typing.Optional[UpdateL7LoadBalancerRequestCustomDomain]` — Custom hostname to serve. Point its DNS CNAME at the load balancer's endpoint host.
    
</dd>
</dl>

<dl>
<dd>

**rules:** `typing.Optional[typing.List[LoadBalancerRule]]` — Replacement routing rules.
    
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

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Returns a load balancer's provisioning status, endpoint URL, and any error conditions. Requires scope: load-balancer.read.
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

client.load_balancers.get_load_balancer_status(
    load_balancer_id="load_balancer_id",
    workspace_id="710995",
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

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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
    workspace_id="710995",
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

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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
    workspace_id="710995",
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

**vm_type:** `VmType` 

Kind of VM the plans are for. Required.
- `cloud`
- `gpu`
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
</dd>
</dl>

<dl>
<dd>

**site_id:** `typing.Optional[str]` — Optional exact placement filter. Copy `site_id` from `GET /compute/sites`.
    
</dd>
</dl>

<dl>
<dd>

**currency:** `typing.Optional[str]` — ISO 4217 code of the currency to quote prices in. Default `INR`.
    
</dd>
</dl>

<dl>
<dd>

**billing_interval:** `typing.Optional[BillingInterval]` 

Billing period to quote prices for.
- `HOURLY`
- `MONTHLY` (default)
    
</dd>
</dl>

<dl>
<dd>

**include_availability:** `typing.Optional[bool]` — Include an advisory placement check. Requires site_id. This does not reserve stock.
    
</dd>
</dl>

<dl>
<dd>

**os_type:** `typing.Optional[ListComputePlansRequestOsType]` — OS pool to check when include_availability is true.
    
</dd>
</dl>

<dl>
<dd>

**requires_public_ip:** `typing.Optional[bool]` — Include public IPv4 capacity in the advisory placement check.
    
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
    workspace_id="710995",
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

**vm_type:** `VmType` 

Kind of VM the images are for. Required.
- `cloud`
- `gpu`
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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

<details><summary><code>client.compute_catalog.<a href="src/ibee/compute_catalog/client.py">list_snapshot_storage_plans</a>(...) -> RecoveryStoragePlanList</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Select a priced item and send its billing_catalog unchanged when creating a snapshot. Discovery does not reserve capacity or create a resource.
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

client.compute_catalog.list_snapshot_storage_plans(
    workspace_id="710995",
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

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
</dd>
</dl>

<dl>
<dd>

**site_id:** `typing.Optional[str]` 
    
</dd>
</dl>

<dl>
<dd>

**currency:** `typing.Optional[str]` 
    
</dd>
</dl>

<dl>
<dd>

**billing_interval:** `typing.Optional[ListSnapshotStoragePlansRequestBillingInterval]` 
    
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

<details><summary><code>client.compute_catalog.<a href="src/ibee/compute_catalog/client.py">list_backup_storage_plans</a>(...) -> RecoveryStoragePlanList</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Select a priced item and send its billing_catalog unchanged when enabling backups or creating a manual backup run.
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

client.compute_catalog.list_backup_storage_plans(
    workspace_id="710995",
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

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
</dd>
</dl>

<dl>
<dd>

**site_id:** `typing.Optional[str]` 
    
</dd>
</dl>

<dl>
<dd>

**currency:** `typing.Optional[str]` 
    
</dd>
</dl>

<dl>
<dd>

**billing_interval:** `typing.Optional[ListBackupStoragePlansRequestBillingInterval]` 
    
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

Returns one page of cloud VMs in the workspace, newest first: 10 by default, at most 100 per page. Use `limit` and `offset` to page through the rest. Requires scope: vm.read.
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
    workspace_id="710995",
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

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
</dd>
</dl>

<dl>
<dd>

**limit:** `typing.Optional[int]` — Maximum number of records to return. The server returns 10 when this is omitted; use `offset` to read further pages.
    
</dd>
</dl>

<dl>
<dd>

**offset:** `typing.Optional[int]` — Number of records to skip before the first one returned.
    
</dd>
</dl>

<dl>
<dd>

**search:** `typing.Optional[str]` — Return only VMs whose name, IP address, OS or plan contains this text.
    
</dd>
</dl>

<dl>
<dd>

**sort_by:** `typing.Optional[ListCloudVmsRequestSortBy]` — Field to sort by. Default `created_at`.
    
</dd>
</dl>

<dl>
<dd>

**sort_direction:** `typing.Optional[ListCloudVmsRequestSortDirection]` — Sort direction. Default `desc`.
    
</dd>
</dl>

<dl>
<dd>

**status:** `typing.Optional[ListCloudVmsRequestStatus]` — Send `all` to include VMs deleted in the selected month (see `date`).
    
</dd>
</dl>

<dl>
<dd>

**date:** `typing.Optional[str]` — Calendar month `YYYY-MM` for the deleted-VM history returned with `status=all`.
    
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
from ibee import Ibee, ComputeBillingSelection
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.cloud_vms.create_cloud_vm(
    workspace_id="710995",
    name="web-server-01",
    site_id="68b99bd78a8eda32ff3f16ea",
    os_distro="ubuntu",
    os_type="linux",
    template_id="tmpl_ubuntu_2204",
    cpu=2,
    ram_mb=4096,
    plan_id="019f25b7-c1b3-7a9e-bfb9-8c83e323b517",
    billing_catalog=ComputeBillingSelection(
        sku_id="sku_id",
        sku_code="sku_code",
        billing_interval="HOURLY",
        committed=False,
        commitment_period="HOURLY",
        unit_price_minor=1,
        price_currency="INR",
    ),
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

**name:** `str` — Display name for the virtual machine.
    
</dd>
</dl>

<dl>
<dd>

**site_id:** `str` — Placement site ID from `GET /compute/sites`. Required: the API refuses a create without it (400 `invalid_site_id`). Use the same value when filtering plans and images.
    
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

**billing_catalog:** `ComputeBillingSelection` 
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
</dd>
</dl>

<dl>
<dd>

**idempotency_key:** `typing.Optional[str]` — Unique key used to safely retry write operations.
    
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

**ssh_keys:** `typing.Optional[typing.List[str]]` — Inline public SSH keys to install on the VM, in addition to the keys referenced by `ssh_key_ids`.
    
</dd>
</dl>

<dl>
<dd>

**vpc_id:** `typing.Optional[str]` — VPC to launch the VM into. Send it together with `subnet_id`; one without the other is refused. Omit both to launch on the public provider network.
    
</dd>
</dl>

<dl>
<dd>

**subnet_id:** `typing.Optional[str]` — Subnet of `vpc_id` for the VM's VPC NIC. Send it together with `vpc_id`.
    
</dd>
</dl>

<dl>
<dd>

**network_connectivity:** `typing.Optional[CreateCloudVmRequestNetworkConnectivity]` — How the VM reaches the internet. With a VPC it defaults to `private`. Without a VPC it is accepted only as `public_ip` together with `reserved_public_ip_id`, which attaches that Reserved IP on the public provider network. `public_ip` is refused on a `nat_gateway` VPC, and on a `private` VPC it needs `reserved_public_ip_id`.
    
</dd>
</dl>

<dl>
<dd>

**vpc_attachment_mode:** `typing.Optional[CreateCloudVmRequestVpcAttachmentMode]` — With a VPC, `primary` makes the VPC NIC the VM's only NIC. `secondary` keeps the public provider NIC as primary and adds the VPC as a second NIC; it needs `vpc_id` and `subnet_id` and cannot be combined with `reserved_public_ip_id`.
    
</dd>
</dl>

<dl>
<dd>

**reserved_public_ip_id:** `typing.Optional[str]` — Reserved IP to attach at launch. Needs `network_connectivity: public_ip` and the `primary` attachment mode. Accepted with a VPC or, without one, on the public provider network.
    
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
    workspace_id="710995",
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

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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

Deletes a cloud VM. Returns an operation you can poll for status. A VM with an automatically assigned public IP needs `public_ip_action` in the body. Requires scope: vm.write.
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
    workspace_id="710995",
    public_ip_action="release",
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

**request:** `VmDeleteRequest` 
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
</dd>
</dl>

<dl>
<dd>

**idempotency_key:** `typing.Optional[str]` — Unique key used to safely retry write operations.
    
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
    workspace_id="710995",
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

**request:** `PowerActionRequest` 
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
</dd>
</dl>

<dl>
<dd>

**idempotency_key:** `typing.Optional[str]` — Unique key used to safely retry write operations.
    
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
    workspace_id="710995",
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

**request:** `PowerActionRequest` 
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
</dd>
</dl>

<dl>
<dd>

**idempotency_key:** `typing.Optional[str]` — Unique key used to safely retry write operations.
    
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
    workspace_id="710995",
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

**request:** `PowerActionRequest` 
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
</dd>
</dl>

<dl>
<dd>

**idempotency_key:** `typing.Optional[str]` — Unique key used to safely retry write operations.
    
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
    workspace_id="710995",
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

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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

Adds or removes SSH keys, resets the Linux user password, or changes SSH password authentication on a cloud VM without rebooting it. Requires scope: vm.write.
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
    workspace_id="710995",
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

**request:** `VmAccessUpdateRequest` 
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
</dd>
</dl>

<dl>
<dd>

**idempotency_key:** `typing.Optional[str]` — Unique key used to safely retry write operations.
    
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

Checks whether a cloud VM can take a requested CPU, memory, or root-disk change before you start the resize. Requires scope: vm.write.
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
    workspace_id="710995",
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

**request:** `VmResizeRequest` 
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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

Changes a cloud VM's CPU and memory, and optionally grows its root disk, after the same precheck the portal runs. Requires scope: vm.write.
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
    workspace_id="710995",
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

**request:** `VmResizeRequest` 
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
</dd>
</dl>

<dl>
<dd>

**idempotency_key:** `typing.Optional[str]` — Unique key used to safely retry write operations.
    
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

Attaches a persistent block storage volume to a cloud VM. Requires scope: vm.write.
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
from ibee import Ibee, BillingCatalogSelection
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.cloud_vms.attach_cloud_vm_volume(
    vm_id="vm_id",
    workspace_id="710995",
    volume_id="volume_id",
    billing_catalog=BillingCatalogSelection(
        sku_id="sku_id",
        sku_code="sku_code",
    ),
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

**request:** `VmAttachVolumeRequest` 
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
</dd>
</dl>

<dl>
<dd>

**idempotency_key:** `typing.Optional[str]` — Unique key used to safely retry write operations.
    
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

Detaches a persistent block storage volume from a cloud VM. Unmount its filesystem in the guest first unless force is used. Requires scope: vm.write.
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
    workspace_id="710995",
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

**request:** `VmDetachVolumeRequest` 
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
</dd>
</dl>

<dl>
<dd>

**idempotency_key:** `typing.Optional[str]` — Unique key used to safely retry write operations.
    
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

Returns a cloud VM's lifecycle and operation event timeline. Requires scope: vm.read.
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
    workspace_id="710995",
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

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
</dd>
</dl>

<dl>
<dd>

**limit:** `typing.Optional[int]` — Maximum number of items to return (1-500). Default 100.
    
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

Returns rolled-up CPU, memory, disk, and network metric series for a cloud VM over a supported time range. Requires scope: vm.read.
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
    workspace_id="710995",
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

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
</dd>
</dl>

<dl>
<dd>

**range:** `typing.Optional[GetCloudVmMetricsTimeseriesRequestRange]` 

Time window to return, ending now.
- `30m`
- `1h`
- `6h`
- `24h`
- `7d`

Default `1h`.
    
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

Returns a cloud VM's received and transmitted byte totals for a calendar month. Requires scope: vm.read.
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
    workspace_id="710995",
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

**month:** `str` — Calendar month to report, as `YYYY-MM` (for example `2026-08`).
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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
    workspace_id="710995",
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

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
</dd>
</dl>

<dl>
<dd>

**limit:** `typing.Optional[int]` — Maximum number of records to return.
    
</dd>
</dl>

<dl>
<dd>

**offset:** `typing.Optional[int]` — Number of items to skip before the first returned item. Default 0.
    
</dd>
</dl>

<dl>
<dd>

**search:** `typing.Optional[str]` — Return only snapshot sets whose name contains this text.
    
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

Creates a recovery snapshot of a cloud VM's root disk, all attached disks, or selected data disks. Requires scope: vm.write.
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
from ibee import Ibee, BillingCatalogSelection
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.cloud_vms.create_cloud_vm_snapshot(
    vm_id="vm_id",
    workspace_id="710995",
    name="name",
    billing_catalog=BillingCatalogSelection(
        sku_id="sku_id",
        sku_code="sku_code",
    ),
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

**request:** `SnapshotCreateRequest` 
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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

Restores a cloud VM snapshot by replacing the VM, creating a new VM, or restoring a single volume. Requires scope: vm.write.
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
    workspace_id="710995",
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

**vm_id:** `str` — Source VM ID for the snapshot.
    
</dd>
</dl>

<dl>
<dd>

**request:** `SnapshotRestoreRequest` 
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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

<details><summary><code>client.cloud_vms.<a href="src/ibee/cloud_vms/client.py">list_all_cloud_vm_snapshots</a>(...) -> SnapshotSetList</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Lists snapshot sets of every Cloud VM in the workspace, as the portal's Snapshots page does. Requires scope: vm.read.
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

client.cloud_vms.list_all_cloud_vm_snapshots(
    workspace_id="710995",
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

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
</dd>
</dl>

<dl>
<dd>

**limit:** `typing.Optional[int]` — Maximum number of snapshot sets to return (1-500). Default 100.
    
</dd>
</dl>

<dl>
<dd>

**offset:** `typing.Optional[int]` — Number of items to skip before the first returned item. Default 0.
    
</dd>
</dl>

<dl>
<dd>

**search:** `typing.Optional[str]` — Return only snapshot sets whose fields contain this text.
    
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
    workspace_id="710995",
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

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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
    workspace_id="710995",
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

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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
    workspace_id="710995",
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

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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

Returns a cloud VM's effective automated backup policy, including whether backups are disabled. Requires scope: vm.read.
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
    workspace_id="710995",
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

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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

Updates a cloud VM's automated backup schedule and retention settings. Requires scope: vm.write.
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
    workspace_id="710995",
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

**request:** `BackupPolicyUpdateRequest` 
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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

Turns on automated backups for a cloud VM and creates its backup policy. Requires scope: vm.write.
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
from ibee import Ibee, BillingCatalogSelection
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.cloud_vms.enable_cloud_vm_backups(
    vm_id="vm_id",
    workspace_id="710995",
    billing_catalog=BillingCatalogSelection(
        sku_id="sku_id",
        sku_code="sku_code",
    ),
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

**request:** `BackupPolicyEnableRequest` 
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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

Stops future automated backups for a cloud VM without deleting existing recovery points. Requires scope: vm.write.
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
    workspace_id="710995",
    request={
        "key": "value"
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

**vm_id:** `str` — Virtual machine ID.
    
</dd>
</dl>

<dl>
<dd>

**request:** `typing.Dict[str, typing.Any]` — Send an empty object, `{}`.
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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
    workspace_id="710995",
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

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
</dd>
</dl>

<dl>
<dd>

**limit:** `typing.Optional[int]` — Maximum number of records to return.
    
</dd>
</dl>

<dl>
<dd>

**offset:** `typing.Optional[int]` — Number of items to skip before the first returned item. Default 0.
    
</dd>
</dl>

<dl>
<dd>

**search:** `typing.Optional[str]` — Return only backup runs whose fields contain this text.
    
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

Restores a cloud VM backup recovery point by replacing the VM, creating a new VM, or restoring a single volume. Requires scope: vm.write.
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
    workspace_id="710995",
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

**request:** `BackupRestoreRequest` 
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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

<details><summary><code>client.cloud_vms.<a href="src/ibee/cloud_vms/client.py">list_all_cloud_vm_backup_runs</a>(...) -> BackupRunList</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Lists backup runs and recovery points of every Cloud VM in the workspace, as the portal's Backups page does. Filter by `vm_id` or `status`. Requires scope: vm.read.
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

client.cloud_vms.list_all_cloud_vm_backup_runs(
    workspace_id="710995",
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

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
</dd>
</dl>

<dl>
<dd>

**vm_id:** `typing.Optional[str]` — Return only runs of this VM.
    
</dd>
</dl>

<dl>
<dd>

**status:** `typing.Optional[typing.Union[BackupStatus, typing.Sequence[BackupStatus]]]` — Return only runs in these states. Repeat the parameter for several states.
    
</dd>
</dl>

<dl>
<dd>

**limit:** `typing.Optional[int]` — Maximum number of records to return.
    
</dd>
</dl>

<dl>
<dd>

**offset:** `typing.Optional[int]` — Number of items to skip before the first returned item. Default 0.
    
</dd>
</dl>

<dl>
<dd>

**search:** `typing.Optional[str]` — Return only backup runs whose fields contain this text.
    
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
    workspace_id="710995",
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

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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

<details><summary><code>client.cloud_vms.<a href="src/ibee/cloud_vms/client.py">delete_cloud_vm_backup_run</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Deletes one backup run and its recovery point, as the portal's Backups page does. Requires scope: vm.write.
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

client.cloud_vms.delete_cloud_vm_backup_run(
    run_id="run_id",
    workspace_id="710995",
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

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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
    workspace_id="710995",
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

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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
    workspace_id="710995",
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

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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

Returns one page of GPU VMs in the workspace, newest first: 10 by default, at most 100 per page. Use `limit` and `offset` to page through the rest. Requires scope: vm.read.
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
    workspace_id="710995",
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

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
</dd>
</dl>

<dl>
<dd>

**limit:** `typing.Optional[int]` — Maximum number of records to return. The server returns 10 when this is omitted; use `offset` to read further pages.
    
</dd>
</dl>

<dl>
<dd>

**offset:** `typing.Optional[int]` — Number of records to skip before the first one returned.
    
</dd>
</dl>

<dl>
<dd>

**search:** `typing.Optional[str]` — Return only VMs whose name, IP address, OS or plan contains this text.
    
</dd>
</dl>

<dl>
<dd>

**sort_by:** `typing.Optional[ListGpuVmsRequestSortBy]` — Field to sort by. Default `created_at`.
    
</dd>
</dl>

<dl>
<dd>

**sort_direction:** `typing.Optional[ListGpuVmsRequestSortDirection]` — Sort direction. Default `desc`.
    
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
from ibee import Ibee, ComputeBillingSelection
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.gpu_vms.create_gpu_vm(
    workspace_id="710995",
    name="ml-training-01",
    site_id="68b99bd78a8eda32ff3f16ea",
    os_distro="ubuntu",
    os_type="linux",
    template_id="tmpl_ubuntu_2204_cuda",
    cpu=8,
    ram_mb=32768,
    gpu_count=1,
    gpu_model="A100",
    plan_id="019f25b7-c1b3-7a9e-bfb9-8c83e323b517",
    billing_catalog=ComputeBillingSelection(
        sku_id="sku_id",
        sku_code="sku_code",
        billing_interval="HOURLY",
        committed=False,
        commitment_period="HOURLY",
        unit_price_minor=1,
        price_currency="INR",
    ),
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

**name:** `str` — Display name for the virtual machine.
    
</dd>
</dl>

<dl>
<dd>

**site_id:** `str` — Placement site ID from `GET /compute/sites`. Required: the API refuses a create without it (400 `invalid_site_id`). Use the same value when filtering plans and images.
    
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

**billing_catalog:** `ComputeBillingSelection` 
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
</dd>
</dl>

<dl>
<dd>

**idempotency_key:** `typing.Optional[str]` — Unique key used to safely retry write operations.
    
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

**ssh_keys:** `typing.Optional[typing.List[str]]` — Inline public SSH keys to install on the VM, in addition to the keys referenced by `ssh_key_ids`.
    
</dd>
</dl>

<dl>
<dd>

**vpc_id:** `typing.Optional[str]` — VPC to launch the VM into. Send it together with `subnet_id`; one without the other is refused. Omit both to launch on the public provider network.
    
</dd>
</dl>

<dl>
<dd>

**subnet_id:** `typing.Optional[str]` — Subnet of `vpc_id` for the VM's VPC NIC. Send it together with `vpc_id`.
    
</dd>
</dl>

<dl>
<dd>

**network_connectivity:** `typing.Optional[CreateGpuVmRequestNetworkConnectivity]` — How the VM reaches the internet. With a VPC it defaults to `private`. Without a VPC it is accepted only as `public_ip` together with `reserved_public_ip_id`, which attaches that Reserved IP on the public provider network. `public_ip` is refused on a `nat_gateway` VPC, and on a `private` VPC it needs `reserved_public_ip_id`.
    
</dd>
</dl>

<dl>
<dd>

**vpc_attachment_mode:** `typing.Optional[CreateGpuVmRequestVpcAttachmentMode]` — GPU VMs support only `primary`: with a VPC, the VPC NIC is the VM's only NIC. `secondary` is refused with 400.
    
</dd>
</dl>

<dl>
<dd>

**reserved_public_ip_id:** `typing.Optional[str]` — Reserved IP to attach at launch. Needs `network_connectivity: public_ip`. Accepted with a VPC or, without one, on the public provider network.
    
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
    workspace_id="710995",
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

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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

Deletes a GPU VM. Returns an operation you can poll for status. A VM with an automatically assigned public IP needs `public_ip_action` in the body. Requires scope: vm.write.
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
    workspace_id="710995",
    public_ip_action="release",
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

**request:** `VmDeleteRequest` 
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
</dd>
</dl>

<dl>
<dd>

**idempotency_key:** `typing.Optional[str]` — Unique key used to safely retry write operations.
    
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
    workspace_id="710995",
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

**request:** `PowerActionRequest` 
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
</dd>
</dl>

<dl>
<dd>

**idempotency_key:** `typing.Optional[str]` — Unique key used to safely retry write operations.
    
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
    workspace_id="710995",
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

**request:** `PowerActionRequest` 
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
</dd>
</dl>

<dl>
<dd>

**idempotency_key:** `typing.Optional[str]` — Unique key used to safely retry write operations.
    
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
    workspace_id="710995",
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

**request:** `PowerActionRequest` 
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
</dd>
</dl>

<dl>
<dd>

**idempotency_key:** `typing.Optional[str]` — Unique key used to safely retry write operations.
    
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
    workspace_id="710995",
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

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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

Adds or removes SSH keys, resets the Linux user password, or changes SSH password authentication on a GPU VM without rebooting it or interrupting running GPU workloads. Requires scope: vm.write.
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
    workspace_id="710995",
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

**request:** `VmAccessUpdateRequest` 
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
</dd>
</dl>

<dl>
<dd>

**idempotency_key:** `typing.Optional[str]` — Unique key used to safely retry write operations.
    
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

Checks whether a GPU VM can take a requested CPU, memory, or root-disk change before you start the resize. The attached GPU stays the same. Requires scope: vm.write.
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
    workspace_id="710995",
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

**request:** `VmResizeRequest` 
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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

Changes a GPU VM's CPU and memory, and optionally grows its root disk, after the same precheck the portal runs. Requires scope: vm.write.
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
    workspace_id="710995",
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

**request:** `VmResizeRequest` 
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
</dd>
</dl>

<dl>
<dd>

**idempotency_key:** `typing.Optional[str]` — Unique key used to safely retry write operations.
    
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

Attaches a persistent block storage volume to a GPU VM, for datasets, checkpoints, or model weights. Requires scope: vm.write.
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
from ibee import Ibee, BillingCatalogSelection
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.gpu_vms.attach_gpu_vm_volume(
    vm_id="vm_id",
    workspace_id="710995",
    volume_id="volume_id",
    billing_catalog=BillingCatalogSelection(
        sku_id="sku_id",
        sku_code="sku_code",
    ),
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

**request:** `VmAttachVolumeRequest` 
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
</dd>
</dl>

<dl>
<dd>

**idempotency_key:** `typing.Optional[str]` — Unique key used to safely retry write operations.
    
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

Detaches a persistent block storage volume from a GPU VM. Stop jobs using it and unmount its filesystem in the guest first unless force is used. Requires scope: vm.write.
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
    workspace_id="710995",
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

**request:** `VmDetachVolumeRequest` 
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
</dd>
</dl>

<dl>
<dd>

**idempotency_key:** `typing.Optional[str]` — Unique key used to safely retry write operations.
    
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

Returns a GPU VM's lifecycle and operation event timeline. Requires scope: vm.read.
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
    workspace_id="710995",
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

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
</dd>
</dl>

<dl>
<dd>

**limit:** `typing.Optional[int]` — Maximum number of items to return (1-500). Default 100.
    
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

Returns rolled-up metric series for a GPU VM over a supported time range. Requires scope: vm.read.
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
    workspace_id="710995",
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

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
</dd>
</dl>

<dl>
<dd>

**range:** `typing.Optional[GetGpuVmMetricsTimeseriesRequestRange]` 

Time window to return, ending now.
- `30m`
- `1h`
- `6h`
- `24h`
- `7d`

Default `1h`.
    
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

Returns a GPU VM's received and transmitted byte totals for a calendar month. Requires scope: vm.read.
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
    workspace_id="710995",
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

**month:** `str` — Calendar month to report, as `YYYY-MM` (for example `2026-08`).
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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
    workspace_id="710995",
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

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
</dd>
</dl>

<dl>
<dd>

**limit:** `typing.Optional[int]` — Maximum number of records to return.
    
</dd>
</dl>

<dl>
<dd>

**offset:** `typing.Optional[int]` — Number of items to skip before the first returned item. Default 0.
    
</dd>
</dl>

<dl>
<dd>

**search:** `typing.Optional[str]` — Return only snapshot sets whose name contains this text.
    
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

Creates a recovery snapshot of a GPU VM's root disk, all attached disks, or selected data disks. Requires scope: vm.write.
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
from ibee import Ibee, BillingCatalogSelection
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.gpu_vms.create_gpu_vm_snapshot(
    vm_id="vm_id",
    workspace_id="710995",
    name="name",
    billing_catalog=BillingCatalogSelection(
        sku_id="sku_id",
        sku_code="sku_code",
    ),
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

**request:** `SnapshotCreateRequest` 
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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

Restores a GPU VM snapshot by replacing the VM, creating a new GPU VM, or restoring a single volume. Requires scope: vm.write.
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
    workspace_id="710995",
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

**vm_id:** `str` — Source GPU VM ID for the snapshot.
    
</dd>
</dl>

<dl>
<dd>

**request:** `SnapshotRestoreRequest` 
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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

<details><summary><code>client.gpu_vms.<a href="src/ibee/gpu_vms/client.py">list_all_gpu_vm_snapshots</a>(...) -> SnapshotSetList</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Lists snapshot sets of every Gpu VM in the workspace, as the portal's Snapshots page does. Requires scope: vm.read.
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

client.gpu_vms.list_all_gpu_vm_snapshots(
    workspace_id="710995",
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

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
</dd>
</dl>

<dl>
<dd>

**limit:** `typing.Optional[int]` — Maximum number of snapshot sets to return (1-500). Default 100.
    
</dd>
</dl>

<dl>
<dd>

**offset:** `typing.Optional[int]` — Number of items to skip before the first returned item. Default 0.
    
</dd>
</dl>

<dl>
<dd>

**search:** `typing.Optional[str]` — Return only snapshot sets whose fields contain this text.
    
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
    workspace_id="710995",
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

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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
    workspace_id="710995",
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

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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
    workspace_id="710995",
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

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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

Returns a GPU VM's effective automated backup policy, including whether backups are disabled. Requires scope: vm.read.
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
    workspace_id="710995",
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

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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

Updates a GPU VM's automated backup schedule and retention settings. Requires scope: vm.write.
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
    workspace_id="710995",
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

**request:** `BackupPolicyUpdateRequest` 
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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

Turns on automated backups for a GPU VM and creates its backup policy. Requires scope: vm.write.
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
from ibee import Ibee, BillingCatalogSelection
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.gpu_vms.enable_gpu_vm_backups(
    vm_id="vm_id",
    workspace_id="710995",
    billing_catalog=BillingCatalogSelection(
        sku_id="sku_id",
        sku_code="sku_code",
    ),
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

**request:** `BackupPolicyEnableRequest` 
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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

Stops future automated backups for a GPU VM without deleting existing recovery points. Requires scope: vm.write.
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
    workspace_id="710995",
    request={
        "key": "value"
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

**vm_id:** `str` — Virtual machine ID.
    
</dd>
</dl>

<dl>
<dd>

**request:** `typing.Dict[str, typing.Any]` — Send an empty object, `{}`.
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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
    workspace_id="710995",
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

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
</dd>
</dl>

<dl>
<dd>

**limit:** `typing.Optional[int]` — Maximum number of records to return.
    
</dd>
</dl>

<dl>
<dd>

**offset:** `typing.Optional[int]` — Number of items to skip before the first returned item. Default 0.
    
</dd>
</dl>

<dl>
<dd>

**search:** `typing.Optional[str]` — Return only backup runs whose fields contain this text.
    
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

Restores a GPU VM backup recovery point by replacing the VM, creating a new GPU VM, or restoring a single volume. Requires scope: vm.write.
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
    workspace_id="710995",
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

**request:** `BackupRestoreRequest` 
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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

<details><summary><code>client.gpu_vms.<a href="src/ibee/gpu_vms/client.py">list_all_gpu_vm_backup_runs</a>(...) -> BackupRunList</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Lists backup runs and recovery points of every Gpu VM in the workspace, as the portal's Backups page does. Filter by `vm_id` or `status`. Requires scope: vm.read.
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

client.gpu_vms.list_all_gpu_vm_backup_runs(
    workspace_id="710995",
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

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
</dd>
</dl>

<dl>
<dd>

**vm_id:** `typing.Optional[str]` — Return only runs of this VM.
    
</dd>
</dl>

<dl>
<dd>

**status:** `typing.Optional[typing.Union[BackupStatus, typing.Sequence[BackupStatus]]]` — Return only runs in these states. Repeat the parameter for several states.
    
</dd>
</dl>

<dl>
<dd>

**limit:** `typing.Optional[int]` — Maximum number of records to return.
    
</dd>
</dl>

<dl>
<dd>

**offset:** `typing.Optional[int]` — Number of items to skip before the first returned item. Default 0.
    
</dd>
</dl>

<dl>
<dd>

**search:** `typing.Optional[str]` — Return only backup runs whose fields contain this text.
    
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
    workspace_id="710995",
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

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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

<details><summary><code>client.gpu_vms.<a href="src/ibee/gpu_vms/client.py">delete_gpu_vm_backup_run</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Deletes one backup run and its recovery point, as the portal's Backups page does. Requires scope: vm.write.
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

client.gpu_vms.delete_gpu_vm_backup_run(
    run_id="run_id",
    workspace_id="710995",
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

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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
    workspace_id="710995",
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

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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

## BlockStorage
<details><summary><code>client.block_storage.<a href="src/ibee/block_storage/client.py">list_block_storage_plans</a>(...) -> BlockStoragePlanList</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Returns the block storage plans with their sizes, performance and prices, as the portal's Create Volume page shows them. Pick a `sku_code` for createBlockVolume. Requires scope: block-storage.read.
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

client.block_storage.list_block_storage_plans(
    workspace_id="710995",
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

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
</dd>
</dl>

<dl>
<dd>

**site_id:** `typing.Optional[str]` — Return only plans offered at this site.
    
</dd>
</dl>

<dl>
<dd>

**currency:** `typing.Optional[str]` — Price currency. Default `INR`.
    
</dd>
</dl>

<dl>
<dd>

**billing_interval:** `typing.Optional[ListBlockStoragePlansRequestBillingInterval]` — Billing interval of the listed prices. Default `MONTHLY`.
    
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

<details><summary><code>client.block_storage.<a href="src/ibee/block_storage/client.py">list_block_volumes</a>(...) -> typing.List[BlockVolume]</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Lists the block storage volumes in a workspace, with their size, status, and attached VM. Requires scope: block-storage.read.
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

client.block_storage.list_block_volumes(
    workspace_id="710995",
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

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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

<details><summary><code>client.block_storage.<a href="src/ibee/block_storage/client.py">create_block_volume</a>(...) -> BlockVolumeAction</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

The public edge resolves authoritative pricing from the server-owned product catalog and validates billing before forwarding this request to the existing portal volume flow. Client-supplied price or billing catalog objects are not accepted.
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

client.block_storage.create_block_volume(
    workspace_id="710995",
    name="name",
    size_gb=1,
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

**name:** `str` — Display name of the volume (1-255 characters).
    
</dd>
</dl>

<dl>
<dd>

**size_gb:** `int` — Size in GB (1-10000).
    
</dd>
</dl>

<dl>
<dd>

**site_id:** `str` — Site to create the volume at.
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
</dd>
</dl>

<dl>
<dd>

**site_name:** `typing.Optional[str]` — Display name of that site, as shown in the portal.
    
</dd>
</dl>

<dl>
<dd>

**sku_code:** `typing.Optional[str]` — Optional public selector returned by the server-owned Block Storage catalog. The edge resolves all price and catalog metadata; callers cannot submit pricing.
    
</dd>
</dl>

<dl>
<dd>

**volume_class:** `typing.Optional[CreateBlockVolumeRequestVolumeClass]` 

Performance class of the volume.
- `capacity`: lowest cost per GB.
- `balanced`: general purpose.
- `performance`: highest throughput and IOPS.
Default `balanced`.
    
</dd>
</dl>

<dl>
<dd>

**replica_count:** `typing.Optional[int]` — Number of synchronous replicas kept for the volume (1-5). Default 2.
    
</dd>
</dl>

<dl>
<dd>

**backup_enabled:** `typing.Optional[bool]` — Whether volume backups are enabled. Default true.
    
</dd>
</dl>

<dl>
<dd>

**idempotency_key:** `typing.Optional[str]` — Caller-chosen key that makes a retried request return the original operation instead of starting a new one.
    
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

<details><summary><code>client.block_storage.<a href="src/ibee/block_storage/client.py">get_block_volume</a>(...) -> BlockVolume</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Returns a block storage volume, including its size, status, and the VM it is attached to. Requires scope: block-storage.read.
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

client.block_storage.get_block_volume(
    volume_id="volume_id",
    workspace_id="710995",
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

**volume_id:** `str` — Workspace-owned block-volume ID.
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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

<details><summary><code>client.block_storage.<a href="src/ibee/block_storage/client.py">delete_block_volume</a>(...) -> BlockVolumeDelete</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Permanently deletes a block storage volume and its data. Requires scope: block-storage.write.
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

client.block_storage.delete_block_volume(
    volume_id="volume_id",
    workspace_id="710995",
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

**volume_id:** `str` — Workspace-owned block-volume ID.
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
</dd>
</dl>

<dl>
<dd>

**force:** `typing.Optional[bool]` — Delete the volume even if it is still attached. Default false.
    
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

<details><summary><code>client.block_storage.<a href="src/ibee/block_storage/client.py">list_block_volume_operations</a>(...) -> typing.List[BlockVolumeOperation]</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Lists the operations run on a block storage volume and their status. Requires scope: block-storage.read.
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

client.block_storage.list_block_volume_operations(
    volume_id="volume_id",
    workspace_id="710995",
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

**volume_id:** `str` — Workspace-owned block-volume ID.
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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

<details><summary><code>client.block_storage.<a href="src/ibee/block_storage/client.py">resize_block_volume</a>(...) -> BlockVolumeAction</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Block volumes can only be increased in size.
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

client.block_storage.resize_block_volume(
    volume_id="volume_id",
    workspace_id="710995",
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

**volume_id:** `str` — Workspace-owned block-volume ID.
    
</dd>
</dl>

<dl>
<dd>

**new_size_gb:** `int` — New size in GB.
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
</dd>
</dl>

<dl>
<dd>

**vm_state:** `typing.Optional[ResizeBlockVolumeRequestVmState]` 

Current power state of the VM, when the caller knows it.
- `running`
- `stopped`
- `suspended`
    
</dd>
</dl>

<dl>
<dd>

**allow_online:** `typing.Optional[bool]` — Permit the resize while the volume is attached to a running VM. Default false.
    
</dd>
</dl>

<dl>
<dd>

**idempotency_key:** `typing.Optional[str]` — Caller-chosen key that makes a retried request return the original operation instead of starting a new one.
    
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

## Cdn
<details><summary><code>client.cdn.<a href="src/ibee/cdn/client.py">list_cdn_distributions</a>(...) -> CdnDistributionList</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Lists the CDN distributions in a workspace. Requires scope: cdn.read.
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

client.cdn.list_cdn_distributions(
    workspace_id="710995",
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

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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

<details><summary><code>client.cdn.<a href="src/ibee/cdn/client.py">create_cdn_distribution</a>(...) -> CdnDistribution</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Creates a CDN distribution that caches and serves content from an object storage bucket or other origin through the edge network. Requires scope: cdn.write.
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

client.cdn.create_cdn_distribution(
    workspace_id="710995",
    name="name",
    origin_id="origin_id",
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

**name:** `str` — Display name of the distribution (1-128 characters).
    
</dd>
</dl>

<dl>
<dd>

**origin_id:** `str` — Bucket name for `bucket` origins, or the custom origin's ID.
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
</dd>
</dl>

<dl>
<dd>

**origin_type:** `typing.Optional[CreateCdnDistributionRequestOriginType]` 

- `bucket`: serve an Object Storage bucket (default).
- `custom`: serve a custom origin.
    
</dd>
</dl>

<dl>
<dd>

**cache_policy:** `typing.Optional[CreateCdnDistributionRequestCachePolicy]` 

Caching behaviour. Default `static-assets`.
- `static-assets`: long-term caching for immutable assets; 1 year at the CDN, browsers revalidate.
- `media`: medium-term caching for video and audio; 30 days at the CDN.
- `short`: short-term caching for frequently changing content; 1 hour at the CDN.
- `no-cache`: no caching, for dynamic responses.
    
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

<details><summary><code>client.cdn.<a href="src/ibee/cdn/client.py">get_cdn_distribution</a>(...) -> CdnDistribution</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Returns a CDN distribution's origin, cache policy, domains, and status. Requires scope: cdn.read.
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

client.cdn.get_cdn_distribution(
    distribution_id="distribution_id",
    workspace_id="710995",
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

**distribution_id:** `str` — CDN distribution ID.
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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

<details><summary><code>client.cdn.<a href="src/ibee/cdn/client.py">delete_cdn_distribution</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Deletes a CDN distribution. Requires scope: cdn.write.
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

client.cdn.delete_cdn_distribution(
    distribution_id="distribution_id",
    workspace_id="710995",
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

**distribution_id:** `str` — CDN distribution ID.
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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

<details><summary><code>client.cdn.<a href="src/ibee/cdn/client.py">update_cdn_distribution</a>(...) -> CdnDistribution</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Changes a CDN distribution's name, origin, or cache policy. Requires scope: cdn.write.
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

client.cdn.update_cdn_distribution(
    distribution_id="distribution_id",
    workspace_id="710995",
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

**distribution_id:** `str` — CDN distribution ID.
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
</dd>
</dl>

<dl>
<dd>

**name:** `typing.Optional[str]` — New display name.
    
</dd>
</dl>

<dl>
<dd>

**cache_policy:** `typing.Optional[UpdateCdnDistributionRequestCachePolicy]` 

New caching behaviour.
- `static-assets`: long-term caching for immutable assets; 1 year at the CDN, browsers revalidate.
- `media`: medium-term caching for video and audio; 30 days at the CDN.
- `short`: short-term caching for frequently changing content; 1 hour at the CDN.
- `no-cache`: no caching, for dynamic responses.
    
</dd>
</dl>

<dl>
<dd>

**enabled:** `typing.Optional[bool]` — Whether the distribution serves traffic.
    
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

<details><summary><code>client.cdn.<a href="src/ibee/cdn/client.py">get_cdn_distribution_metrics</a>(...) -> CdnDistributionMetrics</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Returns traffic, cache and origin metrics of the distribution for the last 24 hours, 7 days or 30 days, as the portal's Metrics tab shows them. Requires scope: cdn.read.
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

client.cdn.get_cdn_distribution_metrics(
    distribution_id="distribution_id",
    workspace_id="710995",
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

**distribution_id:** `str` — CDN distribution ID.
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
</dd>
</dl>

<dl>
<dd>

**range:** `typing.Optional[GetCdnDistributionMetricsRequestRange]` — Time range. Default `24h`.
    
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

<details><summary><code>client.cdn.<a href="src/ibee/cdn/client.py">get_cdn_website_config</a>(...) -> CdnWebsiteConfig</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Returns a CDN distribution's static website settings, such as its index document. Requires scope: cdn.read.
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

client.cdn.get_cdn_website_config(
    distribution_id="distribution_id",
    workspace_id="710995",
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

**distribution_id:** `str` — CDN distribution ID.
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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

<details><summary><code>client.cdn.<a href="src/ibee/cdn/client.py">update_cdn_website_config</a>(...) -> CdnWebsiteConfig</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Turns on static website hosting for a CDN distribution, or changes its index document. Requires scope: cdn.write.
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

client.cdn.update_cdn_website_config(
    distribution_id="distribution_id",
    workspace_id="710995",
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

**distribution_id:** `str` — CDN distribution ID.
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
</dd>
</dl>

<dl>
<dd>

**index_document:** `typing.Optional[str]` — Object served for directory requests. Default `index.html`.
    
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

<details><summary><code>client.cdn.<a href="src/ibee/cdn/client.py">delete_cdn_website_config</a>(...) -> CdnWebsiteConfig</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Turns off static website hosting for a CDN distribution. Requires scope: cdn.write.
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

client.cdn.delete_cdn_website_config(
    distribution_id="distribution_id",
    workspace_id="710995",
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

**distribution_id:** `str` — CDN distribution ID.
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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

<details><summary><code>client.cdn.<a href="src/ibee/cdn/client.py">list_cdn_custom_domains</a>(...) -> CdnCustomDomainList</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Lists the custom domains on a CDN distribution, with their verification and certificate status. Requires scope: cdn.read.
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

client.cdn.list_cdn_custom_domains(
    distribution_id="distribution_id",
    workspace_id="710995",
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

**distribution_id:** `str` — CDN distribution ID.
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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

<details><summary><code>client.cdn.<a href="src/ibee/cdn/client.py">create_cdn_custom_domain</a>(...) -> CdnCustomDomain</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Adds a custom domain to a CDN distribution and returns the DNS records needed to verify it. Requires scope: cdn.write.
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

client.cdn.create_cdn_custom_domain(
    distribution_id="distribution_id",
    workspace_id="710995",
    domain="domain",
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

**distribution_id:** `str` — CDN distribution ID.
    
</dd>
</dl>

<dl>
<dd>

**domain:** `str` — Fully qualified hostname to serve, for example `cdn.example.com`.
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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

<details><summary><code>client.cdn.<a href="src/ibee/cdn/client.py">get_cdn_custom_domain</a>(...) -> CdnCustomDomain</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Returns a CDN custom domain's verification status, DNS instructions, and TLS certificate status. Requires scope: cdn.read.
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

client.cdn.get_cdn_custom_domain(
    distribution_id="distribution_id",
    domain="domain",
    workspace_id="710995",
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

**distribution_id:** `str` — CDN distribution ID.
    
</dd>
</dl>

<dl>
<dd>

**domain:** `str` — Fully qualified custom domain.
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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

<details><summary><code>client.cdn.<a href="src/ibee/cdn/client.py">delete_cdn_custom_domain</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Removes a custom domain from a CDN distribution. Requires scope: cdn.write.
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

client.cdn.delete_cdn_custom_domain(
    distribution_id="distribution_id",
    domain="domain",
    workspace_id="710995",
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

**distribution_id:** `str` — CDN distribution ID.
    
</dd>
</dl>

<dl>
<dd>

**domain:** `str` — Fully qualified custom domain.
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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

<details><summary><code>client.cdn.<a href="src/ibee/cdn/client.py">verify_cdn_custom_domain</a>(...) -> CdnCustomDomainVerification</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Checks a CDN custom domain's DNS records and updates its verification status. Requires scope: cdn.write.
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

client.cdn.verify_cdn_custom_domain(
    distribution_id="distribution_id",
    domain="domain",
    workspace_id="710995",
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

**distribution_id:** `str` — CDN distribution ID.
    
</dd>
</dl>

<dl>
<dd>

**domain:** `str` — Fully qualified custom domain.
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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

<details><summary><code>client.cdn.<a href="src/ibee/cdn/client.py">purge_cdn_cache</a>(...) -> CdnCachePurge</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Purges matching cache content synchronously for a distribution in the
selected workspace. For a normal single-page application deployment,
use `mode: url` with `paths: ["/index.html"]`. Do not purge
fingerprinted assets such as `/assets/app.a91c3.js`; use `paths:
["/*"]` only for an emergency full-cache invalidation.
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

client.cdn.purge_cdn_cache(
    distribution_id="distribution_id",
    workspace_id="710995",
    mode="url",
    paths=[
        "/index.html"
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

**distribution_id:** `str` — CDN distribution ID.
    
</dd>
</dl>

<dl>
<dd>

**mode:** `PurgeCdnCacheRequestMode` 

- `url`: purge the paths in `paths`.
- `hostname`: purge everything for the hostnames in `hostnames`.
- `tag`: purge content tagged with `tags`.
- `prefix`: purge paths starting with `prefixes`.
- `all`: purge the whole distribution.
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
</dd>
</dl>

<dl>
<dd>

**paths:** `typing.Optional[typing.List[str]]` — Paths to purge, for `url` mode.
    
</dd>
</dl>

<dl>
<dd>

**hostnames:** `typing.Optional[typing.List[str]]` — Hostnames to purge, for `hostname` mode.
    
</dd>
</dl>

<dl>
<dd>

**tags:** `typing.Optional[typing.List[str]]` — Cache tags to purge, for `tag` mode.
    
</dd>
</dl>

<dl>
<dd>

**prefixes:** `typing.Optional[typing.List[str]]` — Path prefixes to purge, for `prefix` mode.
    
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

## ContainerRegistry
<details><summary><code>client.container_registry.<a href="src/ibee/container_registry/client.py">check_container_registry_name_availability</a>(...) -> ContainerRegistryNameAvailability</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Checks whether a registry name is free across IBEE. Names are global and never reassigned; unavailable names come with suggestions. Requires scope: container-registry.read.
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

client.container_registry.check_container_registry_name_availability(
    registry_name="registry_name",
    workspace_id="710995",
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

**registry_name:** `str` — Registry name to check.
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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

<details><summary><code>client.container_registry.<a href="src/ibee/container_registry/client.py">list_container_registries</a>(...) -> ContainerRegistryList</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Lists the workspace's registries, newest first. Paged with `page` and `page_size` (at most 100). Requires scope: container-registry.read.
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

client.container_registry.list_container_registries(
    workspace_id="710995",
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

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
</dd>
</dl>

<dl>
<dd>

**page:** `typing.Optional[int]` — Page number.
    
</dd>
</dl>

<dl>
<dd>

**page_size:** `typing.Optional[int]` — Number of records per page.
    
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

<details><summary><code>client.container_registry.<a href="src/ibee/container_registry/client.py">create_container_registry</a>(...) -> ContainerRegistry</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Creates a registry with a storage plan (`billing_catalog.sku_code`).
The registry service asks Billing whether the workspace may buy that
plan and refuses with 403 `billing_resource_not_eligible` (and a
`reason`) when it may not. Returns 201 when the registry is active, or
202 while provisioning finishes in the background; poll the registry
until `observed_state` is `ACTIVE`. Requires scope:
container-registry.write.
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
from ibee import Ibee, ContainerRegistrySecuritySettings, ContainerRegistryBillingCatalog
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.container_registry.create_container_registry(
    workspace_id="710995",
    registry_name="acme-apps",
    confirm_registry_name="acme-apps",
    visibility="PRIVATE",
    security=ContainerRegistrySecuritySettings(
        vulnerability_pull_policy="ALLOW",
    ),
    billing_catalog=ContainerRegistryBillingCatalog(
        sku_code="REGISTRY-STORAGE-250GB",
    ),
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

**registry_name:** `str` — Globally unique name; it cannot be changed or reused.
    
</dd>
</dl>

<dl>
<dd>

**confirm_registry_name:** `str` — Must equal `registry_name`.
    
</dd>
</dl>

<dl>
<dd>

**billing_catalog:** `ContainerRegistryBillingCatalog` 
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
</dd>
</dl>

<dl>
<dd>

**visibility:** `typing.Optional[ContainerRegistryVisibility]` 

- `PRIVATE`: pulls need an access token (default).
- `PUBLIC`: anonymous pulls are allowed; egress is charged.
    
</dd>
</dl>

<dl>
<dd>

**acknowledge_public_egress_charges:** `typing.Optional[bool]` — Required to be `true` when `visibility` is `PUBLIC`.
    
</dd>
</dl>

<dl>
<dd>

**security:** `typing.Optional[ContainerRegistrySecuritySettings]` 
    
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

<details><summary><code>client.container_registry.<a href="src/ibee/container_registry/client.py">get_container_registry</a>(...) -> ContainerRegistry</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Returns one registry, including its visibility, pull policy and provisioning state. A deleted registry is still returned, with `deleted_at` set. Requires scope: container-registry.read.
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

client.container_registry.get_container_registry(
    registry_id="registry_id",
    workspace_id="710995",
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

**registry_id:** `str` — Registry ID.
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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

<details><summary><code>client.container_registry.<a href="src/ibee/container_registry/client.py">delete_container_registry</a>(...) -> ContainerRegistry</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Starts deleting a registry; returns 202 with `observed_state: DELETING`. The registry must be empty: 409 with `detail.code: registry_not_empty` otherwise (see Empty registry). The name is never reused. Requires scope: container-registry.write.
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

client.container_registry.delete_container_registry(
    registry_id="registry_id",
    workspace_id="710995",
    confirm_registry_name="confirm_registry_name",
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

**registry_id:** `str` — Registry ID.
    
</dd>
</dl>

<dl>
<dd>

**confirm_registry_name:** `str` — The registry's name, repeated to confirm a destructive call.
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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

<details><summary><code>client.container_registry.<a href="src/ibee/container_registry/client.py">update_container_registry_visibility</a>(...) -> ContainerRegistry</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Makes a registry private or public. Public requires `acknowledge_public_egress_charges: true`, because anonymous pull bandwidth is billed to the workspace. Returns 202 while the change is applied. Requires scope: container-registry.write.
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

client.container_registry.update_container_registry_visibility(
    registry_id="registry_id",
    workspace_id="710995",
    visibility="PUBLIC",
    acknowledge_public_egress_charges=True,
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

**registry_id:** `str` — Registry ID.
    
</dd>
</dl>

<dl>
<dd>

**visibility:** `ContainerRegistryVisibility` 
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
</dd>
</dl>

<dl>
<dd>

**acknowledge_public_egress_charges:** `typing.Optional[bool]` — Required to be `true` when `visibility` is `PUBLIC`.
    
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

<details><summary><code>client.container_registry.<a href="src/ibee/container_registry/client.py">retry_container_registry_provisioning</a>(...) -> ContainerRegistryReconcile</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Queues the registry's pending change (create, update, upgrade or delete) to run again, for example after `observed_state: ERROR`. Requires scope: container-registry.write.
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

client.container_registry.retry_container_registry_provisioning(
    registry_id="registry_id",
    workspace_id="710995",
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

**registry_id:** `str` — Registry ID.
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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

<details><summary><code>client.container_registry.<a href="src/ibee/container_registry/client.py">get_container_registry_package</a>(...) -> ContainerRegistryPackage</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Returns the registry's current storage plan, a pending upgrade if there is one, and the status of the change being applied. Requires scope: container-registry.read.
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

client.container_registry.get_container_registry_package(
    registry_id="registry_id",
    workspace_id="710995",
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

**registry_id:** `str` — Registry ID.
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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

<details><summary><code>client.container_registry.<a href="src/ibee/container_registry/client.py">upgrade_container_registry_package</a>(...) -> ContainerRegistryPackageOperation</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Moves an active registry to a larger storage plan. Only larger quotas
are accepted and only one change can be pending (409 otherwise). The
registry service asks Billing first and refuses with 403
`billing_resource_not_eligible` when the plan is not allowed. Send an
`Idempotency-Key` header: a retry with the same key and plan returns
the original operation (202 while pending, 200 once applied); the same
key with a different plan returns 409. Requires scope:
container-registry.write.
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
from ibee import Ibee, ContainerRegistryBillingCatalog
from ibee.environment import IbeeEnvironment

client = Ibee(
    token="<token>",
    environment=IbeeEnvironment.PRODUCTION,
)

client.container_registry.upgrade_container_registry_package(
    registry_id="registry_id",
    workspace_id="710995",
    billing_catalog=ContainerRegistryBillingCatalog(
        sku_code="REGISTRY-STORAGE-500GB",
    ),
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

**registry_id:** `str` — Registry ID.
    
</dd>
</dl>

<dl>
<dd>

**billing_catalog:** `ContainerRegistryBillingCatalog` 
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
</dd>
</dl>

<dl>
<dd>

**idempotency_key:** `typing.Optional[str]` — Unique key for this upgrade. The registry service reads this header (not `X-Idempotency-Key`); a retry with the same key and plan returns the original operation.
    
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

<details><summary><code>client.container_registry.<a href="src/ibee/container_registry/client.py">list_container_registry_access_tokens</a>(...) -> typing.List[ContainerRegistryAccessToken]</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Lists the access tokens that can use this registry, newest first. Secrets are never returned. Requires scope: container-registry.read.
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

client.container_registry.list_container_registry_access_tokens(
    registry_id="registry_id",
    workspace_id="710995",
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

**registry_id:** `str` — Registry ID.
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
</dd>
</dl>

<dl>
<dd>

**include_revoked:** `typing.Optional[bool]` — Include revoked tokens.
    
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

<details><summary><code>client.container_registry.<a href="src/ibee/container_registry/client.py">create_container_registry_access_token</a>(...) -> ContainerRegistryAccessTokenSecret</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Creates a Docker login credential for the registry. The `username`
and `secret` are returned once and cannot be read again. The registry
must be active, and the registry service asks Billing whether the
workspace may create credentials. Requires scope:
container-registry.write.
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

client.container_registry.create_container_registry_access_token(
    registry_id="registry_id",
    workspace_id="710995",
    token_name="production-k8s",
    permission="PULL",
    expires_in_days=90,
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

**registry_id:** `str` — Registry ID.
    
</dd>
</dl>

<dl>
<dd>

**token_name:** `str` — Unique among the organization's active tokens.
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
</dd>
</dl>

<dl>
<dd>

**permission:** `typing.Optional[ContainerRegistryAccessTokenPermission]` 

- `PULL`: pull only (default).
- `PULL_PUSH`: pull and push.
    
</dd>
</dl>

<dl>
<dd>

**expires_in_days:** `typing.Optional[int]` — 1 to 365, or -1 for a token that does not expire.
    
</dd>
</dl>

<dl>
<dd>

**description:** `typing.Optional[str]` — Optional description (up to 255 characters).
    
</dd>
</dl>

<dl>
<dd>

**registry_ids:** `typing.Optional[typing.List[str]]` — Other registries in the same workspace the token may also use. The registry in the path is always included.
    
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

<details><summary><code>client.container_registry.<a href="src/ibee/container_registry/client.py">rotate_container_registry_access_token</a>(...) -> ContainerRegistryAccessTokenSecret</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Issues a new secret for an active token; the old secret stops working immediately. The new secret is returned once. Revoked or expired tokens return 409. Requires scope: container-registry.write.
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

client.container_registry.rotate_container_registry_access_token(
    registry_id="registry_id",
    token_id="token_id",
    workspace_id="710995",
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

**registry_id:** `str` — Registry ID.
    
</dd>
</dl>

<dl>
<dd>

**token_id:** `str` — Registry access token ID.
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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

<details><summary><code>client.container_registry.<a href="src/ibee/container_registry/client.py">revoke_container_registry_access_token</a>(...) -> ContainerRegistryMessage</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Revokes a token immediately. Revoking an already revoked token succeeds. Requires scope: container-registry.write.
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

client.container_registry.revoke_container_registry_access_token(
    registry_id="registry_id",
    token_id="token_id",
    workspace_id="710995",
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

**registry_id:** `str` — Registry ID.
    
</dd>
</dl>

<dl>
<dd>

**token_id:** `str` — Registry access token ID.
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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

<details><summary><code>client.container_registry.<a href="src/ibee/container_registry/client.py">list_container_registry_repositories</a>(...) -> ContainerRegistryRepositoryList</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Lists an active registry's repositories. Paged with `page` and `page_size` (at most 100). Requires scope: container-registry.read.
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

client.container_registry.list_container_registry_repositories(
    registry_id="registry_id",
    workspace_id="710995",
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

**registry_id:** `str` — Registry ID.
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
</dd>
</dl>

<dl>
<dd>

**search:** `typing.Optional[str]` — Fuzzy match on the repository name.
    
</dd>
</dl>

<dl>
<dd>

**sort:** `typing.Optional[ListContainerRegistryRepositoriesRequestSort]` — Column to sort by; prefix with `-` for descending.
    
</dd>
</dl>

<dl>
<dd>

**page:** `typing.Optional[int]` — Page number.
    
</dd>
</dl>

<dl>
<dd>

**page_size:** `typing.Optional[int]` — Number of records per page.
    
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

<details><summary><code>client.container_registry.<a href="src/ibee/container_registry/client.py">delete_container_registry_repository</a>(...) -> ContainerRegistryMessage</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Permanently deletes a repository and all of its images. Requires `confirm=true`. Requires scope: container-registry.write.
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

client.container_registry.delete_container_registry_repository(
    registry_id="registry_id",
    repository_name="repository_name",
    workspace_id="710995",
    confirm=True,
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

**registry_id:** `str` — Registry ID.
    
</dd>
</dl>

<dl>
<dd>

**repository_name:** `str` — Repository name inside the registry, for example `api`.
    
</dd>
</dl>

<dl>
<dd>

**confirm:** `bool` — Must be `true` to confirm permanent deletion.
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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

<details><summary><code>client.container_registry.<a href="src/ibee/container_registry/client.py">list_container_registry_artifacts</a>(...) -> ContainerRegistryArtifactList</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Lists the images (artifacts) in one repository with their tags and scan overview. Paged with `page` and `page_size` (at most 100). Requires scope: container-registry.read.
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

client.container_registry.list_container_registry_artifacts(
    registry_id="registry_id",
    workspace_id="710995",
    repository_name="repository_name",
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

**registry_id:** `str` — Registry ID.
    
</dd>
</dl>

<dl>
<dd>

**repository_name:** `str` — Repository name inside the registry, for example `api` or `team/api`.
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
</dd>
</dl>

<dl>
<dd>

**page:** `typing.Optional[int]` — Page number.
    
</dd>
</dl>

<dl>
<dd>

**page_size:** `typing.Optional[int]` — Number of records per page.
    
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

<details><summary><code>client.container_registry.<a href="src/ibee/container_registry/client.py">delete_container_registry_artifact</a>(...) -> ContainerRegistryMessage</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Permanently deletes one image and every tag that points to it. Requires `confirm=true`. Requires scope: container-registry.write.
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

client.container_registry.delete_container_registry_artifact(
    registry_id="registry_id",
    reference="reference",
    workspace_id="710995",
    repository_name="repository_name",
    confirm=True,
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

**registry_id:** `str` — Registry ID.
    
</dd>
</dl>

<dl>
<dd>

**reference:** `str` — Image digest (`sha256:...`) or tag.
    
</dd>
</dl>

<dl>
<dd>

**repository_name:** `str` — Repository name inside the registry, for example `api` or `team/api`.
    
</dd>
</dl>

<dl>
<dd>

**confirm:** `bool` — Must be `true` to confirm permanent deletion.
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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

<details><summary><code>client.container_registry.<a href="src/ibee/container_registry/client.py">scan_container_registry_artifact</a>(...) -> ContainerRegistryMessage</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Queues a new vulnerability scan of one image. Existing results stay visible until it completes. Requires scope: container-registry.write.
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

client.container_registry.scan_container_registry_artifact(
    registry_id="registry_id",
    reference="reference",
    workspace_id="710995",
    repository_name="repository_name",
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

**registry_id:** `str` — Registry ID.
    
</dd>
</dl>

<dl>
<dd>

**reference:** `str` — Image digest (`sha256:...`) or tag.
    
</dd>
</dl>

<dl>
<dd>

**repository_name:** `str` — Repository name inside the registry, for example `api` or `team/api`.
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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

<details><summary><code>client.container_registry.<a href="src/ibee/container_registry/client.py">get_container_registry_security_settings</a>(...) -> ContainerRegistrySecuritySettingsStatus</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Returns the vulnerability pull policy. Scanning and SBOM generation always run on push. Requires scope: container-registry.read.
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

client.container_registry.get_container_registry_security_settings(
    registry_id="registry_id",
    workspace_id="710995",
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

**registry_id:** `str` — Registry ID.
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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

<details><summary><code>client.container_registry.<a href="src/ibee/container_registry/client.py">update_container_registry_security_settings</a>(...) -> ContainerRegistrySecuritySettingsStatus</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Sets the vulnerability pull policy: `ALLOW`, or block pulls of images with findings at or above `CRITICAL`, `HIGH`, `MEDIUM` or `LOW`. Returns 202 while the change is applied. Requires scope: container-registry.write.
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

client.container_registry.update_container_registry_security_settings(
    registry_id="registry_id",
    workspace_id="710995",
    vulnerability_pull_policy="BLOCK_CRITICAL",
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

**registry_id:** `str` — Registry ID.
    
</dd>
</dl>

<dl>
<dd>

**vulnerability_pull_policy:** `ContainerRegistryPullPolicy` 
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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

<details><summary><code>client.container_registry.<a href="src/ibee/container_registry/client.py">get_container_registry_vulnerability_summary</a>(...) -> ContainerRegistryVulnerabilitySummary</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Returns the number of vulnerability findings in an active registry, by severity. Requires scope: container-registry.read.
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

client.container_registry.get_container_registry_vulnerability_summary(
    registry_id="registry_id",
    workspace_id="710995",
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

**registry_id:** `str` — Registry ID.
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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

<details><summary><code>client.container_registry.<a href="src/ibee/container_registry/client.py">list_container_registry_vulnerabilities</a>(...) -> ContainerRegistryVulnerabilityList</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Lists vulnerability findings in an active registry, with optional filters. Paged with `page` and `page_size` (at most 100). Requires scope: container-registry.read.
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

client.container_registry.list_container_registry_vulnerabilities(
    registry_id="registry_id",
    workspace_id="710995",
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

**registry_id:** `str` — Registry ID.
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
</dd>
</dl>

<dl>
<dd>

**severity:** `typing.Optional[ListContainerRegistryVulnerabilitiesRequestSeverity]` 

Return only findings of this severity.
- `Critical`
- `High`
- `Medium`
- `Low`
- `Unknown`
- `None`
    
</dd>
</dl>

<dl>
<dd>

**cve_id:** `typing.Optional[str]` — Return only findings for this CVE or advisory ID.
    
</dd>
</dl>

<dl>
<dd>

**repository_name:** `typing.Optional[str]` — Return only findings on artifacts in this repository.
    
</dd>
</dl>

<dl>
<dd>

**digest:** `typing.Optional[str]` — Return only findings on the artifact with this digest.
    
</dd>
</dl>

<dl>
<dd>

**tag:** `typing.Optional[str]` — Return only findings on artifacts carrying this tag.
    
</dd>
</dl>

<dl>
<dd>

**package:** `typing.Optional[str]` — Return only findings in this package.
    
</dd>
</dl>

<dl>
<dd>

**page:** `typing.Optional[int]` — Page number.
    
</dd>
</dl>

<dl>
<dd>

**page_size:** `typing.Optional[int]` — Number of records per page.
    
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

<details><summary><code>client.container_registry.<a href="src/ibee/container_registry/client.py">list_container_registry_sboms</a>(...) -> ContainerRegistrySbomList</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Lists the SBOMs of one repository, one per image digest. Paged with `page` and `page_size` (at most 100). Requires scope: container-registry.read.
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

client.container_registry.list_container_registry_sboms(
    registry_id="registry_id",
    workspace_id="710995",
    repository_name="repository_name",
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

**registry_id:** `str` — Registry ID.
    
</dd>
</dl>

<dl>
<dd>

**repository_name:** `str` — Repository name inside the registry, for example `api` or `team/api`.
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
</dd>
</dl>

<dl>
<dd>

**page:** `typing.Optional[int]` — Page number.
    
</dd>
</dl>

<dl>
<dd>

**page_size:** `typing.Optional[int]` — Number of records per page.
    
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

<details><summary><code>client.container_registry.<a href="src/ibee/container_registry/client.py">get_container_registry_sbom</a>(...) -> ContainerRegistrySbom</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Returns one image's SBOM components and their relationships. `q` filters components by name, version, type, license, supplier or package URL. Components are paged with `page` and `page_size` (at most 100). Requires scope: container-registry.read.
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

client.container_registry.get_container_registry_sbom(
    registry_id="registry_id",
    artifact_digest="artifact_digest",
    workspace_id="710995",
    repository_name="repository_name",
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

**registry_id:** `str` — Registry ID.
    
</dd>
</dl>

<dl>
<dd>

**artifact_digest:** `str` — Image digest, for example `sha256:4f3c...`.
    
</dd>
</dl>

<dl>
<dd>

**repository_name:** `str` — Repository name inside the registry, for example `api` or `team/api`.
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
</dd>
</dl>

<dl>
<dd>

**q:** `typing.Optional[str]` — Component search text.
    
</dd>
</dl>

<dl>
<dd>

**page:** `typing.Optional[int]` — Page number.
    
</dd>
</dl>

<dl>
<dd>

**page_size:** `typing.Optional[int]` — Number of records per page.
    
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

<details><summary><code>client.container_registry.<a href="src/ibee/container_registry/client.py">download_container_registry_sbom</a>(...) -> typing.Iterator[bytes]</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Downloads one image's full SBOM document as a JSON attachment (SPDX or CycloneDX). Requires scope: container-registry.read.
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

client.container_registry.download_container_registry_sbom(
    registry_id="registry_id",
    artifact_digest="artifact_digest",
    repository_name="x",
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

**registry_id:** `str` — Registry ID.
    
</dd>
</dl>

<dl>
<dd>

**artifact_digest:** `str` — Image digest, for example `sha256:4f3c...`.
    
</dd>
</dl>

<dl>
<dd>

**repository_name:** `str` — Repository name inside the registry, for example `api` or `team/api`.
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
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

<details><summary><code>client.container_registry.<a href="src/ibee/container_registry/client.py">get_container_registry_metrics</a>(...) -> ContainerRegistryMetrics</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Returns storage use against the plan quota and outbound bandwidth over the last 24 hours, 7 days or 30 days. Bytes are decimal (1 GB = 1,000,000,000 bytes). Requires scope: container-registry.read.
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

client.container_registry.get_container_registry_metrics(
    registry_id="registry_id",
    workspace_id="710995",
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

**registry_id:** `str` — Registry ID.
    
</dd>
</dl>

<dl>
<dd>

**workspace_id:** `typing.Optional[str]` — The positive numeric workspace ID to scope this request to. Zero, negative, and non-numeric values are rejected.
    
</dd>
</dl>

<dl>
<dd>

**range:** `typing.Optional[GetContainerRegistryMetricsRequestRange]` — Time window.
    
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

