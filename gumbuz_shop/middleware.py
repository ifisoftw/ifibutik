import datetime
from django.core.cache import cache
from django.conf import settings

class ActiveUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.session.session_key:
            # Get current dict
            active_users = cache.get('active_users_dict', {})
            
            # Update current user timestamp
            now = datetime.datetime.now().timestamp()
            active_users[request.session.session_key] = now
            
            # Cleanup expired (optional optimization: do this only occasionally)
            timeout = 300
            active_users = {k: v for k, v in active_users.items() if now - v < timeout}
            
            # Save back
            cache.set('active_users_dict', active_users, timeout + 60)

        response = self.get_response(request)
        return response

def get_active_user_count():
    # This is a bit expensive for Redis/Memcached if we have millions of keys,
    # but for a small shop with local memory cache or limited users, it's fine.
    # For production with Redis, we might want to use a set or a different approach.
    # Since we are using default cache (likely LocMem or simple file), we can iterate keys if possible
    # OR we maintain a separate set of active keys.
    
    # Improved approach: Maintain a set of active session keys
    # But for simplicity and standard Django cache, we can't easily iterate keys in all backends.
    # Let's use a slightly different approach: 
    # We will just rely on the middleware setting keys, but counting them is hard without a set.
    
    # Alternative: Use a single cache key storing a dict of active users? 
    # No, race conditions.
    
    # Alternative: Redis `keys` command (if redis).
    # Since I don't know the cache backend for sure (likely default LocMem for dev), 
    # I will assume we can't easily count keys.
    
    # Let's try a "Online Users" model approach or a shared cache set?
    # Actually, for a simple dashboard, we can use a "bucket" approach or just a simple list if traffic is low.
    
    # Let's stick to the plan but refine: 
    # We will use a dedicated cache key `active_users_list` which is a dict {session_key: timestamp}.
    # We clean it up on read.
    
    active_users = cache.get('active_users_dict', {})
    
    # Clean up expired
    now = datetime.datetime.now().timestamp()
    timeout = 300 # 5 minutes
    
    # Filter out expired
    active_users = {k: v for k, v in active_users.items() if now - v < timeout}
    
    return len(active_users)
