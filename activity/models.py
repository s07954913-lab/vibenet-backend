from django.db import models


# ─── USER ─────────────────────────────────────────────────
class User(models.Model):
    username   = models.CharField(max_length=100)
    email      = models.EmailField(unique=True)
    password   = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email


# ─── ACTIVITY ─────────────────────────────────────────────
class Activity(models.Model):
    TYPE_CHOICES = [
        ('search',  'Search History'),
        ('ads',     'Ad Link History'),
        ('mention', 'Mention History'),
        ('account', 'Account History'),
        ('reuse',   'Content Reuse'),
        ('deleted', 'Recently Deleted'),
    ]
    user_id    = models.CharField(max_length=100)
    type       = models.CharField(max_length=50, choices=TYPE_CHOICES)
    data       = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user_id} — {self.type}"


# ─── EXPLORE ──────────────────────────────────────────────
class ExplorePost(models.Model):
    CATEGORY_CHOICES = [
        ('trending', 'Trending'), ('drama', 'Drama'),
        ('comedy',   'Comedy'),   ('islamic', 'Islamic'),
        ('sports',   'Sports'),   ('food', 'Food'),
        ('music',    'Music'),    ('other', 'Other'),
    ]
    title       = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    image_url   = models.URLField()
    category    = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='other')
    user_name   = models.CharField(max_length=100)
    user_img    = models.URLField(blank=True)
    likes       = models.IntegerField(default=0)
    views       = models.IntegerField(default=0)
    is_trending = models.BooleanField(default=False)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


# ─── HOME FEED ────────────────────────────────────────────
class HomeFeedPost(models.Model):
    TYPE_CHOICES = [('image', 'Image'), ('video', 'Video')]
    user_id    = models.IntegerField()
    user_name  = models.CharField(max_length=100)
    user_img   = models.URLField(blank=True)
    type       = models.CharField(max_length=10, choices=TYPE_CHOICES, default='image')
    media_url  = models.URLField(max_length=1000)
    caption    = models.TextField(blank=True)
    likes      = models.IntegerField(default=0)
    shares     = models.IntegerField(default=0)
    is_saved   = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user_name} — {self.type}"


class Comment(models.Model):
    post       = models.ForeignKey(HomeFeedPost, on_delete=models.CASCADE, related_name='comments')
    user_id    = models.IntegerField()
    user_name  = models.CharField(max_length=100)
    text       = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user_name}: {self.text[:30]}"


# ─── AI CHAT HISTORY ──────────────────────────────────────
class ChatHistory(models.Model):
    ROLE_CHOICES = [('user', 'User'), ('assistant', 'Assistant')]
    user_id    = models.IntegerField()
    role       = models.CharField(max_length=20, choices=ROLE_CHOICES)
    content    = models.TextField()
    liked      = models.BooleanField(default=False)
    disliked   = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.user_id} — {self.role}: {self.content[:30]}"


# ─── POST LIKE / VIEW ─────────────────────────────────────
class PostLike(models.Model):
    user_id    = models.IntegerField()
    post_id    = models.IntegerField()
    post_type  = models.CharField(max_length=50, default='explore')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user_id', 'post_id', 'post_type')

    def __str__(self):
        return f"User {self.user_id} liked {self.post_type} {self.post_id}"


class PostView(models.Model):
    user_id    = models.IntegerField()
    post_id    = models.IntegerField()
    post_type  = models.CharField(max_length=50, default='explore')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"User {self.user_id} viewed {self.post_type} {self.post_id}"


# ─── ADMIN ────────────────────────────────────────────────
class AdminUser(models.Model):
    STATUS_CHOICES = [
        ('active',     'Active'),
        ('suspended',  'Suspended'),
        ('banned',     'Banned'),
    ]
    name       = models.CharField(max_length=100)
    email      = models.EmailField(unique=True)
    initials   = models.CharField(max_length=5, blank=True)
    color      = models.CharField(max_length=20, default='gray')
    status     = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    joined     = models.CharField(max_length=50, blank=True)
    posts      = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.status})"


class Report(models.Model):
    TYPE_CHOICES   = [('image', 'Image'), ('doc', 'Document')]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('kept',    'Kept'),
        ('removed', 'Removed'),
    ]
    type       = models.CharField(max_length=10, choices=TYPE_CHOICES, default='doc')
    title      = models.CharField(max_length=200)
    desc       = models.TextField(blank=True)
    detail     = models.TextField(blank=True)
    img        = models.URLField(blank=True)
    status     = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.status})"


# ─── ANALYTICS ────────────────────────────────────────────
class UserAnalytics(models.Model):
    user_id       = models.IntegerField(unique=True)
    new_followers = models.IntegerField(default=0)
    engage_rate   = models.FloatField(default=0.0)
    weekly_growth = models.FloatField(default=0.0)
    performance   = models.FloatField(default=0.0)
    mon           = models.IntegerField(default=0)
    tue           = models.IntegerField(default=0)
    wed           = models.IntegerField(default=0)
    thu           = models.IntegerField(default=0)
    fri           = models.IntegerField(default=0)
    updated_at    = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Analytics — User {self.user_id}"


# ─── BALANCE ──────────────────────────────────────────────
class UserBalance(models.Model):
    user_id               = models.IntegerField(unique=True)
    balance_usd           = models.FloatField(default=0.0)
    total_coins           = models.IntegerField(default=0)
    low_balance_threshold = models.FloatField(default=5.0)
    updated_at            = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Balance — User {self.user_id}: ${self.balance_usd}"


# ─── TRANSACTIONS ─────────────────────────────────────────
class Transaction(models.Model):
    TYPE_CHOICES   = [('credit', 'Credit'), ('debit', 'Debit')]
    STATUS_CHOICES = [
        ('completed', 'Completed'),
        ('pending',   'Pending'),
        ('failed',    'Failed'),
    ]
    user_id     = models.IntegerField()
    type        = models.CharField(max_length=10, choices=TYPE_CHOICES)
    amount      = models.FloatField()
    description = models.CharField(max_length=255)
    status      = models.CharField(max_length=20, choices=STATUS_CHOICES, default='completed')
    currency    = models.CharField(max_length=10, default='USD')
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user_id} — {self.type}: ${self.amount}"


class CoinLog(models.Model):
    TYPE_CHOICES = [('earned', 'Earned'), ('spent', 'Spent')]
    user_id     = models.IntegerField()
    type        = models.CharField(max_length=10, choices=TYPE_CHOICES)
    coins       = models.IntegerField()
    description = models.CharField(max_length=255)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user_id} — {self.type}: {self.coins} coins"


class TransactionAlert(models.Model):
    TYPE_CHOICES = [
        ('credit',  'Credit'),
        ('debit',   'Debit'),
        ('warning', 'Warning'),
    ]
    user_id    = models.IntegerField()
    type       = models.CharField(max_length=10, choices=TYPE_CHOICES)
    title      = models.CharField(max_length=100)
    message    = models.TextField()
    is_read    = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user_id} — {self.title}"


# ─── CHAT SYSTEM ──────────────────────────────────────────
class ChatConversation(models.Model):
    user_id      = models.IntegerField()
    other_name   = models.CharField(max_length=100)
    other_img    = models.CharField(max_length=500, blank=True)
    last_message = models.TextField(blank=True)
    is_online    = models.BooleanField(default=False)
    updated_at   = models.DateTimeField(auto_now=True)
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"User {self.user_id} ↔ {self.other_name}"


class ChatMessage(models.Model):
    conversation = models.ForeignKey(
        ChatConversation, on_delete=models.CASCADE, related_name='messages'
    )
    sender_id  = models.IntegerField()
    text       = models.TextField()
    is_read    = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Msg from {self.sender_id}: {self.text[:30]}"


# ─── NOTIFICATIONS ────────────────────────────────────────
class Notification(models.Model):
    TYPE_CHOICES = [
        ('Follow',   'Follow'),
        ('Likes',    'Likes'),
        ('Comments', 'Comments'),
    ]
    user_id    = models.IntegerField()
    from_name  = models.CharField(max_length=100)
    from_img   = models.CharField(max_length=500, blank=True)
    type       = models.CharField(max_length=20, choices=TYPE_CHOICES)
    is_read    = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.from_name} → {self.type} → User {self.user_id}"


# ─── USER PROFILE ─────────────────────────────────────────
class UserProfile(models.Model):
    user_id       = models.IntegerField(unique=True)
    name          = models.CharField(max_length=100)
    bio           = models.TextField(blank=True)
    profile_image = models.CharField(max_length=500, blank=True)
    followers     = models.IntegerField(default=0)
    following     = models.IntegerField(default=0)
    likes         = models.IntegerField(default=0)
    updated_at    = models.DateTimeField(auto_now=True)
    created_at    = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} (User {self.user_id})"


class UserPost(models.Model):
    user_id    = models.IntegerField()
    video_url  = models.CharField(max_length=1000)
    caption    = models.TextField(blank=True)
    views      = models.CharField(max_length=20, default='0')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Post by User {self.user_id}"


# ─── REELS ────────────────────────────────────────────────
class ReelLike(models.Model):
    user_id    = models.IntegerField()
    video_id   = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user_id', 'video_id')

    def __str__(self):
        return f"User {self.user_id} liked {self.video_id}"


class ReelSave(models.Model):
    user_id    = models.IntegerField()
    video_id   = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user_id', 'video_id')

    def __str__(self):
        return f"User {self.user_id} saved {self.video_id}"


class ReelFollow(models.Model):
    user_id       = models.IntegerField()
    channel_title = models.CharField(max_length=200)
    created_at    = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user_id', 'channel_title')

    def __str__(self):
        return f"User {self.user_id} follows {self.channel_title}"


class ReelComment(models.Model):
    user_id    = models.IntegerField()
    video_id   = models.CharField(max_length=100)
    user_name  = models.CharField(max_length=100)
    text       = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user_name}: {self.text[:30]}"


# ─── VIDEO / PHOTO UPLOAD ─────────────────────────────────
class ReelUpload(models.Model):
    TYPE_CHOICES = [('video', 'Video'), ('image', 'Image')]

    user_id    = models.IntegerField()
    file_name  = models.CharField(max_length=500)
    file_size  = models.FloatField(help_text='Size in MB')
    file_type  = models.CharField(max_length=100)
    media_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='video')
    caption    = models.TextField(blank=True)
    duration   = models.CharField(max_length=20, blank=True, help_text='e.g. 0:42 min')
    resolution = models.CharField(max_length=50, blank=True, help_text='e.g. 1920x1080')
    file_url   = models.CharField(max_length=1000, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Upload by User {self.user_id} — {self.file_name}"


# ─── USER FOLLOW (NAYA) ───────────────────────────────────
# User-to-user follow system (TikTok style)
class UserFollow(models.Model):
    follower_id  = models.IntegerField()   # jo follow kar raha hai
    following_id = models.IntegerField()   # jise follow kar rahe hain
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower_id', 'following_id')
        ordering        = ['-created_at']

    def __str__(self):
        return f"User {self.follower_id} → follows → User {self.following_id}"
    # ─── API LOG MONITOR ──────────────────────────────────────
class APILog(models.Model):
    method        = models.CharField(max_length=10)
    path          = models.CharField(max_length=500)
    status_code   = models.IntegerField()
    request_body  = models.TextField(blank=True)
    response_body = models.TextField(blank=True)
    ip_address    = models.GenericIPAddressField(null=True)
    duration_ms   = models.FloatField(default=0)
    timestamp     = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.method} {self.path} → {self.status_code}"