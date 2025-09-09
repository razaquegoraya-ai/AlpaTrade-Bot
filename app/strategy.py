import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
import logging

from app.models import StrategyConfig, OrderSide, OrderType, AutomationMode
from app.indicators import TechnicalIndicators
from app.alpaca_client import AlpacaClient

logger = logging.getLogger(__name__)


class TradingSignal:
    """Represents a trading signal"""
    def __init__(
        self,
        symbol: str,
        side: OrderSide,
        confidence: float,
        price: Optional[float] = None,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None,
        timeframe: str = "1D",
        strategy_name: str = "default",
        indicators: Optional[Dict[str, Any]] = None,
        notes: Optional[str] = None
    ):
        self.symbol = symbol
        self.side = side
        self.confidence = confidence
        self.price = price
        self.stop_loss = stop_loss
        self.take_profit = take_profit
        self.timeframe = timeframe
        self.strategy_name = strategy_name
        self.indicators = indicators or {}
        self.notes = notes
        self.timestamp = datetime.utcnow()


class StochasticCCIStrategy:
    """Trading strategy based on Stochastic and CCI indicators"""
    
    def __init__(self, config: StrategyConfig, alpaca_client: AlpacaClient):
        self.config = config
        self.alpaca_client = alpaca_client
        self.indicators = TechnicalIndicators()
        
    def analyze_symbol(
        self,
        symbol: str,
        data: pd.DataFrame,
        timeframe: str
    ) -> Optional[TradingSignal]:
        """
        Analyze a symbol and generate trading signals
        
        Args:
            symbol: Stock symbol
            data: OHLCV data
            timeframe: Timeframe of the data
            
        Returns:
            TradingSignal if conditions are met, None otherwise
        """
        try:
            if len(data) < max(self.config.stoch_k_period, self.config.cci_period) + 10:
                return None
                
            # Calculate indicators
            df_with_indicators = self.indicators.calculate_all_indicators(
                data,
                stoch_k_period=self.config.stoch_k_period,
                stoch_d_period=self.config.stoch_d_period,
                cci_period=self.config.cci_period
            )
            
            # Get latest values
            latest = df_with_indicators.iloc[-1]
            prev = df_with_indicators.iloc[-2] if len(df_with_indicators) > 1 else latest
            
            # Check for buy signals
            buy_signal = self._check_buy_conditions(latest, prev)
            if buy_signal:
                return TradingSignal(
                    symbol=symbol,
                    side=OrderSide.BUY,
                    confidence=buy_signal['confidence'],
                    price=latest['close'],
                    stop_loss=buy_signal.get('stop_loss'),
                    take_profit=buy_signal.get('take_profit'),
                    timeframe=timeframe,
                    strategy_name=self.config.name,
                    indicators={
                        'stoch_k': latest['stoch_k'],
                        'stoch_d': latest['stoch_d'],
                        'cci': latest['cci'],
                        'rsi': latest.get('rsi'),
                        'close': latest['close']
                    },
                    notes=buy_signal.get('notes')
                )
            
            # Check for sell signals
            sell_signal = self._check_sell_conditions(latest, prev)
            if sell_signal:
                return TradingSignal(
                    symbol=symbol,
                    side=OrderSide.SELL,
                    confidence=sell_signal['confidence'],
                    price=latest['close'],
                    stop_loss=sell_signal.get('stop_loss'),
                    take_profit=sell_signal.get('take_profit'),
                    timeframe=timeframe,
                    strategy_name=self.config.name,
                    indicators={
                        'stoch_k': latest['stoch_k'],
                        'stoch_d': latest['stoch_d'],
                        'cci': latest['cci'],
                        'rsi': latest.get('rsi'),
                        'close': latest['close']
                    },
                    notes=sell_signal.get('notes')
                )
                
            return None
            
        except Exception as e:
            logger.error(f"Error analyzing {symbol}: {e}")
            return None
    
    def _check_buy_conditions(self, latest: pd.Series, prev: pd.Series) -> Optional[Dict[str, Any]]:
        """Check for buy signal conditions"""
        try:
            # Stochastic oversold conditions
            stoch_oversold = (
                latest['stoch_k'] < self.config.stoch_oversold and
                latest['stoch_d'] < self.config.stoch_oversold and
                latest['stoch_k'] > latest['stoch_d']  # K crossing above D
            )
            
            # CCI oversold conditions
            cci_oversold = latest['cci'] < self.config.cci_oversold
            
            # RSI not extremely oversold (avoid falling knife)
            rsi_ok = latest.get('rsi', 50) > 25
            
            # Volume confirmation (if available)
            volume_ok = True
            if 'volume' in latest and 'volume' in prev:
                volume_ok = latest['volume'] > prev['volume'] * 0.8
            
            if stoch_oversold and cci_oversold and rsi_ok and volume_ok:
                confidence = 0.7
                
                # Calculate stop loss and take profit
                stop_loss = latest['close'] * (1 - self.config.stop_loss_percent / 100)
                take_profit = latest['close'] * (1 + (self.config.stop_loss_percent * 2) / 100)
                
                return {
                    'confidence': confidence,
                    'stop_loss': stop_loss,
                    'take_profit': take_profit,
                    'notes': f"Stochastic oversold ({latest['stoch_k']:.1f}), CCI oversold ({latest['cci']:.1f})"
                }
                
            return None
            
        except Exception as e:
            logger.error(f"Error checking buy conditions: {e}")
            return None
    
    def _check_sell_conditions(self, latest: pd.Series, prev: pd.Series) -> Optional[Dict[str, Any]]:
        """Check for sell signal conditions"""
        try:
            # Stochastic overbought conditions
            stoch_overbought = (
                latest['stoch_k'] > self.config.stoch_overbought and
                latest['stoch_d'] > self.config.stoch_overbought and
                latest['stoch_k'] < latest['stoch_d']  # K crossing below D
            )
            
            # CCI overbought conditions
            cci_overbought = latest['cci'] > self.config.cci_overbought
            
            # RSI not extremely overbought
            rsi_ok = latest.get('rsi', 50) < 75
            
            # Volume confirmation
            volume_ok = True
            if 'volume' in latest and 'volume' in prev:
                volume_ok = latest['volume'] > prev['volume'] * 0.8
            
            if stoch_overbought and cci_overbought and rsi_ok and volume_ok:
                confidence = 0.7
                
                # Calculate stop loss and take profit
                stop_loss = latest['close'] * (1 + self.config.stop_loss_percent / 100)
                take_profit = latest['close'] * (1 - (self.config.stop_loss_percent * 2) / 100)
                
                return {
                    'confidence': confidence,
                    'stop_loss': stop_loss,
                    'take_profit': take_profit,
                    'notes': f"Stochastic overbought ({latest['stoch_k']:.1f}), CCI overbought ({latest['cci']:.1f})"
                }
                
            return None
            
        except Exception as e:
            logger.error(f"Error checking sell conditions: {e}")
            return None


class RiskManager:
    """Risk management for trading operations"""
    
    def __init__(self, config: StrategyConfig, alpaca_client: AlpacaClient):
        self.config = config
        self.alpaca_client = alpaca_client
    
    async def calculate_position_size(
        self,
        symbol: str,
        price: float,
        account_value: float
    ) -> int:
        """
        Calculate position size based on risk management rules
        
        Args:
            symbol: Stock symbol
            price: Entry price
            account_value: Total account value
            
        Returns:
            Number of shares to trade
        """
        try:
            # Calculate capital allocation
            allocated_capital = account_value * (self.config.capital_allocation_percent / 100)
            
            # Calculate position size
            position_size = int(allocated_capital / price)
            
            # Ensure minimum position size
            if position_size < 1:
                return 0
                
            return position_size
            
        except Exception as e:
            logger.error(f"Error calculating position size: {e}")
            return 0
    
    async def check_risk_limits(
        self,
        symbol: str,
        side: OrderSide,
        quantity: int,
        price: float
    ) -> Tuple[bool, str]:
        """
        Check if trade meets risk management criteria
        
        Args:
            symbol: Stock symbol
            side: Buy or sell
            quantity: Number of shares
            price: Price per share
            
        Returns:
            Tuple of (is_allowed, reason)
        """
        try:
            # Get current positions
            positions = await self.alpaca_client.get_positions()
            
            # Check maximum positions limit
            if len(positions) >= self.config.max_positions:
                return False, f"Maximum positions limit reached ({self.config.max_positions})"
            
            # Check if already holding this symbol
            current_position = next((p for p in positions if p['symbol'] == symbol), None)
            if current_position and side == OrderSide.BUY:
                return False, f"Already holding position in {symbol}"
            
            # Check position size
            position_value = quantity * price
            account_info = await self.alpaca_client.get_account_info()
            
            if position_value > account_info.buying_power:
                return False, "Insufficient buying power"
            
            return True, "Risk checks passed"
            
        except Exception as e:
            logger.error(f"Error checking risk limits: {e}")
            return False, f"Risk check error: {e}"


class StrategyEngine:
    """Main strategy engine that coordinates trading operations"""
    
    def __init__(self, alpaca_client: AlpacaClient):
        self.alpaca_client = alpaca_client
        self.strategies: Dict[str, StochasticCCIStrategy] = {}
        self.risk_managers: Dict[str, RiskManager] = {}
    
    def add_strategy(self, config: StrategyConfig):
        """Add a trading strategy"""
        strategy = StochasticCCIStrategy(config, self.alpaca_client)
        risk_manager = RiskManager(config, self.alpaca_client)
        
        self.strategies[config.name] = strategy
        self.risk_managers[config.name] = risk_manager
    
    def remove_strategy(self, strategy_name: str):
        """Remove a trading strategy"""
        if strategy_name in self.strategies:
            del self.strategies[strategy_name]
        if strategy_name in self.risk_managers:
            del self.risk_managers[strategy_name]
    
    async def analyze_symbols(
        self,
        symbols: List[str],
        timeframes: List[str]
    ) -> List[TradingSignal]:
        """
        Analyze multiple symbols across multiple timeframes
        
        Args:
            symbols: List of symbols to analyze
            timeframes: List of timeframes to analyze
            
        Returns:
            List of trading signals
        """
        signals = []
        
        for symbol in symbols:
            for timeframe in timeframes:
                try:
                    # Get historical data
                    end_date = datetime.now()
                    start_date = end_date - timedelta(days=365)  # Get 1 year of data
                    
                    data = await self.alpaca_client.get_historical_data(
                        symbol, timeframe, start_date, end_date
                    )
                    
                    if data.empty:
                        continue
                    
                    # Analyze with each active strategy
                    for strategy_name, strategy in self.strategies.items():
                        if not strategy.config.is_active:
                            continue
                            
                        signal = strategy.analyze_symbol(symbol, data, timeframe)
                        if signal:
                            signals.append(signal)
                            
                except Exception as e:
                    logger.error(f"Error analyzing {symbol} on {timeframe}: {e}")
                    continue
        
        return signals
    
    async def execute_signal(
        self,
        signal: TradingSignal,
        automation_mode: AutomationMode = AutomationMode.ALERT_ONLY
    ) -> Dict[str, Any]:
        """
        Execute a trading signal based on automation mode
        
        Args:
            signal: Trading signal to execute
            automation_mode: Automation mode (auto, alert_only, semi_auto)
            
        Returns:
            Execution result
        """
        try:
            if automation_mode == AutomationMode.ALERT_ONLY:
                return {
                    "status": "alert",
                    "message": f"Alert: {signal.side.value} {signal.symbol} at {signal.price}",
                    "signal": signal
                }
            
            # Get risk manager for this strategy
            risk_manager = self.risk_managers.get(signal.strategy_name)
            if not risk_manager:
                return {"status": "error", "message": "Risk manager not found"}
            
            # Calculate position size
            account_info = await self.alpaca_client.get_account_info()
            quantity = await risk_manager.calculate_position_size(
                signal.symbol, signal.price, account_info.equity
            )
            
            if quantity == 0:
                return {"status": "error", "message": "Position size is zero"}
            
            # Check risk limits
            is_allowed, reason = await risk_manager.check_risk_limits(
                signal.symbol, signal.side, quantity, signal.price
            )
            
            if not is_allowed:
                return {"status": "rejected", "message": reason}
            
            # Execute trade if in auto mode
            if automation_mode == AutomationMode.AUTO:
                order_result = await self.alpaca_client.place_order(
                    symbol=signal.symbol,
                    side=signal.side,
                    order_type=OrderType.MARKET,
                    quantity=quantity
                )
                
                return {
                    "status": "executed",
                    "order": order_result,
                    "signal": signal
                }
            
            # Semi-auto mode - return for manual confirmation
            return {
                "status": "pending_confirmation",
                "message": f"Confirm {signal.side.value} {quantity} shares of {signal.symbol} at {signal.price}",
                "signal": signal,
                "quantity": quantity
            }
            
        except Exception as e:
            logger.error(f"Error executing signal: {e}")
            return {"status": "error", "message": str(e)}
