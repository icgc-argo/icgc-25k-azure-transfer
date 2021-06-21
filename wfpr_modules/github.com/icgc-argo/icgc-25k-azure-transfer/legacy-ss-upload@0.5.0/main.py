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
import subprocess
import requests


def upload_data(song_url, score_url, study_id, analysis_id, access_token, data_files=list()):
    file_names = [os.path.basename(f) for f in data_files]

    # prepare manifest file
    url = f'{song_url}/studies/{study_id}/analysis/{analysis_id}'
    headers = {"Authorization": f"Bearer {access_token}"}
    res = requests.get(url, headers=headers)

    if res.status_code == 200:
        payload_dict = json.loads(res.text)
        if payload_dict['analysisState'] != 'UNPUBLISHED':
            sys.exit(f'SONG analysis object not in UNPUBLISHED state, file upload not permitted.')

        cwd = os.getcwd()
        with open('manifest.txt', 'w') as m:
            m.write(f"{analysis_id}\t\t\n")
            for f in payload_dict['file']:
                if f['fileName'] not in file_names:
                    sys.exit(f"File '{f['fileName']}' exists in SONG payload, but not provided for upload.")

                file_path = os.path.join(cwd, f['fileName'])
                m.write(f"{f['objectId']}\t{file_path}\t{f['fileMd5sum']}\n")

    else:
        sys.exit(f'Unable to retieve SONG analysis object {analysis_id}')

    profile = 'collab'
    if 'azure' in score_url.lower():
        profile = 'azure'
    elif 'aws' in score_url.lower():
        profile = 'aws'

    transport_parallel_env = f"TRANSPORT_PARALLEL={os.environ['TRANSPORT_PARALLEL']}" \
                             if os.environ.get('TRANSPORT_PARALLEL') else ''

    transport_mem_env = f"TRANSPORT_MEMORY={os.environ['TRANSPORT_MEMORY']}" \
                        if os.environ.get('TRANSPORT_MEMORY') else ''

    # score client upload
    upload_cmd = f'{transport_parallel_env} {transport_mem_env} METADATA_URL={song_url} STORAGE_URL={score_url} ACCESSTOKEN={access_token}'
    upload_cmd += f' score-client --profile {profile} upload --manifest manifest.txt'

    proc = subprocess.Popen(
                upload_cmd,
                shell=True,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
    stdout, stderr = proc.communicate()

    if proc.returncode:  # error occurred
        print(f"SCORE upload failed, more info: {stderr}", file=sys.stderr)
        sys.exit(proc.returncode)

    # publish song analysis
    url = f'{song_url}/studies/{study_id}/analysis/publish/{analysis_id}'
    headers = {"Authorization": f"Bearer {access_token}"}
    res = requests.put(url, headers=headers)

    if res.status_code != 200:
        sys.exit(f'Data files uploaded, but unable to publish SONG analysis. More info: {res.text}')
    else:
        print('Data files uploaded, SONG analysis published.', file=sys.stderr)


def main():
    """
    Python implementation of tool: legacy-ss-upload

    This is auto-generated Python code, please update as needed!
    """

    parser = argparse.ArgumentParser(description='Tool: legacy-ss-upload')
    parser.add_argument('-u', '--song-url', type=str, help='SONG (metadata) server URL', required=True)
    parser.add_argument('-r', '--score-url', type=str, help='SCORE (data) server URL')
    parser.add_argument('-s', '--study-id', type=str, help='Study ID', required=True)
    parser.add_argument('-a', '--analysis-id', type=str, help='SONG analysis ID', required=True)
    parser.add_argument('-d', '--data-files', type=str, nargs='+', help='Data files to be uploaded', required=True)
    args = parser.parse_args()

    for f in args.data_files:
        if not os.path.isfile(f):
            sys.exit(f"Error: specified upload file '{f}' does not exist or is not accessible!")

    access_token = os.environ.get('ACCESS_TOKEN')
    if not access_token:
        sys.exit('Please provide access token as environment variable: ACCESS_TOKEN')

    upload_data(args.song_url, args.score_url, args.study_id, args.analysis_id, access_token, args.data_files)


if __name__ == "__main__":
    main()
