-- ============================================================
-- AURA App — Supabase Database Schema (ACTUAL — already deployed)
-- Project: https://jbabssesevowywncmtcm.supabase.co
-- ============================================================
-- This file documents the schema that is already in Supabase.
-- The server code (server.js) maps to these exact table/column names.

-- Users profile (extends Supabase auth.users)
create table public.profiles (
  id uuid references auth.users(id) on delete cascade primary key,
  display_name text,
  birth_date date,
  element text check (element in ('fire','water','earth','air')),
  intention text,
  created_at timestamptz default now()
);

-- Entitlements / subscription tier
create table public.user_entitlements (
  id uuid default gen_random_uuid() primary key,
  user_id uuid references public.profiles(id) on delete cascade unique,
  tier text default 'free' check (tier in ('free','premium','pro')),
  revenuecat_id text,
  expires_at timestamptz,
  updated_at timestamptz default now()
);

-- Usage tracking (resets monthly)
-- Server maps: ai_tokens_limit → monthly_allowance, ai_tokens_used → monthly_used,
--              ai_tokens_bonus → bonus_tokens, storage_limit/used/bonus → memory
create table public.user_usage (
  id uuid default gen_random_uuid() primary key,
  user_id uuid references public.profiles(id) on delete cascade unique,
  ai_tokens_used integer default 0,
  ai_tokens_limit integer default 0,
  ai_tokens_bonus integer default 0,
  storage_used integer default 0,
  storage_limit integer default 0,
  storage_bonus integer default 0,
  period_reset_at timestamptz default (date_trunc('month', now()) + interval '1 month')
);

-- Reading history
create table public.readings (
  id uuid default gen_random_uuid() primary key,
  user_id uuid references public.profiles(id) on delete cascade,
  cards_drawn text[],
  question text,
  ai_response text,
  is_saved boolean default false,
  created_at timestamptz default now()
);

-- Journal entries
create table public.journal_entries (
  id uuid default gen_random_uuid() primary key,
  user_id uuid references public.profiles(id) on delete cascade,
  content text,
  linked_reading_id uuid references public.readings(id),
  created_at timestamptz default now()
);

-- Auto-create profile + usage + entitlement when user signs up
create or replace function public.handle_new_user()
returns trigger as $$
begin
  insert into public.profiles (id) values (new.id);
  insert into public.user_entitlements (user_id) values (new.id);
  insert into public.user_usage (user_id) values (new.id);
  return new;
end;
$$ language plpgsql security definer;

create trigger on_auth_user_created
  after insert on auth.users
  for each row execute procedure public.handle_new_user();

-- Row level security (users can only see their own data)
alter table public.profiles enable row level security;
alter table public.user_entitlements enable row level security;
alter table public.user_usage enable row level security;
alter table public.readings enable row level security;
alter table public.journal_entries enable row level security;

create policy "Users see own profile" on public.profiles for all using (auth.uid() = id);
create policy "Users see own entitlements" on public.user_entitlements for all using (auth.uid() = user_id);
create policy "Users see own usage" on public.user_usage for all using (auth.uid() = user_id);
create policy "Users see own readings" on public.readings for all using (auth.uid() = user_id);
create policy "Users see own journal" on public.journal_entries for all using (auth.uid() = user_id);
