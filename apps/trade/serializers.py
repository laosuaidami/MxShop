__author__ = 'hewei'
__date__ = '18-12-14'
import time
from random import Random

from rest_framework import serializers

from goods.models import Goods
from .models import ShoppingCart, OrderInfo, OrderGoods
from goods.serializers import GoodsSerializer
from utils.alipay import generate_payment_alipay_links


class ShopCartDetailSerializer(serializers.ModelSerializer):
    goods = GoodsSerializer(many=False, )

    class Meta:
        model = ShoppingCart
        fields = '__all__'


class ShopCartSerializer(serializers.Serializer):
    """购物车序列化"""
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    nums = serializers.IntegerField(required=True, min_value=1, label='数量',
                                    error_messages={
                                        'min_value': '商品数量不能小于1',
                                        'required': '请选择购买数量'
                                    })
    goods = serializers.PrimaryKeyRelatedField(required=True, label='商品', queryset=Goods.objects.all())

    def create(self, validated_data):                  # serializers 中的重要知识点
        user = self.context['request'].user    # serializers 需要这样取数据request
        nums = validated_data['nums']
        goods = validated_data['goods']
        existed = ShoppingCart.objects.filter(user=user, goods=goods)
        if existed:
            existed = existed[0]
            existed.nums += nums
            existed.save()
        else:
            existed = ShoppingCart.objects.create(**validated_data)
        return existed                               # 必须返回，用于前段返回数据的序列化

    def update(self, instance, validated_data):        # serializers.Serializer 使用put方法时，中必须实现这个方法，不然报错，具体可参考其继承类
        # 修改商品数量
        instance.nums = validated_data['nums']
        instance.save()
        return instance


class OrderSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )

    pay_status = serializers.CharField(read_only=True)
    trade_no = serializers.CharField(read_only=True)
    order_sn = serializers.CharField(read_only=True)
    pay_time = serializers.DateTimeField(read_only=True)
    add_time = serializers.DateTimeField(read_only=True)
    alipay_url = serializers.SerializerMethodField(read_only=True)

    # 方法的名字很重要， 一定要在字段alipay_url的前面加get_
    def get_alipay_url(self, obj):
        re_url = generate_payment_alipay_links(subject=obj.order_sn,
                                               out_trade_no=obj.order_sn,
                                               total_amount=obj.order_mount)
        return re_url

    def generate_order_sn(self):
        # 当前时间 + userid + 随机数
        random_ins = Random()
        order_sn = "{time_str}{userid}{ranstr}".format(time_str=time.strftime("%Y%m%d%H%M%S"),
                                                       userid=self.context['request'].user.id,
                                                       ranstr=random_ins.randrange(10, 99))
        return order_sn

    def validate(self, attrs):
        attrs['order_sn'] = self.generate_order_sn()
        return attrs

    class Meta:
        model = OrderInfo
        fields = '__all__'


class OrderGoodsSerializer(serializers.ModelSerializer):
    goods = GoodsSerializer(many=False)

    class Meta:
        model = OrderGoods
        fields = '__all__'


class OrderDetailSerializer(serializers.ModelSerializer):
    goods = OrderGoodsSerializer(many=True)
    alipay_url = serializers.SerializerMethodField(read_only=True)

    # 方法的名字很重要， 一定要在字段alipay_url的前面加get_
    def get_alipay_url(self, obj):  # obj 就是serializers对象
        re_url = generate_payment_alipay_links(subject=obj.order_sn,
                                               out_trade_no=obj.order_sn,
                                               total_amount=obj.order_mount)
        return re_url

    class Meta:
        model = OrderInfo
        fields = '__all__'











