from django.db import models
from users.models import User


# Create your models here.

class Income(models.Model):
    SOURCE_OPTIONS = [
        ('SALARY', 'SALARY'),
        ('BONUS', 'BONUS'),
    ]

    source = models.CharField(choices=SOURCE_OPTIONS, max_length=255)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    owner = models.ForeignKey(to=User, related_name='income', on_delete=models.CASCADE)
    date = models.DateField(blank=False, null=False)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return str(self.owner) + '\'s income'
