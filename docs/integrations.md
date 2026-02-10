# Integrations

## PubMed
- Use NCBI E-utilities (esearch + efetch).
- Ingest on a schedule and store metadata in `sources`.
- Track last sync timestamps to avoid re-fetching.

## Supabase
- Postgres + pgvector for retrieval.
- Service role key for backend services.
- RLS for all user-facing tables.

## Lovable
- Use Supabase as the single source of truth.
- Expose read-only views for content browsing.
- Keep bot and agent logs visible for admins only.

## Telegram
- Bot Gateway handles webhooks and routing.
- Moderator runs before response delivery.
- Store all messages and decisions in Supabase.
