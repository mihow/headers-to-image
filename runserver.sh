#! /bin/bash

source env/bin/activate

python -c "import sys; assert(sys.version_info[0] < 3)" || { echo 'Only Python 2.X is supported' ; exit 1; }

export FLASK_DEBUG=True
export FLASK_APP=app.py

export AWS_PROFILE=michael

flask run
