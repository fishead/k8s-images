from __future__ import print_function
import urllib2
import json
import os


IMAGES = [
    'etcd-amd64',
    'kube-apiserver-amd64',
    'kube-controller-manager-amd64',
    'kube-scheduler-amd64'
]


for image in IMAGES:
    print('dealing with ' + image)
    raw_json = urllib2.urlopen('https://gcr.io/v2/google-containers/' + image + '/tags/list').read()
    parsed_json = json.loads(raw_json)
    tags = parsed_json['tags']


    for tag in tags:
        filepath = os.path.join(os.getcwd(), image, tag, 'Dockerfile')


        try:
            docker_file = file(filepath, 'w+');


        except IOError as e:
            os.makedirs(os.path.dirname(filepath))
            docker_file = file(filepath, 'w+');


        except Exception as e:
            raise


        print('FROM gcr.io/google_containers/' + image + ':' + tag, file = docker_file)
