#!/usr/bin/env python3
"""
Cryptocurrency Trader MCP Server
Provides automated cryptocurrency trading capabilities including market analysis,
portfolio management, trading strategies, and risk management (mock implementation).
"""

import json
import logging
import uuid
import random
from datetime import datetime, timedelta
from typing import Any, Dict, List

# MCP imports
from fastmcp import FastMCP

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("cryptocurrency_trader")

# Create MCP server instance
mcp = FastMCP('cryptocurrency_trader')

# Global state
CRYPTO_LOGS = []
PORTFOLIOS = {}
TRADING_STRATEGIES = {}
MARKET_DATA = {}
TRADES = {}
ALERTS = []

def log_operation(operation: str, details: Dict[str, Any]):
    """Log cryptocurrency trading operations for audit trail"""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "operation": operation,
        "details": details,
        "status": "completed"
    }
    CRYPTO_LOGS.append(log_entry)
    logger.info(f"Cryptocurrency Trader Operation: {operation} - {details}")

def _initialize_market_data():
    """Initialize sample market data for cryptocurrencies"""
    cryptocurrencies = ["BTC", "ETH", "ADA", "DOT", "LINK", "LTC", "XRP", "DOGE"]

    for crypto in cryptocurrencies:
        base_price = random.uniform(100, 50000)
        MARKET_DATA[crypto] = {
            "symbol": crypto,
            "current_price": base_price,
            "price_24h_ago": base_price * random.uniform(0.9, 1.1),
            "volume_24h": random.uniform(1000000, 100000000),
            "market_cap": base_price * random.uniform(1000000, 100000000),
            "last_updated": datetime.now().isoformat()
        }

def _update_portfolio_value(portfolio_id: str):
    """Update the total value of a portfolio based on current market prices"""
    portfolio = PORTFOLIOS[portfolio_id]
    total_value = portfolio["cash_balance"]

    for symbol, quantity in portfolio["holdings"].items():
        if symbol in MARKET_DATA:
            total_value += quantity * MARKET_DATA[symbol]["current_price"]

    portfolio["total_value"] = total_value

def _calculate_asset_allocation(portfolio: dict) -> dict:
    """Calculate asset allocation percentages for a portfolio"""
    total_value = portfolio["total_value"]
    allocation = {"cash": (portfolio["cash_balance"] / total_value) * 100}

    for symbol, quantity in portfolio["holdings"].items():
        if symbol in MARKET_DATA:
            holding_value = quantity * MARKET_DATA[symbol]["current_price"]
            allocation[symbol] = (holding_value / total_value) * 100

    return {k: round(v, 2) for k, v in allocation.items()}

# Initialize market data
_initialize_market_data()

@mcp.tool()
def create_portfolio(portfolio_name: str, initial_balance: float = 10000.0, base_currency: str = "USD") -> dict:
    """Create a new cryptocurrency portfolio"""
    portfolio_id = str(uuid.uuid4())[:8]

    portfolio = {
        "portfolio_id": portfolio_id,
        "name": portfolio_name,
        "base_currency": base_currency,
        "cash_balance": initial_balance,
        "total_value": initial_balance,
        "holdings": {},
        "created_at": datetime.now().isoformat(),
        "performance": {
            "total_return": 0.0,
            "total_return_percentage": 0.0,
            "daily_pnl": 0.0
        }
    }

    PORTFOLIOS[portfolio_id] = portfolio

    log_operation("create_portfolio", {
        "portfolio_name": portfolio_name,
        "portfolio_id": portfolio_id,
        "initial_balance": initial_balance
    })

    return {
        "portfolio_id": portfolio_id,
        "name": portfolio_name,
        "status": "created",
        "initial_balance": initial_balance,
        "base_currency": base_currency
    }

@mcp.tool()
def execute_trade(portfolio_id: str, symbol: str, trade_type: str, quantity: float, order_type: str = "market") -> dict:
    """Execute a cryptocurrency trade (BUY/SELL)"""
    if portfolio_id not in PORTFOLIOS:
        return {"error": f"Portfolio {portfolio_id} not found"}

    if symbol not in MARKET_DATA:
        return {"error": f"Cryptocurrency {symbol} not supported"}

    portfolio = PORTFOLIOS[portfolio_id]
    current_price = MARKET_DATA[symbol]["current_price"]
    trade_id = str(uuid.uuid4())[:8]

    # Calculate trade value
    trade_value = quantity * current_price

    # Validate trade
    if trade_type.upper() == "BUY":
        if trade_value > portfolio["cash_balance"]:
            return {"error": "Insufficient cash balance for buy order"}

        # Execute buy
        portfolio["cash_balance"] -= trade_value
        if symbol not in portfolio["holdings"]:
            portfolio["holdings"][symbol] = 0
        portfolio["holdings"][symbol] += quantity

    elif trade_type.upper() == "SELL":
        current_holdings = portfolio["holdings"].get(symbol, 0)
        if quantity > current_holdings:
            return {"error": f"Insufficient {symbol} holdings for sell order"}

        # Execute sell
        portfolio["cash_balance"] += trade_value
        portfolio["holdings"][symbol] -= quantity
        if portfolio["holdings"][symbol] == 0:
            del portfolio["holdings"][symbol]

    else:
        return {"error": "Trade type must be BUY or SELL"}

    # Record trade
    trade = {
        "trade_id": trade_id,
        "portfolio_id": portfolio_id,
        "symbol": symbol,
        "trade_type": trade_type.upper(),
        "quantity": quantity,
        "price": current_price,
        "trade_value": trade_value,
        "order_type": order_type,
        "status": "executed",
        "timestamp": datetime.now().isoformat()
    }
    TRADES[trade_id] = trade

    # Update portfolio value
    _update_portfolio_value(portfolio_id)

    log_operation("execute_trade", {
        "trade_id": trade_id,
        "symbol": symbol,
        "trade_type": trade_type,
        "quantity": quantity,
        "value": trade_value
    })

    return {
        "trade_id": trade_id,
        "status": "executed",
        "symbol": symbol,
        "trade_type": trade_type,
        "quantity": quantity,
        "price": current_price,
        "trade_value": trade_value
    }

@mcp.tool()
def analyze_market(symbol: str = None, analysis_type: str = "technical") -> dict:
    """Analyze cryptocurrency market data and trends"""
    if symbol and symbol not in MARKET_DATA:
        return {"error": f"Cryptocurrency {symbol} not found"}

    if symbol:
        # Analyze specific cryptocurrency
        crypto_data = MARKET_DATA[symbol]
        price_change_24h = crypto_data["current_price"] - crypto_data["price_24h_ago"]
        price_change_percentage = (price_change_24h / crypto_data["price_24h_ago"]) * 100

        # Generate mock technical indicators
        analysis = {
            "symbol": symbol,
            "current_price": crypto_data["current_price"],
            "price_change_24h": price_change_24h,
            "price_change_percentage": round(price_change_percentage, 2),
            "volume_24h": crypto_data["volume_24h"],
            "market_cap": crypto_data["market_cap"],
            "technical_indicators": {
                "rsi": round(random.uniform(20, 80), 2),
                "macd": round(random.uniform(-1, 1), 4),
                "sma_20": crypto_data["current_price"] * random.uniform(0.95, 1.05),
                "sma_50": crypto_data["current_price"] * random.uniform(0.9, 1.1)
            },
            "sentiment": random.choice(["bullish", "bearish", "neutral"]),
            "recommendation": random.choice(["buy", "sell", "hold"])
        }
    else:
        # Market overview
        total_market_cap = sum(data["market_cap"] for data in MARKET_DATA.values())
        top_performers = sorted(
            MARKET_DATA.items(),
            key=lambda x: (x[1]["current_price"] - x[1]["price_24h_ago"]) / x[1]["price_24h_ago"],
            reverse=True
        )[:3]

        analysis = {
            "market_overview": {
                "total_market_cap": total_market_cap,
                "total_volume_24h": sum(data["volume_24h"] for data in MARKET_DATA.values()),
                "market_sentiment": random.choice(["fear", "greed", "neutral"]),
                "fear_greed_index": random.randint(0, 100)
            },
            "top_performers": [
                {
                    "symbol": symbol,
                    "current_price": data["current_price"],
                    "price_change_percentage": round(
                        ((data["current_price"] - data["price_24h_ago"]) / data["price_24h_ago"]) * 100, 2
                    )
                }
                for symbol, data in top_performers
            ]
        }

    log_operation("analyze_market", {"symbol": symbol, "analysis_type": analysis_type})

    return analysis

@mcp.tool()
def create_trading_strategy(strategy_name: str, strategy_config: dict) -> dict:
    """Create a new automated trading strategy"""
    strategy_id = str(uuid.uuid4())[:8]

    strategy = {
        "strategy_id": strategy_id,
        "name": strategy_name,
        "config": strategy_config,
        "status": "active",
        "created_at": datetime.now().isoformat(),
        "performance": {
            "total_trades": 0,
            "successful_trades": 0,
            "total_profit_loss": 0.0
        }
    }

    TRADING_STRATEGIES[strategy_id] = strategy

    log_operation("create_trading_strategy", {
        "strategy_name": strategy_name,
        "strategy_id": strategy_id
    })

    return {
        "strategy_id": strategy_id,
        "name": strategy_name,
        "status": "created",
        "config": strategy_config
    }

@mcp.tool()
def get_portfolio_performance(portfolio_id: str) -> dict:
    """Get detailed portfolio performance and analytics"""
    if portfolio_id not in PORTFOLIOS:
        return {"error": f"Portfolio {portfolio_id} not found"}

    portfolio = PORTFOLIOS[portfolio_id]
    _update_portfolio_value(portfolio_id)

    # Calculate performance metrics
    initial_value = 10000.0  # Assume initial value for now
    current_value = portfolio["total_value"]
    total_return = current_value - initial_value
    total_return_percentage = (total_return / initial_value) * 100

    # Get portfolio trades
    portfolio_trades = [
        trade for trade in TRADES.values()
        if trade["portfolio_id"] == portfolio_id
    ]

    performance = {
        "portfolio_id": portfolio_id,
        "name": portfolio["name"],
        "current_value": current_value,
        "cash_balance": portfolio["cash_balance"],
        "holdings": portfolio["holdings"],
        "performance_metrics": {
            "total_return": total_return,
            "total_return_percentage": round(total_return_percentage, 2),
            "total_trades": len(portfolio_trades),
            "daily_pnl": portfolio["performance"]["daily_pnl"]
        },
        "asset_allocation": _calculate_asset_allocation(portfolio),
        "last_updated": datetime.now().isoformat()
    }

    log_operation("get_portfolio_performance", {"portfolio_id": portfolio_id})

    return performance

@mcp.tool()
def get_market_data(symbol: str = None) -> dict:
    """Get current market data for cryptocurrencies"""
    if symbol:
        if symbol not in MARKET_DATA:
            return {"error": f"Cryptocurrency {symbol} not found"}

        data = MARKET_DATA[symbol].copy()
        data["price_change_24h"] = data["current_price"] - data["price_24h_ago"]
        data["price_change_percentage"] = round(
            ((data["current_price"] - data["price_24h_ago"]) / data["price_24h_ago"]) * 100, 2
        )

        log_operation("get_market_data", {"symbol": symbol})
        return data
    else:
        # Return all market data
        all_data = {}
        for symbol, data in MARKET_DATA.items():
            market_info = data.copy()
            market_info["price_change_24h"] = data["current_price"] - data["price_24h_ago"]
            market_info["price_change_percentage"] = round(
                ((data["current_price"] - data["price_24h_ago"]) / data["price_24h_ago"]) * 100, 2
            )
            all_data[symbol] = market_info

        log_operation("get_market_data", {"symbols": "all"})
        return {"market_data": all_data, "count": len(all_data)}

@mcp.tool()
def get_crypto_logs(limit: int = 50) -> dict:
    """Retrieve cryptocurrency trading operation logs"""
    recent_logs = CRYPTO_LOGS[-limit:] if limit > 0 else CRYPTO_LOGS

    return {
        "logs": recent_logs,
        "total_operations": len(CRYPTO_LOGS),
        "returned_count": len(recent_logs)
    }

if __name__ == "__main__":
    mcp.run()
