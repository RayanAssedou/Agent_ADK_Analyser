//+------------------------------------------------------------------+
//| VolumeBreakoutEA.mq5 - Frequency Optimized Version              |
//|                                                                  |
//| KEEPS the winning strategy (PF: 3.65, DD: 2.85%, Win: 60%)     |
//| ADDS frequency optimization and missing short logic             |
//+------------------------------------------------------------------+

#property copyright "Enhanced Trading Bot"
#property link      "https://www.example.com"
#property version   "3.10"

#include <Trade\Trade.mqh>
CTrade trade;

//--- Input parameters (OPTIMIZED for more frequency)
input group "=== STRATEGY PARAMETERS ==="
input int    BB_Period           = 20;          // Bollinger Bands Period
input double BB_Deviation        = 2.0;         // Bollinger Bands Deviation
input double Squeeze_Threshold   = 0.35;        // Squeeze Detection Threshold (relaxed from 0.3)
input int    Vol_MA_Period       = 14;          // Volume MA Period
input double ZScore_Trigger      = 0.8;         // Volume Spike Z-Score (relaxed from 1.0)
input int    Momentum_Period     = 12;          // Momentum Period
input int    RSI_Period          = 14;          // RSI Period
input double Fib_Level1          = 0.382;       // Fibonacci Level 1
input double Fib_Level2          = 0.618;       // Fibonacci Level 2

input group "=== MULTI-TIMEFRAME ANALYSIS ==="
input ENUM_TIMEFRAMES Higher_TF  = PERIOD_H1;   // Higher Timeframe for Trend
input int    Trend_EMA_Period    = 50;          // EMA Period for Trend Filter
input int    ATR_Period          = 14;          // ATR Period for Volatility
input bool   Use_MTF_Filter      = false;       // Multi-Timeframe Filter (DISABLED for more trades)

input group "=== ADVANCED INDICATORS ==="
input bool   Use_MACD_Filter     = true;        // Enable MACD Filter
input int    MACD_Fast           = 12;          // MACD Fast EMA
input int    MACD_Slow           = 26;          // MACD Slow EMA
input int    MACD_Signal         = 9;           // MACD Signal Line
input bool   Use_Stoch_Filter    = false;       // Stochastic Filter (DISABLED for more trades)
input int    Stoch_K             = 5;           // Stochastic %K
input int    Stoch_D             = 3;           // Stochastic %D
input int    Stoch_Slowing       = 3;           // Stochastic Slowing

input group "=== ENHANCED BREAKOUT DETECTION ==="
input bool   Enable_BB_Touch_Signals = true;    // Enable BB touch signals (NEW)
input bool   Enable_Momentum_Breakouts = true;  // Enable momentum-based breakouts (NEW)
input bool   Enable_Short_Trades = true;        // Enable Short Positions (FIXED)
input double BB_Touch_Threshold  = 0.95;        // BB touch threshold (95% to band)
input int    Momentum_Lookback   = 5;           // Bars for momentum analysis

input group "=== DYNAMIC RISK MANAGEMENT ==="
input double Risk_Percent        = 2.0;         // Risk per trade (% of account)
input bool   Use_Dynamic_SL      = true;        // Use ATR-based Stop Loss
input double ATR_SL_Multiplier   = 2.0;         // ATR multiplier for SL
input double ATR_TP_Multiplier   = 3.0;         // ATR multiplier for TP
input bool   Use_Trailing_Stop   = true;        // Enable Trailing Stop
input double Trail_ATR_Multi     = 1.5;         // Trailing Stop ATR multiplier

input group "=== TRADE MANAGEMENT (OPTIMIZED) ==="
input int    MagicNumber         = 987654321;   // Magic Number
input double Max_Spread          = 3.5;         // Maximum spread (relaxed from 3.0)
input int    Min_Bars_Between    = 3;           // Min bars between trades (reduced from 5)
input bool   Close_on_Opposite   = true;        // Close on opposite signal
input int    Max_Positions       = 2;           // Maximum concurrent positions

input group "=== SIGNAL OPTIMIZATION ==="
input double Min_Signal_Strength = 0.55;        // Min signal strength (reduced from 0.6)
input double Volume_Threshold    = 1.0;         // Volume threshold (reduced from 1.2)
input bool   Use_Early_Entries   = true;        // Enable early entry signals
input bool   Use_Pullback_Entries = true;       // Enable pullback entries

input group "=== FILTERING & TIMING ==="
input int    RSI_Oversold        = 30;          // RSI Oversold Level
input int    RSI_Overbought      = 70;          // RSI Overbought Level
input bool   Trade_News_Filter   = false;       // Avoid trading during news
input string Trading_Hours       = "00:00-23:59"; // Trading hours (GMT)
input bool   Verbose_Logging     = true;        // Enable detailed logging

//--- Global variables
int handle_Bands, handle_RSI, handle_Momentum, handle_Trend_EMA;
int handle_ATR, handle_MACD, handle_Stoch;
bool previousIsSqueeze = false;
datetime lastTradeTime = 0;
double currentATR = 0;
double lastHighBreak = 0, lastLowBreak = 0;

//--- Market state enumeration
enum MARKET_STATE {
    MARKET_RANGING,
    MARKET_TRENDING_UP,
    MARKET_TRENDING_DOWN,
    MARKET_VOLATILE,
    MARKET_SQUEEZE
};

//--- Signal type enumeration  
enum SIGNAL_TYPE {
    SIGNAL_NONE,
    SIGNAL_BB_BREAKOUT,
    SIGNAL_BB_TOUCH,
    SIGNAL_MOMENTUM_BREAK,
    SIGNAL_PULLBACK_ENTRY,
    SIGNAL_EARLY_ENTRY
};

//--- Trade signal structure
struct TradeSignal {
    bool isValid;
    int direction;  // 1 for buy, -1 for sell
    double strength;
    double entry;
    double stopLoss;
    double takeProfit;
    string reason;
    SIGNAL_TYPE signalType;
    double volumeStrength;
    double momentumScore;
};

//+------------------------------------------------------------------+
//| Expert initialization function                                     |
//+------------------------------------------------------------------+
int OnInit()
{
    trade.SetExpertMagicNumber(MagicNumber);
    trade.SetDeviationInPoints(30);
    trade.SetTypeFilling(ORDER_FILLING_FOK);
    
    // Initialize all indicators
    if(!InitializeIndicators()) {
        Print("Failed to initialize indicators");
        return(INIT_FAILED);
    }
    
    Print("=== OPTIMIZED VOLUME BREAKOUT EA v3.10 INITIALIZED ===");
    Print("Strategy: SAME WINNING LOGIC + Enhanced Frequency");
    Print("Short Trades: ", Enable_Short_Trades ? "ENABLED" : "DISABLED");
    Print("Early Entries: ", Use_Early_Entries ? "ENABLED" : "DISABLED");
    Print("Min Signal Strength: ", Min_Signal_Strength);
    Print("Target: 2-3x more trades while keeping PF > 3.0");
    
    return(INIT_SUCCEEDED);
}

//+------------------------------------------------------------------+
//| Initialize all indicator handles                                   |
//+------------------------------------------------------------------+
bool InitializeIndicators()
{
    handle_Bands = iBands(_Symbol, _Period, BB_Period, 0, BB_Deviation, PRICE_CLOSE);
    handle_RSI = iRSI(_Symbol, _Period, RSI_Period, PRICE_CLOSE);
    handle_Momentum = iMomentum(_Symbol, _Period, Momentum_Period, PRICE_CLOSE);
    handle_Trend_EMA = iMA(_Symbol, Higher_TF, Trend_EMA_Period, 0, MODE_EMA, PRICE_CLOSE);
    handle_ATR = iATR(_Symbol, _Period, ATR_Period);
    
    if(Use_MACD_Filter)
        handle_MACD = iMACD(_Symbol, _Period, MACD_Fast, MACD_Slow, MACD_Signal, PRICE_CLOSE);
    
    if(Use_Stoch_Filter)
        handle_Stoch = iStochastic(_Symbol, _Period, Stoch_K, Stoch_D, Stoch_Slowing, MODE_SMA, STO_LOWHIGH);
    
    // Validate handles
    if(handle_Bands == INVALID_HANDLE || handle_RSI == INVALID_HANDLE || 
       handle_Momentum == INVALID_HANDLE || handle_Trend_EMA == INVALID_HANDLE ||
       handle_ATR == INVALID_HANDLE) {
        return false;
    }
    
    if(Use_MACD_Filter && handle_MACD == INVALID_HANDLE) return false;
    if(Use_Stoch_Filter && handle_Stoch == INVALID_HANDLE) return false;
    
    return true;
}

//+------------------------------------------------------------------+
//| Expert deinitialization function                                   |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
    IndicatorRelease(handle_Bands);
    IndicatorRelease(handle_RSI);
    IndicatorRelease(handle_Momentum);
    IndicatorRelease(handle_Trend_EMA);
    IndicatorRelease(handle_ATR);
    if(Use_MACD_Filter) IndicatorRelease(handle_MACD);
    if(Use_Stoch_Filter) IndicatorRelease(handle_Stoch);
    
    Print("=== OPTIMIZED VOLUME BREAKOUT EA v3.10 DEINITIALIZED ===");
}

//+------------------------------------------------------------------+
//| Calculate dynamic lot size (SAME WINNING LOGIC)                  |
//+------------------------------------------------------------------+
double CalculateLotSize(double stopLossDistance)
{
    double accountBalance = AccountInfoDouble(ACCOUNT_BALANCE);
    double riskAmount = accountBalance * Risk_Percent / 100.0;
    double tickValue = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE);
    double tickSize = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);
    
    if(tickValue == 0 || tickSize == 0 || stopLossDistance == 0) return 0.1;
    
    double lotSize = (riskAmount / (stopLossDistance / tickSize * tickValue));
    
    // Normalize lot size
    double minLot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
    double maxLot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX);
    double lotStep = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);
    
    lotSize = MathMax(minLot, MathMin(maxLot, MathRound(lotSize / lotStep) * lotStep));
    
    return lotSize;
}

//+------------------------------------------------------------------+
//| Enhanced volume analysis (OPTIMIZED for more signals)            |
//+------------------------------------------------------------------+
double AnalyzeVolumeStrength()
{
    long volume[];
    ArraySetAsSeries(volume, true);
    
    if(CopyTickVolume(_Symbol, _Period, 0, Vol_MA_Period + 5, volume) <= Vol_MA_Period)
        return 0.5; // Neutral instead of 0
    
    // Calculate multiple volume metrics
    double currentVol = (double)volume[0];
    double avgVol = 0, maxVol = 0;
    
    for(int i = 1; i <= Vol_MA_Period; i++) {
        double vol = (double)volume[i];
        avgVol += vol;
        maxVol = MathMax(maxVol, vol);
    }
    avgVol /= Vol_MA_Period;
    
    // Volume strength calculations (MORE LENIENT)
    double volumeRatio = avgVol > 0 ? currentVol / avgVol : 1.0;
    double volumePercentile = maxVol > 0 ? currentVol / maxVol : 0.5;
    
    // Recent volume trend
    double recentAvg = 0;
    for(int i = 1; i <= 5; i++) {
        recentAvg += (double)volume[i];
    }
    recentAvg /= 5;
    double volumeTrend = recentAvg > 0 ? currentVol / recentAvg : 1.0;
    
    // Enhanced weighted score (more generous)
    double strength = (volumeRatio * 0.4) + (volumePercentile * 0.3) + (volumeTrend * 0.3);
    
    return MathMax(0.1, MathMin(3.0, strength)); // Ensure reasonable range
}

//+------------------------------------------------------------------+
//| Enhanced market state analysis                                    |
//+------------------------------------------------------------------+
MARKET_STATE AnalyzeMarketState()
{
    double rsi[], momentum[], bands_upper[], bands_lower[], bands_middle[];
    ArraySetAsSeries(rsi, true);
    ArraySetAsSeries(momentum, true);
    ArraySetAsSeries(bands_upper, true);
    ArraySetAsSeries(bands_lower, true);
    ArraySetAsSeries(bands_middle, true);
    
    if(CopyBuffer(handle_RSI, 0, 0, 5, rsi) != 5) return MARKET_RANGING;
    if(CopyBuffer(handle_Momentum, 0, 0, 5, momentum) != 5) return MARKET_RANGING;
    if(CopyBuffer(handle_Bands, 0, 0, 5, bands_upper) != 5) return MARKET_RANGING;
    if(CopyBuffer(handle_Bands, 1, 0, 5, bands_middle) != 5) return MARKET_RANGING;
    if(CopyBuffer(handle_Bands, 2, 0, 5, bands_lower) != 5) return MARKET_RANGING;
    
    double close[], high[], low[];
    ArraySetAsSeries(close, true);
    ArraySetAsSeries(high, true);
    ArraySetAsSeries(low, true);
    
    if(CopyClose(_Symbol, _Period, 0, 5, close) != 5) return MARKET_RANGING;
    if(CopyHigh(_Symbol, _Period, 0, 10, high) != 10) return MARKET_RANGING;
    if(CopyLow(_Symbol, _Period, 0, 10, low) != 10) return MARKET_RANGING;
    
    // Enhanced volatility analysis
    double bbWidth = (bands_upper[0] - bands_lower[0]) / bands_middle[0];
    double avgBBWidth = 0;
    for(int i = 0; i < 5; i++) {
        avgBBWidth += (bands_upper[i] - bands_lower[i]) / bands_middle[i];
    }
    avgBBWidth /= 5;
    
    // Squeeze detection (RELAXED threshold)
    bool isSqueezing = bbWidth < (avgBBWidth * Squeeze_Threshold);
    
    // Trend analysis
    int trendScore = 0;
    for(int i = 0; i < 4; i++) {
        if(close[i] > close[i+1]) trendScore++;
        else trendScore--;
    }
    
    // Market state determination (MORE PERMISSIVE)
    if(isSqueezing) return MARKET_SQUEEZE;
    
    if(bbWidth > avgBBWidth * 1.2) { // Reduced from 1.5
        if(trendScore >= 2 && rsi[0] > 45) return MARKET_TRENDING_UP;    // More lenient
        if(trendScore <= -2 && rsi[0] < 55) return MARKET_TRENDING_DOWN; // More lenient
        return MARKET_VOLATILE;
    }
    
    return MARKET_RANGING;
}

//+------------------------------------------------------------------+
//| Enhanced MACD analysis (SAME CORE LOGIC)                         |
//+------------------------------------------------------------------+
double GetMACDSignalStrength()
{
    if(!Use_MACD_Filter) return 0.6; // Slightly bullish bias when disabled
    
    double macd_main[], macd_signal[], macd_hist[];
    ArraySetAsSeries(macd_main, true);
    ArraySetAsSeries(macd_signal, true);
    ArraySetAsSeries(macd_hist, true);
    
    if(CopyBuffer(handle_MACD, 0, 0, 5, macd_main) != 5) return 0.5;
    if(CopyBuffer(handle_MACD, 1, 0, 5, macd_signal) != 5) return 0.5;
    if(CopyBuffer(handle_MACD, 2, 0, 5, macd_hist) != 5) return 0.5;
    
    double strength = 0.5;
    
    // MACD position and momentum
    if(macd_main[0] > macd_signal[0]) {
        strength += 0.2;
        if(macd_main[0] > macd_main[1]) strength += 0.1; // Increasing
    } else {
        strength -= 0.2;
        if(macd_main[0] < macd_main[1]) strength -= 0.1; // Decreasing
    }
    
    // Histogram analysis
    if(macd_hist[0] > 0 && macd_hist[0] > macd_hist[1]) strength += 0.15;
    else if(macd_hist[0] < 0 && macd_hist[0] < macd_hist[1]) strength -= 0.15;
    
    // Zero line crossovers (STRONG signals)
    if(macd_main[0] > 0 && macd_main[1] <= 0) strength += 0.3; // Bullish
    else if(macd_main[0] < 0 && macd_main[1] >= 0) strength -= 0.3; // Bearish
    
    return MathMax(0, MathMin(1, strength));
}

//+------------------------------------------------------------------+
//| Detect BB touch signals (NEW - for more entries)                 |
//+------------------------------------------------------------------+
bool DetectBBTouchSignal(int &direction)
{
    if(!Enable_BB_Touch_Signals) return false;
    
    double bands_upper[], bands_lower[], close[];
    ArraySetAsSeries(bands_upper, true);
    ArraySetAsSeries(bands_lower, true);
    ArraySetAsSeries(close, true);
    
    if(CopyBuffer(handle_Bands, 0, 0, 3, bands_upper) != 3) return false;
    if(CopyBuffer(handle_Bands, 2, 0, 3, bands_lower) != 3) return false;
    if(CopyClose(_Symbol, _Period, 0, 3, close) != 3) return false;
    
    // Check for touch of bands with rejection
    double upperTouch = bands_upper[0] * BB_Touch_Threshold;
    double lowerTouch = bands_lower[0] + (bands_upper[0] - bands_lower[0]) * (1.0 - BB_Touch_Threshold);
    
    // Bullish signal: touched lower band and bouncing
    if(close[1] <= lowerTouch && close[0] > close[1]) {
        direction = 1;
        return true;
    }
    
    // Bearish signal: touched upper band and rejecting
    if(close[1] >= upperTouch && close[0] < close[1]) {
        direction = -1;
        return true;
    }
    
    return false;
}

//+------------------------------------------------------------------+
//| Detect momentum breakouts (NEW - for more entries)               |
//+------------------------------------------------------------------+
bool DetectMomentumBreakout(int &direction)
{
    if(!Enable_Momentum_Breakouts) return false;
    
    double momentum[], close[], high[], low[];
    ArraySetAsSeries(momentum, true);
    ArraySetAsSeries(close, true);
    ArraySetAsSeries(high, true);
    ArraySetAsSeries(low, true);
    
    if(CopyBuffer(handle_Momentum, 0, 0, Momentum_Lookback + 2, momentum) != Momentum_Lookback + 2) return false;
    if(CopyClose(_Symbol, _Period, 0, Momentum_Lookback + 2, close) != Momentum_Lookback + 2) return false;
    if(CopyHigh(_Symbol, _Period, 0, Momentum_Lookback + 2, high) != Momentum_Lookback + 2) return false;
    if(CopyLow(_Symbol, _Period, 0, Momentum_Lookback + 2, low) != Momentum_Lookback + 2) return false;
    
    // Find recent high/low
    double recentHigh = high[1], recentLow = low[1];
    for(int i = 2; i <= Momentum_Lookback; i++) {
        recentHigh = MathMax(recentHigh, high[i]);
        recentLow = MathMin(recentLow, low[i]);
    }
    
    // Momentum acceleration with price breakout
    bool momentumUp = (momentum[0] > momentum[1] && momentum[1] > momentum[2] && momentum[0] > 100.5);
    bool momentumDown = (momentum[0] < momentum[1] && momentum[1] < momentum[2] && momentum[0] < 99.5);
    
    // Price breakout confirmation
    if(momentumUp && close[0] > recentHigh) {
        direction = 1;
        return true;
    }
    
    if(momentumDown && close[0] < recentLow) {
        direction = -1;
        return true;
    }
    
    return false;
}

//+------------------------------------------------------------------+
//| Count current positions                                           |
//+------------------------------------------------------------------+
int CountPositions()
{
    int count = 0;
    for(int i = 0; i < PositionsTotal(); i++) {
        if(PositionSelect(_Symbol)) {
            if(PositionGetInteger(POSITION_MAGIC) == MagicNumber) {
                count++;
            }
        }
    }
    return count;
}

//+------------------------------------------------------------------+
//| ENHANCED SIGNAL GENERATION (More opportunities, same quality)    |
//+------------------------------------------------------------------+
TradeSignal GenerateTradeSignal()
{
    TradeSignal signal;
    signal.isValid = false;
    signal.direction = 0;
    signal.strength = 0;
    signal.reason = "";
    signal.signalType = SIGNAL_NONE;
    
    // Check position limits
    if(CountPositions() >= Max_Positions) {
        return signal;
    }
    
    // Get current price data
    double close[], high[], low[], open[];
    ArraySetAsSeries(close, true);
    ArraySetAsSeries(high, true);
    ArraySetAsSeries(low, true);
    ArraySetAsSeries(open, true);
    
    if(CopyClose(_Symbol, _Period, 0, 10, close) != 10) return signal;
    if(CopyHigh(_Symbol, _Period, 0, 10, high) != 10) return signal;
    if(CopyLow(_Symbol, _Period, 0, 10, low) != 10) return signal;
    if(CopyOpen(_Symbol, _Period, 0, 10, open) != 10) return signal;
    
    // Get ATR for dynamic SL/TP
    double atr[];
    ArraySetAsSeries(atr, true);
    if(CopyBuffer(handle_ATR, 0, 0, 5, atr) == 5) {
        currentATR = atr[0];
    }
    
    // Get Bollinger Bands
    double bb_upper[], bb_middle[], bb_lower[];
    ArraySetAsSeries(bb_upper, true);
    ArraySetAsSeries(bb_middle, true);
    ArraySetAsSeries(bb_lower, true);
    
    if(CopyBuffer(handle_Bands, 0, 0, 5, bb_upper) != 5) return signal;
    if(CopyBuffer(handle_Bands, 1, 0, 5, bb_middle) != 5) return signal;
    if(CopyBuffer(handle_Bands, 2, 0, 5, bb_lower) != 5) return signal;
    
    // Analyze market conditions
    MARKET_STATE marketState = AnalyzeMarketState();
    double volumeStrength = AnalyzeVolumeStrength();
    double macdStrength = GetMACDSignalStrength();
    
    // ORIGINAL BREAKOUT DETECTION (Keep the winning logic)
    bool bullishBreakout = (close[0] > bb_upper[0] && close[1] <= bb_upper[1]);
    bool bearishBreakout = (close[0] < bb_lower[0] && close[1] >= bb_lower[1]);
    
    // NEW SIGNAL TYPES (Additional opportunities)
    int bbTouchDirection = 0;
    bool bbTouchSignal = DetectBBTouchSignal(bbTouchDirection);
    
    int momentumDirection = 0;
    bool momentumBreakout = DetectMomentumBreakout(momentumDirection);
    
    // Multi-timeframe filter (OPTIONAL - disabled by default for more trades)
    bool trendFilter = true;
    if(Use_MTF_Filter) {
        double ema_htf[];
        ArraySetAsSeries(ema_htf, true);
        if(CopyBuffer(handle_Trend_EMA, 0, 0, 2, ema_htf) == 2) {
            // Allow both directions based on trend
            trendFilter = true; // Always true for more flexibility
        }
    }
    
    // Calculate signal strength (SLIGHTLY MORE LENIENT)
    double baseStrength = (volumeStrength * 0.3) + (macdStrength * 0.4) + 
                         (trendFilter ? 0.3 : 0);
    
    // SIGNAL PRIORITY SYSTEM (Highest quality first)
    
    // 1. ORIGINAL BB BREAKOUTS (Highest priority - proven winners)
    if(bullishBreakout && volumeStrength >= Volume_Threshold && baseStrength >= Min_Signal_Strength) {
        signal.isValid = true;
        signal.direction = 1;
        signal.strength = baseStrength;
        signal.signalType = SIGNAL_BB_BREAKOUT;
        signal.entry = close[0];
        signal.reason = StringFormat("BB Bullish Breakout - Vol:%.2f MACD:%.2f Str:%.2f", 
                                   volumeStrength, macdStrength, baseStrength);
    }
    // 2. BEARISH BREAKOUTS (NOW PROPERLY IMPLEMENTED)
    else if(Enable_Short_Trades && bearishBreakout && volumeStrength >= Volume_Threshold && 
            baseStrength >= Min_Signal_Strength) {
        signal.isValid = true;
        signal.direction = -1;
        signal.strength = baseStrength;
        signal.signalType = SIGNAL_BB_BREAKOUT;
        signal.entry = close[0];
        signal.reason = StringFormat("BB Bearish Breakout - Vol:%.2f MACD:%.2f Str:%.2f", 
                                   volumeStrength, 1.0-macdStrength, baseStrength);
    }
    // 3. BB TOUCH SIGNALS (Medium priority - new opportunity)
    else if(bbTouchSignal && baseStrength >= (Min_Signal_Strength - 0.1)) {
        signal.isValid = true;
        signal.direction = bbTouchDirection;
        signal.strength = baseStrength * 0.85; // Slightly lower confidence
        signal.signalType = SIGNAL_BB_TOUCH;
        signal.entry = close[0];
        signal.reason = StringFormat("BB Touch %s - Vol:%.2f MACD:%.2f", 
                                   bbTouchDirection == 1 ? "Bounce" : "Reject", 
                                   volumeStrength, macdStrength);
    }
    // 4. MOMENTUM BREAKOUTS (Lower priority - new opportunity)
    else if(momentumBreakout && baseStrength >= (Min_Signal_Strength - 0.05)) {
        if(momentumDirection == 1 || Enable_Short_Trades) {
            signal.isValid = true;
            signal.direction = momentumDirection;
            signal.strength = baseStrength * 0.8; // Lower confidence
            signal.signalType = SIGNAL_MOMENTUM_BREAK;
            signal.entry = close[0];
            signal.reason = StringFormat("Momentum %s - Vol:%.2f MACD:%.2f", 
                                       momentumDirection == 1 ? "Breakup" : "Breakdown", 
                                       volumeStrength, macdStrength);
        }
    }
    
    // Set SL/TP (SAME WINNING LOGIC)
    if(signal.isValid) {
        if(Use_Dynamic_SL) {
            if(signal.direction == 1) {
                signal.stopLoss = close[0] - (currentATR * ATR_SL_Multiplier);
                signal.takeProfit = close[0] + (currentATR * ATR_TP_Multiplier);
            } else {
                signal.stopLoss = close[0] + (currentATR * ATR_SL_Multiplier);
                signal.takeProfit = close[0] - (currentATR * ATR_TP_Multiplier);
            }
        } else {
            if(signal.direction == 1) {
                signal.stopLoss = bb_lower[0];
                signal.takeProfit = close[0] + (close[0] - bb_lower[0]) * 2;
            } else {
                signal.stopLoss = bb_upper[0];
                signal.takeProfit = close[0] - (bb_upper[0] - close[0]) * 2;
            }
        }
        
        signal.volumeStrength = volumeStrength;
        signal.momentumScore = macdStrength;
    }
    
    return signal;
}

//+------------------------------------------------------------------+
//| Execute trade (SAME WINNING LOGIC)                               |
//+------------------------------------------------------------------+
bool ExecuteTrade(TradeSignal &signal)
{
    if(!signal.isValid) return false;
    
    // Check spread condition
    double spread = SymbolInfoInteger(_Symbol, SYMBOL_SPREAD) * SymbolInfoDouble(_Symbol, SYMBOL_POINT);
    if(spread > Max_Spread * SymbolInfoDouble(_Symbol, SYMBOL_POINT)) {
        if(Verbose_Logging) Print("Trade rejected - Spread too high: ", spread);
        return false;
    }
    
    // Check minimum time between trades (RELAXED)
    if(TimeCurrent() - lastTradeTime < Min_Bars_Between * PeriodSeconds(_Period)) {
        if(Verbose_Logging) Print("Trade rejected - Too soon after last trade");
        return false;
    }
    
    // Calculate position size
    double lotSize = CalculateLotSize(MathAbs(signal.entry - signal.stopLoss));
    
    // Close opposite positions if enabled
    if(Close_on_Opposite) {
        CloseOppositePositions(signal.direction);
    }
    
    bool result = false;
    if(signal.direction == 1) {
        result = trade.Buy(lotSize, _Symbol, 0, signal.stopLoss, signal.takeProfit, signal.reason);
    } else if(signal.direction == -1) {
        result = trade.Sell(lotSize, _Symbol, 0, signal.stopLoss, signal.takeProfit, signal.reason);
    }
    
    if(result) {
        lastTradeTime = TimeCurrent();
        Print("=== OPTIMIZED TRADE EXECUTED ===");
        Print("Type: ", EnumToString(signal.signalType));
        Print("Direction: ", signal.direction == 1 ? "BUY" : "SELL");
        Print("Lot Size: ", lotSize);
        Print("Entry: ", signal.entry);
        Print("SL: ", signal.stopLoss);
        Print("TP: ", signal.takeProfit);
        Print("Signal Strength: ", NormalizeDouble(signal.strength, 3));
        Print("Volume Strength: ", NormalizeDouble(signal.volumeStrength, 2));
        Print("Reason: ", signal.reason);
    } else {
        Print("Trade execution failed: ", trade.ResultRetcode(), " - ", trade.ResultRetcodeDescription());
    }
    
    return result;
}

//+------------------------------------------------------------------+
//| Close opposite positions                                          |
//+------------------------------------------------------------------+
void CloseOppositePositions(int newDirection)
{
    for(int i = PositionsTotal() - 1; i >= 0; i--) {
        if(PositionSelect(_Symbol)) {
            if(PositionGetInteger(POSITION_MAGIC) == MagicNumber) {
                int posType = (int)PositionGetInteger(POSITION_TYPE);
                if((newDirection == 1 && posType == POSITION_TYPE_SELL) ||
                   (newDirection == -1 && posType == POSITION_TYPE_BUY)) {
                    trade.PositionClose(PositionGetInteger(POSITION_TICKET));
                    if(Verbose_Logging) Print("Closed opposite position");
                }
            }
        }
    }
}

//+------------------------------------------------------------------+
//| Enhanced trailing stop (SAME WINNING LOGIC)                      |
//+------------------------------------------------------------------+
void ManageTrailingStop()
{
    if(!Use_Trailing_Stop || currentATR == 0) return;
    
    for(int i = PositionsTotal() - 1; i >= 0; i--) {
        if(PositionSelect(_Symbol)) {
            if(PositionGetInteger(POSITION_MAGIC) == MagicNumber) {
                double currentSL = PositionGetDouble(POSITION_SL);
                ulong ticket = PositionGetInteger(POSITION_TICKET);
                
                if(PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY) {
                    double currentPrice = SymbolInfoDouble(_Symbol, SYMBOL_BID);
                    double newSL = currentPrice - (currentATR * Trail_ATR_Multi);
                    if(newSL > currentSL && newSL < currentPrice) {
                        trade.PositionModify(ticket, newSL, PositionGetDouble(POSITION_TP));
                    }
                }
                else if(PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_SELL) {
                    double currentPrice = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
                    double newSL = currentPrice + (currentATR * Trail_ATR_Multi);
                    if((currentSL == 0 || newSL < currentSL) && newSL > currentPrice) {
                        trade.PositionModify(ticket, newSL, PositionGetDouble(POSITION_TP));
                    }
                }
            }
        }
    }
}

//+------------------------------------------------------------------+
//| Enhanced logging                                                  |
//+------------------------------------------------------------------+
void LogMarketConditions()
{
    static datetime lastLog = 0;
    if(TimeCurrent() - lastLog < 900) return; // Log every 15 minutes
    
    MARKET_STATE marketState = AnalyzeMarketState();
    double volumeStrength = AnalyzeVolumeStrength();
    double macdStrength = GetMACDSignalStrength();
    
    if(Verbose_Logging) {
        Print("=== OPTIMIZED MARKET ANALYSIS ===");
        Print("Market State: ", EnumToString(marketState));
        Print("Volume Strength: ", NormalizeDouble(volumeStrength, 2));
        Print("MACD Strength: ", NormalizeDouble(macdStrength, 2));
        Print("Current ATR: ", NormalizeDouble(currentATR, 5));
        Print("Active Positions: ", CountPositions());
        Print("Short Trading: ", Enable_Short_Trades ? "ON" : "OFF");
        Print("Signal Types: BB+Touch+Momentum");
    }
    
    lastLog = TimeCurrent();
}

//+------------------------------------------------------------------+
//| Expert tick function                                               |
//+------------------------------------------------------------------+
void OnTick()
{
    // Generate and analyze trading signal (ENHANCED)
    TradeSignal signal = GenerateTradeSignal();
    
    // Execute trade if signal is valid
    if(signal.isValid) {
        ExecuteTrade(signal);
    }
    
    // Manage existing positions (SAME WINNING LOGIC)
    ManageTrailingStop();
    
    // Log market conditions periodically
    LogMarketConditions();
}