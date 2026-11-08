from __future__ import annotations

from typing import Any, Dict, List, Optional

from database import database_connection


class InvProjects:
    """Product catalog operations (kept under the original module/class name)."""

    def __init__(self, conn_str: Optional[str] = None):
        self.conn_str = conn_str

    def get_connection(self) -> Any:
        return database_connection(self.conn_str)

    def bind(self, filter_text: Optional[str] = None) -> List[Dict[str, Any]]:
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
                T_sor AS Row,
                T_polc AS Shelf
            FROM dbo.[Termék jellemzők]
        """
        params: List[Any] = []
        if filter_text and filter_text.strip():
            sql += " WHERE T_nev LIKE ? OR T_marka LIKE ? OR T_kateg LIKE ?"
            query = f"%{filter_text.strip()}%"
            params.extend((query, query, query))
        sql += " ORDER BY T_nev"

        with self.get_connection() as cn:
            return [
                {
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
                for row in cn.cursor().execute(sql, params)
            ]

    @staticmethod
    def _validate_product(
        brand: str,
        name: str,
        category: str,
        package_quantity: int,
        unit: str,
        row: str,
        shelf: str,
    ) -> None:
        if not name or not name.strip():
            raise ValueError("A terméknév kötelező.")
        if not brand or not brand.strip():
            raise ValueError("A márka kötelező.")
        if not category or not category.strip():
            raise ValueError("A kategória kötelező.")
        if package_quantity < 0:
            raise ValueError("A csomag mennyisége nem lehet negatív.")
        if not unit or not unit.strip():
            raise ValueError("A mértékegység kötelező.")
        if not row or not row.strip() or not shelf or not shelf.strip():
            raise ValueError("A sor és a polc megadása kötelező.")

    def add_product(
        self,
        brand: str,
        name: str,
        category: str,
        prescription_required: bool,
        package_quantity: int,
        unit: str,
        description: Optional[str],
        row: str,
        shelf: str,
    ) -> int:
        self._validate_product(brand, name, category, package_quantity, unit, row, shelf)
        sql = """
            INSERT INTO dbo.[Termék jellemzők](
                T_marka, T_nev, T_kateg, T_veny, T_mennyiseg,
                T_mertekegyseg, T_leiras, T_sor, T_polc
            )
            OUTPUT INSERTED.T_ID
            VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        with self.get_connection() as cn:
            cursor = cn.cursor()
            product_id = cursor.execute(
                sql,
                (
                    brand.strip(),
                    name.strip(),
                    category.strip(),
                    bool(prescription_required),
                    package_quantity,
                    unit.strip(),
                    description.strip() if description and description.strip() else None,
                    row.strip(),
                    shelf.strip(),
                ),
            ).fetchone()[0]
            cn.commit()
            return int(product_id)

    def update_product(
        self,
        product_id: int,
        brand: str,
        name: str,
        category: str,
        prescription_required: bool,
        package_quantity: int,
        unit: str,
        description: Optional[str],
        row: str,
        shelf: str,
    ) -> None:
        self._validate_product(brand, name, category, package_quantity, unit, row, shelf)
        sql = """
            UPDATE dbo.[Termék jellemzők]
            SET T_marka = ?, T_nev = ?, T_kateg = ?, T_veny = ?,
                T_mennyiseg = ?, T_mertekegyseg = ?, T_leiras = ?, T_sor = ?, T_polc = ?
            WHERE T_ID = ?
        """
        with self.get_connection() as cn:
            cursor = cn.cursor()
            cursor.execute(
                sql,
                (
                    brand.strip(),
                    name.strip(),
                    category.strip(),
                    bool(prescription_required),
                    package_quantity,
                    unit.strip(),
                    description.strip() if description and description.strip() else None,
                    row.strip(),
                    shelf.strip(),
                    product_id,
                ),
            )
            if cursor.rowcount == 0:
                raise KeyError(f"Nem található termék: {product_id}")
            cn.commit()

    def delete_product(self, product_id: int) -> None:
        with self.get_connection() as cn:
            cursor = cn.cursor()
            cursor.execute(
                """
                SELECT TOP 1 stock.T_kod
                FROM dbo.[Konkrét termék] AS stock
                WHERE stock.T_ID = ?
                  AND EXISTS (
                      SELECT 1 FROM dbo.[Eladások] AS sales
                      WHERE sales.T_kod = stock.T_kod
                  )
                """,
                (product_id,),
            )
            sold_batch = cursor.fetchone()
            if sold_batch is not None:
                raise ValueError(
                    f"A termék nem törölhető, mert értékesítési előzménye van ({sold_batch.T_kod})."
                )

            cursor.execute("DELETE FROM dbo.[Konkrét termék] WHERE T_ID = ?", (product_id,))
            cursor.execute("DELETE FROM dbo.[Termék jellemzők] WHERE T_ID = ?", (product_id,))
            if cursor.rowcount == 0:
                raise KeyError(f"Nem található termék: {product_id}")
            cn.commit()

    def load_kpis(self) -> Dict[str, int]:
        sql = """
            SELECT
                COUNT(*) AS ProductCnt,
                SUM(CASE WHEN T_veny = 1 THEN 1 ELSE 0 END) AS PrescriptionProductCnt,
                COUNT(DISTINCT T_kateg) AS CategoryCnt
            FROM dbo.[Termék jellemzők]
        """
        with self.get_connection() as cn:
            row = cn.cursor().execute(sql).fetchone()
            return {
                "ProductCnt": row.ProductCnt,
                "PrescriptionProductCnt": row.PrescriptionProductCnt or 0,
                "CategoryCnt": row.CategoryCnt,
            }


if __name__ == "__main__":
    print(InvProjects().bind())
