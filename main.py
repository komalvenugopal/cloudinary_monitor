#!/usr/bin/env python
import yaml
import logging
import datetime
import os
from checkers.last_accessed import CloudinaryChecker
from notifiers.notify import Notifier
# import requests,json

if __name__ == '__main__':
    directory = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    config = yaml.load(open(os.path.join(directory, 'config.yml'), 'r').read(),Loader=yaml.Loader)

    logging.basicConfig(filename=os.path.join(directory, 'cloudinary.log'),level=logging.DEBUG)

    for domain in config['cloudinary']['domain']:
        checker = CloudinaryChecker(
            url=config['cloudinary']['url'],
            api_key=config['cloudinary']['api_key'],
            api_secret=config['cloudinary']['api_secret'],
            domain=domain,
            notifiers=config['notifiers']
        )
        logging.info(domain + 'Checker started at: ' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

        '''
        report_id="e2552f6074a4958cca8aacb8b4ef079ab7196a88a9824158edad63c74886b916"
        folders = checker.get_folders()
        resource_type=["videos"]
        '''

        ''' GENERATE '''
        folders=[]
        report_id = checker.create_access_report( from_date=None, to_date="2022-04-30", resource_type="all", exclude_folders=folders, sort_by="accessed_at" )
        resources = checker.fetch_access_report(report_id, 300)
        logging.info("Checker ended at " + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')+ " for " + domain)


        ''' DELETE '''
        logging.info(domain + "Deletion Started at " + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')+ " for " + domain)
        checker.delete_resources(report_id=report_id+".csv")
        logging.info(domain + "Deletion Ended at " + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')+ " for " + domain)


        notifier = Notifier()
        notifier.notifiers = config['notifiers']
        notifier.messages = [{    
            "status":"#D00000",
            "long_message":"Hello",
            "short_message":"Hi",
            "time_string":"1212",
            "domain":"jivox",
            "username": "Cloudinary",
            "icon_url": "https://cloudinary-res.cloudinary.com/image/upload/website/cloudinary_web_favicon.png"
        }]
        notifier.notify()