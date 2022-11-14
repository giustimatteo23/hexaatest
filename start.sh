#!/bin/bash

if (( ${DEVMODE} == "TRUE" ))
then {
   echo "We are in developer mode... pulling newest source with git..."

   cd /Python-3.10.5
   rm -r hexaatest
   git clone https://github.com/giustimatteo23/hexaatest.git
   cd hexaatest
   rm Dockerfile*
   pip install -r requirements.txt &>/dev/null
}
else {
   echo "DEVMODE env var is not true. We are in production mode... not pulling newest source"
}
fi

python3.9 main.py
