# Proyecto RAIN: Sistema de Diagnóstico de Ansiedad 🧠

El proyecto consiste en el desarrollo de un sistema de diagnóstico diseñado para ayudar a detectar la probabilidad de padecer ansiedad a partir de parámetros con incertidumbre. Se basa en la Inteligencia Artificial, utilizando una Red Bayesiana implementada con la biblioteca `pgmpy`.

El objetivo principal es traducir datos cualitativos e inciertos (como factores de riesgo y percepción de síntomas) en una métrica objetiva y cuantificable, sirviendo como herramienta de soporte a la decisión clínica.

## 🚀 Características Principales

*   **Manejo de Incertidumbre:** Cuantifica la influencia de factores de riesgo y síntomas utilizando Tablas de Probabilidad Condicional (CPDs).
*   **Motor de Inferencia Bayesiana:** Emplea *Variable Elimination* para realizar la propagación de probabilidades y calcular la creencia posterior en tiempo real.
*   **Interfaz Gráfica Intuitiva:** Desarrollada de forma nativa para guiar al usuario a través de un flujo secuencial (Evaluación General -> Síntomas -> Resultados).
*   **Generación de Reportes:** Permite exportar los resultados del diagnóstico (nivel de riesgo, factores influyentes y recomendaciones) a un documento PDF.

## 🧠 Arquitectura del Modelo

La topología de la Red Bayesiana (Grafo Acíclico Dirigido) se divide en dos niveles:

1.  **Factores de Riesgo (Nodos Padre):** Antecedentes familiares, Edad y Estrés laboral/académico.
2.  **Síntomas (Evidencia / Nodos Hijo):** Nerviosismo, Fatiga, Concentración, Irritabilidad, Tensión muscular y Trastornos del sueño.

El sistema opera a través de un patrón modular que desacopla la lógica de inferencia de la interfaz de usuario, garantizando la escalabilidad y mantenibilidad del software.

## 🛠️ Tecnologías Utilizadas

*   **Python:** Lenguaje de programación principal.
*   **pgmpy:** Definición de la estructura del modelo, gestión de tablas CPD y ejecución algorítmica de inferencia exacta.
*   **Tkinter:** Construcción de la interfaz gráfica nativa (`tkinter`, `ttk`, `messagebox`).
*   **FPDF:** Generación de reportes persistentes en PDF para los pacientes.

## ⚙️ Instalación y Ejecución

Para ejecutar este proyecto de forma local, asegúrate de tener Python instalado y sigue estos pasos:

1.  Clona este repositorio:
    ```bash
    git clone [https://github.com/tu-usuario/sistema-diagnostico-ansiedad.git](https://github.com/tu-usuario/sistema-diagnostico-ansiedad.git)
    ```
2.  Instala las dependencias necesarias:
    ```bash
    pip install pgmpy fpdf
    ```
3.  Ejecuta la aplicación principal:
    ```bash
    python sistema_diagnostico_ansiedad.py
    ```
    *(Opcional: Si quieres ejecutar las pruebas del normalizador de datos, puedes lanzar `python prueba_normalizacion_datos.py`)*.

## 📷 Capturas de Pantalla

* Pantalla de Bienvenida
  
<img width="591" height="577" alt="pantalla-bienvenida" src="https://github.com/user-attachments/assets/6606ca95-2412-4c5e-b984-11b9d242e3b0" />

* Pantalla de Evaluación de Factores

<img width="587" height="447" alt="pantalla-factores" src="https://github.com/user-attachments/assets/34460d63-c29e-473e-a2e8-c1ba7941c5ae" />

* Pantalla de Evaluación de Síntomas

<img width="595" height="572" alt="pantalla-sintomas" src="https://github.com/user-attachments/assets/0ba76eff-4bb6-4dfa-bea8-c79935ceab8d" />

* Pantalla de Resultados y Diagnóstico

<img width="592" height="572" alt="pantalla-resultados" src="https://github.com/user-attachments/assets/68a42e54-7cfb-4485-89a3-a0d0f577f4fc" />

---
*Desarrollado en el contexto del Grado en Inteligencia Artificia en la asignatura de Razonamiento con Incertidumbre*
