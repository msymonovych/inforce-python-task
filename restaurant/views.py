from datetime import date

from django.db.models import Avg
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from restaurant.models import Restaurant, Menu, Vote
from restaurant.serializers import (
    RestaurantSerializer,
    MenuSerializer,
    RestaurantDetailSerializer,
    VoteSerializer,
    MenuListSerializer,
    VoteRetrieveSerializer,
)


class RestaurantViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet,
):
    serializer_class = RestaurantSerializer
    queryset = Restaurant.objects.all()

    def get_serializer_class(self):
        if self.action == "retrieve":
            return RestaurantDetailSerializer

        return self.serializer_class

    @action(detail=True, methods=["get"], url_path="today")
    def today(self, request, pk=None):
        today = date.today()
        menu = Menu.objects.filter(restaurant=pk, date=today).first()
        serializer = MenuSerializer(menu, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MenuViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet,
):
    serializer_class = MenuSerializer
    queryset = Menu.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return MenuListSerializer

        if self.action == "vote":
            return VoteSerializer

        return self.serializer_class

    @action(detail=False, methods=["get"], url_path="current-day-menu")
    def current_day_menus(self, request):
        today = date.today()
        menus = self.get_queryset().filter(date=today)
        serializer = MenuSerializer(menus, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="vote")
    def vote(self, request, pk=None):
        menu = self.get_object()
        employee = request.user

        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            vote, _ = Vote.objects.update_or_create(
                menu=menu,
                employee=employee,
                defaults=serializer.validated_data
            )
            serializer = VoteRetrieveSerializer(vote)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["get"], url_path="rating")
    def get_rating(self, request, pk=None):
        menu = self.get_object()
        rating = menu.votes.aggregate(rating=Avg("score"))

        return Response(rating, status=status.HTTP_200_OK)
