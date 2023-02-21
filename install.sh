#!/usr/bin/env bash

echo "Going to create songs folder and music database"
[ ! -d "songs" ] && mkdir songs
sqlite3 music <<'END_SQL'
.timeout 2000
CREATE TABLE IF NOT EXISTS songs (uuid varchar(50), album varchar(20), title varchar(20), artist varchar(200),file_name varchar(200));
END_SQL
echo "Done"