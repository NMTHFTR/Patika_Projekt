from __future__ import annotations

from typing import Any, Dict, List, Optional

from database import database_connection
from inv import Inv


class InvDetails:
    """Product details and stock batches from the Patika database."""

    def __init__(self, conn_str: Optional[str] = None):
        self.conn_str = conn_str

    def get_connection(self) -> Any:
        return database_connection(self.conn_str)

    def load_product(self, product_id: int) -> Optional[Dict[str, Any]]:
        sql = """
            SELECT
                T_ID AS ProductId,
                T_marka AS Brand,
                T_nev AS Name,
                T_kateg AS Category,
                T_veny AS PrescriptionRequired,
                T_mennyiseg AS PackageQuantity,
                T_mertekegyseg AS Unit,
                T_leiras AS Description,
                T_sor AS [Row],
                T_polc AS Shelf
            FROM dbo.[Termék jellemzők]
            WHERE T_ID = ?
        """
        with self.get_connection() as cn:
            row = cn.cursor().execute(sql, (product_id,)).fetchone()
            if row is None:
                return None
            return {
                "ProductId": row.ProductId,
                "Brand": row.Brand,
                "Name": row.Name,
                "Category": row.Category,
                "PrescriptionRequired": bool(row.PrescriptionRequired),
                "PackageQuantity": row.PackageQuantity,
                "Unit": row.Unit.strip(),
                "Description": row.Description,
                "Row": row.Row.strip(),
                "Shelf": row.Shelf.strip(),
            }

    def bind_batches(
        self, product_id: int, filter_text: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        parts = Inv(self.conn_str).get_parts(product_id=product_id, search=filter_text)
        return [
            {
                "BatchCode": part["PartId"],
                "Name": part["Name"],
                "Category": part["Category"],
                "Location": part["Location"],
                "ExpiryDate": part["ExpiryDate"],
                "Quantity": part["Quantity"],
            }
            for part in parts
        ]

    def delete_selected_batches(self, product_id: int, batch_codes: List[str]) -> None:
        codes = list(dict.fromkeys(code.strip() for code in batch_codes if code.strip()))
        if not codes:
            return

        placeholders = ", ".join("?" for _ in codes)
        with self.get_connection() as cn:
            cursor = cn.cursor()
            cursor.execute(
                f"""
                SELECT COUNT(*)
                FROM dbo.[Konkrét termék]
                WHERE T_ID = ? AND T_kod IN ({placeholders})
                """,
                [product_id, *codes],
            )
            if cursor.fetchone()[0] != len(codes):
                raise ValueError("Legalább egy megadott tétel nem ehhez a termékhez tartozik.")
            cursor.execute(
                f"""
                SELECT stock.T_kod
                FROM dbo.[Konkrét termék] AS stock
                WHERE stock.T_ID = ? AND stock.T_kod IN ({placeholders})
                  AND EXISTS (
                      SELECT 1 FROM dbo.[Eladások] AS sales
                      WHERE sales.T_kod = stock.T_kod
                  )
                """,
                [product_id, *codes],
            )
            sold_codes = [row.T_kod for row in cursor.fetchall()]
            if sold_codes:
                raise ValueError(
                    "Az értékesítési előzménnyel rendelkező tételek nem törölhetők: "
                    + ", ".join(sold_codes)
                )
            cursor.execute(
                f"""
                DELETE FROM dbo.[Konkrét termék]
                WHERE T_ID = ? AND T_kod IN ({placeholders})
                """,
                [product_id, *codes],
            )
            cn.commit()


if __name__ == "__main__":
    print(InvDetails().bind_batches(1))
