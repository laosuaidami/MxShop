
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import mixins
from rest_framework import generics, filters
from rest_framework.pagination import PageNumberPagination
from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.authentication import TokenAuthentication
from rest_framework_extensions.cache.mixins import CacheResponseMixin
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle

from .serializers import GoodsSerializer, CategorySerializer, PriceRangeSerializer, BannerSerializer, HotSearchSerializer, IndexCategorySerializer
from .filters import GoodsFilter, PriceRangeFilter
from .models import Goods, GoodsCategory, PriceRange, Banner, HotSearchWords
from MxShop.settings import SECRET_KEY

# Create your views here.

# 方法一
# class GoodsListView(APIView):
#     """
#     List all snippets, or create a new snippet.
#     """
#     def get(self, request, format=None):
#         goods = Goods.objects.all()[:10]
#         goods_serializer = GoodsSerializer(goods, many=True)
#         return Response(goods_serializer.data)
#
#     def post(self, request):
#         serializer = GoodsSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)

# 方法二
# class GoodsListView(mixins.ListModelMixin,generics.GenericAPIView):
#     queryset = Goods.objects.all()
#     serializer_class = GoodsSerializer
#
#     def get(self, request, *args, **kwargs):
#         return self.list(request, *args, **kwargs)


# 方法三
# 分页
class GoodsPagination(PageNumberPagination):
    """
    商品分页参数设置
    """
    page_size = 12   # 默认每页数据个数
    page_size_query_param = 'page_size'
    page_query_param = 'page'  # URL中字段get/?page=xxx&page_size=12
    max_page_size = 100  # 每页请求最大数据个数


class GoodsListView(generics.ListAPIView):
    queryset = Goods.objects.all()
    serializer_class = GoodsSerializer
    pagination_class = GoodsPagination


# 设置缓存
# 注意CacheResponseMixin 要放到继承类的第一个
class GoodsListViewSet(CacheResponseMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    商品列表页, 分页，  ， 过滤， 排序
    """
    serializer_class = GoodsSerializer   # 商品序列化
    pagination_class = GoodsPagination   # 分页

    # 类属性过滤
    # queryset = Goods.objects.all()

    # 实例方法过滤
    # def get_queryset(self):
    #     queryset = Goods.objects.all()
    #     price_min = self.request.query_params.get('price_min', 0)
    #     if price_min:
    #         if price_min.isdigit() and int(price_min) > 0:
    #             queryset = queryset.filter(shop_price__gt=int(price_min))
    #     return queryset

    # django自带过滤器
    queryset = Goods.objects.all().order_by('-sold_num')
    # authentication_classes = (TokenAuthentication, )
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    # filter_fields = ('name', 'shop_price')   # 字段过滤
    search_fields = ('name', 'goods_brief', 'goods_desc')  # 字段搜索^ = @ $
    filterset_class = GoodsFilter  # 字段过滤
    ordering_fields = ('sold_num', 'shop_price', 'add_time')  # 排序
    throttle_classes = (UserRateThrottle, AnonRateThrottle)   # 访问限速

    def retrieve(self, request, *args, **kwargs):   # 重载RetrieveModelMixin中的retrieve方法
        instance = self.get_object()
        instance.click_num += 1
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class CategoryViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    list:
        商品分类列表数据
    """
    queryset = GoodsCategory.objects.filter(category_type=1)
    serializer_class = CategorySerializer


class PriceRangeViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    list:
        商品分类价格区间数据
    """
    queryset = PriceRange.objects.all()
    filter_backends = (DjangoFilterBackend,)
    serializer_class = PriceRangeSerializer
    filterset_class = PriceRangeFilter


class HotSearchViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    list:
        获取热搜词列表
    """
    queryset = HotSearchWords.objects.all().order_by('-index')
    serializer_class = HotSearchSerializer


class BannerViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    list:
        获取轮播图列表
    """
    queryset = Banner.objects.all().order_by('-index')
    serializer_class = BannerSerializer


class IndexCategoryViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    list:
        首页商品分类数据
    """
    queryset = GoodsCategory.objects.filter(is_tab=True, name__in=('生鲜食品', '酒水饮料'))
    serializer_class = IndexCategorySerializer


