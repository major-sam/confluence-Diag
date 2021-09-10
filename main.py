import os
from pprint import pprint

import requests as reqs
import json

# todo откостылить в CI
JSON = os.path.join(
    'C:' + os.sep + 'Users' + os.sep + 'vrebyachih' + os.sep + 'smart_git' + os.sep + 'jenkins-shared-libriary' +
    os.sep + 'resources' + os.sep + 'com' + os.sep + 'packageMap.json')
SPACE_KEY = "DEV"
headers = {'Content-Type': 'application/json; charset=utf-8',
           'Authorization': "Bearer MzMzMjY0MDM2NjQ4Or7DMrZ0bCaAqXHJHTadPz6aFkMR"
           }


def generate_page(dict_vars):
    if dict_vars['db']:
        db_line = "<h4>Database:"+dict_vars['db']['dbName']+"</h4>" \
            "<h5>Initial backup path:"+dict_vars['db']['backupFilePath']+"</h5>" \
            "<h5>Initial scripts:"+dict_vars['db']['initScripts']+"</h5>"
        if dict_vars['db']['dbFiles']:
            db_line += "<h5>DB physical files names:"+str(dict_vars['db']['dbFiles'])+"</h5>"
    else:
        db_line = "<h4>No Database for this service</h4>"
    return "<h4>Description:</h4><p><br />"+dict_vars['type']+" "+dict_vars['description']+"</p>" \
           "<h4>BitBucket Repo:</h4><p><br />"+dict_vars['repo']+"</p>" \
           "<h4>Man page:</h4><p><br />"+dict_vars['manPage']+"</p>" \
           + db_line +  \
           "<h4>Post deploy scripts:</h4><p><br />"+dict_vars['params']['postDeployScripts']+"</p>" \
           "<h4>Default path:</h4><p><br />"+dict_vars['type']+"</p>" \
           "<h4>Links:</h4><p><br />"+str(dict_vars['links'])+"</p>"
    # return '<p>' + dict_vars['description'] + '</p>'


def load_json():
    with open(JSON) as file:
        service_map = json.load(file)
        return service_map


def put_html_to_confluence():
    service_maps = load_json()
    for service_map in service_maps.values():
        page_id = service_map['confluencePageId']
        confluence_url = "https://confluence.baltbet.ru:8444/rest/api/content/" + page_id + "?expand=body.storage," \
                                                                                            "version"
        response = reqs.get(url=confluence_url, headers=headers)
        content_dict = json.loads(response.content)
        version = content_dict['version']['number']
        version += 1
        body = '{"id":"' + page_id + '","type":"page","title":"' + service_map[
            'name'] + '","space":{"key":"' + SPACE_KEY \
               + '"},"body":{"storage":{"value":"' + generate_page(service_map) \
               + '","representation":"storage"}},"version":{"number":' + str(version) + '}}'
        reqs.put(url=confluence_url, headers=headers, data=body.encode('utf-8'))


# todo откостылить в консольный запуск
if __name__ == '__main__':
    put_html_to_confluence()
