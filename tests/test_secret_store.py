from __future__ import annotations

import inspect
import unittest

import httpx

from ibee import (
    BatchCreateSecretItem,
    Ibee,
)
from ibee.secret_store.client import AsyncSecretStoreClient, SecretStoreClient
from ibee.secret_store.raw_client import AsyncRawSecretStoreClient, RawSecretStoreClient


WORKSPACE_ID = "973318"
STORE_ID = "store-123"
SECRET_ID = "secret-456"
IDENTITY_ID = "identity-789"
SCOPE_ID = "scope-123"


class SecretStoreLifecycleTest(unittest.TestCase):
    def setUp(self) -> None:
        self.requests: list[tuple[str, str]] = []

        def handler(request: httpx.Request) -> httpx.Response:
            self.requests.append((request.method, request.url.path))
            self.assertEqual(request.url.params.get("workspace_id"), WORKSPACE_ID)

            if request.url.path == "/v1/billing/resource-eligibility":
                return httpx.Response(
                    200,
                    json={
                        "organization_id": "org-1",
                        "allowed": True,
                        "reason": "eligible",
                        "billing_mode": "PREPAID",
                        "billing_state": "CURRENT",
                        "sku_code": "SECRETMA-STD",
                        "evaluated_at": "2026-08-13T00:00:00Z",
                    },
                )

            identity = {
                "id": IDENTITY_ID,
                "organization_id": "org-1",
                "workspace_id": WORKSPACE_ID,
                "name": "payments-api",
                "auth_method": "approle",
                "openbao_role_name": "identity-role",
                "status": "active",
                "token_policy_mode": "read_write",
                "created_at": "2026-08-03T00:00:00Z",
                "updated_at": "2026-08-03T00:00:00Z",
            }
            scope = {
                "id": SCOPE_ID,
                "identity_id": IDENTITY_ID,
                "scope_type": "store",
                "store_id": STORE_ID,
                "organization_id": "org-1",
                "workspace_id": WORKSPACE_ID,
                "access_mode": "read_write",
                "allow_version_read": True,
                "allow_rollback": True,
                "allow_destroy": False,
                "created_at": "2026-08-03T00:00:00Z",
            }

            if request.url.path.endswith("/versions/1"):
                payload = {
                    "secret_id": SECRET_ID,
                    "secret_name": "database-url",
                    "version": 1,
                    "data": {"url": "redacted"},
                    "metadata": {"version": 1},
                }
            elif request.url.path.endswith("/versions"):
                payload = {
                    "secret_id": SECRET_ID,
                    "secret_name": "database-url",
                    "current_version": 2,
                    "oldest_version": 1,
                    "versions": {},
                }
            elif request.url.path.endswith("secrets:batchIngest"):
                payload = {
                    "results": [],
                    "created_count": 0,
                    "skipped_count": 1,
                    "failed_count": 0,
                }
            elif request.url.path.endswith("/permanent") or request.url.path.endswith("/destroy"):
                payload = {"status": "permanently_deleted" if request.url.path.endswith("/permanent") else "destroyed"}
            elif request.url.path.endswith("/access") or request.url.path.endswith("/rotate-secret-id"):
                payload = {
                    "identity_id": IDENTITY_ID,
                    "auth_method": "approle",
                    "role_id": "role-id",
                    "secret_id": "sensitive-test-value",
                    "secret_id_accessor": "accessor-id",
                }
            elif request.url.path.endswith("/revoke"):
                payload = {"status": "revoked"}
            elif request.url.path.endswith("/scopes") and request.method == "GET":
                payload = {"scopes": [scope], "total": 1}
            elif request.url.path.endswith("/scopes") or f"/scopes/{SCOPE_ID}" in request.url.path:
                payload = {"status": "deleted"} if request.method == "DELETE" else scope
            elif request.url.path.endswith("/identities") and request.method == "GET":
                payload = {"identities": [identity], "total": 1}
            elif f"/identities/{IDENTITY_ID}" in request.url.path or request.url.path.endswith("/identities"):
                payload = {"status": "deleted"} if request.method == "DELETE" else identity
            elif request.url.path.endswith("/value") or request.url.path.endswith("/rollback"):
                payload = {"id": SECRET_ID, "secret_name": "database-url", "data": {}, "metadata": {}}
            elif request.url.path == "/v1/secret-store/stores" and request.method == "GET":
                payload = {"stores": [], "total": 0, "page": 1, "limit": 50}
            elif request.url.path.endswith("/secrets") and request.method == "GET":
                payload = {"secrets": [], "total": 0, "page": 1, "limit": 50}
            elif "/secrets/" in request.url.path:
                payload = {"id": SECRET_ID, "status": "active"}
            else:
                payload = {"id": STORE_ID, "status": "active"}

            return httpx.Response(200, json=payload)

        transport = httpx.MockTransport(handler)
        self.http = httpx.Client(transport=transport)
        self.client = Ibee(token="test-token", base_url="https://api.example.test/v1", httpx_client=self.http)

    def tearDown(self) -> None:
        self.http.close()

    def test_all_35_secret_store_control_plane_operations_use_expected_routes(self) -> None:
        secret_store = self.client.secret_store

        secret_store.list_secret_stores(workspace_id=WORKSPACE_ID)
        secret_store.create_secret_store(workspace_id=WORKSPACE_ID, name="production")
        secret_store.get_secret_store(STORE_ID, workspace_id=WORKSPACE_ID)
        secret_store.update_secret_store(STORE_ID, workspace_id=WORKSPACE_ID, description="updated")
        secret_store.archive_secret_store(STORE_ID, workspace_id=WORKSPACE_ID)
        secret_store.unarchive_secret_store(STORE_ID, workspace_id=WORKSPACE_ID)
        secret_store.permanently_delete_secret_store(STORE_ID, workspace_id=WORKSPACE_ID)
        secret_store.list_secrets(STORE_ID, workspace_id=WORKSPACE_ID)
        secret_store.create_secret(
            STORE_ID,
            workspace_id=WORKSPACE_ID,
            secret_name="database-url",
            value={"url": "redacted"},
        )
        secret_store.batch_create_secrets(
            STORE_ID,
            workspace_id=WORKSPACE_ID,
            secrets=[BatchCreateSecretItem(secret_name="api-key", value={"key": "redacted"})],
        )
        secret_store.get_secret(SECRET_ID, workspace_id=WORKSPACE_ID)
        secret_store.delete_secret(SECRET_ID, workspace_id=WORKSPACE_ID)
        secret_store.get_secret_value(SECRET_ID, workspace_id=WORKSPACE_ID)
        secret_store.update_secret_value(SECRET_ID, workspace_id=WORKSPACE_ID, value={"key": "replacement"}, cas=1)
        secret_store.patch_secret_value(SECRET_ID, workspace_id=WORKSPACE_ID, value={"username": "ibee"})
        secret_store.undelete_secret(SECRET_ID, workspace_id=WORKSPACE_ID, versions=[1])
        secret_store.destroy_secret_versions(SECRET_ID, workspace_id=WORKSPACE_ID, versions=[1])
        secret_store.permanently_delete_secret(SECRET_ID, workspace_id=WORKSPACE_ID)
        secret_store.list_secret_versions(SECRET_ID, workspace_id=WORKSPACE_ID)
        secret_store.get_secret_version(SECRET_ID, 1, workspace_id=WORKSPACE_ID)
        secret_store.rollback_secret(SECRET_ID, workspace_id=WORKSPACE_ID, version=1)
        secret_store.list_secret_identities(STORE_ID, workspace_id=WORKSPACE_ID)
        secret_store.create_secret_identity(
            STORE_ID,
            workspace_id=WORKSPACE_ID,
            auth_method="approle",
            name="payments-api",
            token_policy_mode="read_write",
        )
        secret_store.get_secret_identity(IDENTITY_ID, workspace_id=WORKSPACE_ID)
        secret_store.update_secret_identity(
            IDENTITY_ID,
            workspace_id=WORKSPACE_ID,
            token_policy_mode="read_only",
        )
        secret_store.disable_secret_identity(IDENTITY_ID, workspace_id=WORKSPACE_ID)
        secret_store.enable_secret_identity(IDENTITY_ID, workspace_id=WORKSPACE_ID)
        secret_store.get_secret_identity_access(IDENTITY_ID, workspace_id=WORKSPACE_ID)
        secret_store.rotate_secret_identity_secret_id(IDENTITY_ID, workspace_id=WORKSPACE_ID)
        secret_store.revoke_secret_identity_sessions(IDENTITY_ID, workspace_id=WORKSPACE_ID)
        secret_store.list_secret_identity_scopes(IDENTITY_ID, workspace_id=WORKSPACE_ID)
        secret_store.create_secret_identity_scope(
            IDENTITY_ID,
            workspace_id=WORKSPACE_ID,
            store_id=STORE_ID,
            access_mode="read_write",
            allow_rollback=True,
        )
        secret_store.update_secret_identity_scope(
            SCOPE_ID,
            workspace_id=WORKSPACE_ID,
            access_mode="read_only",
        )
        secret_store.delete_secret_identity_scope(SCOPE_ID, workspace_id=WORKSPACE_ID)
        secret_store.delete_secret_identity(IDENTITY_ID, workspace_id=WORKSPACE_ID)

        self.assertEqual(
            [
                request
                for request in self.requests
                if request[1] != "/v1/billing/resource-eligibility"
            ],
            [
                ("GET", "/v1/secret-store/stores"),
                ("POST", "/v1/secret-store/stores"),
                ("GET", f"/v1/secret-store/stores/{STORE_ID}"),
                ("PATCH", f"/v1/secret-store/stores/{STORE_ID}"),
                ("POST", f"/v1/secret-store/stores/{STORE_ID}/archive"),
                ("POST", f"/v1/secret-store/stores/{STORE_ID}/unarchive"),
                ("DELETE", f"/v1/secret-store/stores/{STORE_ID}/permanent"),
                ("GET", f"/v1/secret-store/stores/{STORE_ID}/secrets"),
                ("POST", f"/v1/secret-store/stores/{STORE_ID}/secrets"),
                ("POST", f"/v1/secret-store/stores/{STORE_ID}/secrets:batchIngest"),
                ("GET", f"/v1/secret-store/secrets/{SECRET_ID}"),
                ("DELETE", f"/v1/secret-store/secrets/{SECRET_ID}"),
                ("GET", f"/v1/secret-store/secrets/{SECRET_ID}/value"),
                ("PUT", f"/v1/secret-store/secrets/{SECRET_ID}/value"),
                ("PATCH", f"/v1/secret-store/secrets/{SECRET_ID}/value"),
                ("POST", f"/v1/secret-store/secrets/{SECRET_ID}/undelete"),
                ("POST", f"/v1/secret-store/secrets/{SECRET_ID}/destroy"),
                ("DELETE", f"/v1/secret-store/secrets/{SECRET_ID}/permanent"),
                ("GET", f"/v1/secret-store/secrets/{SECRET_ID}/versions"),
                ("GET", f"/v1/secret-store/secrets/{SECRET_ID}/versions/1"),
                ("POST", f"/v1/secret-store/secrets/{SECRET_ID}/rollback"),
                ("GET", f"/v1/secret-store/stores/{STORE_ID}/identities"),
                ("POST", f"/v1/secret-store/stores/{STORE_ID}/identities"),
                ("GET", f"/v1/secret-store/identities/{IDENTITY_ID}"),
                ("PATCH", f"/v1/secret-store/identities/{IDENTITY_ID}"),
                ("POST", f"/v1/secret-store/identities/{IDENTITY_ID}/disable"),
                ("POST", f"/v1/secret-store/identities/{IDENTITY_ID}/enable"),
                ("GET", f"/v1/secret-store/identities/{IDENTITY_ID}/access"),
                ("POST", f"/v1/secret-store/identities/{IDENTITY_ID}/rotate-secret-id"),
                ("POST", f"/v1/secret-store/identities/{IDENTITY_ID}/revoke"),
                ("GET", f"/v1/secret-store/identities/{IDENTITY_ID}/scopes"),
                ("POST", f"/v1/secret-store/identities/{IDENTITY_ID}/scopes"),
                ("PATCH", f"/v1/secret-store/scopes/{SCOPE_ID}"),
                ("DELETE", f"/v1/secret-store/scopes/{SCOPE_ID}"),
                ("DELETE", f"/v1/secret-store/identities/{IDENTITY_ID}"),
            ],
        )

    def test_sync_and_async_clients_have_matching_public_operations(self) -> None:
        def operations(client_type: type) -> set[str]:
            return {
                name
                for name, member in inspect.getmembers(client_type)
                if not name.startswith("_") and (inspect.isfunction(member) or inspect.iscoroutinefunction(member))
            }

        sync_operations = operations(SecretStoreClient)
        async_operations = operations(AsyncSecretStoreClient)
        self.assertEqual(sync_operations, async_operations)
        self.assertEqual(len(sync_operations), 35)

        raw_sync_operations = operations(RawSecretStoreClient)
        raw_async_operations = operations(AsyncRawSecretStoreClient)
        self.assertEqual(raw_sync_operations, sync_operations)
        self.assertEqual(raw_async_operations, sync_operations)

        for operation in sync_operations:
            self.assertEqual(
                inspect.signature(getattr(SecretStoreClient, operation)),
                inspect.signature(getattr(AsyncSecretStoreClient, operation)),
                operation,
            )
            self.assertEqual(
                inspect.signature(getattr(RawSecretStoreClient, operation)).parameters,
                inspect.signature(getattr(AsyncRawSecretStoreClient, operation)).parameters,
                operation,
            )


if __name__ == "__main__":
    unittest.main()
