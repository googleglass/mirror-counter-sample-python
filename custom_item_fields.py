# Copyright (C) 2013 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Set of static methods to provide custom fields for a timeline item.

custom_item_fields uses timelineItem.sourceItemId of a timeline
item to enable custom fields (i.e. variables) for the timeline
item. Each custom field is a key->value pair encapsulated in a
dictionary (usually called fields). The dictionary is JSON
serialized and stored in the sourceItemId field of a timeline item.

Additionally, a possible use of a custom_item_fields is to use the
custom fields to render the HTML of a timeline item. This class
takes care of this by using jinja templates.
"""

__author__ = 'jewang.net (Jennifer Wang)'

import jinja2
import json
import os


jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))


KEY = 'sourceItemId'


def get_fields_from_json(json_input):
  """Returns a dictionary from json_input."""
  return json.loads(json_input)


def get_fields_from_item(item):
  """Returns dictionary made from sourceItemId field timeline item.

  Constructs a new dictionary holding custom fields from json_input
  assuming that input JSON is in item['sourceItemId'].
  """
  return get_fields_from_json(item.get(KEY, '{}'))


def get_json_from_fields(fields):
  """Returns JSON for custom fields to go in item['sourceItemId']."""
  return json.dumps(fields)


def render_html_from_fields(fields, template_url):
  """Returns html rendering of timeline item with custom fields data."""
  template = jinja_environment.get_template(template_url)
  return template.render(fields)


def get(item, key):
  """Returns value associated with in input key."""
  fields = get_fields_from_item(item)
  return fields[key]


def set(item, key, val, template_url=''):
  """Sets key->value custom field in timeline item."""
  return set_multiple(item, {key: val}, template_url)


def set_multiple(item, new_fields, template_url=''):
  """Sets key->value custom fields in timeline item.

  To do this, this method updates a timeline item's sourceItemId
  and, if enabled, template html.

  Generating JSON and rendering html with each call could cause
  performance issues on larger scale Glassware.
  """
  fields = get_fields_from_item(item)
  fields.update(new_fields)

  item['sourceItemId'] = get_json_from_fields(fields)
  if template_url:
    item['html'] = render_html_from_fields(
        fields, template_url)

  return item
