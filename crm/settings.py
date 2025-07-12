# crm/settings.py
# CRM-specific settings for django-crontab

from django.conf import settings

# Ensure django_crontab is in INSTALLED_APPS
if 'django_crontab' not in settings.INSTALLED_APPS:
    settings.INSTALLED_APPS += ['django_crontab']

# Cron Jobs Configuration
CRONJOBS = [
    ('*/5 * * * *', 'crm.cron.log_crm_heartbeat'),
    ('0 */12 * * *', 'crm.cron.updatelowstock'),
]

# Add to main settings if not already there
if not hasattr(settings, 'CRONJOBS'):
    settings.CRONJOBS = CRONJOBS
else:
    settings.CRONJOBS.extend(CRONJOBS)

# Celery Beat Schedule Configuration
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    'generate-crm-report': {
        'task': 'crm.tasks.generatecrmreport',
        'schedule': crontab(day_of_week='mon', hour=6, minute=0),
    },
}

# Add to main settings if not already there
if not hasattr(settings, 'CELERY_BEAT_SCHEDULE'):
    settings.CELERY_BEAT_SCHEDULE = CELERY_BEAT_SCHEDULE
else:
    settings.CELERY_BEAT_SCHEDULE.update(CELERY_BEAT_SCHEDULE)
