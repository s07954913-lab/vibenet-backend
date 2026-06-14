from django.urls import path
from . import views

urlpatterns = [

    # ================= AUTH =================
    path('signup/',      views.signup,      name='signup'),
    path('login/',       views.login,       name='login'),
    path('google-auth/', views.google_auth, name='google-auth'),

    # ================= USER SEARCH (NAYA) =================
    # GET /api/users/search/?q=ali
    path('users/search/', views.search_users, name='search-users'),

    # ================= PUBLIC PROFILE (NAYA) =================
    # GET /api/users/<user_id>/public/  → profile + all posts
    path('users/<int:user_id>/public/', views.public_profile, name='public-profile'),

    # ================= FOLLOW SYSTEM (NAYA) =================
    # POST /api/users/follow/  body: {follower_id, following_id}
    path('users/follow/',                                  views.toggle_follow,       name='toggle-follow'),
    # GET  /api/users/<follower_id>/follows/<following_id>/
    path('users/<int:follower_id>/follows/<int:following_id>/', views.check_follow_status, name='check-follow-status'),
    # GET  /api/users/<user_id>/followers/
    path('users/<int:user_id>/followers/',                 views.get_followers,       name='get-followers'),
    # GET  /api/users/<user_id>/following/
    path('users/<int:user_id>/following/',                 views.get_following,       name='get-following'),

    # ================= ACTIVITY =================
    path('activity/<str:user_id>/',                views.user_activity,   name='user-activity'),
    path('activity/<str:user_id>/<str:act_type>/', views.clear_activity,  name='clear-activity'),
    path('admin-activity/',                        views.admin_activity,  name='admin-activity'),

    # ================= EXPLORE =================
    path('explore/',                      views.explore_list,     name='explore-list'),
    path('explore/trending/',             views.explore_trending, name='explore-trending'),
    path('explore/create/',              views.explore_create,   name='explore-create'),
    path('explore/<int:post_id>/like/',  views.explore_like,     name='explore-like'),
    path('explore/<int:post_id>/delete/', views.explore_delete,  name='explore-delete'),

    # ================= EXPLORE SAVE (NAYA) =================
    path('save-search/', views.save_search, name='save-search'),
    path('save-click/',  views.save_click,  name='save-click'),

    # ================= HOME FEED =================
    # feed_like ab liker_user_id leta hai → auto notification bhejta hai
    # feed_comments ab commenter user_id leta hai → auto notification bhejta hai
    path('feed/',                             views.feed_list,     name='feed-list'),
    path('feed/create/',                      views.feed_create,   name='feed-create'),
    path('feed/<int:post_id>/like/',          views.feed_like,     name='feed-like'),
    path('feed/<int:post_id>/share/',         views.feed_share,    name='feed-share'),
    path('feed/<int:post_id>/save/',          views.feed_save,     name='feed-save'),
    path('feed/<int:post_id>/delete/',        views.feed_delete,   name='feed-delete'),
    path('feed/<int:post_id>/comments/',      views.feed_comments, name='feed-comments'),

    # ================= AI CHAT HISTORY =================
    path('chat/<int:user_id>/',              views.chat_history,        name='chat-history'),
    path('chat/<int:user_id>/clear/',        views.clear_chat_history,  name='clear-chat-history'),
    path('chat/message/<int:msg_id>/',       views.update_chat_message, name='update-chat-message'),

    # ================= DETAIL =================
    path('detail/like/',                             views.toggle_like,  name='toggle-like'),
    path('detail/like/<int:user_id>/<int:post_id>/', views.check_like,   name='check-like'),
    path('detail/likes/<int:post_id>/',              views.likes_count,  name='likes-count'),
    path('detail/view/',                             views.save_view,    name='save-view'),
    path('detail/views/<int:post_id>/',              views.views_count,  name='views-count'),

    # ================= ADMIN =================
    path('admin-users/',                     views.admin_users_list,    name='admin-users-list'),
    path('admin-users/create/',              views.admin_user_create,   name='admin-user-create'),
    path('admin-users/<int:user_id>/',       views.admin_user_update,   name='admin-user-update'),
    path('admin-reports/',                   views.admin_reports_list,  name='admin-reports-list'),
    path('admin-reports/create/',            views.admin_report_create, name='admin-report-create'),
    path('admin-reports/<int:report_id>/',   views.admin_report_action, name='admin-report-action'),

    # ================= ANALYTICS =================
    path('analytics/<int:user_id>/',       views.get_analytics,  name='get-analytics'),
    path('analytics/<int:user_id>/save/',  views.save_analytics, name='save-analytics'),

    # ================= BALANCE =================
    path('balance/<int:user_id>/',       views.get_balance,  name='get-balance'),
    path('balance/<int:user_id>/save/',  views.save_balance, name='save-balance'),

    # ================= TRANSACTIONS =================
    path('transactions/<int:user_id>/',        views.get_transactions,   name='get-transactions'),
    path('transactions/<int:user_id>/create/', views.create_transaction, name='create-transaction'),

    # ================= COINS =================
    path('coins/<int:user_id>/',     views.get_coin_log, name='get-coin-log'),
    path('coins/<int:user_id>/add/', views.add_coin_log, name='add-coin-log'),

    # ================= ALERTS =================
    path('alerts/<int:user_id>/',          views.get_alerts,           name='get-alerts'),
    path('alerts/<int:user_id>/create/',   views.create_alert,         name='create-alert'),
    path('alerts/read/<int:alert_id>/',    views.mark_alert_read,      name='mark-alert-read'),
    path('alerts/<int:user_id>/read-all/', views.mark_all_alerts_read, name='mark-all-alerts-read'),

    # ================= CHAT SYSTEM =================
    path('conversations/<int:user_id>/',          views.get_conversations,     name='get-conversations'),
    path('conversations/<int:user_id>/create/',   views.create_conversation,   name='create-conversation'),
    path('conversations/<int:conv_id>/messages/', views.conversation_messages, name='conversation-messages'),
    path('conversations/<int:conv_id>/read/',     views.mark_messages_read,    name='mark-messages-read'),
    path('conversations/<int:conv_id>/delete/',   views.delete_conversation,   name='delete-conversation'),

    # ================= NOTIFICATIONS =================
    path('notifications/<int:user_id>/',          views.get_notifications,          name='get-notifications'),
    path('notifications/<int:user_id>/create/',   views.create_notification_api,    name='create-notification'),
    path('notifications/delete/<int:note_id>/',   views.delete_notification,        name='delete-notification'),
    path('notifications/read/<int:note_id>/',     views.mark_notification_read,     name='mark-notification-read'),
    path('notifications/<int:user_id>/read-all/', views.mark_all_notifications_read, name='mark-all-notifications-read'),

    # ================= PROFILE =================
    path('profile/<int:user_id>/',              views.get_profile,      name='get-profile'),
    path('profile/<int:user_id>/save/',         views.save_profile,     name='save-profile'),
    path('profile/<int:user_id>/posts/',        views.get_user_posts,   name='get-user-posts'),
    path('profile/<int:user_id>/posts/create/', views.create_user_post, name='create-user-post'),
    path('profile/posts/<int:post_id>/delete/', views.delete_user_post, name='delete-user-post'),

    # ================= REELS =================
    path('reels/like/',                    views.reel_toggle_like,    name='reel-toggle-like'),
    path('reels/liked/<int:user_id>/',     views.reel_liked_list,     name='reel-liked-list'),
    path('reels/save/',                    views.reel_toggle_save,    name='reel-toggle-save'),
    path('reels/saved/<int:user_id>/',     views.reel_saved_list,     name='reel-saved-list'),
    path('reels/follow/',                  views.reel_toggle_follow,  name='reel-toggle-follow'),
    path('reels/following/<int:user_id>/', views.reel_following_list, name='reel-following-list'),
    path('reels/<str:video_id>/comments/', views.reel_comments,       name='reel-comments'),

    # ================= UPLOAD =================
    path('upload/',                        views.upload_media, name='upload-media'),
    path('upload/<int:user_id>/',          views.get_uploads,  name='get-uploads'),
    path('upload/delete/<int:upload_id>/', views.delete_upload, name='delete-upload'),
    # Conversation get or create (2 users ke beech)
path('conversations/get-or-create/', views.get_or_create_conversation, name='conv-get-or-create'),

# New messages polling
path('conversations/<int:conv_id>/messages/new/', views.new_messages, name='new-messages'),
# ══════════════════════════════════════════════════════════
#  YEH 2 URLS apni urls.py mein add karein
#  CHAT SYSTEM section ke andar
# ══════════════════════════════════════════════════════════

# Existing CHAT SYSTEM URLs ke neeche yeh add karein:

path('conversations/get-or-create/',
     views.get_or_create_conversation,
     name='conv-get-or-create'),

path('conversations/<int:conv_id>/messages/new/',
     views.new_messages,
     name='new-messages'),

# ══════════════════════════════════════════════════════════
#  IMPORTANT: get-or-create URL, create URL se PEHLE likhein
#  Warna Django 'get-or-create' ko user_id samjhega
# ══════════════════════════════════════════════════════════
#
#  Sahi order:
#  path('conversations/get-or-create/', ...),        ← pehle
#  path('conversations/<int:user_id>/create/', ...),  ← baad mein
]