import frappe
from frappe.utils import nowdate


def after_install():
    print("Setting up Salon App...")
    _create_roles()
    _create_services()
    _create_staff()
    _create_packages()
    _create_branches()
    _create_type_settings()
    frappe.db.commit()
    print("Salon App setup complete!")


def _create_roles():
    for r in ["Salon Owner", "Salon Staff", "Salon Receptionist"]:
        if not frappe.db.exists("Role", r):
            frappe.get_doc({"doctype": "Role", "role_name": r, "desk_access": 1}).insert(ignore_permissions=True)
    print("  Roles created")


def _create_services():
    services = [
        # MEN
        ("Men Haircut", "Men", "Haircut", 150, 20, "Classic and modern haircuts for men"),
        ("Kids Haircut", "Men", "Haircut", 100, 15, "Gentle haircuts for children"),
        ("Beard Trim", "Men", "Beard & Shave", 100, 15, "Neat beard shaping and trimming"),
        ("Clean Shave", "Men", "Beard & Shave", 80, 15, "Traditional razor clean shave"),
        ("Beard Design", "Men", "Beard & Shave", 200, 25, "Creative beard styling"),
        ("Men Basic Facial", "Men", "Men Facial", 300, 45, "Deep cleansing facial for men"),
        ("Men Detan Facial", "Men", "Men Facial", 400, 60, "Detan and brightening facial"),
        ("Men Hair Color", "Men", "Men Hair Color", 500, 60, "Hair coloring for men"),
        ("Head Massage", "Men", "Men Grooming", 200, 20, "Relaxing head massage"),
        # WOMEN
        ("Women Haircut", "Women", "Hair Styling", 250, 30, "Precision cut for all hair types"),
        ("Blow Dry", "Women", "Hair Styling", 300, 30, "Professional blow dry and styling"),
        ("Hair Straightening", "Women", "Hair Treatment", 1200, 120, "Semi-permanent straightening"),
        ("Hair Rebonding", "Women", "Hair Treatment", 2500, 180, "Permanent rebonding treatment"),
        ("Women Basic Facial", "Women", "Women Facial", 500, 60, "Deep cleansing facial"),
        ("Gold Facial", "Women", "Women Facial", 800, 75, "Luxury gold leaf facial"),
        ("Full Arms Waxing", "Women", "Waxing", 200, 30, "Full arms hair removal"),
        ("Full Legs Waxing", "Women", "Waxing", 300, 40, "Full legs hair removal"),
        ("Full Body Waxing", "Women", "Waxing", 800, 90, "Complete body waxing"),
        ("Eyebrow Threading", "Women", "Threading", 30, 10, "Eyebrow shaping"),
        ("Upper Lip Threading", "Women", "Threading", 20, 5, "Upper lip hair removal"),
        ("Bridal Makeup", "Women", "Bridal", 8000, 180, "Complete bridal look"),
        ("Party Makeup", "Women", "Makeup", 2000, 90, "Party and event makeup"),
        ("Manicure", "Women", "Nail Art", 300, 45, "Hand care and nail polish"),
        ("Pedicure", "Women", "Nail Art", 400, 60, "Foot care and nail polish"),
        # UNISEX
        ("Hair Spa", "Unisex", "Hair Spa", 600, 60, "Deep nourishing hair spa"),
        ("Deep Conditioning", "Unisex", "Scalp Treatment", 800, 75, "Intensive conditioning"),
        ("Keratin Treatment", "Unisex", "Keratin", 3000, 180, "Smoothing keratin treatment"),
        ("Scalp Massage", "Unisex", "Massage", 400, 30, "Therapeutic scalp massage"),
        ("Full Body Massage", "Unisex", "Massage", 1500, 60, "Relaxing full body massage"),
        ("Hair Coloring", "Unisex", "Hair Color", 1500, 120, "Professional hair coloring"),
        ("Highlights", "Unisex", "Hair Color", 2000, 150, "Balayage and highlights"),
    ]
    for name, stype, cat, price, dur, desc in services:
        if not frappe.db.exists("Salon Service", name):
            try:
                frappe.get_doc({
                    "doctype": "Salon Service",
                    "service_name": name,
                    "salon_type": stype,
                    "category": cat,
                    "price": price,
                    "duration_minutes": dur,
                    "description": desc,
                    "is_active": 1
                }).insert(ignore_permissions=True)
            except Exception as e:
                print(f"  Warning service {name}: {e}")
    print(f"  Services created")


def _create_staff():
    staff = [
        ("Rajan Kumar", "Men", "Barber", "Haircut, Beard Styling", "9876543210", 8),
        ("Suresh M", "Men", "Barber", "Clean Shave, Beard Design", "9876543215", 5),
        ("Anita Reddy", "Women", "Stylist", "Hair Styling, Makeup", "9876543211", 10),
        ("Priya Sharma", "Women", "Skin Therapist", "Facials, Waxing, Threading", "9876543212", 7),
        ("Kavya Nair", "Women", "Nail Tech", "Manicure, Pedicure", "9876543213", 4),
        ("Deepa Rao", "Unisex", "Stylist", "Hair Spa, Keratin, Color", "9876543214", 9),
        ("Meena T", "Women", "Makeup Artist", "Bridal, Party Makeup", "9876543216", 6),
    ]
    for name, stype, role, spec, phone, exp in staff:
        if not frappe.db.exists("Salon Staff", name):
            try:
                frappe.get_doc({
                    "doctype": "Salon Staff",
                    "staff_name": name,
                    "salon_type": stype,
                    "role": role,
                    "specialization": spec,
                    "phone": phone,
                    "experience_years": exp,
                    "is_active": 1
                }).insert(ignore_permissions=True)
            except Exception as e:
                print(f"  Warning staff {name}: {e}")
    print(f"  Staff created")


def _create_packages():
    packages = [
        ("Quick Groom", "Men", 299, "Best starter combo",
         "Men Haircut\nBeard Trim\nFace Cleanup", 10, 30),
        ("Royal Groom", "Men", 799, "Complete men grooming",
         "Designer Haircut\nBeard Design\nDetan Facial\nHead Massage", 15, 45),
        ("Glow Package", "Women", 799, "Most popular women package",
         "Women Haircut\nBasic Facial\nEyebrow Threading\nHead Massage", 10, 30),
        ("Beauty Blast", "Women", 1499, "Complete beauty package",
         "Hair Styling\nGold Facial\nArms Waxing\nManicure\nEyebrow + Lip", 20, 45),
        ("Bridal Glow", "Women", 8999, "Complete bridal package",
         "Bridal Makeup\nHair Styling\nFull Body Waxing\nFacial\nManicure + Pedicure", 0, 90),
        ("Spa Day", "Unisex", 1299, "Relaxation package",
         "Hair Spa\nDeep Conditioning\nScalp Massage", 10, 60),
        ("Hair Transformation", "Unisex", 3999, "Complete hair makeover",
         "Keratin Treatment\nDeep Conditioning\nHair Coloring\nHair Spa", 15, 90),
    ]
    for name, stype, price, desc, svcs, disc, validity in packages:
        if not frappe.db.exists("Salon Package", name):
            try:
                frappe.get_doc({
                    "doctype": "Salon Package",
                    "package_name": name,
                    "salon_type": stype,
                    "price": price,
                    "description": desc,
                    "services_included": svcs,
                    "discount_percent": disc,
                    "validity_days": validity,
                    "is_active": 1
                }).insert(ignore_permissions=True)
            except Exception as e:
                print(f"  Warning package {name}: {e}")
    print(f"  Packages created")


def _create_branches():
    """Create sample branches"""
    branches = [
        ("Main Branch", "Bengaluru", "MG Road, Bengaluru - 560001", "+91 98765 43210"),
        ("Chennai Branch", "Chennai", "Anna Nagar, Chennai - 600040", "+91 98765 43220"),
    ]
    for name, city, addr, phone in branches:
        if not frappe.db.exists("Salon Branch", name):
            try:
                frappe.get_doc({
                    "doctype": "Salon Branch",
                    "branch_name": name,
                    "city": city,
                    "address": addr,
                    "phone": phone,
                    "is_active": 1
                }).insert(ignore_permissions=True)
            except Exception as e:
                print(f"  Warning branch {name}: {e}")
    print("  Branches created")


def _create_type_settings():
    """Create per-type settings"""
    settings = [
        ("Men", "Men's Grooming Studio", "Expert cuts, beard styling & grooming", "+91 98765 43210", "9 AM - 8 PM Daily"),
        ("Women", "Women's Beauty Studio", "Hair, skin, makeup & bridal services", "+91 98765 43211", "9 AM - 8 PM Daily"),
        ("Unisex", "Unisex Salon", "Hair spa, keratin, massage for everyone", "+91 98765 43212", "9 AM - 8 PM Daily"),
    ]
    for stype, name, tagline, phone, hours in settings:
        if not frappe.db.exists("Salon Type Settings", stype):
            try:
                frappe.get_doc({
                    "doctype": "Salon Type Settings",
                    "salon_type": stype,
                    "salon_name": name,
                    "tagline": tagline,
                    "phone": phone,
                    "working_hours": hours,
                    "google_rating": 4.9,
                    "upi_id": "salon@upi",
                    "address": "Bengaluru, Karnataka",
                    "city": "Bengaluru"
                }).insert(ignore_permissions=True)
            except Exception as e:
                print(f"  Warning settings {stype}: {e}")
    print("  Type settings created")
