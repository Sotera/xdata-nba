#!/bin/bash

### USER DEFINED VARIABLES ###
HDFS_STAGE_DIR=/tmp/hive/data/staged/
SCRIPT_DIR=.
LOCAL_DATA_DIR=.
HIVE_DATABASE=xdata_nba
PAUSE=0
#
# The file_table_mapping array stores a mapping between
# the data file name and the table it maps to. This
# is required for the loading of data into Hive
#
declare -a FILE_TABLE_MAPPING=('team_data.hive:team' 'game_players.hive:game_players' 'game_commentary.hive:game_commentary' 'game_comments.hive:game_comments' 'game_stats.hive:game_stats' 'game_player_stats.hive:game_player_stats' 'game_play_by_play.hive:game_play_by_play')

### CONSTANTS DEFINITIONS - FOR COLORS ###
bldred=$(tput bold)$(tput setaf 1)
bldgreen=$(tput bold)$(tput setaf 2)
bldcyan=$(tput bold)$(tput setaf 6)
bldmag=$(tput bold)$(tput setaf 5)
txtrst=$(tput sgr0)

### PROGRAM DEFINED VARIABLES ###
CREATE_HIVE_TABLES=false
STAGE_HIVE_DATA=false
LOAD_HIVE_DATA=false
OVERWRITE=false
PRECANNED=false

#
# DISPLAY USAGE MESSAGE
#
usage() {
  cat <<EOF
  usage: $0 options

  This script loads data into Hive tables

  OPTIONS:
  -h shows this message
  -d specifies that you wish to drop and recreate the Hive tables
  -s specifies that you wish to stage hive data files into HDFS
  -o specifies that you wish to overwrite existing staged data in HDFS
  -l specifies that you wish to load hive data from HDFS to HIVE
  -a specifies that you wish to exercise all options excluding -p
  -p executes the 'pre-canned' deployment options
EOF
}

#
# READ COMMAND LINE ARGUMENTS
#
while getopts "dslahop" OPTION
do
  case ${OPTION} in
    h)
      usage
      exit 1
      ;;
    d)
      CREATE_HIVE_TABLES=true
      ;;
    s)
      STAGE_HIVE_DATA=true
      ;;
    o)
      OVERWRITE=true
      ;;
    l)
      LOAD_HIVE_DATA=true
      ;;
    a)
      CREATE_HIVE_TABLES=true
      STAGE_HIVE_DATA=true
      LOAD_HIVE_DATA=true
      OVERWRITE=true
      ;;
    p)
      CREATE_HIVE_TABLES=true
      STAGE_HIVE_DATA=true
      LOAD_HIVE_DATA=true
      OVERWRITE=true
      PRECANNED=true
      PRECANNED_DATA_INPUT=./data/
      PRECANNED_DATA_OUTPUT=./output/
  esac
done

echo ${bldcyan}'----- Starting XData NBA Load -----'${txtrst}
 
#
# CREATE TABLES
#
if ${CREATE_HIVE_TABLES} ; then
  echo ${bldmag}'Dropping Hive Tables'${txtrst}
  $(hive -f ${SCRIPT_DIR}/drop_xdata_nba_tables.hql)

  echo ${bldmag}'Creating Hive Tables'${txtrst}
  $(hive -f ${SCRIPT_DIR}/create_xdata_nba.hql)
fi

#
# UNPACK PRECANNED DATASETS
#
if ${PRECANNED} ; then
  echo ${bldmag}'Unpacking Precanned Data'${txtrst}
  if [ ! -d "$LOCAL_DATA_DIR" ]; then
    mkdir -p $LOCAL_DATA_DIR
  fi
  for z in ${PRECANNED_DATA_INPUT}*.zip;
  do
    echo $z
    unzip -oq ${z} -d ${PRECANNED_DATA_OUTPUT}
  done
  echo ${bldmag}'Transforming Data'${txtrst}
  cd com/soteradefense/xdata/
  for p in transformer*.py;
  do
    python ${p}
  done
  cd ../../../
fi

#
# STAGE HIVE DATA
#
if ${STAGE_HIVE_DATA} ; then
  echo ${bldmag}'Staging Hive Data'${txtrst}
  $(hdfs dfs -test -d ${HDFS_STAGE_DIR})
  status=$?
  # CHECK TO SEE IF DIRECTORY EXISTS, IF NOT CREATE IT
  if [ $status -ne 0 ]; then 
   echo ${bldred}HDFS directory '${HDFS_STAGE_DIR}' not found. Creating it now.${txtrst}
   $(hdfs dfs -mkdir -p ${HDFS_STAGE_DIR}) 
  fi
  # COPY FILES OVER, DELETE EXISTING IF 'OVERWRITE' IS TRUE
  FILES=${LOCAL_DATA_DIR}/*.hive
  for f in $FILES
  do
    filename=$(basename ${f})
    # CHECK IF USER WANTS TO OVERWRITE EXISTING FILE
    if ${OVERWRITE} ; then
      $(hdfs dfs -test -e ${HDFS_STAGE_DIR}${filename})
      status=$?
      if [ $status -eq 0 ]; then
        echo ${bldred}Removing current file \'${filename}\' from HDFS${txtrst}
        cmd=${HDFS_STAGE_DIR}${filename}
        ignore_result=$(hdfs dfs -rm ${cmd})
      fi
    fi
    echo ${bldgreen}Writing \'${filename}\' to HDFS${txtrst}
    $(hdfs dfs -put $f ${HDFS_STAGE_DIR})
  done
  echo ${bldmag}Pausing for ${PAUSE} seconds to allow copy to complete in cluster${txtrst}
  sleep ${PAUSE}
fi

#
# LOAD HIVE TABLES
#
if ${LOAD_HIVE_DATA} ; then
  echo ${bldmag}'Loading Hive Data'${txtrst}
  for f in ${FILE_TABLE_MAPPING[@]}
  do
    filename=$(echo $f | cut -f1 -d:)
    tablename=$(echo $f | cut -f2 -d:)
    $(hdfs dfs -test -e ${HDFS_STAGE_DIR}${filename})
    status=$?
    if [ $status -eq 0 ]; then
      echo ${bldgreen}Loading data from ${filename} into table ${tablename}${txtrst}
      ignore_results=$(hive --database ${HIVE_DATABASE} -e "LOAD DATA INPATH '${HDFS_STAGE_DIR}${filename}' OVERWRITE INTO TABLE ${tablename};")
    else 
      echo ${bldred}File \'${filename}\' not found in HDFS dir \'${HDFS_STAGE_DIR}\'${txtrst}
    fi
  done
fi

#
# WRAP UP
#
if ! ${STAGE_HIVE_DATA} && ! ${CREATE_HIVE_TABLES} && ! ${LOAD_HIVE_DATA} ; then
  usage
  echo ${bldred}  -- The default behavior is to do nothing --${txtrst}
fi

echo ${bldcyan}'----- Completed XData NBA Load -----'${txtrst}
