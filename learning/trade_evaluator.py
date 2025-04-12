from trading_bot.logging_setup import setup_logging
from trading_bot.core import TradingBotCore
from trading_bot.symbol_filter import SymbolFilter
from trading_bot.data_sources.market_data import MarketData

logger = setup_logging('trade_evaluator')

class TradeEvaluator:
    def __init__(self, market_state: dict):
        self.volatility = market_state['volatility']

    def evaluate_trade(self, trade: dict) -> dict:
        """Evaluate the performance of a trade."""
        try:
            if 'profit' not in trade:
                logger.warning("Trade does not contain profit information")
                return {'status': 'failed', 'reason': 'no profit data'}

            # Динамическая корректировка оценки на основе волатильности
            risk_adjusted_profit = trade['profit'] * (1 - self.volatility / 2)
            
            evaluation = {
                'profit': trade['profit'],
                'risk_adjusted_profit': risk_adjusted_profit,
                'success': trade['profit'] > 0
            }
            logger.info(f"Trade evaluation: {evaluation}")
            return evaluation
        except Exception as e:
            logger.error(f"Failed to evaluate trade: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    market_state = {'volatility': 0.3}
    evaluator = TradeEvaluator(market_state)
    core = TradingBotCore(market_state)
    symbol_filter = SymbolFilter(market_state)
    market_data = MarketData(market_state)
    
    # Получаем символы
    symbols = symbol_filter.filter_symbols(market_data.get_symbols('binance'), 'binance')
    
    if symbols:
        # Запускаем торговлю для получения реальной сделки
        trades = core.run_trading(symbols[0], 'bollinger', 10000, '1h', 30, 'binance')
        if trades:
            evaluation = evaluator.evaluate_trade(trades[0])
            print(f"Evaluation for {symbols[0]}: {evaluation}")
        else:
            print(f"No trades executed for {symbols[0]}")
    else:
        print("No symbols available for testing")
