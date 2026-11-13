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
            elif status == "expiring_soon":
                sql += " AND stock.T_lejaratdatum >= CONVERT(date, GETDATE()) AND stock.T_lejaratdatum <= DATEADD(day, 30, CONVERT(date, GETDATE()))"
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
                    "Name": row.Name or "",
                    "Category": row.Category or "",
                    "Location": row.Location.strip() if row.Location else "Raktár",
                    "ExpiryDate": row.ExpiryDate,
                    "ProductId": row.ProductId,
                    "ProductName": row.ProductName or "",
                    "Quantity": row.Quantity if row.Quantity is not None else 0,
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
                stock.T_db AS Quantity,
                product.T_marka AS Brand,
                product.T_veny AS IsPrescription,
                product.T_leiras AS Description,
                product.T_hatoanyag AS ActiveIngredient
            FROM dbo.[Konkrét termék] AS stock
            INNER JOIN dbo.[Termék jellemzők] AS product ON product.T_ID = stock.T_ID
            WHERE stock.T_kod IN ({placeholders})
        """
        with self.get_connection() as cn:
            results = []
            cursor = cn.cursor()
            for row in cursor.execute(sql, batch_codes):
                results.append({
                    "PartId": row.PartId,
                    "Barcode": row.Barcode,
                    "Name": row.Name,
                    "Category": row.Category,
                    "Location": row.Location.strip() if row.Location else "Raktár",
                    "ExpiryDate": row.ExpiryDate,
                    "ProductId": row.ProductId,
                    "Quantity": row.Quantity,
                    "Brand": row.Brand.strip() if row.Brand else "Ismeretlen gyártó",
                    "IsPrescription": bool(row.IsPrescription),
                    "Description": row.Description.strip() if row.Description else "Nincs leírás feltöltve ehhez a termékhez.",
                    "ActiveIngredient": row.ActiveIngredient.strip() if row.ActiveIngredient else "Nincs megadva"
                })
            return results

    def load_kpis(self) -> Dict[str, int]:
        # Egyetlen optimalizált lekérdezés az összes patika KPI adathoz - LEZÁRVA A VÉGÉN!
        sql = """
            SELECT
                (SELECT COUNT(*) FROM dbo.[Termék jellemzők]) AS ProductCnt,
                (SELECT COUNT(*) FROM dbo.[Konkrét termék]) AS BatchCnt,
                (SELECT COALESCE(SUM(T_db), 0) FROM dbo.[Konkrét termék]) AS StockCnt,
                (SELECT COUNT(*) FROM dbo.[Konkrét termék]
                 WHERE T_lejaratdatum < CAST(GETDATE() AS DATE)) AS ExpiredBatchCnt,
                (SELECT COUNT(*) FROM dbo.[Konkrét termék] WHERE T_db <= 0) AS OutOfStockBatchCnt
        """ # <--- ITT HIÁNYZOTT EGY ZÁRÓJEL A ");" ELŐTT, EZ OKOZTA A 0-KAT!
        
        with self.get_connection() as cn:
            row = cn.cursor().execute(sql).fetchone()
            if row:
                return {
                    "ProductCnt": getattr(row, "ProductCnt", 0),
                    "BatchCnt": getattr(row, "BatchCnt", 0),
                    "StockCnt": getattr(row, "StockCnt", 0),
                    "ExpiredBatchCnt": getattr(row, "ExpiredBatchCnt", 0),
                    "OutOfStockBatchCnt": getattr(row, "OutOfStockBatchCnt", 0),
                }
            return {
                "ProductCnt": 0, "BatchCnt": 0, "StockCnt": 0, 
                "ExpiredBatchCnt": 0, "OutOfStockBatchCnt": 0
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
        barcode = req_data.get('barcode', '').strip()
        name = req_data.get('name', '').strip()
        category = req_data.get('category', '').strip()
        location = req_data.get('location', '').strip()
        expiry_str = req_data.get('expiry_date', '2027-01-01')
        quantity = int(req_data.get('quantity', 1))

        # Alapértelmezett értékek kezelése ha valami üresen jönne
        sor = location if location else "Raktár"
        polc = "1"
        
        words = name.split()
        brand = words[0] if words else "Ismeretlen"

        # ÚJ RÉSZ: Ha nincs megadva vonalkód (az új legördülős bevételező űrlapról jön),
        # akkor a meglévő katalógusból keresi ki a terméket és csak készletet szúr be.
        if not barcode:
            if not name:
                return jsonify({"error": "A gyógyszer nevének kiválasztása kötelező!"}), 400
            if quantity < 1:
                return jsonify({"error": "A mennyiségnek legalább 1-nek kell lennie!"}), 400

            with service.get_connection() as cn:
                cursor = cn.cursor()
                cursor.execute(
                    "SELECT TOP 1 T_ID FROM dbo.[Termék jellemzők] WHERE T_nev = ?",
                    (name,)
                )
                row = cursor.fetchone()
                if not row:
                    return jsonify({"error": "A kiválasztott gyógyszer nem található a katalógusban!"}), 404

                product_id = int(row[0])
                import time
                batch_code = f"K{int(time.time() * 1000)}"[-12:]

                cursor.execute(
                    """
                    INSERT INTO dbo.[Konkrét termék](T_kod, T_ID, T_lejaratdatum, T_db)
                    VALUES(?, ?, ?, ?)
                    """,
                    (batch_code, product_id, date.fromisoformat(expiry_str), quantity)
                )
                cn.commit()

            return jsonify({
                "message": "Sikeres bevételezés a raktárba!",
                "ProductId": product_id,
                "BatchCode": batch_code
            }), 201

        # A TE EREDETI RÉGI KÓDOD (változatlanul hagyva, ha vonalkóddal érkezik kérés):
        sql_jellemzo = """
            INSERT INTO dbo.[Termék jellemzők](T_marka, T_nev, T_hatoanyag, T_kateg, T_veny, T_mennyiseg, T_mertekegyseg, T_leiras, T_sor, T_polc)
            OUTPUT INSERTED.T_ID
            VALUES(?, ?, ?, ?, 0, 1, 'db', 'Felhasználó által rögzített tétel.', ?, ?);
        """
        
        sql_konkret = """
            INSERT INTO dbo.[Konkrét termék](T_kod, T_ID, T_lejaratdatum, T_db)
            VALUES(?, ?, ?, ?)
        """

        with service.get_connection() as cn:
            cursor = cn.cursor()
            
            # Lépés 1: Alap adatok beszúrása és az ID azonnali kiolvasása
            cursor.execute(sql_jellemzo, (brand, name, name, category, sor, polc))
            row = cursor.fetchone()
            
            if not row or row[0] is None:
                raise Exception("Az Azure nem tudta generálni vagy visszaadni az új gyógyszerazonosítót.")
                
            product_id = int(row[0])
            
            # Lépés 2: Konkrét darabszám és dátum mentése a kapott ID alapján
            cursor.execute(sql_konkret, (barcode, product_id, date.fromisoformat(expiry_str), quantity))
            
            cn.commit()

        return jsonify({"message": "Sikeres hozzáadás az Azure-ba", "ProductId": product_id}), 201
    except Exception as e:
        print("!!! JAVÍTÁSI ADATBÁZIS HIBA:", str(e))
        return jsonify({"error": str(e)}), 500





@app.route('/api/parts/<id>', methods=['GET'])
def get_part_by_id(id):
    try:
        result = service.get_parts_by_ids([id])
        if not result or len(result) == 0:
            return jsonify({"error": "A gyógyszer nem található"}), 404
        return jsonify(result[0])
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route('/api/categories', methods=['GET'])
def get_categories():
    try:
        # Lekérjük az egyedi kategóriákat közvetlenül az adatbázisból
        sql = "SELECT DISTINCT T_kateg FROM dbo.[Termék jellemzők] WHERE T_kateg IS NOT NULL"
        with service.get_connection() as cn:
            cursor = cn.cursor()
            categories = [row[0].strip() for row in cursor.execute(sql) if row[0]]
        return jsonify(categories)
    except Exception as e:
        return jsonify({"error": str(e)}), 500



from invfo import InvFo

@app.get("/api/top-categories")
def get_top_categories():
    inv_fo = InvFo()
    return inv_fo.load_top_categories()

@app.route('/api/product-types', methods=['GET'])
def get_product_types():
    try:
        sql = """
            SELECT T_ID AS id, T_nev AS name, T_kateg AS category
            FROM dbo.[Termék jellemzők]
            ORDER BY T_nev
        """
        with service.get_connection() as cn:
            cursor = cn.cursor()
            results = [
                {
                    "id": row.id,
                    "name": row.name.strip(),
                    "category": row.category.strip() if row.category else ""
                }
                for row in cursor.execute(sql)
            ]
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route('/api/top-sold', methods=['GET'])
def get_top_sold():
    try:
        sql = """
            SELECT
                p.T_nev AS Name,
                p.T_kateg AS Category,
                COALESCE(SUM(e.E_db), 0) AS TotalSold
            FROM dbo.[Eladások] e
            INNER JOIN dbo.[Konkrét termék] k ON e.T_kod = k.T_kod
            INNER JOIN dbo.[Termék jellemzők] p ON k.T_ID = p.T_ID
            GROUP BY p.T_ID, p.T_nev, p.T_kateg
            ORDER BY TotalSold DESC
        """
        with service.get_connection() as cn:
            cursor = cn.cursor()
            results = [
                {
                    "Name": row.Name.strip(),
                    "Category": row.Category.strip() if row.Category else "",
                    "TotalSold": int(row.TotalSold)
                }
                for row in cursor.execute(sql)
            ]
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route('/api/sales-stats/<int:product_id>', methods=['GET'])
def get_product_sales_stats(product_id):
    try:
        sql = """
            SELECT
                COALESCE(SUM(e.E_db), 0) AS TotalSold,
                COALESCE(SUM(
                    CASE 
                        WHEN YEAR(e.E_datum) = YEAR(GETDATE()) AND MONTH(e.E_datum) = MONTH(GETDATE()) 
                        THEN e.E_db 
                        ELSE 0 
                    END
                ), 0) AS MonthlySold
            FROM dbo.[Eladások] e
            INNER JOIN dbo.[Konkrét termék] k ON e.T_kod = k.T_kod
            WHERE k.T_ID = ?
        """
        with service.get_connection() as cn:
            row = cn.cursor().execute(sql, (product_id,)).fetchone()
            return jsonify({
                "TotalSold": int(row.TotalSold) if row else 0,
                "MonthlySold": int(row.MonthlySold) if row else 0
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route('/api/sell', methods=['POST'])
def sell_product():
    try:
        req_data = request.get_json()
        product_id = int(req_data.get('product_id'))
        receipt_code = str(req_data.get('receipt_code', '')).strip()
        sell_qty = int(req_data.get('quantity', 0))

        if not receipt_code:
            return jsonify({"error": "A nyugtaszám megadása kötelező!"}), 400
        if len(receipt_code) > 15:
            return jsonify({"error": "A nyugtaszám maximum 15 karakter lehet!"}), 400
        if sell_qty <= 0:
            return jsonify({"error": "Az eladott mennyiségnek legalább 1-nek kell lennie!"}), 400

        with service.get_connection() as cn:
            cursor = cn.cursor()

            cursor.execute("""
                SELECT T_kod, T_db, T_lejaratdatum
                FROM dbo.[Konkrét termék]
                WHERE T_ID = ? AND T_db > 0
                ORDER BY T_lejaratdatum ASC
            """, (product_id,))
            batches = cursor.fetchall()

            total_available = sum(int(row.T_db) for row in batches)
            if total_available < sell_qty:
                return jsonify({"error": f"Nincs elég készlet! Összesen elérhető: {total_available} db."}), 400

            remaining_to_sell = sell_qty

            for batch in batches:
                if remaining_to_sell <= 0:
                    break

                batch_code = batch.T_kod
                available_in_batch = int(batch.T_db)
                take = min(available_in_batch, remaining_to_sell)

                cursor.execute("""
                    UPDATE dbo.[Konkrét termék]
                    SET T_db = T_db - ?
                    WHERE T_kod = ?
                """, (take, batch_code))

                cursor.execute("""
                    INSERT INTO dbo.[Eladások] (E_kod, T_kod, E_datum, E_db)
                    VALUES (?, ?, GETDATE(), ?)
                """, (receipt_code, batch_code, take))

                remaining_to_sell -= take

            cn.commit()

        return jsonify({"message": f"Sikeres eladás! ({sell_qty} db rögzítve a {receipt_code} számú nyugtára.)"}), 200
    except Exception as e:
        print("!!! ELADÁSI HIBA:", str(e))
        return jsonify({"error": str(e)}), 500



if __name__ == "__main__":
    app.run(host="localhost", port=8000, debug=True)
    
    
