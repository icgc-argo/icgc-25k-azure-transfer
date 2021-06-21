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

permissible_studies = [
    'BOCA-UK',
    'BRCA-UK',
    'BTCA-SG',
    'CLLE-ES',
    'CMDI-UK',
    'ESAD-UK',
    'LAML-KR',
    'LICA-FR',
    'LINC-JP',
    'LIRI-JP',
    'MELA-AU',
    'ORCA-IN',
    'OV-AU',
    'PACA-AU',
    'PACA-CA',
    'PAEN-AU',
    'PAEN-IT',
    'PRAD-CA',
    'PRAD-UK',
    'RECA-EU'
]

def permissibleStudy(study_id){
    if (study_id in permissible_studies) {
        return study_id
    } else {
        exit 1, "Not a permitted study: " + study_id
    }
}
