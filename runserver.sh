#! /bin/bash

source env/bin/activate

python -c "import sys; assert(sys.version_info[0] < 3)" || { echo 'Only Python 2.X is supported' ; exit 1; }

export FLASK_DEBUG=True
export FLASK_APP=app.py

# This is now done within app.py
# if [ ! -f .env ]
# then
#     export $(cat .env | xargs)
# fi

flask run
