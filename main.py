import datetime
import sys
import argparse

import requests


from elasticsearch import Elasticsearch

class Stats():
    def __init__(self):
        #self.outfit_id = '37509507321455149'
        self.api_url   = 'http://census.daybreakgames.com/get/ps2:v2/outfit_member/?outfit_id=%s&c:limit=999999&c:resolve=online_status'
        self.es        = Elasticsearch()


    def get_online_members(self, outfit_id):
        online_members = 0
        # Returns local time zone
        now            = datetime.datetime.utcnow()

        r = requests.get(self.api_url % (outfit_id))

        if r.status_code != 200:
            sys.exit(r.status_code)

        data          = r.json()
        member_list   = data['outfit_member_list']
        total_members = data['returned']

        for member in member_list:
            if member['online_status'] != "0":
                online_members += 1

        print('total: %s -- online: %s' % (total_members, online_members))
            #print(member)
        
        body = {'online_members':online_members,'total_members':total_members,'outfit_id':outfit_id,'timestamp':now}
        result = self.es.index(index='planetside_2', doc_type='online_members', body=body)


if __name__ == '__main__':
    stats = Stats()
    
    parser = argparse.ArgumentParser(description='send Planetside 2 stats to elasticsearch')
    parser.add_argument('--online-members', action='store')


    args = parser.parse_args()

    if args.online_members:
        stats.get_online_members(args.online_members)

