import frappe
import urllib.parse
from frappe.utils import nowdate, flt


class SalonAppointment(frappe.model.document.Document):
    def after_insert(self):
        _auto_create_customer(self)

    def on_update(self):
        if self.status == "Confirmed":
            _auto_create_invoice(self)


def _auto_create_customer(appt):
    if not (appt.customer_name and appt.customer_phone):
        return
    try:
        if not frappe.db.get_value("Salon Customer", {"phone": appt.customer_phone}, "name"):
            frappe.get_doc({
                "doctype": "Salon Customer",
                "full_name": appt.customer_name,
                "phone": appt.customer_phone,
                "salon_type": appt.salon_type or "Unisex"
            }).insert(ignore_permissions=True)
            frappe.db.commit()
    except Exception as e:
        frappe.log_error(str(e), "Auto Create Customer Error")


def _auto_create_invoice(appt):
    try:
        if frappe.db.get_value("Salon Invoice", {"appointment": appt.name}, "name"):
            return
        # Get price from service
        price = 0
        if appt.service:
            try:
                price = flt(frappe.db.get_value("Salon Service", appt.service, "price") or 0)
            except Exception:
                price = 0
        frappe.get_doc({
            "doctype": "Salon Invoice",
            "customer_name": appt.customer_name,
            "appointment": appt.name,
            "salon_type": appt.salon_type or "Unisex",
            "service": appt.service or "",
            "stylist": appt.stylist or "",
            "invoice_date": nowdate(),
            "subtotal": price,
            "grand_total": price,
            "payment_status": "Unpaid"
        }).insert(ignore_permissions=True)
        frappe.db.commit()
    except Exception as e:
        frappe.log_error(str(e), "Auto Create Invoice Error")


def _build_wa_msg(appt, status):
    name = appt.customer_name or "Customer"
    service = appt.service or "service"
    date = str(appt.appointment_date or "")
    time = str(appt.appointment_time or "")[:5]
    salon = appt.salon_type or "Salon"
    try:
        ph = frappe.db.get_single_value("Salon Settings", "phone") or "+91 98765 43210"
        upi = frappe.db.get_single_value("Salon Settings", "upi_id") or "salon@upi"
    except Exception:
        ph = "+91 98765 43210"
        upi = "salon@upi"
    price = 0
    if service:
        try:
            price = flt(frappe.db.get_value("Salon Service", service, "price") or 0)
        except Exception:
            price = 0

    if status == "Booked":
        return (f"*Appointment Booked!*\n\nDear *{name}*,\n"
                f"Your *{salon} Salon* appointment is received!\n\n"
                f"Date: *{date}* | Time: *{time}*\nService: *{service}*\n\n"
                f"We will confirm shortly.\nCall: *{ph}*\n\nThank you!")
    elif status == "Confirmed":
        upi_link = f"upi://pay?pa={urllib.parse.quote(upi)}&pn={urllib.parse.quote(salon+' Salon')}&am={int(price)}&cu=INR"
        return (f"*Appointment Confirmed!*\n\nDear *{name}*,\n"
                f"Your *{salon} Salon* booking is confirmed!\n\n"
                f"Date: *{date}* | Time: *{time}*\nService: *{service}*\n"
                f"Amount: *Rs.{int(price)}*\n\n"
                f"Pay Now (UPI): {upi_link}\n"
                f"UPI ID: *{upi}*\n\nSee you soon!")
    elif status == "Completed":
        return (f"*Thank You {name}!*\n\n"
                f"Your *{service}* session is complete!\n"
                f"Hope you loved it. Book again: *{ph}*")
    elif status == "Cancelled":
        return (f"*Appointment Cancelled*\n\nDear *{name}*,\n"
                f"Your *{service}* on *{date}* has been cancelled.\n"
                f"Rebook anytime: *{ph}*")
    return f"Hi {name}, update from {salon} Salon."


@frappe.whitelist()
def update_appointment_status(appointment_name, new_status):
    try:
        appt = frappe.get_doc("Salon Appointment", appointment_name)
        appt.status = new_status
        appt.save(ignore_permissions=True)
        frappe.db.commit()

        inv_name = None
        if new_status == "Confirmed":
            _auto_create_invoice(appt)
            inv_name = frappe.db.get_value("Salon Invoice", {"appointment": appointment_name}, "name")

        wa_link = None
        phone = appt.customer_phone or ""
        if phone:
            msg = _build_wa_msg(appt, new_status)
            digits = "".join(filter(str.isdigit, phone))
            if len(digits) == 10:
                digits = "91" + digits
            wa_link = "https://wa.me/" + digits + "?text=" + urllib.parse.quote(msg)

        return {
            "success": True,
            "new_status": new_status,
            "customer": appt.customer_name,
            "phone": phone,
            "wa_link": wa_link,
            "invoice": inv_name
        }
    except Exception as e:
        frappe.log_error(str(e), "update_appointment_status Error")
        return {"success": False, "error": str(e)}
