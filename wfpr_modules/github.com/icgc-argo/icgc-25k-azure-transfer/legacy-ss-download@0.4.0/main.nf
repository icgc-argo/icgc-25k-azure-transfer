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

/********************************************************************/
/* this block is auto-generated based on info from pkg.json where   */
/* changes can be made if needed, do NOT modify this block manually */
nextflow.enable.dsl = 2
version = '0.4.0'

container = [
    'ghcr.io': 'ghcr.io/icgc-argo/icgc-25k-azure-transfer.legacy-ss-download'
]
default_container_registry = 'ghcr.io'
/********************************************************************/


// universal params go here
params.container_registry = ""
params.container_version = ""
params.container = ""

params.cpus = 2
params.mem = 2  // GB
params.transport_mem = 1 // GB
params.publish_dir = ""  // set to empty string will disable publishDir

params.max_retries = 3  // set to 0 will disable retry
params.first_retry_wait_time = 60  // in seconds

// tool specific parmas go here, add / change as needed
params.api_token = ""
params.song_url = "https://song.cancercollaboratory.org"
params.score_url = "https://storage.cancercollaboratory.org"
params.study_id = "PACA-CA"
params.analysis_id = "dcf87a9f-2fdf-415d-9987-f41096849a60"
params.metadata_only = null


process legacySsDownload {
  container "${params.container ?: container[params.container_registry ?: default_container_registry]}:${params.container_version ?: version}"
  publishDir "${params.publish_dir}/${task.process.replaceAll(':', '_')}", mode: "copy", enabled: params.publish_dir

  cpus params.cpus
  memory "${params.mem} GB"

  maxRetries params.max_retries
  errorStrategy {
    if (params.max_retries && task.attempt <= params.max_retries && !(task.exitStatus in [130, 137])) {  // assume intentional kill yields 130, 137 exitcode
      sleep(Math.pow(2, task.attempt) * params.first_retry_wait_time * 1000 as long);  // backoff time increases exponentially before each retry
      return 'retry'
    } else {
      return 'finish'  // when max_retries is 0 or it's the last attempt, return 'finish' so other running / pending tasks will not be cancelled
    }
  }

  input:  // input, make update as needed
    val study_id
    val analysis_id
    env ACCESS_TOKEN

  output:  // output, make update as needed
    path "output_dir/*.payload.json", emit: payload_json
    path "output_dir/data/*", emit: data_file optional true

  script:
    // add and initialize variables here as needed
    arg_score_url = params.score_url ? "-r ${params.score_url}" : ""
    arg_metadata_only = params.metadata_only ? "-m" : ""

    """
    export TRANSPORT_PARALLEL=${params.cpus}
    export TRANSPORT_MEMORY=${params.transport_mem}

    mkdir -p output_dir

    main.py \
      -u ${params.song_url} \
      -s ${study_id} \
      -a ${analysis_id} \
      -o output_dir ${arg_score_url} ${arg_metadata_only}

    """
}


// this provides an entry point for this main script, so it can be run directly without clone the repo
// using this command: nextflow run <git_acc>/<repo>/<pkg_name>/<main_script>.nf -r <pkg_name>.v<pkg_version> --params-file xxx
workflow {
  legacySsDownload(
    params.study_id,
    params.analysis_id,
    params.api_token
  )
}
