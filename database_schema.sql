-- Supabase Database Schema for Inbox Clarity
-- Run this SQL in your Supabase SQL editor to set up the required tables

-- Create users table for tracking usage
CREATE TABLE IF NOT EXISTS users (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id TEXT UNIQUE NOT NULL, -- This will be the OAuth token/user identifier
    encrypted_refresh_token TEXT, -- Encrypted OAuth refresh token
    daily_processed_count INTEGER DEFAULT 0,
    last_processed_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for faster lookups
CREATE INDEX IF NOT EXISTS idx_users_user_id ON users(user_id);
CREATE INDEX IF NOT EXISTS idx_users_last_processed_date ON users(last_processed_date);

-- Optional: Create table for storing classification results (for future features)
-- This table is not used in the MVP but can be useful for analytics
CREATE TABLE IF NOT EXISTS classified_emails (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(user_id),
    email_id_from_gmail TEXT NOT NULL,
    category TEXT NOT NULL,
    subject TEXT,
    sender TEXT,
    snippet TEXT,
    classified_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for classified_emails
CREATE INDEX IF NOT EXISTS idx_classified_emails_user_id ON classified_emails(user_id);
CREATE INDEX IF NOT EXISTS idx_classified_emails_category ON classified_emails(category);

-- Enable Row Level Security (RLS) for security
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE classified_emails ENABLE ROW LEVEL SECURITY;

-- Create policies for RLS (users can only access their own data)
CREATE POLICY "Users can view own data" ON users
    FOR SELECT USING (user_id = current_setting('request.jwt.claims', true)::json->>'sub');

CREATE POLICY "Users can update own data" ON users
    FOR UPDATE USING (user_id = current_setting('request.jwt.claims', true)::json->>'sub');

CREATE POLICY "Users can insert own data" ON users
    FOR INSERT WITH CHECK (user_id = current_setting('request.jwt.claims', true)::json->>'sub');

-- Note: The backend uses the service role key which bypasses RLS,
-- so these policies are mainly for future direct frontend access if needed

-- Create a function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to automatically update updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
