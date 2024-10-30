import datetime
from django.db import models

def get_image_upload_bears(instance, filename):
    # 現在の年と次の月を取得
    year = datetime.datetime.now().year
    next_month = (datetime.datetime.now().month % 12) + 1
    return f"{year}/{next_month}/bear/{filename}"

class Bears(models.Model):
    date = models.DateField()
    title = models.CharField(max_length=255)
    content = models.TextField()
    image = models.ImageField(upload_to=get_image_upload_bears, blank=True, null=True)
    performers = models.TextField(blank=True, null=True) 
    
    def __str__(self):
        return self.title
    
def get_image_upload_sengoku(instance, filename):
    # 現在の年と次の月を取得
    year = datetime.datetime.now().year
    next_month = (datetime.datetime.now().month % 12) + 1
    return f"{year}/{next_month}/sengoku/{filename}"

class Sengoku(models.Model):
    date = models.DateField()
    title = models.CharField(max_length=255)
    content = models.TextField()
    image = models.ImageField(upload_to=get_image_upload_sengoku, blank=True, null=True)
    
    def __str__(self):
        return self.title
    
def get_image_upload_helluva(instance, filename):
    # 現在の年と次の月を取得
    year = datetime.datetime.now().year
    next_month = (datetime.datetime.now().month % 12) + 1
    return f"{year}/{next_month}/helluva/{filename}"

class Helluva(models.Model):
    date = models.DateField()
    title = models.CharField(max_length=255)
    content = models.TextField()
    image = models.ImageField(upload_to=get_image_upload_helluva, blank=True, null=True)
    
    def __str__(self):
        return self.title
    
def get_image_upload_fuzz(instance, filename):
    # 現在の年と次の月を取得
    year = datetime.datetime.now().year
    next_month = (datetime.datetime.now().month % 12) + 1
    return f"{year}/{next_month}/fuzz/{filename}"

class Fuzz(models.Model):
    date = models.DateField()
    title = models.CharField(max_length=255)
    content = models.TextField()
    performers = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to=get_image_upload_fuzz, blank=True, null=True)
    
    def __str__(self):
        return self.title
    
def get_image_upload_mele(instance, filename):
    # 現在の年と次の月を取得
    year = datetime.datetime.now().year
    next_month = (datetime.datetime.now().month % 12) + 1
    return f"{year}/{next_month}/mele/{filename}"

class Mele(models.Model):
    date = models.DateField()
    title = models.CharField(max_length=255)
    content = models.TextField()
    performers = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to=get_image_upload_mele, blank=True, null=True)
    
    def __str__(self):
        return self.title
    
def get_image_upload_socore(instance, filename):
    # 現在の年と次の月を取得
    year = datetime.datetime.now().year
    next_month = (datetime.datetime.now().month % 12) + 1
    return f"{year}/{next_month}/socore/{filename}"

class Socore(models.Model):
    date = models.DateField()
    title = models.CharField(max_length=255)
    content = models.TextField()
    performers = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to=get_image_upload_socore, blank=True, null=True)
    
    def __str__(self):
        return self.title
    
def get_image_upload_tora(instance, filename):
    # 現在の年と次の月を取得
    year = datetime.datetime.now().year
    next_month = (datetime.datetime.now().month % 12) + 1
    return f"{year}/{next_month}/tora/{filename}"

class Tora(models.Model):
    date = models.DateField()
    title = models.CharField(max_length=255)
    content = models.TextField()
    image = models.ImageField(upload_to=get_image_upload_tora, blank=True, null=True)
    
    def __str__(self):
        return self.title
    
def get_image_upload_hokage(instance, filename):
    # 現在の年と次の月を取得
    year = datetime.datetime.now().year
    next_month = (datetime.datetime.now().month % 12) + 1
    return f"{year}/{next_month}/hokage/{filename}"

class Hokage(models.Model):
    date = models.DateField()
    title = models.CharField(max_length=255)
    content = models.TextField()
    performers = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to=get_image_upload_hokage, blank=True, null=True)
    
    def __str__(self):
        return self.title
