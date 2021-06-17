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
    'ghcr.io': 'ghcr.io/icgc-argo/icgc-25k-azure-transfer.legacy-ss-upload'
]
default_container_registry = 'ghcr.io'
/********************************************************************/


// universal params go here
params.container_registry = ""
params.container_version = ""
params.container = ""

params.cpus = 2
params.mem = 2  // GB
params.publish_dir = ""  // set to empty string will disable publishDir


// tool specific parmas go here, add / change as needed
params.transport_mem = 1 // GB
params.api_token = ""
params.song_url = "https://song.azure-dev.overture.bio"
params.score_url = "https://score.azure-dev.overture.bio"
params.study_id = "PACA-CA"
params.analysis_id = "dcf87a9f-2fdf-415d-9987-f41096849a60"
params.data_files = []  // required


process legacySsUpload {
  container "${params.container ?: container[params.container_registry ?: default_container_registry]}:${params.container_version ?: version}"
  publishDir "${params.publish_dir}/${task.process.replaceAll(':', '_')}", mode: "copy", enabled: params.publish_dir

  cpus params.cpus
  memory "${params.mem} GB"

  input:  // input, make update as needed
    val study_id
    val analysis_id
    path data_files

  output:
    stdout emit: analysis_id

  script:
    // add and initialize variables here as needed
    accessToken = params.api_token ? params.api_token : "`cat /tmp/rdpc_secret/secret`"

    """
    export ACCESS_TOKEN=${accessToken}
    export TRANSPORT_PARALLEL=${params.cpus}
    export TRANSPORT_MEMORY=${params.transport_mem}

    main.py \
      -u ${params.song_url} \
      -r ${params.score_url} \
      -s ${study_id} \
      -a ${analysis_id} \
      -d ${data_files}

    echo -n ${analysis_id}
    """
}


// this provides an entry point for this main script, so it can be run directly without clone the repo
// using this command: nextflow run <git_acc>/<repo>/<pkg_name>/<main_script>.nf -r <pkg_name>.v<pkg_version> --params-file xxx
workflow {
  data_files = Channel.fromPath(params.data_files)

  legacySsUpload(
    params.study_id,
    params.analysis_id,
    data_files.collect()
  )
}
