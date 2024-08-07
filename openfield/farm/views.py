from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from rest_framework import status
from rest_framework.response import Response
from django.db.models import OuterRef, Subquery
from datetime import datetime
from .models import Farm, FarmStatusLog
from .serializers import *
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .detectChangeService import makeChangeRate


# 페이지네이션 설정
class FarmPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 100
    
# 관리자 list view
@method_decorator(ensure_csrf_cookie, name='dispatch')
class FarmAdminListAPIView(generics.ListAPIView):
    permission_classes = [IsAdminUser]
    
    serializer_class = FarmListSerializer
    pagination_class = FarmPagination  # 페이지네이션 클래스 설정

    def get_queryset(self):
        queryset = Farm.objects.filter(farmillegalbuildinglog__farm_illegal_building_status=0)

        # farm_created 필터링 기준으로 받기
        farm_created_param = self.request.query_params.get('farm_created', None)
        if farm_created_param:
            try:
                farm_created_date = datetime.strptime(farm_created_param, '%Y%m%d').date()
                # farm_created_date를 기준으로 필터링
                queryset = queryset.filter(
                    status_logs__farm_created__date__gte=farm_created_date
                ).distinct()
            except ValueError:
                # 날짜 형식이 올바르지 않은 경우 처리
                queryset = Farm.objects.none()  # 빈 쿼리셋 반환

        return queryset

# 관리자 detail view
@method_decorator(ensure_csrf_cookie, name='dispatch')
class FarmAdminDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAdminUser]
    
    serializer_class = FarmDetailSerializer
    queryset = Farm.objects.filter(farmillegalbuildinglog__farm_illegal_building_status=0)
    
    def post(self, request, *args, **kwargs):
        farm_id = self.kwargs.get('pk')
        has_change_detection = FarmChangeDetection.objects.filter(farm_id=farm_id).exists()
        
        if has_change_detection:
            makeChangeRate(farm_id)
            return Response({'msg': 'success'}, status=status.HTTP_201_CREATED)
        return Response({'msg': 'no satellite imgs in the land'}, status=status.HTTP_404_NOT_FOUND)

# 불법건축물 list view
@method_decorator(ensure_csrf_cookie, name='dispatch')
class FarmIbDetectedListAPIView(generics.ListAPIView):
    permission_classes = [IsAdminUser]
    
    serializer_class = FarmListSerializer
    pagination_class = FarmPagination  # 페이지네이션 클래스 설정

    def get_queryset(self):
        queryset = Farm.objects.filter(farmillegalbuildinglog__farm_illegal_building_status=1)
        return queryset

# 불법건축물 detail view
@method_decorator(ensure_csrf_cookie, name='dispatch')
class FarmIbDetectedDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAdminUser]
    
    serializer_class = FarmPolygonDetectionDetailSerializer
    queryset = Farm.objects.filter(farmillegalbuildinglog__farm_illegal_building_status=1)

# 사용자 list view
@method_decorator(ensure_csrf_cookie, name='dispatch')
class FarmUserListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    
    serializer_class = FarmListSerializer
    def get_queryset(self):
        queryset = get_user_farms()
        return queryset

# # 사용자 detail view
@method_decorator(ensure_csrf_cookie, name='dispatch')
class FarmUserDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FarmDetailSerializer
    
    def get_queryset(self):
        queryset = get_user_farms()
        return queryset
    
    def post(self, request, *args, **kwargs):
        user_id = request.user.id
        farm_id = self.kwargs.get('pk')
        try:
            farm = Farm.objects.get(pk=farm_id)
            recent_log = FarmStatusLog.objects.filter(farm=farm).order_by('-farm_created').first()
            if recent_log and recent_log.farm_status != 1:
                return Response({'msg': 'The latest farm status is not 1.'}, status=status.HTTP_400_BAD_REQUEST)

            FarmStatusLog.objects.create(
                farm=farm,
                farm_status=2,
                user_id=user_id
            )
            return Response({'msg': 'success'}, status=status.HTTP_201_CREATED)
        except Farm.DoesNotExist:
            return Response({'msg': 'Farm not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'msg': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# 사용자 mypage list view
@method_decorator(ensure_csrf_cookie, name='dispatch')
class FarmUserMypageListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FarmStatusLogMypageSerializer
    
    def get_queryset(self):
        user_id = self.request.user.id
        queryset = FarmStatusLog.objects.filter(user_id=user_id).all()
        return queryset
    
# 관리자 mypage list view
@method_decorator(ensure_csrf_cookie, name='dispatch')
class FarmAdminMypageListView(generics.ListAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = FarmStatusLogMypageSerializer
    
    def get_queryset(self):
        # queryset = FarmStatusLog.objects.filter(farm_status=2).all() 
        # return queryset
        latest_logs = FarmStatusLog.objects.filter(
            farm=OuterRef('farm')
        ).order_by('-farm_created')
        
        queryset = FarmStatusLog.objects.filter(
            farm_status=2,
            farm_created=Subquery(latest_logs.values('farm_created')[:1])
        )
        
        return queryset

@method_decorator(ensure_csrf_cookie, name='dispatch')
class FarmAdminMypageDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = FarmStatusLogMypageSerializer
    
    def post(self, request, *args, **kwargs):
        user_id = request.data.get("user_id")
        farm_id = self.kwargs.get('pk')
        try:
            farm = Farm.objects.get(pk=farm_id)
            recent_log = FarmStatusLog.objects.filter(farm=farm).order_by('-farm_created').first()
            if recent_log and recent_log.farm_status != 2:
                return Response({'msg': 'The latest farm status is not 2.'}, status=status.HTTP_400_BAD_REQUEST)

            FarmStatusLog.objects.create(
                farm=farm,
                farm_status=3,
                user_id=user_id
            )
            return Response({'msg': 'success'}, status=status.HTTP_201_CREATED)
        except Farm.DoesNotExist:
            return Response({'msg': 'Farm not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'msg': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def delete(self, request, *args, **kwargs):
        user_id = request.data.get("user_id")
        farm_id = self.kwargs.get('pk')
        try:
            farm = Farm.objects.get(pk=farm_id)
            recent_log = FarmStatusLog.objects.filter(farm=farm).order_by('-farm_created').first()
            if recent_log and recent_log.farm_status != 2:
                return Response({'msg': 'The latest farm status is not 2.'}, status=status.HTTP_400_BAD_REQUEST)

            FarmStatusLog.objects.create(
                farm=farm,
                farm_status=1,
                user_id=user_id
            )
            return Response({'msg': 'success'}, status=status.HTTP_201_CREATED)
        except Farm.DoesNotExist:
            return Response({'msg': 'Farm not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'msg': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@method_decorator(ensure_csrf_cookie, name='dispatch')
class FarmChangeDetectionView(generics.RetrieveAPIView):
    permission_classes=[IsAdminUser]
    serializer_class = FarmChangeDetectionLogDetailSerializer
    queryset = Farm.objects.all()
    
    
    
def get_user_farms():
    threshold = 9
    
    latest_farm_status_log = FarmStatusLog.objects.filter(
        farm=OuterRef('pk')
    ).order_by('-farm_created').values('farm_status')[:1]
    
    latest_change_detection_log = FarmChangeDetectionLog.objects.filter(
        farm=OuterRef('pk')
    ).order_by('-farm_change_detection_log_created').values('change_rating_result')[:1]

    queryset = Farm.objects.filter(
        farmillegalbuildinglog__farm_illegal_building_status=0
    ).annotate(
        latest_status=Subquery(latest_farm_status_log)
    ).filter(
        latest_status=1
    )

    queryset = queryset.annotate(
        latest_change_rating_result=Subquery(latest_change_detection_log)
    ).filter(
        latest_change_rating_result__isnull=False
    ).filter(
        latest_change_rating_result__lte=threshold
    )
    
    return queryset
