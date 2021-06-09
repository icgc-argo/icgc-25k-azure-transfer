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

nextflow.enable.dsl = 2
version = '0.1.0'  // package version

// universal params go here, change default value as needed
params.cpus = 1
params.mem = 1  // GB
params.publish_dir = ""  // set to empty string will disable publishDir

// tool specific parmas go here, add / change as needed
params.cleanup = true

params.study_id = "TEST-PR"
params.analysis_id = "9940db0f-c100-496a-80db-0fc100d96ac1"

params.api_token = ""
params.download_api_token = ""
params.upload_api_token = ""

params.song_cpus = 1
params.song_mem = 1  // GB
params.score_cpus = 1
params.score_mem = 1  // GB
params.score_transport_mem = 1  // GB

params.download_song_url = "https://song.rdpc-qa.cancercollaboratory.org"
params.download_score_url = "https://score.rdpc-qa.cancercollaboratory.org"

params.upload_song_url = "https://song.azure-dev.overture.bio"
params.upload_score_url = "https://score.azure-dev.overture.bio"


download_params = [
    *:params,
    'song_url': params.download_song_url,
    'score_url': params.download_score_url,
    'api_token': params.download_api_token ?: params.api_token
]

upload_params = [
    *:params,
    'song_url': params.upload_song_url,
    'score_url': params.upload_score_url,
    'api_token': params.upload_api_token ?: params.api_token
]


include { SongScoreDownload as Download } from './wfpr_modules/github.com/icgc-argo/nextflow-data-processing-utility-tools/song-score-download@2.6.2/main.nf' params(download_params)
include { legacySongSubmit as Submit } from './wfpr_modules/github.com/icgc-argo/icgc-25k-azure-transfer/legacy-song-submit@0.1.0/main.nf' params(upload_params)
include { SongScoreUpload as Upload } from './wfpr_modules/github.com/icgc-argo/nextflow-data-processing-utility-tools/song-score-upload@2.7.0/main.nf' params(upload_params)


// please update workflow code as needed
workflow AzureTransferWf {
  take:
    study_id
    analysis_id

  main:
    Download(
      study_id,
      analysis_id
    )

    Submit(
      params.upload_song_url,
      study_id,
      Download.out.analysis_json
    )

    Upload(
      study_id,
      file('NO_FILE'),
      Download.out.files.collect(),
      Submit.out
    )
}


// this provides an entry point for this main script, so it can be run directly without clone the repo
// using this command: nextflow run <git_acc>/<repo>/<pkg_name>/<main_script>.nf -r <pkg_name>.v<pkg_version> --params-file xxx
workflow {
  AzureTransferWf(
    params.study_id,
    params.analysis_id
  )
}
