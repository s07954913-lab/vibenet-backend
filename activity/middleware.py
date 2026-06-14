import time
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import APILog

class APILoggerMiddleware:
    def __init__(self, get_response):
        self.get_response  = get_response
        self.channel_layer = get_channel_layer()

    def __call__(self, request):
        start = time.time()

        try:
            req_body = request.body.decode('utf-8')[:2000]
        except:
            req_body = ''

        response = self.get_response(request)
        duration = round((time.time() - start) * 1000, 2)

        if request.path.startswith('/api/'):
            try:
                res_body = response.content.decode('utf-8')[:2000]
            except:
                res_body = ''

            log = APILog.objects.create(
                method        = request.method,
                path          = request.path,
                status_code   = response.status_code,
                request_body  = req_body,
                response_body = res_body,
                ip_address    = request.META.get('REMOTE_ADDR'),
                duration_ms   = duration,
            )

            # Live broadcast admin ko
            try:
                async_to_sync(self.channel_layer.group_send)('api_logs', {
                    'type':        'new_log',
                    'method':      log.method,
                    'path':        log.path,
                    'status_code': log.status_code,
                    'duration_ms': log.duration_ms,
                    'ip_address':  str(log.ip_address),
                    'timestamp':   str(log.timestamp),
                })
            except:
                pass

        return response