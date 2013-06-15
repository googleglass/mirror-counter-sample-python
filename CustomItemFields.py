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

"""Set of static methods to provide custom fields for a timeline item."""

__author__ = 'jenniferwang@google.com (Jennifer Wang)'

import json
import os

import jinja2

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))


class CustomItemFields(object):
  """
  CustomItemFields uses timelineItem.sourceItemId of a timeline
  item to enable custom fields (i.e. variables) for the timeline
  item. Each custom field is a key->value pair encapsulated in a
  dictionary (usually called fields). The dictionary is JSON
  serialized and stored in the sourceItemId field of a timeline item.

  Additionally, a possible use of a CustomitemFields is to use the
  custom fields to render the HTML of a timeline item. This class
  takes care of this by using jinja templates.
  """
  @classmethod
  def get_fields_from_json(cls, json_input):
    """Returns a dictionary from json_input."""
    return json.loads(json_input)

  @classmethod
  def get_fields_from_item(cls, item):
    """
    Constructs a new dictionary holding custom fields from json_input
    assuming that input JSON is in item['sourceItemId']
    """
    key = 'sourceItemId'
    if key in item:
      return cls.get_fields_from_json(item[key])
    else:
      return {}

  @classmethod
  def get_json_from_fields(cls, fields):
    """Returns JSON for custom fields to go in item['sourceItemId']."""
    return json.dumps(fields)

  @classmethod
  def render_html_from_fields(cls, fields, template_url):
    """Returns html rendering of timeline item with custom fields data."""
    template = jinja_environment.get_template(template_url)
    return template.render(fields)

  @classmethod
  def get(cls, item, key):
    """Returns value associated with in input key."""
    fields = cls.get_fields_from_item(item)
    return fields[key]

  @classmethod
  def set(cls, item, key, val, template_url=''):
    return cls.set_multiple(item, {key: val}, template_url)

  @classmethod
  def set_multiple(cls, item, new_fields, template_url=''):
    """
    Sets key->value field in timeline item.
    To do this, this method updates a timeline item's sourceItemId
    and, if enabled, template html.

    Generating JSON and rendering html with each call could cause
    performance issues on larger scale Glassware.
    """
    fields = cls.get_fields_from_item(item)
    fields.update(new_fields)

    item['sourceItemId'] = cls.get_json_from_fields(fields)
    if template_url:
      item['html'] = cls.render_html_from_fields(
          fields, template_url)

    return item
