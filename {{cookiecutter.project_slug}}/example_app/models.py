from base.models import BaseDatabaseModel
from django.db import models
from pydantic import BaseModel


# Create your models here.
class User(BaseDatabaseModel):
    user_id = models.CharField(max_length=8, unique=True)
    username = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    password = models.CharField(max_length=255)

    class Meta:
        db_table = "t_user"


class PydanticUser(BaseModel):
    user_id: str
    username: str
    email: str
    password: str
