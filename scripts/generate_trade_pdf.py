#!/usr/bin/env python3
"""
AI Trading Analyst — Professional PDF Report Generator (Hermes Edition)

Reads structured JSON from /tmp/trade_report_data.json and produces
a professional multi-page PDF investment report using ReportLab.

Usage:
    python3 generate_trade_pdf.py

Expects data file at: /tmp/trade_report_data.json
Outputs: ./TRADE-REPORT.pdf
"""

import json
import os
import sys
from datetime import datetime

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib.units import inch, mm, cm
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        PageBreak, KeepTogether, HRFlowable, Image
    )
    from reportlab.graphics.shapes import Drawing, Rect, String, Line, Circle
    from reportlab.graphics.charts.barcharts import VerticalBarChart
    from reportlab.graphics.charts.lineplots import LinePlot
except ImportError:
    print("ReportLab not installed. Run: pip3 install reportlab")
    sys.exit(1)


# ─── Color Scheme ───────────────────────────────────────────────────────────

NAVY_BLUE = "#1a365d"
STRONG_BUY = "#22763d"
BUY = "#48bb78"
HOLD = "#d69e2e"
CAUTION = "#dd6b20"
AVOID = "#c53030"
BODY_TEXT = "#2d3748"
TABLE_BORDER = "#e2e8f0"
DISCLAIMER_BG = "#fffff0"

# ─── Page Dimensions ────────────────────────────────────────────────────────

PAGE_WIDTH, PAGE_HEIGHT = A4
MARGIN = 0.75 * inch

# ─── Data Loading ───────────────────────────────────────────────────────────

def load_data():
    path = "/tmp/trade_report_data.json"
    if not os.path.exists(path):
        print(f"Error: Data file not found at {path}")
        print("Run an analysis first (e.g., 'trade analyze AAPL'), then try again.")
        sys.exit(1)
    with open(path) as f:
        return json.load(f)


def get_signal_color(signal):
    signal = signal.lower()
    if "strong buy" in signal:
        return STRONG_BUY
    elif "buy" in signal:
        return BUY
    elif "hold" in signal or "accumulate" in signal:
        return HOLD
    elif "caution" in signal or "neutral" in signal:
        return CAUTION
    elif "avoid" in signal or "sell" in signal:
        return AVOID
    return BODY_TEXT


# ─── Style Definitions ──────────────────────────────────────────────────────

styles = getSampleStyleSheet()

cover_title = ParagraphStyle(
    "CoverTitle", parent=styles["Title"],
    fontSize=28, leading=34, textColor=colors.HexColor(NAVY_BYTE := NAVY_BLUE),
    spaceAfter=12, alignment=TA_CENTER
)

cover_subtitle = ParagraphStyle(
    "CoverSubtitle", parent=styles["Normal"],
    fontSize=14, leading=18, textColor=colors.HexColor(BODY_TEXT),
    spaceAfter=30, alignment=TA_CENTER
)

heading1 = ParagraphStyle(
    "H1", parent=styles["Heading1"],
    fontSize=18, leading=22, textColor=colors.HexColor(NAVY_BLUE),
    spaceBefore=16, spaceAfter=8
)

heading2 = ParagraphStyle(
    "H2", parent=styles["Heading2"],
    fontSize=14, leading=18, textColor=colors.HexColor(NAVY_BLUE),
    spaceBefore=12, spaceAfter=6
)

body = ParagraphStyle(
    "Body", parent=styles["Normal"],
    fontSize=10, leading=14, textColor=colors.HexColor(BODY_TEXT),
    spaceAfter=6
)

small_text = ParagraphStyle(
    "Small", parent=styles["Normal"],
    fontSize=8, leading=10, textColor=colors.HexColor("#718096"),
    spaceAfter=4
)

disclaimer_style = ParagraphStyle(
    "Disclaimer", parent=styles["Normal"],
    fontSize=8, leading=10, textColor=colors.HexColor("#744210"),
    backColor=colors.HexColor(DISCLAIMER_BG),
    borderPadding=8, spaceAfter=12, alignment=TA_CENTER
)


# ─── Drawing Helpers ────────────────────────────────────────────────────────

def score_bar(value, max_val=100, width=300, height=18, label=""):
    """Draw a horizontal score bar."""
    d = Drawing(width + 100, height + 10)
    # Background
    d.add(Rect(0, 5, width, height, fillColor=colors.Color(0.9, 0.9, 0.9),
               strokeColor=colors.Color(0.8, 0.8, 0.8), strokeWidth=0.5))
    # Filled portion
    fill_w = int(width * (value / max_val))
    bar_color = colors.HexColor(get_signal_color(
        "Strong Buy" if value >= 85 else "Buy" if value >= 70 else
        "Hold" if value >= 55 else "Caution" if value >= 40 else "Avoid"
    ))
    d.add(Rect(0, 5, fill_w, height, fillColor=bar_color,
               strokeColor=bar_color, strokeWidth=0.5))
    # Label
    if label:
        d.add(String(5, height // 2 + 2, label, fontSize=9,
                      fontName="Helvetica", fillColor=colors.white))
    # Score text
    d.add(String(width + 8, height // 2 + 2, f"{value}/{max_val}",
                  fontSize=10, fontName="Helvetica-Bold",
                  fillColor=colors.HexColor(NAVY_BLUE)))
    return d


def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) / 255.0 for i in (0, 2, 4))


# ─── Page Template Callbacks ────────────────────────────────────────────────

def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(colors.HexColor("#a0aec0"))
    canvas.drawCentredString(PAGE_WIDTH / 2, 0.4 * inch,
                             "DISCLAIMER: For educational/research purposes only. Not financial advice.")
    canvas.drawCentredString(PAGE_WIDTH / 2, 0.25 * inch,
                             f"Page {doc.page}")
    canvas.restoreState()


# ─── Report Builders ────────────────────────────────────────────────────────

def build_cover(data):
    elements = []
    meta = data.get("report_metadata", {})
    
    elements.append(Spacer(1, 2 * inch))
    elements.append(Paragraph("AI Trading Research Report", cover_title))
    elements.append(Paragraph("Generated by AI Trading Analyst (Hermes)", cover_subtitle))
    elements.append(Spacer(1, 0.3 * inch))
    elements.append(Paragraph(
        f"<b>Date:</b> {meta.get('generated_date', datetime.now().strftime('%Y-%m-%d'))}",
        body
    ))
    elements.append(Paragraph(
        f"<b>Analyses Included:</b> {meta.get('total_analyses', 0)}",
        body
    ))
    elements.append(Spacer(1, 0.5 * inch))
    elements.append(HRFlowable(width="80%", thickness=1,
                                 color=colors.HexColor(NAVY_BLUE)))
    elements.append(Spacer(1, 0.3 * inch))
    elements.append(Paragraph(
        "This report provides AI-generated research and analysis for educational "
        "purposes only. It is NOT financial advice. All data should be independently "
        "verified. Past performance does not indicate future results. Always consult "
        "a licensed financial advisor before making investment decisions.",
        disclaimer_style
    ))
    elements.append(PageBreak())
    return elements


def build_executive_summary(data):
    elements = []
    summary = data.get("executive_summary", {})
    
    elements.append(Paragraph("Executive Summary", heading1))
    elements.append(HRFlowable(width="100%", thickness=1,
                                 color=colors.HexColor(NAVY_BLUE)))
    elements.append(Spacer(1, 0.15 * inch))
    
    # Top picks
    strong_buys = summary.get("strong_buys", [])
    buys = summary.get("buys", [])
    holds = summary.get("holds", [])
    avoids = summary.get("avoids", [])
    
    if strong_buys:
        elements.append(Paragraph(f"<b>Strong Buys:</b> {', '.join(strong_buys)}", body))
    if buys:
        elements.append(Paragraph(f"<b>Buys:</b> {', '.join(buys)}", body))
    if holds:
        elements.append(Paragraph(f"<b>Holds:</b> {', '.join(holds)}", body))
    if avoids:
        elements.append(Paragraph(f"<b>Avoids:</b> {', '.join(avoids)}", body))
    
    elements.append(Spacer(1, 0.15 * inch))
    top_pick = summary.get("top_conviction_pick", "")
    risk_flag = summary.get("biggest_risk_flag", "")
    if top_pick:
        elements.append(Paragraph(f"<b>Top Conviction Pick:</b> {top_pick}", body))
    if risk_flag:
        elements.append(Paragraph(f"<b>Biggest Risk Flag:</b> {risk_flag}", body))
    
    # Upcoming catalysts
    catalysts = summary.get("upcoming_catalysts", [])
    if catalysts:
        elements.append(Spacer(1, 0.15 * inch))
        elements.append(Paragraph("Upcoming Catalysts:", heading2))
        for cat in catalysts:
            elements.append(Paragraph(f"• {cat}", body))
    
    # Bar chart for scores
    elements.append(Spacer(1, 0.2 * inch))
    elements.append(Paragraph("Score Overview", heading2))
    for analysis in data.get("analyses", []):
        score = analysis.get("trade_score", 50)
        ticker = analysis.get("ticker", "?")
        elements.append(score_bar(score, label=ticker))
        elements.append(Spacer(1, 0.05 * inch))
    
    return elements


def build_stock_pages(data):
    elements = []
    
    for analysis in data.get("analyses", []):
        ticker = analysis.get("ticker", "?")
        company = analysis.get("company_name", "")
        score = analysis.get("trade_score", 0)
        signal = analysis.get("trade_signal", "N/A")
        
        elements.append(Paragraph(f"Analysis: {ticker} — {company}", heading1))
        elements.append(HRFlowable(width="100%", thickness=1,
                                     color=colors.HexColor(NAVY_BLUE)))
        elements.append(Spacer(1, 0.1 * inch))
        
        # Score + Signal row
        signal_color = get_signal_color(signal)
        elements.append(Paragraph(
            f"<b>Trade Score:</b> {score}/100 &nbsp;&nbsp;"
            f"<b>Signal:</b> <font color='{signal_color}'>{signal}</font>",
            body
        ))
        elements.append(Spacer(1, 0.1 * inch))
        
        # Score bar
        elements.append(score_bar(score, label=f"{ticker}"))
        elements.append(Spacer(1, 0.15 * inch))
        
        # Key levels table
        levels = analysis.get("key_levels", {})
        price = analysis.get("price_at_analysis", "N/A")
        target = analysis.get("price_target", "N/A")
        stop = analysis.get("stop_loss", "N/A")
        
        levels_data = [
            ["Metric", "Value"],
            ["Current Price", f"${price}"],
            ["Price Target", f"${target}"],
            ["Stop Loss", f"${stop}"],
            ["Support", f"${levels.get('support', 'N/A')}"],
            ["Resistance", f"${levels.get('resistance', 'N/A')}"],
        ]
        t = Table(levels_data, colWidths=[1.5*inch, 1.5*inch])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(NAVY_BLUE)),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor(TABLE_BORDER)),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.Color(0.97, 0.97, 0.97)]),
        ]))
        elements.append(t)
        elements.append(Spacer(1, 0.15 * inch))
        
        # Sub-scores
        sub_scores = analysis.get("sub_scores", {})
        if sub_scores:
            elements.append(Paragraph("Dimension Scores:", heading2))
            for dim, val in sub_scores.items():
                elements.append(score_bar(val, label=dim.replace("_", " ").title()))
                elements.append(Spacer(1, 0.04 * inch))
        
        elements.append(PageBreak())
    
    return elements


def build_portfolio_page(data):
    elements = []
    portfolio = data.get("portfolio")
    if not portfolio:
        return elements
    
    elements.append(Paragraph("Portfolio Summary", heading1))
    elements.append(HRFlowable(width="100%", thickness=1,
                                 color=colors.HexColor(NAVY_BLUE)))
    elements.append(Spacer(1, 0.1 * inch))
    
    port_data = [
        ["Metric", "Value"],
        ["Total Value", f"${portfolio.get('total_value', 0):,}"],
        ["Holdings", str(portfolio.get('holdings_count', 0))],
        ["Portfolio Beta", str(portfolio.get('portfolio_beta', 'N/A'))],
        ["Dividend Yield", portfolio.get('dividend_yield', 'N/A')],
        ["Health Score", f"{portfolio.get('portfolio_health_score', 'N/A')}/100"],
    ]
    
    t = Table(port_data, colWidths=[2*inch, 2*inch])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(NAVY_BLUE)),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor(TABLE_BORDER)),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.Color(0.97, 0.97, 0.97)]),
    ]))
    elements.append(t)
    elements.append(PageBreak())
    
    return elements


def build_watchlist_page(data):
    elements = []
    watchlist = data.get("watchlist")
    if not watchlist:
        return elements
    
    elements.append(Paragraph("Watchlist Summary", heading1))
    elements.append(HRFlowable(width="100%", thickness=1,
                                 color=colors.HexColor(NAVY_BLUE)))
    elements.append(Spacer(1, 0.1 * inch))
    
    elements.append(Paragraph(
        f"<b>Stocks Tracked:</b> {watchlist.get('watchlist_count', 0)} &nbsp;|&nbsp; "
        f"<b>Top Stock:</b> {watchlist.get('top_stock', 'N/A')} &nbsp;|&nbsp; "
        f"<b>Active Alerts:</b> {watchlist.get('active_alerts', 0)}",
        body
    ))
    elements.append(PageBreak())
    
    return elements


# ─── Main ───────────────────────────────────────────────────────────────────

def main():
    data = load_data()
    output_path = os.path.join(os.getcwd(), "TRADE-REPORT.pdf")
    
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=MARGIN,
        rightMargin=MARGIN,
        topMargin=0.8 * inch,
        bottomMargin=0.8 * inch,
        title="AI Trading Research Report",
        author="AI Trading Analyst (Hermes)"
    )
    
    elements = []
    
    # Build each section
    elements.extend(build_cover(data))
    elements.extend(build_executive_summary(data))
    elements.extend(build_stock_pages(data))
    elements.extend(build_portfolio_page(data))
    elements.extend(build_watchlist_page(data))
    
    # Build the PDF
    try:
        doc.build(elements, onFirstPage=footer, onLaterPages=footer)
        file_size = os.path.getsize(output_path)
        print(f"✅ PDF report generated: {output_path}")
        print(f"   File size: {file_size:,} bytes")
        print(f"   Pages: ~{len([e for e in elements if isinstance(e, PageBreak)]) + 1}")
    except Exception as e:
        print(f"❌ PDF generation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
