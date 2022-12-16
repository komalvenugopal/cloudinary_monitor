import boto3
import requests
import json
import logging
import datetime

class Notifier(object):
    def notify(self):
        for message in self.messages:
            for notifier in self.notifiers:
                if(notifier=="slack"):
                    status = message[notifier]['status']
                    domain = message[notifier]['domain']
                    long_message = message[notifier]['long_message']
                    short_message = message[notifier]['short_message']
                    time_string = datetime.datetime.now()
                    username = self.notifiers[notifier]['username'] if 'username' in self.notifiers[notifier] else "Python Triggers"
                    icon_url = self.notifiers[notifier]['icon_url'] if 'icon_url' in self.notifiers[notifier] else "https://slack.com/img/icons/app-57.png"
                    for channel in self.notifiers[notifier]["channels"]:
                        final_message = self.construct_message(status, long_message, short_message, time_string, domain, channel, username, icon_url)
                        response = requests.post(self.notifiers[notifier]["url"], data=final_message)
                        logging.info('Sent Message to: ' + channel)

                elif(notifier=="lambda"):
                    lambda_client = boto3.client('lambda',region_name=self.notifiers[notifier]['region'])
                    lambda_payload = {
                        "name" : message[notifier]["name"],
                        "subject": message[notifier]["subject"],
                        "message": message[notifier]["body"]
                    }
                    lambda_client.invoke(FunctionName=self.notifiers[notifier]["name"], InvocationType='Event', Payload=json.dumps(lambda_payload))            

                elif(notifier=="sns"):
                    sns_client = boto3.client('sns',region_name=self.notifiers[notifier]['region'])
                    sns_client.publish(TargetArn=self.notifiers[notifier]["arn"], Message=json.dumps(message[notifier]["body"]), Subject=message[notifier]["subject"])
        self.messages = []

    def construct_message(self, status, long_message, short_message, time_string, domain, channel, username, icon_url):
        message = '''
            {
                "channel": "%s",
                "text": "%s",
                "attachments": [
                    {
                        "color": "%s",
                        "fields": [
                            {
                                "title": "Message",
                                "value": "%s",
                                "short": true
                            },
                            {
                                "title": "Time",
                                "value": "%s",
                                "short": true
                            },
                            {
                                "title": "Domain",
                                "value": "%s",
                                "short": true
                            }
                        ]
                    }
                ],
                "username": "%s",
                "icon_url": "%s"
            }
        ''' % (channel, long_message, status, short_message, time_string, domain, username, icon_url)
        return message