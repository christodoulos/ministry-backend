#!/bin/bash
rsync -avz --delete apografi_sync*.py psped_sync*.py apografi_check*.py count_distinct.py requirements.txt src wsgi.py ypes-backend:flask
ssh ypes-backend 'source ~/flask/venv/bin/activate && pip install -r ~/flask/requirements.txt'
ssh oper@lola 'sudo supervisorctl reload'
