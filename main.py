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
    notifier = Notifier()
    notifier.notifiers = config['notifiers']

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

        # folders = checker.get_folders()
        # resource_type=["videos"]
        # resources= [1]
        # report_id="e2552f6074a4958cca8aacb8b4ef079ab7196a88a9824158edad63c74886b916"

        ''' GENERATE '''
        folders=[]
        report_id = checker.create_access_report( from_date=None, to_date="2022-04-30", resource_type="all", exclude_folders=folders, sort_by="accessed_at" )
        resources = checker.fetch_access_report(report_id, 300)
        logging.info("Checker ended at " + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')+ " for " + domain)

        notifier.messages = [{
            "status": "#008000" if len(resources)>0 else "#D00000",
            "long_message":"Generated Assets Data for: "+ report_id,
            "short_message": "Success" if len(resources)>0 else "Failed",
            "time_string":datetime.datetime.now(),
            "domain":domain,
            "username": "Cloudinary",
            "icon_url": "https://cloudinary-res.cloudinary.com/image/upload/website/cloudinary_web_favicon.png"
        }]
        notifier.notify()


        ''' DELETE '''
        logging.info(domain + "Deletion Started at " + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')+ " for " + domain)
        response = checker.delete_resources(report_id=report_id+".csv")
        logging.info(domain + "Deletion Ended at " + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')+ " for " + domain)

        notifier.messages = [{
            "status": "#008000" if response==True else "#D00000",
            "long_message":"Deleted Assets Data for "+ report_id,
            "short_message": "Success" if response==True else "Failed",
            "time_string":datetime.datetime.now(),
            "domain":domain,
            "username": "Cloudinary",
            "icon_url": "https://cloudinary-res.cloudinary.com/image/upload/website/cloudinary_web_favicon.png"
        }]
        notifier.notify()