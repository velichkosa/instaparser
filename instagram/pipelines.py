# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient


class InstagramPipeline:
    def __init__(self):
        self.MONGO_HOST = "localhost"
        self.MONGO_PORT = 27017
        self.MONGO_DB = 'Instagram'

    def process_item(self, item, spider):
        self.to_mongo(item, spider, self.MONGO_DB)
        return item

    def to_mongo(self, base, spider, MONGO_DB):
        with MongoClient(self.MONGO_HOST, self.MONGO_PORT) as client:
            db = client[MONGO_DB]
            users = db[spider.name]
            if base['friendship'] == 'followers':
                update_data = {
                    "$set": {
                        "user_id": base['user_id'],
                        "username": base['username'],
                        "full_name": base['full_name'],
                        "photo": base['photo'],
                        "post_data": base['post_data'],
                        "followers_to_user": base['master_id'],
                        "following_to_user": None
                    }
                }
                filter_data = {"user_id": base['user_id']}
                users.update_one(filter_data, update_data, upsert=True)
            elif base['friendship'] == 'following':
                update_data = {
                    "$set": {
                        "user_id": base['user_id'],
                        "username": base['username'],
                        "full_name": base['full_name'],
                        "photo": base['photo'],
                        "post_data": base['post_data'],
                        "followers_to_user": None,
                        "following_to_user": base['master_id']
                    }
                }
                filter_data = {"user_id": base['user_id']}
                users.update_one(filter_data, update_data, upsert=True)