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
import subprocess


def download_metadata(song_url, study_id, analysis_id, access_token, output_dir):
    url = f"{song_url}/studies/{study_id}/analysis/{analysis_id}"

    if access_token:
        headers = {"Authorization": f"Bearer {access_token}"}
        res = requests.get(url, headers=headers)
    else:
        res = requests.get(url)

    if res.status_code == 200:
        metadata_dict = json.loads(res.text)
        with open(os.path.join(output_dir, f"{analysis_id}.payload.json"), 'w') as o:
            o.write(json.dumps(metadata_dict, indent=2))

        return analysis_id

    else:
        return


def download_data(song_url, score_url, study_id, analysis_id, access_token, output_dir):
    if not access_token:
        sys.exit('Please provide access token as environment variable: ACCESS_TOKEN')

    if not score_url:
        sys.exit('Please provide SCORE server URL')

    profile = 'collab'
    if 'azure' in score_url.lower():
        profile = 'azure'
    elif 'aws' in score_url.lower():
        profile = 'aws'

    download_cmd = f'METADATA_URL={song_url} STORAGE_URL={score_url} ACCESSTOKEN={access_token}'
    download_cmd += f' score-client --profile {profile} download --study-id {study_id} --analysis-id {analysis_id} --output-dir {output_dir}/data'

    proc = subprocess.Popen(
                download_cmd,
                shell=True,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
    stdout, stderr = proc.communicate()

    if proc.returncode:  # error occurred
        print(f"SCORE download failed, more info: {stderr}", file=sys.stderr)
        sys.exit(proc.returncode)


def main():
    """
    Python implementation of tool: legacy-ss-download

    This is auto-generated Python code, please update as needed!
    """

    parser = argparse.ArgumentParser(description='Tool: legacy-ss-download')
    parser.add_argument('-u', '--song-url', type=str, help='SONG (metadata) server URL', required=True)
    parser.add_argument('-r', '--score-url', type=str, help='SCORE (data) server URL')
    parser.add_argument('-s', '--study-id', type=str, help='Study ID', required=True)
    parser.add_argument('-a', '--analysis-id', type=str, help='SONG analysis ID', required=True)
    parser.add_argument('-m', '--metadata-only', action='store_true', help='Download metadata JSON only')
    parser.add_argument('-o', '--output-dir', type=str, help='Output directory', required=True)
    args = parser.parse_args()

    if not os.path.isdir(args.output_dir):
        sys.exit('Error: specified output dir %s does not exist or is not accessible!' % args.output_dir)

    access_token = os.environ.get('ACCESS_TOKEN')

    analysis_id = download_metadata(args.song_url, args.study_id, args.analysis_id, access_token, args.output_dir)
    if analysis_id:
        print(analysis_id)  # stdout for NF to catch the analysisId

        if args.metadata_only:
            sys.exit()

        download_data(args.song_url, args.score_url, args.study_id, args.analysis_id, access_token, args.output_dir)

    else:
        sys.exit(f"Not able to retrieve SONG analysis, study {args.study_id}, analysis_id: {args.analysis_id}")


if __name__ == "__main__":
    main()
