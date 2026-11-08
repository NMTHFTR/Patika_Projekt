from __future__ import annotations

from typing import Any, Dict, List, Optional

from database import database_connection


class InvFo:
    """Dashboard queries for the Patika product and stock tables."""

    def __init__(self, conn_str: Optional[str] = None):
        self.conn_str = conn_str

    def get_connection(self) -> Any:
        return database_connection(self.conn_str)

    def load_kpis(self) -> Dict[str, int]:
        sql = """
            SELECT
                (SELECT COUNT(*) FROM dbo.[Termék jellemzők]) AS ProductCnt,
                (SELECT COUNT(*) FROM dbo.[Konkrét termék]) AS BatchCnt,
                (SELECT COALESCE(SUM(T_db), 0) FROM dbo.[Konkrét termék]) AS StockCnt,
                (SELECT COUNT(*) FROM dbo.[Konkrét termék]
                 WHERE T_lejaratdatum < CONVERT(date, GETDATE())) AS ExpiredBatchCnt,
                (SELECT COUNT(*) FROM dbo.[Konkrét termék] WHERE T_db <= 0) AS OutOfStockBatchCnt
        """
        with self.get_connection() as cn:
            row = cn.cursor().execute(sql).fetchone()
            return {
                "ProductCnt": row.ProductCnt,
                "BatchCnt": row.BatchCnt,
                "StockCnt": row.StockCnt,
                "ExpiredBatchCnt": row.ExpiredBatchCnt,
                "OutOfStockBatchCnt": row.OutOfStockBatchCnt,
            }

    def load_top_categories(self) -> List[Dict[str, Any]]:
        sql = """
            SELECT
                COALESCE(NULLIF(LTRIM(RTRIM(T_kateg)), ''), '(nincs)') AS Category,
                COUNT(*) AS Cnt
            FROM dbo.[Termék jellemzők]
            GROUP BY COALESCE(NULLIF(LTRIM(RTRIM(T_kateg)), ''), '(nincs)')
            ORDER BY COUNT(*) DESC, Category
        """
        with self.get_connection() as cn:
            return [
                {"Category": row.Category, "Cnt": row.Cnt}
                for row in cn.cursor().execute(sql)
            ]

    def load_top_products(self) -> List[Dict[str, Any]]:
        sql = """
            SELECT
                product.T_ID AS ProductId,
                product.T_nev AS Name,
                product.T_kateg AS Category,
                COALESCE(SUM(stock.T_db), 0) AS StockCnt
            FROM dbo.[Termék jellemzők] AS product
            LEFT JOIN dbo.[Konkrét termék] AS stock ON stock.T_ID = product.T_ID
            GROUP BY product.T_ID, product.T_nev, product.T_kateg
            ORDER BY COALESCE(SUM(stock.T_db), 0) DESC, product.T_nev
        """
        with self.get_connection() as cn:
            return [
                {
                    "ProductId": row.ProductId,
                    "Name": row.Name,
                    "Category": row.Category,
                    "StockCnt": row.StockCnt,
                }
                for row in cn.cursor().execute(sql)
            ]


if __name__ == "__main__":
    print(InvFo().load_kpis())
