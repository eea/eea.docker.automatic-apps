# The contents of this file are subject to the Mozilla Public
# License Version 1.1 (the "License"); you may not use this file
# except in compliance with the License. You may obtain a copy of
# the License at http://www.mozilla.org/MPL/
#
# Software distributed under the License is distributed on an "AS
# IS" basis, WITHOUT WARRANTY OF ANY KIND, either express or
# implied. See the License for the specific language governing
# rights and limitations under the License.
#
# The Initial Owner of the Original Code is European Environment
# Agency (EEA). All Rights Reserved.
#
# Authors:
# Olimpiu Rob - Eau de Web Romania

__doc__ = """
    Applications trigger.
"""

import argparse
import logging
import os
import sys

import requests

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger("Reportek Automatic Apps")

FWD_ENVS_ENDPOINT = 'ReportekEngine/get_forward_envelopes'
FWD_ENDPOINT = 'forwardState'


def trigger_apps(portal_url, user, password, timeout):
    total = 0
    success = 0
    failed = 0
    fwd_envs_url = '/'.join([portal_url, FWD_ENVS_ENDPOINT])
    auth = (user, password)
    resp = requests.get(fwd_envs_url, auth=auth, timeout=int(timeout))
    if resp.ok:
        envs = resp.json()
        for env in envs:
            trigger_url = '/'.join([env, FWD_ENDPOINT])
            while True:
                t_resp = requests.get(trigger_url,
                                      auth=auth,
                                      timeout=int(timeout))
                if t_resp.ok:
                    info = t_resp.json()
                    forwarded = info.get('forwarded')
                    triggered = info.get('triggered')
                    triggerable = info.get('triggerable')
                    if forwarded:
                        logger.info("Successfully forwarded {} for {}".format(forwarded, env))
                        success += 1
                    if triggered:
                        logger.info("Successfully triggered {} for {}".format(triggered, env))
                        success += 1
                    if not triggerable:
                        logger.info("No more triggerable app for {}".format(env))
                        break
                else:
                    logger.warning("Unable to trigger {}. Response code: {} - {}".format(env, t_resp.status_code, t_resp.content))
                    failed += 1
                    break

    else:
        logger.error("Unable to retrieve running envelopes: {}".format(resp.status_code))
    total = success + failed
    logger.info("Finished. Total: {}, Success: {}, Failed: {}".format(total,
                                                                      success,
                                                                      failed))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'portal_url',
        metavar='portal_url',
        help='Portal url',
        nargs='?',
        default=os.environ.get('PORTAL_URL'))
    parser.add_argument(
        'user',
        metavar='user',
        help='Username',
        nargs='?',
        default=os.environ.get('USERNAME'))
    parser.add_argument(
        'password',
        metavar='password',
        help='Password',
        nargs='?',
        default=os.environ.get('PASSWORD'))
    parser.add_argument(
        'timeout',
        metavar='timeout',
        nargs='?',
        help='Timeout',
        default=os.environ.get('TIMEOUT', 20))

    try:
        args = parser.parse_args()
    except:
        args = None

    if not args or not args.portal_url or not args.user or not args.password:
        print(__doc__)
        print("For help use --help")
    else:
        trigger_apps(args.portal_url, args.user, args.password, args.timeout)
