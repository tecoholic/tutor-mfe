#!/usr/bin/env python
"""
Test script for MFE_DEV_MODE feature.
Tests the MFEMountData class with dev mode configuration.
"""

import sys
import os

# Add the tutormfe module to the path
sys.path.insert(0, os.path.dirname(__file__))

from tutormfe.plugin import MFEMountData


def test_mfe_mount_data_without_dev_mode():
    """Test default behavior without MFE_DEV_MODE."""
    mfe_data = MFEMountData(mounts=[], dev_mode_apps=[])
    
    dev_services = list(mfe_data.get_dev_mode_services())
    print("✓ Test 1 (no dev mode): get_dev_mode_services() returns empty list")
    assert len(dev_services) == 0, "Expected empty list when no dev mode configured"


def test_mfe_mount_data_with_dev_mode_unmounted():
    """Test dev mode with unmounted MFEs."""
    # Simulate unmounted MFEs
    mfe_data = MFEMountData(mounts=[], dev_mode_apps=["profile", "authn"])
    
    # Create mock unmounted MFEs
    mfe_data.unmounted = [
        ("profile", {"port": 1995}),
        ("authn", {"port": 1999}),
        ("learning", {"port": 2000}),
    ]
    
    dev_services = list(mfe_data.get_dev_mode_services())
    dev_service_names = [name for name, _, _ in dev_services]
    
    print("✓ Test 2 (dev mode unmounted): Correct MFEs in dev mode")
    assert "profile" in dev_service_names, "profile should be in dev services"
    assert "authn" in dev_service_names, "authn should be in dev services"
    assert "learning" not in dev_service_names, "learning should NOT be in dev services"
    assert len(dev_services) == 2, f"Expected 2 dev services, got {len(dev_services)}"


def test_mfe_mount_data_with_mounted_mfes():
    """Test that mounted MFEs are always included regardless of dev_mode_apps."""
    mfe_data = MFEMountData(mounts=[], dev_mode_apps=["authn"])
    
    # Create mock mounted and unmounted MFEs
    mfe_data.mounted = [
        ("profile", {"port": 1995}, ["/path/to/profile"]),
    ]
    mfe_data.unmounted = [
        ("authn", {"port": 1999}),
        ("learning", {"port": 2000}),
    ]
    
    dev_services = list(mfe_data.get_dev_mode_services())
    dev_service_names = [name for name, _, _ in dev_services]
    
    print("✓ Test 3 (mounted MFEs): Mounted MFEs always included + dev mode list")
    assert "profile" in dev_service_names, "profile (mounted) should always be in dev services"
    assert "authn" in dev_service_names, "authn (in dev_mode_apps) should be in dev services"
    assert "learning" not in dev_service_names, "learning should NOT be in dev services"
    assert len(dev_services) == 2, f"Expected 2 dev services, got {len(dev_services)}"


def test_mfe_mount_data_mount_preservation():
    """Test that mounted MFEs preserve their mounts in dev services."""
    mfe_data = MFEMountData(mounts=[], dev_mode_apps=["authn"])
    
    # Create mock mounted and unmounted MFEs
    mfe_data.mounted = [
        ("profile", {"port": 1995}, ["/host/profile:/openedx/app"]),
    ]
    mfe_data.unmounted = [
        ("authn", {"port": 1999}),
    ]
    
    dev_services = list(mfe_data.get_dev_mode_services())
    
    # Check mounted MFE has mounts
    profile_service = next((s for s in dev_services if s[0] == "profile"), None)
    assert profile_service is not None, "profile should be in dev services"
    assert len(profile_service[2]) > 0, "profile should have mounts"
    assert profile_service[2][0] == "/host/profile:/openedx/app", "mount should be preserved"
    
    # Check unmounted MFE in dev mode has no mounts
    authn_service = next((s for s in dev_services if s[0] == "authn"), None)
    assert authn_service is not None, "authn should be in dev services"
    assert len(authn_service[2]) == 0, "authn (unmounted) should have no mounts"
    
    print("✓ Test 4 (mount preservation): Mounted MFEs keep mounts, unmounted MFEs have no mounts")


def test_unmounted_mfes_calculation():
    """Test the unmounted MFEs list for shared service."""
    mfe_data = MFEMountData(mounts=[], dev_mode_apps=["profile", "authn"])
    
    # Create mock unmounted MFEs
    mfe_data.unmounted = [
        ("profile", {"port": 1995}),
        ("authn", {"port": 1999}),
        ("learning", {"port": 2000}),
        ("gradebook", {"port": 1994}),
    ]
    
    # Simulate the Jinja2 calculation from the patch
    other_unmounted = [app for app, _ in mfe_data.unmounted if app not in mfe_data.dev_mode_apps]
    
    print("✓ Test 5 (shared service calculation): Correctly identifies MFEs for shared service")
    assert "learning" in other_unmounted, "learning should be in shared service"
    assert "gradebook" in other_unmounted, "gradebook should be in shared service"
    assert "profile" not in other_unmounted, "profile should NOT be in shared service"
    assert "authn" not in other_unmounted, "authn should NOT be in shared service"
    assert len(other_unmounted) == 2, f"Expected 2 unmounted MFEs for shared service, got {len(other_unmounted)}"


if __name__ == "__main__":
    print("\n" + "="*70)
    print("Testing MFE_DEV_MODE Feature Implementation")
    print("="*70 + "\n")
    
    try:
        test_mfe_mount_data_without_dev_mode()
        test_mfe_mount_data_with_dev_mode_unmounted()
        test_mfe_mount_data_with_mounted_mfes()
        test_mfe_mount_data_mount_preservation()
        test_unmounted_mfes_calculation()
        
        print("\n" + "="*70)
        print("All tests passed! ✓")
        print("="*70 + "\n")
        sys.exit(0)
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
