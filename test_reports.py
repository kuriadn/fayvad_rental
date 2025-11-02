#!/usr/bin/env python
"""
Simple test script to verify report generation functionality
"""
import os
import sys
import django

# Setup Django
sys.path.append('/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fayvad_rentals.settings')
django.setup()

from reports.utils import (
    generate_financial_report,
    generate_tenant_report,
    generate_property_report,
    generate_occupancy_report,
    generate_maintenance_report,
    generate_collection_report,
    generate_revenue_report,
    export_report_json,
    export_report_csv
)

def test_reports():
    """Test all report generation functions"""
    print("Testing Report Generation Functions")
    print("=" * 50)

    # Test financial report
    print("\n1. Financial Report:")
    try:
        data = generate_financial_report()
        print(f"✅ Generated: {data}")
    except Exception as e:
        print(f"❌ Error: {e}")

    # Test tenant report
    print("\n2. Tenant Report:")
    try:
        data = generate_tenant_report()
        print(f"✅ Generated: {data}")
    except Exception as e:
        print(f"❌ Error: {e}")

    # Test property report
    print("\n3. Property Report:")
    try:
        data = generate_property_report()
        print(f"✅ Generated: {data}")
    except Exception as e:
        print(f"❌ Error: {e}")

    # Test occupancy report
    print("\n4. Occupancy Report:")
    try:
        data = generate_occupancy_report()
        print(f"✅ Generated: {data}")
    except Exception as e:
        print(f"❌ Error: {e}")

    # Test maintenance report
    print("\n5. Maintenance Report:")
    try:
        data = generate_maintenance_report()
        print(f"✅ Generated: {data}")
    except Exception as e:
        print(f"❌ Error: {e}")

    # Test collection report
    print("\n6. Collection Report:")
    try:
        data = generate_collection_report()
        print(f"✅ Generated: {data}")
    except Exception as e:
        print(f"❌ Error: {e}")

    # Test revenue report
    print("\n7. Revenue Report:")
    try:
        data = generate_revenue_report()
        print(f"✅ Generated: {data}")
    except Exception as e:
        print(f"❌ Error: {e}")

    # Test export functions
    print("\n8. Export Functions:")
    try:
        test_data = {'test': 'data', 'value': 123}
        json_export = export_report_json(test_data, 'test')
        print(f"✅ JSON Export: {json_export}")

        csv_response = export_report_csv(test_data, 'test')
        print(f"✅ CSV Export: Content-Type={csv_response.get('Content-Type')}, Filename={csv_response.get('Content-Disposition')}")
    except Exception as e:
        print(f"❌ Error: {e}")

    print("\n" + "=" * 50)
    print("Report generation test completed!")

if __name__ == '__main__':
    test_reports()
