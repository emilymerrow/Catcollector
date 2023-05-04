from django.db import models
from django.contrib.auth.models import User # importing the user model
from django.urls import reverse  # kind of like redirect
# Create your models here.


class Toy(models.Model):
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=20)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('toys_detail', kwargs={'pk': self.id})


# One Cat has many feedings
# cat.<related_model_name<_set.all(), .create(), .get, .filter
# cat.feeding_set


class Cat(models.Model):
    name = models.CharField(max_length=100)
    breed = models.CharField(max_length=100)
    description = models.TextField(max_length=250)
    age = models.IntegerField()
    # A User has many cats, cat belongs to a User
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # the related model must be defined first because there is no hoisting
	# toy has to be defined before you can reference
    toys = models.ManyToManyField(Toy)
    # This function happens when our create form or update form is submitted,
    # and CatsCreate CBV after it has handled the post request
    # or CatsUpdate CBV handles the PUT request

    def get_absolute_url(self):
        # path('cats/<int:cat_id>/', views.cats_detail, name='detail'),
        # self.id is referring to the cat that was just created
        # when the submit the form
        return reverse('detail', kwargs={'cat_id': self.id})

    def __str__(self):
        return f"{self.name} is {self.age} years old"


class Photo(models.Model):
	# url of the image on aws
    url = models.CharField(max_length=200)
    cat = models.ForeignKey(Cat, on_delete=models.CASCADE)

    def __str__(self):
        return f"Photo for cat_id: {self.cat_id} @{self.url}"


# All Caps in python, This is a convention that says
# this variable should never be overwritten
MEALS = (
        ('B', 'Breakfast'),
        ('L', 'Lunch'),
        ('D', 'Dinner'),
)
# select menus ^
# One Cat has Many Feedling, Feeding belongs to a Cat


class Feeding(models.Model):
    date = models.DateField('feeding date')
    # meal will be represented by a single letter (B)reakfast, (L)unch, (D)inner
    # # we set the default value for meal to 'B
    meal = models.CharField(max_length=1, choices=MEALS, default=MEALS[0][0])
    # Create a cat_id FK
    # models.CASCADE, if we delete a cat, delete its feedings as well
    cat = models.ForeignKey(Cat, on_delete=models.CASCADE)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        # get_meal_display is automatically generated,
        # on inputs that have choices parameter, see meal
        return f"{self.get_meal_display()} on {self.date}"
