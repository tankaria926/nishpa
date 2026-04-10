from django.core.management.base import BaseCommand
from purchase_order.models import Vendor


class Command(BaseCommand):
    help = 'Populate sample vendors for purchase order system'

    def handle(self, *args, **options):
        vendors_data = [
            {
                'name': 'Global Supplies Co.',
                'email': 'info@globalsupplies.com',
                'phone': '+1-800-123-4567',
                'address': '123 Commerce Street',
                'city': 'New York',
                'state': 'NY',
                'country': 'United States',
                'postal_code': '10001',
                'tax_id': 'TAX123456789',
                'bank_name': 'First National Bank',
                'bank_account': '1234567890',
                'contact_person': 'John Anderson',
            },
            {
                'name': 'Premium Materials Ltd.',
                'email': 'sales@premiummaterials.com',
                'phone': '+44-20-7946-0958',
                'address': '456 Industrial Road',
                'city': 'London',
                'state': 'London',
                'country': 'United Kingdom',
                'postal_code': 'SW1A 1AA',
                'tax_id': 'GB123456789',
                'bank_name': 'HSBC UK',
                'bank_account': '98765432101',
                'contact_person': 'Sarah Miller',
            },
            {
                'name': 'Asia Tech Distributors',
                'email': 'contact@asiatechdist.com',
                'phone': '+65-6789-0123',
                'address': '789 Business Hub',
                'city': 'Singapore',
                'state': 'Singapore',
                'country': 'Singapore',
                'postal_code': '018956',
                'tax_id': 'SG987654321',
                'bank_name': 'DBS Bank',
                'bank_account': '5555666677778888',
                'contact_person': 'Michael Wong',
            },
            {
                'name': 'European Quality Imports',
                'email': 'procurement@euquality.de',
                'phone': '+49-30-1234-5678',
                'address': '321 Trade Center',
                'city': 'Berlin',
                'state': 'Berlin',
                'country': 'Germany',
                'postal_code': '10115',
                'tax_id': 'DE456789123',
                'bank_name': 'Deutsche Bank',
                'bank_account': '111222333444555',
                'contact_person': 'Klaus Mueller',
            },
            {
                'name': 'India Exports International',
                'email': 'export@indiaexp.in',
                'phone': '+91-22-1234-5678',
                'address': '654 Shipping Lane',
                'city': 'Mumbai',
                'state': 'Maharashtra',
                'country': 'India',
                'postal_code': '400001',
                'tax_id': 'IN123456789AB',
                'bank_name': 'ICICI Bank',
                'bank_account': '9999888877776666',
                'contact_person': 'Rajesh Patel',
            },
            {
                'name': 'Reliable Components Corp.',
                'email': 'order@reliablecomp.com',
                'phone': '+1-713-555-0100',
                'address': '987 Industrial Park',
                'city': 'Houston',
                'state': 'TX',
                'country': 'United States',
                'postal_code': '77001',
                'tax_id': 'TAX987654321',
                'bank_name': 'Chase Bank',
                'bank_account': '4444333322221111',
                'contact_person': 'James Wilson',
            },
        ]

        created_count = 0
        for vendor_data in vendors_data:
            vendor, created = Vendor.objects.get_or_create(
                email=vendor_data['email'],
                defaults=vendor_data
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created vendor: {vendor.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'⚠ Vendor already exists: {vendor.name}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\n✓ Successfully populated {created_count} new vendors'
            )
        )
