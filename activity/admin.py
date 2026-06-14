from django.contrib import admin
from .models import (
    Activity, ExplorePost, HomeFeedPost, Comment,
    ChatHistory, PostLike, PostView,
    AdminUser, Report, UserAnalytics,
    UserBalance, Transaction, CoinLog, TransactionAlert,
    ChatConversation, ChatMessage, Notification,
    UserProfile, UserPost,
    ReelLike, ReelSave, ReelFollow, ReelComment
)

for model in [
    Activity, ExplorePost, HomeFeedPost, Comment,
    ChatHistory, PostLike, PostView,
    AdminUser, Report, UserAnalytics,
    UserBalance, Transaction, CoinLog, TransactionAlert,
    ChatConversation, ChatMessage, Notification,
    UserProfile, UserPost,
    ReelLike, ReelSave, ReelFollow, ReelComment
]:
    try:
        admin.site.unregister(model)
    except admin.sites.NotRegistered:
        pass
    admin.site.register(model)