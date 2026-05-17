# fastapi-porter-service

A Porter-style delivery backend built with FastAPI, PostgreSQL, Redis, and Celery. Features real-time driver location tracking, radius-based driver matching, WebSocket push notifications, and a full delivery lifecycle state machine.

## Stack

- **FastAPI** — REST API + WebSocket
- **PostgreSQL + Alembic** — relational storage with migrations
- **Redis** — GEO-based driver location, pub/sub notifications, heartbeat tracking, eligible driver sets
- **Celery** — async task queue for radius expansion and auto-cancellation
- **Docker + Docker Compose** — fully containerized

---

## Features

### Auth
- OTP-based registration and login
- JWT tokens (HS256)
- Role-based access control: `USER`, `DRIVER`, `ADMIN`

### User Flow
- Register → OTP verify → login → request delivery
- Cancel an in-progress request (if status is `REQUESTED` or `ACCEPTED`)

### Driver Flow
- Register as driver → admin approval required
- Connect via WebSocket to stream live location
- Receive push notifications when a nearby ride becomes available
- Accept, collect, start, reach destination, and drop

### Admin Flow
- Approve or reject driver registration
- Rejected drivers are automatically cleaned up via Celery after a delay

### Radius Expansion (Celery)
- When a ride is requested, a Celery task fires immediately
- Searches for online drivers within an initial radius (2 km), expanding by 1 km every 30 seconds up to 9 km
- Eligible drivers are stored in a Redis sorted set keyed by ride ID
- If no driver accepts within 10 minutes, the ride is auto-cancelled
- Uses `INCR` for atomic radius counter; pipeline for batched Redis reads

### WebSocket — Driver Location
`ws://host/driver_loc?token=<JWT>`
- Driver sends `{"long": float, "lat": float}` continuously
- Server stores location in Redis GEO set (`driver_location`)
- Heartbeat key (`driver_online:<account_id>`) expires after 60s — used to filter offline drivers
- Token expiry checked on every message; connection closed with code 1008 on expiry
- Server pushes ride notifications to the driver via the same WebSocket connection using Redis pub/sub

---

## API Endpoints

### Registration & Auth
| Method | Path | Description |
|--------|------|-------------|
| POST | `/registration` | Register user, returns OTP |
| POST | `/register-verify` | Verify OTP, create account |
| POST | `/login` | Request login OTP |
| POST | `/login-verify` | Verify OTP, returns JWT |

### Driver
| Method | Path | Description |
|--------|------|-------------|
| POST | `/driver-reg` | Register as driver (USER role) |

### Admin
| Method | Path | Description |
|--------|------|-------------|
| PATCH | `/admin/drivers/{driver_id}/status` | Approve or reject driver |

### Porter Requests
| Method | Path | Description |
|--------|------|-------------|
| POST | `/req-porter` | Create a delivery request |
| GET | `/all_request` | View all requests (debug) |

### Accept
| Method | Path | Description |
|--------|------|-------------|
| PATCH | `/accept-porter/{req_id}` | Accept a ride (driver only, must be in eligible set) |

### Lifecycle
| Method | Path | Description |
|--------|------|-------------|
| PATCH | `/driver_reached/{req_id}` | Driver reached pickup |
| PATCH | `/driver_collected/{req_id}` | Item collected |
| PATCH | `/driver_started/{req_id}` | Delivery started |
| PATCH | `/driver_dropped/{req_id}` | Item dropped — ride complete |
| PATCH | `/cancel_req/{req_id}` | Cancel ride (USER or DRIVER) |

### WebSocket
| Path | Description |
|------|-------------|
| `ws://host/driver_loc?token=<JWT>` | Driver location stream + notification channel |

---

## Ride Status Machine

```
REQUESTED → ACCEPTED → REACHED → COLLECTED → STARTED → DROPPED
         ↘            ↘
          CANCELLED    CANCELLED (driver)
         ↙
USER_CANCELLED
```

Auto-cancelled after 10 minutes if no driver accepts.

---

## Running with Docker

```bash
docker compose up --build
```

On first start, run migrations:

```bash
docker exec backend alembic upgrade head
```

### Environment Variables (`.env`)

```
DATABASE_URL=postgresql+psycopg2://postgres:<password>@localhost:5432/porter
DOCKER_DATABASE_URL=postgresql+psycopg2://postgres:<password>@postgres:5432/porter
SECRET_KEY=<your_secret_key>
REDIS_HOST_NAME=localhost
CELERY_URL=redis://localhost
REDIS_URL=redis://redis:6379/0
POSTGRES_USER=postgres
POSTGRES_PASSWORD=<password>
POSTGRES_DB=porter
```

---

## Running Locally

```bash
pip install -r requirements.txt
uvicorn main:app --reload
celery -A tasks worker --loglevel=INFO --pool=solo
```

Requires a running PostgreSQL and Redis instance.

---

## Project Structure

```
.
├── main.py
├── Schema.py          # SQLAlchemy models
├── Models.py          # Pydantic request models
├── enums.py           # Status, Role, Gender enums
├── auth.py            # JWT decode dependency
├── database.py        # DB session, Redis clients
├── tasks.py           # Celery tasks
├── alembic/           # Migrations
└── routers/
    ├── user_registration.py
    ├── login.py
    ├── driver_reg.py
    ├── admin_ver.py
    ├── porter_req.py
    ├── accept.py
    ├── driver_location.py
    └── driver_lifecycle.py
```
