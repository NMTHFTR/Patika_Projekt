from __future__ import annotations

from datetime import date
from typing import Any, Dict, Iterable, List, Optional

from database import database_connection


class Inv:
    """Inventory operations backed by the Patika product and stock tables."""

    def __init__(self, conn_str: Optional[str] = None):
        self.conn_str = conn_str

    def get_connection(self) -> Any:
        return database_connection(self.conn_str)

    def bind_products(self) -> List[Dict[str, Any]]:
        sql = """
            SELECT T_ID AS ProductId, T_nev AS Name
            FROM dbo.[Termék jellemzők]
            ORDER BY T_nev
        """
        with self.get_connection() as cn:
            return [
                {"ProductId": row.ProductId, "Name": row.Name}
                for row in cn.cursor().execute(sql)
            ]

    def bind_categories(self) -> List[str]:
        sql = """
            SELECT DISTINCT T_kateg
            FROM dbo.[Termék jellemzők]
            WHERE NULLIF(LTRIM(RTRIM(T_kateg)), '') IS NOT NULL
            ORDER BY T_kateg
        """
        with self.get_connection() as cn:
            return [row[0].strip() for row in cn.cursor().execute(sql)]

    def get_parts(
        self,
        search: Optional[str] = None,
        category: Optional[str] = None,
        status: Optional[str] = None,
        product_id: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        sql = """
            SELECT
                stock.T_kod AS PartId,
                stock.T_kod AS Barcode,
                product.T_nev AS Name,
                product.T_kateg AS Category,
                CONCAT(RTRIM(product.T_sor), ' / ', RTRIM(product.T_polc)) AS Location,
                stock.T_lejaratdatum AS ExpiryDate,
                stock.T_ID AS ProductId,
                product.T_nev AS ProductName,
                stock.T_db AS Quantity
            FROM dbo.[Konkrét termék] AS stock
            INNER JOIN dbo.[Termék jellemzők] AS product ON product.T_ID = stock.T_ID
            WHERE 1 = 1
        """
        params: List[Any] = []

        if search and search.strip():
            sql += " AND (product.T_nev LIKE ? OR stock.T_kod LIKE ? OR product.T_marka LIKE ?)"
            query = f"%{search.strip()}%"
            params.extend((query, query, query))

        if category and category.strip():
            sql += " AND product.T_kateg = ?"
            params.append(category.strip())

        if status:
            if status == "in_stock":
                sql += " AND stock.T_db > 0 AND stock.T_lejaratdatum >= CONVERT(date, GETDATE())"
            elif status == "out_of_stock":
                sql += " AND stock.T_db <= 0"
            elif status == "expired":
                sql += " AND stock.T_lejaratdatum < CONVERT(date, GETDATE())"
            else:
                raise ValueError("A státusz csak in_stock, out_of_stock vagy expired lehet.")

        if product_id is not None:
            sql += " AND stock.T_ID = ?"
            params.append(product_id)

        sql += " ORDER BY product.T_kateg, product.T_nev, stock.T_lejaratdatum"

        with self.get_connection() as cn:
            return [
                {
                    "PartId": row.PartId,
                    "Barcode": row.Barcode,
                    "Name": row.Name,
                    "Category": row.Category,
                    "Location": row.Location.strip(),
                    "ExpiryDate": row.ExpiryDate,
                    "ProductId": row.ProductId,
                    "ProductName": row.ProductName,
                    "Quantity": row.Quantity,
                }
                for row in cn.cursor().execute(sql, params)
            ]

    def get_parts_by_ids(self, ids: Iterable[str]) -> List[Dict[str, Any]]:
        batch_codes = list(dict.fromkeys(code.strip() for code in ids if code.strip()))
        if not batch_codes:
            return []

        placeholders = ", ".join("?" for _ in batch_codes)
        sql = f"""
            SELECT
                stock.T_kod AS PartId,
                stock.T_kod AS Barcode,
                product.T_nev AS Name,
                product.T_kateg AS Category,
                CONCAT(RTRIM(product.T_sor), ' / ', RTRIM(product.T_polc)) AS Location,
                stock.T_lejaratdatum AS ExpiryDate,
                stock.T_ID AS ProductId,
                stock.T_db AS Quantity
            FROM dbo.[Konkrét termék] AS stock
            INNER JOIN dbo.[Termék jellemzők] AS product ON product.T_ID = stock.T_ID
            WHERE stock.T_kod IN ({placeholders})
        """
        with self.get_connection() as cn:
            return [
                {
                    "PartId": row.PartId,
                    "Barcode": row.Barcode,
                    "Name": row.Name,
                    "Category": row.Category,
                    "Location": row.Location.strip(),
                    "ExpiryDate": row.ExpiryDate,
                    "ProductId": row.ProductId,
                    "Quantity": row.Quantity,
                }
                for row in cn.cursor().execute(sql, batch_codes)
            ]

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

    def build_groups(self, parts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        grouped: Dict[int, List[Dict[str, Any]]] = {}
        for part in parts:
            product_id = int(part["ProductId"])
            grouped.setdefault(product_id, []).append(part)

        result: List[Dict[str, Any]] = []
        for product_id, batches in sorted(
            grouped.items(),
            key=lambda item: (
                -sum(int(batch.get("Quantity") or 0) for batch in item[1]),
                str(item[0]),
            ),
        ):
            sample = batches[0]
            result.append(
                {
                    "ProductId": product_id,
                    "Count": sum(int(batch.get("Quantity") or 0) for batch in batches),
                    "BatchCount": len(batches),
                    "SampleName": str(sample.get("Name") or "").strip(),
                    "Category": sample.get("Category"),
                    "KeySafe": self.make_safe_key(str(product_id)),
                }
            )
        return result

    @staticmethod
    def make_safe_key(value: str) -> str:
        if not value:
            return "empty"
        chars = []
        for ch in value:
            ok = ("a" <= ch <= "z") or ("A" <= ch <= "Z") or ("0" <= ch <= "9") or ch in ("-", "_")
            chars.append(ch if ok else "_")
        return "".join(chars)

    def add_stock_batch(
        self,
        product_id: int,
        batch_code: str,
        expiry_date: date,
        quantity: int,
    ) -> None:
        if not batch_code or not batch_code.strip():
            raise ValueError("A tételkód kötelező.")
        if quantity < 0:
            raise ValueError("A készletmennyiség nem lehet negatív.")

        sql = """
            INSERT INTO dbo.[Konkrét termék](T_kod, T_ID, T_lejaratdatum, T_db)
            VALUES(?, ?, ?, ?)
        """
        with self.get_connection() as cn:
            cn.cursor().execute(sql, (batch_code.strip(), product_id, expiry_date, quantity))
            cn.commit()

    def update_batch_quantity(self, batch_code: str, quantity: int) -> None:
        if quantity < 0:
            raise ValueError("A készletmennyiség nem lehet negatív.")

        with self.get_connection() as cn:
            cursor = cn.cursor()
            cursor.execute(
                "UPDATE dbo.[Konkrét termék] SET T_db = ? WHERE T_kod = ?",
                (quantity, batch_code),
            )
            if cursor.rowcount == 0:
                raise KeyError(f"Nem található tétel: {batch_code}")
            cn.commit()

    def delete_batches(self, batch_codes: Iterable[str]) -> None:
        codes = list(dict.fromkeys(code.strip() for code in batch_codes if code.strip()))
        if not codes:
            return

        placeholders = ", ".join("?" for _ in codes)
        with self.get_connection() as cn:
            cursor = cn.cursor()
            cursor.execute(
                f"""
                SELECT stock.T_kod
                FROM dbo.[Konkrét termék] AS stock
                WHERE stock.T_kod IN ({placeholders})
                  AND EXISTS (
                      SELECT 1 FROM dbo.[Eladások] AS sales
                      WHERE sales.T_kod = stock.T_kod
                  )
                """,
                codes,
            )
            sold_codes = [row.T_kod for row in cursor.fetchall()]
            if sold_codes:
                raise ValueError(
                    "Az értékesítési előzménnyel rendelkező tételek nem törölhetők: "
                    + ", ".join(sold_codes)
                )
            cursor.execute(
                f"DELETE FROM dbo.[Konkrét termék] WHERE T_kod IN ({placeholders})",
                codes,
            )
            cn.commit()

    def add_stock_batches_from_rows(self, rows: List[Dict[str, Any]]) -> int:
        inserted = 0
        with self.get_connection() as cn:
            cursor = cn.cursor()
            for row in rows:
                try:
                    product_id = int(row["ProductId"])
                    batch_code = str(row["BatchCode"]).strip()
                    expiry_date = date.fromisoformat(str(row["ExpiryDate"]))
                    quantity = int(row["Quantity"])
                except (KeyError, TypeError, ValueError) as exc:
                    raise ValueError(
                        "Minden tételsorhoz ProductId, BatchCode, YYYY-MM-DD formátumú "
                        "ExpiryDate és egész Quantity szükséges."
                    ) from exc

                if not batch_code or quantity < 0:
                    raise ValueError("A tételkód kötelező, a készletmennyiség nem lehet negatív.")
                cursor.execute(
                    """
                    INSERT INTO dbo.[Konkrét termék](T_kod, T_ID, T_lejaratdatum, T_db)
                    VALUES(?, ?, ?, ?)
                    """,
                    (batch_code, product_id, expiry_date, quantity),
                )
                inserted += 1
            cn.commit()
        return inserted


from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
service = Inv()

@app.route('/api/kpis', methods=['GET'])
def get_kpis():
    try:
        return jsonify(service.load_kpis())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/parts', methods=['GET'])
def get_parts():
    try:
        search = request.args.get('search')
        category = request.args.get('category')
        status = request.args.get('status')
        return jsonify(service.get_parts(search=search, category=category, status=status))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/parts', methods=['POST'])
def add_part():
    try:
        req_data = request.get_json()
        # Az új verzióban az add_stock_batch függvényt hívjuk meg fix adatokkal
        service.add_stock_batch(
            product_id=int(req_data.get('product_id', 1)),
            batch_code=req_data.get('barcode'),
            expiry_date=date.fromisoformat(req_data.get('expiry_date', '2027-01-01')),
            quantity=int(req_data.get('quantity', 10))
        )
        return jsonify({"message": "Sikeres hozzáadás"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="localhost", port=8000, debug=True)

