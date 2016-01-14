import datetime
import sys
import argparse

import requests

from influxdb import InfluxDBClient

class Stats():
    def __init__(self, ip, port):
        #self.outfit_id = '37509507321455149'
        self.api_url   = 'http://census.daybreakgames.com/get/ps2:v2/outfit_member/?outfit_id=%s&c:limit=999999&c:resolve=online_status'

        self.client = InfluxDBClient(ip, port, 'root', 'root', 'planetside_2')


    def get_online_members(self, outfit_id):
        online_members = 0
        total_members  = 0

        # Returns local time zone
        now            = datetime.datetime.utcnow()

        r = requests.get(self.api_url % (outfit_id))

        if r.status_code != 200:
            sys.exit(r.status_code)

        data          = r.json()
        member_list   = data['outfit_member_list']
        total_members = data['returned']

        for member in member_list:
            if member['online_status'] == "17":
                online_members += 1

        print('total: %s -- online: %s' % (total_members, online_members))
        
        body = [
                {
                    'measurement':'online_members',
                    'tags':
                    {
                        'outfit_id':outfit_id,
                    },
                    'time':now,
                    'fields':
                    {
                        'total_members':total_members,
                        'online_members':online_members,
                    }
                }
               ]

        self.client.write_points(body)


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description='send Planetside 2 stats to elasticsearch')
    parser.add_argument('--online-members', action='store')
    parser.add_argument('--db-ip',          action='store', default='localhost')
    parser.add_argument('--db-port',        action='store', default=8086, type=int)

    
    args = parser.parse_args()
    stats = Stats(args.db_ip, args.db_port)


    if args.online_members:
        stats.get_online_members(args.online_members)

