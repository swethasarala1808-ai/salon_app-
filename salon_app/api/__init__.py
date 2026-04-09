import frappe
import urllib.parse
from frappe.utils import nowdate, flt


@frappe.whitelist(allow_guest=True)
def get_services(gender_type=None):
    filters = [["is_active", "=", 1]]
    if gender_type and gender_type != "All":
        filters.append(["gender_type", "in", [gender_type, "Unisex"]])
    services = frappe.get_list(
        "Salon Service",
        fields=["name", "service_name", "category", "gender_type", "price", "duration_minutes", "description", "image"],
        filters=filters,
        order_by="category asc, price asc",
        limit=100
    )
    return services


@frappe.whitelist(allow_guest=True)
def get_stylists(gender_type=None):
    filters = [["is_active", "=", 1]]
    if gender_type and gender_type != "All":
        filters.append(["gender_type", "in", [gender_type, "Unisex"]])
    stylists = frappe.get_list(
        "Salon Stylist",
        fields=["name", "full_name", "gender_type", "specialization", "experience_years", "photo", "bio", "skills"],
        filters=filters,
        limit=50
    )
    return stylists


@frappe.whitelist(allow_guest=True)
def get_packages(gender_type=None):
    filters = [["is_active", "=", 1]]
    if gender_type and gender_type != "All":
        filters.append(["gender_type", "in", [gender_type, "Unisex"]])
    packages = frappe.get_list(
        "Salon Package",
        fields=["name", "package_name", "gender_type", "price", "validity_days", "discount_percent", "description", "services_included"],
        filters=filters,
        limit=30
    )
    return packages


@frappe.whitelist(allow_guest=True)
def get_settings():
    try:
        doc = frappe.get_doc("Salon Settings", "Salon Settings")
        return {
            "salon_name": doc.salon_name or "Salon App",
            "tagline": doc.tagline or "",
            "salon_type": doc.salon_type or "Unisex",
            "phone": doc.phone or "",
            "email": doc.email or "",
            "address": doc.address or "",
            "hours": doc.hours or "9 AM - 8 PM",
            "upi_id": doc.upi_id or "",
            "google_rating": doc.google_rating or 4.9,
            "total_clients": doc.total_clients or 0,
            "experience_years": doc.experience_years or 0,
        }
    except Exception:
        return {"salon_name": "Salon App", "salon_type": "Unisex"}


@frappe.whitelist(allow_guest=True)
def book_appointment(customer_name, customer_phone, salon_type, service,
                     appointment_date, appointment_time, stylist=None, notes=None):
    try:
        # Auto-create customer
        existing_cust = frappe.db.get_value("Salon Customer", {"phone": customer_phone}, "name")
        if not existing_cust:
            cust = frappe.new_doc("Salon Customer")
            cust.full_name = customer_name
            cust.phone = customer_phone
            cust.salon_type_preference = salon_type
            cust.insert(ignore_permissions=True)

        # Create appointment
        appt = frappe.new_doc("Salon Appointment")
        appt.customer_name = customer_name
        appt.customer_phone = customer_phone
        appt.salon_type = salon_type
        appt.service = service
        appt.appointment_date = appointment_date
        appt.appointment_time = appointment_time
        appt.status = "Booked"
        if stylist:
            appt.stylist = stylist
        if notes:
            appt.notes = notes
        appt.insert(ignore_permissions=True)
        frappe.db.commit()

        return {"success": True, "appointment": appt.name, "message": f"Booking confirmed! ID: {appt.name}"}
    except Exception as e:
        frappe.logger().error(f"book_appointment error: {e}")
        return {"success": False, "error": str(e)}


@frappe.whitelist()
def get_dashboard_data(salon_type=None):
    from frappe.utils import getdate, get_first_day, get_last_day
    today = nowdate()
    month_start = get_first_day(today)

    filters = [["appointment_date", "=", today]]
    if salon_type:
        filters.append(["salon_type", "=", salon_type])

    today_appts = frappe.db.count("Salon Appointment", filters)
    confirmed = frappe.db.count("Salon Appointment", [["appointment_date", "=", today], ["status", "in", ["Confirmed", "In Progress"]]])

    month_filters = [["invoice_date", "between", [month_start, today]]]
    if salon_type:
        month_filters.append(["salon_type", "=", salon_type])

    invoices = frappe.db.sql(f"""
        SELECT COALESCE(SUM(grand_total), 0) as total
        FROM `tabSalon Invoice`
        WHERE invoice_date BETWEEN '{month_start}' AND '{today}'
        {"AND salon_type = '" + salon_type + "'" if salon_type else ""}
        AND payment_status = 'Paid'
    """, as_dict=True)

    revenue = invoices[0].total if invoices else 0
    total_customers = frappe.db.count("Salon Customer")

    return {
        "today_appointments": today_appts,
        "confirmed_today": confirmed,
        "month_revenue": revenue,
        "total_customers": total_customers,
    }
