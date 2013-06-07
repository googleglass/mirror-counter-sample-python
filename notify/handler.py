# Copyright (C) 2013 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Request Handler for /notify endpoint."""

__author__ = 'alainv@google.com (Alain Vongsouvanh)'


import io
import json
import logging
import webapp2

from apiclient.http import MediaIoBaseUpload
from oauth2client.appengine import StorageByKeyName

from model import Credentials
import util


class NotifyHandler(webapp2.RequestHandler):
  """Request Handler for notification pings."""

  def post(self):
    """Handles notification pings."""
    logging.info('Got a notification with payload %s', self.request.body)
    data = json.loads(self.request.body)
    userid = data['userToken']
    # TODO: Check that the userToken is a valid userToken.
    self.mirror_service = util.create_service(
        'mirror', 'v1',
        StorageByKeyName(Credentials, userid, 'credentials').get())
    if data.get('collection') == 'timeline':
      self._handle_timeline_notification(data)

  def _handle_timeline_notification(self, data):
    """Handle timeline notification."""

    operations = ['increment', 'decrement', 'reset'];
    for user_action in data.get('userActions', []):
      logging.info(user_action)
      if user_action.get('type') == 'CUSTOM' and user_action.get('payload') in operations:
        # Fetch the timeline item.
        item = self.mirror_service.timeline().get(id=data['itemId']).execute()
	text = item['text']
	name = text[0:(text.rfind(':')+2)]; # includes ": " end of text 
	num = int(text[text.rfind(':')+2 : ])

	logging.info(num)
	logging.info(name)
	if user_action.get('payload') == operations[0]:
	  item['text'] = name + str(num + 1); 
	elif user_action.get('payload') == operations[1]:
	  item['text'] = name + str(num - 1); 
	elif user_action.get('payload') == operations[2]:
	  item['text'] = name + "0"; 

	if 'notification' in item:
	    item.pop('notification');
	self.mirror_service.timeline().update(id=data['itemId'], body=item).execute()
	# Only handle the first successful action.
        break

      else:
        logging.info(
            "I don't know what to do with this notification: %s", user_action)


NOTIFY_ROUTES = [
    ('/notify', NotifyHandler)
]
