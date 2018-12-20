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
import requests
import os
import sys
import logging
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger("Reportek Automatic Apps")

ACTIVE_APPS_ENDPOINT = 'ReportekEngine/getWkAppsActive'
TRIGGER_ENDPOINT = 'triggerApplication'


def trigger_apps(portal_url, user, password, timeout, wf_app):
    apps_url = '/'.join([portal_url, ACTIVE_APPS_ENDPOINT])
    auth = (user, password)
    params = {'p_applications': wf_app}
    resp = requests.get(apps_url, auth=auth, params=params, timeout=int(timeout))
    total = 0
    success = 0
    failed = 0
    if resp.ok:
        wks = resp.json()
        for wk in wks:
            wk_id = wk.split('/')[-1]
            trigger_url = '/'.join([wk, TRIGGER_ENDPOINT])
            t_params = {'p_workitem_id': wk_id}
            t_resp = requests.get(trigger_url, auth=auth, params=t_params, timeout=int(timeout))
            if t_resp.ok and t_resp.text == '1':
                logger.info("Successfully triggered {} for {}".format(wf_app, wk))
                success += 1
            else:
                logger.warning("Unable to trigger {} for {}. Response code: {} - {}".format(wf_app, wk, t_resp.status_code, t_resp.content))
                failed += 1
            total += 1
    else:
        logger.error("Unable to retrieve active Apps workitems: {}".format(resp.status_code))
    logger.info("Finished. Total: {}, Success: {}, Failed: {}".format(total, success, failed))

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
        'wf_app',
        metavar='wf_app',
        help='Workflow app to be triggered',
        nargs='?',
        default=os.environ.get('WF_APP'))
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

    if not args or not args.portal_url or not args.wf_app or not args.user or not args.password:
        print(__doc__)
        print("For help use --help")
    else:
        trigger_apps(args.portal_url, args.user, args.password, args.timeout, args.wf_app)
