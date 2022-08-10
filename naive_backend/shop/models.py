from tkinter import CASCADE
from django.db import models


class Artist(models.Model):
    name = models.CharField(verbose_name='Имя',
                            max_length=250, null=False)
    date_of_birth = models.DateField()


class Artwork(models.Model):
    title = models.CharField(verbose_name='Название',
                             max_length=250)
    description = models.TextField(verbose_name='Описание')
    author = models.ForeignKey(Artist, related_name='artworks',
                               on_delete=models.CASCADE)
