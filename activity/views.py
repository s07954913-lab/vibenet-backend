from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
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
from .serializers import (
    UserSerializer, ActivitySerializer, ExplorePostSerializer,
    HomeFeedPostSerializer, CommentSerializer,
    ChatHistorySerializer, PostLikeSerializer, PostViewSerializer,
    AdminUserSerializer, ReportSerializer, UserAnalyticsSerializer,
    UserBalanceSerializer, TransactionSerializer,
    CoinLogSerializer, TransactionAlertSerializer,
    ChatConversationSerializer, ChatMessageSerializer,
    NotificationSerializer, UserProfileSerializer, UserPostSerializer,
    ReelLikeSerializer, ReelSaveSerializer,
    ReelFollowSerializer, ReelCommentSerializer,
    ReelUploadSerializer, UserFollowSerializer,
)
import os


# ══════════════════════════════════════════════════════════
#  HELPER — auto notification banana
# ══════════════════════════════════════════════════════════
def create_notification(to_user_id, from_user_id, notif_type):
    """
    Jab koi follow/like/comment kare to us user ko
    automatically notification bhejo.
    notif_type: 'Follow' | 'Likes' | 'Comments'
    """
    try:
        from_profile = UserProfile.objects.get(user_id=from_user_id)
        from_name    = from_profile.name
        from_img     = from_profile.profile_image
    except UserProfile.DoesNotExist:
        try:
            from_user = User.objects.get(id=from_user_id)
            from_name = from_user.username
        except User.DoesNotExist:
            from_name = 'Someone'
        from_img = ''

    Notification.objects.create(
        user_id   = to_user_id,
        from_name = from_name,
        from_img  = from_img,
        type      = notif_type,
        is_read   = False,
    )


# ══════════════════════════════════════════════════════════
#  AUTH
# ══════════════════════════════════════════════════════════
@api_view(['POST'])
def signup(request):
    username = request.data.get('username')
    email    = request.data.get('email')
    password = request.data.get('password')

    if User.objects.filter(email=email).exists():
        return Response({'success': False, 'message': 'Email already registered'})

    user = User.objects.create(username=username, email=email, password=password)
    return Response({'success': True, 'message': 'Signup successful', 'user_id': user.id})


@api_view(['POST'])
def login(request):
    email    = request.data.get('email')
    password = request.data.get('password')
    try:
        user = User.objects.get(email=email, password=password)
        return Response({
            'success':  True,
            'message':  'Login successful',
            'user_id':  user.id,
            'username': user.username,
        })
    except User.DoesNotExist:
        return Response({'success': False, 'message': 'Invalid email or password'})


@api_view(['POST'])
def google_auth(request):
    email     = request.data.get('email')
    username  = request.data.get('username', '')
    photo_url = request.data.get('photo_url', '')

    if not email:
        return Response({'success': False, 'message': 'Email missing'})

    try:
        user = User.objects.filter(email=email).first()
        if not user:
            base_username  = username or email.split('@')[0]
            final_username = base_username
            counter        = 1
            while User.objects.filter(username=final_username).exists():
                final_username = f"{base_username}{counter}"
                counter += 1
            user = User.objects.create(
                username=final_username, email=email, password='google_oauth'
            )
        return Response({
            'success':   True,
            'message':   'Google login successful',
            'user_id':   user.id,
            'username':  user.username,
            'email':     user.email,
            'photo_url': photo_url,
        })
    except Exception as e:
        return Response({'success': False, 'message': str(e)})


# ══════════════════════════════════════════════════════════
#  USER SEARCH (NAYA)
# ══════════════════════════════════════════════════════════
@api_view(['GET'])
def search_users(request):
    """
    GET /api/users/search/?q=ali
    Username ya name se users dhundo.
    Returns: [{user_id, username, name, profile_image, followers}]
    """
    query = request.query_params.get('q', '').strip()
    if not query:
        return Response([])

    users = User.objects.filter(username__icontains=query)[:20]
    result = []
    for u in users:
        try:
            profile = UserProfile.objects.get(user_id=u.id)
            img       = profile.profile_image
            name      = profile.name
            followers = profile.followers
        except UserProfile.DoesNotExist:
            img       = ''
            name      = u.username
            followers = 0

        result.append({
            'user_id':       u.id,
            'username':      u.username,
            'name':          name,
            'profile_image': img,
            'followers':     followers,
        })

    return Response(result)


# ══════════════════════════════════════════════════════════
#  PUBLIC PROFILE + POSTS (NAYA)
# ══════════════════════════════════════════════════════════
@api_view(['GET'])
def public_profile(request, user_id):
    """
    GET /api/users/<user_id>/public/
    Kisi bhi user ka public profile aur uski sari posts.
    """
    try:
        profile = UserProfile.objects.get(user_id=user_id)
        data    = UserProfileSerializer(profile).data
    except UserProfile.DoesNotExist:
        data = {
            'user_id': user_id, 'name': 'User', 'bio': '',
            'profile_image': '', 'followers': 0, 'following': 0, 'likes': 0,
        }

    # Username bhi add karo
    try:
        u = User.objects.get(id=user_id)
        data['username'] = u.username
    except User.DoesNotExist:
        data['username'] = ''

    # Us user ki sari posts
    posts        = UserPost.objects.filter(user_id=user_id)
    data['posts'] = UserPostSerializer(posts, many=True).data

    return Response(data)


# ══════════════════════════════════════════════════════════
#  FOLLOW / UNFOLLOW (NAYA)
# ══════════════════════════════════════════════════════════
@api_view(['POST'])
def toggle_follow(request):
    """
    POST /api/users/follow/
    Body: { follower_id, following_id }

    - Agar already follow hai → unfollow karo
    - Agar follow nahi → follow karo + notification bhejo
      + follower/following counts update karo
    """
    follower_id  = request.data.get('follower_id')
    following_id = request.data.get('following_id')

    if not follower_id or not following_id:
        return Response({'success': False, 'message': 'follower_id aur following_id required hain'}, status=400)

    if str(follower_id) == str(following_id):
        return Response({'success': False, 'message': 'Aap apne aap ko follow nahi kar sakte'}, status=400)

    existing = UserFollow.objects.filter(
        follower_id=follower_id, following_id=following_id
    ).first()

    if existing:
        # ─── UNFOLLOW ─────────────────────────────────────
        existing.delete()

        # Counts kam karo
        try:
            follower_profile           = UserProfile.objects.get(user_id=follower_id)
            follower_profile.following = max(0, follower_profile.following - 1)
            follower_profile.save()
        except UserProfile.DoesNotExist:
            pass

        try:
            following_profile           = UserProfile.objects.get(user_id=following_id)
            following_profile.followers = max(0, following_profile.followers - 1)
            following_profile.save()
        except UserProfile.DoesNotExist:
            pass

        return Response({'success': True, 'following': False, 'message': 'Unfollow ho gaya'})

    else:
        # ─── FOLLOW ───────────────────────────────────────
        UserFollow.objects.create(follower_id=follower_id, following_id=following_id)

        # Counts barhaao
        try:
            follower_profile           = UserProfile.objects.get(user_id=follower_id)
            follower_profile.following += 1
            follower_profile.save()
        except UserProfile.DoesNotExist:
            pass

        try:
            following_profile           = UserProfile.objects.get(user_id=following_id)
            following_profile.followers += 1
            following_profile.save()
        except UserProfile.DoesNotExist:
            pass

        # Auto notification — jise follow kiya usse batao
        create_notification(
            to_user_id   = following_id,
            from_user_id = follower_id,
            notif_type   = 'Follow',
        )

        return Response({'success': True, 'following': True, 'message': 'Follow ho gaya'})


@api_view(['GET'])
def check_follow_status(request, follower_id, following_id):
    """
    GET /api/users/<follower_id>/follows/<following_id>/
    Check karo kya follower_id ne following_id ko follow kiya hua hai.
    """
    is_following = UserFollow.objects.filter(
        follower_id=follower_id, following_id=following_id
    ).exists()
    return Response({'following': is_following})


@api_view(['GET'])
def get_followers(request, user_id):
    """
    GET /api/users/<user_id>/followers/
    Is user ke saare followers ki list.
    """
    follows = UserFollow.objects.filter(following_id=user_id)
    result  = []
    for f in follows:
        try:
            profile = UserProfile.objects.get(user_id=f.follower_id)
            img     = profile.profile_image
            name    = profile.name
        except UserProfile.DoesNotExist:
            try:
                u    = User.objects.get(id=f.follower_id)
                name = u.username
            except User.DoesNotExist:
                name = 'User'
            img = ''
        result.append({
            'user_id': f.follower_id,
            'name':    name,
            'img':     img,
        })
    return Response(result)


@api_view(['GET'])
def get_following(request, user_id):
    """
    GET /api/users/<user_id>/following/
    Is user ne jinhe follow kiya hua hai unki list.
    """
    follows = UserFollow.objects.filter(follower_id=user_id)
    result  = []
    for f in follows:
        try:
            profile = UserProfile.objects.get(user_id=f.following_id)
            img     = profile.profile_image
            name    = profile.name
        except UserProfile.DoesNotExist:
            try:
                u    = User.objects.get(id=f.following_id)
                name = u.username
            except User.DoesNotExist:
                name = 'User'
            img = ''
        result.append({
            'user_id': f.following_id,
            'name':    name,
            'img':     img,
        })
    return Response(result)


# ══════════════════════════════════════════════════════════
#  ACTIVITY
# ══════════════════════════════════════════════════════════
@api_view(['GET', 'POST'])
def user_activity(request, user_id):
    if request.method == 'POST':
        serializer = ActivitySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'data': serializer.data}, status=201)
        return Response(serializer.errors, status=400)

    items  = Activity.objects.filter(user_id=user_id)
    result = {
        'searchHistory':  list(items.filter(type='search') .values_list('data', flat=True)),
        'adsHistory':     list(items.filter(type='ads')    .values_list('data', flat=True)),
        'mentionHistory': list(items.filter(type='mention').values_list('data', flat=True)),
        'accountHistory': list(items.filter(type='account').values_list('data', flat=True)),
        'deletedItems':   list(items.filter(type='deleted').values_list('data', flat=True)),
        'reuseHistory':   list(items.filter(type='reuse')  .values_list('data', flat=True)),
    }
    return Response(result)


@api_view(['DELETE'])
def clear_activity(request, user_id, act_type):
    count, _ = Activity.objects.filter(user_id=user_id, type=act_type).delete()
    return Response({'success': True, 'deleted': count})


@api_view(['GET'])
def admin_activity(request):
    items = Activity.objects.all()[:200]
    return Response(ActivitySerializer(items, many=True).data)


# ══════════════════════════════════════════════════════════
#  EXPLORE
# ══════════════════════════════════════════════════════════
@api_view(['GET'])
def explore_list(request):
    category = request.query_params.get('category', None)
    posts    = ExplorePost.objects.filter(category=category) if category else ExplorePost.objects.all()
    return Response(ExplorePostSerializer(posts, many=True).data)


@api_view(['GET'])
def explore_trending(request):
    posts = ExplorePost.objects.filter(is_trending=True)[:20]
    return Response(ExplorePostSerializer(posts, many=True).data)


@api_view(['POST'])
def explore_create(request):
    serializer = ExplorePostSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)


@api_view(['POST'])
def explore_like(request, post_id):
    try:
        post        = ExplorePost.objects.get(id=post_id)
        post.likes += 1
        post.save()
        return Response({'success': True, 'likes': post.likes})
    except ExplorePost.DoesNotExist:
        return Response({'error': 'Not found'}, status=404)


@api_view(['DELETE'])
def explore_delete(request, post_id):
    try:
        ExplorePost.objects.get(id=post_id).delete()
        return Response({'success': True})
    except ExplorePost.DoesNotExist:
        return Response({'error': 'Not found'}, status=404)


# ══════════════════════════════════════════════════════════
#  HOME FEED
# ══════════════════════════════════════════════════════════
@api_view(['GET'])
def feed_list(request):
    return Response(HomeFeedPostSerializer(HomeFeedPost.objects.all(), many=True).data)


@api_view(['POST'])
def feed_create(request):
    serializer = HomeFeedPostSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)


@api_view(['POST'])
def feed_like(request, post_id):
    """
    Post like karo + post owner ko notification bhejo.
    Body: { liker_user_id }  (optional — agar missing ho tab bhi like count badh jaata hai)
    """
    try:
        post        = HomeFeedPost.objects.get(id=post_id)
        post.likes += 1
        post.save()

        # Auto notification — post owner ko batao
        liker_user_id = request.data.get('liker_user_id')
        if liker_user_id and str(liker_user_id) != str(post.user_id):
            create_notification(
                to_user_id   = post.user_id,
                from_user_id = liker_user_id,
                notif_type   = 'Likes',
            )

        return Response({'success': True, 'likes': post.likes})
    except HomeFeedPost.DoesNotExist:
        return Response({'error': 'Not found'}, status=404)


@api_view(['POST'])
def feed_share(request, post_id):
    try:
        post         = HomeFeedPost.objects.get(id=post_id)
        post.shares += 1
        post.save()
        return Response({'success': True, 'shares': post.shares})
    except HomeFeedPost.DoesNotExist:
        return Response({'error': 'Not found'}, status=404)


@api_view(['POST'])
def feed_save(request, post_id):
    try:
        post          = HomeFeedPost.objects.get(id=post_id)
        post.is_saved = not post.is_saved
        post.save()
        return Response({'success': True, 'is_saved': post.is_saved})
    except HomeFeedPost.DoesNotExist:
        return Response({'error': 'Not found'}, status=404)


@api_view(['DELETE'])
def feed_delete(request, post_id):
    try:
        HomeFeedPost.objects.get(id=post_id).delete()
        return Response({'success': True})
    except HomeFeedPost.DoesNotExist:
        return Response({'error': 'Not found'}, status=404)


@api_view(['GET', 'POST'])
def feed_comments(request, post_id):
    """
    Comment karo + post owner ko notification bhejo.
    POST body: { user_id, user_name, text }
    """
    try:
        post = HomeFeedPost.objects.get(id=post_id)
    except HomeFeedPost.DoesNotExist:
        return Response({'error': 'Not found'}, status=404)

    if request.method == 'POST':
        data         = request.data.copy()
        data['post'] = post.id
        serializer   = CommentSerializer(data=data)
        if serializer.is_valid():
            serializer.save()

            # Auto notification — post owner ko batao
            commenter_user_id = request.data.get('user_id')
            if commenter_user_id and str(commenter_user_id) != str(post.user_id):
                create_notification(
                    to_user_id   = post.user_id,
                    from_user_id = commenter_user_id,
                    notif_type   = 'Comments',
                )

            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    return Response(CommentSerializer(post.comments.all(), many=True).data)


# ══════════════════════════════════════════════════════════
#  AI CHAT HISTORY
# ══════════════════════════════════════════════════════════
@api_view(['GET', 'POST'])
def chat_history(request, user_id):
    if request.method == 'POST':
        data            = request.data.copy()
        data['user_id'] = user_id
        serializer      = ChatHistorySerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    return Response(ChatHistorySerializer(
        ChatHistory.objects.filter(user_id=user_id), many=True
    ).data)


@api_view(['DELETE'])
def clear_chat_history(request, user_id):
    count, _ = ChatHistory.objects.filter(user_id=user_id).delete()
    return Response({'success': True, 'deleted': count})


@api_view(['PATCH'])
def update_chat_message(request, msg_id):
    try:
        msg = ChatHistory.objects.get(id=msg_id)
        if 'liked' in request.data:
            msg.liked    = request.data['liked']
            msg.disliked = False
        if 'disliked' in request.data:
            msg.disliked = request.data['disliked']
            msg.liked    = False
        msg.save()
        return Response({'success': True})
    except ChatHistory.DoesNotExist:
        return Response({'error': 'Not found'}, status=404)


# ══════════════════════════════════════════════════════════
#  DETAIL PAGE
# ══════════════════════════════════════════════════════════
@api_view(['POST'])
def toggle_like(request):
    user_id   = request.data.get('user_id')
    post_id   = request.data.get('post_id')
    post_type = request.data.get('post_type', 'explore')
    existing  = PostLike.objects.filter(
        user_id=user_id, post_id=post_id, post_type=post_type
    ).first()
    if existing:
        existing.delete()
        return Response({'success': True, 'liked': False})
    PostLike.objects.create(user_id=user_id, post_id=post_id, post_type=post_type)
    return Response({'success': True, 'liked': True})


@api_view(['GET'])
def check_like(request, user_id, post_id):
    post_type = request.query_params.get('post_type', 'explore')
    exists    = PostLike.objects.filter(
        user_id=user_id, post_id=post_id, post_type=post_type
    ).exists()
    return Response({'liked': exists})


@api_view(['GET'])
def likes_count(request, post_id):
    post_type = request.query_params.get('post_type', 'explore')
    count     = PostLike.objects.filter(post_id=post_id, post_type=post_type).count()
    return Response({'post_id': post_id, 'likes': count})


@api_view(['POST'])
def save_view(request):
    user_id   = request.data.get('user_id')
    post_id   = request.data.get('post_id')
    post_type = request.data.get('post_type', 'explore')
    PostView.objects.create(user_id=user_id, post_id=post_id, post_type=post_type)
    total = PostView.objects.filter(post_id=post_id, post_type=post_type).count()
    return Response({'success': True, 'total_views': total})


@api_view(['GET'])
def views_count(request, post_id):
    post_type = request.query_params.get('post_type', 'explore')
    count     = PostView.objects.filter(post_id=post_id, post_type=post_type).count()
    return Response({'post_id': post_id, 'views': count})


# ══════════════════════════════════════════════════════════
#  ADMIN PANEL
# ══════════════════════════════════════════════════════════
@api_view(['GET'])
def admin_users_list(request):
    return Response(AdminUserSerializer(AdminUser.objects.all(), many=True).data)


@api_view(['POST'])
def admin_user_create(request):
    serializer = AdminUserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)


@api_view(['PATCH'])
def admin_user_update(request, user_id):
    try:
        user       = AdminUser.objects.get(id=user_id)
        serializer = AdminUserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'data': serializer.data})
        return Response(serializer.errors, status=400)
    except AdminUser.DoesNotExist:
        return Response({'error': 'Not found'}, status=404)


@api_view(['GET'])
def admin_reports_list(request):
    status  = request.query_params.get('status', None)
    reports = Report.objects.filter(status=status) if status else Report.objects.all()
    return Response(ReportSerializer(reports, many=True).data)


@api_view(['POST'])
def admin_report_create(request):
    serializer = ReportSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)


@api_view(['PATCH'])
def admin_report_action(request, report_id):
    try:
        report        = Report.objects.get(id=report_id)
        report.status = request.data.get('status', report.status)
        report.save()
        return Response({'success': True, 'status': report.status})
    except Report.DoesNotExist:
        return Response({'error': 'Not found'}, status=404)


# ══════════════════════════════════════════════════════════
#  ANALYTICS
# ══════════════════════════════════════════════════════════
@api_view(['GET'])
def get_analytics(request, user_id):
    try:
        analytics = UserAnalytics.objects.get(user_id=user_id)
        return Response(UserAnalyticsSerializer(analytics).data)
    except UserAnalytics.DoesNotExist:
        return Response({
            'user_id': user_id, 'new_followers': 0, 'engage_rate': 0.0,
            'weekly_growth': 0.0, 'performance': 0.0,
            'mon': 0, 'tue': 0, 'wed': 0, 'thu': 0, 'fri': 0,
        })


@api_view(['POST'])
def save_analytics(request, user_id):
    try:
        analytics  = UserAnalytics.objects.get(user_id=user_id)
        serializer = UserAnalyticsSerializer(analytics, data=request.data, partial=True)
    except UserAnalytics.DoesNotExist:
        data            = request.data.copy()
        data['user_id'] = user_id
        serializer      = UserAnalyticsSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response({'success': True, 'data': serializer.data})
    return Response(serializer.errors, status=400)


# ══════════════════════════════════════════════════════════
#  BALANCE
# ══════════════════════════════════════════════════════════
@api_view(['GET'])
def get_balance(request, user_id):
    try:
        balance = UserBalance.objects.get(user_id=user_id)
        return Response(UserBalanceSerializer(balance).data)
    except UserBalance.DoesNotExist:
        return Response({
            'user_id': user_id, 'balance_usd': 0.0,
            'total_coins': 0, 'low_balance_threshold': 5.0,
        })


@api_view(['POST'])
def save_balance(request, user_id):
    try:
        balance    = UserBalance.objects.get(user_id=user_id)
        serializer = UserBalanceSerializer(balance, data=request.data, partial=True)
    except UserBalance.DoesNotExist:
        data            = request.data.copy()
        data['user_id'] = user_id
        serializer      = UserBalanceSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response({'success': True, 'data': serializer.data})
    return Response(serializer.errors, status=400)


# ══════════════════════════════════════════════════════════
#  TRANSACTIONS
# ══════════════════════════════════════════════════════════
@api_view(['GET'])
def get_transactions(request, user_id):
    tx_type = request.query_params.get('type', None)
    txs     = Transaction.objects.filter(user_id=user_id)
    if tx_type:
        txs = txs.filter(type=tx_type)
    return Response(TransactionSerializer(txs, many=True).data)


@api_view(['POST'])
def create_transaction(request, user_id):
    data            = request.data.copy()
    data['user_id'] = user_id
    serializer      = TransactionSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        try:
            balance = UserBalance.objects.get(user_id=user_id)
            if data.get('type') == 'credit':
                balance.balance_usd += float(data.get('amount', 0))
            else:
                balance.balance_usd -= float(data.get('amount', 0))
            balance.save()
        except UserBalance.DoesNotExist:
            pass
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)


# ══════════════════════════════════════════════════════════
#  COIN LOG
# ══════════════════════════════════════════════════════════
@api_view(['GET'])
def get_coin_log(request, user_id):
    logs = CoinLog.objects.filter(user_id=user_id)
    return Response(CoinLogSerializer(logs, many=True).data)


@api_view(['POST'])
def add_coin_log(request, user_id):
    data            = request.data.copy()
    data['user_id'] = user_id
    serializer      = CoinLogSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        try:
            balance = UserBalance.objects.get(user_id=user_id)
            if data.get('type') == 'earned':
                balance.total_coins += int(data.get('coins', 0))
            else:
                balance.total_coins -= int(data.get('coins', 0))
            balance.save()
        except UserBalance.DoesNotExist:
            pass
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)


# ══════════════════════════════════════════════════════════
#  ALERTS
# ══════════════════════════════════════════════════════════
@api_view(['GET'])
def get_alerts(request, user_id):
    alerts = TransactionAlert.objects.filter(user_id=user_id)
    return Response(TransactionAlertSerializer(alerts, many=True).data)


@api_view(['POST'])
def create_alert(request, user_id):
    data            = request.data.copy()
    data['user_id'] = user_id
    serializer      = TransactionAlertSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)


@api_view(['PATCH'])
def mark_alert_read(request, alert_id):
    try:
        alert         = TransactionAlert.objects.get(id=alert_id)
        alert.is_read = True
        alert.save()
        return Response({'success': True})
    except TransactionAlert.DoesNotExist:
        return Response({'error': 'Not found'}, status=404)


@api_view(['PATCH'])
def mark_all_alerts_read(request, user_id):
    TransactionAlert.objects.filter(user_id=user_id).update(is_read=True)
    return Response({'success': True})


# ══════════════════════════════════════════════════════════
#  CHAT SYSTEM
# ══════════════════════════════════════════════════════════
@api_view(['GET'])
def get_conversations(request, user_id):
    convs = ChatConversation.objects.filter(user_id=user_id)
    return Response(ChatConversationSerializer(convs, many=True).data)


@api_view(['POST'])
def create_conversation(request, user_id):
    data            = request.data.copy()
    data['user_id'] = user_id
    serializer      = ChatConversationSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)


@api_view(['GET', 'POST'])
def conversation_messages(request, conv_id):
    try:
        conv = ChatConversation.objects.get(id=conv_id)
    except ChatConversation.DoesNotExist:
        return Response({'error': 'Not found'}, status=404)

    if request.method == 'POST':
        data                 = request.data.copy()
        data['conversation'] = conv.id
        serializer           = ChatMessageSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            conv.last_message = data.get('text', '')
            conv.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    return Response(ChatMessageSerializer(conv.messages.all(), many=True).data)


@api_view(['PATCH'])
def mark_messages_read(request, conv_id):
    ChatMessage.objects.filter(conversation_id=conv_id, is_read=False).update(is_read=True)
    return Response({'success': True})


@api_view(['DELETE'])
def delete_conversation(request, conv_id):
    try:
        ChatConversation.objects.get(id=conv_id).delete()
        return Response({'success': True})
    except ChatConversation.DoesNotExist:
        return Response({'error': 'Not found'}, status=404)


# ══════════════════════════════════════════════════════════
#  NOTIFICATIONS
# ══════════════════════════════════════════════════════════
@api_view(['GET'])
def get_notifications(request, user_id):
    notif_type = request.query_params.get('type', None)
    notes      = Notification.objects.filter(user_id=user_id)
    if notif_type:
        notes = notes.filter(type=notif_type)
    return Response(NotificationSerializer(notes, many=True).data)


@api_view(['POST'])
def create_notification_api(request, user_id):
    data            = request.data.copy()
    data['user_id'] = user_id
    serializer      = NotificationSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)


@api_view(['DELETE'])
def delete_notification(request, note_id):
    try:
        Notification.objects.get(id=note_id).delete()
        return Response({'success': True})
    except Notification.DoesNotExist:
        return Response({'error': 'Not found'}, status=404)


@api_view(['PATCH'])
def mark_notification_read(request, note_id):
    try:
        note         = Notification.objects.get(id=note_id)
        note.is_read = True
        note.save()
        return Response({'success': True})
    except Notification.DoesNotExist:
        return Response({'error': 'Not found'}, status=404)


@api_view(['PATCH'])
def mark_all_notifications_read(request, user_id):
    Notification.objects.filter(user_id=user_id).update(is_read=True)
    return Response({'success': True})


# ══════════════════════════════════════════════════════════
#  USER PROFILE
# ══════════════════════════════════════════════════════════
@api_view(['GET'])
def get_profile(request, user_id):
    try:
        profile = UserProfile.objects.get(user_id=user_id)
        return Response(UserProfileSerializer(profile).data)
    except UserProfile.DoesNotExist:
        return Response({
            'user_id': user_id, 'name': 'User', 'bio': '',
            'profile_image': '', 'followers': 0, 'following': 0, 'likes': 0,
        })


@api_view(['POST'])
def save_profile(request, user_id):
    try:
        profile    = UserProfile.objects.get(user_id=user_id)
        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
    except UserProfile.DoesNotExist:
        data            = request.data.copy()
        data['user_id'] = user_id
        serializer      = UserProfileSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response({'success': True, 'data': serializer.data})
    return Response(serializer.errors, status=400)


@api_view(['GET'])
def get_user_posts(request, user_id):
    posts = UserPost.objects.filter(user_id=user_id)
    return Response(UserPostSerializer(posts, many=True).data)


@api_view(['POST'])
def create_user_post(request, user_id):
    data            = request.data.copy()
    data['user_id'] = user_id
    serializer      = UserPostSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)


@api_view(['DELETE'])
def delete_user_post(request, post_id):
    try:
        UserPost.objects.get(id=post_id).delete()
        return Response({'success': True})
    except UserPost.DoesNotExist:
        return Response({'error': 'Not found'}, status=404)


# ══════════════════════════════════════════════════════════
#  REELS
# ══════════════════════════════════════════════════════════
@api_view(['POST'])
def reel_toggle_like(request):
    user_id  = request.data.get('user_id')
    video_id = request.data.get('video_id')
    existing = ReelLike.objects.filter(user_id=user_id, video_id=video_id).first()
    if existing:
        existing.delete()
        return Response({'success': True, 'liked': False})
    ReelLike.objects.create(user_id=user_id, video_id=video_id)
    return Response({'success': True, 'liked': True})


@api_view(['GET'])
def reel_liked_list(request, user_id):
    liked = ReelLike.objects.filter(user_id=user_id).values_list('video_id', flat=True)
    return Response({'liked_ids': list(liked)})


@api_view(['POST'])
def reel_toggle_save(request):
    user_id  = request.data.get('user_id')
    video_id = request.data.get('video_id')
    existing = ReelSave.objects.filter(user_id=user_id, video_id=video_id).first()
    if existing:
        existing.delete()
        return Response({'success': True, 'saved': False})
    ReelSave.objects.create(user_id=user_id, video_id=video_id)
    return Response({'success': True, 'saved': True})


@api_view(['GET'])
def reel_saved_list(request, user_id):
    saved = ReelSave.objects.filter(user_id=user_id).values_list('video_id', flat=True)
    return Response({'saved_ids': list(saved)})


@api_view(['POST'])
def reel_toggle_follow(request):
    user_id       = request.data.get('user_id')
    channel_title = request.data.get('channel_title')
    existing      = ReelFollow.objects.filter(
        user_id=user_id, channel_title=channel_title
    ).first()
    if existing:
        existing.delete()
        return Response({'success': True, 'following': False})
    ReelFollow.objects.create(user_id=user_id, channel_title=channel_title)
    return Response({'success': True, 'following': True})


@api_view(['GET'])
def reel_following_list(request, user_id):
    following = ReelFollow.objects.filter(user_id=user_id).values_list('channel_title', flat=True)
    return Response({'following': list(following)})


@api_view(['GET', 'POST'])
def reel_comments(request, video_id):
    if request.method == 'POST':
        data             = request.data.copy()
        data['video_id'] = video_id
        serializer       = ReelCommentSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    comments = ReelComment.objects.filter(video_id=video_id)
    return Response(ReelCommentSerializer(comments, many=True).data)


# ══════════════════════════════════════════════════════════
#  UPLOAD
# ══════════════════════════════════════════════════════════
@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser, JSONParser])
def upload_media(request):
    user_id = request.data.get('user_id')
    if not user_id:
        return Response({'success': False, 'message': 'user_id required'}, status=400)

    data = {
        'user_id':    user_id,
        'file_name':  request.data.get('file_name', ''),
        'file_size':  request.data.get('file_size', 0),
        'file_type':  request.data.get('file_type', ''),
        'media_type': request.data.get('media_type', 'video'),
        'caption':    request.data.get('caption', ''),
        'duration':   request.data.get('duration', ''),
        'resolution': request.data.get('resolution', ''),
        'file_url':   request.data.get('file_url', ''),
    }

    serializer = ReelUploadSerializer(data=data)
    if serializer.is_valid():
        upload = serializer.save()
        return Response({
            'success':   True,
            'message':   'Upload database mein save ho gaya!',
            'upload_id': upload.id,
            'data':      serializer.data,
        }, status=201)

    return Response({'success': False, 'errors': serializer.errors}, status=400)


@api_view(['GET'])
def get_uploads(request, user_id):
    uploads = ReelUpload.objects.filter(user_id=user_id)
    return Response({
        'success': True,
        'count':   uploads.count(),
        'data':    ReelUploadSerializer(uploads, many=True).data,
    })


@api_view(['DELETE'])
def delete_upload(request, upload_id):
    try:
        ReelUpload.objects.get(id=upload_id).delete()
        return Response({'success': True, 'message': 'Upload delete ho gaya'})
    except ReelUpload.DoesNotExist:
        return Response({'error': 'Not found'}, status=404)


# ══════════════════════════════════════════════════════════
#  EXPLORE SEARCH SAVE / CLICK SAVE
# ══════════════════════════════════════════════════════════
@api_view(['POST'])
def save_search(request):
    query         = request.data.get('query', '')
    results_count = request.data.get('results_count', 0)
    user_id       = request.data.get('user_id', 'anonymous')

    Activity.objects.create(
        user_id = str(user_id),
        type    = 'search',
        data    = {'query': query, 'results_count': results_count},
    )
    return Response({'success': True})
@api_view(['POST'])
def get_or_create_conversation(request):
    user1_id = request.data.get('user1_id')
    user2_id = request.data.get('user2_id')

    if not user1_id or not user2_id:
        return Response({'error': 'user1_id aur user2_id required'}, status=400)

    from django.db.models import Q
    conv = ChatConversation.objects.filter(
        Q(user_id=user1_id, other_user_id=user2_id) |
        Q(user_id=user2_id, other_user_id=user1_id)
    ).first()

    if not conv:
        conv = ChatConversation.objects.create(
            user_id=user1_id,
            other_user_id=user2_id
        )

    return Response({'id': conv.id})
@api_view(['GET'])
def new_messages(request, conv_id):
    after_id = int(request.GET.get('after', 0))
    msgs = ChatMessage.objects.filter(
        conversation_id=conv_id,
        id__gt=after_id
    ).order_by('id')

    data = [{
        'id':        m.id,
        'text':      m.text,
        'sender_id': m.sender_id,
        'created_at': m.created_at.isoformat(),
        'is_read':   m.is_read,
    } for m in msgs]

    return Response(data)
# ══════════════════════════════════════════════════════════
#  YEH DO FUNCTIONS apni views.py mein add karein
#  (existing code ke neeche paste karein)
# ══════════════════════════════════════════════════════════

from django.db.models import Q

@api_view(['GET'])
def new_messages(request, conv_id):
    """
    GET /api/conversations/<conv_id>/messages/new/?after=<last_message_id>
    Sirf wo messages jo after ID ke baad aaye hain.
    Polling ke liye use hota hai — har 3 sec mein frontend call karta hai.
    """
    try:
        after_id = int(request.GET.get('after', 0))
    except ValueError:
        after_id = 0

    try:
        conv = ChatConversation.objects.get(id=conv_id)
    except ChatConversation.DoesNotExist:
        return Response([], status=200)

    msgs = ChatMessage.objects.filter(
        conversation=conv,
        id__gt=after_id
    ).order_by('id')

    data = [{
        'id':         m.id,
        'text':       m.text,
        'sender_id':  m.sender_id,
        'created_at': m.created_at.isoformat(),
        'is_read':    m.is_read,
    } for m in msgs]

    return Response(data)


@api_view(['POST'])
def get_or_create_conversation(request):
    """
    POST /api/conversations/get-or-create/
    Body: { "user1_id": 1, "user2_id": 2 }

    Agar in do users ke beech conversation already hai → wahi return karo
    Agar nahi hai → naya banao
    """
    user1_id = request.data.get('user1_id')
    user2_id = request.data.get('user2_id')

    if not user1_id or not user2_id:
        return Response({'error': 'user1_id aur user2_id required hain'}, status=400)

    if str(user1_id) == str(user2_id):
        return Response({'error': 'Apne aap se chat nahi kar sakte'}, status=400)

    # Dono directions check karo
    conv = ChatConversation.objects.filter(
        Q(user_id=user1_id, other_user_id=user2_id) |
        Q(user_id=user2_id, other_user_id=user1_id)
    ).first()

    if not conv:
        conv = ChatConversation.objects.create(
            user_id=user1_id,
            other_user_id=user2_id,
            name=f'Chat_{user1_id}_{user2_id}'
        )

    return Response({'id': conv.id, 'created': conv is not None})

@api_view(['POST'])
def save_click(request):
    user_id   = request.data.get('user_id', 'anonymous')
    Activity.objects.create(
        user_id = str(user_id),
        type    = 'reuse',
        data    = {
            'item_id':   request.data.get('item_id'),
            'item_type': request.data.get('item_type'),
            'title':     request.data.get('title'),
            'thumb_url': request.data.get('thumb_url'),
            'video_id':  request.data.get('video_id'),
        },
    )
    
    return Response({'success': True})