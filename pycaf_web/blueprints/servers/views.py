#!/usr/bin/python
# -*- coding: utf8 -*-

from flask import Blueprint, render_template

blueprint = Blueprint('servers', __name__, template_folder='templates')

# A dictionary containing all imported servers
# TODO: find a better way to store theses
loaded_servers = dict()

def load_server(file_path):
    """
    Loads a pickled server from its filepath and inserts it in the loaded_servers dict.
    """
    print("Loading server.")
    with open(file_path, 'rb') as f:
        import pickle
        loaded_server = pickle.load(f)

    if loaded_server:
        global loaded_servers
        loaded_servers[loaded_server.uuid] = loaded_server
        return loaded_server.uuid

    return None

@blueprint.route('/get_server_from_uuid/<uuid>', methods=['GET'])
def get_server_from_uuid(uuid):
    """
    Parses the loaded_servers global to return server with uuid.
    """
    if uuid is None:
        return "Cannot get server with UUID: None."

    global loaded_servers
    for server_uuid in loaded_servers:
        if uuid == server_uuid:
            server = loaded_servers[uuid]
            #print("UUID neat: {}".format(server.uuid))
            #print("Infos are: {}".format(server.os_informations))
            #print("Modules are: {}".format(server.get_modules()))
            return render_template("servers/server_info.html", os_informations = server.os_informations,
                            server_id = server.uuid, modules=server.get_modules())

    return "Cannot find server with UUID: {}".format(uuid)

@blueprint.route('/list_servers')
def list_servers():
    """
    Lists all imported servers
    """
    print("Listing loaded servers")
    global loaded_servers

    return render_template('servers/list_servers.html', servers = loaded_servers)


@blueprint.route('/compare_servers', methods=['POST'])
def compare_servers():
    return "Not implemented yet"


@blueprint.route('/get_module_details/<uuid>/<module_name>', methods=['GET'])
def get_module_details(uuid, module_name):
    return render_template("servers/module_info.html", uuid=uuid, module_name=module_name)
