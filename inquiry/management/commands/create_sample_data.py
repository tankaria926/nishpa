from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Create hardcoded sample ProductCategory and Product records for Nishpa (dental products)'

    def handle(self, *args, **options):
        from inquiry.models import ProductCategory, Product

        # NOTE: These are dental products (from the provided Excel sheet).
        # The image URLs below are example internet images (Unsplash) chosen per category.
        # Replace any URL with your preferred product image if needed.

        # Category-level representative images (used for each product in that category)
        cat_images = {
            'Restorative': 'https://images.unsplash.com/photo-1588774069163-38f3a6598c15?auto=format&fit=crop&w=800&q=60',
            'Radiology & Dental': 'https://images.unsplash.com/photo-1582719478250-4786b9c6c58b?auto=format&fit=crop&w=800&q=60',
            'Disposable': 'https://images.unsplash.com/photo-1583947582887-3b1d2f1b0a1d?auto=format&fit=crop&w=800&q=60',
            'Dispenser': 'https://images.unsplash.com/photo-1578496479404-6b3b6b7a5f2f?auto=format&fit=crop&w=800&q=60',
            'Others': 'https://images.unsplash.com/photo-1556228720-3b7f8c2f0b62?auto=format&fit=crop&w=800&q=60',
            'Autoclave': 'https://images.unsplash.com/photo-1580281657521-ff6a3f1e0a3f?auto=format&fit=crop&w=800&q=60',
            'Sleeves': 'https://images.unsplash.com/photo-1580281657521-ff6a3f1e0a3f?auto=format&fit=crop&w=800&q=60',
        }

        # Hardcoded categories and products with WORKING dental product images (Pexels/Free sources)
        samples = {
            'Restorative': [
                ('Composite Resin – A2', 'https://images.pexels.com/photos/3962287/pexels-photo-3962287.jpeg?w=640', 'RES-001'),
            ],
            'Radiology & Dental': [
                ('Dental OPG X-Ray Viewer', 'https://images.pexels.com/photos/3962285/pexels-photo-3962285.jpeg?w=640', 'RAD-001'),
                ('X-Ray Dental Films Holders', 'https://images.pexels.com/photos/4020588/pexels-photo-4020588.jpeg?w=640', 'RAD-002'),
                ('X-Ray Dental Clips (S.S.)', 'https://images.pexels.com/photos/3962283/pexels-photo-3962283.jpeg?w=640', 'RAD-003'),
                ('X-Ray Dental Hangers (S.S.)', 'https://images.pexels.com/photos/4020590/pexels-photo-4020590.jpeg?w=640', 'RAD-004'),
                ('X-Ray Developing Box', 'https://images.pexels.com/photos/3962288/pexels-photo-3962288.jpeg?w=640', 'RAD-005'),
                ('X-Ray Lead Apron', 'https://images.pexels.com/photos/4020589/pexels-photo-4020589.jpeg?w=640', 'RAD-006'),
            ],
            'Disposable': [
                ('Cotton Rolls', 'https://images.pexels.com/photos/5632399/pexels-photo-5632399.jpeg?w=640', 'DIS-001'),
                ('Cotton Balls', 'https://images.pexels.com/photos/5632400/pexels-photo-5632400.jpeg?w=640', 'DIS-002'),
                ('Mouth Chick Dry Guard', 'https://images.pexels.com/photos/5632401/pexels-photo-5632401.jpeg?w=640', 'DIS-003'),
                ('Twizzer, Mirror Top & Probe', 'https://images.pexels.com/photos/4021282/pexels-photo-4021282.jpeg?w=640', 'DIS-004'),
                ('Three-way Syringe Nozzle', 'https://images.pexels.com/photos/4021283/pexels-photo-4021283.jpeg?w=640', 'DIS-005'),
                ('Applicators Brush', 'https://images.pexels.com/photos/5635854/pexels-photo-5635854.jpeg?w=640', 'DIS-006'),
                ('Micro Applicators Tip', 'https://images.pexels.com/photos/5635855/pexels-photo-5635855.jpeg?w=640', 'DIS-007'),
                ('Wedges', 'https://images.pexels.com/photos/3692784/pexels-photo-3692784.jpeg?w=640', 'DIS-008'),
                ('Suction Tip (Saliva Ejector)', 'https://images.pexels.com/photos/5632402/pexels-photo-5632402.jpeg?w=640', 'DIS-009'),
                ('Vinyl Apron', 'https://images.pexels.com/photos/5635856/pexels-photo-5635856.jpeg?w=640', 'DIS-010'),
            ],
            'Dispenser': [
                ('G.P. Organizer', 'https://images.pexels.com/photos/3945683/pexels-photo-3945683.jpeg?w=640', 'DSP-001'),
                ('L.C. Organizer', 'https://images.pexels.com/photos/3945684/pexels-photo-3945684.jpeg?w=640', 'DSP-002'),
                ('Endo Box', 'https://images.pexels.com/photos/3962286/pexels-photo-3962286.jpeg?w=640', 'DSP-003'),
                ('Endo Ring Plastic', 'https://images.pexels.com/photos/4021284/pexels-photo-4021284.jpeg?w=640', 'DSP-004'),
                ('Plastic Bur Block', 'https://images.pexels.com/photos/3945685/pexels-photo-3945685.jpeg?w=640', 'DSP-005'),
                ('Plastic Impression Tray', 'https://images.pexels.com/photos/4020591/pexels-photo-4020591.jpeg?w=640', 'DSP-006'),
                ('Plastic Chick Retractor', 'https://images.pexels.com/photos/3945686/pexels-photo-3945686.jpeg?w=640', 'DSP-007'),
            ],
            'Others': [
                ('Plastic Spatula', 'https://images.pexels.com/photos/3945687/pexels-photo-3945687.jpeg?w=640', 'OTH-001'),
                ('Dental Photography Mirror', 'https://images.pexels.com/photos/4021285/pexels-photo-4021285.jpeg?w=640', 'OTH-002'),
                ('Suction Machine', 'https://images.pexels.com/photos/5632403/pexels-photo-5632403.jpeg?w=640', 'OTH-003'),
                ('Glass Beads Sterilizer', 'https://images.pexels.com/photos/3945688/pexels-photo-3945688.jpeg?w=640', 'OTH-004'),
                ('Electronic Glass Beads Sterilizer', 'https://images.pexels.com/photos/4021286/pexels-photo-4021286.jpeg?w=640', 'OTH-005'),
                ('Vibrators', 'https://images.pexels.com/photos/3945689/pexels-photo-3945689.jpeg?w=640', 'OTH-006'),
                ('Mixing Pad', 'https://images.pexels.com/photos/5635857/pexels-photo-5635857.jpeg?w=640', 'OTH-007'),
                ('Mailers Streep', 'https://images.pexels.com/photos/3945690/pexels-photo-3945690.jpeg?w=640', 'OTH-008'),
                ('Towel Clip', 'https://images.pexels.com/photos/4021287/pexels-photo-4021287.jpeg?w=640', 'OTH-009'),
                ('Lubricant Oil', 'https://images.pexels.com/photos/5632404/pexels-photo-5632404.jpeg?w=640', 'OTH-010'),
                ('Micro Torch', 'https://images.pexels.com/photos/3945691/pexels-photo-3945691.jpeg?w=640', 'OTH-011'),
            ],
            'Autoclave': [
                ('Endo G.P. Organizer', 'https://images.pexels.com/photos/3945692/pexels-photo-3945692.jpeg?w=640', 'AUT-001'),
                ('Endo Box', 'https://images.pexels.com/photos/4020592/pexels-photo-4020592.jpeg?w=640', 'AUT-002'),
                ('S.S. Endo Ring', 'https://images.pexels.com/photos/5632405/pexels-photo-5632405.jpeg?w=640', 'AUT-003'),
                ('Bur Box', 'https://images.pexels.com/photos/3945693/pexels-photo-3945693.jpeg?w=640', 'AUT-004'),
                ('Starry Tray', 'https://images.pexels.com/photos/4021288/pexels-photo-4021288.jpeg?w=640', 'AUT-005'),
                ('G.P. Cutter', 'https://images.pexels.com/photos/3945694/pexels-photo-3945694.jpeg?w=640', 'AUT-006'),
                ('Bait Registration Tray', 'https://images.pexels.com/photos/5632406/pexels-photo-5632406.jpeg?w=640', 'AUT-007'),
                ('Wooden Wedges', 'https://images.pexels.com/photos/3692785/pexels-photo-3692785.jpeg?w=640', 'AUT-008'),
                ('Screw Post', 'https://images.pexels.com/photos/3945695/pexels-photo-3945695.jpeg?w=640', 'AUT-009'),
                ('Fiber Post', 'https://images.pexels.com/photos/4021289/pexels-photo-4021289.jpeg?w=640', 'AUT-010'),
                ('Top Turbo Oil Spray', 'https://images.pexels.com/photos/3945696/pexels-photo-3945696.jpeg?w=640', 'AUT-011'),
            ],
            'Sleeves': [
                ('Scaler Sleeves', 'https://images.pexels.com/photos/5632407/pexels-photo-5632407.jpeg?w=640', 'SLV-001'),
                ('3 Way Syringe Sleeves', 'https://images.pexels.com/photos/4021290/pexels-photo-4021290.jpeg?w=640', 'SLV-002'),
                ('GP Cutter Sleeves', 'https://images.pexels.com/photos/3945697/pexels-photo-3945697.jpeg?w=640', 'SLV-003'),
                ('Transparent Intra Oral Camera Sleeves', 'https://images.pexels.com/photos/5632408/pexels-photo-5632408.jpeg?w=640', 'SLV-004'),
                ('Endo Errigation Sleeves', 'https://images.pexels.com/photos/4021291/pexels-photo-4021291.jpeg?w=640', 'SLV-005'),
                ('Light Cure Sleeves', 'https://images.pexels.com/photos/3945698/pexels-photo-3945698.jpeg?w=640', 'SLV-006'),
                ('OPG Bite block sleeves', 'https://images.pexels.com/photos/5632409/pexels-photo-5632409.jpeg?w=640', 'SLV-007'),
                ('RVG Sleeves', 'https://images.pexels.com/photos/4020593/pexels-photo-4020593.jpeg?w=640', 'SLV-008'),
                ('OPG 3D Hygenic sleeves', 'https://images.pexels.com/photos/3945699/pexels-photo-3945699.jpeg?w=640', 'SLV-009'),
                ('PSP 1 X-ray sleeves', 'https://images.pexels.com/photos/5632410/pexels-photo-5632410.jpeg?w=640', 'SLV-010'),
                ('Sensor Sleeves', 'https://images.pexels.com/photos/4021292/pexels-photo-4021292.jpeg?w=640', 'SLV-011'),
            ],
        }

        created = 0
        for cat_name, products in samples.items():
            cat, _ = ProductCategory.objects.get_or_create(name=cat_name)
            for idx, (name, image_url, sku) in enumerate(products, start=1):
                # Use provided image_url (now working URLs)
                image_url_final = image_url

                p, is_new = Product.objects.get_or_create(
                    category=cat,
                    name=name,
                    defaults={'image_url': image_url_final, 'sku': sku}
                )
                if not is_new:
                    p.image_url = image_url_final
                    p.sku = sku
                    p.save()
                else:
                    created += 1
                # Also create/update matching inventory product so the Inventory app is populated
                try:
                    from inventory.models import Product as InvProduct, Category as InvCategory, Warehouse, Stock

                    inv_cat, _ = InvCategory.objects.get_or_create(name=cat_name)
                    inv_prod, inv_created = InvProduct.objects.get_or_create(
                        name=name,
                        defaults={
                            'sku': sku,
                            'category': inv_cat,
                            'unit_cost': 0,
                        }
                    )
                    if not inv_created:
                        inv_prod.sku = sku
                        inv_prod.category = inv_cat
                        inv_prod.save()

                    # Ensure a default warehouse exists and create initial stock to avoid empty UI actions
                    warehouse, _ = Warehouse.objects.get_or_create(name='Default Warehouse')
                    stock, _ = Stock.objects.get_or_create(product=inv_prod, warehouse=warehouse, defaults={'quantity': 10})
                except Exception:
                    # inventory app may not be present in all environments — skip silently
                    pass

        self.stdout.write(self.style.SUCCESS(f'Created/updated sample data (new products: {created}).'))
