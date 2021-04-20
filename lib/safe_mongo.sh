#!/bin/bash

### Switch out Credentials with Dummy line

MG=mongodb.py 
MGD=mongodb.py.dummy

rm $MGD
cp $MG $MGD

sed -i s#"$(grep -iEo  "client.*=.*MongoClient.*"  $MG)"#"client = MONGOCLIENTLINE"#g $MGD
diff $MG $MGD
