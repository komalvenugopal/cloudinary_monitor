import boto3
import requests
import json
import logging

class Notifier(object):
    def notify(self):
        lambda_client = boto3.client('lambda')
        for message in self.messages:
            status = message['status']
            domain = message['domain']
            long_message = message['long_message']
            short_message = message['short_message']
            time_string = message['time_string']       
            username = message['username'] if 'username' in message else "Python Triggers"
            icon_url = message['icon_url'] if 'icon_url' in message else "https://slack.com/img/icons/app-57.png"

            for notifier in self.notifiers:
                if(notifier=="slack"):
                    for channel in self.notifiers["slack"]["channels"]:
                        message = self.construct_message(status, long_message, short_message, time_string, domain, channel, username, icon_url)
                        response = requests.post(self.notifiers["slack"]["url"], data=message)
                        logging.info('Sent Message to: ' + channel)

                elif(notifier=="lambda_function"):
                    lambda_payload = {
                        "name": short_message,
                        "state": status,
                        "message": long_message
                    }
                    lambda_client.invoke(FunctionName=self.notifiers["lambda_function"], InvocationType='Event', Payload=json.dumps(lambda_payload))            
        self.messages = []

    def construct_message(self, status, long_message, short_message, time_string, domain, channel, username, icon_url):
        message = '''
            {
                "channel": "%s",
                "text": "%s",
                "attachments": [
                    {
                        "pretext": "Alert !!!",
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