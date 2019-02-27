from random import choice

from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from rest_framework import viewsets, mixins
from rest_framework.response import Response
from rest_framework import status
from rest_framework_jwt.serializers import jwt_encode_handler, jwt_payload_handler
from rest_framework.permissions import IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.authentication import SessionAuthentication

from .serializers import SmsSerializer, UserRegSerializer, UserDetailSerializer
from utils.yunpian import YunPian
from MxShop.settings import APIKEY
from .models import VerifyCode
from .tasks import SendSmsTask
# Create your views here.
User = get_user_model()


class CustomBackend(ModelBackend):
    """
    用户登录密码验证
    通过配置setting AUTHENTICATION_BACKENDS 变量
    自定义用户验证
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = User.objects.get(Q(username=username) | Q(mobile=username))
            if user.check_password(password):
                return user
        except Exception as e:
            return None


class SmsCodeViewset(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    发送短信验证码
    """
    serializer_class = SmsSerializer

    def generate_code(self):
        """
        生成四位数字的验证码
        :return:
        """
        seeds = "1234567890"
        random_str = []
        for i in range(4):
            random_str.append(choice(seeds))

        return "".join(random_str)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)   # 设置raise_exception=True,如果验证失败drf将会返回400错误

        mobile = serializer.validated_data["mobile"]

        code = self.generate_code()
        SendSmsTask.apply_async(queue='work_queue', kwargs={'code': code, 'mobile': mobile})  # 方便传参数， 改变队列
        yun_pian = YunPian(APIKEY)
        sms_status = yun_pian.send_sms(code=code, mobile=mobile)

        if sms_status["code"] != 0:
            return Response({
                "mobile": sms_status["msg"]
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            code_record = VerifyCode(code=code, mobile=mobile)
            code_record.save()
            return Response({
                "mobile": mobile
            }, status=status.HTTP_201_CREATED)
        # return Response({
        #     "mobile": mobile
        # }, status=status.HTTP_201_CREATED)


class UserRegViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    用户注册
    """
    serializer_class = UserRegSerializer
    queryset = User.objects.all()

    # 如果注册之后需要用户登录再登录，则以下代码没有必要了，但是如要用户注册完成后直接登录，则需要重写mixins中的create方法，给前端返回JWT
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)
        re_dict = serializer.data
        payload = jwt_payload_handler(user)
        re_dict['token'] = jwt_encode_handler(payload)
        re_dict['name'] = user.name if user.name else user.username

        headers = self.get_success_headers(serializer.data)
        return Response(re_dict, status=status.HTTP_201_CREATED, headers=headers)

    # 重载perform_create，返回user对象
    def perform_create(self, serializer):
        return serializer.save()


# 方法二动态设置用户信息的访问 UpdateModelMixin 需要使用put patch 方法请求
class UserViewSet(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    """
        retrieve:
        获取用户信息.

        update:
        修改用户信息.

        partial_update:
        修改用户信息.

    """
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)

    # 只能获取当前用户的信息
    # queryset = User.objects.all()  # 这个是可以获取所有用户的信息
    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)

    def get_object(self):
        return self.request.user

    # 动态设置 permission_classes
    # permission_classes = (IsAuthenticated, )
    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        # action = ['retrieve', 'list', 'create', 'update', 'partial_update', 'destroy']
        if self.action == 'retrieve':      # 请注意只有继承GenericViewSet才可以使用self.action,具体实现可查看源码
            return [IsAuthenticated()]
        elif self.action == 'create':
            return []
        return []

    # 动态设置 serializer_class
    # serializer_class = UserDetailSerializer
    def get_serializer_class(self):
        """
        Return the class to use for the serializer.
        Defaults to using `self.serializer_class`.

        You may want to override this if you need to provide different
        serializations depending on the incoming request.

        (Eg. admins get full serialization, others get basic serialization)
        """
        assert self.serializer_class is None, (
            "'%s' should either include a `serializer_class` attribute, "
            "or override the `get_serializer_class()` method."
            % self.__class__.__name__
        )

        if self.action == 'retrieve':
            return UserDetailSerializer
        elif self.action == 'create':
            return UserRegSerializer
        return UserDetailSerializer







