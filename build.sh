#!/bin/bash
echo "---------------------"
echo "Building project..."
set -e
date

start_time=$(date +%s)

docker build -t nginx:production .docker/nginx
docker build -t flask:production .


elapsed=$(($(date +%s) - start_time))
echo ""
echo "---------------------"
echo "ALL DONE. Build finished in $elapsed seconds"
date
echo "---------------------"
echo ""
