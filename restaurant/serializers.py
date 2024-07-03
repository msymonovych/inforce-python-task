from rest_framework import serializers

from restaurant.models import Restaurant, Menu, MenuItem, Vote


class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ("name", "description", "price")


class MenuSerializer(serializers.ModelSerializer):
    menu_items = MenuItemSerializer(many=True, read_only=False)

    class Meta:
        model = Menu
        fields = ("date", "restaurant", "menu_items",)

    def create(self, validated_data):
        menu_items = validated_data.pop("menu_items")
        menu = Menu.objects.create(**validated_data)

        for item in menu_items:
            MenuItem.objects.create(menu=menu, **item)

        return menu


class MenuListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Menu
        fields = ("id", "date", "restaurant")


class VoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = ("score", )


class VoteRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = "__all__"


class RestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = "__all__"


class RestaurantDetailSerializer(serializers.ModelSerializer):
    menus = MenuSerializer(many=True, read_only=True)

    class Meta:
        model = Restaurant
        fields = ("id", "name", "menus")
