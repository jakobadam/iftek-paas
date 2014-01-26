#!/usr/bin/env sh
rm -rf /etc/skel/public_html
mkdir  /etc/skel/public_html

rm -rf /tmp/iftek
git clone https://github.com/jakobadam/iftek.git /tmp/iftek
cd /tmp/iftek
git archive master | tar -x -C /etc/skel/public_html
chmod a+w /etc/skel/public_html/blog/conf/config.php
