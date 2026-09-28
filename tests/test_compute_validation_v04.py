"""Pure portal rules in ibee.validation (compute, recovery, billing SKUs)."""

from __future__ import annotations

import datetime as dt

import pytest

from ibee.validation import (
    IbeeValidationError,
    assert_vm_action_allowed,
    billing_catalog_for_term,
    build_vm_billing_catalog,
    default_billing_term,
    expand_batch_names,
    normalize_billing_options,
    normalize_vpc_connectivity_type,
    recovery_default_vm_name,
    recovery_min_root_disk_gb,
    recovery_target_volume_names,
    resolve_delete_public_ip_action,
    validate_billing_catalog,
    validate_compute_operation_id,
    validate_next_run_at,
    validate_ssh_public_key,
    validate_vm_id,
    validate_vm_name,
    with_attached_billing_skus,
)


def test_ids() -> None:
    assert validate_vm_id(" 0123456789ABCDEF01234567 ") == "0123456789ABCDEF01234567"
    for bad in ("all", "vm-1", "0123456789abcdef0123456", 12, None):
        with pytest.raises(IbeeValidationError):
            validate_vm_id(bad)
    assert validate_compute_operation_id("op_0123456789abcdef01234567")
    with pytest.raises(IbeeValidationError):
        validate_compute_operation_id("op-0123456789abcdef01234567")


def test_names_and_batches() -> None:
    assert validate_vm_name(" web-01 ") == "web-01"
    with pytest.raises(IbeeValidationError):
        validate_vm_name("web 01")
    assert expand_batch_names("web", 1) == ["web"]
    assert expand_batch_names("web", 3) == ["web-1", "web-2", "web-3"]
    assert expand_batch_names("web", 2, ["api", None]) == ["api", "web-2"]
    for count in (0, 6, True):
        with pytest.raises(IbeeValidationError):
            expand_batch_names("web", count)
    with pytest.raises(IbeeValidationError):
        expand_batch_names("web", 2, ["A", "a"])
    with pytest.raises(IbeeValidationError):
        expand_batch_names("web", 2, reserved_ip=True)


def test_ssh_public_keys() -> None:
    assert validate_ssh_public_key("  sk-ssh-ed25519@openssh.com AAAA+/= me@laptop ")
    for bad in ("ssh-dss AAAA", "ssh-rsa", "ssh-rsa AAA*", "ssh-rsa AAAA\nx", "-----BEGIN RSA PRIVATE KEY-----", 'from="x" ssh-rsa AAAA'):
        with pytest.raises(IbeeValidationError):
            validate_ssh_public_key(bad)


def test_billing_catalog_rules() -> None:
    result = validate_billing_catalog({"skuId": 1, "skuCode": " vm-a ", "attachedSkus": {"Reserved-IP": {"sku_id": 2, "sku_code": "rip"}}})
    assert result["sku_code"] == "VM-A" and result["attached_skus"] == {"reserved_ip": {"sku_id": 2, "sku_code": "RIP"}}
    for bad in (
        None,
        [],
        {"sku_code": "X"},
        {"sku_id": " ", "sku_code": "X"},
        {"sku_id": 1, "sku_code": "  "},
        {"sku_id": 1, "sku_code": "rootdisk-50"},
        {"sku_id": 1, "sku_code": "X", "attached_skus": {"root-disk": {"sku_id": 1, "sku_code": "Y"}}},
        {"sku_id": 1, "sku_code": "X", "attached_skus": "nope"},
    ):
        with pytest.raises(IbeeValidationError):
            validate_billing_catalog(bad)
    with pytest.raises(IbeeValidationError):
        validate_billing_catalog({"sku_id": 1, "sku_code": "X", "product_code": "block_storage"}, expected_product="snapshot_storage")
    with pytest.raises(IbeeValidationError):
        with_attached_billing_skus({"sku_id": 1, "sku_code": "X"}, {"rootvolume": {"sku_id": 1, "sku_code": "Y"}})


def test_billing_terms_match_the_portal_port() -> None:
    options = normalize_billing_options(
        [
            {"billing_interval": "YEARLY", "unit_price_minor": "1000", "commitment_period": "bogus"},
            {"billing_interval": "WEEKLY", "unit_price_minor": 1},
            {"billing_interval": "HOURLY", "unit_price_minor": None},
        ]
    )
    assert options == [{"billing_interval": "YEARLY", "unit_price_minor": 1000, "committed": False, "commitment_period": "YEARLY"}]
    assert default_billing_term({"billing_options": options}) == "YEARLY"
    assert default_billing_term({"billing_options": []}) is None
    assert billing_catalog_for_term({"sku_id": 1}, {"billing_interval": "HOURLY", "committed": False, "commitment_period": "HOURLY", "unit_price_minor": 5, "discount_percent": 0}) == {
        "sku_id": 1,
        "billing_interval": "HOURLY",
        "committed": False,
        "commitment_period": "HOURLY",
        "discount_percent": 0,
        "unit_price_minor": 5,
    }
    # A plan without billing options is sent unchanged (billed hourly by the API).
    assert build_vm_billing_catalog({"sku_id": 1, "sku_code": "a"}, term=None) == {"sku_id": 1, "sku_code": "A", "attached_skus": {}}
    with pytest.raises(IbeeValidationError):
        build_vm_billing_catalog(None, term=None)


def test_state_matrix() -> None:
    assert_vm_action_allowed({"status": "stopped"}, "start")
    assert_vm_action_allowed({"status": "error"}, "resize")
    for record, action in (({"status": "running"}, "start"), ({"status": "stopped"}, "reboot"), ({"status": "deleted"}, "delete"), ({"status": "restoring"}, "snapshot")):
        with pytest.raises(IbeeValidationError):
            assert_vm_action_allowed(record, action)


def test_delete_public_ip_decision() -> None:
    assert resolve_delete_public_ip_action({"public_ip": " "}) is None
    assert resolve_delete_public_ip_action({"public_ip": "1.1.1.1", "retained_reserved_public_ip_id": "r"}) is None
    assert resolve_delete_public_ip_action({"public_ip": "1.1.1.1"}) == {"public_ip_action": "release"}
    with pytest.raises(IbeeValidationError) as info:
        resolve_delete_public_ip_action(
            {"public_ip": "1.1.1.1", "name": "web"}, public_ip_action="reserve", reserved_ip_billing_catalog={"sku_id": 1, "sku_code": "R"}
        )
    assert info.value.code == "vm_site_unavailable"
    with pytest.raises(IbeeValidationError):
        resolve_delete_public_ip_action({"public_ip": "1.1.1.1", "site_id": "s"}, public_ip_action="keep")
    body = resolve_delete_public_ip_action(
        {"public_ip": "1.1.1.1", "site_id": "s", "name": "n" * 200},
        public_ip_action="reserve",
        reserved_ip_billing_catalog={"sku_id": 1, "sku_code": "r"},
    )
    assert len(body["reserved_ip_label"]) == 120


def test_vpc_connectivity_normalisation() -> None:
    assert [normalize_vpc_connectivity_type(v) for v in ("NAT", "nat_gateway", "private", "public", None)] == [
        "nat_gateway",
        "nat_gateway",
        "private",
        "public",
        "public",
    ]


def test_recovery_naming_and_min_root_disk() -> None:
    manifest = [
        {"source_volume_id": "root", "role": "root", "size_gb": 50.06},
        {"source_volume_id": "d1", "volume_name": "vol"},
        {"source_volume_id": "d2", "role": "data", "display_name": " "},
    ]
    assert recovery_min_root_disk_gb(manifest) == 50
    assert recovery_min_root_disk_gb([{"source_volume_id": "r", "display_size_gb": 101}]) == 100
    assert recovery_min_root_disk_gb([{"source_volume_id": "r", "size_gb": 40}]) == 40
    created = dt.datetime(2026, 1, 2, 23, 0, tzinfo=dt.timezone(dt.timedelta(hours=-5)))
    assert recovery_default_vm_name("", "backup", created) == "vm-backup-restored-20260103"
    assert recovery_target_volume_names(manifest, "snapshot", "2026-09-01T00:00:00Z") == {
        "d1": "vol-snapshot-restored-20260901",
        "d2": "d2-snapshot-restored-20260901",
    }


def test_next_run_at_must_be_aware() -> None:
    assert validate_next_run_at("2026-10-01T02:30:00Z").tzinfo is not None
    for bad in (dt.datetime(2026, 10, 1), "2026-10-01T02:30:00", "tomorrow"):
        with pytest.raises(IbeeValidationError):
            validate_next_run_at(bad)
