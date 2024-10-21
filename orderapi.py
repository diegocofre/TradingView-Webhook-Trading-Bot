import logbot
import json, os, config
from ftxapi import Ftx
from bybitapi import ByBit

exchange = 'SUBACCOUNT_NAME'
leverage = 1.0
risk = 1.0 / 100
api_key = 'API_KEY'
api_secret = 'API_SECRET'


# ================== SET GLOBAL VARIABLES ==================


def global_var(payload):
    global exchange
    global leverage
    global risk
    global api_key
    global api_secret

    exchange = payload['exchange']
    
    leverage = os.environ.get('LEVERAGE', config.LEVERAGE)
    leverage = float(leverage)

    risk = os.environ.get('RISK', config.RISK)
    risk = float(risk) / 100    

    if exchange == 'BYBIT':
        api_key = os.environ.get('BYBIT_API_KEY', config.BYBIT_API_KEY)
        api_secret = os.environ.get('BYBIT_API_SECRET', config.BYBIT_API_SECRET)
    else:
        logbot.logs(">>> Exchange name not found!", True)
        return {
            "success": False,
            "error": "exchange name not found"
        }
           
    return {
        "success": True
    }


# ================== MAIN ==================


def order(payload: dict):
    #   DEFINE GLOBAL VARIABLE
    glob = global_var(payload)
    if not glob['success']:
        return glob
    
    init_var = {
        #'exchange': exchange,
        'leverage': leverage,
        'risk': risk,
        'api_key': api_key,
        'api_secret': api_secret
    }
    exchange = payload['exchange']
    
    #   SET EXCHANGE CLASS
    exchange_api = None
    try:
        if exchange.upper() == 'FTX':
            exchange_api = Ftx(init_var)
        elif exchange.upper() == 'BYBIT':
            exchange_api = ByBit(init_var)
    except Exception as e:
        logbot.logs('>>> /!\ An exception occured : {}'.format(e), True)
        return {
            "success": False,
            "error": str(e)
        }

    logbot.logs('>>> Exchange : {}'.format(exchange))
    logbot.logs('>>> Subaccount : {}'.format(exchange))

    #   FIND THE APPROPRIATE TICKER IN DICTIONNARY
    ticker = ""
    if exchange.upper() == 'BYBIT':
        ticker = payload['ticker']
    else:
        with open('tickers.json') as json_file:
            tickers = json.load(json_file)
            try:
                ticker = tickers[exchange.lower()][payload['ticker']]
            except Exception as e:
                logbot.logs('>>> /!\ An exception occured : {}'.format(e), True)
                return {
                    "success": False,
                    "error": str(e)
                }
    logbot.logs(">>> Ticker '{}' found".format(ticker))

    #   ALERT MESSAGE CONDITIONS
    if payload['message'] == 'entry':
        logbot.logs(">>> Order message : 'entry'")
        exchange_api.exit_position(ticker)
        orders = exchange_api.entry_position(payload, ticker)
        return orders

    elif payload['message'] == 'exit':
        logbot.logs(">>> Order message : 'exit'")
        exit_res = exchange_api.exit_position(ticker)
        return exit_res

    elif payload['message'][-9:] == 'breakeven':
        logbot.logs(">>> Order message : 'breakeven'")
        breakeven_res = exchange_api.breakeven(payload, ticker)
        return breakeven_res
    
    elif payload['message']== 'pivot':
        logbot.logs(">>> Order message : 'pivot'")
        pivot_res = exchange_api.entry_spot_position(payload, ticker )
        return pivot_res
    
    elif payload['message']== 'karma':
        logbot.logs(">>> Order message : 'karma'")
        r = exchange_api.get_balance()
        return str(r)
        
    else:
        logbot.logs(f">>> Order message : '{payload['message']}'")

    return {
        "message": payload['message']
    }
