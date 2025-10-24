# Architecture — HR Agent Prototype

But : prototype d'un agent RH (FAQ, recherche documentaire, chat LLM)

Composants :
- Backend : FastAPI (orchestration conversation, redaction PII, endpoints REST/WebSocket)
- Frontend : React (UI chat minimal)
- DB : Postgres (métadonnées)
- Vector DB : optionnel (Pinecone / Weaviate) pour embeddings
- Stockage : S3-compatible pour fichiers RH

RGPD & sécurité :
- Redaction PII configurable (REDACT_PII)
- Conservation des conversations configurable (CONVERSATION_RETENTION_DAYS)
- Hébergement recommandé : AWS (région EU) + Secrets Manager
- Logs sensibles masqués par défaut

Déploiement local :
1. Copier `.env.example` -> `.env` et remplir
2. docker-compose up --build
3. Backend : http://localhost:8000
4. Frontend : http://localhost:3000
