from django.urls import path
from . import views

app_name = "sake_app"

urlpatterns = [
    # 都道府県
    path("prefecture/", views.prefecture_list, name="prefecture_list"),
    path("prefecture/<int:pk>/", views.prefecture_detail, name="prefecture_detail"),
    # 日本酒
    path("sake/", views.sake_list, name="sake_list"),
    path("sake/<int:pk>/", views.sake_detail, name="sake_detail"),
    # 日本酒ログ
    path("mylog/", views.sakelog_list, name="sakelog_list"),
    path("mylog/<int:pk>/", views.sakelog_detail, name="sakelog_detail"),
    # お気に入り
    path("favorites/", views.favorite_list, name="favorite_list"),
]
