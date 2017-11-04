import os
import glob

from config import Config

from models.vhosts import Vhost

def list_vhost_files():
    files = glob.glob(Config['vhosts_files'])
    vhosts = []
    for vhost in files:
        vhost_specs = {}
        with open(vhost, 'r') as opened:
            lines = opened.readlines()


        ## HOSTS
        host = lines[0][:-2].strip()
        secondary_host = None
        if len(host.split(' ')) > 1:
            hosts = host.split(' ')
            host = hosts[0]
            secondary_host = hosts[1]
        vhost_specs['host'] = host
        vhost_specs['secondary_host'] = secondary_host


        ## LOCAL ADDRESS
        local_address = lines[2][:-2].split(':')[0].strip()[8:]
        vhost_specs['local_address'] = local_address


        ## PORT
        port = lines[2][:-2].split(':')[1].strip()
        vhost_specs['port'] = port
        vhosts.append(vhost_specs)
    return vhosts

def list_vhosts_db():
    vhosts = []
    for vhost in Vhost.select():
        vhost_specs = {
            'address': vhost.address,
            'secondary_address': vhost.secondary_address,
            'internal_ip': vhost.internal_ip,
            'internal_port': vhost.internal_ip
        }
        vhosts.append(vhost_specs)
    return vhosts


def new_vhost(address, secondary_address = None, internal_ip = '127.0.0.1', internal_port):
    model = '{host_a} {host_b} {{\n\tgzip\n\tproxy / {ip}:{port} {{\n\t\ttransparent\n\t}}\n}}'

    try:
        with open(Config['vhosts_path'] + address + '.conf', 'w') as opened:
            opened.write(model.format(
            host_a = address,
            host_b = secondary_address or '',
            ip = internal_ip,
            port = internal_port
            ))

        if address not in [i['address'] for i in list_vhosts_db()]:
            Vhost.create(
            address = address,
            secondary_address = secondary_address,
            internal_ip = internal_ip,
            internal_port = internal_port
            )
        else:
            vhost = Vhost.get(address = address)
            vhost.secondary_address = secondary_address
            vhost.internal_ip = internal_ip
            vhost.internal_port = internal_port
            vhost.save()
        return True
    except:
        return False


def delete_vhost(address):
    try:
        vhost = Vhost.get(Vhost.address == address)
        vhost.delete_instance()
        os.remove(Config['vhosts_path'] + address + '.conf')
        return True
    except Exception as e:
        print(e)
        return False


def load():
    try:
        for vhost in list_vhost_files():
            if vhost['host'] not in [i['address'] for i in list_vhosts_db()]:
                Vhost.create(
                address = vhost['host'],
                secondary_address = vhost['secondary_host'],
                internal_ip = vhost['local_address'],
                internal_port = vhost['port']
                )
        return True
    except:
        return False
