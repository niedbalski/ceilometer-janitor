#!/usr/bin/env python

__author__ = "Jorge Niedbalski <niedbalski@ubuntu.com>"

import os
import re
import operator
import smtplib

from keystoneclient.v2_0 import client
from ceilometerclient.client import get_client
from ceilometerclient.v2.options import cli_to_array

from novaclient.v1_1 import client as novaclient

from datetime import datetime, timedelta
from optparse import OptionParser

_HERE = os.path.dirname(os.path.basename(__file__))
TEMPLATES_PATH = os.path.join(_HERE, "templates")


from jinja2 import Environment, FileSystemLoader


def send_email(sender, receveirs, message):
    try:
        smtp = smtplib.SMTP('localhost')
        smtp.sendmail(sender, receivers, message)
    except Exception as ex:
     print ex
     pass


def dispatch_report(tenants):
    for email, instances in tenants.items():
        instances = [i.to_dict() for i in instances]
        send_email('sts-stack-noreply@canonical.com', [email],
                   load_template("stop_instance", {'email': email,
                                                   'instances': instances,
	}))


def load_template(name, params):
    env = Environment(loader=FileSystemLoader(TEMPLATES_PATH))
    return env.get_template(name + ".tpl").render(**params)


def is_old_enough(created, delta):
    return datetime.strptime(created, '%Y-%m-%dT%H:%M:%SZ') <= delta


def is_bootstrap_or_bastion(name):
    return name.endswith('bastion') or name.endswith('machine-0')


def is_active_vm(status):
    return status in ("ACTIVE", )


def instance_regex_matches(instance, regexes):
    for regex in regexes:
        if regex.match(instance.human_id) or regex.match(instance.id):
            return True
    return False


def filter_instances(delta, excluded_tenants, excluded_instances):

    keystone = client.Client(username=os.environ.get('OS_USERNAME'),
                             password=os.environ.get('OS_PASSWORD'),
                             tenant_name=os.environ.get('OS_TENANT_NAME'),
                             auth_url=os.environ.get('OS_AUTH_URL'))

    nova = novaclient.Client(None, None, None, auth_url=keystone.auth_url,
                             tenant_id=keystone.tenant_id,
                             auth_token=keystone.auth_token)

    for server in nova.servers.list(search_opts={'all_tenants': True}):
        if is_bootstrap_or_bastion(server.human_id) or is_active_vm(server.status) or \
           is_old_enough(server.updated, delta) or instance_regex_matches(
               server, excluded_instances):
            continue

        tenant = keystone.tenants.get(server.tenant_id)
        setattr(tenant, 'email', keystone.users.get(server.user_id).email)

        if tenant.name not in excluded_tenants:
            yield tenant, server


def filter_ceilometer_stats(instance_id, meters):

    ceilometer = get_client(api_version=2, **{
        'os_username': os.environ.get("OS_USERNAME"),
        'os_password': os.environ.get("OS_PASSWORD"),
        'os_tenant_name': os.environ.get("OS_TENANT_NAME"),
        'os_auth_url': os.environ.get("OS_AUTH_URL"),
    })

    for meter in meters:
        for stat in ceilometer.statistics.list(meter_name=meter.get('field'),
                                               q=cli_to_array(
                                                   "resource_id={0}".format(
                                                       instance_id))):
            yield getattr(operator, meter.get('op'))(float(stat.avg),
                                                     float(meter.get('value')))


def parse_options():
    parser = OptionParser()
    parser.add_option("-d", "--days", dest="days", default=3,
                      help="Days delta for instances", metavar="days")

    parser.add_option("-m", "--meters", default="cpu_util<=0.9",
                      dest="meters",
                      help="Meters to check, i.e: 'cpu_util<=0.9'")

    parser.add_option("-e", "--exclude-tenants", default="",
                      dest="exclude_tenants")

    parser.add_option("-s", "--send-report", default=False,
                      dest="dispatch_report")

    parser.add_option("-w", "--whitelist", default=None,
                      dest="whitelist")

    parser.add_option("-q", "--quiet", default=False,
                      dest="quiet")

    parser.add_option("-a", "--action", default="stop",
                      dest="action")

    (options, args) = parser.parse_args()
    return options


def main():
    options = parse_options()
    meters = cli_to_array(options.meters)
    delta = datetime.now() - timedelta(days=int(options.days))
    excluded_tenants = options.exclude_tenants.split(",")
    excluded_instances = []

    if options.whitelist:
        with open(options.whitelist) as rd:
            excluded_instances = [re.compile(
                line.strip('\n')) for line in rd.readlines()]

    print "Looking for instances matching: {0} usage criteria ignoring the ones created over the last {1} days\n".format(options.meters, options.days)

    to_report = {}
    for tenant, instance in filter_instances(delta, excluded_tenants,
                                             excluded_instances):

        if not all(f for f in filter_ceilometer_stats(instance.id, meters)):
            continue

        if tenant.email not in to_report:
            to_report[tenant.email] = []

        to_report[tenant.email].append(instance)
        if not options.quiet:
            print "{0},{1},{2} => {3}".format(tenant.name, instance.human_id,
                                              instance.updated, options.action)
            getattr(instance, options.action)()
            instance.stop()
        else:
            print "{0},{1},{2}".format(tenant.name,
                                       instance.human_id,
                                       instance.updated)

    if options.dispatch_report and not options.quiet:
        dispatch_report(to_report)


if __name__ == "__main__":
    main()
