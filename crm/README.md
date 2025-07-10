# CRM Application Setup Guide

This guide provides instructions for setting up and running the CRM application with all its scheduled tasks and background jobs.

## Prerequisites

- Python 3.8+
- Django 4.2+
- Redis server
- Git

## Installation Steps

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Install and Start Redis

For Ubuntu/Debian:
```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

For macOS (using Homebrew):
```bash
brew install redis
brew services start redis
```

### 3. Database Setup

Run Django migrations:
```bash
python manage.py migrate
```

### 4. Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

### 5. Start the Django Development Server

```bash
python manage.py runserver
```

The GraphQL endpoint will be available at `http://localhost:8000/graphql`

## Background Tasks Setup

### 1. Celery Worker

In a new terminal, start the Celery worker:

```bash
celery -A crm worker -l info
```

### 2. Celery Beat Scheduler

In another terminal, start the Celery Beat scheduler:

```bash
celery -A crm beat -l info
```

### 3. Django Crontab Setup

Add the cron jobs to your system crontab:

```bash
python manage.py crontab add
```

To view the scheduled cron jobs:

```bash
python manage.py crontab show
```

To remove cron jobs:

```bash
python manage.py crontab remove
```

## Manual Script Execution

### Customer Cleanup Script

Run manually:
```bash
./crm/cron_jobs/clean_inactive_customers.sh
```

### Order Reminders Script

Run manually:
```bash
cd /path/to/project
python crm/cron_jobs/send_order_reminders.py
```

## Log Files

The following log files are created in `/tmp/`:

- `/tmp/customer_cleanup_log.txt` - Customer cleanup logs
- `/tmp/order_reminders_log.txt` - Order reminder logs
- `/tmp/crm_heartbeat_log.txt` - System heartbeat logs
- `/tmp/low_stock_updates_log.txt` - Low stock update logs
- `/tmp/crm_report_log.txt` - Weekly CRM report logs

## Verification

### 1. Check GraphQL Endpoint

Visit `http://localhost:8000/graphql` in your browser to access the GraphQL playground.

### 2. Test Queries

Try this basic query:
```graphql
query {
  hello
  allCustomers {
    edges {
      node {
        id
        name
        email
      }
    }
  }
}
```

### 3. Monitor Logs

Check the log files periodically to ensure all scheduled tasks are running:

```bash
tail -f /tmp/crm_heartbeat_log.txt
tail -f /tmp/crm_report_log.txt
```

## Troubleshooting

### Redis Connection Issues

Check if Redis is running:
```bash
redis-cli ping
```

Should return `PONG`.

### Celery Issues

If Celery tasks are not running, check:
1. Redis is running and accessible
2. Celery worker is running
3. Django settings are correct

### Cron Job Issues

If cron jobs are not executing:
1. Check cron job syntax: `python manage.py crontab show`
2. Verify script permissions: `ls -la crm/cron_jobs/`
3. Check system cron logs: `sudo tail -f /var/log/cron`

## Development

### Adding New Scheduled Tasks

1. **Django Crontab**: Add to `CRONJOBS` in `settings.py`
2. **Celery Beat**: Add to `CELERY_BEAT_SCHEDULE` in `settings.py`
3. **Shell Scripts**: Create in `crm/cron_jobs/` and add to crontab files

### Testing

Run the Django test suite:
```bash
python manage.py test
```

## Production Deployment

For production deployment:

1. Use a production Redis instance
2. Configure Celery with proper broker settings
3. Use a process manager like Supervisor for Celery workers
4. Set up proper logging and monitoring
5. Configure system cron jobs with appropriate user permissions
