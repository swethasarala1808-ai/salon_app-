app_name = "salon_app"
app_title = "Salon App"
app_publisher = "Swetha"
app_description = "3-in-1 Salon Management - Men, Women & Unisex"
app_email = "swetha@bizaxl.com"
app_license = "MIT"
app_version = "1.0.0"

after_install = "salon_app.install.after_install"

doc_events = {
    "Salon Appointment": {
        "after_insert": "salon_app.doctype.salon_appointment.salon_appointment.SalonAppointment.after_insert",
        "on_update": "salon_app.doctype.salon_appointment.salon_appointment.SalonAppointment.on_update",
    }
}
