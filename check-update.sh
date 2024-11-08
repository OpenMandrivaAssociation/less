#!/bin/sh
#set -x
curl -s "https://www.greenwoodsoftware.com/less/" |grep 'The current released version is' |sed -e 's,.*-,,;s,\..*,,'

