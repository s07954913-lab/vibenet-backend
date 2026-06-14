from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import ProductSearchHistory
from activity.models import Activity, User


@api_view(['POST'])
def save_search(request):
    query         = request.data.get('query')
    results_count = request.data.get('results_count', 0)
    user_id       = request.data.get('user_id')

    obj = ProductSearchHistory.objects.create(
        query=query,
        results_count=results_count,
        user_id=user_id,
    )

    if user_id:
        Activity.objects.create(
            user_id=str(user_id),
            type='search',
            data={
                'query':         query,
                'results_count': results_count,
            }
        )

    return Response({'success': True, 'id': obj.id}, status=201)