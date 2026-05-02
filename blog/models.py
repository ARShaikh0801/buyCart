from django.db import models
from django.contrib.auth.models import User

class Blogpost(models.Model):
    post_id=models.AutoField(primary_key=True)
    title=models.CharField(max_length=200)
    description = models.TextField() 
    pub_date=models.DateField(auto_now=True)
    author=models.CharField(max_length=50,default="")
    thumbnail=models.ImageField(upload_to='blog/images',default="")
    likes=models.IntegerField(default=0)
    product = models.ForeignKey('shop.Product', on_delete=models.SET_NULL, null=True, blank=True, related_name='blog_posts')


    def __str__(self):
        return self.title
    
class Like(models.Model):
    post = models.ForeignKey(Blogpost, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('post', 'user')

    def __str__(self):
        return f"{self.user.username} liked {self.post.title}"