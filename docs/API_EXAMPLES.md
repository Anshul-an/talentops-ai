# TalentOps AI — API Examples

### Health Check
```bash
curl http://localhost:8000/api/health
curl http://localhost:8000/api/health/detailed
curl http://localhost:8000/api/version
```

### Candidates Search & Notes
```bash
curl "http://localhost:8000/api/candidates/search?q=python"
curl -X POST http://localhost:8000/api/candidates/1/notes -H "Content-Type: application/json" -d '{"note": "Strong match"}'
curl http://localhost:8000/api/candidates/1/notes
```

### Fitment Scoring
```bash
curl -X POST http://localhost:8000/api/score -H "Content-Type: application/json" -d '{"job_id": 1, "candidate_ids": [1]}'
```

### Pre-screening Chat
```bash
curl -X POST http://localhost:8000/api/chat/1 -H "Content-Type: application/json" -d '{"message": "Hello"}'
curl -X POST http://localhost:8000/api/chat/1/reset
```

### Scheduling
```bash
curl http://localhost:8000/api/interviews
curl -X POST "http://localhost:8000/api/interviews/book/1?slot_id=slot-mon-1000"
```
