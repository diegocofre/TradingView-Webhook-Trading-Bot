import os

WEBHOOK_PASSPHRASE = 'motdue2024'

DISCORD_LOGS_URL = None
DISCORD_ERR_URL = None
DISCORD_AVATAR_URL = None
DISCORD_STUDY_URL = None
DISCORD_STUDY_AVATAR_URL = None
LEVERAGE = 50
RISK = 5

BYBIT_API_KEY = 'MJAgbqRcIuvABByKYM' 
BYBIT_API_SECRET = 'QE6Sx0vroEoANrhm6BzRzvZ4fXNzrZrbDQLc'

# https://tvwebhook2-179710bde712.herokuapp.com

#heroku config:set LEVERAGE=50
#heroku config:set RISK=5
#heroku config:set BYBIT_API_KEY=MJAgbqRcIuvABByKYM
#heroku config:set BYBIT_API_SECRET=QE6Sx0vroEoANrhm6BzRzvZ4fXNzrZrbDQLc


# git push heroku main
# heroku restart --app tdwebhook2
# heroku logs --tail --app tdwebhook2



#os.environ['HTTP_PROXY'] = 'http://127.0.0.1:8888'
#os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:8888'


#DEPLOY AWS
# eb init -p python-3.12 tvwebhook2410 --region sa-east-1
# eb create tvwh-env2
# aws elasticbeanstalk update-environment --environment-name tvwh-env --option-settings Namespace=aws:autoscaling:launchconfiguration,OptionName=IamInstanceProfile,Value=aws-elasticbeanstalk-ec2-role


#DEPLOY GCLOUD
#gcloud config set project tvwebhook2
#gcloud app create --region=europe-west2

#gcloud projects add-iam-policy-binding tvwebhook2 --member="serviceAccount:tvwebhook2@appspot.gserviceaccount.com" --role="roles/storage.admin"

#gcloud config set compute/region europe-west2
#gcloud config list

#gcloud app deploy
#gcloud app logs tail -s default

#https://tvwebhook-438923.ue.r.appspot.com/
#https://tvwebhook-438923.ue.r.appspot.com/tradingview-to-webhook-order