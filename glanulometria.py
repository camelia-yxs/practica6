import numpy as np
import matplotlib.pyplot as plt
from fpdf import FPDF
from datetime import datetime

# ===========================
# FUNCIONES DEL PROGRAMA
# ===========================

def leer_datos_ensayo():
    N = int(input("Ingrese el número de tamices (N): "))
    diametros = []
    masas_retenidas = []

    for i in range(N):
        d = float(input(f"Diámetro del tamiz {i + 1} (mm): "))
        m = float(input(f"Masa retenida en tamiz {i + 1} (g): "))
        diametros.append(d)
        masas_retenidas.append(m)

    diametros = np.array(diametros)
    masas_retenidas = np.array(masas_retenidas)
    orden = np.argsort(diametros)[::-1]
    diametros = diametros[orden]
    masas_retenidas = masas_retenidas[orden]

    return diametros, masas_retenidas

def calcular_porcentajes(masas_retenidas):
    """
    Calcula masa total, masa acumulada y porcentaje que pasa (% pasa)
    usando los datos de masa retenida en cada tamiz.
    """
    masa_total = np.sum(masas_retenidas)
    masa_acumulada = np.cumsum(masas_retenidas)
    pasa = 100 - (masa_acumulada / masa_total) * 100
    return masa_total, masa_acumulada, pasa

def obtener_d(valor_objetivo, diametros, pasa):
    """
    Obtiene el diámetro (D10, D30 o D60) mediante interpolación logarítmica.
    """
    diametros = np.array(diametros, dtype=float)
    pasa = np.array(pasa, dtype=float)
    try:
        diametros_log = np.log10(diametros)
        log_d = np.interp(valor_objetivo, pasa[::-1], diametros_log[::-1])
        return 10 ** log_d
    except Exception:
        return np.nan

def calcular_parametros(diametros, pasa):
    D10 = obtener_d(10, diametros, pasa)
    D30 = obtener_d(30, diametros, pasa)
    D60 = obtener_d(60, diametros, pasa)
    if any(np.isnan([D10, D30, D60])) or D10 == 0 or D60 == 0:
        Cu, Cc = np.nan, np.nan
    else:
        Cu = D60 / D10
        Cc = (D30 ** 2) / (D60 * D10)
    return D10, D30, D60, Cu, Cc

def clasificar_suelo(Cu, Cc, LL=None, IP=None, P_fino=10, tipo="Arena"):
    if tipo == "Grava":
        if P_fino < 5:
            return "GW" if Cu >= 4 and 1 < Cc < 3 else "GP"
        elif P_fino >= 12:
            return "GM/GC"
        else:
            return "GP-GM"
    elif tipo == "Arena":
        if P_fino < 5:
            return "SW" if Cu >= 6 and 1 < Cc < 3 else "SP"
        elif P_fino >= 12:
            return "SM/SC"
        else:
            return "SP-SM"
    return "Tipo no definido"

# ===========================
# NUEVO: DATOS DEL ENSAYO
# ===========================

def datos_generales():
    print("\n=== Datos del Ensayo ===")
    nombre_suelo = input("Nombre del suelo: ")
    autor = input("Nombre del responsable: ")
    proyecto = input("Proyecto o lugar: ")
    fecha = datetime.now().strftime("%d/%m/%Y")
    return nombre_suelo, autor, proyecto, fecha

# ===========================
# GRÁFICA Y PDF
# ===========================

def graficar_curva(diametros, pasa):
    plt.figure()
    plt.semilogx(diametros, pasa, marker='o', color='b')
    plt.gca().invert_xaxis()
    plt.grid(True, which="both", linestyle="--", linewidth=0.5)
    plt.xlabel("Diámetro (mm)")
    plt.ylabel("% Que Pasa")
    plt.title("Curva Granulométrica")
    plt.tight_layout()
    plt.savefig("curva_granulometrica.png", dpi=300)
    plt.close()

def generar_reporte_pdf(nombre_suelo, autor, proyecto, fecha, D10, D30, D60, Cu, Cc, clasificacion):
    pdf = FPDF()
    pdf.add_page()

    # Encabezado
    pdf.set_fill_color(200, 220, 255)
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "REPORTE DE ANALISIS GRANULOMETRICO", ln=True, align="C", fill=True)
    pdf.ln(5)

    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 8, f"Nombre del suelo: {nombre_suelo}", ln=True)
    pdf.cell(0, 8, f"Proyecto / Lugar: {proyecto}", ln=True)
    pdf.cell(0, 8, f"Responsable: {autor}", ln=True)
    pdf.cell(0, 8, f"Fecha de generación: {fecha}", ln=True)
    pdf.ln(10)

    # Resultados
    pdf.set_font("Arial", "B", 14)
    pdf.set_fill_color(230, 230, 230)
    pdf.cell(0, 10, "Resultados del Ensayo", ln=True, align="C", fill=True)
    pdf.ln(5)

    pdf.set_font("Arial", "", 12)
    resultados = [
        ("D10 (mm)", f"{D10:.4f}"),
        ("D30 (mm)", f"{D30:.4f}"),
        ("D60 (mm)", f"{D60:.4f}"),
        ("Cu (Coef. Uniformidad)", f"{Cu:.4f}"),
        ("Cc (Coef. Curvatura)", f"{Cc:.4f}"),
        ("Clasificación SUCS", clasificacion),
    ]

    for nombre, valor in resultados:
        pdf.cell(80, 8, nombre, border=1)
        pdf.cell(60, 8, valor, border=1, ln=True)

    pdf.ln(10)

    # Imagen
    try:
        pdf.image("curva_granulometrica.png", x=15, w=180)
    except:
        pdf.cell(0, 10, "⚠ No se pudo insertar la gráfica.", ln=True)

    pdf.output("reporte_granulometrico.pdf")
    print("✅ PDF generado con éxito: reporte_granulometrico.pdf")

# ===========================
# MAIN
# ===========================

def main():
    print("\n=== ANÁLISIS GRANULOMÉTRICO ===")

    nombre_suelo, autor, proyecto, fecha = datos_generales()
    diametros, masas_retenidas = leer_datos_ensayo()
    masa_total, masa_acumulada, pasa = calcular_porcentajes(masas_retenidas)
    D10, D30, D60, Cu, Cc = calcular_parametros(diametros, pasa)
    clasificacion = clasificar_suelo(Cu, Cc)

    print(f"\nResultados:")
    print(f"D10 = {D10:.4f} mm")
    print(f"D30 = {D30:.4f} mm")
    print(f"D60 = {D60:.4f} mm")
    print(f"Cu = {Cu:.4f}")
    print(f"Cc = {Cc:.4f}")
    print(f"Clasificación SUCS: {clasificacion}")

    graficar_curva(diametros, pasa)
    generar_reporte_pdf(nombre_suelo, autor, proyecto, fecha, D10, D30, D60, Cu, Cc, clasificacion)


if _name_ == "_main_":
    main()
