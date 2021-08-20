#!/usr/bin/env nextflow

/*
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
*/

/*
 This is an auto-generated checker workflow to test the generated main template workflow, it's
 meant to illustrate how testing works. Please update to suit your own needs.
*/

nextflow.enable.dsl = 2
version = '0.12.0'

// universal params
params.publish_dir = ""
params.container = ""
params.container_registry = ""
params.container_version = ""

params.max_retries = 0  // set to 0 will disable retry
params.first_retry_wait_time = 60  // in seconds

// tool specific parmas go here, add / change as needed
params.cleanup = true

params.study_id = "TEST-PR"
params.analysis_id = "9940db0f-c100-496a-80db-0fc100d96999"

params.api_token = ""
params.download_api_token = ""
params.upload_api_token = ""

params.transport_mem = 1

params.download_cpus = null
params.download_mem = null
params.download_transport_mem = null
params.upload_cpus = null
params.upload_mem = null
params.upload_transport_mem = null

params.ignore_sid_mismatch = false

params.download_song_url = "https://song.cancercollaboratory.org"
params.download_score_url = "https://storage.cancercollaboratory.org"

params.upload_song_url = "https://song.azure-dev.overture.bio"
params.upload_score_url = "https://score.azure-dev.overture.bio"


include { AzureTransferWf } from '../main'


workflow {
  AzureTransferWf(
    params.study_id,
    params.analysis_id,
    params.api_token
  )
}
