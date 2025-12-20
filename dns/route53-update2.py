#!/usr/bin/python3
# -----------------------------------------------------------------
# route53-update2.py -- Updates a DNS record in Amazon's Route 53. This is the
# python3, boto version.
#
# Copyright 2025 Michael Kelly (m@michaelkelly.org)
# -----------------------------------------------------------------

from urllib import request
import boto3
import click
import logging
import socket
import sys

# https://www.rdegges.com/2018/to-30-billion-and-beyond/
IP_SERVICE_URL = "https://api.ipify.org"

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
    logger.debug(f"list_resource_record_sets({zone_id}) => {response}")
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
    hostname = socket.getfqdn()
    exe = sys.argv[0]
    comment = f'Updated by {exe} on {hostname}'
    response = client.change_resource_record_sets(
        HostedZoneId=zone_id,
        ChangeBatch={
            'Comment': comment,
            'Changes': [{
                'Action': 'UPSERT',
                'ResourceRecordSet': rrs,
            }]
        })
    logger.debug(f"change_resource_record_sets({zone_id}) => {response}")


def delete_dns(client, zone_id, rrs):
    hostname = socket.getfqdn()
    exe = sys.argv[0]
    comment = f'Deleted by {exe} on {hostname}'
    response = client.change_resource_record_sets(
        HostedZoneId=zone_id,
        ChangeBatch={
            'Comment': comment,
            'Changes': [{
                'Action': 'DELETE',
                'ResourceRecordSet': rrs,
            }]
        })
    logger.debug(f"change_resource_record_sets({zone_id}) => {response}")


@click.command()
@click.option(
    "--log-level",
    type=click.Choice(["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"]),
    default="WARNING",
    show_default=True,
    callback=lambda ctx, param, val: logger.setLevel(val),
    expose_value=False,
    help="Set the log level")
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
    "--ip",
    type=str,
    default=None,
    help="Set DNS record to provided IP. Do not auto-detect.")
@click.option(
    "--delete",
    type=bool,
    is_flag=True,
    default=False,
    help="Delete the DNS record instead of updating it.")
@click.option(
    "--dry-run",
    type=bool,
    is_flag=True,
    default=False,
    help="Don't actually do the thing. Usually useful with --log-level INFO")
def main(zone_id, domain, ttl, ip, dry_run, delete):
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
    
    \b
    We can also clean up after ourselves and delete a record:
        ./route53-update2.py --zone-id Z0000000000000 \\
                --domain test.example.com. --delete
    """
    if not domain.endswith('.'):
        raise click.UsageError(
            "--domain must be fully-qualified, ending with '.'")
    if dry_run:
        logger.info(f"Dry run mode. Will not make changes.")
    client = boto3.client('route53')

    if delete:
        logger.info("Delete mode selected.")
        cur_rrs = get_rr_from_dns(client, zone_id, domain)
        logger.info(f"current rr = {cur_rrs}")
        if cur_rrs is None:
            logger.info("No matching record found to delete. Quitting.")
            sys.exit(1)
        if dry_run:
            logger.info("Would delete DNS record.")
        else:
            delete_dns(client, zone_id, cur_rrs)
            logger.info("Record deleted")
        return

    if ip is None:
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
        logger.info("IP updated")


if __name__ == "__main__":
    main()
