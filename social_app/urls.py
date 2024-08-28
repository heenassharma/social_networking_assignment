from django.urls import path, include
from rest_framework.routers import DefaultRouter
from social_app.views.user_view import UserViewSet
from social_app.views.friend_request_view import FriendRequestViewSet

router = DefaultRouter()
router.register(r"users", UserViewSet)
router.register(
    r"friend-requests", FriendRequestViewSet, basename="friend-request"
)

urlpatterns = [
    path("", include(router.urls)),
    path(
        "token/",
        UserViewSet.as_view({"post": "login"}),
        name="token_obtain_pair",
    ),
    path("signup/", UserViewSet.as_view({"post": "signup"}), name="signup"),
    path(
        "friend-requests/<int:pk>/update-status/",
        FriendRequestViewSet.as_view({"patch": "update_status"}),
        name="friend-request-update-status",
    ),
]

urlpatterns += router.urls
