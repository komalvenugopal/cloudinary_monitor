#!/usr/bin/env python
import yaml
import logging
import datetime
import os
from checkers.last_accessed import CloudinaryChecker
from notifiers.notify import Notifier
# import requests,json

def generate_report(checker,from_date=None,to_date=datetime.date.today(),resource_type="all",folders=[]):
    report_id = checker.create_access_report( from_date=from_date, to_date=to_date, resource_type=resource_type, exclude_folders=folders, sort_by="accessed_at" )
    return report_id

def fetch_report(domain, checker,report_id, sleep_seconds):
    resources = checker.fetch_access_report(domain, report_id, sleep_seconds)
    return resources

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
            notifier=notifier
        )
        logging.info(domain + 'Checker started at: ' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

        ''' GENERATE '''
        # folders = checker.get_folders()
        # report_id = generate_report(checker=checker, resource_type="video", to_date="2022-07-23")
        # resources = fetch_report(domain=domain, checker=checker, report_id=report_id, sleep_seconds=300)

        ''' DELETE '''
        report_id = "7251"
        response = checker.delete_resources(domain, report_id=report_id)

        logging.info("Checker ended at " + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')+ " for " + domain)