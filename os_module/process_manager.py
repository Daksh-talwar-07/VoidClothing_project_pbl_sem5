import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer


def generate_inventory_report(products, path=None):
    os.makedirs("reports", exist_ok=True)
    path = path or os.path.join("reports", "inventory_report.pdf")

    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(path, pagesize=A4)

    story = [
        Paragraph("VOID CLOTHING - Inventory Report", styles["Title"]),
        Paragraph(f"Generated At: {datetime.now():%d-%m-%Y %H:%M:%S}", styles["Normal"]),
        Spacer(1, 16),
    ]

    rows = [["ID", "Name", "Category", "Price", "Stock"]]
    total_stock = 0
    for p in products:
        rows.append([p["id"], p["name"], p["category"], f"Rs. {p['price']}", p["stock"]])
        total_stock += p["stock"]

    table = Table(rows, repeatRows=1, colWidths=[35, 190, 90, 70, 50])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.black),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.whitesmoke]),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
    ]))
    story += [table, Spacer(1, 16),
              Paragraph(f"Total Products: {len(products)} | Total Stock: {total_stock}", styles["Heading3"])]

    doc.build(story)
    return path