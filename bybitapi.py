import logbot
from pybit.unified_trading import HTTP
import json
import os
from flask import Flask, request

app = Flask(__name__)

class ByBit:
    def __init__(self, var: dict):
        #self.subaccount_name = var['subaccount_name']
        self.leverage = var['leverage']
        self.risk = var['risk']
        self.api_key = var['api_key']
        self.api_secret = var['api_secret']

    # =============== SIGN, POST AND REQUEST ===============

    def _try_request(self, method: str, **kwargs):
        session = HTTP(testnet=True,api_key=self.api_key, api_secret=self.api_secret)
        category = kwargs.get('category','linear')
        try:
            if method == 'get_wallet_balance':
                req = session.get_wallet_balance(accountType="UNIFIED", coin=kwargs.get('coin'))
            elif method == 'my_position':
                req = session.get_positions(category= category, symbol=kwargs.get('symbol'))
            elif method == 'place_active_order':
                order_params = {
                    "category": category ,
                    "symbol": kwargs.get('symbol'),
                    "side": kwargs.get('side'),
                    "orderType": kwargs.get('order_type'),
                    "qty": kwargs.get('qty'),
                    "timeInForce": kwargs.get('time_in_force'),
                    "reduceOnly": kwargs.get('reduce_only'),
                    "closeOnTrigger": kwargs.get('close_on_trigger')
                }
                if 'price' in kwargs:
                    order_params['price'] = kwargs['price']
                if 'stop_loss' in kwargs:
                    order_params['stopLoss'] = kwargs['stop_loss']
                
                req = session.place_order(**order_params)
            elif method == 'place_conditional_order':
                req = session.place_order(category=category, symbol=kwargs.get('symbol'),
                                                      side=kwargs.get('side'), order_type=kwargs.get('order_type'),
                                                      qty=kwargs.get('qty'), price=kwargs.get('price'),
                                                      basePrice=kwargs.get('base_price'), 
                                                      trigger_price=kwargs.get('stop_px'),
                                                      triggerBy=kwargs.get('trigger_by'), 
                                                      timeInForce=kwargs.get('time_in_force'),
                                                      reduceOnly=kwargs.get('reduce_only'), 
                                                      closeOnTrigger=kwargs.get('close_on_trigger'))
            elif method == 'cancel_all_active_orders':
                req = session.cancel_all_orders(category=category, symbol=kwargs.get('symbol'))
            elif method == 'set_trading_stop':
                req = session.set_trading_stop(category=category, symbol=kwargs.get('symbol'), 
                                               side=kwargs.get('side'), stopLoss=kwargs.get('stop_loss'))
            elif method == 'query_symbol':
                req = session.get_instruments_info(category=category)
            elif method == 'get_tickers':
                req = session.get_tickers(category=category, symbol=kwargs.get('symbol'))  
        except Exception as e:
            logbot.logs('>>> /!\ An exception occurred: {}'.format(e), True)
            return {
                "success": False,
                "error": str(e)
            }
        if req['retCode']:
            logbot.logs('>>> /!\ {}'.format(req['retMsg']), True)
            return {
                    "success": False,
                    "error": req['retMsg']
                }
        else:
            req['success'] = True
        return req

    # ================== UTILITY FUNCTIONS ==================

    def _rounded_size(self, size, qty_step):
        step_size = round(float(size) / qty_step) * qty_step
        if isinstance(qty_step, float):
            decimal = len(str(qty_step).split('.')[1])
            return round(step_size, decimal)
        return step_size
    
    def _parse_ticker(self, ticker, side=None):
        parts = ticker.split('-')
        if side != None: side = side.capitalize()  
        if len(parts) != 2:
            raise ValueError(f"Invalid ticker format: {ticker}")
        
        class TickerInfo:
            def __init__(self, symbol, buy=None, sell=None, side=None):
                self.symbol = symbol
                self.buy = buy
                self.sell = sell
                self.side = side
        
        if side is None:
            return TickerInfo(symbol=parts[0] + parts[1])
        elif side == 'Buy':
            return TickerInfo(symbol=parts[0] + parts[1], buy=parts[0], sell=parts[1], side=side)
        elif side == 'Sell':
            return TickerInfo(symbol=parts[0] + parts[1], buy=parts[1], sell=parts[0], side=side)
        else:
            raise ValueError(f"Invalid side value: {side}")
    
    # ================== ORDER FUNCTIONS ==================

    def entry_spot_position(self, ticker, side):
        orders = []
        tkinfo = self._parse_ticker(ticker, side) 

        r = self._try_request('get_wallet_balance', coin=tkinfo.sell)
        if not r['success']:
            return r
        
        list = r['result']['list']
        # Encontrar el diccionario que tiene 'coin' igual a sell
        sell_coin_info = next((item for account in list for item in account['coin'] if item['coin'] == tkinfo.sell), None)

        if sell_coin_info:
           size = round(float(sell_coin_info['walletBalance']), 6)
           
        if not size: 
            return {
                "success": False,
                "error": f"{tkinfo.sell} balance not found"
            }

        logbot.logs(f'>>> Found {size} {tkinfo.sell} to sell')     
        
        # if side == 'Buy':
        #     r = self._try_request('get_tickers', category='spot', symbol=tkinfo.symbol)
        #     if not r['success']:
        #         return r
            
        #     symbol_info = next((item for item in r['result']['list'] if item['symbol'] == tkinfo.symbol), None)
        #     if not symbol_info:
        #         return {
        #         "success": False,
        #         "error": f"Symbol {tkinfo.symbol} not found"
        #         }
            
        #     current_price = float(symbol_info['lastPrice'])
        #     logbot.logs(f'>>> Current price of {tkinfo.symbol} is {current_price}')
            
        #     # Calculate the quantity to buy with a 0.1 margin of error
        #     size = round((size * (1 - 0.3)) / current_price, 4)
        #     logbot.logs(f'>>> Calculated size to buy: {size}')
            
        size = round(size * 0.999, 5) 
        
           
        r = self._try_request('place_active_order', 
                            category='spot',
                            symbol= tkinfo.symbol, 
                            side= side, 
                            order_type='Market', 
                            qty=size, 
                            time_in_force="GoodTillCancel", 
                            reduce_only=False, 
                            close_on_trigger=False)
        if not r['success']:
            r['orders'] = orders
            return r
        orders.append(r['result'])
        logbot.logs(f">>> Order {side} {tkinfo.symbol} {size} posted with success")
        
        return {
            "success": True,
            "orders": orders
        }

    def entry_position(self, payload: dict, ticker):
        #   PLACE ORDER
        orders = []

        side = 'Buy'
        close_sl_tp_side = 'Sell'
        stop_loss = payload['long SL']
        take_profit = payload['long TP']

        if payload['action'] == 'sell':
            side = 'Sell'
            close_sl_tp_side = 'Buy'
            stop_loss = payload['short SL']
            take_profit = payload['short TP']
        
        r = self._try_request('query_symbol')      
        if not r['success']:
            return r
        
        r = r['result']['list']
        my_item = next((item for item in r if item['symbol'] == 'BTCUSDT'), None)
        if not my_item:
            return {
                "success": False,
                "error": "Symbol BTCUSDT not found"
            }
        qty_step = my_item['lotSizeFilter']['qtyStep']

        # 0/ Get free collateral and calculate position
        r = self._try_request('get_wallet_balance', coin="USDT")
        if not r['success']:
            return r
        
        list = r['result']['list']
        # Encontrar el diccionario que tiene 'coin' igual a 'USDT'
        usdt_info = next((item for account in list for item in account['coin'] if item['coin'] == 'USDT'), None)

        if usdt_info:
           free_collateral = float(usdt_info['walletBalance'])
           
        if not free_collateral: 
            return {
                "success": False,
                "error": "USDT balance not found"
            }

        logbot.logs('>>> Found free collateral: {}'.format(free_collateral))
        size = (free_collateral * self.risk) / abs(payload['price'] - stop_loss)
        if (size / (free_collateral / payload['price'])) > self.leverage:
            return {
                    "success": False,
                    "error": "leverage is higher than maximum limit you set"
                }
        
        size = self._rounded_size(size, qty_step)

        logbot.logs(f">>> SIZE: {size}, SIDE: {side}, PRICE: {payload['price']}, SL: {stop_loss}, TP: {take_profit}")
     
        # 1/ place order with stop loss
        if 'type' in payload.keys():
            order_type = payload['type']  # 'market' or 'limit'
            order_type = order_type.capitalize()
        else:
            order_type = 'Market'  # per default market if none is specified
        if order_type != 'Market' and order_type != 'Limit':
            return {
                    "success": False,
                    "error": f"order type '{order_type}' is unknown"
                }
        exe_price = None if order_type == "Market" else payload['price']
        r = self._try_request('place_active_order', 
                            symbol=ticker, 
                            side=side, 
                            order_type=order_type, 
                            qty=size, 
                            price=exe_price, 
                            stop_loss=stop_loss, 
                            time_in_force="GoodTillCancel", 
                            reduce_only=False, 
                            close_on_trigger=False)
        if not r['success']:
            r['orders'] = orders
            return r
        orders.append(r['result'])
        logbot.logs(f">>> Order {order_type} posted with success")
        
        # 2/ place the take profit only if it is not None or 0
        if take_profit:
            if order_type == 'Market':
                r = self._try_request('place_active_order', 
                                    symbol=ticker, 
                                    side=close_sl_tp_side, 
                                    order_type="Limit",  # so we avoid paying fees on market take profit
                                    qty=size, 
                                    price=take_profit,
                                    time_in_force="GoodTillCancel", 
                                    reduce_only=True, 
                                    close_on_trigger=False)
                if not r['success']:
                    r['orders'] = orders
                    return r
                orders.append(r['result'])
                logbot.logs(">>> Take profit posted with success")
            else:  # Limit order type
                r = self._try_request('place_conditional_order', 
                                    symbol=ticker, 
                                    side=close_sl_tp_side, 
                                    order_type="Limit", 
                                    qty=size, 
                                    price=take_profit, 
                                    base_price=exe_price, 
                                    stop_px=exe_price, 
                                    trigger_by='LastPrice', 
                                    time_in_force="GoodTillCancel", 
                                    reduce_only=False,  # Do not set to True
                                    close_on_trigger=False)
                if not r['success']:
                    r['orders'] = orders
                    return r
                orders.append(r['result'])
                logbot.logs(">>> Take profit posted with success")
        
        # 3/ (optional) place multiples take profits
        i = 1
        while True:
            tp = f'tp{i}'
            if tp in payload.keys():
                # place limit order
                dist = abs(payload['price'] - stop_loss) * payload[tp]
                mid_take_profit = (payload['price'] + dist) if side == 'Buy' else (payload['price'] - dist)
                mid_size = size * (payload['tp Close'] / 100)
                mid_size = self._rounded_size(mid_size, qty_step)
                if order_type == 'Market':
                    r = self._try_request('place_active_order', 
                            symbol=ticker, 
                            side=close_sl_tp_side, 
                            order_type="Limit",  # so we avoid paying fees on market take profit
                            qty=mid_size, 
                            price=mid_take_profit,
                            time_in_force="GoodTillCancel", 
                            reduce_only=True, 
                            close_on_trigger=False)
                    if not r['success']:
                        r['orders'] = orders
                        return r
                    orders.append(r['result'])
                    logbot.logs(f">>> Take profit {i} posted with success at price {mid_take_profit} with size {mid_size}")
                else:  # Stop limit type
                    r = self._try_request('place_conditional_order', 
                                    symbol=ticker, 
                                    side=close_sl_tp_side, 
                                    order_type="Limit", 
                                    qty=mid_size, 
                                    price=mid_take_profit, 
                                    base_price=exe_price, 
                                    stop_px=exe_price, 
                                    trigger_by='LastPrice', 
                                    time_in_force="GoodTillCancel", 
                                    reduce_only=False,  # Do not set to True
                                    close_on_trigger=False)
                    if not r['success']:
                        r['orders'] = orders
                        return r
                    orders.append(r['result'])
                    logbot.logs(f">>> Take profit {i} posted with success at price {mid_take_profit} with size {mid_size}")
            else:
                break
            i += 1
        
        return {
            "success": True,
            "orders": orders
        }

    def exit_position(self, ticker):
        #   CLOSE POSITION IF ONE IS ONGOING
        tkinfo = self._parse_ticker(ticker)   
        r = self._try_request('my_position', symbol=tkinfo.symbol)
        if not r['success']:
            return r
        logbot.logs(">>> Retrieve positions")

        for position in r['result']['list']:
            open_size = float(position['size'])
            if open_size > 0:
                open_side = position['side']
                close_side = 'Sell' if open_side == 'Buy' else 'Buy'
                
                r = self._try_request('place_active_order', 
                                    symbol=tkinfo.symbol,
                                    side=close_side,
                                    order_type="Market",
                                    qty=open_size,
                                    price=None,
                                    time_in_force="GoodTillCancel",
                                    reduce_only=True,
                                    close_on_trigger=False)

                if not r['success']:
                    return r
                logbot.logs(">>> Close ongoing position with success")

                break

        #   DELETE ALL ORDERS REMAINING
        r = self._try_request('cancel_all_active_orders', symbol=tkinfo.symbol)
        if not r['success']:
            return r

        logbot.logs(">>> Deleted all orders remaining with success")
        
        return {
            "success": True
        }

    def breakeven(self, payload: dict, ticker):
        #   SET STOP LOSS TO BREAKEVEN
        r = self._try_request('my_position', symbol=ticker)
        if not r['success']:
            return r
        logbot.logs(">>> Retrieve positions")

        orders = []

        for position in r['result']:
            open_size = position['size']
            if open_size > 0:
                open_side = position['side']
                breakeven_price = payload['long Breakeven'] if open_side == 'Buy' else payload['short Breakeven']

                # place market stop loss at breakeven
                r = self._try_request('set_trading_stop', 
                                    symbol=ticker, 
                                    side=open_side,  # Side of the open position
                                    stop_loss=breakeven_price)
                if not r['success']:
                    return r
                orders.append(r['result'])
                logbot.logs(f">>> Breakeven stop loss posted with success at price {breakeven_price}")

        return {
            "success": True,
            "orders": orders
        }

