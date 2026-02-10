# Agents

## Scout-Analyst
- Purpose: find and ingest PubMed news and abstracts.
- Inputs: keyword profiles, date range, journal filters.
- Outputs: normalized records with PMID, title, abstract, keywords.
- Tools: PubMed E-utilities, deduplication, metadata tagging.

## Medical Writer
- Purpose: scientific articles with citations.
- Inputs: selected sources, topic brief, target length.
- Outputs: structured article, references, limitations section.
- Rules: only cite sources present in Supabase.

## Creative Editor
- Purpose: blog content and marketing-friendly summaries.
- Inputs: Medical Writer draft, brand voice guidelines.
- Outputs: readable blog posts with simplified explanations.
- Rules: no medical claims without cited evidence.

## Telegram Bots

### Dr Drake (Protocols)
- Purpose: deliver approved protocols and safe guidance.
- Inputs: user questions and context.
- Outputs: protocol-based answers, citations, next steps.
- Rules: never diagnose, never prescribe.

### Moderator (Protection)
- Purpose: safety checks and abuse prevention.
- Inputs: raw user messages and bot outputs.
- Outputs: allow/block/flag decisions with reasons.
- Rules: escalate sensitive cases to a human channel.
