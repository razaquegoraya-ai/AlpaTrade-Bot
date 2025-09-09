import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class TechnicalIndicators:
    """Technical indicators for trading strategies"""
    
    @staticmethod
    def stochastic_oscillator(
        high: pd.Series,
        low: pd.Series,
        close: pd.Series,
        k_period: int = 14,
        d_period: int = 3
    ) -> Tuple[pd.Series, pd.Series]:
        """
        Calculate Stochastic Oscillator
        
        Args:
            high: High prices
            low: Low prices
            close: Close prices
            k_period: Period for %K calculation
            d_period: Period for %D calculation (SMA of %K)
            
        Returns:
            Tuple of (%K, %D) series
        """
        try:
            # Calculate %K
            lowest_low = low.rolling(window=k_period).min()
            highest_high = high.rolling(window=k_period).max()
            
            k_percent = 100 * ((close - lowest_low) / (highest_high - lowest_low))
            
            # Calculate %D (SMA of %K)
            d_percent = k_percent.rolling(window=d_period).mean()
            
            return k_percent, d_percent
        except Exception as e:
            logger.error(f"Error calculating Stochastic Oscillator: {e}")
            return pd.Series(), pd.Series()

    @staticmethod
    def commodity_channel_index(
        high: pd.Series,
        low: pd.Series,
        close: pd.Series,
        period: int = 20
    ) -> pd.Series:
        """
        Calculate Commodity Channel Index (CCI)
        
        Args:
            high: High prices
            low: Low prices
            close: Close prices
            period: Period for calculation
            
        Returns:
            CCI series
        """
        try:
            # Calculate Typical Price
            typical_price = (high + low + close) / 3
            
            # Calculate Simple Moving Average of Typical Price
            sma_tp = typical_price.rolling(window=period).mean()
            
            # Calculate Mean Deviation
            mean_deviation = typical_price.rolling(window=period).apply(
                lambda x: np.mean(np.abs(x - x.mean()))
            )
            
            # Calculate CCI
            cci = (typical_price - sma_tp) / (0.015 * mean_deviation)
            
            return cci
        except Exception as e:
            logger.error(f"Error calculating CCI: {e}")
            return pd.Series()

    @staticmethod
    def rsi(close: pd.Series, period: int = 14) -> pd.Series:
        """
        Calculate Relative Strength Index (RSI)
        
        Args:
            close: Close prices
            period: Period for calculation
            
        Returns:
            RSI series
        """
        try:
            delta = close.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            
            return rsi
        except Exception as e:
            logger.error(f"Error calculating RSI: {e}")
            return pd.Series()

    @staticmethod
    def moving_average(close: pd.Series, period: int, ma_type: str = "sma") -> pd.Series:
        """
        Calculate Moving Average
        
        Args:
            close: Close prices
            period: Period for calculation
            ma_type: Type of MA ('sma', 'ema', 'wma')
            
        Returns:
            Moving average series
        """
        try:
            if ma_type.lower() == "sma":
                return close.rolling(window=period).mean()
            elif ma_type.lower() == "ema":
                return close.ewm(span=period).mean()
            elif ma_type.lower() == "wma":
                weights = np.arange(1, period + 1)
                return close.rolling(window=period).apply(
                    lambda x: np.dot(x, weights) / weights.sum(), raw=True
                )
            else:
                raise ValueError(f"Unknown MA type: {ma_type}")
        except Exception as e:
            logger.error(f"Error calculating Moving Average: {e}")
            return pd.Series()

    @staticmethod
    def bollinger_bands(
        close: pd.Series,
        period: int = 20,
        std_dev: float = 2.0
    ) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Calculate Bollinger Bands
        
        Args:
            close: Close prices
            period: Period for calculation
            std_dev: Standard deviation multiplier
            
        Returns:
            Tuple of (upper_band, middle_band, lower_band)
        """
        try:
            middle_band = close.rolling(window=period).mean()
            std = close.rolling(window=period).std()
            
            upper_band = middle_band + (std * std_dev)
            lower_band = middle_band - (std * std_dev)
            
            return upper_band, middle_band, lower_band
        except Exception as e:
            logger.error(f"Error calculating Bollinger Bands: {e}")
            return pd.Series(), pd.Series(), pd.Series()

    @staticmethod
    def macd(
        close: pd.Series,
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9
    ) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Calculate MACD
        
        Args:
            close: Close prices
            fast_period: Fast EMA period
            slow_period: Slow EMA period
            signal_period: Signal line EMA period
            
        Returns:
            Tuple of (macd_line, signal_line, histogram)
        """
        try:
            ema_fast = close.ewm(span=fast_period).mean()
            ema_slow = close.ewm(span=slow_period).mean()
            
            macd_line = ema_fast - ema_slow
            signal_line = macd_line.ewm(span=signal_period).mean()
            histogram = macd_line - signal_line
            
            return macd_line, signal_line, histogram
        except Exception as e:
            logger.error(f"Error calculating MACD: {e}")
            return pd.Series(), pd.Series(), pd.Series()

    @staticmethod
    def calculate_all_indicators(
        df: pd.DataFrame,
        stoch_k_period: int = 14,
        stoch_d_period: int = 3,
        cci_period: int = 20,
        rsi_period: int = 14,
        ma_period: int = 20,
        bb_period: int = 20,
        bb_std: float = 2.0,
        macd_fast: int = 12,
        macd_slow: int = 26,
        macd_signal: int = 9
    ) -> pd.DataFrame:
        """
        Calculate all indicators for a DataFrame
        
        Args:
            df: DataFrame with OHLCV data
            Various periods for different indicators
            
        Returns:
            DataFrame with all indicators added
        """
        try:
            result_df = df.copy()
            
            # Stochastic Oscillator
            stoch_k, stoch_d = TechnicalIndicators.stochastic_oscillator(
                df['high'], df['low'], df['close'], stoch_k_period, stoch_d_period
            )
            result_df['stoch_k'] = stoch_k
            result_df['stoch_d'] = stoch_d
            
            # CCI
            result_df['cci'] = TechnicalIndicators.commodity_channel_index(
                df['high'], df['low'], df['close'], cci_period
            )
            
            # RSI
            result_df['rsi'] = TechnicalIndicators.rsi(df['close'], rsi_period)
            
            # Moving Averages
            result_df['sma'] = TechnicalIndicators.moving_average(df['close'], ma_period, 'sma')
            result_df['ema'] = TechnicalIndicators.moving_average(df['close'], ma_period, 'ema')
            
            # Bollinger Bands
            bb_upper, bb_middle, bb_lower = TechnicalIndicators.bollinger_bands(
                df['close'], bb_period, bb_std
            )
            result_df['bb_upper'] = bb_upper
            result_df['bb_middle'] = bb_middle
            result_df['bb_lower'] = bb_lower
            
            # MACD
            macd_line, signal_line, histogram = TechnicalIndicators.macd(
                df['close'], macd_fast, macd_slow, macd_signal
            )
            result_df['macd'] = macd_line
            result_df['macd_signal'] = signal_line
            result_df['macd_histogram'] = histogram
            
            return result_df
        except Exception as e:
            logger.error(f"Error calculating all indicators: {e}")
            return df
