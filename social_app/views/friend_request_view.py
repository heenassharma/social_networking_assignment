from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from social_app.models.friend_request import FriendRequest
from social_app.serializers.friend_request_serializer import FriendRequestSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from django.contrib.auth import get_user_model
from social_app.serializers.user_serializer import UserSerializer
from django.core.cache import cache
from datetime import datetime, timedelta
from rest_framework.exceptions import ValidationError


User = get_user_model()

class FriendRequestViewSet(viewsets.ModelViewSet):
    queryset = FriendRequest.objects.all()
    serializer_class = FriendRequestSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'],
            permission_classes=[IsAuthenticated])
    def sendrequest(self, request):
        # Get the current user
        current_user = request.user

        # Check if the user has already sent 3 friend requests within the last minute
        cache_key = f"friend_request_count_{current_user.id}"
        request_count = cache.get(cache_key, default=0)
        if request_count >= 3:
            return Response({
                                "error": "You have reached the limit of 3 friend requests within a minute."},
                            status=status.HTTP_429_TOO_MANY_REQUESTS)

        # Increase the request count for the user
        cache.set(cache_key, request_count + 1, timeout=60)

        # Continue with the friend request creation
        to_user_id = request.data.get('to_user')
        to_user = User.objects.get(pk=to_user_id)
        existing_request = FriendRequest.objects.filter(from_user=current_user,
                                                        to_user=to_user).exists()
        if existing_request:
            raise ValidationError(
                "You have already sent a friend request to this user.")

        if to_user != current_user:
            friend_request = FriendRequest.objects.create(
                from_user=current_user, to_user=to_user)
            serializer = self.get_serializer(friend_request)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {"error": "Cannot send friend request to yourself"},
                status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        serializer.save(from_user=self.request.user)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def pending_requests(self, request):
        user = request.user
        pending_requests = FriendRequest.objects.filter(to_user=user, status='pending')
        serializer = self.get_serializer(pending_requests, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def friends(self, request):
        user = request.user
        friends = User.objects.filter(Q(sent_requests__to_user=user, sent_requests__status='accepted') |
                                      Q(received_requests__from_user=user, received_requests__status='accepted'))
        serializer = UserSerializer(friends, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['patch'], permission_classes=[IsAuthenticated])
    def update_status(self, request, pk=None):
        print(pk)
        friend_request = FriendRequest.objects.get(pk=pk)

        # Check if the request was sent by the same user
        if friend_request.from_user == request.user:
            return Response({
                                "error": "You cannot update the status of a friend request sent by yourself."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Check if the status is being updated to "rejected" or "accepted"
        # if 'status' in request.data and request.data['status'] in ['rejected',
        #                                                            'accepted']:
        #     return Response({
        #                         "error": "You cannot update the status of the friend request to 'rejected' or 'accepted'."},
        #                     status=status.HTTP_400_BAD_REQUEST)

        # Proceed with the update
        serializer = self.get_serializer(friend_request, data=request.data,
                                         partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)