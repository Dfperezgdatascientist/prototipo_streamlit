#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Autoservicio Corporativo — Diners Club
Plataforma de ejecución de procesos batch vía web con autenticación,
registro de auditoría y exportación a Excel.

Ejecutar:
    streamlit run app.py --server.port 8080 --server.address 0.0.0.0
"""

import streamlit as st
import pandas as pd
import hashlib
import json
import time
import io
from datetime import datetime
from pathlib import Path

# ─────────────────────────────────────────────────────────────
# Configuración de página
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Autoservicio · Diners Club",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────────────────────
# CSS corporativo — estética limpia azul marino
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

:root {
    --navy:      #0B1F3A;
    --navy-mid:  #122B52;
    --blue:      #1A56DB;
    --blue-light:#3B82F6;
    --gold:      #D4A017;
    --gold-light:#F5C842;
    --bg:        #F0F4FA;
    --surface:   #FFFFFF;
    --border:    #D1DCF0;
    --text:      #0B1F3A;
    --text-soft: #4A6080;
    --success:   #059669;
    --error:     #DC2626;
    --warn:      #D97706;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background: var(--bg) !important;
}

/* Header corporativo */
.corp-header {
    background: linear-gradient(135deg, var(--navy) 0%, var(--navy-mid) 60%, #1A3A6B 100%);
    padding: 28px 40px;
    border-radius: 16px;
    margin-bottom: 28px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: 0 8px 32px rgba(11,31,58,0.18);
    position: relative;
    overflow: hidden;
}
.corp-header::before {
    content: '';
    position: absolute;
    top: -40px; right: -40px;
    width: 180px; height: 180px;
    background: radial-gradient(circle, rgba(212,160,23,0.15) 0%, transparent 70%);
    border-radius: 50%;
}
.corp-header::after {
    content: '';
    position: absolute;
    bottom: -30px; left: 30%;
    width: 120px; height: 120px;
    background: radial-gradient(circle, rgba(26,86,219,0.2) 0%, transparent 70%);
    border-radius: 50%;
}
.corp-title {
    color: #FFFFFF;
    font-size: 26px;
    font-weight: 700;
    letter-spacing: -0.5px;
    margin: 0;
}
.corp-subtitle {
    color: rgba(255,255,255,0.6);
    font-size: 13px;
    font-weight: 400;
    margin-top: 4px;
    font-family: 'DM Mono', monospace;
    letter-spacing: 0.5px;
}
.corp-badge {
    background: rgba(212,160,23,0.2);
    border: 1px solid rgba(212,160,23,0.5);
    color: var(--gold-light);
    font-size: 11px;
    font-weight: 600;
    padding: 4px 12px;
    border-radius: 20px;
    letter-spacing: 1px;
    text-transform: uppercase;
    font-family: 'DM Mono', monospace;
}

/* Cards */
.card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 28px 32px;
    margin-bottom: 20px;
    box-shadow: 0 2px 12px rgba(11,31,58,0.06);
    transition: box-shadow 0.2s;
}
.card:hover { box-shadow: 0 6px 24px rgba(11,31,58,0.10); }

.card-title {
    font-size: 15px;
    font-weight: 600;
    color: var(--navy);
    margin-bottom: 6px;
    display: flex;
    align-items: center;
    gap: 8px;
}
.card-desc {
    font-size: 13px;
    color: var(--text-soft);
    margin-bottom: 20px;
    line-height: 1.5;
}

/* Login card */
.login-wrap {
    max-width: 440px;
    margin: 60px auto 0;
}
.login-logo {
    text-align: center;
    margin-bottom: 32px;
}
.login-logo-text {
    font-size: 36px;
    font-weight: 700;
    color: var(--navy);
    letter-spacing: -1px;
}
.login-logo-sub {
    font-size: 13px;
    color: var(--text-soft);
    font-family: 'DM Mono', monospace;
    margin-top: 4px;
}

/* Status badges */
.status-ok   { background:#ECFDF5; color:#065F46; border:1px solid #6EE7B7; padding:4px 10px; border-radius:20px; font-size:12px; font-weight:600; }
.status-warn { background:#FFFBEB; color:#92400E; border:1px solid #FCD34D; padding:4px 10px; border-radius:20px; font-size:12px; font-weight:600; }
.status-err  { background:#FEF2F2; color:#991B1B; border:1px solid #FCA5A5; padding:4px 10px; border-radius:20px; font-size:12px; font-weight:600; }

/* Audit row */
.audit-row {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px 0;
    border-bottom: 1px solid var(--border);
    font-size: 13px;
}
.audit-ts { font-family:'DM Mono',monospace; color:var(--text-soft); font-size:11px; min-width:140px; }
.audit-user { font-weight:600; color:var(--navy); min-width:120px; }
.audit-action { color:var(--text-soft); flex:1; }

/* Job card seleccionado */
.job-selected {
    border: 2px solid var(--blue) !important;
    background: #EFF6FF !important;
}

/* Steps */
.step-row {
    display: flex;
    align-items: flex-start;
    gap: 14px;
    margin-bottom: 14px;
}
.step-num {
    min-width: 28px; height: 28px;
    background: var(--navy); color: white;
    border-radius: 50%;
    font-size: 12px; font-weight: 700;
    display: flex; align-items:center; justify-content:center;
    flex-shrink: 0;
    margin-top: 2px;
}
.step-num.done { background: var(--success); }
.step-text { font-size: 14px; color: var(--text); padding-top: 4px; }

/* Ocultar elementos streamlit */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 24px !important; max-width: 1100px !important; }
[data-testid="stSidebar"] { display: none !important; }

/* Botones */
.stButton > button {
    background: var(--blue) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    padding: 10px 24px !important;
    transition: all 0.2s !important;
    box-shadow: 0 2px 8px rgba(26,86,219,0.25) !important;
}
.stButton > button:hover {
    background: #1449C0 !important;
    box-shadow: 0 4px 16px rgba(26,86,219,0.35) !important;
    transform: translateY(-1px) !important;
}

/* Inputs */
.stTextInput > div > div > input,
.stSelectbox > div > div,
.stTextArea > div > div > textarea {
    border-radius: 8px !important;
    border: 1px solid var(--border) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 14px !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: var(--blue) !important;
    box-shadow: 0 0 0 3px rgba(26,86,219,0.12) !important;
}

/* Progress */
.stProgress > div > div > div > div {
    background: linear-gradient(90deg, var(--blue), var(--blue-light)) !important;
    border-radius: 4px !important;
}

/* Dataframe */
.stDataFrame { border-radius: 10px !important; overflow: hidden !important; border: 1px solid var(--border) !important; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] { gap: 4px; background: transparent; border-bottom: 2px solid var(--border); }
.stTabs [data-baseweb="tab"] { border-radius: 8px 8px 0 0 !important; font-family: 'DM Sans', sans-serif !important; font-weight: 500 !important; }
.stTabs [aria-selected="true"] { background: var(--blue) !important; color: white !important; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# Estado de sesión
# ─────────────────────────────────────────────────────────────
def init_session():
    defaults = {
        "authenticated": False,
        "username": "",
        "user_display": "",
        "login_time": None,
        "audit_log": [],
        "job_result": None,
        "job_running": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_session()


# ─────────────────────────────────────────────────────────────
# Usuarios (en producción reemplazar con LDAP / BD)
# ─────────────────────────────────────────────────────────────
USERS = {
    "sandra.ortiz": {"password": hashlib.sha256("Diners2024!".encode()).hexdigest(), "display": "Sandra Ortiz",    "role": "Analista Senior"},
    "admin":        {"password": hashlib.sha256("Admin123!".encode()).hexdigest(),   "display": "Administrador",   "role": "Admin"},
    "demo":         {"password": hashlib.sha256("demo".encode()).hexdigest(),         "display": "Usuario Demo",    "role": "Demo"},
}


# ─────────────────────────────────────────────────────────────
# Auditoría
# ─────────────────────────────────────────────────────────────
AUDIT_FILE = Path("audit_log.jsonl")

def audit(action: str, detail: str = ""):
    entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "user":      st.session_state.username,
        "action":    action,
        "detail":    detail,
    }
    st.session_state.audit_log.append(entry)
    with open(AUDIT_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


# ─────────────────────────────────────────────────────────────
# Jobs disponibles (catálogo)
# ─────────────────────────────────────────────────────────────
JOBS = {
    "carga_sftp": {
        "icon": "📂",
        "name": "Carga desde SFTP",
        "desc": "Lee archivos de un servidor SFTP y los carga a Teradata.",
        "inputs": [],
    },
    "consulta_teradata": {
        "icon": "🗄️",
        "name": "Consulta Teradata",
        "desc": "Ejecuta una consulta sobre DWH_PRESTAGE y retorna los resultados.",
        "inputs": ["query"],
    },
    "formulario_manual": {
        "icon": "📝",
        "name": "Ingreso Manual de Datos",
        "desc": "Permite ingresar registros manualmente desde un formulario y exportarlos a Excel.",
        "inputs": ["form"],
    },
    "alerta_iaagents": {
        "icon": "🤖",
        "name": "Reporte IA Agents",
        "desc": "Genera reporte de alertas del proceso IA Agents para una fecha dada.",
        "inputs": ["fecha"],
    },
}


# ─────────────────────────────────────────────────────────────
# Simulación de ejecución de jobs
# ─────────────────────────────────────────────────────────────
def run_job_sftp() -> pd.DataFrame:
    """Simula lectura desde SFTP."""
    time.sleep(2)
    return pd.DataFrame({
        "archivo":   ["ISD_2025_01.parquet", "ISD_2025_02.parquet", "ISD_2025_03.parquet"],
        "registros": [120_450, 98_320, 134_780],
        "estado":    ["✅ Cargado", "✅ Cargado", "✅ Cargado"],
        "timestamp": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")] * 3,
    })

def run_job_teradata(query: str) -> pd.DataFrame:
    """Simula consulta Teradata."""
    time.sleep(1.5)
    # Aquí va: teradatasql.connect(...) + cur.execute(query)
    return pd.DataFrame({
        "fecha_carga":    ["2026-04-15", "2026-04-15", "2026-04-15"],
        "hora_carga":     ["08", "09", "10"],
        "cant_registros": [4_521, 3_897, 5_103],
        "alerta":         ["OK", "OK", "DIFERENCIAS"],
    })

def run_job_iaagents(fecha: str) -> pd.DataFrame:
    """Simula reporte de alertas IA Agents."""
    time.sleep(2)
    horas = [f"{h:02d}" for h in range(0, 24)]
    import random
    random.seed(42)
    return pd.DataFrame({
        "fecha_carga":        [fecha] * 24,
        "hora_carga":         horas,
        "cant_archivos_json": [random.randint(50, 200) for _ in horas],
        "cant_ids_aws":       [random.randint(45, 195) for _ in horas],
        "cant_ids_teradata":  [random.randint(45, 195) for _ in horas],
        "alerta":             [random.choice(["OK", "OK", "OK", "DIFERENCIAS"]) for _ in horas],
    })


# ─────────────────────────────────────────────────────────────
# Exportar a Excel
# ─────────────────────────────────────────────────────────────
def df_to_excel(df: pd.DataFrame, sheet_name: str = "Resultado") -> bytes:
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)
        ws = writer.sheets[sheet_name]
        # Formato básico de columnas
        for col in ws.columns:
            max_len = max(len(str(cell.value or "")) for cell in col)
            ws.column_dimensions[col[0].column_letter].width = min(max_len + 4, 50)
    return buf.getvalue()


# ─────────────────────────────────────────────────────────────
# PANTALLA DE LOGIN
# ─────────────────────────────────────────────────────────────
def show_login():
    st.markdown("""
    <div class="login-wrap">
        <div class="login-logo">
            <div class="login-logo-text">💳 Diners Club</div>
            <div class="login-logo-sub">PLATAFORMA DE AUTOSERVICIO · DATA & IA</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_c = st.columns([1, 2, 1])[1]
    with col_c:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("**Iniciar sesión**")
        st.caption("Ingresa tus credenciales corporativas")

        username = st.text_input("Usuario", placeholder="tu.nombre", key="login_user")
        password = st.text_input("Contraseña", type="password", placeholder="••••••••", key="login_pass")

        col_btn, col_hint = st.columns([1, 1])
        with col_btn:
            login_btn = st.button("Ingresar →", use_container_width=True)

        if login_btn:
            user_data = USERS.get(username.lower())
            hashed    = hashlib.sha256(password.encode()).hexdigest()
            if user_data and user_data["password"] == hashed:
                st.session_state.authenticated  = True
                st.session_state.username        = username.lower()
                st.session_state.user_display    = user_data["display"]
                st.session_state.login_time      = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                audit("LOGIN", f"Inicio de sesión exitoso")
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos.")

        st.markdown("</div>", unsafe_allow_html=True)
        st.caption("💡 Demo: usuario `demo` / contraseña `demo`")


# ─────────────────────────────────────────────────────────────
# PANTALLA PRINCIPAL
# ─────────────────────────────────────────────────────────────
def show_main():
    user_info = USERS.get(st.session_state.username, {})

    # ── Header ───────────────────────────────────────────────
    st.markdown(f"""
    <div class="corp-header">
        <div>
            <div class="corp-title">💳 Autoservicio Data & IA</div>
            <div class="corp-subtitle">DINERS CLUB ECUADOR · PLATAFORMA DE PROCESOS</div>
        </div>
        <div style="text-align:right; z-index:1;">
            <div class="corp-badge">● EN LÍNEA</div>
            <div style="color:rgba(255,255,255,0.7); font-size:12px; margin-top:8px;">
                {st.session_state.user_display} &nbsp;·&nbsp; {user_info.get('role','')}<br>
                <span style="font-family:'DM Mono',monospace; font-size:11px; opacity:0.5;">
                    Sesión: {st.session_state.login_time}
                </span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Tabs principales ─────────────────────────────────────
    tab_jobs, tab_form, tab_audit = st.tabs(["⚡ Ejecutar Job", "📝 Ingreso Manual", "📋 Auditoría"])

    # ════════════════════════════════════════════════════════
    # TAB 1 — Ejecutar Job
    # ════════════════════════════════════════════════════════
    with tab_jobs:
        col_left, col_right = st.columns([1, 1.6], gap="large")

        with col_left:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="card-title">🗂️ Selecciona el proceso a ejecutar</div>', unsafe_allow_html=True)
            st.markdown('<div class="card-desc">Elige uno de los jobs disponibles. El sistema registrará quién ejecutó el proceso y a qué hora.</div>', unsafe_allow_html=True)

            job_key = st.selectbox(
                "Job disponible",
                options=list(JOBS.keys()),
                format_func=lambda k: f"{JOBS[k]['icon']}  {JOBS[k]['name']}",
                label_visibility="collapsed",
            )
            job = JOBS[job_key]

            st.markdown(f"""
            <div style="background:#F0F4FA; border-radius:8px; padding:12px 16px; margin:12px 0; font-size:13px; color:#4A6080;">
                {job['icon']} &nbsp;<b>{job['name']}</b><br>
                <span style="margin-top:4px; display:block;">{job['desc']}</span>
            </div>
            """, unsafe_allow_html=True)

            # Inputs específicos por job
            extra_input = {}

            if "query" in job["inputs"]:
                extra_input["query"] = st.text_area(
                    "Consulta SQL",
                    value="SEL TOP 100 * FROM DWH_PRESTAGE.IAAGENTS_S3 WHERE fecha_carga = CURRENT_DATE - 1",
                    height=100,
                )

            if "fecha" in job["inputs"]:
                extra_input["fecha"] = st.date_input("Fecha de reporte").strftime("%Y-%m-%d")

            st.markdown("</div>", unsafe_allow_html=True)

            # Botón ejecutar
            ejecutar = st.button(f"▶  Ejecutar — {job['name']}", use_container_width=True)

        with col_right:
            st.markdown('<div class="card" style="min-height:320px;">', unsafe_allow_html=True)
            st.markdown('<div class="card-title">📊 Resultado</div>', unsafe_allow_html=True)

            if ejecutar:
                audit(f"EJECUTAR_JOB", f"Job: {job_key} | Inputs: {extra_input}")
                st.session_state.job_result = None

                with st.spinner(f"Ejecutando **{job['name']}**..."):
                    bar = st.progress(0)
                    for pct in range(0, 101, 20):
                        time.sleep(0.15)
                        bar.progress(pct)

                    if job_key == "carga_sftp":
                        df_result = run_job_sftp()
                    elif job_key == "consulta_teradata":
                        df_result = run_job_teradata(extra_input.get("query", ""))
                    elif job_key == "alerta_iaagents":
                        df_result = run_job_iaagents(extra_input.get("fecha", "2026-04-16"))
                    else:
                        df_result = pd.DataFrame()

                    bar.progress(100)

                st.session_state.job_result = df_result
                audit("JOB_COMPLETADO", f"Job: {job_key} | Filas resultado: {len(df_result)}")
                st.success(f"✅ Job completado — {len(df_result)} registros obtenidos")

            if st.session_state.job_result is not None:
                df_r = st.session_state.job_result
                if not df_r.empty:
                    # Métricas rápidas
                    m1, m2, m3 = st.columns(3)
                    m1.metric("Filas", f"{len(df_r):,}")
                    m2.metric("Columnas", len(df_r.columns))
                    if "alerta" in df_r.columns:
                        dif = (df_r["alerta"] != "OK").sum()
                        m3.metric("Alertas", int(dif), delta=f"-{dif}" if dif > 0 else None, delta_color="inverse")

                    st.dataframe(df_r, use_container_width=True, height=240)

                    # Exportar Excel
                    xlsx_bytes = df_to_excel(df_r, sheet_name=job["name"])
                    fname = f"{job_key}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                    st.download_button(
                        label="⬇️  Descargar Excel",
                        data=xlsx_bytes,
                        file_name=fname,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True,
                    )
                    audit("DESCARGA_EXCEL", f"Archivo: {fname} | Filas: {len(df_r)}")
                else:
                    st.info("El job se ejecutó pero no retornó datos.")
            else:
                st.markdown("""
                <div style="text-align:center; padding:60px 20px; color:#94A3B8;">
                    <div style="font-size:48px; margin-bottom:12px;">⚡</div>
                    <div style="font-size:14px;">Selecciona un job y presiona <b>Ejecutar</b></div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════
    # TAB 2 — Ingreso Manual
    # ════════════════════════════════════════════════════════
    with tab_form:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">📝 Formulario de ingreso manual de datos</div>', unsafe_allow_html=True)
        st.markdown('<div class="card-desc">Completa el formulario. Los registros se acumulan en la sesión y se pueden exportar a Excel.</div>', unsafe_allow_html=True)

        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            f_tarjeta = st.text_input("Número de tarjeta", placeholder="4000 0000 0000 0000")
            f_cedula  = st.text_input("Cédula / RUC",      placeholder="1700000000")
        with col_f2:
            f_nombre  = st.text_input("Nombre completo",   placeholder="Juan Pérez")
            f_marca   = st.selectbox("Marca", ["VISA", "MASTERCARD", "DINERS", "AMEX"])
        with col_f3:
            f_valor   = st.number_input("Valor ($)", min_value=0.0, step=0.01, format="%.2f")
            f_obs     = st.text_input("Observación", placeholder="Opcional")

        col_add, col_clear, _ = st.columns([1, 1, 3])
        with col_add:
            add_btn = st.button("➕ Agregar registro", use_container_width=True)
        with col_clear:
            if st.button("🗑️ Limpiar tabla", use_container_width=True):
                st.session_state["form_data"] = []
                st.rerun()

        if "form_data" not in st.session_state:
            st.session_state["form_data"] = []

        if add_btn:
            if not f_tarjeta or not f_nombre:
                st.warning("Tarjeta y Nombre son obligatorios.")
            else:
                st.session_state["form_data"].append({
                    "tarjeta":      f_tarjeta,
                    "cedula":       f_cedula,
                    "nombre":       f_nombre,
                    "marca":        f_marca,
                    "valor":        f_valor,
                    "observacion":  f_obs,
                    "usuario":      st.session_state.user_display,
                    "timestamp":    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                })
                audit("FORM_ADD", f"Tarjeta: {f_tarjeta[-4:]} | Nombre: {f_nombre}")
                st.success("✅ Registro agregado.")

        if st.session_state["form_data"]:
            df_form = pd.DataFrame(st.session_state["form_data"])
            st.markdown(f"**{len(df_form)} registros ingresados**")
            st.dataframe(df_form, use_container_width=True, height=200)

            xlsx_form = df_to_excel(df_form, sheet_name="Ingreso Manual")
            fname_form = f"ingreso_manual_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            st.download_button(
                "⬇️  Exportar a Excel",
                data=xlsx_form,
                file_name=fname_form,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=False,
            )
        else:
            st.info("Aún no hay registros. Completa el formulario y presiona **Agregar registro**.")

        st.markdown("</div>", unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════
    # TAB 3 — Auditoría
    # ════════════════════════════════════════════════════════
    with tab_audit:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">📋 Registro de auditoría de sesión</div>', unsafe_allow_html=True)
        st.markdown('<div class="card-desc">Todas las acciones realizadas quedan registradas con usuario, timestamp y detalle. El log completo se guarda en <code>audit_log.jsonl</code>.</div>', unsafe_allow_html=True)

        logs = list(reversed(st.session_state.audit_log))
        if logs:
            df_audit = pd.DataFrame(logs)
            st.dataframe(df_audit, use_container_width=True, height=300)

            xlsx_audit = df_to_excel(df_audit, "Auditoria")
            st.download_button(
                "⬇️  Exportar auditoría",
                data=xlsx_audit,
                file_name=f"auditoria_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        else:
            st.info("No hay eventos registrados aún en esta sesión.")

        st.markdown("</div>", unsafe_allow_html=True)

    # ── Footer + cerrar sesión ────────────────────────────────
    st.markdown("---")
    col_f1, col_f2 = st.columns([4, 1])
    with col_f1:
        st.caption(f"Diners Club Ecuador · Autoservicio Data & IA · Sesión iniciada: {st.session_state.login_time}")
    with col_f2:
        if st.button("🚪 Cerrar sesión"):
            audit("LOGOUT", "Cierre de sesión")
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()


# ─────────────────────────────────────────────────────────────
# ROUTER principal
# ─────────────────────────────────────────────────────────────
if not st.session_state.authenticated:
    show_login()
else:
    show_main()
