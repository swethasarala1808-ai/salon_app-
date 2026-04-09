app_name = "salon_app"
app_title = "Salon App"
app_publisher = "Swetha"
app_description = "3-in-1 Salon Management for Men, Women & Unisex Salons"
app_email = "swetha@bizaxl.com"
app_license = "MIT"
app_version = "1.0.0"

app_include_css = ["/assets/salon_app/css/salon.css"]
app_include_js = ["/assets/salon_app/js/salon.js"]

after_install = "salon_app.salon_app.install.after_install"
after_migrate = "salon_app.salon_app.install.after_install"

doc_events = {
    "Salon Appointment": {
        "after_insert": "salon_app.salon_app.doctype.salon_appointment.salon_appointment.after_insert",
        "on_update": "salon_app.salon_app.doctype.salon_appointment.salon_appointment.on_update",
    }
}
