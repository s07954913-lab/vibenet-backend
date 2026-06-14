from django.db import models

class ProductSearchHistory(models.Model):
    query         = models.CharField(max_length=255)
    results_count = models.IntegerField(default=0)
    searched_at   = models.DateTimeField(auto_now_add=True)
    user_id       = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.query