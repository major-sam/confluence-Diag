import os
from pprint import pprint
import requests as reqs
import json
from diagrams import Diagram, Edge
from diagrams.azure.web import AppServiceDomains
from diagrams.azure.compute import AutomanagedVM
from diagrams.azure.database import SQLDatabases
from diagrams.onprem.queue import Rabbitmq
from diagrams.onprem.inmemory import Redis

# todo откостылить в CI
JSON = os.path.join(
    'C:' + os.sep + 'Users' + os.sep + 'vrebyachih' + os.sep + 'smart_git' + os.sep + 'jenkins-shared-libriary' +
    os.sep + 'resources' + os.sep + 'com' + os.sep + 'packageMap.json')
SPACE_KEY = "DEV"
headers = {'Content-Type': 'application/json; charset=utf-8',
           'Authorization': "Bearer MzMzMjY0MDM2NjQ4Or7DMrZ0bCaAqXHJHTadPz6aFkMR"
           }
CONTENT_ROOT = "https://confluence.baltbet.ru:8444/rest/api/content/"
headers_wo_content = {
    'Authorization': "Bearer MzMzMjY0MDM2NjQ4Or7DMrZ0bCaAqXHJHTadPz6aFkMR",
    'X-Atlassian-Token': 'no-check'
}
LINK_MAP = {
    'weak': ['dashed', 'black'],
    'hard': ['bold', 'black'],
    'critical': ['bold', 'red']
}


def draw_diagram(service):
    with Diagram(service['name'], outformat="jpg", filename=service['name'], show=False):
        service_app = AppServiceDomains(service['name'])
        if 'db' in service and service['db']:
            SQLDatabases(service['db']['dbName']) >> service_app
        if 'redis' in service and service['redis']:
            Redis(service['redis']) >> service_app
        if 'rabbit' in service and service['rabbit']:
            Rabbitmq(service['rabbit']) >> service_app

        for link in service['links']:
            link_object = AutomanagedVM(link)
            _lo = service['links'][link]
            _lo_power = _lo['dependency'].lower()
            service_app >> Edge(label=_lo['proto'] + ":" + str(_lo['port']),
                                style=LINK_MAP[_lo_power][0],
                                color=LINK_MAP[_lo_power][1]) >> link_object


def generate_page(dict_vars):
    if dict_vars['db']:
        db_line = "<h4>Database: " + dict_vars['db']['dbName'] + \
                  "</h4><h5>Initial backup path:" + dict_vars['db']['backupFilePath'] + "</h5><h5>Initial scripts: " + \
                  dict_vars['db']['initScripts'] + "</h5>"
        if dict_vars['db']['dbFiles']:
            db_line += "<h5>DB physical files names: " + str(dict_vars['db']['dbFiles']) + "</h5>"
    else:
        db_line = "<h4>No Database for this service</h4>"
    return "<ac:layout><ac:layout-section ac:type=\'two_equal\'><ac:layout-cell>" + \
           "<h4>Description:</h4><p><br />" + dict_vars['type'] + " " \
           + dict_vars['description'] + "</p><h4>BitBucket Repo:</h4><p><br />" + \
           dict_vars['repo'] + "</p><h4>Man page: </h4><p><br />" + dict_vars['manPage'] + "</p>" + db_line + \
           "<h4>Post deploy scripts: </h4><p><br />" + \
           dict_vars['params']['postDeployScripts'] + "</p><h4>Default path:</h4><p><br />" + \
           dict_vars['type'] + "</p><br /></ac:layout-cell>" + \
           "<ac:layout-cell><p><ac:image ac:align=\'center\' ac:height=\'400\'><ri:attachment ri:filename=\'" + \
           dict_vars['name'] + ".jpg\' /></ac:image></p></ac:layout-cell></ac:layout-section></ac:layout>"


# "<p><ac:image ac:border=\"true\" ac:style=\"max-height:250.0px;\" ac:height=\"1080\" ac:width=\"1016\">" +\
# "<ri:attachment ri:title=\"ClientWorkSpace.jpg\"/></ac:image></p>"

def load_json():
    with open(JSON) as file:
        service_map = json.load(file)
        return service_map


def post_attachment(service_map):
    page_id = service_map['confluencePageId']
    gg = reqs.get(url=CONTENT_ROOT + page_id + "/child/attachment?filename=" + service_map['name'] + ".jpg",
                  headers=headers)
    content_dict = json.loads(gg.content)
    attachment_id = content_dict['results'][0]['id']
    file = {'file': open(service_map['name'] + '.jpg', 'rb')}
    response = reqs.post(url=CONTENT_ROOT + page_id + "/child/attachment/" + attachment_id + "/data",
                         headers=headers_wo_content,
                         files=file)


def put_html_to_confluence():
    service_maps = load_json()
    for service_map in service_maps.values():
        page_id = service_map['confluencePageId']
        draw_diagram(service_map)
        post_attachment(service_map)
        confluence_url = CONTENT_ROOT + page_id + "?expand=body.storage,version"
        response = reqs.get(url=confluence_url, headers=headers)
        content_dict = json.loads(response.content)
        version = content_dict['version']['number']
        version += 1
        body = '{"id":"' + page_id + '","type":"page","title":"' + service_map['name'] + '","space":{"key":"' + \
               SPACE_KEY + '"},"body":{"storage":{"value":"' + generate_page(service_map) + \
               '","representation":"storage"}},"version":{"number":' + str(version) + '}}'
        response = reqs.put(url=confluence_url, headers=headers, data=body.encode('utf-8'))
        pprint(service_map['name'] + ":" + str(response))


# todo откостылить в консольный запуск
if __name__ == '__main__':
    put_html_to_confluence()
    pprint("done")
