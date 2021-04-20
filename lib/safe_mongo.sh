#!/bin/bash

### Switch out Credentials with Dummy line

MG=mongodb.py 
MGD=mongodb.py.dummy
PROD=mongodb.py.prod

if [ x"$1" == x"done" ]; then
    mv $PROD $MG 
    exit
fi

[ -f $MGD ] && rm $MGD
cp $MG $MGD

sed -i s#"$(grep -iEo  "client.*=.*MongoClient.*"  $MG)"#"client = MONGOCLIENTLINE"#g $MGD
diff $MG $MGD

mv $MG $PROD 
mv $MGD $MG

if grep MONGO $MG; then
    echo git add $MG
    echo git commit -m \"\"  $MG
    echo git push 
fi
