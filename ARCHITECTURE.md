# MedLinka — Software Architecture Document

> **Audience guide:** Sections 1–4 are for all readers. Section 5 (Logical View) targets end-users and business stakeholders. Section 6 (Process View) targets system integrators and performance engineers. Section 7 (Development View) targets developers and project managers. Section 8 (Physical View) targets system engineers and DevOps. Section 9 (Scenarios) is for all readers and serves as validation of the architecture.

---

## Change History

| Version | Date | Author | Description |
|---------|------|--------|-------------|
| 1.0 | 2026-04-10 | MedLinka Team | Initial release — 4+1 architecture integration for FastAPI/React Native stack |

---

## Table of Contents

1. Scope
2. References
3. Software Architecture Overview
4. Architectural Goals and Constraints
5. Logical View



---

## 1. Scope

MedLinka addresses the difficulty many people face when accessing affordable healthcare. Physical distance from hospitals, cost barriers, and lack of digital health tools leave many patients without timely care. MedLinka is a multilingual platform (Arabic, Turkish, English) that bridges patients and medical resources by centralizing three core services: AI-assisted symptom triage, doctor consultation booking, and pharmacy ordering.

**What MedLinka covers:**
- Native mobile application for patients (iOS/Android via React Native).
- Web dashboard for doctors and pharmacy management (React + Vite).
- Secure user registration and profile management with multilingual support.
- AI-powered symptom analysis via the Gemini API.
- Doctor consultation scheduling.
- Medicine catalogue browsing, ordering, and prescription tracking.

**What MedLinka explicitly does not cover:**
- Real-time hardware sensor integration or external health device synchronization.
- In-person hospital management or electronic health record (EHR) interoperability.
- Payment processing (marked [TBD] for a future release).

This document follows the Kruchten 4+1 Architectural View Model.

---

## 2. References

| # | Title | Source |
|---|-------|--------|
| R1 | Architectural Blueprints — The "4+1" View Model of Software Architecture | Philippe Kruchten, IEEE Software, Vol. 12 No. 6, November 1995 |
| R2 | SWE 332 Software Architecture — Course Material | Semester 2025–2026 |
| R3 | FastAPI Official Documentation | https://fastapi.tiangolo.com/ |

---

## 3. Software Architecture Overview

MedLinka is designed as a modular, API-first system. The architecture cleanly separates the client interfaces (Mobile App and Web Dashboard) from the backend business logic and data storage (FastAPI + SQLite).

The fundamental architectural strategy is **API-driven modular decomposition**. Each major domain — auth, triage, consultation, pharmacy, and reminders — is implemented as a separate FastAPI router/module. External dependencies (like the Gemini AI API) are wrapped behind dedicated service classes, ensuring that the core business logic remains independent of third-party SDKs.

### 3.1 Architectural Style

The system follows a **layered client-server** style utilizing asynchronous I/O:
- **Clients:** A React Native mobile app (Expo) for end-users, and a React web dashboard for doctors/pharmacies.
- **Server:** A FastAPI application running on Uvicorn (ASGI), providing RESTful endpoints (`/api/v1/...`).
- **Processing:** The server processes requests asynchronously, utilizing FastAPI's `BackgroundTasks` for non-blocking operations like sending medication reminders.

### 3.2 Correspondence Between Views

| Logical category | Process task | Development module | Physical node |
|------------------|-------------|-------------------|---------------|
| `User`, `Doctor` | Async request handling | `backend/routers/auth.py` | Docker App Container |
| `AIAdvice` | API call + Disclaimer injection | `backend/routers/ai.py` | Docker App → Gemini API |
| `Consultation` | Synchronous booking transaction | `backend/routers/appointments.py`| Docker App → SQLite DB |
| `Order`, `Cart` | Synchronous order transaction | `backend/routers/pharmacy.py` | Docker App → SQLite DB |
| `ReminderTask` | FastAPI `BackgroundTask` | `backend/routers/reminders.py` | Docker App (Background) |

---

## 4. Architectural Goals and Constraints

### 4.1 Quality Goals (Priority Order)

| Priority | Quality Attribute | Description | Measurable target |
|----------|------------------|-------------|-------------------|
| 1 | Security / Privacy | Health data must be protected | JWT authentication; HTTPS enforced; PII secured. |
| 2 | Performance | High concurrency handling | Fast I/O operations utilizing FastAPI's async capabilities. |
| 3 | Modifiability | Easy swap of UI and AI providers | Separation of concerns (React Native / React / FastAPI). |
| 4 | Usability | Multilingual support | Native RTL (Arabic) and LTR (English, Turkish) switching. |

### 4.2 Constraints
- **Framework:** Python / FastAPI required for the backend.
- **Timeline:** One academic semester limits scope (payment processing deferred).
- **Infrastructure:** Dockerized environment for easy local testing and eventual cloud deployment.

---

## 5. Logical View

> **Reader:** End-users, business stakeholders, and developers.

The logical view describes the object-oriented decomposition of MedLinka, organized around functional bounded contexts.

### 5.1 Class Categories and Responsibilities

**Category 1 — Identity & Localization (`users`)**
- `User`: Base class storing credentials, language preference (`ar`, `en`, `tr`), and role.
- `DoctorProfile` / `PatientProfile`: Extensions of the user model for specific roles.

**Category 2 — AI Triage (`ai_triage`)**
- `TriageSession`: Represents an AI chat conversation.
- `AIAdvice`: Stores Gemini AI output, including the mandatory medical disclaimer.

**Category 3 — Consultation (`appointments`)**
- `AvailabilitySlot`: A window on a doctor's calendar.
- `Appointment`: Links a patient to an availability slot.

**Category 4 — Pharmacy (`pharmacy` & `orders`)**
- `Medicine`: Catalogue item (name, dosage, stock).
- `Order` / `OrderItem`: Created upon checkout, containing dosage instructions.

**Category 5 — Reminders (`reminders`)**
- `ReminderSchedule`: Generated from an order item to alert the patient automatically.

### 5.2 Key Relationships
- `User` has one-to-many `TriageSession`s.
- `Appointment` links exactly one `PatientProfile` and one `DoctorProfile`.
- `Order` contains many `OrderItem`s.
- `OrderItem` generates exactly one `ReminderSchedule`.

---

### 5.3 Database Schema Diagram (ERD)

![](https://github.com/krkralkair007/Medical-care-reminder-and-pharmacy-/blob/5239a865e9cbbbe74143dfa0e82cac73404a6523/5.3%20Database%20Schema%20Diagram%20(ERD)%20.jpg)

---

## 6. Process View

> **Reader:** System integrators and performance engineers.

### 6.1 Process Flow and Concurrency

MedLinka utilizes Python's asynchronous ecosystem (ASGI/Uvicorn) to handle high concurrency without the overhead of heavy threads.

**Flow A — AI Triage (Synchronous API with Async I/O)**
1. Mobile App sends `POST /api/v1/ai/chat` with symptom text and `Accept-Language` header.
2. FastAPI receives the request and validates the JWT token.
3. FastAPI awaits the `Gemini API` call asynchronously (non-blocking).
4. The response is processed, a legal disclaimer is injected based on the requested language, and the result is returned to the user.

**Flow B — Order Checkout & Reminders (Background Tasks)**
1. Mobile App sends `POST /api/v1/orders`.
2. FastAPI validates stock and writes the `Order` to the SQLite database.
3. Instead of blocking the HTTP response, FastAPI dispatches a `BackgroundTask` to process the `ReminderSchedule`.
4. The API immediately returns a success response to the patient.
5. In the background, the server schedules the notification logic.

---

![flow A](https://github.com/malfakih1/Medical-care-reminder-and-pharmacy-/blob/21eacafca656ba25723a9441e6c6328976fee143/flow_triage.png)

---

![flow B](https://github.com/malfakih1/Medical-care-reminder-and-pharmacy-/blob/7daa8e4e2b2a73932cd4e81a1f714b38fb0a00be/flow_b_order_checkout.png)

**Flow C — Doctor Booking**

![](https://github.com/krkralkair007/Medical-care-reminder-and-pharmacy-/blob/f5da9263195b1ddb7b6368b3b69b8545d0974795/Flow%20C%20%E2%80%94%20Doctor%20Booking.jpg)

---

### 6.3 Fault Tolerance
- **AI Failure:** If Gemini times out, the backend catches the exception and returns a localized standard error ("AI unavailable, please consult a doctor").
- **Database Locks:** SQLite handles concurrent reads well, but writes are sequential. FastAPI's async ORM interactions ensure the event loop is not blocked during I/O.

---

## 7. Development View

> **Reader:** Developers and project managers.

### 7.1 Layer Hierarchy & Repository Structure

The monorepo is divided strictly by tier to allow independent development of the mobile client, web client, and backend.

```text
medlinka/
├── backend/                  # Layer 3: Server (FastAPI + SQLite)
│   ├── routers/              # API endpoints (auth, doctors, ai, orders)
│   ├── models/               # SQLAlchemy DB models & Pydantic schemas
│   ├── services/             # External integrations (Gemini AI)
│   ├── main.py               # Application entry point
│   └── requirements.txt
├── mobile/                   # Layer 2: Mobile Client (React Native + Expo)
│   ├── app/                  # Screens and navigation
│   └── package.json
├── dashboard/                # Layer 1: Web Client (React + Vite)
│   ├── src/                  # Admin/Doctor interfaces
│   └── package.json
└── docker-compose.yml        # Layer 0: Infrastructure
```

### 7.2 Design Rules

1. **Localization First:** All error messages and AI prompts must dynamically respect the `Accept-Language` header (`ar`, `tr`, `en`).
2. **API Versioning:** All endpoints must be prefixed with `/api/v1/`.
3. **Decoupled AI:** The `routers/ai.py` must never import Gemini directly; it must use `services/gemini_client.py`.

---

## 8. Physical View

> **Reader:** System engineers and DevOps.

### 8.1 Deployment Configuration (Dockerized)

The current environment is containerized using Docker Compose for seamless local deployment and testing.

| Node / Container | Software | Role |
|------------------|----------|------|
| `backend` | Python 3.11 + FastAPI + Uvicorn | API Server exposed on port `8000` |
| `database` | SQLite (mounted volume) | Persistent data storage |
| `dashboard` | Node + React (Vite) | Web UI exposed on port `3000` |
| Mobile Device | Expo Go App | Connects to local network API |

**External Dependencies:**
- **Gemini API:** Accessed via outbound HTTPS from the `backend` container.

---

### 8.2 System Architecture Diagram

> Shows how all physical nodes, containers, and external services connect to each other.
![](https://github.com/krkralkair007/Medical-care-reminder-and-pharmacy-/blob/546fa83adfe9b2a32df9d34d18a3e49fb0a86ed2/8.2%20System%20Architecture%20Diagram.jpg)

### 8.3 API Endpoints Map

> A full map of all exposed REST endpoints and their purpose.

```
BASE URL: http://localhost:8000/api/v1/

Authentication
  POST   /auth/register          --> Register new user
  POST   /auth/login             --> Login, receive JWT token

Doctors
  GET    /doctors                --> List all doctors
  GET    /doctors/<id>           --> Get single doctor by ID

Patients
  GET    /patients               --> List all patients
  GET    /patients/<id>          --> Get single patient by ID

Appointments
  GET    /appointments           --> List all appointments (with names)
  GET    /appointments/<id>      --> Get single appointment by ID
  POST   /appointments           --> Book a new appointment
                                     Body: { patient_id, doctor_id, appointment_date }

Pharmacy
  GET    /pharmacy/medicines     --> Browse medicine catalogue
  POST   /orders                 --> Submit a cart / place an order

AI Triage
  POST   /ai/chat                --> Send symptoms, receive AI advice
                                     Header: Accept-Language: ar | en | tr
```

---

## 9. Scenarios

### 9.1 Scenario A — Multilingual AI Triage
1. A Turkish patient authenticates. App sets `Accept-Language: tr`.
2. Patient sends symptoms to `POST /api/v1/ai/chat`.
3. The FastAPI router passes the prompt and language flag to the Gemini service.
4. Gemini processes the request. The backend appends a Turkish medical disclaimer.
5. The Mobile App displays the localized advice and suggests booking a doctor.

### 9.2 Scenario B — Medicine Order
1. Patient browses `/api/v1/pharmacy/medicines` and submits a cart to `POST /api/v1/orders`.
2. FastAPI validates the stock and commits the order to SQLite.
3. A `BackgroundTask` is triggered to schedule medication reminders based on the `OrderItem` instructions.
4. The patient immediately sees a "Success" screen on the mobile app without waiting for the reminder scheduling to finish.

---

## 10. Size and Performance

- **Codebase:** Separated into 3 distinct ecosystems (Python backend, React Native mobile, React web).
- **Performance Target:** FastAPI guarantees sub-100ms response times for database reads (e.g., listing doctors). AI triage is bounded strictly by Gemini network latency.
- **Data:** SQLite is currently used for zero-config deployment. If traffic exceeds SQLite's write capacity, the ORM (SQLAlchemy) allows switching to PostgreSQL with minimal code changes.

---

## 11. Quality

- **Security:** Passwords are hashed using bcrypt. API relies on stateless JWTs.
- **Medical Safety:** The AI system is heavily sandboxed. Every single AI response includes a non-bypassable medical disclaimer injected at the backend layer.
- **Accessibility:** The mobile and web apps fully support Right-to-Left (RTL) layouts for Arabic users natively through the UI frameworks.

---

## Appendix A — Design Principles and Rationale

| Decision | Alternatives considered | Chosen approach | Rationale |
|----------|------------------------|-----------------|-----------|
| Backend Framework | Django, Flask | **FastAPI** | Superior async performance, automatic Swagger UI docs (`/docs`), and native type checking with Pydantic. |
| AI Provider | OpenAI, Vertex AI | **Gemini** | Highly capable multilingual processing, cost-effective for the academic/startup phase. |
| Mobile Tech | Native (Swift/Kotlin) | **React Native (Expo)** | Single codebase for iOS and Android; aligns with the web team's React knowledge. |
| Database | PostgreSQL | **SQLite** | Zero-configuration needed for local dev via Docker. SQLAlchemy makes future migration to Postgres trivial. |
| Async Tasks | Celery + Redis | **FastAPI BackgroundTasks** | Keeps infrastructure simple (no extra containers needed) while still preventing HTTP blocking. |
