
from trading_bot.logging_setup import setup_logging

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
    trade = {
        'symbol': 'BTC/USDT',
        'profit': 500
    }
    evaluation = evaluator.evaluate_trade(trade)
    print(f"Evaluation: {evaluation}")
