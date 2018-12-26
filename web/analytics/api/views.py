from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from web.analytics.service import Analytics

class AnalyticsTrackView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        data = request.data
        
        Analytics.track(
            event = data.get("event"),
            user = request.user,
            entity_id = data.get("entity_id")
        )

        return Response({
        }, status=status.HTTP_200_OK)
