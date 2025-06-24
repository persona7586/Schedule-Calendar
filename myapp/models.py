from django.db import models

# Create your models here.
class Events(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255,null=True,blank=True)
    start = models.DateTimeField(null=True,blank=True)
    end = models.DateTimeField(null=True,blank=True)

    class Meta:
        db_table = "tblevents"

# 메인 페이지 메모 기능 추가
class Memo(models.Model):
    title      = models.CharField(max_length=255)
    content    = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table  = "tblmemo"
        ordering  = ['created_at']

    def __str__(self):
        return self.title