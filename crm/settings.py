# crm/settings.py
# CRM-specific settings for django-crontab

from django.conf import settings

# Ensure django_crontab is in INSTALLED_APPS
if 'django_crontab' not in settings.INSTALLED_APPS:
    settings.INSTALLED_APPS += ['django_crontab']

# Cron Jobs Configuration
CRONJOBS = [
    ('*/5 * * * *', 'crm.cron.log_crm_heartbeat'),
    ('0 */12 * * *', 'crm.cron.update_low_stock'),
]

# Add to main settings if not already there
if not hasattr(settings, 'CRONJOBS'):
    settings.CRONJOBS = CRONJOBS
else:
    settings.CRONJOBS.extend(CRONJOBS)
