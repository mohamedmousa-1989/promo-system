from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveUpdateDestroyAPIView, RetrieveAPIView

from promoapp.serializers import PromoSerializer, RemainingPointsSerializer, ConsumePromoPointsSerializer
from promoapp.models import Promo
from promoapp.permissions import IsAdmin, PromoOwnerOrAdmin

class PromoList(ListAPIView):
    """List of all promos available and their recipients."""
    
    queryset = Promo.objects.all()
    serializer_class = PromoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """Show only promos of particular user if not an admin."""

        if not request.user.is_staff or not request.user.is_superuser:
            self.queryset = Promo.objects.filter(recipient=request.user)
        
        return super().get(request, *args, **kwargs)


class PromoCreate(CreateAPIView):
    """Create a promo."""

    serializer_class = PromoSerializer
    queryset = Promo.objects.all()
    permission_classes = [IsAdmin]

    def create(self, request, *args, **kwargs):
        """Validate user input."""

        try:
            points = request.data.get('points')
            if points is not None and float(points) <= 0.0:
                raise ValidationError({'Points: points should be greater than zero.'})
        except ValueError:
            raise ValidationError({'Points: please enter a valid number.'})
        return super().create(request, *args, **kwargs)


class PromoRetrieveUpdateDelete(RetrieveUpdateDestroyAPIView):
    """Get, update or delete a promo."""

    queryset = Promo.objects.all()
    lookup_field = 'id'
    serializer_class = PromoSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]

    def delete(self, request, *args, **kwargs):
        """Delete the promo from cache on successful deletion."""
        promo_id = request.data.get('id')
        response = super().delete(request, *args, **kwargs)
        if response.status_code == 204:
            from django.core.cache import cache
            cache.delete('promo_data_{}'.format(promo_id))
        return response

    def update(self, request, *args, **kwargs):
        """Update the promo data in cache on successful updating."""
        response = super().update(request, *args, **kwargs)
        if response.status_code == 200:
            from django.core.cache import cache
            promo = response.data
            cache.set('promo_data_{}'.format(promo['id']), {
                'name': promo['name'],
                'points': promo['points'],
            })
        return response


class RemainingPointsRetrieve(RetrieveAPIView):
    """Get the remaining points of a particular promo."""
    
    queryset = Promo.objects.all()
    serializer_class = RemainingPointsSerializer
    lookup_field = 'id'
    permission_classes = [permissions.IsAuthenticated, PromoOwnerOrAdmin]


class ConsumePromoPoints(RetrieveAPIView):
    """Get the remaining points of a particular promo."""
    
    queryset = Promo.objects.all()
    serializer_class = ConsumePromoPointsSerializer
    lookup_field = 'id'
    permission_classes = [permissions.IsAuthenticated, PromoOwnerOrAdmin]
    
    def get(self, request, *args, **kwargs):
        points_to_use = kwargs.get('points_to_use', None)
        promo = self.get_object()
        promo_points_left = promo.points - promo.points_used
        promo.points_used += points_to_use
        if promo.points_used > promo.points:
            raise ValidationError({'You do NOT have enough points. You have only {} points left.'.format(promo_points_left)})        
        promo.save()

        return Response({
            'msg': '{} points deducted from {} successfully.'.format(points_to_use, promo.name),
            'Remaining points': promo_points_left - points_to_use
        })