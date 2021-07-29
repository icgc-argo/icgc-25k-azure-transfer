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
version = '0.11.0'

// universal params go here, change default value as needed
params.cpus = 1
params.mem = 1  // GB
params.publish_dir = ""  // set to empty string will disable publishDir

params.max_retries = 3  // set to 0 will disable retry
params.first_retry_wait_time = 60  // in seconds

// tool specific parmas go here, add / change as needed
params.cleanup = true

params.study_id = "TEST-PR"
params.analysis_id = "9940db0f-c100-496a-80db-0fc100d96999"

params.api_token = ""
params.download_api_token = ""
params.upload_api_token = ""

params.local_dir = "NO_DIR"  // optional, when specified download and upload will be performed in a single step to make use of local directory instead of NFS
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


download_params = [
    *:params,
    'cpus': params.download_cpus ?: params.cpus,
    'mem': params.download_mem ?: params.mem,
    'song_url': params.download_song_url,
    'score_url': params.download_score_url,
    'api_token': params.download_api_token ?: params.api_token,
    'transport_mem': params.download_transport_mem ?: params.transport_mem
]

submit_params = [
    *:params,
    'song_url': params.upload_song_url,
    'api_token': params.upload_api_token ?: params.api_token
]

upload_params = [
    *:params,
    'cpus': params.upload_cpus ?: params.cpus,
    'mem': params.upload_mem ?: params.mem,
    'song_url': params.upload_song_url,
    'score_url': params.upload_score_url,
    'api_token': params.upload_api_token ?: params.api_token,
    'transport_mem': params.upload_transport_mem ?: params.transport_mem
]

transfer_params = [
    *:params,
    'cpus': params.download_cpus ?: params.cpus,
    'mem': params.download_mem ?: params.mem,
    'download_song_url': params.download_song_url,
    'download_score_url': params.download_score_url,
    'upload_song_url': params.upload_song_url,
    'upload_score_url': params.upload_score_url,
]


include { permissibleStudy } from './local_modules/permissible-study.nf'
include { legacySsDownload as DownloadMeta } from './wfpr_modules/github.com/icgc-argo/icgc-25k-azure-transfer/legacy-ss-download@0.4.0/main.nf' params([*:download_params, 'metadata_only': true, 'cpus': params.cpus, 'mem': params.mem])
include { legacySongSubmit as Submit } from './wfpr_modules/github.com/icgc-argo/icgc-25k-azure-transfer/legacy-song-submit@0.7.0/main.nf' params(submit_params)
include { scoreDataTransfer as Transfer } from './wfpr_modules/github.com/icgc-argo/icgc-25k-azure-transfer/score-data-transfer@0.6.0/main.nf' params(transfer_params)
include { legacySsDownload as DownloadData } from './wfpr_modules/github.com/icgc-argo/icgc-25k-azure-transfer/legacy-ss-download@0.4.0/main.nf' params(download_params)
include { legacySsUpload as Upload } from './wfpr_modules/github.com/icgc-argo/icgc-25k-azure-transfer/legacy-ss-upload@0.5.0/main.nf' params(upload_params)
include { cleanupWorkdir as cleanup } from './wfpr_modules/github.com/icgc-argo/data-processing-utility-tools/cleanup-workdir@1.0.0/main.nf'


// please update workflow code as needed
workflow AzureTransferWf {
  take:
    study_id
    analysis_id
    api_token

  main:
    study_id = permissibleStudy(study_id)

    DownloadMeta(
      study_id,
      Channel.from(analysis_id),
      api_token
    )

    Submit(
      study_id,
      DownloadMeta.out.payload_json,
      api_token
    )

    if (params.local_dir == 'NO_DIR') {  // no local dir set
      DownloadData(
        study_id,
        Submit.out,
        api_token
      )

      Upload(
        study_id,
        Submit.out,
        DownloadData.out.data_file.collect(),
        api_token
      )
    } else {  // with local dir, perform download and upload together in one step
      Transfer(
        study_id,
        Submit.out,
        api_token
      )
    }

    // assume no cleanup is needed when local_dir is used, for
    // example k8s emptyDir: https://kubernetes.io/docs/concepts/storage/volumes/#emptydir
    if (params.cleanup && params.local_dir == 'NO_DIR') {
      cleanup(
        DownloadData.out.data_file.concat(DownloadMeta.out.payload_json).collect(),
        Upload.out.analysis_id.collect()
      )
    }
}


// this provides an entry point for this main script, so it can be run directly without clone the repo
// using this command: nextflow run <git_acc>/<repo>/<pkg_name>/<main_script>.nf -r <pkg_name>.v<pkg_version> --params-file xxx
workflow {
  AzureTransferWf(
    params.study_id,
    params.analysis_id,
    params.api_token
  )
}
