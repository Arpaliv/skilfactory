from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User


class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0)

    def update_rating(self):
        self.rating = 0
        post_rating = 0
        comment_rating = 0
        for post in Post.objects.filter(author=self):
            post_rating += post.rating * 3
        for comment in Comment.objects.filter(Q(post__author=self) | Q(user=self.user)):
            comment_rating += comment.rating
        self.rating = post_rating + comment_rating
        self.save()


class PostCategory(models.Model):
    post = models.ForeignKey('Post', on_delete=models.CASCADE)
    category = models.ForeignKey('Category', on_delete=models.CASCADE)


class Category(models.Model):
    name = models.CharField(unique=True, max_length=255)


class Post(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    type = models.CharField(choices=[('news', 'новость'), ('article', 'статья')], max_length=255)
    time_of_addition = models.DateTimeField(auto_now_add=True)
    category = models.ManyToManyField(Category, through=PostCategory, null=True)
    heading = models.CharField(max_length=255)
    text = models.TextField()
    rating = models.IntegerField(default=0)

    def like(self, value=1):
        self.rating += value

    def dislike(self, value=1):
        self.rating -= value

    def previw(self):
        answer = self.text[0:124] + '...'
        return answer


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)  #Разрешим оставлять комментарии анонимам
    text = models.TextField(null = True)
    time_of_addating = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField(default=0)

    def like(self, value=1):
        self.rating += value

    def dislike(self, value=1):
        self.rating -= value

