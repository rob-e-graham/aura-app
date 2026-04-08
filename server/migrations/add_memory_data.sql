-- Add memory_data column to profiles for syncing personalization memory
-- Run this in Supabase SQL Editor
ALTER TABLE public.profiles
ADD COLUMN IF NOT EXISTS memory_data jsonb DEFAULT '{}';

-- The existing RLS policy "Users see own profile" already covers this column
-- since it's on the profiles table with: auth.uid() = id
