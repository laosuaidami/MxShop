# -*- coding: utf-8 -*-

# pip install pycryptodome         # 安装加密需要的工具包
__author__ = 'bobby'

from datetime import datetime
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
from base64 import b64encode, b64decode
from urllib.parse import quote_plus
from urllib.parse import urlparse, parse_qs
from urllib.request import urlopen
from base64 import decodebytes, encodebytes
import json

from MxShop.settings import PRIVATE_KEY_PATH, ALI_PUB_KEY_PATH, ALI_APPID, APP_NOTIFY_URL, RETURN_URL, ALI_DEBUG


class AliPay(object):
    """
    支付宝支付接口
    """
    def __init__(self, appid, app_notify_url, app_private_key_path,
                 alipay_public_key_path, return_url, debug=False):
        self.appid = appid
        self.app_notify_url = app_notify_url
        self.app_private_key_path = app_private_key_path
        self.app_private_key = None
        self.return_url = return_url
        with open(self.app_private_key_path) as fp:
            self.app_private_key = RSA.importKey(fp.read())

        self.alipay_public_key_path = alipay_public_key_path
        with open(self.alipay_public_key_path) as fp:
            self.alipay_public_key = RSA.import_key(fp.read())


        if debug is True:
            self.__gateway = "https://openapi.alipaydev.com/gateway.do"
        else:
            self.__gateway = "https://openapi.alipay.com/gateway.do"

    def direct_pay(self, subject, out_trade_no, total_amount, return_url=None, **kwargs):
        """用户请求参数biz_content字段"""
        biz_content = {
            "subject": subject,
            "out_trade_no": out_trade_no,
            "total_amount": total_amount,
            "product_code": "FAST_INSTANT_TRADE_PAY",
            # "qr_pay_mode":4
        }

        biz_content.update(kwargs)
        data = self.build_body("alipay.trade.page.pay", biz_content, self.return_url)
        return self.sign_data(data)

    def build_body(self, method, biz_content, return_url=None):
        data = {
            "app_id": self.appid,
            "method": method,
            "charset": "utf-8",
            "sign_type": "RSA2",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "version": "1.0",
            "biz_content": biz_content
        }

        if return_url is not None:
            data["notify_url"] = self.app_notify_url
            data["return_url"] = self.return_url

        return data

    def sign_data(self, data):
        data.pop("sign", None)
        # 排序后的字符串
        unsigned_items = self.ordered_data(data)
        unsigned_string = "&".join("{0}={1}".format(k, v) for k, v in unsigned_items)
        sign = self.sign(unsigned_string.encode("utf-8"))
        quoted_string = "&".join("{0}={1}".format(k, quote_plus(v)) for k, v in unsigned_items)

        # 获得最终的订单信息字符串
        signed_string = quoted_string + "&sign=" + quote_plus(sign)
        return signed_string

    def ordered_data(self, data):
        complex_keys = []
        for key, value in data.items():
            if isinstance(value, dict):
                complex_keys.append(key)

        # 将字典类型的数据dump出来
        for key in complex_keys:
            data[key] = json.dumps(data[key], separators=(',', ':'))

        return sorted([(k, v) for k, v in data.items()])

    def sign(self, unsigned_string):
        # 开始计算签名
        key = self.app_private_key
        signer = PKCS1_v1_5.new(key)
        signature = signer.sign(SHA256.new(unsigned_string))
        # base64 编码，转换为unicode表示并移除回车
        sign = encodebytes(signature).decode("utf8").replace("\n", "")
        return sign

    def _verify(self, raw_content, signature):
        # 开始计算签名
        key = self.alipay_public_key
        signer = PKCS1_v1_5.new(key)
        digest = SHA256.new()
        digest.update(raw_content.encode("utf8"))
        if signer.verify(digest, decodebytes(signature.encode("utf8"))):
            return True
        return False

    def verify(self, data, signature):
        if "sign_type" in data:
            sign_type = data.pop("sign_type")
        # 排序后的字符串
        unsigned_items = self.ordered_data(data)
        message = "&".join(u"{}={}".format(k, v) for k, v in unsigned_items)
        return self._verify(message, signature)


def generate_payment_alipay_links(subject="测试订单",
                                  out_trade_no="201702021222",
                                total_amount=0.01):
    """
    生成支付宝请求连接
    :param subject: 订单标题
    :param out_trade_no: 商户订单号，64个字符以内、可包含字母、数字、下划线；需保证在商户端不重复
    :param total_amount: 订单总金额，单位为元，精确到小数点后两位，取值范围[0.01,100000000]
    :return:
    """
    # PRIVATE_KEY_PATH, ALI_PUB_KEY_PATH, ALI_APPID, APP_NOTIFY_URL, RETURN_URL, ALI_DEBUG
    alipay = AliPay(
        appid=ALI_APPID,
        app_notify_url=APP_NOTIFY_URL,  # 异步接口，当用户完成支付，会返回支付结果
        app_private_key_path=PRIVATE_KEY_PATH,
        alipay_public_key_path=ALI_PUB_KEY_PATH,  # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
        debug=ALI_DEBUG,  # 默认False,
        return_url=RETURN_URL  # 用户完成支付跳转的url
    )
    url = alipay.direct_pay(
        subject=subject,
        out_trade_no=out_trade_no,
        total_amount=total_amount
    )
    re_url = "https://openapi.alipaydev.com/gateway.do?{data}".format(data=url)
    return re_url


def alipay_verify_return_data(processed_dict):
    """
    验证return_url
    :param processed_dict: 需要验证的数据，支付宝返回的数据
    :return: 验证结果
    """
    sign = processed_dict.pop('sign', None)
    alipay = AliPay(
        appid=ALI_APPID,
        app_notify_url=APP_NOTIFY_URL,  # 异步接口，当用户完成支付，会返回支付结果
        app_private_key_path=PRIVATE_KEY_PATH,
        alipay_public_key_path=ALI_PUB_KEY_PATH,  # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
        debug=ALI_DEBUG,  # 默认False,
        return_url=RETURN_URL  # 用户完成支付跳转的url
    )
    return alipay.verify(processed_dict, sign)


if __name__ == "__main__":
    # 生成支付宝请求连接
    re_url = generate_payment_alipay_links(subject="测试订单",
                                           out_trade_no="2017020212223",
                                           total_amount=0.01)
    print(re_url)

    # 验证return_url
    return_url = 'http://www.dayushu.top:8000/alipay/return/?charset=utf-8&out_trade_no=201702021222&method=alipay.trade.page.pay.return&total_amount=0.01&sign=RT9NfqDiIhVTyCbNdVi5EsSdPYhezF2Md5o%2FdyjbMGNxH%2BbKR1ezRASKgFJ7UbvtH6YQj8t3XXvCGmsyvZsO%2BNrL%2Fygi2pTlgIjRta1yuoEZfFpt2oPWwCZhH%2BVToUjDaenJ%2Be1qQ47RJ4szkXQx1jnpb9qj%2Fqek8Bhca8ngWSGtImr4fMkzKd5jrKDNlSuo9LEdzxB5Bt2o3CzBrJBHDR4TbEV2iA1gXLKzBPt6tt94KEAhtP4rS44LWNbxXprxufjj0vdUbCoPCFGTdUaMA70CQFpoXt4O%2FksklcmfaucEm1dh4CDRcc9505MFLmVFn0Jyn2LEp4Hqmz5Zu3D5Sg%3D%3D&trade_no=2019012922001467530501052331&auth_app_id=2016092200571749&version=1.0&app_id=2016092200571749&sign_type=RSA2&seller_id=2088102176796300&timestamp=2019-01-29+16%3A46%3A30'
    o = urlparse(return_url)
    query = parse_qs(o.query)
    processed_query = {}
    for key, value in query.items():
        processed_query[key] = value[0]
    print(alipay_verify_return_data(processed_query))






    # return_url = 'http://www.dayushu.top:8000/alipay/return/?charset=utf-8&out_trade_no=201702021222&method=alipay.trade.page.pay.return&total_amount=0.01&sign=RT9NfqDiIhVTyCbNdVi5EsSdPYhezF2Md5o%2FdyjbMGNxH%2BbKR1ezRASKgFJ7UbvtH6YQj8t3XXvCGmsyvZsO%2BNrL%2Fygi2pTlgIjRta1yuoEZfFpt2oPWwCZhH%2BVToUjDaenJ%2Be1qQ47RJ4szkXQx1jnpb9qj%2Fqek8Bhca8ngWSGtImr4fMkzKd5jrKDNlSuo9LEdzxB5Bt2o3CzBrJBHDR4TbEV2iA1gXLKzBPt6tt94KEAhtP4rS44LWNbxXprxufjj0vdUbCoPCFGTdUaMA70CQFpoXt4O%2FksklcmfaucEm1dh4CDRcc9505MFLmVFn0Jyn2LEp4Hqmz5Zu3D5Sg%3D%3D&trade_no=2019012922001467530501052331&auth_app_id=2016092200571749&version=1.0&app_id=2016092200571749&sign_type=RSA2&seller_id=2088102176796300&timestamp=2019-01-29+16%3A46%3A30'

    # alipay = AliPay(
    #     appid="2016092200571749",
    #     app_notify_url="http://www.dayushu.top:8000/alipay/return/",   # 异步接口，当用户完成支付，会返回支付结果
    #     app_private_key_path="../trade/keys/private_2048.txt",
    #     alipay_public_key_path="../trade/keys/alipay_key_2048.txt",  # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
    #     debug=True,  # 默认False,
    #     return_url="http://www.dayushu.top:8000/alipay/return/"     # 用户完成支付跳转的url
    # )

    # 验证return_url
    # o = urlparse(return_url)
    # query = parse_qs(o.query)
    # processed_query = {}
    # ali_sign = query.pop("sign")[0]
    # for key, value in query.items():
    #     processed_query[key] = value[0]
    # print(alipay.verify(processed_query, ali_sign))

    # 生成支付宝请求连接
    # url = alipay.direct_pay(
    #     subject="测试订单",
    #     out_trade_no="201702021222",
    #     total_amount=0.01
    # )
    # re_url = "https://openapi.alipaydev.com/gateway.do?{data}".format(data=url)
    # print(re_url)
    # print('okkkk')




