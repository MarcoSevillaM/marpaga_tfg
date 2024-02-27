# Codigo para las tareas programadas

from django_cron import CronJobBase, Schedule
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string
import time

# Tarea para eliminar los usuarios que no tenga la cuenta activada
class RemoveInactiveUsers(CronJobBase):
    RUN_EVERY_MINS = 1 # every 1 minute
    
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'marpaga.remove_inactive_users'    # a unique code

    def do(self):
        User.objects.filter(is_active=False).delete()