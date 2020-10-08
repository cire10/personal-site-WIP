from django.db import models
from django.utils.text import slugify

# Create your models here.
# convention is capitalized word
class Blog(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, max_length=200, null=False)
    body = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title
    
    def body_snippet(self):
        return self.body[:100] + '...'
    
    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = slugify(self.title, allow_unicode=True)
        super(Blog, self).save(*args, **kwargs)

# every time a model is added or updated
# need to use python manage.py makemigrations
# then python manage.py migrate