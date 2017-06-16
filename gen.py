from __future__ import print_function
import urllib2
import json
import os


IMAGES = [
    'gcr.io/google_containers/etcd-amd64',
    'gcr.io/google_containers/kube-apiserver-amd64',
    'gcr.io/google_containers/kube-controller-manager-amd64',
    'gcr.io/google_containers/kube-scheduler-amd64',
    'gcr.io/google_containers/pause-amd64',
    'gcr.io/google_containers/kube-proxy-amd64',
    'gcr.io/google_containers/k8s-dns-kube-dns-amd64',
    'gcr.io/google_containers/k8s-dns-sidecar-amd64',
    'gcr.io/google_containers/k8s-dns-dnsmasq-nanny-amd64',
    'gcr.io/google_containers/pause-amd64',
    'gcr.io/google_containers/kube-discovery-amd64',
    'gcr.io/google_containers/kube-dnsmasq-amd64',
    'gcr.io/google_containers/kubedns-amd64',
    'gcr.io/google_containers/kubernetes-dashboard-amd64',
    'quay.io/coreos/flannel',
    'quay.io/calico/node',
    'quay.io/calico/cni',
    'quay.io/coreos/etcd',
    'quay.io/calico/kube-policy-controller',
    'gcr.io/kubernetes-helm/tiller',
    'gcr.io/google_containers/defaultbackend',
    'gcr.io/google_containers/nginx-ingress-controller',
    'gcr.io/google_containers/heapster-influxdb-amd64',
    'gcr.io/google_containers/heapster-amd64',
    'gcr.io/google_containers/heapster-grafana-amd64',
    'gcr.io/google_containers/cluster-proportional-autoscaler-amd64',
    'gcr.io/google_containers/kibana',
    'gcr.io/google_containers/fluentd-elasticsearch',
    'gcr.io/google_containers/elasticsearch',
    'gcr.io/google_containers/exechealthz-amd64',
]


def get_tag_url(image_url):
    [domain, owner, image_name] = image_url.split('/')

    if domain == 'gcr.io':
        return 'https://gcr.io/v2/' + owner + '/' + image_name + '/tags/list'
    elif domain == 'quay.io':
        return 'https://quay.io/v2/' + owner + '/' + image_name + '/tags/list'


def to_kebab_case(str):
    return str.replace('/', '.')


for image_url in IMAGES:
    print('dealing with ' + image_url)

    raw_json = urllib2.urlopen(get_tag_url(image_url)).read()
    parsed_json = json.loads(raw_json)
    tags = parsed_json['tags']
    image_name = image_url.split('/')[-1]

    for tag in tags:
        filepath = os.path.join(os.getcwd(), to_kebab_case(image_url), tag, 'Dockerfile')

        try:
            docker_file = file(filepath, 'w+')

        except IOError as e:
            os.makedirs(os.path.dirname(filepath))
            docker_file = file(filepath, 'w+')

        except Exception as e:
            raise

        print('FROM ' + image_url + ':' + tag, file=docker_file)
