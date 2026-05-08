# Supabase & Database Security Guide

Since you are building a backend to handle authentication, data access, and display for your Election Comparison System, it is highly important that you secure your Supabase database. Because Supabase provides an auto-generated API, it has specific security paradigms you need to be aware of.

## 1. Row Level Security (RLS)
This is the **most important** security feature in Supabase. By default, newly created tables in Supabase might be completely accessible if someone gets ahold of your `anon` public key. 

Because your election data is read-only for the public, you need to enable RLS and explicitly allow read access while blocking write access.

**Action Required in Supabase SQL Editor:**
```sql
-- Enable RLS on all tables
ALTER TABLE elections ENABLE ROW LEVEL SECURITY;
ALTER TABLE constituencies ENABLE ROW LEVEL SECURITY;
ALTER TABLE candidates ENABLE ROW LEVEL SECURITY;

-- Create a policy to allow ANYONE to read the data
CREATE POLICY "Allow public read access" ON elections FOR SELECT USING (true);
CREATE POLICY "Allow public read access" ON constituencies FOR SELECT USING (true);
CREATE POLICY "Allow public read access" ON candidates FOR SELECT USING (true);

-- (Do NOT create policies for INSERT, UPDATE, or DELETE. This means only your backend 
-- using the service_role key, or direct PostgreSQL connections, can modify the data)
```

## 2. API Keys (`anon` vs `service_role`)
Supabase provides two main API keys. Understanding where to use them is critical:

- **`anon` (Public Key):** Safe to put in your Frontend code (Next.js, React). It **is** bound by the Row Level Security (RLS) rules you set above. 
- **`service_role` (Secret Key):** This is the **God-mode key**. It entirely bypasses RLS. **Never expose this to the frontend**. You should only use this key in your secure backend server (or when running admin scripts like our python uploader).

## 3. Protect Your `.env` Variables
You currently have your direct Postgres Database Password and your `service_role` keys inside your `.env` file.
- **Never commit your `.env` file to GitHub.** 
- Make sure your `.gitignore` file contains `.env`.
- If your database password or `service_role` key is ever leaked, malicious actors can wipe out your entire database.

## 4. Backend Authentication & Data Access
Since you are building a backend:
- **Authentication:** You can use Supabase Auth. When a user logs in, Supabase issues a JWT (JSON Web Token). Your backend can verify this JWT to ensure the user is who they say they are.
- **Expensive Queries:** Historical election databases can result in massive queries (e.g., aggregating 60 years of data). Do not let the frontend directly hit the database for massive `GROUP BY` aggregations. Instead, have your backend perform these queries, perhaps cache the results in Redis or memory, and then serve the cached result to the frontend. This protects your database from Denial of Service (DoS) by thousands of people requesting heavy data.

## 5. Direct Database Connections (Connection Pooling)
When your backend connects to Supabase via `DATABASE_URL` (like we did with `psycopg2`), it uses a direct connection. PostgreSQL can only handle a certain number of concurrent direct connections.
- If your backend scales and has hundreds of concurrent users, you should use **Supabase's Connection Pooler (Supavisor)**. 
- You can find your Pooler connection string in your Supabase Dashboard under **Database -> Connection Pooling**. It uses port `6543` instead of `5432`. Use the pooled URL for your backend server when it goes to production.

## Summary Checklist for Production:
- [ ] RLS is ENABLED on `elections`, `constituencies`, and `candidates`.
- [ ] SELECT policies are set up so the public can view data.
- [ ] NO public policies exist for INSERT/UPDATE/DELETE.
- [ ] `.env` is added to `.gitignore`.
- [ ] Frontend only uses the `anon` key.
- [ ] Backend uses `service_role` OR the Connection Pooler URL.
