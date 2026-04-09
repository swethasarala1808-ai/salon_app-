# 💈 Salon App — 3-in-1 Frappe Salon Management

A single Frappe app that manages **Men**, **Women**, and **Unisex** salons separately with dedicated portals for each.

---

## 🏗 App Structure

```
salon_app/
├── salon_app/
│   ├── doctype/
│   │   ├── salon_settings/       # Single doctype: salon config, UPI, contact
│   │   ├── salon_service/        # Services with gender_type field
│   │   ├── service_category/     # Categories (Men/Women/Unisex)
│   │   ├── salon_stylist/        # Stylists with salon type assignment
│   │   ├── salon_customer/       # Customer records (auto-created on booking)
│   │   ├── salon_appointment/    # Bookings with WhatsApp + invoice auto-create
│   │   ├── salon_invoice/        # Billing (auto-created on Confirmed)
│   │   └── salon_package/        # Packages per salon type
│   ├── api/
│   │   └── __init__.py           # Whitelisted APIs for portals
│   ├── www/
│   │   ├── index.html            # Landing: choose Men / Women / Unisex
│   │   ├── men/index.html        # Men salon portal (blue theme)
│   │   ├── women/index.html      # Women salon portal (pink theme)
│   │   ├── unisex/index.html     # Unisex salon portal (teal theme)
│   │   └── owner/index.html      # Owner dashboard (all 3 salons)
│   ├── public/
│   │   ├── css/salon.css
│   │   └── js/salon.js           # Shared booking functions
│   ├── install.py                # Post-install: roles, categories, sample data
│   └── hooks.py
├── setup.py
└── requirements.txt
```

---

## 🚀 Installation (in your frappe-bench)

### Step 1: Create GitHub Repo
1. Go to https://github.com/new
2. Name: `salon_app` → Create

### Step 2: Clone this repo into your bench
```bash
cd ~/frappe-bench
bench get-app https://github.com/YOUR_USERNAME/salon_app.git
```

### Step 3: Create a new site
```bash
bench new-site salon.localhost \
  --mariadb-root-password root \
  --admin-password Admin@123 \
  --install-app salon_app
```

### Step 4: Start bench
```bash
bench start
```

### Step 5: Visit your portals
| Portal | URL |
|--------|-----|
| 🏠 Landing | http://salon.localhost:8000 |
| 💈 Men Salon | http://salon.localhost:8000/men |
| 💄 Women Salon | http://salon.localhost:8000/women |
| ✨ Unisex Salon | http://salon.localhost:8000/unisex |
| 📊 Owner Dashboard | http://salon.localhost:8000/owner |
| ⚙ Frappe Admin | http://salon.localhost:8000/app |

---

## 🎨 Salon Themes

| Salon | Color | Focus |
|-------|-------|-------|
| 💈 Men | Blue `#114EFF` | Haircut, Beard, Shave, Facial |
| 💄 Women | Pink `#db2777` | Hair, Wax, Makeup, Bridal, Nails |
| ✨ Unisex | Teal `#14F1B1` | Hair Spa, Keratin, Massage, All |

---

## 📋 DocTypes

| DocType | Auto-name | Purpose |
|---------|-----------|---------|
| Salon Settings | Single | UPI, phone, hours, address |
| Salon Service | service_name | Services filtered by gender_type |
| Service Category | category_name | Categories per salon type |
| Salon Stylist | full_name | Stylists assigned to salon type |
| Salon Customer | SALON-CUST-.YYYY.-.##### | Auto-created on booking |
| Salon Appointment | SALON-APT-.YYYY.-.##### | Core booking doctype |
| Salon Invoice | SALON-INV-.YYYY.-.##### | Auto-created on Confirmed |
| Salon Package | package_name | Deals per salon type |

---

## 🔧 API Endpoints

All whitelisted in `salon_app/api/__init__.py`:

```
GET  /api/method/salon_app.salon_app.api.get_services?gender_type=Men
GET  /api/method/salon_app.salon_app.api.get_stylists?gender_type=Women
GET  /api/method/salon_app.salon_app.api.get_packages?gender_type=Unisex
GET  /api/method/salon_app.salon_app.api.get_settings
POST /api/method/salon_app.salon_app.api.book_appointment
POST /api/method/salon_app.salon_app.doctype.salon_appointment.salon_appointment.update_appointment_status
```

---

## 💡 Owner Dashboard Features
- 🔐 Login with Frappe credentials
- 📊 Stats: Today's bookings by Men/Women/Unisex
- 📅 Appointments with status dropdown (WhatsApp popup on change)
- 👤 Customers list
- ✂ Services management
- 👥 Stylists management  
- 💰 Billing / Invoices with Mark Paid
- 📦 Packages management
- 🔔 Live notifications from portal bookings
- 🔄 Sync pending portal bookings to Frappe

---

## 👤 Author
Swetha | swetha@bizaxl.com
