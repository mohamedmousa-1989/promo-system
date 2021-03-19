from django.db import models
from django.contrib.auth.models import User


class Promo(models.Model):
    """Model that represents a promo."""

    name = models.CharField(max_length=100)
    points = models.FloatField()
    recipient = models.ForeignKey(User, related_name='promos', on_delete=models.CASCADE, limit_choices_to={'is_staff': False},)
    points_used = models.FloatField(default=0.0)

    def __str__(self):
        """
        Unicode representation for a promo.

        :return: string
        """
        return self.name


