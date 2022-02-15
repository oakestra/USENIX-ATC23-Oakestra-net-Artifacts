from flask import Flask, request
from flask_socketio import SocketIO
from interfaces.mongodb_requests import mongo_init
from network.tablequery import *
from network import subnetwork_management, routes_interests
from operations import instances_management, cluster_management
from operations import service_management
from net_logging import configure_logging
import os

my_logger = configure_logging()

app = Flask(__name__)
app.secret_key = b'\xc8I\xae\x85\x90E\x9aBxQP\xde\x8es\xfdY'
app.logger.addHandler(my_logger)

socketio = SocketIO(app, async_mode='eventlet', logger=True, engineio_logger=True, cors_allowed_origins='*')

MY_PORT = os.environ.get('MY_PORT') or 10100


# .............. Cluster Handshake .....................#
# ......................................................#

@app.route('/api/net/cluster', methods=['POST'])
def register_new_cluster():
    """
        Registration of the new cluster
        json file structure:{
            'cluster_id':string
            'cluster_port':int
        }
    """
    app.logger.info("Incoming Request /api/net/cluster")
    data = request.json
    app.logger.info(data)

    cluster_management.register_clsuter(
        cluster_id=data.get("cluster_id"),
        cluster_port=data.get("cluster_port"),
        cluster_address=str(request.remote_addr)
    )


@app.route('/api/net/interest/<job_name>', methods=['DELETE'])
def register_new_cluster(job_name):
    """
        Deregistration of an interest
        json file structure:{
            'job_name':string
        }
    """
    job_name = job_name.replace("_", ".")
    app.logger.info("Incoming Request DELETE /api/net/interest/" + job_name)
    return routes_interests.deregister_interest(request.remote_addr, job_name)


# ......... Deployment Endpoints .......................#
# ......................................................#

@app.route('/api/net/service/net_deploy_status', methods=['POST'])
def update_instance_local_deployment_addresses():
    """
    Result of the deploy operation in a cluster and the subsequent generated network addresses
    json file structure:{
        'job_id':string
        'instances:[{
            'instance_number':int
            'namespace_ip':string
            'host_ip':string
            'host_port':string
        }]
    }
    """

    app.logger.info("Incoming Request /api/job/net_deploy_status")
    data = request.json
    app.logger.info(data)

    return instances_management.update_instance_local_addresses(
        instances=data.get('instances'),
        job_id=data.get('job_id')
    )


@app.route('/api/net/service/deploy', methods=['POST'])
def new_service_deployment():
    """
    Input:
        {
            system_job_id:int,
            deployment_descriptor:{}
        }
    service deployment descriptor and job_id
    The System Manager decorates the service with a new RR Ip in its own DB
    """

    app.logger.info("Incoming Request /api/net/service/deploy")
    data = request.json
    app.logger.info(data)

    return service_management.deploy_request(
        deployment_descriptor=data.get('deployment_descriptor'),
        system_job_id=data.get('system_job_id')
    )


@app.route('/api/net/instance/deploy', methods=['POST'])
def new_instance_deployment():
    """
    Input:
        {
            system_job_id:int,
            replicas:int,
            cluster_id:string,
        }
    The System Manager adds an instance ip for a new deployed instance to a new cluster
    """

    app.logger.info("Incoming Request /api/net/instance/deploy")
    data = request.json
    app.logger.info(data)

    return instances_management.deploy_request(
        sys_job_id=data.get('system_job_id'),
        replicas=data.get('replicas'),
        cluster_id=data.get('cluster_id')
    )


@app.route('/api/net/undeploy/<system_job_id>/<instance>', methods=['DELETE'])
def instance_undeployment(system_job_id, instance):
    """
    Input:
        {
            system_job_id:int,
            instance:int
        }
    Undeployment request for the instance number "instance"
    """

    app.logger.info("Incoming Request /api/net/undeploy/" + str(system_job_id) + "/<instance>" + str(instance))

    return instances_management.undeploy_request(str(system_job_id), int(instance))


# .............. Table query Endpoints .................#
# ......................................................#

@app.route('/api/net/service/<service_name>/instances', methods=['GET'])
def table_query_resolution_by_jobname(service_name):
    """
    Get all the instances of a job given the complete name
    """
    service_name = service_name.replace("_", ".")
    app.logger.info("Incoming Request /api/net/service/" + str(service_name) + "/instances")
    return instances_management.get_service_instances(name=service_name, cluster_ip=request.remote_addr)


@app.route('/api/net/service/ip/<service_ip>/instances', methods=['GET'])
def table_query_resolution_by_ip(service_ip):
    """
    Get all the instances of a job given a Service IP in 172_30_x_y notation
    """
    service_ip = service_ip.replace("_", ".")
    app.logger.info("Incoming Request /api/net/service/ip/" + str(service_ip) + "/instances")
    return instances_management.get_service_instances(ip=service_ip, cluster_ip=request.remote_addr)


# ........ Subnetwork management endpoints .............#
# ......................................................#

@app.route('/api/net/subnet', methods=['GET'])
def subnet_request():
    """
    Returns a new subnetwork address
    """
    addr = subnetwork_management.new_subnetwork_addr()
    return {'subnet_addr': addr}


if __name__ == '__main__':
    import eventlet

    mongo_init(app)
    eventlet.wsgi.server(eventlet.listen(('0.0.0.0', int(MY_PORT))), app, log=my_logger)
