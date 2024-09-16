import os

WEBHOOK_PASSPHRASE = 'setyourpassphrasehere'

DISCORD_LOGS_URL = None
DISCORD_ERR_URL = None
DISCORD_AVATAR_URL = None
DISCORD_STUDY_URL = None
DISCORD_STUDY_AVATAR_URL = None

LEVERAGE_TESTING = 100
RISK_TESTING = 10
API_KEY_TESTING = '18IFa1AXubyRxV778L'
API_SECRET_TESTING = 'WaR4N8SHvVr2Clzm0R939RwQUUITgz9RBbOk'

#please review these settings with bybit api documentation
LEVERAGE_MYBYBITACCOUNT = 50
RISK_MYBYBITACCOUNT = 5

#API_KEY_MYBYBITACCOUNT = 'd76eL3NbVSUqb2zyoS'
#API_SECRET_MYBYBITACCOUNT = 'e2miW7MwIbw0ZVJ85CsrQruXAPoVtAfb2Fnq'
API_KEY_MYBYBITACCOUNT = '18IFa1AXubyRxV778L'
API_SECRET_MYBYBITACCOUNT = 'WaR4N8SHvVr2Clzm0R939RwQUUITgz9RBbOk'

# https://tvbot-79a793c11bdc.herokuapp.com/

# git push heroku main
# heroku restart --app tvbot
# heroku logs --tail --app tvbot

#heroku config:set LEVERAGE_TESTING=100
#heroku config:set RISK_TESTING=your_risk_testing

#heroku config:set API_KEY_TESTING ='UPAFznEo72Yv5FCX1n'
#heroku config:set API_SECRET_TESTING='CTmisiLKyaoRwjp6MGOSs0n2BYHDMuC2G9Rx'

os.environ['HTTP_PROXY'] = 'http://127.0.0.1:8888'
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:8888'
