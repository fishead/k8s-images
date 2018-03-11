#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import images
from urllib import request, error


# #############################################################################
# ######################### config there variables ############################
# #############################################################################

#  your username at hub.docker.com
docker_hub_username = os.environ.get('DOCKER_HUB_USERNAME')
# your password
docker_hub_password = os.environ.get('DOCKER_HUB_PASSWORD')

# your git provider name `github` or 'bitbucket'
docker_file_provider = 'github'

# your git repo name
docker_file_provider_repo_name = 'fishead/k8s-images'
_base_url = 'https://hub.docker.com/v2'


def json_stringify(obj):
    return json.dumps(obj).encode('utf8')


def json_parse(str):
    return json.loads(str)


def login(username, password):
    login_url = _base_url + '/users/login'
    data = {
        'username': username,
        'password': password,
    }
    headers = {
        'Content-Type': 'application/json',
    }
    res = post_request(login_url, data=json_stringify(data), headers=headers)
    return json_parse(res.read())


def create_autobuild(token, namespace, repository, vcs_repo_name, provider='github', description='', is_private=False, build_tags=[]):
    create_autobuild_url = _base_url + '/repositories/' + namespace + '/' + repository + '/autobuild/'

    data = {
        'dockerhub_repo_name': namespace + '/' + repository,
        'provider': provider,
        'vcs_repo_name': vcs_repo_name,
        'description': description,
        'is_private': is_private,
        'build_tags': build_tags,
    }
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'JWT ' + token,
    }
    res = post_request(create_autobuild_url, data=json_stringify(data), headers=headers)
    return json_parse(res.read())


def fetch_autobuild(token, namespace, repository):
    fetch_autobuild_url = _base_url + '/repositories/' + namespace + '/' + repository + '/autobuild/'
    headers = {
        'Authorization': 'JWT ' + token,
    }
    res = get_request(fetch_autobuild_url, headers=headers)
    return json_parse(res.read())


def create_autobuild_tag(token, namespace, repository, image_tag, dockerfile_location, source_type='Branch', source_name='master'):
    create_autobuild_tag_url = _base_url + '/repositories/' + namespace + '/' + repository + '/autobuild/tags/'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'JWT ' + token,
    }
    data = {
        'namespace': namespace,
        'repoName': repository,
        'name': image_tag,
        'dockerfile_location': dockerfile_location,
        'source_type': source_type,
        'source_name': source_name,
    }
    res = post_request(create_autobuild_tag_url, data=json_stringify(data), headers=headers)
    return json_parse(res.read())


def update_autobuild_tag(token, namespace, repository, autobuild_tag_id, image_tag, dockerfile_location, source_type='Branch', source_name='master'):
    update_autobuild_tag_url = _base_url + '/repositories/' + namespace + '/' + repository + '/autobuild/tags/' + str(autobuild_tag_id)
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'JWT ' + token,
    }
    data = {
        'namespace': namespace,
        'repoName': repository,
        'name': image_tag,
        'dockerfile_location': dockerfile_location,
        'source_type': source_type,
        'source_name': source_name,
    }
    res = put_request(update_autobuild_tag_url, data=json_stringify(data), headers=headers)

    return json_parse(res.read())


def delete_autobuild_tag(token, namespace, repository, autobuild_tag_id):
    delete_autobuild_tag_url = _base_url + '/repositories/' + namespace + '/' + repository + '/autobuild/tags/' + str(autobuild_tag_id) + '/'
    headers = {
        'Authorization': 'JWT ' + token,
    }
    res = delete_request(delete_autobuild_tag_url, headers=headers)


def get_request(url, headers={}):
    return _request(url, method='GET', headers=headers)


def post_request(url, data, headers={}):
    return _request(url, method='POST', data=data, headers=headers)


def put_request(url, data, headers={}):
    return _request(url, method='PUT', data=data, headers=headers)


def delete_request(url, headers={}):
    return _request(url, method='DELETE', headers=headers)


def _request(url, method='GET', data=None, headers={}, timeout=10):
    req = request.Request(url, method=method, data=data, headers=headers)
    return request.urlopen(req, timeout=timeout)


def to_kebab_case(str):
    return str.replace('/', '.')


if __name__ == '__main__':
    try:
        login_res = login(username=docker_hub_username, password=docker_hub_password)
        token = login_res.get('token')
    except error.HTTPError as e:
        print(e.reason)

    assert token, 'username and/or password wrong'

    cwd = os.getcwd()

    for image_url in images.IMAGES:
        print('image: ' + image_url)

        dir_name = to_kebab_case(image_url)
        image_repo_path = os.path.join(cwd, dir_name)

        tags = [filename for filename in os.listdir(image_repo_path) if os.path.isdir(os.path.join(image_repo_path, filename))]

        # make sure autobuild exists
        try:
            autobuild = fetch_autobuild(
                token,
                namespace=docker_hub_username,
                repository=dir_name,
            )
        except error.HTTPError as e:
            # if autobuild does not exists, then create it
            if (e.getcode() == 404):
                autobuild = create_autobuild(
                    token,
                    namespace=docker_hub_username,
                    repository=dir_name,
                    provider=docker_file_provider,
                    vcs_repo_name=docker_file_provider_repo_name,
                    description='mirror of ' + image_url,
                )
            else:
                raise e
        assert autobuild, 'something is wrong, autobuild does not exists'

        exists_build_tags = autobuild.get('build_tags')

        # remove exists tags
        for exists_build_tag in exists_build_tags:
            delete_autobuild_tag(
                token,
                namespace=docker_hub_username,
                repository=dir_name,
                autobuild_tag_id=exists_build_tag.get('id'),
            )

        for tag in tags:
            print('\ttag: ' + tag)
            docker_file_location = os.path.join('/', dir_name, tag)

            create_autobuild_tag(
                token=token,
                namespace=docker_hub_username,
                repository=dir_name,
                image_tag=tag,
                dockerfile_location=docker_file_location
            )
