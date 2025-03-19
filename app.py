from datetime import datetime

import psycopg2
from flask import Flask, jsonify, request

app = Flask(__name__)


def get_db_connection():
    return psycopg2.connect(
        dbname="car_db",
        user="postgres",
        password="postgres",
        host="localhost",
        port="5432",
    )


@app.route("/price-range", methods=["GET"])
def get_price_range():
    model = request.args.get("model")
    if not model:
        return jsonify({"error": "Missing model parameter"}), 400

    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(
            """
            SELECT name, MIN(price), MAX(price)
            FROM cars
            WHERE model = %s
            GROUP BY name, model
        """,
            (model,),
        )

        results = cur.fetchall()

        if results:
            return jsonify(
                [
                    {
                        "car_name": row[0],
                        "model": model,
                        "min_price": float(row[1]),
                        "max_price": float(row[2]),
                    }
                    for row in results
                ]
            )
        return jsonify({"error": "Model not found or no price data"}), 404

    except psycopg2.Error as e:
        return jsonify({"error": f"Database error: {e}"}), 500
    finally:
        if conn:
            conn.close()


@app.route("/top-common", methods=["GET"])
def top_common_car():
    month = request.args.get("month")
    if not month:
        return jsonify({"error": "Missing month parameter"}), 400

    try:
        datetime.strptime(month, "%Y-%m")
    except ValueError:
        return jsonify({"error": "Invalid month format. Use YYYY-MM"}), 400

    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(
            """
            SELECT name, model, COUNT(*) as count
            FROM cars
            WHERE DATE_TRUNC('month', date_posted) = DATE_TRUNC('month', TO_DATE(%s, 'YYYY-MM'))
            GROUP BY name, model
            ORDER BY count DESC
            LIMIT 1
        """,
            (month,),
        )

        result = cur.fetchone()

        if result:
            return jsonify(
                {
                    "month": month,
                    "car_name": result[0],
                    "model": result[1],
                    "count": result[2],
                }
            )
        return jsonify({"error": "No data available for this month"}), 404

    except psycopg2.Error as e:
        return jsonify({"error": f"Database error: {e}"}), 500
    finally:
        if conn:
            conn.close()


@app.route("/least-common", methods=["GET"])
def least_common_car():
    month = request.args.get("month")
    if not month:
        return jsonify({"error": "Missing month parameter"}), 400

    try:
        datetime.strptime(month, "%Y-%m")
    except ValueError:
        return jsonify({"error": "Invalid month format. Use YYYY-MM"}), 400

    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(
            """
            SELECT name, model, COUNT(*) as count
            FROM cars
            WHERE DATE_TRUNC('month', date_posted) = DATE_TRUNC('month', TO_DATE(%s, 'YYYY-MM'))
            GROUP BY name, model
            ORDER BY count ASC
            LIMIT 1
        """,
            (month,),
        )

        result = cur.fetchone()

        if result:
            return jsonify(
                {
                    "month": month,
                    "car_name": result[0],
                    "model": result[1],
                    "count": result[2],
                }
            )
        return jsonify({"error": "No data available for this month"}), 404

    except psycopg2.Error as e:
        return jsonify({"error": f"Database error: {e}"}), 500
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
