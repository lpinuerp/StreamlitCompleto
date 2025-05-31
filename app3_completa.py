import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
import pygwalker as pyg
import streamlit.components.v1 as components
from io import BytesIO

# ----------------------------
# CONFIGURACIÓN GENERAL DE LA APLICACIÓN
# ----------------------------


st.set_page_config(page_title="Dashboard Titanic", layout="wide")


st.title("Dashboard Interactivo: Análisis del Titanic")


# ----------------------------
# CARGA DEL DATASET LOCAL
# ----------------------------





@st.cache_data
def cargar_datos():
    #return sns.load_dataset("titanic")
    return pd.read_csv("titanic.csv")

df = cargar_datos()



st.write("Vista previa de los datos:")



st.dataframe(df.head())

# ----------------------------
# SIDEBAR: FILTROS INTERACTIVOS
# ----------------------------


st.sidebar.header("Filtros del Panel")



clase = st.sidebar.selectbox("Clase del pasajero", df["Pclass"].unique())

sexo = st.sidebar.multiselect("Sexo", df["Sex"].unique(), default=df["Sex"].unique())



edad = st.sidebar.slider("Edad", int(df["Age"].min()), int(df["Age"].max()), (15, 50))



embarked = st.sidebar.radio("Puerto de Embarque", df["Embarked"].dropna().unique())


solo_supervivientes = st.sidebar.checkbox("Mostrar solo sobrevivientes")

# ----------------------------
# APLICAR FILTROS AL DATAFRAME
# ----------------------------


df_filtrado = df[
    (df["Pclass"] == clase) &
    (df["Sex"].isin(sexo)) &
    (df["Age"].between(edad[0], edad[1])) &
    (df["Embarked"] == embarked)
]
if solo_supervivientes:
    df_filtrado = df_filtrado[df_filtrado["Survived"] == 1]


# ----------------------------
# MENÚ PRINCIPAL CON SELECTBOX
# ----------------------------
with st.expander(" ¿Qué hace selectbox?"):
    """
    st.selectbox
    Permite al usuario seleccionar una opción de un menú desplegable.
    Aquí se utiliza como menú de navegación para separar secciones de la app en vistas exclusivas:
    - "Análisis General": KPIs, visualizaciones con Seaborn y Plotly.
    - "Exploración con PyGWalker": vista interactiva automática y carga desde JSON.
    """
menu = st.selectbox("Selecciona una sección", ["Elige un Menú","Análisis General", "Exploración con PyGWalker"])


# ------------------------------------------------------------------------------------
# MENU SECCION ANALISIS GENERAL
# ------------------------------------------------------------------------------------

if menu == "Análisis General":

    # ----------------------------
    # KPIs USANDO METRICS Y COLUMNS
    # ----------------------------



    col1, col2, col3 = st.columns(3)




    total = len(df_filtrado)
    supervivientes = df_filtrado["Survived"].sum()
    porc = round((supervivientes / total) * 100, 2) if total > 0 else 0
    col1.metric(" Total Pasajeros", total)
    col2.metric("Supervivientes", supervivientes)
    col3.metric(" Tasa de Supervivencia", f"{porc}%")

    # ----------------------------
    # VISUALIZACIÓN CON SEABORN
    # ----------------------------


    st.subheader(" Distribución de Edad (Seaborn)")
    fig, ax = plt.subplots()
    sns.histplot(data=df_filtrado, x="Age", hue="Survived", multiple="stack", palette="pastel", bins=20, ax=ax)
    ax.set_title("Distribución de Edad por Supervivencia")
    st.pyplot(fig)

    # ----------------------------
    # VISUALIZACIÓN INTERACTIVA CON PLOTLY
    # ----------------------------


    st.subheader(" Supervivencia por Clase y Sexo (Plotly)")



    fig2 = px.histogram(
        df_filtrado,
        x="Pclass",
        color="Sex",
        barmode="group",
        histfunc="count",
        facet_col="Survived",
        category_orders={"Pclass": [1, 2, 3]},
        labels={"Survived": "Sobrevivió?"}
    )



    st.plotly_chart(fig2, use_container_width=True)

    # ----------------------------
    # TABS PARA ORGANIZAR CONTENIDO
    # ----------------------------


    tab1, tab2, tab3 = st.tabs([" Tabla", " Gráficos", " Estadísticas"])

    with tab1:
        st.dataframe(df_filtrado)

    with tab2:
        fig3 = px.violin(df_filtrado, y="Age", x="Sex", color="Survived", box=True, points="all")
        st.plotly_chart(fig3, use_container_width=True)

    with tab3:
        st.write(" Estadísticas descriptivas:")
        st.dataframe(df_filtrado.describe())

    # ----------------------------
    # EXPANDER PARA CONTENIDO COLAPSABLE
    # ----------------------------

    with st.expander(" ¿Qué significa cada columna?"):
        st.markdown("""
        - `Pclass`: clase del pasajero (1 = Primera, 2 = Segunda, 3 = Tercera)
        - `Sex`: sexo
        - `Age`: edad
        - `SibSp`: número de hermanos / cónyuges a bordo
        - `Parch`: número de padres / hijos a bordo
        - `Fare`: tarifa pagada
        - `Embarked`: puerto de embarque
        - `Survived`: 0 = No, 1 = Sí
        """)

    # ----------------------------
    # FORMULARIO PARA INTERACCIÓN DEL USUARIO
    # ----------------------------

    with st.form("formulario_feedback"):
        st.subheader(" Feedback del usuario")


        nombre = st.text_input("Tu nombre")

        comentario = st.text_area("¿Qué te pareció el dashboard?")
 
        puntaje = st.slider("Puntaje de satisfacción:", 1, 10, 5)
 
        enviar = st.form_submit_button("Enviar")

        if enviar:
    
            st.success(f"\Gracias {nombre}! Calificaste el dashboard con un {puntaje}/10.")

    # ----------------------------
    # FUNCIONALIDAD PARA EXPORTAR A EXCEL
    # ----------------------------

    def convertir_a_excel(df):
        output = BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False, sheet_name="Pasajeros")
        return output.getvalue()



    st.download_button(
        label="Descargar Excel",
        data=convertir_a_excel(df_filtrado),
        file_name="titanic_filtrado.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


# ------------------------------------------------------------------------------------
# MENU SECCION ANALISIS PYGWALKER
# ------------------------------------------------------------------------------------

elif menu == "Exploración con PyGWalker":
    st.subheader("🧭 PyGWalker - Exploración Visual")
    tab_pyg1, tab_pyg2 = st.tabs(["⚙️ PyGWalker dinámico", "📁 Cargar JSON de PyGWalker"])

    with tab_pyg1:
        generated_html = pyg.to_html(df_filtrado, return_html=True, dark='light')
        st.subheader("⚙️ Exploración Dinámica con PyGWalker")
        components.html(generated_html, height=800, scrolling=True)

    with tab_pyg2:
        st.subheader("📁 Subir archivo JSON de PyGWalker")
        uploaded_file = st.file_uploader("Selecciona un archivo .json exportado desde PyGWalker", type="json")

        if uploaded_file is not None:
            try:
                json_content = uploaded_file.read().decode("utf-8")
                components.html(json_content, height=800, scrolling=True)
            except Exception as e:
                st.error(f"Error al cargar el archivo: {e}")


else:
    st.write("Elige una seccion")

# ----------------------------
# FOOTER CON INFORMACIÓN DE CONTACTO
# ----------------------------


st.sidebar.markdown("---")
st.sidebar.markdown("Creado por: **Tu Nombre**")
st.sidebar.markdown(" contacto@tucorreo.com")



## requirements
#streamlit
#pandas
#seaborn
#matplotlib
#plotly
#xlsxwriter
# pygwalker