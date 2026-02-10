# BioPeptidePlus AI Ecosystem

This repository initializes the BioPeptidePlus AI ecosystem: a network of AI agents, Telegram bots, and a data layer integrated with Supabase and Lovable.

## Goals
- Discover and index relevant biomedical research (PubMed).
- Generate scientific articles and consumer-facing blogs.
- Deliver clinical protocols and safe responses via Telegram bots.
- Provide a unified data and audit layer in Supabase.

## Core Components
- Scout-Analyst: discovery and ingestion of PubMed sources.
- Medical Writer: scientific article drafts with citations.
- Creative Editor: blog posts and marketing-friendly outputs.
- Telegram bots: Dr Drake (protocols) and Moderator (safety).
- Supabase: data storage, auth, and audit trail.
- Lovable: product UI integrated with Supabase.

## Repository Structure
- `docs/` architecture, agents, data model, integrations, roadmap

## Next Steps
1. Finalize data model and event flows.
2. Choose the execution runtime for agents (Node or Python).
3. Implement Supabase schema and seed data.
4. Build ingestion pipeline for PubMed.
5. Launch Telegram bots with moderation gate.
