__date__ = '18-12-8'
__author__ = 'hewei'
from rest_framework.views import APIView
from django.views.generic.base import View
from goods.models import Goods
from django.forms.models import model_to_dict
from django.core import serializers
from django.http import HttpResponse, JsonResponse
import json
from .tasks import CourseTask

class GoodsListView(View):
    def get(self, request):
        """
        通过django的view实现商品列表页
        :param request:
        :return:
        """
        json_list = []
        goods = Goods.objects.all()[:10]
        # 方法一  不能对add_time 和 images 进行序列化
        # for good in goods:
        #     json_dict = {}
        #     json_dict['name'] = good.name
        #     json_dict['category'] = good.category.name
        #     json_list.append(json_dict)

        # 方法二  不能对add_time 和 images 进行序列化
        # for good in goods:
        #     json_dict = model_to_dict(good)
        #     json_list.append(json_dict)

        # return HttpResponse(json.dumps(json_list), content_type='application/json')

        # 方法三 可以对add_time 和 images 进行序列化
        # json_data = serializers.serialize('json', goods)
        # return HttpResponse(json_data, content_type='application/json')

        # 方法四  可以对add_time 和 images 进行序列化
        json_data = serializers.serialize('json', goods)
        data = json.loads(json_data)
        return JsonResponse(data, safe=False)


class DoTaskView(View):
    """
    执行异步任务
    """
    def get(self, request):
        # 执行异步任务
        print('start do request')
        # CourseTask.delay()     # 这种方式也可以，但是不方便修改队列
        CourseTask.apply_async(args=('hello', ), queue='work_queue', kwargs={'key':10, })  # 方便传参数， 改变队列
        print('end do request')
        return JsonResponse({'result': 'ok'})



