# Scaling Notes (Overview)

- Replace SQLite with managed DB (RDS / Cloud SQL); use connection pooling.
- Add message queue (RabbitMQ / SQS) for help-request events. Supervisor notifications go through queue/worker.
- Use Redis for caching KB and fuzzy search indexes.
- Use background worker (Celery / RQ) for timeouts and heavy tasks.
- Use authentication/role-based access for supervisor UI.
- Use LiveKit real integration for live transfer/hold flows and Twilio for telephony if needed.

# Notes
This generated code is intentionally pragmatic and minimal to meet the assignment constraints.

# Optional Enhancements
- Expand KB fuzzy matching to use rapidfuzz for higher accuracy.
- Add OpenAI or LLM-based answer synthesis into `ai_agent` (requires API key).
- Replace simulated notifications with real webhook examples (ngrok + receiver).
