#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
  Copyright (C) 2021,  OICR

  This program is free software: you can redistribute it and/or modify
  it under the terms of the GNU Affero General Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU Affero General Public License for more details.

  You should have received a copy of the GNU Affero General Public License
  along with this program.  If not, see <http://www.gnu.org/licenses/>.

  Authors:
    Junjun Zhang
"""

import os
import sys
import json
import argparse
import requests


def cleanup_payload(payload, study_id):
    with open(payload, 'r') as p:
        payload_dict = json.load(p)

    if 'sample' not in payload_dict:
        sys.exit("No 'sample' found in the payload.")

    if len(payload_dict['sample']) != 1:
        sys.exit(f"Payload must contain exactly one 'sample', {len(payload_dict['sample'])} found.")

    if payload_dict.get('study') != study_id:
        sys.exit(f"'study' in payload {payload_dict.get('study')} does not match study_id {study_id}")

    # rm analysisState
    payload_dict.pop('analysisState', None)

    # rm experiment.analysisId
    payload_dict['experiment'].pop('analysisId', None)

    # rm sampleId, specimenId, donorId
    payload_dict['sample'][0].pop('sampleId', None)
    payload_dict['sample'][0].pop('specimenId', None)
    payload_dict['sample'][0]['specimen'].pop('specimenId', None)
    payload_dict['sample'][0]['specimen'].pop('donorId', None)
    payload_dict['sample'][0]['donor'].pop('donorId', None)
    payload_dict['sample'][0]['donor'].pop('studyId', None)

    # rm file.objectId, file.studyId, file.analysisId
    for f in payload_dict['file']:
        f.pop('objectId', None)
        f.pop('studyId', None)
        f.pop('analysisId', None)

    return payload_dict


def submit_payload(song_url, study_id, payload, access_token):
    refreshed_payload = cleanup_payload(payload, study_id)
    analysis_id = refreshed_payload['analysisId']

    # check whether analysis object already exists
    url = f"{song_url}/studies/{study_id}/analysis/{analysis_id}"
    res = requests.get(url)
    if res.status_code == 200:
        exist_payload_dict = json.loads(res.text)
        if exist_payload_dict['analysisState'] == 'PUBLISHED':
            sys.exit("SONG analysis object already exists and in PUBLISHED state, "
                     f"study: {study_id}, analysis ID {analysis_id}")

        elif exist_payload_dict['analysisState'] != 'UNPUBLISHED':
            sys.exit(f"SONG analysis object already exists and in unsupported state, state: {exist_payload_dict['analysisState']} "
                     f"study: {study_id}, analysis ID {analysis_id}")

        else:  # now analysisState of existing analysis object is UNPUBLISHED
            pass  # TODO: check existing analysis object is the same as the payload to be uploaded
            print(f"Use existing analysis object, study: {study_id}, analysis ID {analysis_id}", file=sys.stderr)

    else:  # continue with submit
        headers = {"Authorization": f"Bearer {access_token}"}
        res = requests.post(
            f"{song_url}/upload/{study_id}",
            headers=headers,
            json=refreshed_payload
        )

        if res.status_code != 200:
            sys.exit(f"Payload upload failed with status code: {res.status_code}")
        else:
            upload_id = res.json()['uploadId']
            res = requests.post(
                f"{song_url}/upload/{study_id}/save/{upload_id}",
                headers=headers
            )
            if res.status_code != 200:
                sys.exit(f"Payload upload failed at save with status code: {res.status_code}")

    return analysis_id


def main():
    """
    Python implementation of tool: legacy-song-submit

    This is auto-generated Python code, please update as needed!
    """

    parser = argparse.ArgumentParser(description='Tool: legacy-song-submit')
    parser.add_argument('-u', '--song-url', type=str, help='SONG server URL', required=True)
    parser.add_argument('-s', '--study-id', type=str, help='Study ID', required=True)
    parser.add_argument('-p', '--payload', type=str, help='SONG metadata payload', required=True)
    args = parser.parse_args()

    if not os.path.isfile(args.payload):
        sys.exit('Error: specified payload file %s does not exist or is not accessible!' % args.payload)

    access_token = os.environ.get('ACCESS_TOKEN')
    if not access_token:
        sys.exit('Please provide SONG access token as environment variable: ACCESS_TOKEN')

    analysis_id = submit_payload(args.song_url, args.study_id, args.payload, access_token)
    if analysis_id:
        print(analysis_id)


if __name__ == "__main__":
    main()

