#!/usr/bin/env python
import docker
import datetime
import atexit
import os
import sys


def get_environment(env_name):
    env_var = os.environ[env_name]
    if not env_var:
        print("{0} is invalid", env_name)
        sys.exit(-400)
    return env_var


base_url = get_environment("DOCKER_BASE_URL")

client = docker.DockerClient(base_url=base_url)

now = datetime.datetime.now()
starting_point = now - datetime.timedelta(minutes=5)


container_suffix = get_environment("BASE_IMAGE_SUFFIX")
base_container_name = get_environment("BASE_IMAGE_NAME")
cluster_name = get_environment("CLUSTER_NAME")


container_name = base_container_name + "-" + container_suffix
init_container_name = base_container_name + "-init-" + container_suffix
sidecar_container_name = base_container_name + "-sidecar-" + container_suffix


def wait_for(action="start"):
    print("Wait for {0} to {1}".format(container_name, action))
    for event in client.events(since=starting_point, decode=True):
        if event["Type"] == "container" and event["Action"] == action and event["Actor"]["Attributes"]["name"] == container_name:
            break


def cleanup():
    print("Cleaning up...")
    try:
        proxy_container = client.containers.get(sidecar_container_name)
        proxy_container.stop()
        pass
    except docker.errors.NotFound:
        pass
    try:
        proxy_container = client.containers.get(sidecar_container_name)
        proxy_container.remove()
        pass
    except docker.errors.NotFound:
        pass


def create_proxy():
    print("Creating proxy...")
    client.containers.run("docker.io/istio/proxy_init:0.7.1",
                          ["-p", "15001", "-u", "1337"],
                          cap_add="NET_ADMIN", detach=True,
                          network_mode="container:"+container_name,
                          auto_remove=True, name=init_container_name)
    istio_proxy_entrypoint = [
        "su", "istio-proxy", "-c",
        '''/usr/local/bin/pilot-agent proxy \
        --proxyLogLevel trace \
        --discoveryAddress istio-pilot.service.consul:15007 \
        --serviceregistry Consul \
        --serviceCluster ${CLUSTER_NAME} \
        --zipkinAddress zipkin.service.consul:9411 \
        --configPath /var/lib/istio >/tmp/envoy.log
        '''
    ]
    client.containers.run("gcr.io/istio-release/proxy_debug:1.0.0",
                          detach=True, network_mode="container:"+container_name,
                          auto_remove=False, name=sidecar_container_name,
                          environment={"CLUSTER_NAME": cluster_name},
                          entrypoint=istio_proxy_entrypoint)
    print("Proxy created")


if __name__ == "__main__":
    atexit.register(cleanup)
    wait_for(action="start")
    create_proxy()
    wait_for(action="die")
