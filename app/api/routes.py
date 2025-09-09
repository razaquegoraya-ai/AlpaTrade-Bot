from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging

from app.models import (
    StrategyConfig, StrategyConfigRequest, TradeRequest, 
    AccountInfo, AutomationMode, OrderSide, OrderType
)
from app.alpaca_client import AlpacaClient
from app.scheduler import TradingScheduler
from app.sentiment import NewsSentimentAnalyzer

logger = logging.getLogger(__name__)

router = APIRouter()

# Global instances (in production, use dependency injection)
alpaca_client = AlpacaClient()
scheduler = TradingScheduler(alpaca_client)
sentiment_analyzer = NewsSentimentAnalyzer()


@router.get("/health")
async def health():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}


@router.get("/account")
async def get_account():
    """Get account information"""
    try:
        account_info = await alpaca_client.get_account_info()
        return account_info
    except Exception as e:
        logger.error(f"Error getting account info: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/positions")
async def get_positions():
    """Get current positions"""
    try:
        positions = await alpaca_client.get_positions()
        return {"positions": positions}
    except Exception as e:
        logger.error(f"Error getting positions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/orders")
async def get_orders(status: str = "all", limit: int = 100):
    """Get orders"""
    try:
        orders = await alpaca_client.get_orders(status=status, limit=limit)
        return {"orders": orders}
    except Exception as e:
        logger.error(f"Error getting orders: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/orders")
async def place_order(order_request: TradeRequest):
    """Place a new order"""
    try:
        order_result = await alpaca_client.place_order(
            symbol=order_request.symbol,
            side=order_request.side,
            order_type=order_request.order_type,
            quantity=order_request.quantity,
            price=order_request.price,
            stop_price=order_request.stop_price,
            trail_percent=order_request.trail_percent
        )
        return {"order": order_result}
    except Exception as e:
        logger.error(f"Error placing order: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/orders/{order_id}")
async def cancel_order(order_id: str):
    """Cancel an order"""
    try:
        success = await alpaca_client.cancel_order(order_id)
        if success:
            return {"message": "Order cancelled successfully"}
        else:
            raise HTTPException(status_code=400, detail="Failed to cancel order")
    except Exception as e:
        logger.error(f"Error cancelling order: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/market-status")
async def get_market_status():
    """Get market status"""
    try:
        status = await alpaca_client.get_market_status()
        return status
    except Exception as e:
        logger.error(f"Error getting market status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/historical-data/{symbol}")
async def get_historical_data(
    symbol: str,
    timeframe: str = "1D",
    days: int = 30
):
    """Get historical data for a symbol"""
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        data = await alpaca_client.get_historical_data(
            symbol, timeframe, start_date, end_date
        )
        
        # Convert to dict for JSON serialization
        data_dict = data.to_dict('records') if not data.empty else []
        
        return {
            "symbol": symbol,
            "timeframe": timeframe,
            "data": data_dict
        }
    except Exception as e:
        logger.error(f"Error getting historical data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/strategies")
async def get_strategies():
    """Get all strategies"""
    try:
        strategies = list(scheduler.strategy_engine.strategies.keys())
        return {"strategies": strategies}
    except Exception as e:
        logger.error(f"Error getting strategies: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/strategies")
async def create_strategy(config: StrategyConfigRequest):
    """Create a new strategy"""
    try:
        strategy_config = StrategyConfig(**config.dict())
        scheduler.add_strategy(strategy_config)
        return {"message": f"Strategy '{config.name}' created successfully"}
    except Exception as e:
        logger.error(f"Error creating strategy: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/strategies/{strategy_name}")
async def delete_strategy(strategy_name: str):
    """Delete a strategy"""
    try:
        scheduler.remove_strategy(strategy_name)
        return {"message": f"Strategy '{strategy_name}' deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting strategy: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/watchlist")
async def get_watchlist():
    """Get current watchlist"""
    try:
        return {"watchlist": scheduler.watchlist}
    except Exception as e:
        logger.error(f"Error getting watchlist: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/watchlist")
async def set_watchlist(symbols: List[str]):
    """Set the watchlist"""
    try:
        scheduler.set_watchlist(symbols)
        return {"message": f"Watchlist updated with {len(symbols)} symbols"}
    except Exception as e:
        logger.error(f"Error setting watchlist: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/scheduler/status")
async def get_scheduler_status():
    """Get scheduler status"""
    try:
        status = scheduler.get_status()
        return status
    except Exception as e:
        logger.error(f"Error getting scheduler status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/scheduler/start")
async def start_scheduler():
    """Start the trading scheduler"""
    try:
        scheduler.start()
        return {"message": "Scheduler started successfully"}
    except Exception as e:
        logger.error(f"Error starting scheduler: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/scheduler/stop")
async def stop_scheduler():
    """Stop the trading scheduler"""
    try:
        scheduler.stop()
        return {"message": "Scheduler stopped successfully"}
    except Exception as e:
        logger.error(f"Error stopping scheduler: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pending-signals")
async def get_pending_signals():
    """Get pending signals for manual confirmation"""
    try:
        signals = scheduler.get_pending_signals()
        return {"pending_signals": signals}
    except Exception as e:
        logger.error(f"Error getting pending signals: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/pending-signals/{signal_id}/confirm")
async def confirm_signal(signal_id: str):
    """Confirm a pending signal"""
    try:
        # Find signal by ID (simplified - in production use proper ID matching)
        signals = scheduler.get_pending_signals()
        signal = next((s for s in signals if s.symbol == signal_id), None)
        
        if not signal:
            raise HTTPException(status_code=404, detail="Signal not found")
        
        success = scheduler.confirm_signal(signal)
        if success:
            return {"message": "Signal confirmed and executed"}
        else:
            raise HTTPException(status_code=400, detail="Failed to confirm signal")
    except Exception as e:
        logger.error(f"Error confirming signal: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/pending-signals/{signal_id}/reject")
async def reject_signal(signal_id: str):
    """Reject a pending signal"""
    try:
        # Find signal by ID (simplified - in production use proper ID matching)
        signals = scheduler.get_pending_signals()
        signal = next((s for s in signals if s.symbol == signal_id), None)
        
        if not signal:
            raise HTTPException(status_code=404, detail="Signal not found")
        
        success = scheduler.reject_signal(signal)
        if success:
            return {"message": "Signal rejected"}
        else:
            raise HTTPException(status_code=400, detail="Failed to reject signal")
    except Exception as e:
        logger.error(f"Error rejecting signal: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sentiment/{symbol}")
async def get_sentiment(symbol: str, hours_back: int = 24):
    """Get sentiment analysis for a symbol"""
    try:
        sentiment_data = await sentiment_analyzer.get_sentiment_for_symbols(
            [symbol], hours_back
        )
        return sentiment_data.get(symbol, {})
    except Exception as e:
        logger.error(f"Error getting sentiment: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sentiment/market")
async def get_market_sentiment(hours_back: int = 24):
    """Get overall market sentiment"""
    try:
        sentiment = await sentiment_analyzer.get_market_sentiment(hours_back)
        return sentiment
    except Exception as e:
        logger.error(f"Error getting market sentiment: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analyze/{symbol}")
async def analyze_symbol(symbol: str, timeframe: str = "1D"):
    """Analyze a symbol for trading signals"""
    try:
        # Get historical data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        
        data = await alpaca_client.get_historical_data(
            symbol, timeframe, start_date, end_date
        )
        
        if data.empty:
            raise HTTPException(status_code=404, detail="No data available for symbol")
        
        # Analyze with all active strategies
        signals = []
        for strategy_name, strategy in scheduler.strategy_engine.strategies.items():
            if strategy.config.is_active:
                signal = strategy.analyze_symbol(symbol, data, timeframe)
                if signal:
                    signals.append(signal)
        
        return {
            "symbol": symbol,
            "timeframe": timeframe,
            "signals": signals
        }
    except Exception as e:
        logger.error(f"Error analyzing symbol: {e}")
        raise HTTPException(status_code=500, detail=str(e))
