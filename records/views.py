from django.db.models import Count
from django.db.models.functions import TruncMonth
from rest_framework import generics
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .auth import fetch_supabase_user, get_bearer_token
from .models import Animal, Profile, Treatment
from .permissions import IsVetOrReadOnly
from .serializers import AnimalSerializer, TreatmentSerializer


class AnimalPagination(PageNumberPagination):
    page_size = 5


def animals_for(user):
    qs = Animal.objects.all()
    return qs if user.role == 'vet' else qs.filter(owner_id=user.id)


def treatments_for(user):
    qs = Treatment.objects.all()
    if user.role == 'vet':
        return qs
    return qs.filter(animal__owner_id=user.id)


class Register(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        token = get_bearer_token(request)
        if not token:
            return Response(
                {'detail': 'Authentication credentials were not provided.'},
                status=401)
        try:
            data = fetch_supabase_user(token)
        except AuthenticationFailed as exc:
            return Response({'detail': str(exc.detail)}, status=401)

        meta = data.get('user_metadata') or {}
        name = meta.get('full_name') or (data.get('email') or 'user').split('@')[0]
        profile, created = Profile.objects.get_or_create(
            id=data['id'],
            defaults={'full_name': name, 'role': 'farmer'},
        )
        return Response(
            {'id': str(profile.id), 'full_name': profile.full_name,
             'role': profile.role},
            status=201 if created else 200,
        )


class AnimalListCreate(generics.ListCreateAPIView):
    serializer_class = AnimalSerializer
    pagination_class = AnimalPagination

    def get_queryset(self):
        return animals_for(self.request.user).order_by('id')

    def perform_create(self, serializer):
        user = self.request.user
        if user.role == 'farmer':
            serializer.save(owner=Profile.objects.get(pk=user.id))
        else:
            if 'owner' not in serializer.validated_data:
                raise ValidationError({'owner': ['This field is required.']})
            serializer.save()


class AnimalDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AnimalSerializer

    def get_queryset(self):
        return animals_for(self.request.user)

    def perform_update(self, serializer):
        user = self.request.user
        if user.role == 'farmer':
            serializer.save(owner=Profile.objects.get(pk=user.id))
        else:
            serializer.save()


class TreatmentListCreate(generics.ListCreateAPIView):
    serializer_class = TreatmentSerializer
    permission_classes = [IsVetOrReadOnly]

    def get_queryset(self):
        qs = treatments_for(self.request.user)
        animal_id = self.request.query_params.get('animal')
        if animal_id and animal_id.isdigit():
            qs = qs.filter(animal_id=animal_id)
        return qs.order_by('id')

    def perform_create(self, serializer):
        serializer.save(vet=Profile.objects.get(pk=self.request.user.id))


class TreatmentDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TreatmentSerializer
    permission_classes = [IsVetOrReadOnly]

    def get_queryset(self):
        return treatments_for(self.request.user)


class TreatmentAnalytics(APIView):
    """Treatments per species per month."""

    def get(self, request):
        rows = (
            treatments_for(request.user)
            .annotate(month=TruncMonth('treat_date'))
            .values('animal__species', 'month')
            .annotate(count=Count('id'))
            .order_by('month', 'animal__species')
        )
        data = [
            {
                'species': r['animal__species'],
                'month': r['month'].strftime('%Y-%m'),
                'count': r['count'],
            }
            for r in rows
        ]
        return Response(data)