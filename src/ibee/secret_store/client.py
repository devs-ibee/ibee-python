# Hand-written (listed in .fernignore).
"""Secret Store client (``client.secret_store``) with the portal's rules.

See :mod:`ibee.secret_store_workflows` for the request flows and
:mod:`ibee.validation.secret_store` for the client-side rules.
This file is generated from one sync template; the async class mirrors it.
"""

from __future__ import annotations

import typing

from .. import secret_store_workflows as ssw
from ..compute_workflows import clean_kwargs, run_async, run_sync
from ..core.client_wrapper import AsyncClientWrapper, SyncClientWrapper
from ..core.request_options import RequestOptions
from ..types.batch_create_secret_item import BatchCreateSecretItem
from ..types.batch_create_secrets_response import BatchCreateSecretsResponse
from ..types.secret import Secret
from ..types.secret_identity import SecretIdentity
from ..types.secret_identity_access import SecretIdentityAccess
from ..types.secret_identity_action_status import SecretIdentityActionStatus
from ..types.secret_identity_list import SecretIdentityList
from ..types.secret_identity_scope import SecretIdentityScope
from ..types.secret_identity_scope_list import SecretIdentityScopeList
from ..types.secret_lifecycle_status import SecretLifecycleStatus
from ..types.secret_list import SecretList
from ..types.secret_store import SecretStore
from ..types.secret_store_list import SecretStoreList
from ..types.secret_value import SecretValue
from ..types.secret_version import SecretVersion
from ..types.secret_versions import SecretVersions
from .raw_client import AsyncRawSecretStoreClient, RawSecretStoreClient
from .types.create_secret_identity_request_auth_method import CreateSecretIdentityRequestAuthMethod
from .types.create_secret_identity_request_token_policy_mode import CreateSecretIdentityRequestTokenPolicyMode
from .types.create_secret_identity_scope_request_access_mode import CreateSecretIdentityScopeRequestAccessMode
from .types.update_secret_identity_request_token_policy_mode import UpdateSecretIdentityRequestTokenPolicyMode
from .types.update_secret_identity_scope_request_access_mode import UpdateSecretIdentityScopeRequestAccessMode

__all__ = ["AsyncSecretStoreClient", "SecretStoreClient"]

# this is used as the default value for optional parameters
OMIT = typing.cast(typing.Any, ...)


class SecretStoreClient:
    """Secret stores, secrets, application identities and identity scopes.

    Every method checks the portal's rules before any request (``IbeeValidationError``)
    and raises typed ``ApiError`` subclasses for error responses (see
    :mod:`ibee.errors.secret_store_errors`). Results are the typed models of 0.3.0.
    """

    def __init__(self, *, client_wrapper: SyncClientWrapper):
        self._client_wrapper = client_wrapper
        self._raw_client = RawSecretStoreClient(client_wrapper=client_wrapper)

    @property
    def with_raw_response(self) -> RawSecretStoreClient:
        """
        Retrieves a raw implementation of this client that returns raw responses.

        The raw client sends the arguments unchanged (only the transport rules apply:
        workspace id, 64 KiB bodies, typed errors).

        Returns
        -------
        RawSecretStoreClient
        """
        return self._raw_client

    # ------------------------------------------------------------------ stores

    def list_secret_stores(
        self,
        *,
        workspace_id: str,
        page: typing.Optional[int] = None,
        limit: typing.Optional[int] = None,
        include_archived: typing.Optional[bool] = None,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> SecretStoreList:
        """
        Lists secret stores in a workspace. Requires scope: secret-store.read.

        ``page`` is an integer >= 1 and ``limit`` an integer 1-200 (the API default is 50).
        Archived stores are listed only with ``include_archived=True`` (the portal always
        lists them, with a Restore action). Use ``list_all_secret_stores`` to fetch every page.

        Examples
        --------
        client.secret_store.list_secret_stores(workspace_id="710995", include_archived=True)
        """
        return run_sync(self._client_wrapper, ssw.list_secret_stores(**clean_kwargs(locals())), request_options)

    def list_all_secret_stores(
        self,
        *,
        workspace_id: str,
        include_archived: typing.Optional[bool] = True,
        page_size: typing.Optional[int] = None,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> typing.List[SecretStore]:
        """
        Every secret store in the workspace, fetching page after page (``page_size`` 1-200,
        default 200). Includes archived stores by default, as the portal does.
        Requires scope: secret-store.read.
        """
        return run_sync(self._client_wrapper, ssw.list_all_secret_stores(**clean_kwargs(locals())), request_options)

    def create_secret_store(
        self,
        *,
        workspace_id: str,
        name: str,
        description: typing.Optional[str] = OMIT,
        preflight_billing: typing.Optional[bool] = None,
        if_exists: typing.Optional[typing.Literal["error", "return"]] = None,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> SecretStore:
        """
        Creates a secret store in a workspace. Requires scope: secret-store.write.
        Billable (SKU ``SECRETMA-STD``): the API answers 402 ``BillingDeniedError`` when billing refuses.

        ``name`` is trimmed and must be 1-128 characters with at least one letter or digit
        (the store key is derived from it); names are unique per workspace, archived stores included.
        ``description`` is trimmed.

        ``preflight_billing=True`` first asks billing whether a ``SECRETMA-STD`` create is allowed
        (as the portal does; needs ``billing.read``, skipped with a warning without it).
        ``if_exists="return"`` returns the existing store with that name (or store key,
        compared case-insensitively) instead of raising ``ConflictError`` on 409, as the portal does.
        The create is never retried automatically.

        Examples
        --------
        client.secret_store.create_secret_store(
            workspace_id="710995", name="production-secrets", description="Secrets for production workloads"
        )
        """
        return run_sync(self._client_wrapper, ssw.create_secret_store(**clean_kwargs(locals())), request_options)

    def get_secret_store(
        self, store_id: str, *, workspace_id: str, request_options: typing.Optional[RequestOptions] = None
    ) -> SecretStore:
        """
        Gets one secret store. Requires scope: secret-store.read.

        A missing store, or one in another workspace, raises ``ResourceNotFoundError`` (HTTP 403).
        """
        return run_sync(self._client_wrapper, ssw.get_secret_store(**clean_kwargs(locals())), request_options)

    def update_secret_store(
        self,
        store_id: str,
        *,
        workspace_id: str,
        name: typing.Optional[str] = OMIT,
        description: typing.Optional[str] = OMIT,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> SecretStore:
        """
        Updates a secret store's name or description. Requires scope: secret-store.write.

        At least one of ``name`` (trimmed, 1-128 characters) or ``description`` (trimmed) is required.
        Renaming keeps the store key. An archived store raises ``StoreArchivedError`` (unarchive it first).
        """
        return run_sync(self._client_wrapper, ssw.update_secret_store(**clean_kwargs(locals())), request_options)

    def archive_secret_store(
        self, store_id: str, *, workspace_id: str, request_options: typing.Optional[RequestOptions] = None
    ) -> SecretStore:
        """
        Archives a secret store: access is blocked (runtime sessions are revoked) until it is
        unarchived. Idempotent. Requires scope: secret-store.write.
        """
        return run_sync(self._client_wrapper, ssw.archive_secret_store(**clean_kwargs(locals())), request_options)

    def unarchive_secret_store(
        self, store_id: str, *, workspace_id: str, request_options: typing.Optional[RequestOptions] = None
    ) -> SecretStore:
        """
        Restores (unarchives) a secret store. Idempotent. Requires scope: secret-store.write.
        """
        return run_sync(self._client_wrapper, ssw.unarchive_secret_store(**clean_kwargs(locals())), request_options)

    def permanently_delete_secret_store(
        self, store_id: str, *, workspace_id: str, request_options: typing.Optional[RequestOptions] = None
    ) -> SecretLifecycleStatus:
        """
        Permanently deletes a secret store with its secrets and access entries. This cannot be undone.
        Requires scope: secret-store.write.

        When a cleanup step fails the API answers 503 and the SDK raises ``DeletionIncompleteError``
        (``failed_steps``); the store stays ``deleting`` and repeating the call is safe.
        """
        return run_sync(
            self._client_wrapper, ssw.permanently_delete_secret_store(**clean_kwargs(locals())), request_options
        )

    # ----------------------------------------------------------------- secrets

    def list_secrets(
        self,
        store_id: str,
        *,
        workspace_id: str,
        q: typing.Optional[str] = None,
        page: typing.Optional[int] = None,
        limit: typing.Optional[int] = None,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> SecretList:
        """
        Lists secrets in a store (soft-deleted secrets included). Requires scope: secret-store.read.

        ``q`` is trimmed and omitted when blank (at most 128 characters; case-insensitive
        substring of the secret name). ``page`` >= 1, ``limit`` 1-200 (API default 50).
        Use ``list_all_secrets`` to fetch every page.
        """
        return run_sync(self._client_wrapper, ssw.list_secrets(**clean_kwargs(locals())), request_options)

    def list_all_secrets(
        self,
        store_id: str,
        *,
        workspace_id: str,
        q: typing.Optional[str] = None,
        page_size: typing.Optional[int] = None,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> typing.List[Secret]:
        """
        Every secret in the store, fetching page after page (``page_size`` 1-200, default 200).
        Requires scope: secret-store.read.
        """
        return run_sync(self._client_wrapper, ssw.list_all_secrets(**clean_kwargs(locals())), request_options)

    def create_secret(
        self,
        store_id: str,
        *,
        workspace_id: str,
        secret_name: str,
        value: typing.Dict[str, typing.Any],
        preflight_billing: typing.Optional[bool] = None,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> Secret:
        """
        Creates a secret in a store. Requires scope: secret-store.write.
        Billable (SKU ``SECRETMA-STD``): the API answers 402 ``BillingDeniedError`` when billing refuses.

        ``secret_name`` is trimmed and lower-cased (as the portal does) and must then be 2-64
        characters of lowercase letters, digits and hyphens, starting with a letter or digit.
        ``value`` is an object with at least one key; keys are trimmed and must not be blank,
        and string values must not be empty. The body must be at most 64 KiB.
        ``preflight_billing=True`` runs the portal's ``SECRETMA-STD`` billing check first.

        Examples
        --------
        client.secret_store.create_secret(
            "store_id", workspace_id="710995", secret_name="database-url", value={"url": "postgres://..."}
        )
        """
        return run_sync(self._client_wrapper, ssw.create_secret(**clean_kwargs(locals())), request_options)

    def batch_create_secrets(
        self,
        store_id: str,
        *,
        workspace_id: str,
        secrets: typing.Sequence[BatchCreateSecretItem],
        request_options: typing.Optional[RequestOptions] = None,
    ) -> BatchCreateSecretsResponse:
        """
        Creates up to 500 secrets in one request. Requires scope: secret-store.write.

        Each item is normalised and checked like ``create_secret`` (items may be
        ``BatchCreateSecretItem`` or dicts). Duplicate names are allowed but the API skips
        them (``duplicate_in_request``); a ``UserWarning`` is emitted. The whole body must be
        at most 64 KiB (``ibee.validation.chunk_batch_secrets`` splits larger sets).
        Per-item results are ``created``, ``skipped`` or ``failed``.
        """
        return run_sync(self._client_wrapper, ssw.batch_create_secrets(**clean_kwargs(locals())), request_options)

    def get_secret(
        self, secret_id: str, *, workspace_id: str, request_options: typing.Optional[RequestOptions] = None
    ) -> Secret:
        """
        Gets secret metadata. Requires scope: secret-store.read.
        """
        return run_sync(self._client_wrapper, ssw.get_secret(**clean_kwargs(locals())), request_options)

    def delete_secret(
        self, secret_id: str, *, workspace_id: str, request_options: typing.Optional[RequestOptions] = None
    ) -> Secret:
        """
        Soft-deletes a secret's latest version (``undelete_secret`` restores it; writing a new
        value reactivates the secret). Requires scope: secret-store.write.
        """
        return run_sync(self._client_wrapper, ssw.delete_secret(**clean_kwargs(locals())), request_options)

    def get_secret_value(
        self, secret_id: str, *, workspace_id: str, request_options: typing.Optional[RequestOptions] = None
    ) -> SecretValue:
        """
        Gets the current secret value (sensitive). Requires scope: secret-store.read.

        A soft-deleted or destroyed latest version raises ``SecretValueNotFoundError`` (404).
        """
        return run_sync(self._client_wrapper, ssw.get_secret_value(**clean_kwargs(locals())), request_options)

    def update_secret_value(
        self,
        secret_id: str,
        *,
        workspace_id: str,
        value: typing.Dict[str, typing.Any],
        cas: typing.Optional[int] = OMIT,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> SecretValue:
        """
        Replaces the secret value, creating a new version. Requires scope: secret-store.write.

        ``value`` follows the ``create_secret`` rules. ``cas`` (integer >= 0) writes only when the
        current version equals it; a mismatch raises ``CasConflictError`` (the API reports it as 502).
        Never retried automatically.
        """
        return run_sync(self._client_wrapper, ssw.update_secret_value(**clean_kwargs(locals())), request_options)

    def patch_secret_value(
        self,
        secret_id: str,
        *,
        workspace_id: str,
        value: typing.Dict[str, typing.Any],
        request_options: typing.Optional[RequestOptions] = None,
    ) -> SecretValue:
        """
        Merges keys into the secret value, creating a new version. Requires scope: secret-store.write.

        ``value`` needs at least one non-blank key; a ``None`` value deletes that key.
        """
        return run_sync(self._client_wrapper, ssw.patch_secret_value(**clean_kwargs(locals())), request_options)

    def undelete_secret(
        self,
        secret_id: str,
        *,
        workspace_id: str,
        versions: typing.Optional[typing.Sequence[int]] = None,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> Secret:
        """
        Restores soft-deleted versions. Requires scope: secret-store.write.

        ``versions`` is 1-100 integers >= 1 (duplicates removed). When omitted, the current
        version is read from ``list_secret_versions`` and restored (``delete_secret`` soft-deletes
        only the latest version); that needs secret-store.read.
        """
        return run_sync(self._client_wrapper, ssw.undelete_secret(**clean_kwargs(locals())), request_options)

    def destroy_secret_versions(
        self,
        secret_id: str,
        *,
        workspace_id: str,
        versions: typing.Sequence[int],
        request_options: typing.Optional[RequestOptions] = None,
    ) -> SecretLifecycleStatus:
        """
        Permanently destroys secret versions (irreversible). Requires scope: secret-store.write.

        ``versions`` is 1-100 integers >= 1 (duplicates removed).
        """
        return run_sync(self._client_wrapper, ssw.destroy_secret_versions(**clean_kwargs(locals())), request_options)

    def permanently_delete_secret(
        self, secret_id: str, *, workspace_id: str, request_options: typing.Optional[RequestOptions] = None
    ) -> SecretLifecycleStatus:
        """
        Permanently deletes a secret and all its versions (irreversible). Requires scope: secret-store.write.
        """
        return run_sync(
            self._client_wrapper, ssw.permanently_delete_secret(**clean_kwargs(locals())), request_options
        )

    def list_secret_versions(
        self, secret_id: str, *, workspace_id: str, request_options: typing.Optional[RequestOptions] = None
    ) -> SecretVersions:
        """
        Lists secret versions. Requires scope: secret-store.read.
        ``ibee.validation.secret_version_state`` gives the portal's status label for a version.
        """
        return run_sync(self._client_wrapper, ssw.list_secret_versions(**clean_kwargs(locals())), request_options)

    def get_secret_version(
        self, secret_id: str, version: int, *, workspace_id: str, request_options: typing.Optional[RequestOptions] = None
    ) -> SecretVersion:
        """
        Gets one secret version with its value (sensitive). Requires scope: secret-store.read.

        ``version`` must be an integer >= 1 (the API would treat 0 as the latest version).
        """
        return run_sync(self._client_wrapper, ssw.get_secret_version(**clean_kwargs(locals())), request_options)

    def rollback_secret(
        self,
        secret_id: str,
        *,
        workspace_id: str,
        version: int,
        check_target: typing.Optional[bool] = True,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> SecretValue:
        """
        Rolls a secret back to a previous version (written as a new current version).
        Requires scope: secret-store.write.

        With ``check_target`` (default) the versions are read first and, as in the portal, the
        current version, an unknown version and a destroyed version are refused. The check needs
        secret-store.read and is skipped with a warning without it.
        """
        return run_sync(self._client_wrapper, ssw.rollback_secret(**clean_kwargs(locals())), request_options)

    # -------------------------------------------------------------- identities

    def list_secret_identities(
        self, store_id: str, *, workspace_id: str, request_options: typing.Optional[RequestOptions] = None
    ) -> SecretIdentityList:
        """
        Lists application identities for a store. Requires scope: secret-store.read.
        """
        return run_sync(self._client_wrapper, ssw.list_secret_identities(**clean_kwargs(locals())), request_options)

    def create_secret_identity(
        self,
        store_id: str,
        *,
        workspace_id: str,
        auth_method: CreateSecretIdentityRequestAuthMethod,
        name: str,
        token_policy_mode: typing.Optional[CreateSecretIdentityRequestTokenPolicyMode] = OMIT,
        k8s_namespace: typing.Optional[str] = OMIT,
        k8s_service_account: typing.Optional[str] = OMIT,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> SecretIdentity:
        """
        Creates an AppRole or Kubernetes application identity with access to the store.
        Requires scope: secret-store.write.

        ``name`` is trimmed (1-128 characters, unique in the workspace, cannot be changed later).
        ``token_policy_mode`` defaults to ``read_only`` and is always sent. Kubernetes identities
        need ``k8s_namespace`` and ``k8s_service_account`` (trimmed); AppRole identities must not
        pass them. The store must be active (``StoreNotActiveError`` otherwise).
        Login details are not returned: call ``get_secret_identity_access``.
        """
        return run_sync(self._client_wrapper, ssw.create_secret_identity(**clean_kwargs(locals())), request_options)

    def get_secret_identity(
        self, identity_id: str, *, workspace_id: str, request_options: typing.Optional[RequestOptions] = None
    ) -> SecretIdentity:
        """
        Gets one application identity. Requires scope: secret-store.read.
        """
        return run_sync(self._client_wrapper, ssw.get_secret_identity(**clean_kwargs(locals())), request_options)

    def delete_secret_identity(
        self, identity_id: str, *, workspace_id: str, request_options: typing.Optional[RequestOptions] = None
    ) -> SecretIdentityActionStatus:
        """
        Deletes an application identity with its permissions and login details.
        Requires scope: secret-store.write.
        """
        return run_sync(self._client_wrapper, ssw.delete_secret_identity(**clean_kwargs(locals())), request_options)

    def update_secret_identity(
        self,
        identity_id: str,
        *,
        workspace_id: str,
        token_policy_mode: typing.Optional[UpdateSecretIdentityRequestTokenPolicyMode] = OMIT,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> SecretIdentity:
        """
        Changes an identity's token policy mode. Requires scope: secret-store.write.

        ``token_policy_mode`` (``read_only`` or ``read_write``) is required. Changing it rewrites
        every scope (``read_only`` clears rollback and destroy) and revokes active sessions.
        """
        return run_sync(self._client_wrapper, ssw.update_secret_identity(**clean_kwargs(locals())), request_options)

    def disable_secret_identity(
        self, identity_id: str, *, workspace_id: str, request_options: typing.Optional[RequestOptions] = None
    ) -> SecretIdentity:
        """
        Disables an identity until it is enabled again (sessions are revoked). Idempotent.
        Requires scope: secret-store.write.
        """
        return run_sync(self._client_wrapper, ssw.disable_secret_identity(**clean_kwargs(locals())), request_options)

    def enable_secret_identity(
        self, identity_id: str, *, workspace_id: str, request_options: typing.Optional[RequestOptions] = None
    ) -> SecretIdentity:
        """
        Enables an identity so it can authenticate again. Idempotent. Requires scope: secret-store.write.
        """
        return run_sync(self._client_wrapper, ssw.enable_secret_identity(**clean_kwargs(locals())), request_options)

    def get_secret_identity_access(
        self, identity_id: str, *, workspace_id: str, request_options: typing.Optional[RequestOptions] = None
    ) -> SecretIdentityAccess:
        """
        Gets an identity's login details (sensitive). Requires scope: secret-store.read.

        For AppRole identities every call issues a new ``secret_id`` (earlier ones stay valid),
        so this call is not idempotent and is never retried automatically. Never log the result.
        A disabled identity raises ``IdentityDisabledError``.
        """
        return run_sync(self._client_wrapper, ssw.get_secret_identity_access(**clean_kwargs(locals())), request_options)

    def rotate_secret_identity_secret_id(
        self,
        identity_id: str,
        *,
        workspace_id: str,
        check_auth_method: typing.Optional[bool] = False,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> SecretIdentityAccess:
        """
        Issues a new AppRole ``secret_id`` (sensitive). Requires scope: secret-store.write.

        The previous ``secret_id`` is not revoked. Never retried automatically.
        ``check_auth_method=True`` reads the identity first and refuses, as the portal does,
        unless it is an active AppRole identity (needs secret-store.read).
        """
        return run_sync(
            self._client_wrapper, ssw.rotate_secret_identity_secret_id(**clean_kwargs(locals())), request_options
        )

    def revoke_secret_identity_sessions(
        self, identity_id: str, *, workspace_id: str, request_options: typing.Optional[RequestOptions] = None
    ) -> SecretIdentityActionStatus:
        """
        Revokes all active sessions of an identity. Requires scope: secret-store.write.
        """
        return run_sync(
            self._client_wrapper, ssw.revoke_secret_identity_sessions(**clean_kwargs(locals())), request_options
        )

    # ------------------------------------------------------------------ scopes

    def list_secret_identity_scopes(
        self, identity_id: str, *, workspace_id: str, request_options: typing.Optional[RequestOptions] = None
    ) -> SecretIdentityScopeList:
        """
        Lists the stores an identity can access. Requires scope: secret-store.read.
        """
        return run_sync(
            self._client_wrapper, ssw.list_secret_identity_scopes(**clean_kwargs(locals())), request_options
        )

    def create_secret_identity_scope(
        self,
        identity_id: str,
        *,
        workspace_id: str,
        store_id: str,
        access_mode: typing.Optional[CreateSecretIdentityScopeRequestAccessMode] = OMIT,
        allow_version_read: typing.Optional[bool] = OMIT,
        allow_rollback: typing.Optional[bool] = OMIT,
        allow_destroy: typing.Optional[bool] = OMIT,
        check_store: typing.Optional[bool] = False,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> SecretIdentityScope:
        """
        Grants an identity access to another store. Requires scope: secret-store.write.

        Defaults (sent explicitly): ``access_mode="read_only"``, ``allow_version_read=True``,
        ``allow_rollback=False``, ``allow_destroy=False``. Rollback and destroy need ``read_write``.
        ``check_store=True`` (as the portal's store picker) reads the identity, its scopes and the
        stores first: the store must be active and not already granted, and a ``read_only``
        identity gets only ``read_only`` scopes (needs secret-store.read).
        """
        return run_sync(
            self._client_wrapper, ssw.create_secret_identity_scope(**clean_kwargs(locals())), request_options
        )

    def delete_secret_identity_scope(
        self, scope_id: str, *, workspace_id: str, request_options: typing.Optional[RequestOptions] = None
    ) -> SecretIdentityActionStatus:
        """
        Removes an identity scope: the identity loses access to that store.
        Requires scope: secret-store.write.
        """
        return run_sync(
            self._client_wrapper, ssw.delete_secret_identity_scope(**clean_kwargs(locals())), request_options
        )

    def update_secret_identity_scope(
        self,
        scope_id: str,
        *,
        workspace_id: str,
        access_mode: typing.Optional[UpdateSecretIdentityScopeRequestAccessMode] = OMIT,
        allow_version_read: typing.Optional[bool] = OMIT,
        allow_rollback: typing.Optional[bool] = OMIT,
        allow_destroy: typing.Optional[bool] = OMIT,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> SecretIdentityScope:
        """
        Updates an identity scope. Requires scope: secret-store.write.

        At least one field is required. ``access_mode="read_only"`` cannot be combined with
        ``allow_rollback=True`` or ``allow_destroy=True``; the API checks the merged scope and
        answers ``ScopeValidationError`` (422) otherwise.
        """
        return run_sync(
            self._client_wrapper, ssw.update_secret_identity_scope(**clean_kwargs(locals())), request_options
        )


class AsyncSecretStoreClient:
    """Secret stores, secrets, application identities and identity scopes.

    Every method checks the portal's rules before any request (``IbeeValidationError``)
    and raises typed ``ApiError`` subclasses for error responses (see
    :mod:`ibee.errors.secret_store_errors`). Results are the typed models of 0.3.0.
    """

    def __init__(self, *, client_wrapper: AsyncClientWrapper):
        self._client_wrapper = client_wrapper
        self._raw_client = AsyncRawSecretStoreClient(client_wrapper=client_wrapper)

    @property
    def with_raw_response(self) -> AsyncRawSecretStoreClient:
        """
        Retrieves a raw implementation of this client that returns raw responses.

        The raw client sends the arguments unchanged (only the transport rules apply:
        workspace id, 64 KiB bodies, typed errors).

        Returns
        -------
        AsyncRawSecretStoreClient
        """
        return self._raw_client

    # ------------------------------------------------------------------ stores

    async def list_secret_stores(
        self,
        *,
        workspace_id: str,
        page: typing.Optional[int] = None,
        limit: typing.Optional[int] = None,
        include_archived: typing.Optional[bool] = None,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> SecretStoreList:
        """
        Lists secret stores in a workspace. Requires scope: secret-store.read.

        ``page`` is an integer >= 1 and ``limit`` an integer 1-200 (the API default is 50).
        Archived stores are listed only with ``include_archived=True`` (the portal always
        lists them, with a Restore action). Use ``list_all_secret_stores`` to fetch every page.

        Examples
        --------
        await client.secret_store.list_secret_stores(workspace_id="710995", include_archived=True)
        """
        return await run_async(self._client_wrapper, ssw.list_secret_stores(**clean_kwargs(locals())), request_options)

    async def list_all_secret_stores(
        self,
        *,
        workspace_id: str,
        include_archived: typing.Optional[bool] = True,
        page_size: typing.Optional[int] = None,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> typing.List[SecretStore]:
        """
        Every secret store in the workspace, fetching page after page (``page_size`` 1-200,
        default 200). Includes archived stores by default, as the portal does.
        Requires scope: secret-store.read.
        """
        return await run_async(self._client_wrapper, ssw.list_all_secret_stores(**clean_kwargs(locals())), request_options)

    async def create_secret_store(
        self,
        *,
        workspace_id: str,
        name: str,
        description: typing.Optional[str] = OMIT,
        preflight_billing: typing.Optional[bool] = None,
        if_exists: typing.Optional[typing.Literal["error", "return"]] = None,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> SecretStore:
        """
        Creates a secret store in a workspace. Requires scope: secret-store.write.
        Billable (SKU ``SECRETMA-STD``): the API answers 402 ``BillingDeniedError`` when billing refuses.

        ``name`` is trimmed and must be 1-128 characters with at least one letter or digit
        (the store key is derived from it); names are unique per workspace, archived stores included.
        ``description`` is trimmed.

        ``preflight_billing=True`` first asks billing whether a ``SECRETMA-STD`` create is allowed
        (as the portal does; needs ``billing.read``, skipped with a warning without it).
        ``if_exists="return"`` returns the existing store with that name (or store key,
        compared case-insensitively) instead of raising ``ConflictError`` on 409, as the portal does.
        The create is never retried automatically.

        Examples
        --------
        await client.secret_store.create_secret_store(
            workspace_id="710995", name="production-secrets", description="Secrets for production workloads"
        )
        """
        return await run_async(self._client_wrapper, ssw.create_secret_store(**clean_kwargs(locals())), request_options)

    async def get_secret_store(
        self, store_id: str, *, workspace_id: str, request_options: typing.Optional[RequestOptions] = None
    ) -> SecretStore:
        """
        Gets one secret store. Requires scope: secret-store.read.

        A missing store, or one in another workspace, raises ``ResourceNotFoundError`` (HTTP 403).
        """
        return await run_async(self._client_wrapper, ssw.get_secret_store(**clean_kwargs(locals())), request_options)

    async def update_secret_store(
        self,
        store_id: str,
        *,
        workspace_id: str,
        name: typing.Optional[str] = OMIT,
        description: typing.Optional[str] = OMIT,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> SecretStore:
        """
        Updates a secret store's name or description. Requires scope: secret-store.write.

        At least one of ``name`` (trimmed, 1-128 characters) or ``description`` (trimmed) is required.
        Renaming keeps the store key. An archived store raises ``StoreArchivedError`` (unarchive it first).
        """
        return await run_async(self._client_wrapper, ssw.update_secret_store(**clean_kwargs(locals())), request_options)

    async def archive_secret_store(
        self, store_id: str, *, workspace_id: str, request_options: typing.Optional[RequestOptions] = None
    ) -> SecretStore:
        """
        Archives a secret store: access is blocked (runtime sessions are revoked) until it is
        unarchived. Idempotent. Requires scope: secret-store.write.
        """
        return await run_async(self._client_wrapper, ssw.archive_secret_store(**clean_kwargs(locals())), request_options)

    async def unarchive_secret_store(
        self, store_id: str, *, workspace_id: str, request_options: typing.Optional[RequestOptions] = None
    ) -> SecretStore:
        """
        Restores (unarchives) a secret store. Idempotent. Requires scope: secret-store.write.
        """
        return await run_async(self._client_wrapper, ssw.unarchive_secret_store(**clean_kwargs(locals())), request_options)

    async def permanently_delete_secret_store(
        self, store_id: str, *, workspace_id: str, request_options: typing.Optional[RequestOptions] = None
    ) -> SecretLifecycleStatus:
        """
        Permanently deletes a secret store with its secrets and access entries. This cannot be undone.
        Requires scope: secret-store.write.

        When a cleanup step fails the API answers 503 and the SDK raises ``DeletionIncompleteError``
        (``failed_steps``); the store stays ``deleting`` and repeating the call is safe.
        """
        return await run_async(
            self._client_wrapper, ssw.permanently_delete_secret_store(**clean_kwargs(locals())), request_options
        )

    # ----------------------------------------------------------------- secrets

    async def list_secrets(
        self,
        store_id: str,
        *,
        workspace_id: str,
        q: typing.Optional[str] = None,
        page: typing.Optional[int] = None,
        limit: typing.Optional[int] = None,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> SecretList:
        """
        Lists secrets in a store (soft-deleted secrets included). Requires scope: secret-store.read.

        ``q`` is trimmed and omitted when blank (at most 128 characters; case-insensitive
        substring of the secret name). ``page`` >= 1, ``limit`` 1-200 (API default 50).
        Use ``list_all_secrets`` to fetch every page.
        """
        return await run_async(self._client_wrapper, ssw.list_secrets(**clean_kwargs(locals())), request_options)

    async def list_all_secrets(
        self,
        store_id: str,
        *,
        workspace_id: str,
        q: typing.Optional[str] = None,
        page_size: typing.Optional[int] = None,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> typing.List[Secret]:
        """
        Every secret in the store, fetching page after page (``page_size`` 1-200, default 200).
        Requires scope: secret-store.read.
        """
        return await run_async(self._client_wrapper, ssw.list_all_secrets(**clean_kwargs(locals())), request_options)

    async def create_secret(
        self,
        store_id: str,
        *,
        workspace_id: str,
        secret_name: str,
        value: typing.Dict[str, typing.Any],
        preflight_billing: typing.Optional[bool] = None,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> Secret:
        """
        Creates a secret in a store. Requires scope: secret-store.write.
        Billable (SKU ``SECRETMA-STD``): the API answers 402 ``BillingDeniedError`` when billing refuses.

        ``secret_name`` is trimmed and lower-cased (as the portal does) and must then be 2-64
        characters of lowercase letters, digits and hyphens, starting with a letter or digit.
        ``value`` is an object with at least one key; keys are trimmed and must not be blank,
        and string values must not be empty. The body must be at most 64 KiB.
        ``preflight_billing=True`` runs the portal's ``SECRETMA-STD`` billing check first.

        Examples
        --------
        await client.secret_store.create_secret(
            "store_id", workspace_id="710995", secret_name="database-url", value={"url": "postgres://..."}
        )
        """
        return await run_async(self._client_wrapper, ssw.create_secret(**clean_kwargs(locals())), request_options)

    async def batch_create_secrets(
        self,
        store_id: str,
        *,
        workspace_id: str,
        secrets: typing.Sequence[BatchCreateSecretItem],
        request_options: typing.Optional[RequestOptions] = None,
    ) -> BatchCreateSecretsResponse:
        """
        Creates up to 500 secrets in one request. Requires scope: secret-store.write.

        Each item is normalised and checked like ``create_secret`` (items may be
        ``BatchCreateSecretItem`` or dicts). Duplicate names are allowed but the API skips
        them (``duplicate_in_request``); a ``UserWarning`` is emitted. The whole body must be
        at most 64 KiB (``ibee.validation.chunk_batch_secrets`` splits larger sets).
        Per-item results are ``created``, ``skipped`` or ``failed``.
        """
        return await run_async(self._client_wrapper, ssw.batch_create_secrets(**clean_kwargs(locals())), request_options)

    async def get_secret(
        self, secret_id: str, *, workspace_id: str, request_options: typing.Optional[RequestOptions] = None
    ) -> Secret:
        """
        Gets secret metadata. Requires scope: secret-store.read.
        """
        return await run_async(self._client_wrapper, ssw.get_secret(**clean_kwargs(locals())), request_options)

    async def delete_secret(
        self, secret_id: str, *, workspace_id: str, request_options: typing.Optional[RequestOptions] = None
    ) -> Secret:
        """
        Soft-deletes a secret's latest version (``undelete_secret`` restores it; writing a new
        value reactivates the secret). Requires scope: secret-store.write.
        """
        return await run_async(self._client_wrapper, ssw.delete_secret(**clean_kwargs(locals())), request_options)

    async def get_secret_value(
        self, secret_id: str, *, workspace_id: str, request_options: typing.Optional[RequestOptions] = None
    ) -> SecretValue:
        """
        Gets the current secret value (sensitive). Requires scope: secret-store.read.

        A soft-deleted or destroyed latest version raises ``SecretValueNotFoundError`` (404).
        """
        return await run_async(self._client_wrapper, ssw.get_secret_value(**clean_kwargs(locals())), request_options)

    async def update_secret_value(
        self,
        secret_id: str,
        *,
        workspace_id: str,
        value: typing.Dict[str, typing.Any],
        cas: typing.Optional[int] = OMIT,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> SecretValue:
        """
        Replaces the secret value, creating a new version. Requires scope: secret-store.write.

        ``value`` follows the ``create_secret`` rules. ``cas`` (integer >= 0) writes only when the
        current version equals it; a mismatch raises ``CasConflictError`` (the API reports it as 502).
        Never retried automatically.
        """
        return await run_async(self._client_wrapper, ssw.update_secret_value(**clean_kwargs(locals())), request_options)

    async def patch_secret_value(
        self,
        secret_id: str,
        *,
        workspace_id: str,
        value: typing.Dict[str, typing.Any],
        request_options: typing.Optional[RequestOptions] = None,
    ) -> SecretValue:
        """
        Merges keys into the secret value, creating a new version. Requires scope: secret-store.write.

        ``value`` needs at least one non-blank key; a ``None`` value deletes that key.
        """
        return await run_async(self._client_wrapper, ssw.patch_secret_value(**clean_kwargs(locals())), request_options)

    async def undelete_secret(
        self,
        secret_id: str,
        *,
        workspace_id: str,
        versions: typing.Optional[typing.Sequence[int]] = None,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> Secret:
        """
        Restores soft-deleted versions. Requires scope: secret-store.write.

        ``versions`` is 1-100 integers >= 1 (duplicates removed). When omitted, the current
        version is read from ``list_secret_versions`` and restored (``delete_secret`` soft-deletes
        only the latest version); that needs secret-store.read.
        """
        return await run_async(self._client_wrapper, ssw.undelete_secret(**clean_kwargs(locals())), request_options)

    async def destroy_secret_versions(
        self,
        secret_id: str,
        *,
        workspace_id: str,
        versions: typing.Sequence[int],
        request_options: typing.Optional[RequestOptions] = None,
    ) -> SecretLifecycleStatus:
        """
        Permanently destroys secret versions (irreversible). Requires scope: secret-store.write.

        ``versions`` is 1-100 integers >= 1 (duplicates removed).
        """
        return await run_async(self._client_wrapper, ssw.destroy_secret_versions(**clean_kwargs(locals())), request_options)

    async def permanently_delete_secret(
        self, secret_id: str, *, workspace_id: str, request_options: typing.Optional[RequestOptions] = None
    ) -> SecretLifecycleStatus:
        """
        Permanently deletes a secret and all its versions (irreversible). Requires scope: secret-store.write.
        """
        return await run_async(
            self._client_wrapper, ssw.permanently_delete_secret(**clean_kwargs(locals())), request_options
        )

    async def list_secret_versions(
        self, secret_id: str, *, workspace_id: str, request_options: typing.Optional[RequestOptions] = None
    ) -> SecretVersions:
        """
        Lists secret versions. Requires scope: secret-store.read.
        ``ibee.validation.secret_version_state`` gives the portal's status label for a version.
        """
        return await run_async(self._client_wrapper, ssw.list_secret_versions(**clean_kwargs(locals())), request_options)

    async def get_secret_version(
        self, secret_id: str, version: int, *, workspace_id: str, request_options: typing.Optional[RequestOptions] = None
    ) -> SecretVersion:
        """
        Gets one secret version with its value (sensitive). Requires scope: secret-store.read.

        ``version`` must be an integer >= 1 (the API would treat 0 as the latest version).
        """
        return await run_async(self._client_wrapper, ssw.get_secret_version(**clean_kwargs(locals())), request_options)

    async def rollback_secret(
        self,
        secret_id: str,
        *,
        workspace_id: str,
        version: int,
        check_target: typing.Optional[bool] = True,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> SecretValue:
        """
        Rolls a secret back to a previous version (written as a new current version).
        Requires scope: secret-store.write.

        With ``check_target`` (default) the versions are read first and, as in the portal, the
        current version, an unknown version and a destroyed version are refused. The check needs
        secret-store.read and is skipped with a warning without it.
        """
        return await run_async(self._client_wrapper, ssw.rollback_secret(**clean_kwargs(locals())), request_options)

    # -------------------------------------------------------------- identities

    async def list_secret_identities(
        self, store_id: str, *, workspace_id: str, request_options: typing.Optional[RequestOptions] = None
    ) -> SecretIdentityList:
        """
        Lists application identities for a store. Requires scope: secret-store.read.
        """
        return await run_async(self._client_wrapper, ssw.list_secret_identities(**clean_kwargs(locals())), request_options)

    async def create_secret_identity(
        self,
        store_id: str,
        *,
        workspace_id: str,
        auth_method: CreateSecretIdentityRequestAuthMethod,
        name: str,
        token_policy_mode: typing.Optional[CreateSecretIdentityRequestTokenPolicyMode] = OMIT,
        k8s_namespace: typing.Optional[str] = OMIT,
        k8s_service_account: typing.Optional[str] = OMIT,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> SecretIdentity:
        """
        Creates an AppRole or Kubernetes application identity with access to the store.
        Requires scope: secret-store.write.

        ``name`` is trimmed (1-128 characters, unique in the workspace, cannot be changed later).
        ``token_policy_mode`` defaults to ``read_only`` and is always sent. Kubernetes identities
        need ``k8s_namespace`` and ``k8s_service_account`` (trimmed); AppRole identities must not
        pass them. The store must be active (``StoreNotActiveError`` otherwise).
        Login details are not returned: call ``get_secret_identity_access``.
        """
        return await run_async(self._client_wrapper, ssw.create_secret_identity(**clean_kwargs(locals())), request_options)

    async def get_secret_identity(
        self, identity_id: str, *, workspace_id: str, request_options: typing.Optional[RequestOptions] = None
    ) -> SecretIdentity:
        """
        Gets one application identity. Requires scope: secret-store.read.
        """
        return await run_async(self._client_wrapper, ssw.get_secret_identity(**clean_kwargs(locals())), request_options)

    async def delete_secret_identity(
        self, identity_id: str, *, workspace_id: str, request_options: typing.Optional[RequestOptions] = None
    ) -> SecretIdentityActionStatus:
        """
        Deletes an application identity with its permissions and login details.
        Requires scope: secret-store.write.
        """
        return await run_async(self._client_wrapper, ssw.delete_secret_identity(**clean_kwargs(locals())), request_options)

    async def update_secret_identity(
        self,
        identity_id: str,
        *,
        workspace_id: str,
        token_policy_mode: typing.Optional[UpdateSecretIdentityRequestTokenPolicyMode] = OMIT,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> SecretIdentity:
        """
        Changes an identity's token policy mode. Requires scope: secret-store.write.

        ``token_policy_mode`` (``read_only`` or ``read_write``) is required. Changing it rewrites
        every scope (``read_only`` clears rollback and destroy) and revokes active sessions.
        """
        return await run_async(self._client_wrapper, ssw.update_secret_identity(**clean_kwargs(locals())), request_options)

    async def disable_secret_identity(
        self, identity_id: str, *, workspace_id: str, request_options: typing.Optional[RequestOptions] = None
    ) -> SecretIdentity:
        """
        Disables an identity until it is enabled again (sessions are revoked). Idempotent.
        Requires scope: secret-store.write.
        """
        return await run_async(self._client_wrapper, ssw.disable_secret_identity(**clean_kwargs(locals())), request_options)

    async def enable_secret_identity(
        self, identity_id: str, *, workspace_id: str, request_options: typing.Optional[RequestOptions] = None
    ) -> SecretIdentity:
        """
        Enables an identity so it can authenticate again. Idempotent. Requires scope: secret-store.write.
        """
        return await run_async(self._client_wrapper, ssw.enable_secret_identity(**clean_kwargs(locals())), request_options)

    async def get_secret_identity_access(
        self, identity_id: str, *, workspace_id: str, request_options: typing.Optional[RequestOptions] = None
    ) -> SecretIdentityAccess:
        """
        Gets an identity's login details (sensitive). Requires scope: secret-store.read.

        For AppRole identities every call issues a new ``secret_id`` (earlier ones stay valid),
        so this call is not idempotent and is never retried automatically. Never log the result.
        A disabled identity raises ``IdentityDisabledError``.
        """
        return await run_async(self._client_wrapper, ssw.get_secret_identity_access(**clean_kwargs(locals())), request_options)

    async def rotate_secret_identity_secret_id(
        self,
        identity_id: str,
        *,
        workspace_id: str,
        check_auth_method: typing.Optional[bool] = False,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> SecretIdentityAccess:
        """
        Issues a new AppRole ``secret_id`` (sensitive). Requires scope: secret-store.write.

        The previous ``secret_id`` is not revoked. Never retried automatically.
        ``check_auth_method=True`` reads the identity first and refuses, as the portal does,
        unless it is an active AppRole identity (needs secret-store.read).
        """
        return await run_async(
            self._client_wrapper, ssw.rotate_secret_identity_secret_id(**clean_kwargs(locals())), request_options
        )

    async def revoke_secret_identity_sessions(
        self, identity_id: str, *, workspace_id: str, request_options: typing.Optional[RequestOptions] = None
    ) -> SecretIdentityActionStatus:
        """
        Revokes all active sessions of an identity. Requires scope: secret-store.write.
        """
        return await run_async(
            self._client_wrapper, ssw.revoke_secret_identity_sessions(**clean_kwargs(locals())), request_options
        )

    # ------------------------------------------------------------------ scopes

    async def list_secret_identity_scopes(
        self, identity_id: str, *, workspace_id: str, request_options: typing.Optional[RequestOptions] = None
    ) -> SecretIdentityScopeList:
        """
        Lists the stores an identity can access. Requires scope: secret-store.read.
        """
        return await run_async(
            self._client_wrapper, ssw.list_secret_identity_scopes(**clean_kwargs(locals())), request_options
        )

    async def create_secret_identity_scope(
        self,
        identity_id: str,
        *,
        workspace_id: str,
        store_id: str,
        access_mode: typing.Optional[CreateSecretIdentityScopeRequestAccessMode] = OMIT,
        allow_version_read: typing.Optional[bool] = OMIT,
        allow_rollback: typing.Optional[bool] = OMIT,
        allow_destroy: typing.Optional[bool] = OMIT,
        check_store: typing.Optional[bool] = False,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> SecretIdentityScope:
        """
        Grants an identity access to another store. Requires scope: secret-store.write.

        Defaults (sent explicitly): ``access_mode="read_only"``, ``allow_version_read=True``,
        ``allow_rollback=False``, ``allow_destroy=False``. Rollback and destroy need ``read_write``.
        ``check_store=True`` (as the portal's store picker) reads the identity, its scopes and the
        stores first: the store must be active and not already granted, and a ``read_only``
        identity gets only ``read_only`` scopes (needs secret-store.read).
        """
        return await run_async(
            self._client_wrapper, ssw.create_secret_identity_scope(**clean_kwargs(locals())), request_options
        )

    async def delete_secret_identity_scope(
        self, scope_id: str, *, workspace_id: str, request_options: typing.Optional[RequestOptions] = None
    ) -> SecretIdentityActionStatus:
        """
        Removes an identity scope: the identity loses access to that store.
        Requires scope: secret-store.write.
        """
        return await run_async(
            self._client_wrapper, ssw.delete_secret_identity_scope(**clean_kwargs(locals())), request_options
        )

    async def update_secret_identity_scope(
        self,
        scope_id: str,
        *,
        workspace_id: str,
        access_mode: typing.Optional[UpdateSecretIdentityScopeRequestAccessMode] = OMIT,
        allow_version_read: typing.Optional[bool] = OMIT,
        allow_rollback: typing.Optional[bool] = OMIT,
        allow_destroy: typing.Optional[bool] = OMIT,
        request_options: typing.Optional[RequestOptions] = None,
    ) -> SecretIdentityScope:
        """
        Updates an identity scope. Requires scope: secret-store.write.

        At least one field is required. ``access_mode="read_only"`` cannot be combined with
        ``allow_rollback=True`` or ``allow_destroy=True``; the API checks the merged scope and
        answers ``ScopeValidationError`` (422) otherwise.
        """
        return await run_async(
            self._client_wrapper, ssw.update_secret_identity_scope(**clean_kwargs(locals())), request_options
        )
