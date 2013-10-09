#!/usr/bin/env bash
USER=$1
read -s -p "Enter MySQL Password: " PASSWORD
userdel -r $1
sql="DROP USER $USER;"
echo $sql | mysql -u root --password="$PASSWORD"
sql="DROP DATABASE \`$USER.blog\`;"
echo $sql | mysql -u root --password="$PASSWORD"
sql="DELETE FROM skyen.users WHERE username = '$1';"
echo $sql | mysql -u root --password="$PASSWORD"
  
