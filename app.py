import io
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Caso de Estudio - New York Stock Exchange", layout="centered")


class DataAnalyzer:
    """
    Clase que encapsula la carga, clasificación y análisis estadístico
    del dataset de estados financieros de empresas listadas en la NYSE.
    """

    def __init__(self, archivo_csv):
        self.df = pd.read_csv(archivo_csv)

        # "Unnamed: 0" solo representa el índice original del archivo, no aporta valor analítico
        if "Unnamed: 0" in self.df.columns:
            self.df = self.df.drop(columns=["Unnamed: 0"])

        # Columna auxiliar de año, derivada de Period Ending (sin valores nulos)
        self.df["Año (Period Ending)"] = pd.to_datetime(self.df["Period Ending"], errors="coerce").dt.year

    def es_valido(self):
        return self.df is not None and len(self.df) > 0

    def clasificar_variables(self):
        numericas = self.df.select_dtypes(include=np.number).columns.tolist()
        categoricas = self.df.select_dtypes(exclude=np.number).columns.tolist()
        return numericas, categoricas

    def resumen_nulos(self):
        nulos = self.df.isnull().sum()
        porcentaje = (nulos / len(self.df) * 100).round(2)
        resumen = pd.DataFrame({"Valores nulos": nulos, "Porcentaje (%)": porcentaje})
        return resumen[resumen["Valores nulos"] > 0].sort_values("Valores nulos", ascending=False)

    def estadisticas_descriptivas(self, columnas):
        return self.df[columnas].describe()

    def detectar_outliers(self, columna):
        q1 = self.df[columna].quantile(0.25)
        q3 = self.df[columna].quantile(0.75)
        iqr = q3 - q1
        limite_inferior = q1 - 1.5 * iqr
        limite_superior = q3 + 1.5 * iqr
        outliers = self.df[(self.df[columna] < limite_inferior) | (self.df[columna] > limite_superior)]
        return len(outliers), limite_inferior, limite_superior

    def filtrar_por_rango(self, columna, valor_min, valor_max):
        return self.df[(self.df[columna] >= valor_min) & (self.df[columna] <= valor_max)]


# ============================================================
# MENÚ LATERAL
# ============================================================
menu = st.sidebar.selectbox(
    "Selecciona una sección",
    ["Home", "Carga de Dataset", "Análisis Exploratorio de Datos", "Conclusiones Finales"]
)

# ============================================================
# HOME
# ============================================================
if menu == "Home":
    st.image("logo-secundario-dmc-institute-01.png", width=250)
    st.title("Análisis Exploratorio de Datos Financieros - New York Stock Exchange")
    st.subheader("Caso de Estudio N°6 - Especialización en Python for Analytics")

    st.markdown("**Nombre completo:** Alexander Marcel José Ñaccha Ñarquez")
    st.markdown("**Curso / Especialización:** Especialización en Python for Analytics")
    st.markdown("**Año:** 2026")

    st.markdown("### Objetivo del análisis")
    st.write(
        "Esta aplicación analiza los estados financieros históricos de empresas "
        "listadas en la Bolsa de Nueva York (NYSE), evaluando indicadores de "
        "ingresos, rentabilidad, liquidez, activos, pasivos y patrimonio. "
        "El objetivo es identificar patrones que apoyen la toma de decisiones, "
        "sin construir modelos predictivos."
    )

    st.markdown("### Sobre el dataset")
    st.write(
        "El archivo New York Stock Exchange.csv contiene 1,781 registros y "
        "79 variables financieras correspondientes a 448 símbolos bursátiles, "
        "con información de balance general, estado de resultados, flujos de "
        "efectivo y razones financieras."
    )

    st.markdown("### Tecnologías utilizadas")
    st.write("- Python")
    st.write("- Streamlit")
    st.write("- Pandas y NumPy")
    st.write("- Matplotlib y Seaborn")

# ============================================================
# CARGA DE DATASET
# ============================================================
elif menu == "Carga de Dataset":
    st.title("Carga de Dataset")

    archivo = st.file_uploader("Sube el archivo New York Stock Exchange.csv", type=["csv"])

    if archivo is not None:
        analizador = DataAnalyzer(archivo)

        if analizador.es_valido():
            st.session_state["analizador"] = analizador
            st.success("Archivo cargado correctamente")

            st.markdown("### Vista previa del dataset")
            st.dataframe(analizador.df.head())

            st.markdown("### Dimensiones del dataset")
            st.write(f"Filas: {analizador.df.shape[0]}  |  Columnas: {analizador.df.shape[1]}")
        else:
            st.error("El archivo cargado no contiene datos válidos")
    else:
        st.info("Sube un archivo CSV para continuar")

# ============================================================
# ANÁLISIS EXPLORATORIO DE DATOS (EDA)
# ============================================================
elif menu == "Análisis Exploratorio de Datos":
    st.title("Análisis Exploratorio de Datos (EDA)")

    if "analizador" not in st.session_state:
        st.warning("Primero debes cargar el dataset en la sección 'Carga de Dataset'")
        st.stop()

    analizador = st.session_state["analizador"]
    df = analizador.df

    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10 = st.tabs([
        "1. Info general", "2. Clasificación", "3. Estadísticas", "4. Nulos",
        "5. Distribución", "6. Categóricas", "7. Bivariado N-C", "8. Bivariado C-C",
        "9. Parámetros", "10. Hallazgos"
    ])

    # ---------------- ÍTEM 1: INFORMACIÓN GENERAL ----------------
    with tab1:
        st.markdown("### Información general del dataset")

        buffer = io.StringIO()
        df.info(buf=buffer)
        st.text(buffer.getvalue())

        col1, col2 = st.columns(2)
        col1.metric("Valores nulos totales", int(df.isnull().sum().sum()))
        col2.metric("Registros duplicados", int(df.duplicated().sum()))

    # ---------------- ÍTEM 2: CLASIFICACIÓN DE VARIABLES ----------------
    with tab2:
        st.markdown("### Clasificación de variables")
        numericas, categoricas = analizador.clasificar_variables()

        col1, col2 = st.columns(2)
        col1.metric("Variables numéricas", len(numericas))
        col2.metric("Variables categóricas", len(categoricas))

        st.write("Variables numéricas:")
        st.write(numericas)
        st.write("Variables categóricas:")
        st.write(categoricas)

    # ---------------- ÍTEM 3: ESTADÍSTICAS DESCRIPTIVAS ----------------
    with tab3:
        st.markdown("### Estadísticas descriptivas")
        numericas, categoricas = analizador.clasificar_variables()

        columnas_describe = st.multiselect(
            "Selecciona columnas numéricas",
            numericas,
            default=["Total Revenue", "Net Income", "Total Assets", "Total Liabilities"]
        )

        if columnas_describe:
            st.dataframe(analizador.estadisticas_descriptivas(columnas_describe))
            st.write("Moda de las columnas seleccionadas:")
            st.dataframe(df[columnas_describe].mode().iloc[[0]])
            st.write(
                "La media y la mediana muestran el valor central de cada variable, "
                "mientras que la desviación estándar indica qué tan dispersos están "
                "los datos. Cuando la media es mucho mayor que la mediana, suele "
                "haber valores extremos que elevan el promedio."
            )

        st.markdown("#### Detección de valores atípicos (método IQR)")
        columna_outlier = st.selectbox("Selecciona una columna para analizar outliers", numericas)
        cantidad, li, ls = analizador.detectar_outliers(columna_outlier)
        st.write(f"Límite inferior: {li:,.2f}  |  Límite superior: {ls:,.2f}")
        st.write(f"Cantidad de valores atípicos detectados: {cantidad}")

    # ---------------- ÍTEM 4: VALORES FALTANTES ----------------
    with tab4:
        st.markdown("### Análisis de valores faltantes")
        resumen_nulos = analizador.resumen_nulos()

        if len(resumen_nulos) > 0:
            st.dataframe(resumen_nulos)

            fig, ax = plt.subplots()
            resumen_nulos["Valores nulos"].plot(kind="bar", ax=ax)
            ax.set_ylabel("Cantidad de nulos")
            ax.set_title("Valores nulos por columna")
            st.pyplot(fig)

            st.write(
                "Los valores faltantes se concentran en Cash Ratio, Current Ratio, "
                "Quick Ratio, Earnings Per Share, Estimated Shares Outstanding y "
                "For Year. No se imputan de forma automática porque son razones "
                "financieras que dependen de otras cuentas del balance; sustituirlas "
                "con la media o la mediana distorsionaría la comparación entre "
                "empresas."
            )
        else:
            st.write("El dataset no presenta valores nulos.")

    # ---------------- ÍTEM 5: DISTRIBUCIÓN DE VARIABLES NUMÉRICAS ----------------
    with tab5:
        st.markdown("### Distribución de variables numéricas")

        variables_clave = ["Total Revenue", "Net Income", "Total Assets", "Total Liabilities"]
        variable_dist = st.selectbox("Selecciona una variable financiera", variables_clave)

        escala = st.radio("Escala de visualización", ["Millones", "Miles de millones"], horizontal=True)
        divisor = 1_000_000 if escala == "Millones" else 1_000_000_000
        etiqueta = "USD (millones)" if escala == "Millones" else "USD (miles de millones)"

        datos_escalados = df[variable_dist] / divisor

        fig, ax = plt.subplots()
        ax.hist(datos_escalados.dropna(), bins=30)
        ax.set_xlabel(etiqueta)
        ax.set_title(f"Distribución de {variable_dist}")
        st.pyplot(fig)

        valores_negativos = int((df[variable_dist] < 0).sum())
        st.write(f"Valores negativos en {variable_dist}: {valores_negativos}")
        st.write(
            "La distribución está concentrada en valores bajos con una cola larga "
            "hacia la derecha (sesgo positivo): la mayoría de empresas reporta "
            "montos moderados, mientras que unas pocas compañías muy grandes "
            "elevan el promedio general."
        )

    # ---------------- ÍTEM 6: VARIABLES CATEGÓRICAS ----------------
    with tab6:
        st.markdown("### Análisis de variables categóricas")

        conteo_ticker = df["Ticker Symbol"].value_counts().head(10)
        proporcion_ticker = (conteo_ticker / len(df) * 100).round(2)

        tabla_categorica = pd.DataFrame({
            "Cantidad de registros": conteo_ticker,
            "Proporción (%)": proporcion_ticker
        })
        st.write("Top 10 empresas (Ticker Symbol) con más registros en el dataset:")
        st.dataframe(tabla_categorica)

        fig, ax = plt.subplots()
        conteo_ticker.plot(kind="bar", ax=ax)
        ax.set_ylabel("Cantidad de registros")
        ax.set_title("Top 10 empresas con más registros")
        st.pyplot(fig)

        st.write(f"Número total de empresas (Ticker Symbol) distintas: {df['Ticker Symbol'].nunique()}")

    # ---------------- ÍTEM 7: BIVARIADO NUMÉRICO vs CATEGÓRICO ----------------
    with tab7:
        st.markdown("### Análisis bivariado: numérico vs categórico")

        tickers_disponibles = sorted(df["Ticker Symbol"].unique().tolist())
        tickers_seleccionados = st.multiselect(
            "Selecciona empresas (Ticker Symbol) a comparar",
            tickers_disponibles,
            default=tickers_disponibles[:5]
        )

        if tickers_seleccionados:
            df_filtrado = df[df["Ticker Symbol"].isin(tickers_seleccionados)]

            st.markdown("#### Total Revenue por empresa en un período seleccionado")
            anios_rev = sorted(df["Año (Period Ending)"].dropna().unique().tolist())
            anio_rev = st.selectbox("Selecciona el año del período (Period Ending)", anios_rev, index=anios_rev.index(2015))
            df_rev = df_filtrado[df_filtrado["Año (Period Ending)"] == anio_rev]

            if len(df_rev) > 0:
                fig0, ax0 = plt.subplots()
                ax0.bar(df_rev["Ticker Symbol"], df_rev["Total Revenue"] / 1_000_000_000)
                ax0.set_ylabel("Total Revenue (miles de millones USD)")
                ax0.set_title(f"Total Revenue por empresa - {int(anio_rev)}")
                st.pyplot(fig0)
            else:
                st.write("Las empresas seleccionadas no tienen registros en ese año.")

            st.markdown("#### Net Income por empresa")
            fig, ax = plt.subplots()
            sns.barplot(data=df_filtrado, x="Ticker Symbol", y="Net Income", ax=ax)
            ax.set_title("Utilidad neta (Net Income) por empresa")
            ax.set_ylabel("Net Income (USD)")
            st.pyplot(fig)

            col1, col2 = st.columns(2)
            with col1:
                fig2, ax2 = plt.subplots()
                sns.boxplot(data=df_filtrado, x="Ticker Symbol", y="Current Ratio", ax=ax2)
                ax2.set_title("Current Ratio por empresa")
                plt.xticks(rotation=45)
                st.pyplot(fig2)
            with col2:
                fig3, ax3 = plt.subplots()
                sns.boxplot(data=df_filtrado, x="Ticker Symbol", y="Quick Ratio", ax=ax3)
                ax3.set_title("Quick Ratio por empresa")
                plt.xticks(rotation=45)
                st.pyplot(fig3)
        else:
            st.write("Selecciona al menos una empresa para ver el análisis.")

    # ---------------- ÍTEM 8: BIVARIADO CATEGÓRICO vs CATEGÓRICO ----------------
    with tab8:
        st.markdown("### Análisis bivariado: categórico vs categórico")

        df_cat = df.dropna(subset=["Profit Margin", "Current Ratio"]).copy()

        df_cat["Categoría de rentabilidad"] = pd.cut(
            df_cat["Profit Margin"], bins=[-1, 5, 15, 1000],
            labels=["Baja (<=5%)", "Media (5%-15%)", "Alta (>15%)"]
        )
        df_cat["Categoría de liquidez"] = pd.cut(
            df_cat["Current Ratio"], bins=[-1, 100, 200, 5000],
            labels=["Baja (<=100)", "Media (100-200)", "Alta (>200)"]
        )

        tabla_cruzada = pd.crosstab(df_cat["Categoría de rentabilidad"], df_cat["Categoría de liquidez"])
        st.write("Relación entre categoría de rentabilidad y categoría de liquidez:")
        st.dataframe(tabla_cruzada)

        fig, ax = plt.subplots()
        tabla_cruzada.plot(kind="bar", stacked=True, ax=ax)
        ax.set_ylabel("Cantidad de registros")
        ax.set_title("Rentabilidad vs Liquidez")
        st.pyplot(fig)

        st.markdown("#### Categoría de rentabilidad por empresa")
        top_tickers = df_cat["Ticker Symbol"].value_counts().head(10).index
        tabla_ticker = pd.crosstab(
            df_cat[df_cat["Ticker Symbol"].isin(top_tickers)]["Ticker Symbol"],
            df_cat["Categoría de rentabilidad"]
        )
        st.dataframe(tabla_ticker)

        st.markdown("#### Disponibilidad de datos por año")
        conteo_anio = df["Año (Period Ending)"].value_counts().sort_index()

        fig2, ax2 = plt.subplots()
        conteo_anio.plot(kind="bar", ax=ax2)
        ax2.set_ylabel("Cantidad de registros")
        ax2.set_title("Registros disponibles por año (Period Ending)")
        st.pyplot(fig2)

    # ---------------- ÍTEM 9: ANÁLISIS POR PARÁMETROS SELECCIONADOS ----------------
    with tab9:
        st.markdown("### Análisis basado en parámetros seleccionados")

        numericas, categoricas = analizador.clasificar_variables()

        ticker_filtro = st.multiselect(
            "Filtrar por empresa (Ticker Symbol)",
            sorted(df["Ticker Symbol"].unique().tolist())
        )

        anios_disponibles = sorted(df["For Year"].dropna().unique().tolist())
        anio_filtro = st.multiselect("Filtrar por año (For Year)", anios_disponibles)

        periodos_disponibles = sorted(df["Period Ending"].astype(str).unique().tolist())
        periodo_filtro = st.multiselect("Filtrar por fecha de cierre (Period Ending)", periodos_disponibles)

        metrica = st.selectbox("Selecciona una métrica financiera a visualizar", numericas)
        unidad = st.selectbox("Unidad de visualización", ["Unidades", "Miles", "Millones", "Miles de millones"])

        df_resultado = df.copy()
        if ticker_filtro:
            df_resultado = df_resultado[df_resultado["Ticker Symbol"].isin(ticker_filtro)]
        if anio_filtro:
            df_resultado = df_resultado[df_resultado["For Year"].isin(anio_filtro)]
        if periodo_filtro:
            df_resultado = df_resultado[df_resultado["Period Ending"].astype(str).isin(periodo_filtro)]

        valor_min = float(df_resultado[metrica].min()) if len(df_resultado) > 0 else 0.0
        valor_max = float(df_resultado[metrica].max()) if len(df_resultado) > 0 else 0.0

        if valor_min < valor_max:
            rango = st.slider(f"Filtrar por rango de {metrica}", valor_min, valor_max, (valor_min, valor_max))
            df_resultado = analizador.filtrar_por_rango(metrica, rango[0], rango[1])
            if ticker_filtro:
                df_resultado = df_resultado[df_resultado["Ticker Symbol"].isin(ticker_filtro)]
            if anio_filtro:
                df_resultado = df_resultado[df_resultado["For Year"].isin(anio_filtro)]
            if periodo_filtro:
                df_resultado = df_resultado[df_resultado["Period Ending"].astype(str).isin(periodo_filtro)]

        divisores = {"Unidades": 1, "Miles": 1_000, "Millones": 1_000_000, "Miles de millones": 1_000_000_000}
        st.write(f"Registros filtrados: {len(df_resultado)}")

        mostrar_tabla = st.checkbox("Mostrar tabla de datos filtrados", value=True)
        if mostrar_tabla:
            st.dataframe(df_resultado[["Ticker Symbol", "Period Ending", "For Year", metrica]])

        if len(df_resultado) > 0:
            valores_escalados = df_resultado[metrica] / divisores[unidad]
            fig, ax = plt.subplots()
            if len(df_resultado) <= 30:
                ax.bar(df_resultado["Ticker Symbol"] + " (" + df_resultado["Period Ending"].astype(str) + ")", valores_escalados)
                ax.set_ylabel(f"{metrica} ({unidad})")
                plt.xticks(rotation=90)
            else:
                ax.hist(valores_escalados.dropna(), bins=30)
                ax.set_xlabel(f"{metrica} ({unidad})")
                ax.set_ylabel("Cantidad de registros")
                st.write("Hay más de 30 registros, por eso se muestra un histograma en lugar de barras.")
            st.pyplot(fig)

        st.caption(
            "Nota: la columna 'Unnamed: 0' fue eliminada desde la carga del dataset "
            "por representar únicamente un índice sin valor analítico."
        )

    # ---------------- ÍTEM 10: HALLAZGOS CLAVE ----------------
    with tab10:
        st.markdown("### Hallazgos clave")

        resumen_general = df.groupby("Ticker Symbol").agg({
            "Total Revenue": "mean",
            "Net Income": "mean",
            "Total Assets": "mean"
        }).sort_values("Total Revenue", ascending=False).head(10)

        st.write("Top 10 empresas por ingreso promedio (Total Revenue):")
        st.dataframe(resumen_general)

        fig, ax = plt.subplots()
        (resumen_general["Total Revenue"] / 1_000_000_000).plot(kind="bar", ax=ax)
        ax.set_ylabel("Total Revenue (miles de millones USD)")
        ax.set_title("Top 10 empresas por ingreso promedio")
        plt.xticks(rotation=45)
        st.pyplot(fig)

        st.markdown("#### Principales hallazgos")
        st.markdown(
            "- El dataset presenta una alta concentración de valores extremos: "
            "unas pocas empresas muy grandes elevan considerablemente el promedio "
            "de Total Revenue y Total Assets respecto a la mediana.\n"
            "- 102 registros muestran utilidad neta (Net Income) negativa, lo que "
            "indica empresas con pérdidas en ese período.\n"
            "- Los valores faltantes en Cash Ratio, Current Ratio y Quick Ratio no "
            "parecen aleatorios: se concentran en periodos o empresas específicas, "
            "por lo que deben tratarse con cuidado antes de comparaciones agregadas.\n"
            "- La columna For Year contiene al menos un valor claramente erróneo "
            "(1215 en lugar de 2015), lo que confirma la necesidad de validar la "
            "calidad del dato antes de usarlo como filtro temporal."
        )

        st.markdown("#### Recomendaciones de interpretación")
        st.markdown(
            "- Comparar empresas usando medianas o razones financieras y no solo "
            "promedios, porque unas pocas compañías muy grandes distorsionan el promedio.\n"
            "- Revisar los registros con utilidad neta negativa de forma individual "
            "antes de incluirlos en comparaciones agregadas.\n"
            "- Excluir de forma explícita los registros sin razones de liquidez al "
            "comparar empresas, en lugar de rellenarlos con la media.\n"
            "- Validar los años (For Year) antes de filtrar por período."
        )

# ============================================================
# CONCLUSIONES FINALES
# ============================================================
elif menu == "Conclusiones Finales":
    st.title("Conclusiones Finales")

    if "analizador" not in st.session_state:
        st.warning("Primero debes cargar el dataset en la sección 'Carga de Dataset'")
        st.stop()

    df = st.session_state["analizador"].df

    st.markdown("#### 1. Concentración de ingresos en pocas empresas")
    top_empresa = df.groupby("Ticker Symbol")["Total Revenue"].mean().idxmax()
    mediana_revenue = df["Total Revenue"].median() / 1_000_000_000
    st.write(
        f"La distribución de Total Revenue está fuertemente sesgada hacia la derecha: "
        f"la empresa con mayor ingreso promedio es **{top_empresa}**, muy por encima "
        f"de la mediana del dataset (aprox. {mediana_revenue:.2f} miles de millones USD). "
        "Esto se evidenció en el histograma del Ítem 5."
    )

    st.markdown("#### 2. Existencia de empresas con pérdidas")
    negativos = int((df["Net Income"] < 0).sum())
    st.write(
        f"Se identificaron {negativos} registros con utilidad neta negativa "
        f"({negativos / len(df) * 100:.1f}% del total), confirmando que no todas "
        "las empresas del dataset fueron rentables en el período analizado "
        "(Ítems 3 y 5)."
    )

    st.markdown("#### 3. Valores faltantes concentrados en razones financieras")
    nulos_ratios = int(df[["Cash Ratio", "Current Ratio", "Quick Ratio"]].isnull().sum().sum())
    st.write(
        f"Las razones de liquidez (Cash Ratio, Current Ratio, Quick Ratio) concentran "
        f"{nulos_ratios} valores nulos en conjunto, por lo que cualquier comparación de "
        "liquidez entre empresas debe excluir explícitamente los registros incompletos "
        "en lugar de imputarlos automáticamente (Ítem 4)."
    )

    st.markdown("#### 4. Problemas de calidad en el campo For Year")
    anios_invalidos = df[df["For Year"].notna() & ~df["For Year"].between(1990, 2020)]
    st.write(
        f"Se detectó al menos {len(anios_invalidos)} registro(s) con valores inválidos "
        "en For Year (por ejemplo, 1215 en lugar de 2015), lo que confirma que este "
        "campo requiere validación antes de usarse como filtro temporal confiable "
        "(Ítem 8)."
    )

    st.markdown("#### 5. Relación entre rentabilidad y liquidez")
    df_c5 = df.dropna(subset=["Profit Margin", "Current Ratio"]).copy()
    df_c5["Categoría de rentabilidad"] = pd.cut(
        df_c5["Profit Margin"], bins=[-1, 5, 15, 1000],
        labels=["Baja (<=5%)", "Media (5%-15%)", "Alta (>15%)"]
    )
    df_c5["Categoría de liquidez"] = pd.cut(
        df_c5["Current Ratio"], bins=[-1, 100, 200, 5000],
        labels=["Baja (<=100)", "Media (100-200)", "Alta (>200)"]
    )
    proporciones = pd.crosstab(
        df_c5["Categoría de rentabilidad"], df_c5["Categoría de liquidez"], normalize="index"
    ) * 100
    alta_en_baja = proporciones.loc["Baja (<=5%)", "Alta (>200)"]
    alta_en_alta = proporciones.loc["Alta (>15%)", "Alta (>200)"]
    st.write(
        f"Entre las empresas con rentabilidad baja, solo {alta_en_baja:.1f}% tiene liquidez alta; "
        f"entre las de rentabilidad alta, el porcentaje sube a {alta_en_alta:.1f}%. "
        "Hay una relación positiva, pero no determinante: incluso entre las empresas "
        "más rentables, más de la mitad no alcanza una liquidez alta (Ítem 8). "
        "Por eso conviene evaluar ambos indicadores por separado al analizar la "
        "salud financiera de una empresa."
    )
    st.dataframe(proporciones.round(1))
