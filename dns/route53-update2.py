#!/usr/bin/python3
# -----------------------------------------------------------------
# route53-update2.py -- Updates a DNS record in Amazon's Route 53. This is the
# python3, boto version.
#
# Copyright 2020 Michael Kelly (michael@michaelkelly.org)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Sat Apr 18 02:23:22 EDT 2020
# -----------------------------------------------------------------

from urllib import request
import boto3
import click
import logging
import socket
import sys

IP_SERVICE_URL = "https://ipv4.icanhazip.com"

# Format inspired by glog
logging.basicConfig(
    format='%(levelname)s %(asctime)s %(filename)s:%(lineno)d %(message)s')
logger = logging.getLogger()


def get_ip():
    logger.info(f"Using {IP_SERVICE_URL} to determine my IP")
    with request.urlopen(IP_SERVICE_URL, data=None, timeout=5.0) as url:
        return url.read().decode("utf-8").strip()


def get_rr_from_dns(client, zone_id, domain):
    response = client.list_resource_record_sets(HostedZoneId=zone_id)
    for rr in response['ResourceRecordSets']:
        if rr['Name'] == domain and rr['Type'] == 'A':
            return rr


def make_resource_record_set(domain, ttl, ip):
    return {
        'Name': domain,
        'Type': 'A',
        'TTL': ttl,
        'ResourceRecords': [{
            'Value': ip,
        }],
    }


def update_dns(client, zone_id, rrs):
    hostname = socket.gethostname()
    exe = sys.argv[0]
    comment = f'Automatic update by {exe} on {hostname}'
    response = client.change_resource_record_sets(
        HostedZoneId=zone_id,
        ChangeBatch={
            'Comment': comment,
            'Changes': [{
                'Action': 'UPSERT',
                'ResourceRecordSet': rrs,
            }]
        })


@click.command()
@click.option(
    "--log-level",
    type=click.Choice(["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"]),
    default="WARNING",
    show_default=True,
    help="Zone ID to update")
@click.option("--zone-id", type=str, required=True, help="Zone ID to update")
@click.option(
    "--domain",
    type=str,
    required=True,
    help="Domain name to update. Must be part of --zone-id.")
@click.option(
    "--ttl",
    type=int,
    default=600,
    show_default=True,
    help="TTL to set on the A record")
@click.option(
    "--dry-run",
    type=bool,
    is_flag=True,
    default=False,
    help="Don't actually do the thing. Usually useful with --log-level INFO")
def main(log_level, zone_id, domain, ttl, dry_run):
    """Updates an AWS Route53 DNS name with this host's current IP.

    We use an external service to get the current IP, and update the IP in
    Route53 if necessary.

    We exit 1 if the current IP is up to date in Route53.

    Examples:

    \b
    Update current IP:
        ./route53-update2.py --zone-id Z0000000000000 \\
                --domain test.example.com.

    \b
    See what we would do:
        ./route53-update2.py --zone-id Z0000000000000 \\
                --domain test.example.com. --log-level INFO --dry-run

    If you want to use different AWS credentials, you can set environment
    variables, documented by boto3 (which we use to talk to Route53) here:

    \b
    https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html#environment-variables

    \b
    Here's an example: Use the "dns" profile:
        AWS_PROFILE=dns ./route53-update2.py [flags]
    """
    logger.setLevel(log_level)
    if not domain.endswith('.'):
        raise click.UsageError("--domain must be fully-qualified, ending with '.'")
    if dry_run:
        logger.info(f"Dry run mode. Will not make changes.")
    client = boto3.client('route53')
    ip = get_ip()
    logger.info(f"My IP is: {ip}")

    cur_rrs = get_rr_from_dns(client, zone_id, domain)
    new_rrs = make_resource_record_set(domain, ttl, ip)
    logger.info(f"current rr = {cur_rrs}")
    logger.info(f"new rr = {new_rrs}")

    # By comparing the whole ResourceRecordSet structures, we update if there is an
    # IP or a TTL change.
    if cur_rrs == new_rrs:
        logger.info("RRSs are equal. DNS is up to date. Quitting.")
        sys.exit(1)
    logger.info("RRSs are different. DNS needs an update")
    if dry_run:
        logger.info("Would update IP.")
    else:
        update_dns(client, zone_id, new_rrs)


if __name__ == "__main__":
    main()
