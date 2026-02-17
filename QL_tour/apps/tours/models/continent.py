from django.db import models

class Continent(models.Model):
    code = models.CharField(max_length=2)
    name = models.CharField()

    def __str__(self) -> str:
        return f"{self.name}"