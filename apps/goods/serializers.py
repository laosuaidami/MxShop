__author__ = 'hewei'
__date__ = '18-12-8'
from rest_framework import serializers
from django.db.models import Q

from goods.models import Goods, GoodsCategory, PriceRange, GoodsImage, Banner, HotSearchWords, GoodsCategoryBrand, IndexAd


# class GoodsSerializer(serializers.Serializer):
#     name = serializers.CharField(required=True, max_length=100)
#     click_num = serializers.IntegerField(default=0)
#     goods_front_image = serializers.ImageField()
#
#     def create(self, validated_data):
#         """
#         Create and return a new `Snippet` instance, given the validated data.
#         """
#         return Goods.objects.create(**validated_data)


class CategorySerializer3(serializers.ModelSerializer):

    class Meta:
        model = GoodsCategory
        # fields = ('name', 'click_num', 'market_price', 'add_time')
        fields = '__all__'
        # fields = ('name',)


class CategorySerializer2(serializers.ModelSerializer):
    sub_cat = CategorySerializer3(many=True)

    class Meta:
        model = GoodsCategory
        # fields = ('name', 'click_num', 'market_price', 'add_time')
        fields = '__all__'
        # fields = ('name',)


class CategorySerializer(serializers.ModelSerializer):
    sub_cat = CategorySerializer2(many=True)

    class Meta:
        model = GoodsCategory
        # fields = ('name', 'click_num', 'market_price', 'add_time')
        fields = '__all__'
        # fields = ('name',)


class GoodsImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = GoodsImage
        fields = ('image', )


class GoodsSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    images = GoodsImageSerializer(many=True)

    class Meta:
        model = Goods
        # fields = ('name', 'click_num', 'market_price', 'add_time')
        fields = '__all__'


class PriceRangeSerializer(serializers.ModelSerializer):

    class Meta:
        model = PriceRange
        fields = ('min', 'max')


class HotSearchSerializer(serializers.ModelSerializer):

    class Meta:
        model = HotSearchWords
        fields = '__all__'


class BannerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Banner
        fields = '__all__'


class CategoryBrandSerializer(serializers.ModelSerializer):

    class Meta:
        model = GoodsCategoryBrand
        fields = '__all__'


class IndexCategorySerializer(serializers.ModelSerializer):
    brands = CategoryBrandSerializer(many=True)
    goods = serializers.SerializerMethodField(read_only=True)   # 自定义添加字段
    ad_goods = serializers.SerializerMethodField(read_only=True)  # 自定义添加字段
    sub_cat = CategorySerializer2(many=True)

    # 方法的名字很重要， 一定要在字段goods的前面加get_
    def get_goods(self, obj):  # obj 就是serializers的对象
        all_goods = Goods.objects.filter(Q(category_id=obj.id) | Q(category__parent_category_id=obj.id) | Q(category__parent_category__parent_category_id=obj.id))
        # context={'request': self.context['request']} 这个 上下文很重要，如果自己在serializers中进行serializer没有设置上下文，图片连接中不会自动加域名的
        goods_serializer = GoodsSerializer(all_goods, many=True, context={'request': self.context['request']})
        return goods_serializer.data

    def get_ad_goods(self, obj):  # obj 就是serializers的对象
        goods_json = {}
        ad_goods = IndexAd.objects.filter(category_id=obj.id)
        if ad_goods:
            goods_ins = ad_goods[0].goods
            # 设置上下文 图片会添加域名路径
            goods_json = GoodsSerializer(goods_ins, many=False, context={'request': self.context['request']}).data
        return goods_json

    class Meta:
        model = GoodsCategory
        fields = '__all__'









