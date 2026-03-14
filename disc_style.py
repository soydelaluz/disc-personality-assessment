import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import random
import json
import base64
from io import BytesIO, StringIO
from disc_core import (
    load_questions,
    load_descriptions,
    calculate_raw_scores,
    normalize_scores,
    calculate_resultant_vector,
    get_style_description,
    get_relative_percentages
)
from disc_report import create_pdf_report


st.set_page_config(
    page_title="Evaluación de Personalidad DISC :bust_in_silhouette:",
    layout="wide",
    page_icon=":bust_in_silhouette:",
)

# Custom CSS to improve app appearance
st.markdown(
    """
<style>
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    .stButton>button {
        background-color: #184b6a;
        color: white;
        font-weight: bold;
    }
    .stProgress > div > div > div {
        background-color: #d3d3d3d3;
    }
</style>
""",
    unsafe_allow_html=True,
)

# App Title with custom styling
st.markdown(
    "<h1 style='text-align: center; color: #184b6a;'>Evaluación de Personalidad DISC 👤</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='text-align: center; font-style: italic;'>Descubre tu estilo de personalidad DISC respondiendo a las siguientes preguntas.</p>",
    unsafe_allow_html=True,
)

# Ensure session state variables are initialized
if "started" not in st.session_state:
    st.session_state.started = False

if "submitted" not in st.session_state:
    st.session_state.submitted = False

if "show_results" not in st.session_state:
    st.session_state.show_results = False

if "uploaded_file" not in st.session_state:
    st.session_state.uploaded_file = None

if "raw_score" not in st.session_state:
    st.session_state.raw_score = {"D": 0, "I": 0, "S": 0, "C": 0}

if "score" not in st.session_state:
    st.session_state.score = {"D": 0, "I": 0, "S": 0, "C": 0}

# If the user hasn't started the assessment yet
if not st.session_state.started:
    st.markdown(
        """
    ### Bienvenido a la Evaluación de Personalidad DISC

    La evaluación DISC es una herramienta que te ayuda a comprender tus rasgos de personalidad a través de cuatro dimensiones principales: Dominancia (D), Influencia (I), Estabilidad (S) y Cumplimiento (C). Al responder a una serie de preguntas, descubrirás tu estilo de personalidad y obtendrás información sobre cómo interactúas con los demás.

    #### Instrucciones:
    - Se te presentará una serie de afirmaciones.
    - Para cada afirmación, indica cuánto estás de acuerdo o en desacuerdo utilizando las opciones proporcionadas.
    - Un valor de **1** significa totalmente en desacuerdo, **2** algo en desacuerdo, **3** neutral, **4** algo de acuerdo, **5** totalmente de acuerdo.
    - Una vez finalizada la evaluación, recibirás tu perfil de estilo DISC y un desglose detallado de tus resultados.
    - Lee atentamente las descripciones, ya que algunas suenan parecidas pero tienen significados distintos.

    Haz clic en "Empezar" para iniciar la evaluación.
    """
    )

    # Create layout for buttons
    c1, c2, c3 = st.columns([1, 2, 1])

    # Handle the "Let's Begin" button press
    if c1.button("Empezar"):
        st.session_state.started = True
        st.session_state.submitted = False
        st.rerun()  # Rerun the script to move to the next stage

    # File upload option, which is shown after clicking "Upload Previous Results"
    if c3.checkbox("Cargar resultados anteriores"):
        # Display the file uploader when the button is clicked
        uploaded_file = st.file_uploader(
            "Carga tus resultados JSON anteriores", type=["json"]
        )
        if uploaded_file is not None:
            # Read the file as bytes
            bytes_data = uploaded_file.getvalue()

            # Convert bytes to string and then to a StringIO object
            stringio = StringIO(bytes_data.decode("utf-8"))

            # Read the JSON content from the string
            try:
                # Load the JSON content
                uploaded_file_content = json.load(stringio)
                # Assume the uploaded content is the normalized_score
                st.session_state.normalized_score = uploaded_file_content

                # Set session states to move forward
                st.session_state.started = True
                st.session_state.show_results = True
                st.session_state.submitted = True
                st.write("¡Archivo cargado y procesado con éxito!")
                st.rerun()  # Rerun to process the results

            except json.JSONDecodeError as e:
                st.error(f"Error al decodificar JSON: {e}")


# Updated plot function
def create_disc_plot(resultant_angle, resultant_magnitude):
    # Reduce the size of the figure by modifying figsize
    fig, ax = plt.subplots(
        figsize=(10, 10), subplot_kw={"projection": "polar"}
    )  # Reduce size from 10x10 to 6x6

    # The rest of your plotting code remains unchanged
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    ax.set_ylim(0, 1.01)

    ax.plot(
        resultant_angle,
        resultant_magnitude,
        "o",
        markersize=24,
        color="#4CAF50",
        label="Tu Estilo DISC",
    )

    categories = ["D", "I", "S", "C"]
    angles = [7 * np.pi / 4, np.pi / 4, 3 * np.pi / 4, 5 * np.pi / 4]
    ax.set_xticks(angles)
    ax.set_xticklabels(categories, fontsize=14, fontweight="bold")

    ax.axvline(x=0, color="gray", linestyle="--", alpha=0.7)
    ax.axvline(x=np.pi, color="gray", linestyle="--", alpha=0.7)

    ax.axvline(x=np.pi / 2, color="gray", linestyle="--", alpha=0.7)
    ax.axvline(x=3 * np.pi / 2, color="gray", linestyle="--", alpha=0.7)

    ax.set_yticklabels([])

    ax.grid(True, alpha=0.3)
    ax.spines["polar"].set_visible(False)
    ax.set_facecolor("#f0f2f6")

    plt.title("Tu Perfil de Estilo DISC", fontsize=16, fontweight="bold", pad=20)

    return fig


# Function to download JSON data
def get_json_download_link(normalized_score):
    json_str = json.dumps(normalized_score, indent=2)
    b64 = base64.b64encode(json_str.encode()).decode()
    href = f'<a href="data:application/json;base64,{b64}" download="disc_results.json">Descargar resultados JSON</a>'
    return href


def get_json_download_button(normalized_score):
    # Convert the normalized score dictionary into a JSON string
    json_str = json.dumps(normalized_score, indent=2)

    # Create a downloadable button using the JSON data
    st.download_button(
        label="Descargar resultados JSON",
        data=json_str,
        file_name="disc_results.json",
        mime="application/json",
    )


# Function to download PDF report
def get_pdf_download_link(pdf_buffer):
    # Encode the PDF buffer in base64 for downloading
    b64 = base64.b64encode(pdf_buffer.getvalue()).decode()
    href = f'<a href="data:application/pdf;base64,{b64}" download="disc_report.pdf">Descargar reporte PDF</a>'
    return href


def get_pdf_download_button(pdf_buffer):
    # Encode the PDF buffer in base64
    b64 = base64.b64encode(pdf_buffer.getvalue()).decode()

    # Convert base64 PDF into a downloadable button
    st.download_button(
        label="Descargar reporte PDF",
        data=pdf_buffer.getvalue(),
        file_name="disc_report.pdf",
        mime="application/pdf",
    )


# If the user has started the test, proceed with the questions
if st.session_state.started:

    # Initialize session state variables for the questions
    if "page_number" not in st.session_state:
        st.session_state.page_number = 0

    if "score" not in st.session_state:
        st.session_state.score = {"D": 0, "I": 0, "S": 0, "C": 0}

    if "answers" not in st.session_state:
        st.session_state.answers = {}

    if "show_results" not in st.session_state:
        st.session_state.show_results = False

    if "submitted" not in st.session_state:
        st.session_state.submitted = False

    if "questions" not in st.session_state:
        questions = load_questions()
        random.shuffle(questions)
        st.session_state.questions = questions[:30]  # Use the first 30 questions

    questions_per_page = 1  # Show one question at a time
    total_questions = len(st.session_state.questions)
    total_pages = (
        total_questions + questions_per_page - 1
    ) // questions_per_page  # Ceiling division

    # Load DISC descriptions
    disc_descriptions = load_descriptions()

    if not st.session_state.show_results:
        start = st.session_state.page_number * questions_per_page
        end = start + questions_per_page

        # Calculate progress
        progress = (st.session_state.page_number) / total_questions

        # Display progress bar outside the form
        st.progress(progress)
        
        with st.form(key=f"form_{st.session_state.page_number}"):
            i = start
            if i < total_questions:
                q = st.session_state.questions[i]
                n = i + 1
                st.markdown(f"#### {n}) {q['question']}")
                options = [
                    "Selecciona una opción",
                    "1 - Totalmente en desacuerdo",
                    "2 - Algo en desacuerdo",
                    "3 - Neutral",
                    "4 - Algo de acuerdo",
                    "5 - Totalmente de acuerdo",
                ]
                selected_option = st.radio(
                    "Elige tu respuesta",
                    options=options,
                    index=0,
                    key=f"radio_{i}",
                    horizontal=True,
                )
                if st.session_state.page_number < total_pages - 1:
                    submit_button = st.form_submit_button("Siguiente")
                else:
                    submit_button = st.form_submit_button("**Mostrar mi estilo DISC**")
            else:
                submit_button = st.form_submit_button("**Mostrar mi estilo DISC**")

        if submit_button:
            if selected_option == "Selecciona una opción":
                st.warning("Por favor, selecciona una respuesta para continuar.")
            else:
                # Map the selected option to a score
                score_mapping = {
                    "1 - Totalmente en desacuerdo": 1,
                    "2 - Algo en desacuerdo": 2,
                    "3 - Neutral": 3,
                    "4 - Algo de acuerdo": 4,
                    "5 - Totalmente de acuerdo": 5,
                }
                st.session_state.answers[i] = score_mapping[selected_option]
                if st.session_state.page_number < total_pages - 1:
                    st.session_state.page_number += 1
                    st.rerun()
                else:
                    # Set flags to show results and indicate submission
                    st.session_state.show_results = True
                    st.session_state.submitted = False  # Ensure this is reset
                    st.rerun()
    else:
        # After the user has completed the assessment or uploaded results
        if not st.session_state.submitted:
            # Calculate raw scores
            st.session_state.score = calculate_raw_scores(st.session_state.answers, st.session_state.questions)
            st.session_state.raw_score = st.session_state.score.copy()

            # Normalize the scores
            normalized_score = normalize_scores(st.session_state.score, st.session_state.questions)
            st.session_state.normalized_score = normalized_score
            st.session_state.submitted = True  # Set to True to avoid recalculation
        else:
            if 'normalized_score' in st.session_state:
                normalized_score = st.session_state.normalized_score
            else:
                normalized_score = normalize_scores(st.session_state.score, st.session_state.questions)
                st.session_state.normalized_score = normalized_score

        # Compute the resultant vector
        resultant_angle, resultant_magnitude = calculate_resultant_vector(normalized_score)
        
        # Create the updated plot
        fig = create_disc_plot(resultant_angle, resultant_magnitude)

        # Use Streamlit columns to control the figure width
        col1, col2, col3 = st.columns([1, 2, 1])

        with col2:  # Display the plot in the middle column
            st.pyplot(fig)

        # Personalized Style Descriptions
        st.markdown("## Tu Estilo DISC Personalizado")
        style_info = get_style_description(normalized_score, resultant_angle, disc_descriptions)
        
        st.markdown(f"### {style_info['title']}")
        st.markdown(style_info['description'])
        st.markdown(f"**Fortalezas:** {style_info['strengths']}")
        st.markdown(f"**Desafíos:** {style_info['challenges']}")

        # Get relative percentages
        relative_percentages = get_relative_percentages(normalized_score)
        
        st.markdown("## Tu Desglose de Estilo DISC")
        st.write("Porcentajes Relativos")
        cols = st.columns(4)
        for idx, (style, score_value) in enumerate(relative_percentages.items()):
            with cols[idx]:
                st.markdown(f"**{style}**")
                # Ensure score_value is within 0 to 100
                score_value = max(0, min(score_value, 100))
                # Adjust the progress bar value to be between 0.0 and 1.0
                st.progress(score_value / 100)
                # Display the score as a percentage
                st.text(f"{score_value:.2f}%")
        
        # Download options
        st.markdown("## Descarga tus Resultados")
        col1, col2 = st.columns(2)
        with col1:
            get_json_download_button(normalized_score)
        with col2:
            pdf_buffer = create_pdf_report(
                            normalized_score=normalized_score,
                            relative_percentages=relative_percentages,
                            fig=fig,
                            style_info=style_info
                        )
            get_pdf_download_button(pdf_buffer)

        # Explanation about DISC styles
        st.markdown("""---""")
        st.markdown(
            """
        ### Cómo entender todos los estilos DISC

        - **Dominancia (D)**: Tiendes a ser directo, orientado a los resultados y asertivo.
        - **Influencia (I)**: Sueles ser extrovertido, entusiasta y optimista.
        - **Estabilidad (S)**: Sueles ser paciente, solidario y estar orientado al equipo.
        - **Cumplimiento (C)**: Tiendes a ser analítico, preciso y detallista.

        Recuerda que todo el mundo tiene aspectos de los cuatro estilos, pero la mayoría de la gente tiende a gravitar hacia uno o dos estilos principales.
        Tu combinación única de estilos influye en tu forma de comunicarte, tomar decisiones e interactuar con los demás.
        """
        )

        if st.button("Reiniciar"):
            st.session_state.pop("page_number")
            st.session_state.pop("score")
            st.session_state.pop("answers")
            st.session_state.pop("show_results")
            st.session_state.pop("questions")
            st.rerun()


st.markdown(
    """
    ---
    <div style="text-align: center;">
        <strong><a href="https://github.com/dzyla/disc-personality-assessment">Código fuente</a></strong> | Desarrollado por <a href="https://dzyla.com">Dawid Zyla</a>
    </div>
    """,
    unsafe_allow_html=True,
)
