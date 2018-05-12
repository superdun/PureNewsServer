# -*- coding:utf-8 -*-
import requests
import json
from wechatpy.exceptions import WeChatOAuthException

class WechatAuth(object):
    """微信公众平台 OAuth 网页授权 """

    API_BASE_URL = 'https://api.weixin.qq.com/'
    OAUTH_BASE_URL = 'https://open.weixin.qq.com/connect/'

    def __init__(self, app_id, secret):
        """

        :param app_id: 微信公众号 app_id
        :param secret: 微信公众号 secret

        """
        self.app_id = app_id
        self.secret = secret
        self._http = requests.Session()

    def _request(self, method, url_or_endpoint, **kwargs):
        if not url_or_endpoint.startswith(('http://', 'https://')):
            url = '{base}{endpoint}'.format(
                base=self.API_BASE_URL,
                endpoint=url_or_endpoint
            )
        else:
            url = url_or_endpoint

        if isinstance(kwargs.get('data', ''), dict):
            body = json.dumps(kwargs['data'], ensure_ascii=False)
            body = body.encode('utf-8')
            kwargs['data'] = body

        res = self._http.request(
            method=method,
            url=url,
            **kwargs
        )
        try:
            res.raise_for_status()
        except requests.RequestException as reqe:
            raise WeChatOAuthException(
                errcode=None,
                errmsg=None,
                client=self,
                request=reqe.request,
                response=reqe.response
            )
        result = json.loads(res.content.decode('utf-8', 'ignore'), strict=False)

        if 'errcode' in result and result['errcode'] != 0:
            errcode = result['errcode']
            errmsg = result['errmsg']
            raise WeChatOAuthException(
                errcode,
                errmsg,
                client=self,
                request=res.request,
                response=res
            )

        return result

    def _get(self, url, **kwargs):
        return self._request(
            method='get',
            url_or_endpoint=url,
            **kwargs
        )

    def fetch_session_key(self, code):
        """获取 session_key

        :param code: 授权完成跳转回来后 URL 中的 code 参数
        :return: JSON 数据包
        """
        res = self._get(
            'sns/jscode2session',
            params={
                'appid': self.app_id,
                'secret': self.secret,
                'js_code': code,
                'grant_type': 'authorization_code'
            }
        )
        self.open_id = res.get('openid')
        self.session_key = res.get('session_key')
        self.union_id = res.get('unionid')
        return res