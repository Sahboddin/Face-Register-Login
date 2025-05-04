from django.db import models

# Create your models here.
from django.contrib.auth.models import User

class UserImage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    face_image = models.ImageField( upload_to='user_faces/')

    
    def __str__(self):
        return self.user.username