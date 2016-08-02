#! /bin/sh

cd `dirname $0`

# Pythonのパス
PYTHON_EXE=/usr/local/bin/python
# 起動スクリプト
TARGET_FILE=server.py
# このスクリプトの設置場所
SCRIPT_DIR=$(cd $(dirname $(readlink -f $0 || echo $0));pwd -P)
# 起動パラメータ
#START_PARAM=--log_file_prefix=${SCRIPT_DIR}/log/tornado.log
START_PARAM=''

# 実行
$PYTHON_EXE $TARGET_FILE $START_PARAM

## 起動方法
##nohup ./Start.sh > log/out.log 2> log/err.log < /dev/null &

