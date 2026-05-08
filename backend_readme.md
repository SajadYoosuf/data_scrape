# Election Comparison System - Backend Architecture & Security Guide

## 1. System Design Philosophy
The backend acts as the secure intermediary between the raw historical data stored in Supabase and the rich visualizations rendered on the frontend. While Supabase provides an auto-generated API, a dedicated backend is crucial for this project because historical election data requires heavy mathematical aggregations that shouldn't be executed directly by public client devices.

### Recommended Tech Stack
- **Framework:** Node.js (Express/NestJS), Python (FastAPI), or Next.js API Routes.
- **Caching:** Redis (to store results of expensive 60-year aggregate queries).
- **Database Client:** Supabase SDK (for auth/REST) and `psycopg2`/`pg` (for complex raw SQL).

## 2. Core Backend Responsibilities
- **Data Aggregation:** Compute heavy statistics like "Swing Seats", "Decade-over-Decade Party Growth", and "Voter Turnout Trends" before sending the JSON to the frontend.
- **Caching Layer:** A single 60-year aggregate query might take a few seconds to run on PostgreSQL. The backend must run this *once*, cache the result in Redis, and serve the cached version to the thousands of concurrent users.
- **Rate Limiting:** Protect the database from DoS attacks by rate-limiting IP addresses requesting expensive calculation endpoints.

## 3. Security Guidelines
Security is the most critical aspect of the backend design. Follow these strict rules:

### A. Row Level Security (RLS)
Even if you use a backend, you must enable RLS on the Supabase database.
- Go to the Supabase SQL editor and run `ALTER TABLE ... ENABLE ROW LEVEL SECURITY;` on `elections`, `constituencies`, and `candidates`.
- Create a `SELECT` policy allowing public read access. **Do not create INSERT/UPDATE/DELETE policies.**

### B. Managing API Keys
- **Service Role Key:** Use the Supabase `service_role` key **only** in this backend environment. This key bypasses RLS and allows your backend to perform administrative tasks.
- **Anon Key:** The backend can issue the `anon` key to the frontend.

### C. Connection Pooling
If your backend uses a direct PostgreSQL connection string (like Prisma, SQLAlchemy, or `psycopg2`), you **must** use the Supabase Connection Pooler URL (usually runs on port `6543`). Direct connections (port `5432`) will crash the database if your backend spawns too many concurrent workers.

### D. Authentication
If the system expands to allow users to "Save their favorite analysis" or "Export data to CSV":
- Use Supabase Auth.
- The frontend will send a JWT (JSON Web Token) in the `Authorization: Bearer <token>` header.
- The backend must verify this JWT before serving premium features or writing user data.
