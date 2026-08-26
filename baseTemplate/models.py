# -*- coding: utf-8 -*-


from django.db import models

# Create your models here.


class version(models.Model):
    currentVersion = models.CharField(max_length=50)
    build = models.IntegerField()

class CyberPanelCosmetic(models.Model):
    MainDashboardCSS = models.TextField(default='')


class UserNotificationPreferences(models.Model):
    user = models.OneToOneField(
        'loginSystem.Administrator',
        on_delete=models.CASCADE,
        related_name='notification_preferences',
    )
    backup_notification_dismissed = models.BooleanField(
        default=False,
        help_text='Whether user has dismissed the backup notification',
    )
    ai_scanner_notification_dismissed = models.BooleanField(
        default=False,
        help_text='Whether user has dismissed the AI scanner notification',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'User Notification Preferences'
        verbose_name_plural = 'User Notification Preferences'

    def __str__(self):
        return 'Notification preferences for %s' % self.user_id
