# Document Insights API
A backend service that accepts document text, processes it asynchronously (simulated AI summarization), and returns structured summaries. Built with FastAPI, MongoDB, and Redis.
## Quick Start
```bash
# Clone the repository
git clone <repository-url>
cd document-insights-api
# Start all services
docker-compose up --build
# The API will be available at [localhost](http://localhost:8000)
# API documentation at [localhost](http://localhost:8000/docs)
