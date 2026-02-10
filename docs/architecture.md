# Architecture

## High-Level Flow
1. Scout-Analyst pulls new PubMed items and stores metadata.
2. Content is normalized, chunked, and embedded.
3. Medical Writer and Creative Editor generate outputs with citations.
4. Telegram bots answer users using verified protocols and safety rules.
5. All runs, prompts, and outputs are logged in Supabase.

## Services
- Agent Orchestrator: schedules and runs agent jobs.
- Ingestion Service: PubMed fetch + parsing + deduplication.
- Knowledge Service: chunking, embeddings, and retrieval.
- Content Service: generation for articles and blogs.
- Bot Gateway: Telegram webhooks + moderation.

## Data Layer (Supabase)
- Postgres + pgvector for embeddings.
- Row-level security for user and bot data.
- Audit tables for prompts, outputs, and decisions.

## Retrieval Strategy
- Use hybrid search: metadata filters + vector similarity.
- Enforce citation rules for medical outputs.
- Maintain a curated "protocols" corpus for Dr Drake.

## Safety and Compliance
- Strict refusal rules for diagnosis and prescriptions.
- Moderator bot blocks disallowed topics and flags users.
- All decisions are logged with timestamps and model IDs.
