__author__ = 'hewei'
__date__ = '18-12-10'
import re
import time
from datetime import datetime, timedelta

from django.utils.timezone import now
from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.validators import UniqueValidator

from MxShop.settings import MOBILE_REGEX
from .models import VerifyCode


User = get_user_model()


class SmsSerializer(serializers.Serializer):
    """
    由于用户只提交了mobile字段，不太符合model中的字段，所以使用普通的serializer进行序列化
    手机验证码验证
    """
    mobile = serializers.CharField(max_length=11, help_text='注册手机号码')

    def validate_mobile(self, mobile):  # 注意函数名字由validate和验证字段mobile拼接成的
        """
        验证手机号码
        :param mobile:
        :return:
        """
        # 手机是否注册
        if User.objects.filter(mobile=mobile).count():
            raise serializers.ValidationError('用户已经存在')

        # 验证手机号码是否合法
        if not re.match(MOBILE_REGEX, mobile):
            raise serializers.ValidationError('手机号码非法')

        # 验证手机号码发送频率
        one_minute_ago = datetime.now() - timedelta(hours=0, minutes=1, seconds=0)
        if VerifyCode.objects.filter(add_time__gt=one_minute_ago, mobile=mobile).count():
            raise serializers.ValidationError('距离上次发送未超过60秒')

        return mobile


class UserRegSerializer(serializers.ModelSerializer):
    """
    这个例子比较特殊应为使用了ModelSerializer,用户提交了多余code的字段，也就是该字段没有出现在Model中
    """
    # write_only=True 应为code不在Model中，所以code字段在返回序列化时回报错，所以要设置成，只写模式
    # 如果不想将某些字段序列化返回时，那就设置 write_only=True ，例如password
    code = serializers.CharField(required=True, write_only=True, max_length=4, min_length=4, help_text='验证码',
                                 label='验证码',
                                 error_messages={
                                     'required': "请输入验证码",
                                     'blank': '请输入验证码',
                                     'max_length': "请输入4位验证码",
                                     'min_length': "请输入4验证码",
                                 })
    username = serializers.CharField(required=True, allow_blank=False, label='注册手机号',
                                     validators=[UniqueValidator(queryset=User.objects.all(), message='用户已存在')])

    # style={'input_type': 'password'} password 输入显示小圆点，密文形式
    password = serializers.CharField(style={'input_type': 'password'}, label='密码', write_only=True)

    # 也可以使用signal来做（post_save)，详见
    # 设置密码为密文
    # def create(self, validated_data):
    #     user = super(UserRegSerializer, self).create(validated_data=validated_data)  # 调用父类create方法，返回User对象
    #     user.set_password(validated_data['password'])   # 调用User基类中set_password 方法将密码设置为密文
    #     user.save()
    #     return user

    def validate_code(self, code):
        """验证单个字段， 可以选择是否返回该字段,此处不需要返回，应为user数据表中没有这个字段"""
        # self.initial_data 字典中保存用户的post过来的数据,initial_data是调用serializer.is_valid(raise_exception=True)之前的原始数据
        verify_records = VerifyCode.objects.filter(mobile=self.initial_data['username']).order_by('-add_time')
        if verify_records:
            if now() - verify_records[0].add_time > timedelta(hours=0, minutes=1, seconds=0):
                raise serializers.ValidationError('验证码过期')
            if verify_records[0].code != code:
                raise serializers.ValidationError('验证码错误1')
        else:
            raise serializers.ValidationError('验证码错误2')
        # 此处不需要return code ， 应为user数据表中没有这个字段

    def validate(self, attrs):
        """
        1. 可以取到所有字段，验证所有字段， 并返回字段
        2. 可以按需添加和减少保存到model的字段
        3. 可以进行字段间的联合验证
        4. 验证顺序，先验证单独的后验证联合的
        """
        attrs['mobile'] = attrs['username']  # 增加 'mobile' 字段  可以保存到数据库
        del attrs['code']                   # 删除 'code' 字段
        # self.fields.pop('code')
        return attrs

    class Meta:
        model = User
        fields = ('username', 'code', 'password')


class UserDetailSerializer(serializers.ModelSerializer):
    """
    用户详情序列化类
    """

    class Meta:
        model = User
        fields = ('name', 'gender', 'birthday', 'email', 'mobile')




