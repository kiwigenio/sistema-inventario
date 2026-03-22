from django.db import models

# Create your models here.
class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank = True, null = True)
    stock_actual = models.IntegerField(default=0)

    def __str__(self):
        return self.nombre
