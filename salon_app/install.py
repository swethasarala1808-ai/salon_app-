import frappe


def after_install():
    print("▶ Salon App: Running setup...")
    _create_roles()
    _create_service_categories()
    _create_sample_services()
    frappe.db.commit()
    print("✅ Salon App: Setup complete.")


def _create_roles():
    roles = [
        {"role_name": "Salon Owner", "desk_access": 1},
        {"role_name": "Salon Stylist", "desk_access": 1},
        {"role_name": "Salon Customer", "desk_access": 0},
        {"role_name": "Salon Receptionist", "desk_access": 1},
    ]
    for r in roles:
        if not frappe.db.exists("Role", r["role_name"]):
            doc = frappe.new_doc("Role")
            doc.role_name = r["role_name"]
            doc.desk_access = r["desk_access"]
            doc.insert(ignore_permissions=True)
            print(f"  ✔ Role: {r['role_name']}")


def _create_service_categories():
    # Men categories
    men_cats = ["Haircut", "Beard & Shave", "Men Facial", "Men Hair Color", "Men Grooming"]
    # Women categories
    women_cats = ["Hair Styling", "Hair Treatment", "Women Facial", "Waxing", "Threading", "Bridal", "Makeup", "Nail Art"]
    # Unisex categories
    unisex_cats = ["Hair Spa", "Scalp Treatment", "Keratin", "Massage", "Packages"]

    all_cats = [
        {"name": c, "gender_type": "Men"} for c in men_cats
    ] + [
        {"name": c, "gender_type": "Women"} for c in women_cats
    ] + [
        {"name": c, "gender_type": "Unisex"} for c in unisex_cats
    ]

    for cat in all_cats:
        if not frappe.db.exists("Service Category", cat["name"]):
            try:
                doc = frappe.new_doc("Service Category")
                doc.category_name = cat["name"]
                doc.gender_type = cat["gender_type"]
                doc.is_active = 1
                doc.insert(ignore_permissions=True)
            except Exception as e:
                print(f"  ⚠ Category {cat['name']}: {e}")
    print(f"  ✔ Service categories created")


def _create_sample_services():
    services = [
        # MEN
        {"name": "Men Haircut", "category": "Haircut", "gender_type": "Men", "price": 150, "duration_minutes": 20},
        {"name": "Kids Haircut", "category": "Haircut", "gender_type": "Men", "price": 100, "duration_minutes": 15},
        {"name": "Beard Trim", "category": "Beard & Shave", "gender_type": "Men", "price": 100, "duration_minutes": 15},
        {"name": "Clean Shave", "category": "Beard & Shave", "gender_type": "Men", "price": 80, "duration_minutes": 15},
        {"name": "Beard Styling", "category": "Beard & Shave", "gender_type": "Men", "price": 150, "duration_minutes": 20},
        {"name": "Men Basic Facial", "category": "Men Facial", "gender_type": "Men", "price": 300, "duration_minutes": 45},
        {"name": "Men Detan Facial", "category": "Men Facial", "gender_type": "Men", "price": 400, "duration_minutes": 60},
        {"name": "Men Hair Color", "category": "Men Hair Color", "gender_type": "Men", "price": 500, "duration_minutes": 60},
        # WOMEN
        {"name": "Women Haircut", "category": "Hair Styling", "gender_type": "Women", "price": 250, "duration_minutes": 30},
        {"name": "Blow Dry", "category": "Hair Styling", "gender_type": "Women", "price": 300, "duration_minutes": 30},
        {"name": "Hair Straightening", "category": "Hair Treatment", "gender_type": "Women", "price": 1200, "duration_minutes": 120},
        {"name": "Hair Rebonding", "category": "Hair Treatment", "gender_type": "Women", "price": 2500, "duration_minutes": 180},
        {"name": "Women Basic Facial", "category": "Women Facial", "gender_type": "Women", "price": 500, "duration_minutes": 60},
        {"name": "Gold Facial", "category": "Women Facial", "gender_type": "Women", "price": 800, "duration_minutes": 75},
        {"name": "Full Arms Waxing", "category": "Waxing", "gender_type": "Women", "price": 200, "duration_minutes": 30},
        {"name": "Full Legs Waxing", "category": "Waxing", "gender_type": "Women", "price": 300, "duration_minutes": 40},
        {"name": "Full Body Waxing", "category": "Waxing", "gender_type": "Women", "price": 800, "duration_minutes": 90},
        {"name": "Eyebrow Threading", "category": "Threading", "gender_type": "Women", "price": 30, "duration_minutes": 10},
        {"name": "Upper Lip Threading", "category": "Threading", "gender_type": "Women", "price": 20, "duration_minutes": 5},
        {"name": "Bridal Makeup", "category": "Bridal", "gender_type": "Women", "price": 8000, "duration_minutes": 180},
        {"name": "Party Makeup", "category": "Makeup", "gender_type": "Women", "price": 2000, "duration_minutes": 90},
        {"name": "Manicure", "category": "Nail Art", "gender_type": "Women", "price": 300, "duration_minutes": 45},
        {"name": "Pedicure", "category": "Nail Art", "gender_type": "Women", "price": 400, "duration_minutes": 60},
        # UNISEX
        {"name": "Hair Spa", "category": "Hair Spa", "gender_type": "Unisex", "price": 600, "duration_minutes": 60},
        {"name": "Deep Conditioning", "category": "Scalp Treatment", "gender_type": "Unisex", "price": 800, "duration_minutes": 75},
        {"name": "Keratin Treatment", "category": "Keratin", "gender_type": "Unisex", "price": 3000, "duration_minutes": 180},
        {"name": "Head Massage", "category": "Massage", "gender_type": "Unisex", "price": 400, "duration_minutes": 30},
        {"name": "Full Body Massage", "category": "Massage", "gender_type": "Unisex", "price": 1500, "duration_minutes": 60},
    ]
    for s in services:
        if not frappe.db.exists("Salon Service", s["name"]):
            try:
                doc = frappe.new_doc("Salon Service")
                doc.service_name = s["name"]
                doc.category = s["category"]
                doc.gender_type = s["gender_type"]
                doc.price = s["price"]
                doc.duration_minutes = s["duration_minutes"]
                doc.is_active = 1
                doc.insert(ignore_permissions=True)
            except Exception as e:
                print(f"  ⚠ Service {s['name']}: {e}")
    print(f"  ✔ Sample services created: {len(services)}")
