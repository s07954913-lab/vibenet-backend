from rest_framework import serializers
from .models import (
    User, Activity, ExplorePost, HomeFeedPost, Comment,
    ChatHistory, PostLike, PostView,
    AdminUser, Report, UserAnalytics,
    UserBalance, Transaction, CoinLog, TransactionAlert,
    ChatConversation, ChatMessage, Notification,
    UserProfile, UserPost,
    ReelLike, ReelSave, ReelFollow, ReelComment,
    ReelUpload, UserFollow,
)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model  = User
        fields = '__all__'


class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model  = Activity
        fields = '__all__'


class ExplorePostSerializer(serializers.ModelSerializer):
    class Meta:
        model  = ExplorePost
        fields = '__all__'


class HomeFeedPostSerializer(serializers.ModelSerializer):
    class Meta:
        model  = HomeFeedPost
        fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Comment
        fields = '__all__'


class ChatHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model  = ChatHistory
        fields = '__all__'


class PostLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model  = PostLike
        fields = '__all__'


class PostViewSerializer(serializers.ModelSerializer):
    class Meta:
        model  = PostView
        fields = '__all__'


class AdminUserSerializer(serializers.ModelSerializer):
    class Meta:
        model  = AdminUser
        fields = '__all__'


class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Report
        fields = '__all__'


class UserAnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model  = UserAnalytics
        fields = '__all__'


class UserBalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model  = UserBalance
        fields = '__all__'


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Transaction
        fields = '__all__'


class CoinLogSerializer(serializers.ModelSerializer):
    class Meta:
        model  = CoinLog
        fields = '__all__'


class TransactionAlertSerializer(serializers.ModelSerializer):
    class Meta:
        model  = TransactionAlert
        fields = '__all__'


class ChatConversationSerializer(serializers.ModelSerializer):
    class Meta:
        model  = ChatConversation
        fields = '__all__'


class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model  = ChatMessage
        fields = '__all__'


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Notification
        fields = '__all__'


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model  = UserProfile
        fields = '__all__'


class UserPostSerializer(serializers.ModelSerializer):
    class Meta:
        model  = UserPost
        fields = '__all__'


class ReelLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model  = ReelLike
        fields = '__all__'


class ReelSaveSerializer(serializers.ModelSerializer):
    class Meta:
        model  = ReelSave
        fields = '__all__'


class ReelFollowSerializer(serializers.ModelSerializer):
    class Meta:
        model  = ReelFollow
        fields = '__all__'


class ReelCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model  = ReelComment
        fields = '__all__'


class ReelUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model  = ReelUpload
        fields = '__all__'


# ─── NAYA: User Follow Serializer ─────────────────────────
class UserFollowSerializer(serializers.ModelSerializer):
    class Meta:
        model  = UserFollow
        fields = '__all__'