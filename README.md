# SSH Consumables Inventory Management System 2026

A full-stack web application for tracking airport site consumables.

---

## 🚀 Quick Start

### Docker (recommended)

**From GitHub Container Registry** (after the first workflow run):

```bash
docker run -d -p 5050:5050 -v ssh-inventory-data:/app/data --name ssh-inventory \
  ghcr.io/joemo31/ssh-inventory-system:latest
```

Open **http://localhost:5050** and log in with `admin` / `admin123`.

**From source** (clone the repo first):

```bash
docker compose up -d
```

Stop: `docker compose down` · View logs: `docker compose logs -f`

Data is stored in a Docker volume (`inventory-data` with compose, or `ssh-inventory-data` with `docker run`).

---

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

**Docker:** [Docker Desktop](https://www.docker.com/products/docker-desktop/) or Docker Engine + Compose

**Without Docker:**

- **Python 3.8 or higher** — https://python.org/downloads
- **Flask** (auto-installed by start scripts, or `pip install -r requirements.txt`)

---

## 🗂️ Project Structure

```
ssh-inventory/
├── Dockerfile             ← Container image definition
├── docker-compose.yml     ← One-command local run
├── requirements.txt
├── START.bat              ← Windows launcher (double-click this)
├── start.sh               ← Linux/Mac launcher
├── README.md
├── backend/
│   ├── app.py             ← Flask API + serves UI (port 5050)
│   └── inventory.db       ← SQLite database (auto-created)
└── frontend/
    └── index.html         ← Web UI (also served at http://localhost:5050 in Docker)
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

**With Docker:** run the container on a host machine, then teammates open `http://YOUR_IP_ADDRESS:5050` in their browser (no config changes needed).

**Without Docker:** start the backend on one PC, then either:

- Have everyone open **http://YOUR_IP_ADDRESS:5050** if you serve the UI from Flask, or
- For the legacy `file://` workflow, set the API in `frontend/index.html` to your host IP (see the `API` constant in the script section)

---

## 💾 Database Backup

The database is stored in `backend/inventory.db`. Back it up regularly by copying this file.

---

## 📧 Monthly Reports

Reports are restricted to:
- **Mahmoud Ali** (Administrator)
- **Eng. Sameh El-Sayed** (Engineer)

Use the Reports section to generate and print monthly summaries.
