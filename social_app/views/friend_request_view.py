from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from social_app.models.friend_request import FriendRequest
from social_app.serializers.friend_request_serializer import (
    FriendRequestSerializer,
)
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, ObjectDoesNotExist
from django.contrib.auth import get_user_model
from social_app.serializers.user_serializer import UserSerializer
from django.core.cache import cache
from rest_framework.exceptions import ValidationError
from ..constants import (
    REQUEST_LIMIT_REACHED,
    REQUEST_ALREADY_SENT,
    PENDING,
    ACCEPTED,
    STATUS_CAN_NOT_BE_UPDATED_BY_YOURSELF,
    DOES_NOT_EXIST,
    CAN_NOT_SEND_REQUEST,
)


User = get_user_model()


class FriendRequestViewSet(viewsets.ModelViewSet):
    queryset = FriendRequest.objects.all()
    serializer_class = FriendRequestSerializer
    permission_classes = [IsAuthenticated]

    @action(
        detail=False, methods=["post"], permission_classes=[IsAuthenticated]
    )
    def sendrequest(self, request):
        # Get the current user
        current_user = request.user

        # Check if the user has already sent 3 friend requests within the last minute
        cache_key = f"friend_request_count_{current_user.id}"
        request_count = cache.get(cache_key, default=0)
        if request_count >= 3:
            return Response(
                {"error": REQUEST_LIMIT_REACHED},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        # Continue with the friend request creation
        to_user_id = request.data.get("to_user")
        to_user = User.objects.get(pk=to_user_id)
        existing_request = FriendRequest.objects.filter(
            from_user=current_user, to_user=to_user
        ).exists()
        if existing_request:
            raise ValidationError(REQUEST_ALREADY_SENT)

        if to_user != current_user:
            friend_request = FriendRequest.objects.create(
                from_user=current_user, to_user=to_user, status=PENDING
            )
            serializer = self.get_serializer(friend_request)
            # Increase the request count for the user
            cache.set(cache_key, request_count + 1, timeout=60)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {"error": CAN_NOT_SEND_REQUEST},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def perform_create(self, serializer):
        serializer.save(from_user=self.request.user)

    @action(
        detail=False, methods=["get"], permission_classes=[IsAuthenticated]
    )
    def pending_requests(self, request):
        user = request.user
        pending_requests = FriendRequest.objects.filter(
            to_user=user, status=PENDING
        )
        serializer = self.get_serializer(pending_requests, many=True)
        return Response(serializer.data)

    @action(
        detail=False, methods=["get"], permission_classes=[IsAuthenticated]
    )
    def friends(self, request):
        user = request.user
        friends = User.objects.filter(
            Q(sent_requests__to_user=user, sent_requests__status=ACCEPTED)
            | Q(
                received_requests__from_user=user,
                received_requests__status=ACCEPTED,
            )
        )
        serializer = UserSerializer(friends, many=True)
        return Response(serializer.data)

    @action(
        detail=False, methods=["patch"], permission_classes=[IsAuthenticated]
    )
    def update_status(self, request, pk=None):
        try:
            friend_request = FriendRequest.objects.get(pk=pk)
        except ObjectDoesNotExist:
            return Response(
                {"error": DOES_NOT_EXIST},
                status=status.HTTP_400_BAD_REQUEST,
            )
        # Check if the request was sent by the same user
        if friend_request.from_user == request.user:
            return Response(
                {"error": STATUS_CAN_NOT_BE_UPDATED_BY_YOURSELF},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = self.get_serializer(
            friend_request, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)
