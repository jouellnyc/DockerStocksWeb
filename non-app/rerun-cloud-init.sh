#!/bin/bash
rm -f /var/log/cloud-init.log \
&& rm -Rf /var/lib/cloud/* \
&& cloud-init -d init \
&& cloud-init -d modules --mode final
