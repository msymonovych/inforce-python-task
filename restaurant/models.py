from django.db import models
from django.conf import settings


class Restaurant(models.Model):
    name = models.CharField(max_length=115)

    def __str__(self):
        return self.name


class Menu(models.Model):
    date = models.DateField()
    restaurant = models.ForeignKey(
        Restaurant, on_delete=models.CASCADE, related_name="menus"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["date", "restaurant"], name="unique_menus"
            )
        ]

    def __str__(self):
        return f"{self.date} - {self.restaurant}"


class MenuItem(models.Model):
    name = models.CharField(max_length=115)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    menu = models.ForeignKey(
        Menu, on_delete=models.CASCADE, related_name="menu_items"
    )

    def __str__(self):
        return self.name


class Vote(models.Model):
    score = models.IntegerField(default=0)
    menu = models.ForeignKey(
        Menu, on_delete=models.CASCADE, related_name="score"
    )
    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="votes"
    )

    def __str__(self):
        return self.menu.__str__() + " Employee: " + self.employee.username
