# Data Model (Supabase)

## Core Tables

### sources
- id (uuid)
- pmid (text, unique)
- title (text)
- abstract (text)
- journal (text)
- published_at (date)
- url (text)
- tags (text[])

### documents
- id (uuid)
- source_id (uuid, fk sources)
- content (text)
- language (text)
- created_at (timestamptz)

### embeddings
- id (uuid)
- document_id (uuid, fk documents)
- embedding (vector)
- model (text)

### agent_runs
- id (uuid)
- agent_name (text)
- input (jsonb)
- output (jsonb)
- model (text)
- status (text)
- started_at (timestamptz)
- finished_at (timestamptz)

### protocols
- id (uuid)
- title (text)
- version (text)
- content (text)
- sources (text[])
- status (text)

### bot_users
- id (uuid)
- platform (text)
- external_id (text)
- created_at (timestamptz)

### bot_messages
- id (uuid)
- user_id (uuid, fk bot_users)
- direction (text)
- content (text)
- created_at (timestamptz)

### moderation_actions
- id (uuid)
- message_id (uuid, fk bot_messages)
- decision (text)
- reason (text)
- created_at (timestamptz)

## Notes
- Add RLS policies for user and bot tables.
- Store all model outputs for auditability.
