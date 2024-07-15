from django.db import models

from .repetition import Repetition


class Advice(models.Model):
    repetition = models.ForeignKey(Repetition, related_name='advice', on_delete=models.CASCADE)
    category = models.TextField()
    text = models.TextField()
    correction_level = models.IntegerField()

    def __str__(self):
        return f"Advice of type {self.category} for repetition {self.repetition.id} with level {self.correction_level}"
