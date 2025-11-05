# Numerologist AI - Development Makefile
# This Makefile provides convenient commands for development workflow

.PHONY: help dev backend mobile docker-up docker-down test clean db-migrate db-upgrade db-downgrade db-current db-history db-revision

# Default target
help:
	@echo "Numerologist AI Development Commands"
	@echo ""
	@echo "  make help          - Show this help message"
	@echo "  make dev           - Start full development environment"
	@echo "  make backend       - Start backend API server only"
	@echo "  make mobile        - Start mobile app dev server only"
	@echo "  make docker-up     - Start PostgreSQL + Redis containers"
	@echo "  make docker-down   - Stop Docker containers"
	@echo "  make test          - Run all tests (backend + mobile)"
	@echo "  make clean         - Clean up generated files and caches"
	@echo ""
	@echo "Database Migration Commands:"
	@echo "  make db-migrate       - Auto-generate migration from model changes"
	@echo "  make db-upgrade       - Apply all pending migrations"
	@echo "  make db-downgrade     - Rollback last migration"
	@echo "  make db-current       - Show current migration version"
	@echo "  make db-history       - Show migration history"
	@echo "  make db-revision MSG='description' - Create empty migration"
	@echo ""
	@echo "Quick Start:"
	@echo "  make dev           # Starts everything needed for development"
	@echo ""

# Start full development environment
dev: docker-up
	@echo "Starting Numerologist AI Development Environment..."
	@echo ""
	@echo "🔧 Backend will start on http://localhost:8000"
	@echo "📚 API Docs available at http://localhost:8000/docs"
	@echo "📱 Mobile app will start via Expo"
	@echo ""
	@echo "Press 'w' in Expo terminal for web preview, or scan QR code"
	@echo ""
	@echo "Starting services in parallel..."
	@$(MAKE) backend & $(MAKE) mobile

# Start backend only
backend:
	@echo "🔧 Starting Backend (FastAPI)..."
	cd backend && uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Start mobile app only
mobile:
	@echo "📱 Starting Mobile App (Expo)..."
	cd mobile && npm start

# Start Docker services
docker-up:
	@echo "🐳 Starting Docker services (PostgreSQL, Redis)..."
	docker-compose up -d
	@echo "✅ Docker services running"
	@echo "   PostgreSQL: localhost:5432"
	@echo "   Redis: localhost:6379"

# Stop Docker services
docker-down:
	@echo "🛑 Stopping Docker services..."
	docker-compose down
	@echo "✅ Docker services stopped"

# Run all tests
test:
	@echo "🧪 Running Backend Tests..."
	cd backend && uv run pytest
	@echo ""
	@echo "🧪 Running Mobile Tests..."
	cd mobile && npm test

# Clean up
clean:
	@echo "🧹 Cleaning up..."
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name ".pytest_cache" -delete
	cd mobile && rm -rf node_modules/.cache 2>/dev/null || true
	@echo "✅ Cleaned up successfully"

# Database Migration Commands
db-migrate:
	@echo "🔄 Auto-generating migration from model changes..."
	@if [ -z "$(MSG)" ]; then \
		echo "❌ Error: MSG is required. Usage: make db-migrate MSG='description'"; \
		exit 1; \
	fi
	cd backend && uv run alembic revision --autogenerate -m "$(MSG)"
	@echo "✅ Migration created. Review the file before applying!"

db-upgrade:
	@echo "⬆️  Applying all pending migrations..."
	cd backend && uv run alembic upgrade head
	@echo "✅ Database is up to date"

db-downgrade:
	@echo "⬇️  Rolling back last migration..."
	cd backend && uv run alembic downgrade -1
	@echo "✅ Rolled back one migration"

db-current:
	@echo "📍 Current migration version:"
	cd backend && uv run alembic current

db-history:
	@echo "📜 Migration history:"
	cd backend && uv run alembic history

db-revision:
	@echo "📝 Creating empty migration..."
	@if [ -z "$(MSG)" ]; then \
		echo "❌ Error: MSG is required. Usage: make db-revision MSG='description'"; \
		exit 1; \
	fi
	cd backend && uv run alembic revision -m "$(MSG)"
	@echo "✅ Empty migration created"

.DEFAULT_GOAL := help
