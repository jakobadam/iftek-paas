#!/usr/bin/env bash
USER=$1
PASSWORD="foobar"
userdel -r $1
sql="DROP USER $USER; DROP DATABASE \`$USER.blog\`;"
echo $sql | mysql -u root --password="$PASSWORD"
sql="DELETE FROM skyen.users WHERE username = '$1';"
echo $sql | mysql -u root --password="$PASSWORD"
  
