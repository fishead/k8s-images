<img src="https://www.docker.com/sites/default/files/vertical.png" style="width: 100px" />
<img src="https://github.com/kubernetes/kubernetes/raw/master/logo/logo.png" style="width: 100px; margin-left: 20px;" />

## What this project for? | 这个项目是用来干什么的？
1. take a docker image url
2. get all the tags of the image
3. generate Dockerfile for each tag
4. (optional) copy image of each tag with the Dockerfile and Docker Hub Automated Build service


## Howto generate Dockerfile

1. Put image urls you want process in `images.py`

2. Generate Dockerfiles
```shell
./gen-dockerfiles.py
```

## (optional) How to copy image with Docker Hub Automated build service
1. Edit variables on top of gen-automated-build-on-docker-hub python script

2. Create [Automated builds](https://docs.docker.com/docker-cloud/builds/automated-build/) on Docker Hub
```shell
./gen-automated-build-on-docker-hub.py
```


## Todo
- [ ] filter tags


## Disclaimer
The code is really rough, use it with caution.
