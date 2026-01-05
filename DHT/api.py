from rest_framework.decorators import api_view
from rest_framework import generics, status
from rest_framework.response import Response
from django.core.mail import send_mail
from django.conf import settings
from .models import Dht11
from .serializers import DHT11Serializer
from .utils import send_telegram

@api_view(['GET'])
def Dlist(request):
    all_data = Dht11.objects.all().order_by('-dt')
    serializer = DHT11Serializer(all_data, many=True)
    return Response({'data': serializer.data}, status=status.HTTP_200_OK)


class DhtViews(generics.CreateAPIView):
    queryset = Dht11.objects.all()
    serializer_class = DHT11Serializer

    def perform_create(self, serializer):
        instance = serializer.save()
        temp = instance.temp

        # 🔥 Alerte température élevée
        if temp > 25:
            # Email (facultatif)
            try:
                send_mail(
                    subject="⚠️ Alerte Température élevée",
                    message=f"La température a atteint {temp:.1f} °C à {instance.dt}.",
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=["saidi02.ma@gmail.com"],
                    fail_silently=True,
                )
            except Exception:
                pass

            # Telegram
            msg = f"⚠️ Alerte DHT11: {temp:.1f} °C (>25) à {instance.dt}"
            send_telegram(msg)
