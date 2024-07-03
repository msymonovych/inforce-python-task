from django.urls import include, path
from rest_framework import routers

from restaurant.views import (
    RestaurantViewSet,
    MenuViewSet
)

router = routers.DefaultRouter()
router.register("restaurants", RestaurantViewSet)
router.register("menus", MenuViewSet)

urlpatterns = [
    path("", include(router.urls))
]

app_name = "restaurant"
