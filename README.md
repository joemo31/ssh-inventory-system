# SSH Consumables Inventory Management System 2026

A full-stack web application for tracking airport site consumables.

---

## 🚀 Quick Start

### Windows
1. Double-click **START.bat**
2. The browser opens automatically
3. Login with: `admin` / `admin123`

### Linux / Mac
```bash
chmod +x start.sh
./start.sh
```

---

## 📋 Requirements

- **Python 3.8 or higher** — https://python.org/downloads
- **Flask** (auto-installed by start scripts)

---

## 🗂️ Project Structure

```
ssh-inventory/
├── START.bat              ← Windows launcher (double-click this)
├── start.sh               ← Linux/Mac launcher
├── README.md
├── backend/
│   ├── app.py             ← Flask API server (port 5050)
│   └── inventory.db       ← SQLite database (auto-created)
└── frontend/
    └── index.html         ← Full web application (open in browser)
```

---

## 👤 Default User Accounts

| Name | Username | Password | Role |
|---|---|---|---|
| Mahmoud Ali | `admin` | `admin123` | Administrator |
| Sameh El-Sayed | `sameh` | `sameh123` | Engineer |
| Ahmed Nagy | `ahmed` | `ahmed123` | Technician |
| Yousef | `yousef` | `yousef123` | Technician |
| Night Reviewer | `night` | `night123` | Night Shift |

> ⚠️ **Change passwords after first login** via the Admin Panel.

---

## 🔐 Role Permissions

| Feature | Admin | Engineer | Technician | Night Reviewer |
|---|:---:|:---:|:---:|:---:|
| View all inventory | ✓ | ✓ | ✓ | ✓ |
| Record receipts | ✓ | ✓ | ✓ | ✓ |
| Issue items | ✓ | ✓ | ✓ | ✓ |
| Delete records | ✓ | — | — | — |
| Admin panel | ✓ | — | — | — |
| Manage users | ✓ | — | — | — |
| Monthly reports | ✓ | ✓ | — | — |

---

## 📦 Inventory Modules

1. **HP 80A Cartridges** — HP Laser 400 Black cartridges
2. **HP 59X Cartridges** — HP Laser 404 Pro White cartridges
3. **LDCS Materials** — Labels (175/roll) and Boarding passes (1000/packet)
4. **Custom Printer Heads** — ATB/BTP heads
5. **DCP Head & Rippon** — Gate DCP heads and ribbons

---

## 🌐 API Endpoints

The backend runs at `http://localhost:5050`

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/auth/login` | Login |
| POST | `/api/auth/logout` | Logout |
| GET | `/api/dashboard` | Stock levels & alerts |
| GET | `/api/inventory/:key` | Category details |
| POST | `/api/receipts` | Record receipt |
| DELETE | `/api/receipts/:id` | Delete receipt |
| POST | `/api/issuances` | Record issuance |
| DELETE | `/api/issuances/:id` | Delete issuance |
| GET | `/api/users` | List users |
| POST | `/api/users` | Create user |
| DELETE | `/api/users/:id` | Deactivate user |
| GET | `/api/departments` | List departments |
| POST | `/api/departments` | Add department |
| GET | `/api/reports/monthly` | Monthly report |
| GET | `/api/activity` | Activity log |

---

## 🖥️ Sharing on Local Network (Team Access)

To let your whole team access the system from their own computers:

1. Find your IP address: run `ipconfig` (Windows) or `ifconfig` (Linux)
2. Edit `frontend/index.html` — change line:
   ```js
   const API = 'http://localhost:5050';
   ```
   to:
   ```js
   const API = 'http://YOUR_IP_ADDRESS:5050';
   ```
3. Share the `frontend/index.html` file with your team, or host it on a shared drive
4. Everyone opens `index.html` in their browser — data is shared via the central backend

---

## 💾 Database Backup

The database is stored in `backend/inventory.db`. Back it up regularly by copying this file.

---

## 📧 Monthly Reports

Reports are restricted to:
- **Mahmoud Ali** (Administrator)
- **Eng. Sameh El-Sayed** (Engineer)

Use the Reports section to generate and print monthly summaries.
