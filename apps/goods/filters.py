__author__ = 'hewei'
__date__ = '18-12-8'
from django_filters import rest_framework as filters
from django.db.models import Q

from .models import Goods, PriceRange


class GoodsFilter(filters.FilterSet):
    """
    商品的过滤类
    """
    pricemin = filters.NumberFilter(field_name="shop_price", lookup_expr='gte', help_text='最低价格')
    pricemax = filters.NumberFilter(field_name="shop_price", lookup_expr='lte', help_text='最高价格')
    name = filters.CharFilter(field_name='name', lookup_expr='icontains', help_text='包含字段')
    top_category = filters.NumberFilter(method='get_category_all', help_text='顶类名')

    def get_category_all(self, queryset, name, value):
        return queryset.filter(Q(category_id=value) | Q(category__parent_category_id=value) | Q(category__parent_category__parent_category_id=value))

    class Meta:
        model = Goods
        # fields = ['min_price', 'max_price', 'name']
        fields = ['pricemin', 'pricemax', 'is_hot', 'is_new']


class PriceRangeFilter(filters.FilterSet):
    """
    默认价格区间过滤类
    """
    proType = filters.CharFilter(field_name="category")

    class Meta:
        model = PriceRange
        fields = ['proType', ]






















