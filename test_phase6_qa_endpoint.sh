#!/bin/bash
curl -X POST http://localhost:8080/api/qa \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the main topic?",
    "documentIds": [6]
  }'
