import time
import logging
import json
import requests
import csv
import pandas as pd

class CloudinaryChecker(object):
    def __init__(self, url, api_key, api_secret, domain, notifiers = {}):
        self.url = url
        self.api_key = api_key
        self.api_secret = api_secret
        self.domain = domain
        self.notifiers = notifiers
        self.messages = []

    def get_folders(self):
        url = "https://"+self.url+"/"+self.domain+"/folders"
        response = requests.get(url, auth=(self.api_key, self.api_secret))
        response = json.loads(response.text)
        self.folders = [folder['name'] for folder in response['folders']]    
        return self.folders

    def create_access_report( self, from_date, to_date, resource_type, exclude_folders, sort_by ):
        url = "https://"+self.url+"/"+self.domain+"/resources_last_access_reports"
        headers = {
            "Content-Type":"application/json"
        }
        payload = {
            "to_date": to_date,
            "exclude_folders": exclude_folders,
            "sort_by": sort_by
        }
        if(from_date!=None):
            payload["from_date"]=from_date
        if(resource_type!="all"):
            payload["resource_type"]=resource_type
            
        print(json.dumps(payload,indent = 4))

        response = requests.post( url, auth =(self.api_key, self.api_secret), headers = headers, data = json.dumps(payload,indent = 4) )
        print(response.text)
        response=json.loads(response.text)
        report_id = response["id"]
        logging.info('Report Requested with Id: ' + report_id)
        return report_id

    def check_report_status(self, report_id, sleep_seconds, counter=0):
        url = "https://"+self.url+"/"+self.domain+"/resources_last_access_reports"+"/"+report_id
        response = requests.request("GET", url, auth=(self.api_key, self.api_secret))
        response=json.loads(response.text)
        if(response['status']=='done'):
            return True
        time.sleep(sleep_seconds)
        return self.check_report_status(report_id, sleep_seconds, counter+1)

    def get_report_data(self, report_id, next_cursor=None):
        total_resources = []
        next_cursor = None
        max_results = 500
        f=open(report_id+".csv", 'a')
        writer = csv.writer(f)
        writer.writerow(["id","name","url","type","access_mode","last_access_time"])

        while True:   
            url = "https://"+self.url+"/"+self.domain+"/resources/last_access_report"+"/"+report_id
            params = { "max_results": max_results }
            if next_cursor:
                params["next_cursor"] =  next_cursor
            
            response = requests.request("GET", url, params=params, auth=(self.api_key, self.api_secret))
            response = json.loads(response.text)
            resources = response["resources"]
            if("next_cursor" in response):
                next_cursor = response["next_cursor"]
                print(next_cursor)
            total_resources.extend(resources)
            asset_ids = [[resource["asset_id"],resource["public_id"],resource["url"],resource["type"],resource["access_mode"],resource["last_access"]] for resource in resources]
            for row in asset_ids:
                writer.writerow(row)
            if len(resources) < max_results:
                break
        f.close()
        return total_resources

    
    def fetch_access_report(self, report_id, sleep_seconds, counter=0):        
        if (self.check_report_status(report_id, sleep_seconds)):
            logging.info('Report Generated Successfully for : ' + report_id + "after "+  str(sleep_seconds*counter) + "seconds")
        resources = self.get_report_data(report_id)
        return resources

    def delete_resources( self, report_id ):
        nrows=0
        chunks=pd.read_csv(report_id,chunksize=100)
        for chunk in chunks:
            data = {'public_ids[]' : list(chunk["name"])}
            url = "https://"+self.url+"/"+self.domain+"/resources/image/upload"
            response = requests.delete( url, auth =(self.api_key, self.api_secret), data = data )
            response=json.loads(response.text)
            logging.info(response)  
        logging.info('Requested Resources Deleted for: ' + report_id)
        return True