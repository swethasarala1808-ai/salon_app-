import frappe
import re
import urllib.parse
from frappe.utils import nowdate, flt


def get_upi_id():
    try:
        return frappe.db.get_single_value("Salon Settings", "upi_id") or "salon@upi"
    except Exception:
        return "salon@upi"


def get_service_price(service_name):
    if not service_name:
        return 0
    price = frappe.db.get_value("Salon Service", service_name, "price")
    return flt(price) if price else 0


def build_wa_message(appt, msg_type, amount=0):
    name = appt.customer_name or "Valued Customer"
    date = str(appt.appointment_date or "")
    time = str(appt.appointment_time or "")[:5]
    service = appt.service or "Salon Service"
    stylist = appt.stylist or "Our expert"
    salon_type = appt.salon_type or "Salon"
    phone = "+91 98765 43210"

    if msg_type == "booked":
        return (
            f"📅 *Appointment Booked!*\n\n"
            f"Dear *{name}*,\n\n"
            f"Your appointment at *{salon_type} Salon* has been received!\n\n"
            f"📆 Date: *{date}*\n⏰ Time: *{time}*\n💈 Service: *{service}*\n\n"
            f"We will confirm shortly. Call: *{phone}*\n\nThank you! 🌟"
        )
    elif msg_type == "confirmed":
        upi_id = get_upi_id()
        tn = urllib.parse.quote(f"{salon_type} Salon - {service}")
        pa = urllib.parse.quote(upi_id)
        upi_link = f"upi://pay?pa={pa}&pn={salon_type}+Salon&am={int(amount)}&cu=INR&tn={tn}"
        return (
            f"✅ *Appointment Confirmed!*\n\n"
            f"Dear *{name}*,\n\n"
            f"Your *{salon_type} Salon* appointment is confirmed! 🎉\n\n"
            f"📆 Date: *{date}*\n⏰ Time: *{time}*\n"
            f"💈 Service: *{service}*\n👤 Stylist: *{stylist}*\n"
            f"💰 Amount: *₹{int(amount)}*\n\n"
            f"💳 *Pay Now:*\n{upi_link}\n\n"
            f"UPI ID: *{upi_id}*\n\nSee you soon! 💈"
        )
    elif msg_type == "completed":
        return (
            f"🙏 *Thank You!*\n\n"
            f"Dear *{name}*,\n\n"
            f"Your *{service}* is complete! Hope you loved it. ✨\n\n"
            f"Book again: Call *{phone}*\n\nSee you next time! 💈"
        )
    elif msg_type == "cancelled":
        return (
            f"❌ *Appointment Cancelled*\n\n"
            f"Dear *{name}*,\n\n"
            f"Your *{service}* appointment on *{date}* has been cancelled.\n\n"
            f"To rebook call: *{phone}*\n\nSorry for the inconvenience! 🙏"
        )
    return f"Hi {name}, update from your Salon! 💈"


def get_wa_link(phone, msg):
    digits = "".join(filter(str.isdigit, phone))
    if len(digits) == 10:
        digits = "91" + digits
    return "https://wa.me/" + digits + "?text=" + urllib.parse.quote(msg)


def auto_create_invoice(appt):
    existing = frappe.db.sql(
        "SELECT name FROM `tabSalon Invoice` WHERE appointment=%s LIMIT 1",
        appt.name, as_list=True
    )
    if existing:
        return frappe.get_doc("Salon Invoice", existing[0][0])
    price = get_service_price(appt.service) or 200
    try:
        inv = frappe.new_doc("Salon Invoice")
        inv.customer_name = appt.customer_name
        inv.appointment = appt.name
        inv.invoice_date = nowdate()
        inv.salon_type = appt.salon_type
        inv.stylist = appt.stylist or ""
        inv.service = appt.service
        inv.subtotal = price
        inv.grand_total = price
        inv.payment_status = "Unpaid"
        inv.flags.ignore_links = True
        inv.insert(ignore_permissions=True)
        frappe.db.commit()
        return inv
    except Exception as e:
        frappe.logger().error(f"Salon Invoice creation failed: {e}")
        return None


@frappe.whitelist()
def update_appointment_status(appointment_name, new_status):
    try:
        appt = frappe.get_doc("Salon Appointment", appointment_name)
        old_status = appt.status
        appt.status = new_status
        appt.save(ignore_permissions=True)
        frappe.db.commit()

        phone = appt.customer_phone or ""

        invoice = None
        invoice_name = None
        if new_status == "Confirmed":
            invoice = auto_create_invoice(appt)
            if invoice:
                invoice_name = invoice.name

        wa_link = None
        if phone:
            amount = flt(invoice.grand_total) if invoice else get_service_price(appt.service)
            msg_map = {
                "Booked": "booked", "Confirmed": "confirmed",
                "In Progress": "in_progress", "Completed": "completed", "Cancelled": "cancelled"
            }
            msg = build_wa_message(appt, msg_map.get(new_status, "booked"), amount)
            wa_link = get_wa_link(phone, msg)

        return {
            "success": True,
            "old_status": old_status,
            "new_status": new_status,
            "customer": appt.customer_name,
            "phone": phone,
            "wa_link": wa_link,
            "invoice_name": invoice_name,
        }
    except Exception as e:
        frappe.logger().error(f"update_appointment_status error: {e}")
        return {"success": False, "error": str(e)}


def after_insert(doc, method=None):
    # Auto-create customer record
    phone = doc.customer_phone or ""
    if doc.customer_name and phone:
        existing = frappe.db.get_value("Salon Customer", {"phone": phone}, "name")
        if not existing:
            try:
                cust = frappe.new_doc("Salon Customer")
                cust.full_name = doc.customer_name
                cust.phone = phone
                cust.salon_type_preference = doc.salon_type
                cust.insert(ignore_permissions=True)
                frappe.db.commit()
            except Exception:
                pass


def on_update(doc, method=None):
    if doc.status == "Confirmed":
        auto_create_invoice(doc)
