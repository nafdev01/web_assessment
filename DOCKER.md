# Docker Setup Guide

This guide explains how to run the Web Assessment application using Docker.

## Prerequisites

- Docker (version 20.10 or higher)
- Docker Compose (version 2.0 or higher)

## Quick Start

### 1. Configure Environment Variables

Copy the example environment file and update it with your settings:

```bash
cp .env.example .env
```

Edit `.env` and update the following important variables:

```bash
# PostgreSQL - Change these for security
POSTGRES_PASSWORD=your_secure_password_here

# Django - Generate a new secret key
DJANGO_SECRET_KEY=your_django_secret_key_here_change_in_production

# Superuser - Change these credentials
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@example.com
DJANGO_SUPERUSER_PASSWORD=admin123

# Email - Configure your SMTP settings
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
```

### 2. Build and Start Services

Build and start all services in detached mode:

```bash
docker-compose up -d --build
```

This will start:

- **PostgreSQL** database (port 5432)
- **Redis** server (port 6379)
- **Django web** application (port 8000)
- **Celery worker** for background tasks
- **Celery beat** for scheduled tasks

### 3. Access the Application

Once all services are running, access the application at:

```
http://localhost:8000
```

Admin panel:

```
http://localhost:8000/admin
```

Use the superuser credentials from your `.env` file to log in.

## Docker Commands

### View Running Containers

```bash
docker-compose ps
```

### View Logs

View logs for all services:

```bash
docker-compose logs -f
```

View logs for a specific service:

```bash
docker-compose logs -f web
docker-compose logs -f celery_worker
docker-compose logs -f db
```

### Stop Services

Stop all services:

```bash
docker-compose down
```

Stop and remove volumes (⚠️ this will delete your database):

```bash
docker-compose down -v
```

### Restart Services

Restart all services:

```bash
docker-compose restart
```

Restart a specific service:

```bash
docker-compose restart web
```

### Execute Commands in Containers

Run Django management commands:

```bash
docker-compose exec web python manage.py <command>
```

Examples:

```bash
# Create migrations
docker-compose exec web python manage.py makemigrations

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser manually
docker-compose exec web python manage.py createsuperuser

# Open Django shell
docker-compose exec web python manage.py shell

# Collect static files
docker-compose exec web python manage.py collectstatic
```

Access PostgreSQL:

```bash
docker-compose exec db psql -U postgres -d web_assessment
```

Access Redis CLI:

```bash
docker-compose exec redis redis-cli
```

### Rebuild After Code Changes

If you make changes to the code:

```bash
docker-compose restart web celery_worker celery_beat
```

If you change dependencies (requirements.txt):

```bash
docker-compose up -d --build
```

## Environment Variables Reference

### PostgreSQL Configuration

- `POSTGRES_DB` - Database name
- `POSTGRES_USER` - Database user
- `POSTGRES_PASSWORD` - Database password
- `POSTGRES_PORT` - PostgreSQL port (default: 5432)

### Redis Configuration

- `REDIS_HOST` - Redis host (default: redis)
- `REDIS_PORT` - Redis port (default: 6379)

### Django Configuration

- `DJANGO_SECRET_KEY` - Django secret key (required)
- `DEBUG` - Debug mode (True/False)
- `ALLOWED_HOSTS` - Comma-separated list of allowed hosts
- `SITE_URL` - Full site URL (e.g., http://localhost:8000)

### Superuser Configuration

- `DJANGO_SUPERUSER_USERNAME` - Admin username
- `DJANGO_SUPERUSER_EMAIL` - Admin email
- `DJANGO_SUPERUSER_PASSWORD` - Admin password

### Email Configuration

- `EMAIL_HOST` - SMTP server
- `EMAIL_HOST_USER` - SMTP username
- `EMAIL_HOST_PASSWORD` - SMTP password
- `EMAIL_PORT` - SMTP port (default: 587)
- `EMAIL_USE_TLS` - Use TLS (True/False)
- `DEFAULT_FROM_EMAIL` - Default sender email

### Port Mappings

- `WEB_PORT` - Web application port (default: 8000)
- `POSTGRES_PORT` - PostgreSQL port mapping (default: 5432)
- `REDIS_PORT` - Redis port mapping (default: 6379)

## Troubleshooting

### Database Connection Issues

If you see database connection errors, ensure PostgreSQL is ready:

```bash
docker-compose logs db
```

### Port Already in Use

If port 8000, 5432, or 6379 is already in use, change the port in `.env`:

```bash
WEB_PORT=8001
POSTGRES_PORT=5433
REDIS_PORT=6380
```

### Reset Database

To completely reset the database:

```bash
docker-compose down -v
docker-compose up -d --build
```

### View Container Resource Usage

```bash
docker stats
```

## Production Deployment

For production deployment:

1. **Update `.env` file:**
   - Set `DEBUG=False`
   - Generate a strong `DJANGO_SECRET_KEY`
   - Set strong passwords for database and superuser
   - Configure proper `ALLOWED_HOSTS`
   - Set up proper email configuration

2. **Use a reverse proxy** (nginx/traefik) in front of the Django application

3. **Enable HTTPS** with SSL certificates

4. **Set up proper backups** for PostgreSQL data volume

5. **Monitor logs** and set up log aggregation

6. **Consider using** managed services for PostgreSQL and Redis in production

## Data Persistence

Docker volumes are used to persist data:

- `postgres_data` - PostgreSQL database
- `redis_data` - Redis data
- `static_volume` - Static files
- `media_volume` - Media uploads

These volumes persist even when containers are stopped or removed (unless you use `docker-compose down -v`).

## Development vs Production

### Development Mode

In `.env`:

```bash
DEBUG=True
DEVELOPMENT_MODE=True
```

### Production Mode

In `.env`:

```bash
DEBUG=False
DEVELOPMENT_MODE=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
SITE_URL=https://yourdomain.com
```

## Support

For issues or questions, check the logs:

```bash
docker-compose logs -f
```
