# Docker Setup Guide

## Quick Start with Docker Compose

### 1. Configure your database connection:
Edit `.env` and add your Neon connection string:
```bash
DATABASE_URL=postgresql://user:password@your-neon-host.neon.tech/dbname?sslmode=require
```

### 2. Build and start the service:
```bash
docker compose up --build
```

This will start:
- **FastAPI application** on port 8000 (connected to your Neon database)

### 2. Test the API:
```bash
# Test endpoint
curl http://localhost:8000/test

# Health check
curl http://localhost:8000/health

# View interactive docs
open http://localhost:8000/docs
```

## Common Commands

### Start services in background:
```bash
docker compose up -d
```

### View logs:
```bash
# View API logs
docker compose logs -f api
```

### Stop services:
```bash
docker compose down
```

### Restart the service:
```bash
docker compose restart
```

### Rebuild after code changes:
```bash
docker compose up --build
```

## Database Access

Your FastAPI app connects to your Neon database using the `DATABASE_URL` in `.env`.

To connect directly to Neon, use the connection string from your Neon dashboard.

## Development Mode

The docker-compose setup includes:
- **Hot reload** - Code changes in `app/` automatically restart the server
- **Volume mounting** - Your local `app/` directory is mounted into the container
- **Environment variables** - Loaded from `.env` file

## Production Build

For production, you can build and run just the API:

```bash
# Build the image
docker build -t brandvoice-api .

# Run the container
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql://user:pass@host:5432/db \
  brandvoice-api
```

## Troubleshooting

### Port already in use:
If port 8000 is already in use, edit `docker-compose.yml`:
```yaml
ports:
  - "8001:8000"  # Change host port
```

### Database connection issues:
- Verify your Neon connection string in `.env`
- Make sure the connection string includes `?sslmode=require`
- Check Neon dashboard for database status

### Reset everything:
```bash
docker compose down -v
docker compose up --build
```

