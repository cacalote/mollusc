import json
import pymongo
from bson.objectid import ObjectId
from bson.son import SON
from common import parse_config

config = parse_config()

class Database():

    def __init__(self):
        try:
            # Create the connection
            if config['valid']:
                mongo_uri = config['database']['mongo_uri']
            else:
                mongo_uri = 'mongodb://localhost'

            connection = pymongo.MongoClient(mongo_uri)

            # Version Check
            server_version = connection.server_info()['version']
            if int(server_version[0]) < 3:
                raise UserWarning(
                    'Incompatible MongoDB Version detected. Requires 3 or higher. Found {0}'.format(server_version))

            # Connect to Databases.
            moldb = connection[config['database']['dbname']]

            # Get Collections
            self.col_sensors = moldb['sensors']
            self.col_sessions = moldb['sessions']
            self.col_auth = moldb['auth']
            self.col_input = moldb['input']
            self.col_downloads = moldb['downloads']
            self.col_clients = moldb['clients']
            self.col_ttylog = moldb['ttylog']
            self.col_keyfingerprints = moldb['keyfingerprints']
            self.col_event = moldb['event']
        except Exception as e:
            print 'Error', e

    def get_allsessions(self, start=0, length=25, search_term=None, col_name='starttime', order=1):
        if search_term and col_name:
            cursor = self.col_sessions.find({col_name: {"$regex": u"{}".format(search_term)}})
        else:
            cursor = self.col_sessions.find()

        if order == 1:
            cursor.sort(col_name, pymongo.ASCENDING)
        else:
            cursor.sort(col_name, pymongo.DESCENDING)
        sessions = cursor.skip(start).limit(length)

        return [s for s in sessions]

    def get_session(self, search):
        cursor = self.col_sessions.find_one(search)
        return cursor

    def count_sessions(self):
        count = self.col_sessions.find().count()
        return count

    def find_auth(self, search):
        cursor = self.col_auth.find(search)
        return [x for x in cursor]

    def get_input(self, search):
        cursor = self.col_input.find(search)
        return [x for x in cursor]

    def get_downloads(self, search):
        cursor = self.col_downloads.find(search)
        return [x for x in cursor]

    def get_ttylog(self, search):
        cursor = self.col_ttylog.find_one(search)
        return cursor

    def get_sensors(self):
        sensors = self.col_sensors.find()
        return [x for x in sensors]

    def get_users(self):
        users = self.col_auth.find({}, {'username': 1, 'password': 1})
        return [x for x in users]

    def get_passwords(self):
        pipeline = [
            {"$unwind": "$password"},
            {"$group": {"_id": "$password", "count": {"$sum": 1}}},
            {"$sort": SON([("count", -1), ("_id", -1)])}
            ]
        this = list(self.col_auth.aggregate(pipeline))
        return this

    def get_usernames(self):
        pipeline = [
            {"$unwind": "$username"},
            {"$group": {"_id": "$username", "count": {"$sum": 1}}},
            {"$sort": SON([("count", -1), ("_id", -1)])}
            ]
        this = list(self.col_auth.aggregate(pipeline))
        return this

    def get_commands(self):
        pipeline = [
            {"$unwind": "$input"},
            {"$group": {"_id": "$input", "count": {"$sum": 1}}},
            {"$sort": SON([("count", -1), ("_id", -1)])}
            ]
        this = list(self.col_input.aggregate(pipeline))
        return this

    def get_downloads(self):
        pipeline = [
            {"$unwind": "$url"},
            {"$group": {"_id": "$url", "count": {"$sum": 1}}},
            {"$sort": SON([("count", -1), ("_id", -1)])}
            ]
        this = list(self.col_downloads.aggregate(pipeline))
        return this

    def all_passwords(self):
        passwords = self.col_auth.find({}, {'password': 1})
        return [x for x in passwords]

    def get_iplist(self):
        iplist = self.col_sessions.find({}, {'src_ip': 1})
        return [x for x in iplist]
