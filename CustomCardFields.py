import json
import jinja2
import os

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class CustomCardFields(object):

  TEMPLATE = jinja_environment.get_template('templates/card.html')

  def __init__(self, dictionary={}):
    self.fields = dictionary;

  @classmethod
  def getFieldsFromJson(cls, Json):
    fields = json.loads(Json);
    return cls(fields);
    
  @classmethod
  def getFieldsFromItem(cls, item):
    key = 'sourceItemId'
    if key in item:
      return cls.getFieldsFromJson(item['sourceItemId'])
    else:
      return cls()

  def getJson(self):
    return json.dumps(self.fields)

  def renderHtml(self):
    return CustomCardFields.TEMPLATE.render(self.fields)

  def get(self, key):
    return self.fields[key]

  def set(self, key, val):
    self.fields[key] = val

  def updateItem(self, item):
    item['sourceItemId'] = self.getJson()
    item['html'] = self.renderHtml()
    return item;
