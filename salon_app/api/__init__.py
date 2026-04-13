import frappe
from frappe.utils import nowdate, flt
import urllib.parse


@frappe.whitelist(allow_guest=True)
def get_branches():
    """Get all active branches for customer site dropdown"""
    try:
        return frappe.get_all(
            "Salon Branch",
            fields=["name", "branch_name", "city", "address", "phone"],
            filters={"is_active": 1},
            order_by="city asc, branch_name asc",
            limit=50
        )
    except Exception:
        return []


@frappe.whitelist(allow_guest=True)
def get_salon_settings(salon_type=None):
    """Get settings for a specific salon type (Men/Women/Unisex)"""
    try:
        if salon_type:
            doc = frappe.get_doc("Salon Type Settings", salon_type)
            return {
                "salon_name": doc.salon_name or f"{salon_type} Salon",
                "tagline": doc.tagline or "",
                "phone": doc.phone or "+91 98765 43210",
                "whatsapp": doc.whatsapp or doc.phone or "+91 98765 43210",
                "email": doc.email or "",
                "address": doc.address or "",
                "city": doc.city or "",
                "working_hours": doc.working_hours or "9 AM - 8 PM Daily",
                "upi_id": doc.upi_id or "",
                "google_rating": doc.google_rating or 4.9,
                "about_us": doc.about_us or "",
                "hero_title": doc.hero_title or "",
                "hero_subtitle": doc.hero_subtitle or "",
                "branch": doc.branch or "",
            }
    except Exception:
        pass
    # Fallback to global settings
    return get_settings()


@frappe.whitelist(allow_guest=True)
def get_services(salon_type=None, branch=None):
    filters = {"is_active": 1}
    if salon_type and salon_type != "All":
        filters["salon_type"] = salon_type
    if branch:
        # Filter by branch OR no branch set (shared services)
        try:
            svc_with_branch = frappe.get_all(
                "Salon Service",
                fields=["name","service_name","salon_type","category","price","duration_minutes","description"],
                filters={**filters, "branch": branch},
                order_by="category asc, price asc",
                limit=100
            )
            if svc_with_branch:
                return svc_with_branch
        except Exception:
            pass
    try:
        result = frappe.get_all(
            "Salon Service",
            fields=["name","service_name","salon_type","category","price","duration_minutes","description"],
            filters=filters,
            order_by="category asc, price asc",
            limit=100
        )
        for s in result:
            if not s.get("service_name"):
                s["service_name"] = s.get("name", "")
        return result
    except Exception as e:
        frappe.log_error(str(e), "get_services Error")
        return []


@frappe.whitelist(allow_guest=True)
def get_staff(salon_type=None, branch=None):
    filters = {"is_active": 1}
    if salon_type and salon_type != "All":
        filters["salon_type"] = salon_type
    if branch:
        try:
            staff_branch = frappe.get_all(
                "Salon Staff",
                fields=["name","staff_name","salon_type","role","specialization","experience_years","photo"],
                filters={**filters, "branch": branch},
                limit=50
            )
            if staff_branch:
                for s in staff_branch:
                    if not s.get("staff_name"): s["staff_name"] = s.get("name","")
                return staff_branch
        except Exception:
            pass
    try:
        staff = frappe.get_all(
            "Salon Staff",
            fields=["name","staff_name","salon_type","role","specialization","experience_years","photo"],
            filters=filters,
            limit=50
        )
        for s in staff:
            if not s.get("staff_name"):
                s["staff_name"] = s.get("name", "")
        return staff
    except Exception as e:
        frappe.log_error(str(e), "get_staff Error")
        return []


@frappe.whitelist(allow_guest=True)
def get_packages(salon_type=None, branch=None):
    filters = {"is_active": 1}
    if salon_type and salon_type != "All":
        filters["salon_type"] = salon_type
    try:
        return frappe.get_all(
            "Salon Package",
            fields=["name","package_name","salon_type","price","validity_days","discount_percent","description","services_included"],
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
                     appointment_date, appointment_time, stylist=None,
                     notes=None, branch=None):
    try:
        if not customer_name or not salon_type or not service or not appointment_date or not appointment_time:
            return {"success": False, "error": "Missing required fields"}

        if customer_phone:
            try:
                if not frappe.db.get_value("Salon Customer", {"phone": customer_phone}, "name"):
                    frappe.get_doc({
                        "doctype": "Salon Customer",
                        "full_name": customer_name,
                        "phone": customer_phone,
                        "salon_type": salon_type
                    }).insert(ignore_permissions=True)
            except Exception:
                pass

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
        # Only set stylist if it exists as Salon Staff
        if stylist:
            if frappe.db.exists("Salon Staff", stylist):
                appt_data["stylist"] = stylist
            else:
                # Try by staff_name field
                name_match = frappe.db.get_value("Salon Staff", {"staff_name": stylist}, "name")
                if name_match:
                    appt_data["stylist"] = name_match

        appt = frappe.get_doc(appt_data)
        appt.insert(ignore_permissions=True)
        frappe.db.commit()
        return {"success": True, "appointment": appt.name, "name": appt.name}
    except Exception as e:
        frappe.log_error(str(e), "Salon book_appointment Error")
        return {"success": False, "error": str(e)}


@frappe.whitelist()
def get_dashboard_stats(salon_type=None):
    today = nowdate()

    def cnt(dt, f=None):
        try: return frappe.db.count(dt, f or {})
        except: return 0

    base = {"appointment_date": today}
    if salon_type and salon_type != "all":
        base["salon_type"] = salon_type

    inv_f = {"payment_status": "Paid"}
    if salon_type and salon_type != "all":
        inv_f["salon_type"] = salon_type

    try:
        invoices = frappe.get_all("Salon Invoice",fields=["grand_total"],filters=inv_f,limit=2000)
        rev = sum(flt(i.grand_total) for i in invoices)
    except: rev = 0

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


@frappe.whitelist()
def get_invoices(salon_type=None):
    try:
        filters = {}
        if salon_type and salon_type != "all":
            filters["salon_type"] = salon_type
        return frappe.get_all(
            "Salon Invoice",
            fields=["name","customer_name","salon_type","service","appointment",
                    "invoice_date","subtotal","grand_total","payment_status","payment_method"],
            filters=filters,
            order_by="invoice_date desc",
            limit=300
        )
    except Exception as e:
        frappe.log_error(str(e), "get_invoices Error")
        return []


@frappe.whitelist()
def get_customers(salon_type=None):
    """Authenticated endpoint to avoid 417 on Salon Customer"""
    try:
        filters = {}
        if salon_type and salon_type != "all":
            filters["salon_type"] = salon_type
        return frappe.get_all(
            "Salon Customer",
            fields=["name","full_name","phone","email","gender","salon_type","total_visits","loyalty_points"],
            filters=filters,
            order_by="full_name asc",
            limit=500
        )
    except Exception as e:
        frappe.log_error(str(e), "get_customers Error")
        return []
