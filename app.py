import logbot
import json, os, config
from flask import Flask, request
from orderapi import order

app = Flask(__name__)

@app.route("/")
def index():
    return app.send_static_file('index.html')

@app.route("/karma")
def karma():
    logbot.logs("========= KARMA =========")         
    data = {"message": "karma", "exchange": "BYBIT", "ticker": ""}      
    r = order(data)
    return r

@app.route("/tradingview-to-webhook-order", methods=['POST'])
def tradingview_webhook():

    logbot.logs("========= STRATEGY =========")
    
    data = json.loads(request.data)

    webhook_passphrase = os.environ.get('WEBHOOK_PASSPHRASE', config.WEBHOOK_PASSPHRASE)

    if 'passphrase' not in data.keys():
        logbot.logs(">>> /!\ No passphrase entered", True)
        return {
            "success": False,
            "message": "no passphrase entered"
        }

    if data['passphrase'] != webhook_passphrase:
        logbot.logs(">>> /!\ Invalid passphrase", True)
        return {
            "success": False,
            "message": "invalid passphrase"
        }

    orders = order(data)
    print(orders)
    return orders

@app.route("/tradingview-to-discord-study", methods=['POST'])
def discord_study_tv():

    logbot.logs("========== STUDY ==========")
    
    data = json.loads(request.data)

    webhook_passphrase = os.environ.get('WEBHOOK_PASSPHRASE', config.WEBHOOK_PASSPHRASE)

    if 'passphrase' not in data.keys():
        logbot.logs(">>> /!\ No passphrase entered", True)
        return {
            "success": False,
            "message": "no passphrase entered"
        }

    if data['passphrase'] != webhook_passphrase:
        logbot.logs(">>> /!\ Invalid passphrase", True)
        return {
            "success": False,
            "message": "invalid passphrase"
        }
    del data["passphrase"]

    try:
        chart_url = data["chart_url"]
        del data["chart_url"]
    except KeyError:
        logbot.logs(">>> /!\ Key 'chart_url' not found", True)

    logbot.study_alert(json.dumps(data), chart_url)

    return {
        "success": True
    }