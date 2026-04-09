MedLinka — Software Architecture Document
________________________________________
1. Design & Decision Making
Problem Domain Analysis
Before touching the solution, here is what MedLinka is actually trying to accomplish:
Business objectives: Connect patients to doctors quickly via AI-assisted triage, reduce friction in pharmacy ordering, and improve medication adherence through automated reminders.
Functional requirements: User auth, AI symptom analysis, doctor availability lookup, consultation booking (with video), medicine ordering, prescription-based reminder scheduling.
Quality attributes (priority order): Security/privacy > Reliability > Performance > Accessibility > Modifiability.
Constraints: Small team, Python-only backend, cloud-hosted, must serve mobile and desktop users, health data is legally sensitive (GDPR/HIPAA-adjacent obligations apply).
________________________________________
Major Design Decision Log
#	Decision	Alternatives Considered	Chosen Option	Rationale	Downside / Risk
D1	Backend framework	Flask, Django, FastAPI	Django	Built-in ORM, admin panel, auth system, and established security defaults reduce boilerplate for a health app	Heavier than Flask; overkill if scope stays small
D2	AI symptom engine	Build own model, use OpenAI API, use Google Vertex AI	OpenAI API (GPT-4o)	Fastest to integrate, well-documented, high accuracy for medical Q&A	Vendor lock-in; per-token cost scales with users; no offline fallback
D3	Database	PostgreSQL, MySQL, MongoDB	PostgreSQL	Relational integrity for linked medical records; supports JSON columns if schema flexibility is needed; excellent Django ORM support	Requires more schema planning up front than NoSQL
D4	Video consultation	Build WebRTC from scratch, Daily.co, Twilio, Agora	Daily.co or Twilio Video API	Both offer HIPAA-eligible infrastructure, fast SDKs, and handle signalling complexity	Monthly cost; users depend on third-party uptime
D5	Hosting	Heroku, AWS, Railway	AWS (EC2 + RDS + S3)	Mature, HIPAA-eligible, fine-grained IAM; scales well	Significantly more complex to configure than Heroku; defer until MVP is proven
D6	Notification delivery	In-process scheduler, Celery + Redis, external cron	Celery + Redis	Decouples reminder logic from request cycle; retries on failure; scales independently	Adds Redis dependency and worker infrastructure
Deferred decisions (do not commit yet):
•	Whether to build a native mobile app (defer until web usage data justifies it).
•	Multi-tenancy for clinic operators (defer until B2B demand is confirmed).
•	Caching layer (Redis already used for Celery; evaluate adding query caching at scale milestone, not now).
________________________________________
Risk Register
Risk	Likelihood	Impact	Mitigation
AI gives dangerous medical advice	Medium	Critical	Add a hard disclaimer on every AI response; never let AI confirm diagnoses — only suggest specialties
Health data breach	Medium	Critical	Encrypt PII at rest (Django's model-level encryption or AWS KMS); enforce HTTPS everywhere; no logging of symptom text
AI API goes down	Low	High	Add a fallback UI state: "AI unavailable — please describe your issue to a doctor directly"
Doctor availability data is stale	High	Medium	Cache availability for maximum 5 minutes; show "last updated" timestamp
Notification spam frustrates users	Medium	Medium	Allow users to pause or delete reminder schedules; rate-limit reminders per day
Technical debt in monolith	Low now / High later	Medium	Use Django apps as bounded modules so each domain (pharmacy, consultations, reminders) can be extracted later
________________________________________
2. Technical Leadership & Coordination
Technical Roadmap
Phase 1 — Foundation (Weeks 1–3) Establish shared infrastructure: Django project scaffold, PostgreSQL schema, user auth (Django Allauth), CI pipeline, and deployment to a staging environment. No AI, no video yet. This phase must be done before anything else — it's the load-bearing foundation.
Phase 2 — Core Flows (Weeks 4–7) Build the two primary user journeys end-to-end: (a) symptom → AI suggestion → book consultation, and (b) search medicine → order → generate reminders. Use mocked doctor data and a basic Celery worker for reminders.
Phase 3 — Integrations (Weeks 8–10) Wire in the real OpenAI API, the Video API, and the Notification Service (push/email/SMS). Harden the reminder scheduler. Add basic encryption for PII fields.
Phase 4 — Quality & Scale (Weeks 11–13) Accessibility audit, performance profiling, security review, load testing, and migration from Heroku staging to AWS production.
________________________________________
Standards & Conventions
Every developer on this project must follow these conventions consistently:
Naming: Django app names are singular nouns (consultation, pharmacy, reminder, account). Model names are PascalCase singular (ConsultationBooking, MedicineOrder). URL patterns use kebab-case (/api/consultations/book/).
API contract: All backend endpoints return a standard envelope: { "status": "ok"|"error", "data": {…}, "message": "…" }. Never return raw model serializations.
AI responses: Every response from the AI module must be wrapped in a MedicalAdviceWrapper that appends the legal disclaimer before it reaches the frontend. This is non-negotiable and enforced in the service layer, not the view.
Frontend state: The AI chat component must maintain a sessionId per conversation and send it with each message so the backend can log complete sessions for audit purposes.
Shared vocabulary:
Term	Plain-language definition
Triage session	A single AI conversation where a user describes symptoms and receives a specialty recommendation
Consultation booking	A scheduled video meeting between one patient and one doctor
Prescription schedule	A reminder plan auto-generated from a medicine order, defining when and how often to take each item
Availability slot	A 30-minute window on a doctor's calendar marked as bookable
MedLinka user	Any registered person — patient or doctor — with an account
________________________________________
Now here is the high-level system context, showing MedLinka and everything it touches:
V
visualize
V
visualize show_widget
________________________________________
3. Documenting the Architecture — The 4+1 Views
View 1: Logical View (What the system does)
This view shows the major functional modules and how they relate to each other. Each box is a bounded domain — think of these as Django apps.
V
visualize
V
visualize show_widget
View 2: Process View — Scenario A: Symptom → Consultation
This sequence shows exactly what happens at runtime when a patient submits symptoms, receives an AI suggestion, and books a doctor. Click any node to explore further.
V
visualize
V
visualize show_widget
View 3: Development View — Package Structure
This is the map a developer needs to navigate the codebase. Every new team member should be shown this diagram on day one.
V
visualize
V
visualize show_widget
View 4: Physical / Deployment View
This shows where all software actually runs in production on AWS.
V
visualize
V
visualize show_widget
________________________________________
4. Iteration & Evaluation
Quality Attribute Tree — Priority Matrix
The following interactive chart maps each quality goal, its weight, and whether the current architecture serves it well. Click any bar to drill deeper.
V
visualize
V
visualize show_widget
________________________________________
Stimulus-Response Scenarios
These are the validation tests for the architecture. Each one must pass before the system is considered production-ready.
#	Quality Goal	Stimulus	Environment	Response	Measurable Target
S1	Security	Attacker submits a crafted JWT with an expired token	Production	Server returns 401; no data is returned	100% of expired tokens rejected
S2	Reliability	User submits a medicine order with no items in cart	Normal load	Server returns 400 with a clear validation error; no empty order written to DB	0 empty orders in database
S3	Performance	100 users simultaneously open the dashboard	Normal conditions	Dashboard loads key data within 2 seconds	p95 < 2,000ms
S4	Reliability	Celery worker crashes mid-reminder send	Background processing	Task is retried up to 3 times; failure is logged to Sentry	0 silent failures
S5	Modifiability	Team switches from OpenAI to Anthropic Claude API	Development	Only ai_triage/service.py changes; all tests pass	≤1 file changed outside ai_triage/
S6	Accessibility	Elderly user navigates booking form using keyboard only	Mobile browser	All form fields reachable via Tab; all controls have visible focus indicators	WCAG AA pass in axe-core
________________________________________
What to Prototype First
Uncertainty is highest in two areas — prototype these before committing the full design:
Prototype 1 — AI triage safety wrapper. Build a minimal endpoint that takes a symptom string, calls OpenAI, and returns the disclaimer-wrapped response. The risk is that the AI returns dangerous or confusing output. You need to see real responses before you can design the disclaimer copy and the handoff CTA properly. Estimated: 2 days.
Prototype 2 — Celery reminder scheduling. Build a standalone Celery task that generates a reminder schedule from a mock prescription and dispatches a test notification. The risk is that the scheduler logic is more complex than expected (timezone handling, dose frequencies, snooze logic). Estimate: 2–3 days.
Everything else — the booking flow, the pharmacy store, the auth — is well-understood Django CRUD work that does not carry significant architectural risk. Build those in the main codebase, not as throwaway prototypes.
________________________________________
Next Iteration Priorities
After an initial working build, these are the things the architecture must revisit — in order:
1.	Observability first. Add structured logging and Sentry error tracking. Flying blind in a health app is unacceptable and this is the biggest current gap.
2.	PII encryption. Before any real patient data enters the system, field-level encryption on health-related columns must be in place.
3.	Video API abstraction. Wrap the video provider behind an interface the same way the AI provider is wrapped, so switching vendors doesn't cascade through the codebase.
4.	Load testing. Run Locust against the two primary scenarios at 100 and 500 concurrent users before go-live.
5.	Doctor-facing interface. The current design is patient-centric. The architecture needs a clear answer for how doctors log in, manage their calendar, and receive booking notifications — this is a separate user journey that needs its own process view.

