from django.db import models

class Task(models.Model):
    code = models.CharField(max_length=100, blank=True)
    name = models.CharField(max_length=100, blank=True)

class Image(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)

    label = models.CharField(max_length=100, blank=True)
    src = models.TextField(blank=True)
    vertical_division = models.IntegerField(null=False)
    rects_list = models.TextField(blank=True)
