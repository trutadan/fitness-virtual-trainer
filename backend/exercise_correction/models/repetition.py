import os

from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver

from exercise_correction.models.video import Video


class Repetition(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='repetitions')
    repetition = models.FileField(upload_to='processed_videos/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Repetition {self.id} of Video {self.video.id}"


# signal to delete repetition files when a Repetition is deleted
@receiver(pre_delete, sender=Repetition)
def delete_repetition_file(sender, instance, **kwargs):
    if instance.repetition:
        if os.path.isfile(instance.repetition.path):
            os.remove(instance.repetition.path)


# signal to delete main video file and all related repetition files when a Video is deleted
@receiver(pre_delete, sender=Video)
def delete_related_files(sender, instance, **kwargs):
    # delete the main video file
    if instance.video:
        if os.path.isfile(instance.video.path):
            os.remove(instance.video.path)

    # delete all related repetition files
    for repetition in instance.repetitions.all():
        if repetition.repetition:
            if os.path.isfile(repetition.repetition.path):
                os.remove(repetition.repetition.path)
