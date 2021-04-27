#!/bin/bash

### Switch out Credentials with Dummy line

MG=mongodb.py 
MGB=mongodb.py.bak
PROD=mongodb.py.prod

if [ x"$1" == x"" ]; then
  echo $0 'msg' or 'done'
  exit
fi

if [ x"$1" == x"done" ]; then
    mv $PROD $MG 
    grep -q MongoClient $MG && echo 'Back to Working Config' 
    exit
fi

MSG="$1"
cp $MG $PROD
cp $MG $MGB

sed -i s#"$(grep -iEo  "client.*=.*MongoClient.*"  $MG)"#"client = MONGOCLIENTLINE"#g $MGB
mv $MGB $MG

if grep MONGO $MG; then
    echo git add $MG
    echo git commit -m $MSG $MG
    echo git push 
fi
