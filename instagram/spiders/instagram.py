import scrapy
import re
from scrapy.http import HtmlResponse
import json

from copy import deepcopy
from instagram.items import InstagramItem
from pprint import pprint


class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['instagram.com']
    start_urls = ['https://www.instagram.com/']
    inst_login_url = 'https://www.instagram.com/accounts/login/ajax/'
    inst_login = 'dosya.tos_offi'
    inst_pswd = '#PWD_INSTAGRAM_BROWSER:10:1632801678:AdtQAIAhzFNGIwE61iVaW+x1E5k8bVSBYHCbC5LGy2vWQdRN2NQWOn3bK3Q5Dnn4SEsW643+FBcGZH/tLiFy7tKNSztf5n+nth1EK0ywO1smjOQSDI/DGAbPkDOva98FC4g5W/2dFy1aVw=='
    parse_user = ['olgamihailina23', 'pyshokandarch']

    def parse(self, response: HtmlResponse):
        csrf = self.fetch_csrf_token(response.text)
        yield scrapy.FormRequest(
            self.inst_login_url,
            method='POST',
            callback=self.login,
            formdata={'username': self.inst_login,
                      'enc_password': self.inst_pswd},
            headers={'x-csrftoken': csrf}
        )

    def login(self, response: HtmlResponse):

        j_data = response.json()
        if j_data['authenticated']:
            for user in self.parse_user:
                yield response.follow(
                    f'/{user}',
                    callback=self.parse_user_data,
                    cb_kwargs={'username': user}
                )

    def parse_user_data(self, response: HtmlResponse, username):
        user_id = self.fetch_user_id(response.text, username)
        variables = {'count': 12,
                     'search_surface': 'follow_list_page'
                     }
        yield response.follow(f'https://i.instagram.com/api/v1/friendships/{user_id}/followers/?count={variables["count"]}&search_surface={variables["search_surface"]}',
                              callback=self.parse_followers,
                              headers={'User-Agent': 'Instagram 155.0.0.37.107'},
                              cb_kwargs={'username': username,
                                         'user_id': user_id,
                                         'variables': deepcopy(variables),
                                         })
        yield response.follow(f'https://i.instagram.com/api/v1/friendships/{user_id}/followers/?count={variables["count"]}&search_surface={variables["search_surface"]}',
                              callback=self.parse_following,
                              headers={'User-Agent': 'Instagram 155.0.0.37.107'},
                              cb_kwargs={'username': username,
                                         'user_id': user_id,
                                         'variables': deepcopy(variables),
                                         })

    def parse_followers(self, response: HtmlResponse, username, user_id, variables):
        res = json.loads(response.text.replace('("', '').replace(')"', ''))
        db_users = res['users']
        for post in db_users:
            item = InstagramItem(
                username=post['username'],
                full_name=post['full_name'],
                user_id=post['pk'],
                photo=post['profile_pic_url'],
                master_id=user_id,
                friendship='followers',
                post_data=post
            )
            yield item
        yield response.follow(
            f'https://i.instagram.com/api/v1/friendships/{user_id}/followers/?count={variables["count"]}&max_id={variables["count"]}&search_surface={variables["search_surface"]}',
            callback=self.user_posts_parse_followers,
            headers={'User-Agent': 'Instagram 155.0.0.37.107'},
            cb_kwargs={'username': username,
                       'user_id': user_id,
                       'variables': deepcopy(variables),
                       'db_users': db_users
                       })

    def parse_following(self, response: HtmlResponse, username, user_id, variables):
        res = json.loads(response.text.replace('("', '').replace(')"', ''))
        db_users = res['users']
        for post in db_users:
            item = InstagramItem(
                username=post['username'],
                full_name=post['full_name'],
                user_id=post['pk'],
                photo=post['profile_pic_url'],
                master_id=user_id,
                friendship='following',
                post_data=post
            )
            yield item
        yield response.follow(
            f'https://i.instagram.com/api/v1/friendships/{user_id}/followers/?count={variables["count"]}&max_id={variables["count"]}',
            callback=self.user_posts_parse_following,
            headers={'User-Agent': 'Instagram 155.0.0.37.107'},
            cb_kwargs={'username': username,
                       'user_id': user_id,
                       'variables': deepcopy(variables),
                       'db_users': db_users
                       })

    def user_posts_parse_followers(self, response: HtmlResponse, username, user_id, variables, db_users):
        j_data = response.json()
        if j_data.get('next_max_id'):
            variables['next_max_id'] = j_data.get('next_max_id')
            variables['big_list'] = j_data.get('big_list')
        else:
            variables['next_max_id'] = 12
        url_posts = f'https://i.instagram.com/api/v1/friendships/{user_id}/followers/?count={variables["count"]}&max_id={variables["next_max_id"]}&search_surface={variables["search_surface"]}'
        yield response.follow(url_posts,
                              callback=self.user_posts_parse_followers,
                              headers={'User-Agent': 'Instagram 155.0.0.37.107'},
                              cb_kwargs={'username': username,
                                         'user_id': user_id,
                                         'variables': deepcopy(variables),
                                         'db_users': db_users
                                         }
                              )
        for post in response.json()['users']:
            item = InstagramItem(
                username=post['username'],
                full_name=post['full_name'],
                user_id=post['pk'],
                photo=post['profile_pic_url'],
                master_id=user_id,
                friendship='followers',
                post_data=post
            )
            yield item

    def user_posts_parse_following(self, response: HtmlResponse, username, user_id, variables, db_users):
        j_data = response.json()
        if j_data.get('next_max_id'):
            variables['next_max_id'] = j_data.get('next_max_id')
            variables['big_list'] = j_data.get('big_list')
        else:
            variables['next_max_id'] = 12
        url_posts = f'https://i.instagram.com/api/v1/friendships/{user_id}/followers/?count={variables["count"]}&max_id={variables["next_max_id"]}'
        yield response.follow(url_posts,
                              callback=self.user_posts_parse_following,
                              headers={'User-Agent': 'Instagram 155.0.0.37.107'},
                              cb_kwargs={'username': username,
                                         'user_id': user_id,
                                         'variables': deepcopy(variables),
                                         'db_users': db_users
                                         }
                              )
        for post in response.json()['users']:
            item = InstagramItem(
                username=post['username'],
                full_name=post['full_name'],
                user_id=post['pk'],
                photo=post['profile_pic_url'],
                master_id=user_id,
                friendship='following',
                post_data=post
            )
            yield item

    def fetch_csrf_token(self, text):
        # Получаем токен для авторизации
        matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
        return matched.split(':').pop().replace(r'"', '')

    def fetch_user_id(self, text, username):
        # Получаем id желаемого пользователя
        matched = re.search(
            '{\"id\":\"\\d+\",\"username\":\"%s\"}' % username, text
        ).group()
        return json.loads(matched).get('id')