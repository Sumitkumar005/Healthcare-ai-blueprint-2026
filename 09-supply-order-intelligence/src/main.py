"""
Supply Order Intelligence System.
"""

import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from .inventory_manager import InventoryManager
from .price_comparison import PriceComparator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base = declarative_base()
db_path = Path(__file__).parent.parent / "inventory.db"
engine = create_engine(f"sqlite:///{db_path}", echo=False)
SessionLocal = sessionmaker(bind=engine)
Base.metadata.create_all(engine)

app = FastAPI(title="Supply Order Intelligence", version="1.0.0")
inventory = InventoryManager()
price_comparator = PriceComparator()


class SupplyUsageRequest(BaseModel):
    supply_name: str
    quantity_used: int


@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve dashboard."""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Supply Order Intelligence</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 1200px; margin: 50px auto; padding: 20px; }
            table { width: 100%; border-collapse: collapse; margin: 20px 0; }
            th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
            th { background: #007bff; color: white; }
            .low-stock { background: #ffebee; }
            button { background: #28a745; color: white; padding: 8px 15px; border: none; cursor: pointer; }
        </style>
    </head>
    <body>
        <h1>Supply Order Intelligence Dashboard</h1>
        <div id="inventory"></div>
        <div id="reorder-alerts"></div>
        <script>
            async function loadInventory() {
                const response = await fetch('/inventory');
                const data = await response.json();
                let html = '<h2>Current Inventory</h2><table><tr><th>Supply</th><th>Current Stock</th><th>Reorder Point</th><th>Status</th></tr>';
                data.forEach(item => {
                    const status = item.current_stock < item.reorder_point ? 'LOW STOCK' : 'OK';
                    const rowClass = item.current_stock < item.reorder_point ? 'low-stock' : '';
                    html += `<tr class="${rowClass}"><td>${item.name}</td><td>${item.current_stock}</td><td>${item.reorder_point}</td><td>${status}</td></tr>`;
                });
                html += '</table>';
                document.getElementById('inventory').innerHTML = html;
            }
            loadInventory();
        </script>
    </body>
    </html>
    """
    return html


@app.get("/inventory")
async def get_inventory():
    """Get current inventory status."""
    return inventory.get_inventory_status()


@app.post("/usage")
async def record_usage(request: SupplyUsageRequest):
    """Record supply usage."""
    inventory.record_usage(request.supply_name, request.quantity_used)
    return {"status": "success"}


@app.get("/reorder-suggestions")
async def get_reorder_suggestions():
    """Get reorder suggestions with price comparison."""
    suggestions = inventory.get_reorder_suggestions()
    for suggestion in suggestions:
        suggestion['prices'] = price_comparator.compare_prices(suggestion['supply_name'])
    return suggestions


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

