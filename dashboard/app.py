"""AstroMed: інтерактивна панель із симуляцією потокових датчиків."""
from datetime import datetime
import os
import random

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dash import Dash, dcc, html, Input, Output

from monitoring.sensors import generate_history, ASTRONAUTS
from models.health_model import analyze_dataframe
from models.resource_optimizer import allocate_medical_kits

# Початкова історія. Надалі кожен тик додає нове симульоване вимірювання.
DATA = analyze_dataframe(generate_history(hours=6))
_rng = random.Random()
_previous = {}
for person in ASTRONAUTS:
    last = DATA[DATA["astronaut"] == person].iloc[-1]
    _previous[person] = {
        "heart_rate": float(last["heart_rate"]),
        "spo2": float(last["spo2"]),
        "temperature": float(last["temperature"]),
        "systolic": float(last["systolic"]),
        "diastolic": float(last["diastolic"]),
        "respiration": float(last["respiration"]),
    }

ENVIRONMENT = {"oxygen": 98.5, "water": 82.0, "power": 94.0}

ASSETS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets"))
app = Dash(__name__, title="AstroMed | Космічний моніторинг", assets_folder=ASSETS_DIR)
app.layout = html.Div(className="page", children=[
    html.Header(className="topbar", children=[
        html.Div([
            html.Div([html.Span("✦", className="brand-mark"), " ASTROMED"], className="brand"),
            html.Div("СИСТЕМА МОНІТОРИНГУ ЖИТТЄДІЯЛЬНОСТІ КОСМІЧНОЇ МІСІЇ", className="subtitle")
        ]),
        html.Div([
            html.Span("●", className="live-dot"),
            html.Span(" LIVE SIMULATION", className="live-label"),
            html.Div(id="clock", className="clock")
        ], className="live-status")
    ]),
    html.Div(className="hero-strip", children=[
        html.Div([html.Div("MISSION CONTROL", className="eyebrow"),
                  html.H1("Панель керування місією"),
                  html.P("Моніторинг екіпажу, життєзабезпечення та медичних ресурсів")]),
        html.Div([html.Div("СТАН СИСТЕМИ", className="eyebrow"),
                  html.Div(id="system-status", className="system-state"),
                  html.Div(id="last-update", className="update-note")], className="system-box")
    ]),
    html.Section(className="controls panel", children=[
        html.Div(className="control-field", children=[html.Label("Космонавт"),
                  dcc.Dropdown(id="astronaut-select", value="all", clearable=False,
                      className="dark-dropdown", searchable=False,
                      options=[{"label": "Увесь екіпаж", "value": "all"}]
                      + [{"label": n, "value": n} for n in ASTRONAUTS])]),
        html.Div(className="control-field", children=[html.Label("Період графіка"),
                  dcc.Dropdown(id="period-select", value="2", clearable=False,
                      className="dark-dropdown", searchable=False, options=[
                      {"label": "Останні 30 хвилин", "value": "0.5"},
                      {"label": "Останні 2 години", "value": "2"},
                      {"label": "Останні 6 годин", "value": "6"}])]),
        html.Div(className="control-field", children=[html.Label("Медичні комплекти"),
                  dcc.Dropdown(id="kits-select", value="2", clearable=False,
                      className="dark-dropdown", searchable=False, options=[
                      {"label": str(n), "value": str(n)} for n in range(4)])])
    ]),
    html.Div(id="metric-cards", className="metrics"),
    html.Section(className="resource-grid", children=[
        html.Div(className="panel resource-panel", children=[
            html.Div([html.H3("Ресурси життєзабезпечення"),
                      html.Span("ENVIRONMENT", className="panel-tag")], className="panel-heading"),
            html.Div(id="resource-bars")
        ]),
        html.Div(className="panel alert-panel", children=[
            html.Div([html.H3("Центр сповіщень"),
                      html.Span("SYSTEM LOG", className="panel-tag")], className="panel-heading"),
            html.Div(id="alerts")
        ])
    ]),
    html.Section(className="charts", children=[
        html.Div(className="panel wide", children=[
            html.Div([html.H3("Динаміка фізіологічних показників"),
                      html.Span("LIVE TELEMETRY", className="panel-tag")], className="panel-heading"),
            dcc.Graph(id="vitals-chart", config={"displayModeBar": False}, animate=True)
        ]),
        html.Div(className="panel", children=[
            html.Div([html.H3("Розподіл станів"),
                      html.Span("RISK ANALYSIS", className="panel-tag")], className="panel-heading"),
            dcc.Graph(id="risk-chart", config={"displayModeBar": False}, animate=True)
        ])
    ]),
    html.Section(className="bottom-grid", children=[
        html.Div(className="panel wide", children=[
            html.Div([html.H3("Поточний стан екіпажу"),
                      html.Span("CREW TELEMETRY", className="panel-tag")], className="panel-heading"),
            html.Div(id="crew-table")
        ]),
        html.Div(className="panel", children=[
            html.Div([html.H3("Медичні комплекти"),
                      html.Span("RESOURCE ALLOCATION", className="panel-tag")], className="panel-heading"),
            html.Div(id="allocation-result")
        ])
    ]),
    html.Footer([
        html.Span("ASTROMED // MISSION CONTROL"),
        html.Span("Навчальний прототип · Дані симульовані · Не для медичної діагностики")
    ], className="footer"),
    dcc.Interval(id="live-interval", interval=2000, n_intervals=0)
])


def generate_live_tick():
    """Додає один новий набір умовних показників для кожного члена екіпажу."""
    global DATA
    now = datetime.now().replace(microsecond=0)
    rows = []
    for person in ASTRONAUTS:
        old = _previous[person]
        new = {
            "heart_rate": max(40, min(135, old["heart_rate"] + _rng.gauss(0, 1.8))),
            "spo2": max(88, min(100, old["spo2"] + _rng.gauss(0, 0.18))),
            "temperature": max(35, min(39, old["temperature"] + _rng.gauss(0, 0.035))),
            "systolic": max(80, min(180, old["systolic"] + _rng.gauss(0, 1.3))),
            "diastolic": max(45, min(115, old["diastolic"] + _rng.gauss(0, 0.9))),
            "respiration": max(7, min(30, old["respiration"] + _rng.gauss(0, 0.35))),
        }
        _previous[person] = new
        rows.append({"timestamp": now, "astronaut": person,
                     **{k: round(v, 2) for k, v in new.items()}})
    DATA = pd.concat([DATA, analyze_dataframe(pd.DataFrame(rows))], ignore_index=True)
    # Обмежуємо обсяг історії останніми 6 годинами.
    DATA = DATA[DATA["timestamp"] >= now - pd.Timedelta(hours=6)].copy()

    # Повільна випадкова зміна запасів — лише демонстраційна телеметрія.
    ENVIRONMENT["oxygen"] = round(max(0, min(100, ENVIRONMENT["oxygen"] + _rng.uniform(-0.025, 0.008))), 1)
    ENVIRONMENT["water"] = round(max(0, min(100, ENVIRONMENT["water"] + _rng.uniform(-0.018, 0.004))), 1)
    ENVIRONMENT["power"] = round(max(0, min(100, ENVIRONMENT["power"] + _rng.uniform(-0.012, 0.006))), 1)


def metric_card(label, value, unit, cls=""):
    return html.Div([
        html.Div(label, className="metric-label"),
        html.Div([html.Span(value, className="metric-value"), html.Span(unit, className="metric-unit")]),
        html.Div(className="metric-accent")
    ], className=f"metric-card {cls}")


def resource_bar(label, value, color, note):
    return html.Div([
        html.Div([html.Span(label), html.Span(f"{value:.1f}%", className="resource-value")],
                 className="resource-topline"),
        html.Div(html.Div(className="resource-fill", style={"width": f"{value}%", "background": color}),
                 className="resource-track"),
        html.Div(note, className="resource-note")
    ], className="resource-item")


def base_layout(fig):
    fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=12, r=12, t=20, b=20),
        font=dict(color="#dce7f7", family="Inter, Arial"),
        legend=dict(orientation="h", y=1.12), transition_duration=450)
    fig.update_xaxes(gridcolor="rgba(145,165,195,.10)", zerolinecolor="rgba(145,165,195,.1)")
    fig.update_yaxes(gridcolor="rgba(145,165,195,.10)", zerolinecolor="rgba(145,165,195,.1)")
    return fig


@app.callback(
    Output("metric-cards", "children"), Output("vitals-chart", "figure"),
    Output("risk-chart", "figure"), Output("crew-table", "children"),
    Output("allocation-result", "children"), Output("resource-bars", "children"),
    Output("alerts", "children"), Output("clock", "children"),
    Output("system-status", "children"), Output("last-update", "children"),
    Input("live-interval", "n_intervals"), Input("astronaut-select", "value"),
    Input("period-select", "value"), Input("kits-select", "value")
)
def update_dashboard(_tick, selected_astronaut, period, kits):
    period = float(period)
    kits = int(kits)
    generate_live_tick()
    now = DATA["timestamp"].max()
    start = now - pd.Timedelta(hours=float(period))
    selected = DATA[DATA["timestamp"] >= start].copy()
    if selected_astronaut != "all":
        selected = selected[selected["astronaut"] == selected_astronaut]
    latest_all = DATA.sort_values("timestamp").groupby("astronaut").tail(1)
    latest_selected = (latest_all if selected_astronaut == "all" else
                       latest_all[latest_all["astronaut"] == selected_astronaut])
    avg = latest_selected.mean(numeric_only=True)
    risk = latest_selected["risk_level"].value_counts()
    overall = "КРИТИЧНИЙ" if (latest_selected["risk_level"] == "Критичний").any() else (
        "УВАГА" if (latest_selected["risk_level"] == "Увага").any() else "НОРМА")
    state_cls = {"НОРМА": "normal", "УВАГА": "warning", "КРИТИЧНИЙ": "critical"}[overall]

    cards = [
        metric_card("СЕРЕДНІЙ ПУЛЬС", f'{avg.get("heart_rate", 0):.0f}', "уд./хв"),
        metric_card("САТУРАЦІЯ SpO₂", f'{avg.get("spo2", 0):.1f}', "%"),
        metric_card("ТЕМПЕРАТУРА", f'{avg.get("temperature", 0):.2f}', "°C"),
        metric_card("СТАН ЕКІПАЖУ", overall, f'{len(latest_selected)} об’єкт(и)', state_cls)
    ]

    # Один графік із двома шкалами: пульс і насичення крові киснем (SpO₂).
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    palette = ["#55d6be", "#58a6ff", "#f5bd5b"]
    people_to_plot = ASTRONAUTS if selected_astronaut == "all" else [selected_astronaut]
    for person, color in zip(people_to_plot, palette):
        subset = selected[selected["astronaut"] == person].sort_values("timestamp")
        fig.add_trace(go.Scatter(x=subset["timestamp"], y=subset["heart_rate"],
            mode="lines", name=f"{person} · пульс", line=dict(color=color, width=2),
            hovertemplate="%{y:.0f} уд./хв<extra>%{fullData.name}</extra>"), secondary_y=False)
        fig.add_trace(go.Scatter(x=subset["timestamp"], y=subset["spo2"],
            mode="lines", name=f"{person} · SpO₂", line=dict(color=color, width=1.7, dash="dot"),
            opacity=.82, hovertemplate="%{y:.1f}%<extra>%{fullData.name}</extra>"), secondary_y=True)
    base_layout(fig).update_layout(xaxis_title="Час", hovermode="x unified")
    fig.update_yaxes(title_text="Пульс, уд./хв", secondary_y=False)
    fig.update_yaxes(title_text="SpO₂, %", range=[85, 101], secondary_y=True, showgrid=False)

    counts = latest_all["risk_level"].value_counts()
    risk_fig = go.Figure(go.Pie(
        labels=["Норма", "Увага", "Критичний"],
        values=[int(counts.get(x, 0)) for x in ["Норма", "Увага", "Критичний"]],
        hole=.68, marker=dict(colors=["#36c995", "#f5b942", "#ff647c"]),
        textinfo="label+value", hovertemplate="%{label}: %{value}<extra></extra>"
    ))
    base_layout(risk_fig).update_layout(showlegend=False, annotations=[dict(
        text=f"{len(latest_all)}<br><span style='font-size:10px'>CREW</span>",
        x=.5, y=.5, showarrow=False, font=dict(size=22, color="#e8eef9"))])

    rows = []
    for _, r in latest_all.iterrows():
        cls = {"Норма": "normal", "Увага": "warning", "Критичний": "critical"}[r["risk_level"]]
        rows.append(html.Tr([
            html.Td(r["astronaut"]), html.Td(f'{r["heart_rate"]:.0f}'),
            html.Td(f'{r["spo2"]:.1f}%'), html.Td(f'{r["temperature"]:.2f} °C'),
            html.Td(f'{r["respiration"]:.1f}'), html.Td(html.Span(r["risk_level"], className=f"pill {cls}")),
            html.Td(str(r["risk_score"]))
        ]))
    table = html.Table([html.Thead(html.Tr([
        html.Th("Космонавт"), html.Th("Пульс"), html.Th("SpO₂"),
        html.Th("Температура"), html.Th("Дихання"), html.Th("Статус"), html.Th("Бал")
    ])), html.Tbody(rows)], className="data-table")

    allocation = allocate_medical_kits(
        latest_all.set_index("astronaut")["risk_score"].to_dict(), int(kits))
    allocation_view = html.Div([
        html.Div([html.Span("Доступно комплектів"), html.Strong(str(allocation["kits_available"]))], className="allocation-stat"),
        html.Div([html.Span("Призначено"), html.Strong(str(allocation["kits_used"]))], className="allocation-stat"),
        html.H4("Пріоритетне призначення"),
        html.Ul([html.Li(n) for n in allocation["assigned"]] or [html.Li("Наразі не потрібні")]),
        html.H4("Очікують комплекту"),
        html.Ul([html.Li(n) for n in allocation["not_assigned"]] or [html.Li("Немає")])
    ], className="allocation")

    resources = [
        resource_bar("КИСЕНЬ У ВІДСІКАХ", ENVIRONMENT["oxygen"], "#55d6be", "Атмосферний резерв"),
        resource_bar("ЗАПАС ВОДИ", ENVIRONMENT["water"], "#58a6ff", "Резервуар життєзабезпечення"),
        resource_bar("ЕНЕРГІЯ", ENVIRONMENT["power"], "#f5bd5b", "Заряд енергосистеми")
    ]
    alert_items = []
    for _, r in latest_all.iterrows():
        if r["risk_level"] != "Норма":
            cls = "warning" if r["risk_level"] == "Увага" else "critical"
            alert_items.append(html.Div([
                html.Span("▲", className=f"alert-icon {cls}"),
                html.Div([html.Strong(r["astronaut"]), html.P(r["reasons"])])
            ], className="alert-item"))
    if ENVIRONMENT["oxygen"] < 90 or ENVIRONMENT["water"] < 20 or ENVIRONMENT["power"] < 20:
        alert_items.append(html.Div("Низький рівень ресурсів життєзабезпечення", className="alert-system"))
    if not alert_items:
        alert_items = [html.Div([html.Span("✓", className="alert-ok"),
                                 html.Span("Критичних сповіщень немає")], className="no-alerts")]

    return (cards, fig, risk_fig, table, allocation_view, resources, alert_items,
            now.strftime("%H:%M:%S"), html.Span(overall, className=f"state-text {state_cls}"),
            f"Оновлено: {now.strftime('%d.%m.%Y %H:%M:%S')}")

if __name__ == "__main__":
    app.run(debug=False, host="127.0.0.1", port=8050)
