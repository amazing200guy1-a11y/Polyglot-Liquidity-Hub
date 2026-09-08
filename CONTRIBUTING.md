# Contributing to Polyglot-Liquidity-Hub

## Architecture
```
                    ┌─────────────────────────┐
                    │   Next.js Operator UI   │
                    └──────────┬──────────────┘
                               │ REST / WebSocket
                    ┌──────────▼──────────────┐
                    │  Python FastAPI Gateway │
                    └──────────┬──────────────┘
                               │ gRPC
              ┌────────────────┼──────────────────┐
              │                │                  │
   ┌──────────▼──┐   ┌─────────▼──────┐  ┌───────▼──────┐
   │  Java LP    │   │  Go Net Layer  │  │  Risk Engine │
   │  Router     │   │  (ultra-low    │  │  (Python)    │
   │  (FIX/REST) │   │   latency)     │  │              │
   └─────────────┘   └───────────────-┘  └──────────────┘
```

## Component Setup

### Next.js Frontend
```bash
cd frontend-nextjs
npm install && npm run dev
```

### Python Microservice
```bash
cd microservice-python
pip install -r requirements.txt
uvicorn main:app --reload
```

### Java Network Layer
```bash
cd network-java
mvn package && java -jar target/liquidity-hub.jar
```

### Go Routing Layer
```bash
cd routing-go
go build ./... && go test ./...
```
