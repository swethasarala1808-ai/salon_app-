import frappe
from frappe.utils import nowdate, flt
import urllib.parse


@frappe.whitelist(allow_guest=True)
def get_services(salon_type=None):
    filters = {"is_active": 1}
    if salon_type and salon_type != "All":
        filters["salon_type"] = salon_type
    try:
        return frappe.get_all(
            "Salon Service",
            fields=["name", "service_name", "salon_type", "category",
                    "price", "duration_minutes", "description"],
            filters=filters,
            order_by="category asc, price asc",
            limit=100
        )
    except Exception:
        return []


@frappe.whitelist(allow_guest=True)
def get_staff(salon_type=None):
    filters = {"is_active": 1}
    if salon_type and salon_type != "All":
        filters["salon_type"] = salon_type
    try:
        staff = frappe.get_all(
            "Salon Staff",
            fields=["name", "staff_name", "salon_type", "role",
                    "specialization", "experience_years", "photo"],
            filters=filters,
            limit=50
        )
        # Ensure staff_name is set (fallback to name)
        for s in staff:
            if not s.get("staff_name"):
                s["staff_name"] = s.get("name", "")
        return staff
    except Exception as e:
        frappe.log_error(str(e), "get_staff Error")
        return []


@frappe.whitelist(allow_guest=True)
def get_packages(salon_type=None):
    filters = {"is_active": 1}
    if salon_type and salon_type != "All":
        filters["salon_type"] = salon_type
    try:
        return frappe.get_all(
            "Salon Package",
            fields=["name", "package_name", "salon_type", "price",
                    "validity_days", "discount_percent", "description",
                    "services_included"],
            filters=filters,
            limit=30
        )
    except Exception:
        return []


@frappe.whitelist(allow_guest=True)
def get_settings():
    try:
        s = frappe.get_doc("Salon Settings", "Salon Settings")
        return {
            "salon_name": s.salon_name or "Luminescent Atelier",
            "tagline": s.tagline or "3-in-1 Premium Salon",
            "phone": s.phone or "+91 98765 43210",
            "address": s.address or "Bengaluru, KA",
            "hours": s.hours or "9 AM - 8 PM Daily",
            "upi_id": s.upi_id or "salon@upi",
            "google_rating": s.google_rating or 4.9,
            "total_clients": s.total_clients or 500,
            "experience_years": s.experience_years or 5,
        }
    except Exception:
        return {
            "salon_name": "Luminescent Atelier",
            "phone": "+91 98765 43210",
            "hours": "9 AM - 8 PM Daily",
            "upi_id": "salon@upi"
        }


@frappe.whitelist(allow_guest=True)
def book_appointment(customer_name, customer_phone, salon_type, service,
                     appointment_date, appointment_time, stylist=None, notes=None):
    try:
        # Validate required fields
        if not customer_name or not salon_type or not service or not appointment_date or not appointment_time:
            return {"success": False, "error": "Missing required fields"}

        # Auto-create customer
        if customer_phone:
            existing = frappe.db.get_value("Salon Customer", {"phone": customer_phone}, "name")
            if not existing:
                try:
                    frappe.get_doc({
                        "doctype": "Salon Customer",
                        "full_name": customer_name,
                        "phone": customer_phone,
                        "salon_type": salon_type
                    }).insert(ignore_permissions=True)
                except Exception:
                    pass

        # Validate stylist link exists
        valid_stylist = None
        if stylist:
            if frappe.db.exists("Salon Staff", stylist):
                valid_stylist = stylist

        appt_data = {
            "doctype": "Salon Appointment",
            "customer_name": customer_name,
            "customer_phone": customer_phone or "",
            "salon_type": salon_type,
            "service": service,
            "appointment_date": appointment_date,
            "appointment_time": appointment_time,
            "status": "Booked",
            "notes": notes or ""
        }
        if valid_stylist:
            appt_data["stylist"] = valid_stylist

        appt = frappe.get_doc(appt_data)
        appt.insert(ignore_permissions=True)
        frappe.db.commit()
        return {"success": True, "appointment": appt.name, "name": appt.name}
    except Exception as e:
        frappe.log_error(str(e), "Salon Booking Error")
        return {"success": False, "error": str(e)}


@frappe.whitelist()
def get_dashboard_stats(salon_type=None):
    today = nowdate()

    def cnt(dt, f=None):
        try:
            return frappe.db.count(dt, f or {})
        except Exception:
            return 0

    base = {"appointment_date": today}
    if salon_type and salon_type != "all":
        base["salon_type"] = salon_type

    inv_f = {"payment_status": "Paid"}
    if salon_type and salon_type != "all":
        inv_f["salon_type"] = salon_type

    try:
        invoices = frappe.get_all(
            "Salon Invoice",
            fields=["grand_total"],
            filters=inv_f,
            limit=2000
        )
        rev = sum(flt(i.grand_total) for i in invoices)
    except Exception:
        rev = 0

    return {
        "today_total": cnt("Salon Appointment", base),
        "today_men": cnt("Salon Appointment", {"appointment_date": today, "salon_type": "Men"}),
        "today_women": cnt("Salon Appointment", {"appointment_date": today, "salon_type": "Women"}),
        "today_unisex": cnt("Salon Appointment", {"appointment_date": today, "salon_type": "Unisex"}),
        "month_revenue": rev,
        "total_customers": cnt("Salon Customer"),
        "total_staff": cnt("Salon Staff", {"is_active": 1}),
        "total_services": cnt("Salon Service", {"is_active": 1}),
    }
