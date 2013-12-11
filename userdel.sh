#!/usr/bin/env bash
USER=$1
read -s -p "Enter MySQL Password: " PASSWORD
userdel -r $1

echo "DROP USER $USER;" | mysql -u root --password="$PASSWORD"
echo "DROP DATABASE \`$USER.blog\`;" | mysql -u root --password="$PASSWORD"
echo "DELETE FROM skyen.validation_tokens \
WHERE user_id = (select id from skyen.users where username = '$1');" | mysql -u root --password="$PASSWORD"
echo "DELETE FROM skyen.users WHERE username = '$1';" | mysql -u root --password="$PASSWORD"
  
