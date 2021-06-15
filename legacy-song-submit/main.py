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


def pop_sids(payload, study_id):
    sids = {
        'objectIds': {}
    }

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
    sids['sampleId'] = payload_dict['sample'][0].pop('sampleId', None)
    sids['specimenId'] = payload_dict['sample'][0].pop('specimenId', None)
    payload_dict['sample'][0]['specimen'].pop('specimenId', None)
    sids['donorId'] = payload_dict['sample'][0]['specimen'].pop('donorId', None)
    payload_dict['sample'][0]['donor'].pop('donorId', None)
    sids['studyId'] = payload_dict['sample'][0]['donor'].pop('studyId', None)

    # rm file.objectId, file.studyId, file.analysisId
    for f in payload_dict['file']:
        sids['objectIds'][f['fileName']] = f.pop('objectId', None)
        f.pop('studyId', None)
        f.pop('analysisId', None)

    return payload_dict, sids


def verify_sids(payload, sids):
    mismatches = []
    if sids['sampleId'] and sids['sampleId'] != payload['sample'][0].pop('sampleId'):
        mismatches.append(f"'sampleId' mismatch, original: {sids['sampleId']}, new: {payload['sample'][0].pop('sampleId')}")

    if sids['specimenId'] and sids['specimenId'] != payload['sample'][0].pop('specimenId'):
        mismatches.append(f"'specimenId' mismatch, original: {sids['specimenId']}, new: {payload['sample'][0].pop('specimenId')}")

    if sids['donorId'] and sids['donorId'] != payload['sample'][0]['donor'].pop('donorId'):
        mismatches.append(f"'donorId' mismatch, original: {sids['donorId']}, new: {payload['sample'][0]['donor'].pop('donorId')}")

    if sids['studyId'] and sids['studyId'] != payload['sample'][0]['donor'].pop('studyId'):
        mismatches.append(f"'studyId' mismatch, original: {sids['studyId']}, new: {payload['sample'][0]['donor'].pop('studyId')}")

    for f in payload['file']:
        if sids['objectIds'].get(f['fileName']) and sids['objectIds'][f['fileName']] != f['objectId']:
            mismatches.append(f"Data file objectId mismatch for '{f['fileName']}', original: {sids['objectIds'][f['fileName']]}, new: {f['objectId']}")

    if mismatches:
        sys.exit("Mismatch(es) of system ID identified. More details:\n" + "\n".join(mismatches))


def submit_payload(song_url, study_id, payload, access_token, ignore_sid_mismatch=False):
    refreshed_payload, sids = pop_sids(payload, study_id)
    analysis_id = refreshed_payload['analysisId']

    # check whether analysis object already exists
    url = f"{song_url}/studies/{study_id}/analysis/{analysis_id}"
    headers = {"Authorization": f"Bearer {access_token}"} if access_token else {}
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        exist_payload_dict = json.loads(res.text)
        if exist_payload_dict['analysisState'] == 'PUBLISHED':
            sys.exit("SONG analysis object already exists and in PUBLISHED state, "
                     f"study: {study_id}, analysis ID: {analysis_id}")

        elif exist_payload_dict['analysisState'] != 'UNPUBLISHED':
            sys.exit(f"SONG analysis object already exists and in unsupported state, state: {exist_payload_dict['analysisState']}, "
                     f"study: {study_id}, analysis ID: {analysis_id}")

        else:  # now analysisState of existing analysis object is UNPUBLISHED
            # check existing analysis object is the same as the payload to be uploaded
            if not ignore_sid_mismatch:
                verify_sids(exist_payload_dict, sids)
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
            else:
                url = f"{song_url}/studies/{study_id}/analysis/{analysis_id}"
                res = requests.get(url, headers=headers)
                if res.status_code == 200:
                    submitted_payload_dict = json.loads(res.text)
                    if not ignore_sid_mismatch:
                        verify_sids(submitted_payload_dict, sids)
                else:
                    sys.exit(f"Unable to retrieve the SONG analysis payload that was just submitted, "
                             f"study: {study_id}, analysis ID:  {analysis_id}")

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
    parser.add_argument('-i', '--ignore-sid-mismatch', action='store_true', default=False,
                        help='SONG metadata payload')
    args = parser.parse_args()

    if not os.path.isfile(args.payload):
        sys.exit('Error: specified payload file %s does not exist or is not accessible!' % args.payload)

    access_token = os.environ.get('ACCESS_TOKEN')
    if not access_token:
        sys.exit('Please provide SONG access token as environment variable: ACCESS_TOKEN')

    analysis_id = submit_payload(args.song_url, args.study_id, args.payload, access_token, args.ignore_sid_mismatch)
    if analysis_id:
        print(analysis_id)


if __name__ == "__main__":
    main()
