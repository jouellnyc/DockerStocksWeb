#!/bin/bash

### Switch out Credentials with Dummy line

MG=mongodb.py 
MGD=mongodb.py.dummy
PROD=mongodb.py.prod

if [ x"$1" == x"" ]; then
  echo $0 'msg' or 'done'
  exit
fi

if [ x"$1" == x"done" ]; then
    mv $PROD $MG 
    grep MongoClient $MG
    exit
fi

MSG="$1"
[ -f $MGD ] && rm $MGD
cp $MG $MGD

sed -i s#"$(grep -iEo  "client.*=.*MongoClient.*"  $MG)"#"client = MONGOCLIENTLINE"#g $MGD
grep -l MongoClient $PROD
grep -l MONGOCLIENT $MG

mv $MG $PROD 
mv $MGD $MG

if grep MONGO $MG; then
    echo git add $MG
    echo git commit -m $MSG $MG
    echo git push 
fi
