from django.db import models
# Create your models here.


class TopTickers(models.Model):
    ticker = models.CharField(max_length=100)
    threadmentions = models.IntegerField()
    commentmentions = models.IntegerField()
    # sum of thread mention score and comment mention score
    mentionsscore = models.IntegerField()
    
class TickerThreads(models.Model):
    ticker = models.CharField(max_length=100)
    url = models.URLField()
    title = models.TextField()
    # dictated by upvote count
    threadscore = models.IntegerField()
    
class TickerComments(models.Model):
    ticker = models.CharField(max_length=100)
    url = models.URLField()
    body = models.TextField()
    # dictated by upvote count
    score = models.IntegerField()
    
    def body_snippet(self):
        return self.body[:100] + '...'