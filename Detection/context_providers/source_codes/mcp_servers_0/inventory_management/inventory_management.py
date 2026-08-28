#!/usr/bin/env python3
"""
Inventory Management MCP Server
Provides e-commerce and retail inventory tracking including stock management,
supplier coordination, demand forecasting, and automated reordering.
"""

import asyncio
import json
import sys
import logging
import uuid
import random
from datetime import datetime, timedelta
from typing import Any, Dict, List

# MCP imports
from fastmcp import FastMCP

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("inventory_management")

# Create MCP server instance
mcp = FastMCP('inventory_management')

class InventoryManagementSystem:
    def __init__(self):
        self.logs = []
        self.products = {}
        self.suppliers = {}
        self.warehouses = {}
        self.stock_movements = {}
        self.purchase_orders = {}
        self.low_stock_alerts = []

        # Initialize with sample data
        self._initialize_sample_data()

    def log_operation(self, operation: str, details: Dict[str, Any]):
        """Log inventory operations for audit trail"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "details": details,
            "status": "completed"
        }
        self.logs.append(log_entry)
        logger.info(f"Inventory Management Operation: {operation} - {details}")

    def _initialize_sample_data(self):
        """Initialize system with sample products and suppliers"""
        # Create sample warehouses
        self.warehouses["WH001"] = {
            "warehouse_id": "WH001",
            "name": "Main Warehouse",
            "location": "New York, NY",
            "capacity": 10000,
            "current_utilization": 0
        }

        # Create sample suppliers
        supplier_id = str(uuid.uuid4())
        self.suppliers[supplier_id] = {
            "supplier_id": supplier_id,
            "name": "Global Supply Co.",
            "contact_email": "orders@globalsupply.com",
            "lead_time_days": 7,
            "reliability_score": 0.95,
            "payment_terms": "NET30"
        }

    @mcp.tool()
    def add_product(self, product_info: Dict) -> Dict[str, Any]:
        """Add a new product to inventory system"""
        product_id = str(uuid.uuid4())

        product = {
            "product_id": product_id,
            "sku": product_info.get("sku", f"SKU-{product_id[:8]}"),
            "name": product_info["name"],
            "description": product_info.get("description", ""),
            "category": product_info.get("category", "general"),
            "unit_cost": product_info.get("unit_cost", 0.0),
            "selling_price": product_info.get("selling_price", 0.0),
            "supplier_id": product_info.get("supplier_id"),
            "reorder_point": product_info.get("reorder_point", 10),
            "reorder_quantity": product_info.get("reorder_quantity", 100),
            "created_at": datetime.now().isoformat(),
            "status": "active",
            "stock_levels": {},  # warehouse_id -> quantity
            "total_stock": 0,
            "reserved_stock": 0,
            "available_stock": 0
        }

        # Initialize stock levels for all warehouses
        for warehouse_id in self.warehouses.keys():
            product["stock_levels"][warehouse_id] = 0

        self.products[product_id] = product

        result = {
            "product_id": product_id,
            "sku": product["sku"],
            "name": product["name"],
            "status": "added",
            "initial_stock": 0,
            "reorder_point": product["reorder_point"]
        }

        self.log_operation("add_product", {
            "product_id": product_id,
            "sku": product["sku"],
            "name": product["name"],
            "category": product["category"]
        })

        return result

    @mcp.tool()
    def update_stock(self, product_id: str, warehouse_id: str, quantity_change: int, movement_type: str) -> Dict[str, Any]:
        """Update stock levels for a product in a specific warehouse"""
        if product_id not in self.products:
            raise ValueError(f"Product {product_id} not found")
        if warehouse_id not in self.warehouses:
            raise ValueError(f"Warehouse {warehouse_id} not found")

        product = self.products[product_id]
        movement_id = str(uuid.uuid4())

        # Record stock movement
        movement = {
            "movement_id": movement_id,
            "product_id": product_id,
            "warehouse_id": warehouse_id,
            "movement_type": movement_type,  # "inbound", "outbound", "adjustment", "transfer"
            "quantity": quantity_change,
            "timestamp": datetime.now().isoformat(),
            "reference": f"REF-{movement_id[:8]}",
            "notes": ""
        }

        # Update stock levels
        old_quantity = product["stock_levels"][warehouse_id]
        new_quantity = max(0, old_quantity + quantity_change)
        product["stock_levels"][warehouse_id] = new_quantity

        # Recalculate totals
        product["total_stock"] = sum(product["stock_levels"].values())
        product["available_stock"] = product["total_stock"] - product["reserved_stock"]

        self.stock_movements[movement_id] = movement

        # Check for low stock alerts
        if new_quantity <= product["reorder_point"] and movement_type == "outbound":
            self._create_low_stock_alert(product_id, warehouse_id, new_quantity)

        result = {
            "movement_id": movement_id,
            "product_id": product_id,
            "sku": product["sku"],
            "warehouse_id": warehouse_id,
            "old_quantity": old_quantity,
            "new_quantity": new_quantity,
            "movement_type": movement_type,
            "total_stock": product["total_stock"],
            "low_stock_alert": new_quantity <= product["reorder_point"]
        }

        self.log_operation("update_stock", {
            "movement_id": movement_id,
            "product_id": product_id,
            "warehouse_id": warehouse_id,
            "quantity_change": quantity_change,
            "movement_type": movement_type
        })

        return result

    def _create_low_stock_alert(self, product_id: str, warehouse_id: str, current_quantity: int):
        """Create a low stock alert"""
        product = self.products[product_id]

        alert = {
            "alert_id": str(uuid.uuid4()),
            "product_id": product_id,
            "sku": product["sku"],
            "product_name": product["name"],
            "warehouse_id": warehouse_id,
            "current_quantity": current_quantity,
            "reorder_point": product["reorder_point"],
            "suggested_reorder_quantity": product["reorder_quantity"],
            "created_at": datetime.now().isoformat(),
            "status": "active",
            "priority": "high" if current_quantity == 0 else "medium"
        }

        self.low_stock_alerts.append(alert)

    @mcp.tool()
    def create_purchase_order(self, order_data: Dict) -> Dict[str, Any]:
        """Create a purchase order for inventory replenishment"""
        po_id = str(uuid.uuid4())

        # Calculate total cost
        total_cost = 0
        line_items = []

        for item in order_data["items"]:
            product_id = item["product_id"]
            if product_id not in self.products:
                raise ValueError(f"Product {product_id} not found")

            product = self.products[product_id]
            quantity = item["quantity"]
            unit_cost = item.get("unit_cost", product["unit_cost"])
            line_total = quantity * unit_cost

            line_item = {
                "product_id": product_id,
                "sku": product["sku"],
                "product_name": product["name"],
                "quantity": quantity,
                "unit_cost": unit_cost,
                "line_total": line_total
            }

            line_items.append(line_item)
            total_cost += line_total

        purchase_order = {
            "po_id": po_id,
            "supplier_id": order_data["supplier_id"],
            "warehouse_id": order_data["warehouse_id"],
            "order_date": datetime.now().isoformat(),
            "expected_delivery": (datetime.now() + timedelta(days=7)).isoformat(),
            "status": "pending",
            "line_items": line_items,
            "subtotal": total_cost,
            "tax_amount": total_cost * 0.08,  # 8% tax
            "total_amount": total_cost * 1.08,
            "notes": order_data.get("notes", "")
        }

        self.purchase_orders[po_id] = purchase_order

        result = {
            "po_id": po_id,
            "supplier_id": order_data["supplier_id"],
            "status": "created",
            "line_items_count": len(line_items),
            "total_amount": round(purchase_order["total_amount"], 2),
            "expected_delivery": purchase_order["expected_delivery"]
        }

        self.log_operation("create_purchase_order", {
            "po_id": po_id,
            "supplier_id": order_data["supplier_id"],
            "total_amount": purchase_order["total_amount"],
            "items_count": len(line_items)
        })

        return result

    def forecast_demand(self, product_id: str, forecast_days: int = 30) -> Dict[str, Any]:
        """Forecast demand for a product based on historical data"""
        if product_id not in self.products:
            raise ValueError(f"Product {product_id} not found")

        product = self.products[product_id]

        # Mock demand forecasting based on historical movements
        product_movements = [
            movement for movement in self.stock_movements.values()
            if movement["product_id"] == product_id and movement["movement_type"] == "outbound"
        ]

        # Calculate daily average demand
        if product_movements:
            total_outbound = sum(abs(movement["quantity"]) for movement in product_movements)
            days_of_data = len(set(movement["timestamp"][:10] for movement in product_movements))
            daily_avg_demand = total_outbound / max(1, days_of_data)
        else:
            # Use random baseline for products without history
            daily_avg_demand = random.uniform(5, 25)

        # Apply seasonality and trend factors
        seasonality_factor = random.uniform(0.8, 1.2)
        trend_factor = random.uniform(0.95, 1.05)

        forecasted_total_demand = int(daily_avg_demand * forecast_days * seasonality_factor * trend_factor)

        # Calculate recommendations
        current_stock = product["available_stock"]
        shortage_risk = max(0, forecasted_total_demand - current_stock)

        forecast = {
            "product_id": product_id,
            "sku": product["sku"],
            "product_name": product["name"],
            "forecast_period_days": forecast_days,
            "current_stock": current_stock,
            "daily_avg_demand": round(daily_avg_demand, 1),
            "forecasted_total_demand": forecasted_total_demand,
            "shortage_risk": shortage_risk,
            "recommended_order_quantity": max(0, shortage_risk + product["reorder_quantity"]),
            "forecast_accuracy_estimate": random.uniform(0.75, 0.95),
            "generated_at": datetime.now().isoformat()
        }

        self.log_operation("forecast_demand", {
            "product_id": product_id,
            "forecast_days": forecast_days,
            "forecasted_demand": forecasted_total_demand,
            "shortage_risk": shortage_risk
        })

        return forecast

# Create global server instance
INVENTORY_SYSTEM = InventoryManagementSystem()

@mcp.tool()
def get_inventory_logs(limit: int = 50) -> dict:
    """Get inventory management operation logs"""
    recent_logs = INVENTORY_SYSTEM.logs[-limit:]
    return {
        "logs": recent_logs,
        "count": len(recent_logs),
        "retrieved_at": datetime.now().isoformat()
    }

@mcp.tool()
def add_product(product_info: dict) -> dict:
    """Add a new product to inventory system"""
    return INVENTORY_SYSTEM.add_product(product_info)

@mcp.tool()
def update_stock(product_id: str, warehouse_id: str, quantity_change: int, movement_type: str) -> dict:
    """Update stock levels for a product in a specific warehouse"""
    return INVENTORY_SYSTEM.update_stock(product_id, warehouse_id, quantity_change, movement_type)

@mcp.tool()
def create_purchase_order(order_data: dict) -> dict:
    """Create a purchase order for inventory replenishment"""
    return INVENTORY_SYSTEM.create_purchase_order(order_data)

@mcp.tool()
def forecast_demand(product_id: str, forecast_days: int = 30) -> dict:
    """Forecast demand for a product based on historical data"""
    return INVENTORY_SYSTEM.forecast_demand(product_id, forecast_days)

@mcp.tool()
def get_low_stock_alerts(priority: str = None) -> dict:
    """Get all active low stock alerts"""
    alerts = [alert for alert in INVENTORY_SYSTEM.low_stock_alerts
              if not priority or alert.get("priority") == priority]
    return {"alerts": alerts, "count": len(alerts)}

@mcp.tool()
def generate_inventory_report(report_type: str = "summary") -> dict:
    """Generate comprehensive inventory reports"""
    return {
        "report_type": report_type,
        "total_products": len(INVENTORY_SYSTEM.products),
        "total_warehouses": len(INVENTORY_SYSTEM.warehouses),
        "low_stock_count": len(INVENTORY_SYSTEM.low_stock_alerts),
        "generated_at": datetime.now().isoformat()
    }
if __name__ == "__main__":
    mcp.run()
