from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import Avg

from users.models import User


class Category(models.Model):
    """
    Модель категорий произведений.
    """
    name = models.CharField(
        verbose_name='Название',
        max_length=100
    )
    slug = models.SlugField(
        verbose_name='Указатель категории',
        max_length=50,
        unique=True
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['name']


class Genre(models.Model):
    """
    Модель для жанров произведений.
    """
    name = models.CharField(
        verbose_name='Название',
        max_length=100
    )
    slug = models.SlugField(
        verbose_name='Указатель жанра',
        max_length=50,
        unique=True
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'
        ordering = ['name']


class Title(models.Model):
    """
    Модель произведений, к которым пишут
    отзывы.
    """
    name = models.CharField(
        verbose_name='Название',
        max_length=100
    )
    genre = models.ManyToManyField(
        Genre,
        verbose_name='Жанр',
        through='GenreTitle'
    )
    category = models.ForeignKey(
        Category,
        verbose_name='Категория',
        on_delete=models.SET_NULL,
        related_name='titles',
        null=True
    )
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        verbose_name='Рейтинг',
        null=True,
        default=None
    )

    def __str__(self):
        return self.name
    
    def average_rating(self):
        return self.reviews.aggregate(Avg('rating'))['rating__avg']

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'
        ordering = ['name']


class GenreTitle(models.Model):
    """
    Дополнительная модель для связи
    моделей жанра произведений и
    категории произведений.
    """
    title = models.ForeignKey(
        Title,
        verbose_name='Произведение',
        on_delete=models.CASCADE)
    genre = models.ForeignKey(
        Genre,
        verbose_name='Жанр',
        on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.title}, жанр - {self.genre}'

    class Meta:
        verbose_name = 'Произведение и жанр'
        verbose_name_plural = 'Произведения и жанры'


class Review(models.Model):
    """
    Модель отзывов к произведениям.
    """
    title = models.ForeignKey(
        Title,
        verbose_name='Произведение',
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviewer'
    )
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    text = models.TextField(
        verbose_name='Текст отзыва'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.title.name}: {self.rating}'

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'title'],
                name='unique_review',
            ),
        ]


class Comment(models.Model):
    """
    Модель комментариев к отзывам.
    """
    review = models.ForeignKey(
        Review,
        verbose_name='Отзыв',
        on_delete=models.CASCADE
    )
    text = models.TextField(
        verbose_name='Текст комментария'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['created_at']
