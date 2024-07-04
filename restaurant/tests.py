from datetime import date, timedelta

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from restaurant.models import Restaurant, Menu


User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def create_restaurant():
    return Restaurant.objects.create(name="Test Restaurant")


@pytest.fixture
def create_menu(create_restaurant):
    return Menu.objects.create(date=date.today(), restaurant=create_restaurant)


@pytest.fixture
def create_user():
    user = User.objects.create_user(
        username="testuser", email="test@example.com", password="password"
    )
    return user


# Restaurant tests

@pytest.mark.django_db
def test_create_restaurant(api_client):
    url = reverse("restaurant:restaurant-list")
    data = {"name": "New Restaurant"}
    response = api_client.post(url, data)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["name"] == "New Restaurant"


@pytest.mark.django_db
def test_create_restaurant_with_wrong_data(api_client):
    url = reverse("restaurant:restaurant-list")
    data = {"WrongData": 12345}
    response = api_client.post(url, data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_get_restaurant_list(api_client, create_restaurant):
    url = reverse("restaurant:restaurant-list")
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == Restaurant.objects.count()


@pytest.mark.django_db
def test_get_restaurant(api_client, create_restaurant):
    url = reverse("restaurant:restaurant-detail", kwargs={"pk": create_restaurant.pk})
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["name"] == create_restaurant.name


@pytest.mark.django_db
def test_get_restaurant_that_does_not_exist(api_client, create_restaurant):
    url = reverse("restaurant:restaurant-detail", kwargs={"pk": 404})
    response = api_client.get(url)

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_get_today_menu(api_client, create_restaurant, create_menu):
    url = reverse("restaurant:restaurant-today", kwargs={"pk": create_restaurant.pk})
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["date"] == str(create_menu.date)


# Menu tests

@pytest.mark.django_db
def test_list_menus(api_client, create_menu):
    url = reverse("restaurant:menu-list")
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == Menu.objects.count()
    assert response.data[0]["date"] == str(create_menu.date)


@pytest.mark.django_db
def test_create_menu(api_client, create_restaurant):
    url = reverse("restaurant:menu-list")
    data = {
        "date": str(date.today()),
        "restaurant": create_restaurant.pk,
        "menu_items": [
            {"name": "Dish 1", "description": "Description 1", "price": "10.50"},
            {"name": "Dish 2", "description": "Description 2", "price": "15.75"},
        ],
    }
    response = api_client.post(url, data, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["date"] == str(date.today())
    assert len(response.data["menu_items"]) == len(data["menu_items"])


@pytest.mark.django_db
def test_current_day_menus(api_client, create_menu):
    url = reverse("restaurant:menu-current-day-menus")
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == Menu.objects.filter(date=date.today()).count()
    assert response.data[0]["date"] == str(date.today())


@pytest.mark.django_db
def test_vote_action(api_client, create_menu, create_user):
    url = reverse("restaurant:menu-vote", kwargs={"pk": create_menu.pk})
    data = {"score": 5}
    api_client.force_authenticate(user=create_user)
    response = api_client.post(url, data)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["score"] == data["score"]


@pytest.mark.django_db
def test_get_rating_action(api_client, create_menu, create_user):
    api_client.force_authenticate(user=create_user)
    vote_url = reverse("restaurant:menu-vote", kwargs={"pk": create_menu.pk})
    api_client.post(vote_url, {"score": 5})

    rating_url = reverse("restaurant:menu-get-rating", kwargs={"pk": create_menu.pk})
    response = api_client.get(rating_url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["rating"] == 5.0
