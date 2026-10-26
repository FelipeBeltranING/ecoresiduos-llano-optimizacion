# EcoResiduos del Llano — Optimización de la Red Logística de Residuos Agropecuarios

> Sistema de optimización para la recepción y el procesamiento de residuos agropecuarios en el departamento del Meta (Colombia). Usa **Programación Lineal (Problema de Transporte / Flujo de Costo Mínimo)** y **Algoritmos Genéticos**. Incluye interfaz interactiva, análisis de sensibilidad y reporte comparativo.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Licencia](https://img.shields.io/badge/Licencia-MIT-green)
![Estado](https://img.shields.io/badge/Estado-En%20desarrollo-yellow)

**Universidad de los Llanos** · Facultad de Ciencias Básicas e Ingeniería · Programa de Ingeniería de Sistemas
**Asignatura:** Optimización · **Periodo académico:** 2026-II · **Proyecto final de curso**

---

## Tabla de contenido

1. [Contexto y problemática](#1-contexto-y-problemática)
2. [Objetivos](#2-objetivos)
3. [Equipo y roles](#3-equipo-y-roles)
4. [Modelo matemático](#4-modelo-matemático)
5. [Diseño del Algoritmo Genético](#5-diseño-del-algoritmo-genético)
6. [Análisis de sensibilidad](#6-análisis-de-sensibilidad)
7. [Reporte comparativo](#7-reporte-comparativo)
8. [Arquitectura y estructura del repositorio](#8-arquitectura-y-estructura-del-repositorio)
9. [Instalación y ejecución](#9-instalación-y-ejecución)
10. [Formato de los datos](#10-formato-de-los-datos)
11. [Flujo de trabajo del equipo](#11-flujo-de-trabajo-del-equipo)
12. [Entregables y cronograma](#12-entregables-y-cronograma)
13. [Tecnologías](#13-tecnologías)
14. [Licencia](#14-licencia)

---

## 1. Contexto y problemática

**EcoResiduos del Llano S.A.S.** valoriza y transforma residuos agropecuarios (biomasa y subproductos de palma, arroz, ganadería y plantaciones forestales) en abonos orgánicos, biocombustibles y suplementos para nutrición animal.

La red está compuesta por:

- **10 empresas agropecuarias aliadas** (fuentes), que generan un volumen semanal constante de residuos.
- **4 plantas de recepción y transformación** (destinos), ubicadas en **Villavicencio, Restrepo, Granada y Puerto Gaitán**.

La asignación empírica de rutas y centros de acopio genera sobrecostos operativos. La Gerencia requiere un sistema que **minimice el costo total de transporte** y determine la **distribución óptima de los flujos** de residuos. El sistema debe permitir:

- Agregar nuevas empresas agropecuarias y nuevas plantas.
- Modificar los coeficientes del modelo (precio por tonelada, costo de transporte, etc.).
- Visualizar resultados y realizar análisis de sensibilidad ante variaciones en oferta, demanda y costos unitarios.

## 2. Objetivos

### Objetivo general

Diseñar y desarrollar una solución computacional basada en modelos de optimización de redes, métodos de transporte y algoritmos genéticos para minimizar el costo logístico de la red de recepción de residuos agropecuarios de la empresa.

### Objetivos específicos

- Estructurar y parametrizar el problema de transporte y flujo en redes con la oferta de las 10 empresas y la capacidad de procesamiento de las 4 plantas.
- Implementar el modelo matemático exacto en Python para hallar el óptimo global.
- Diseñar e implementar un Algoritmo Genético (AG) adaptado a la asignación de flujos de la red para obtener soluciones cuasi-óptimas.
- Realizar el análisis de sensibilidad ante variaciones en costos unitarios, oferta y demanda.
- Comparar el método exacto y el AG en calidad de la función objetivo, tiempo de cómputo, escalabilidad y respuesta ante escenarios de sensibilidad.

## 3. Equipo y roles

**Grupo: Orion**

| Rol | Integrante | Código | Responsabilidades | Módulos a cargo |
|---|---|---|---|---|
| Líder de Proyecto / Analista de Negocio | **Felipe Beltrán** | 160005207 | Coordinación general, seguimiento del cronograma, informe técnico IEEE y validación de las restricciones del modelo de negocio | `docs/`, `data/` |
| Ingeniero de Modelado y Optimización | **Julián Báez** | 160005203 | Formulación matemática de la red (grafo, variables, función objetivo, restricciones) e implementación del solucionador exacto | `src/modelo/`, `src/exacto/` |
| Desarrollador de Metaheurísticas | **Martín Pineda** | 160005227 | Diseño, codificación y ajuste de parámetros del AG (cromosoma, fitness, selección, cruce y mutación) | `src/genetico/` |
| Desarrollador de Software e Interfaz | **Juan Navarro** | 160005245 | Arquitectura de software, interfaz de parametrización dinámica, visualización del análisis de sensibilidad y reportes comparativos | `src/interfaz/`, `src/sensibilidad/`, `src/comparacion/` |

## 4. Modelo matemático

### 4.1 Red como grafo dirigido

La red se define como un grafo dirigido $G = (V, E)$:

- $V = O \cup P$, donde $O = \{o_1, \dots, o_m\}$ son las empresas agropecuarias (fuentes) y $P = \{p_1, \dots, p_n\}$ son las plantas (destinos). Si se incluyen centros de acopio intermedios, se añade el conjunto $T$ de nodos de paso: $V = O \cup T \cup P$.
- $E$ contiene los arcos $(i, j)$ que representan las rutas viales del Meta, cada uno con su distancia estimada $d_{ij}$ (km) y su costo asociado.

En el caso base, $m = 10$ y $n = 4$.

### 4.2 Conjuntos

| Símbolo | Descripción |
|---|---|
| $I = \{1, \dots, m\}$ | Empresas agropecuarias (fuentes) |
| $J = \{1, \dots, n\}$ | Plantas de procesamiento (destinos) |

### 4.3 Parámetros

| Símbolo | Descripción | Unidad |
|---|---|---|
| $a_i$ | Oferta semanal de residuos de la empresa $i$ | t/semana |
| $b_j$ | Capacidad (demanda) semanal de procesamiento de la planta $j$ | t/semana |
| $d_{ij}$ | Distancia vial entre la empresa $i$ y la planta $j$ | km |
| $k$ | Costo de transporte por tonelada-kilómetro | COP/(t·km) |
| $o_j$ | Costo de operación (procesamiento) por tonelada en la planta $j$ | COP/t |
| $c_{ij} = k \cdot d_{ij} + o_j$ | Costo unitario total de enviar una tonelada de $i$ a $j$ | COP/t |

### 4.4 Variables de decisión

$$x_{ij} \geq 0 \quad \text{: toneladas semanales enviadas de la empresa } i \text{ a la planta } j$$

### 4.5 Función objetivo

$$\min Z = \sum_{i \in I} \sum_{j \in J} c_{ij} \, x_{ij}$$

### 4.6 Restricciones

**Oferta** (se recoge todo el residuo generado por cada empresa):

$$\sum_{j \in J} x_{ij} = a_i \quad \forall i \in I$$

**Demanda / capacidad** (ninguna planta excede su capacidad):

$$\sum_{i \in I} x_{ij} \leq b_j \quad \forall j \in J$$

**No negatividad:**

$$x_{ij} \geq 0 \quad \forall i \in I, \; j \in J$$

### 4.7 Balance de la red

- Si $\sum a_i \leq \sum b_j$, el modelo es factible tal como está planteado.
- Si $\sum a_i > \sum b_j$, el sistema agrega automáticamente una **planta ficticia** con capacidad $\sum a_i - \sum b_j$ y un costo de penalización alto. El flujo asignado a ella representa el residuo que la red no puede procesar (cuello de botella).

## 5. Diseño del Algoritmo Genético

| Componente | Diseño |
|---|---|
| **Cromosoma** | Matriz de flujos $x_{ij}$ de tamaño $m \times n$, aplanada en un vector de longitud $m \cdot n$ (genes reales $\geq 0$) |
| **Población inicial** | Soluciones aleatorias que reparten la oferta $a_i$ de cada empresa entre las plantas, más soluciones construidas con heurísticas (esquina noroeste, costo mínimo) |
| **Función de aptitud** | $f = \dfrac{1}{Z + \lambda \cdot \text{Pen}}$, donde $\text{Pen} = \sum_i \left\| \sum_j x_{ij} - a_i \right\| + \sum_j \max\left(0, \sum_i x_{ij} - b_j\right)$ |
| **Selección** | Torneo o ruleta (configurable) |
| **Cruce** | Un punto o dos puntos sobre el vector aplanado (configurable) |
| **Mutación** | Transferencia de una cantidad de flujo de una planta a otra dentro de la misma empresa, conservando su oferta |
| **Reparación** | Opcional: reescalado de cada fila para cumplir la oferta tras el cruce |
| **Elitismo** | Se conservan los mejores individuos de cada generación |
| **Parámetros ajustables** | Tamaño de población, número de generaciones, tasa de cruce, tasa de mutación, $\lambda$ y tipo de selección/cruce (desde la interfaz) |

## 6. Análisis de sensibilidad

Escenarios soportados desde la interfaz:

- **Costo de combustible/transporte:** variación porcentual de $k$ o de costos $c_{ij}$ específicos.
- **Oferta de residuos:** variación porcentual de $a_i$ (global o por empresa).
- **Cuellos de botella:** reducción de la capacidad $b_j$ de una o varias plantas.

Resultados que se reportan:

- **Precios sombra (duales)** de las restricciones de oferta y capacidad.
- **Costos reducidos** de las variables $x_{ij}$ no básicas.
- **Rangos de variación permitidos** de costos y capacidades sin alterar la base óptima, calculados mediante re-optimización paramétrica.
- Comportamiento comparado del modelo exacto y del AG en cada escenario.

## 7. Reporte comparativo

| Métrica | Modelo exacto | Algoritmo Genético |
|---|---|---|
| Costo total (COP) | — | — |
| Tiempo de ejecución (s) | — | — |
| Gap frente al óptimo (%) | 0 | — |
| Factibilidad (violaciones) | 0 | — |

El gap se calcula como:

$$\text{Gap}(\%) = \frac{Z_{AG} - Z^{*}}{Z^{*}} \times 100$$

*La tabla se llena automáticamente al ejecutar el módulo de comparación. También se evalúa la escalabilidad aumentando el número de empresas y plantas.*

## 8. Arquitectura y estructura del repositorio

```
ecoresiduos-llano-optimizacion/
├── src/
│   ├── modelo/            # Definición de la red, grafo y carga/validación de datos
│   ├── exacto/            # Solucionador de programación lineal (PuLP + CBC)
│   ├── genetico/          # Algoritmo Genético
│   ├── sensibilidad/      # Precios sombra, costos reducidos, rangos y escenarios
│   ├── comparacion/       # Reporte exacto vs. AG
│   └── interfaz/          # Aplicación Streamlit
├── data/                  # Datos de prueba regionales (CSV)
├── tests/                 # Pruebas unitarias (pytest)
├── docs/                  # Informe IEEE, diagramas y figuras
├── requirements.txt
├── LICENSE
└── README.md
```

Flujo general:

```
data/ (CSV) ──► modelo ──┬──► exacto ──────┐
                         │                 ├──► comparacion ──► interfaz
                         └──► genetico ────┘         ▲
                                   sensibilidad ─────┘
```

## 9. Instalación y ejecución

**Requisitos:** Python 3.10 o superior y Git.

```bash
# 1. Clonar el repositorio
git clone https://github.com/FelipeBeltranING/ecoresiduos-llano-optimizacion.git
cd ecoresiduos-llano-optimizacion

# 2. Crear y activar el entorno virtual
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux / macOS
source .venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Ejecutar la interfaz
streamlit run src/interfaz/app.py

# 5. Ejecutar las pruebas
pytest
```

## 10. Formato de los datos

Los datos de prueba se ubican en `data/` y pueden editarse desde la interfaz o directamente en los archivos:

| Archivo | Columnas | Descripción |
|---|---|---|
| `empresas.csv` | `id, nombre, municipio, oferta_t` | Empresas agropecuarias y su oferta semanal |
| `plantas.csv` | `id, municipio, capacidad_t, costo_operacion` | Plantas y su capacidad semanal |
| `distancias.csv` | `empresa_id, planta_id, distancia_km` | Distancias viales estimadas entre cada empresa y cada planta |
| `parametros.csv` | `parametro, valor` | Coeficientes globales (costo por t·km, precio por tonelada, $\lambda$, etc.) |

Para agregar una empresa o una planta basta con añadir una fila a `empresas.csv` o `plantas.csv` y sus distancias en `distancias.csv`; no se requieren cambios en el código.

## 11. Flujo de trabajo del equipo

- `main`: versión estable, solo se actualiza mediante Pull Request revisado.
- `develop`: integración de los módulos.
- Ramas por funcionalidad: `feature/modelo-exacto`, `feature/genetico`, `feature/interfaz`, `feature/sensibilidad`, `docs/informe`.
- Mensajes de commit descriptivos en español, por ejemplo: `feat(genetico): agrega cruce de dos puntos`.

## 12. Entregables y cronograma

| Fase | Descripción | Responsable principal | Estado |
|---|---|---|---|
| Fase 1 | Modelado de la red logística (grafo y modelo de PL) | Julián Báez | ⬜ |
| Fase 2 | Implementación y validación de la solución exacta | Julián Báez | ⬜ |
| Fase 3 | Algoritmo Genético | Martín Pineda | ⬜ |
| Fase 4 | Interfaz, análisis de sensibilidad y reporte comparativo | Juan David Navarro | ⬜ |
| — | Informe técnico en formato IEEE | Felipe Beltrán | ⬜ |
| — | Sustentación práctica con escenarios en vivo | Todo el equipo | ⬜ |

**Entregables:**

- [ ] Informe técnico (formato IEEE) en `docs/`
- [ ] Código fuente documentado y modular
- [ ] Sustentación práctica con casos de prueba y análisis de sensibilidad en vivo

## 13. Tecnologías

Python · PuLP (CBC) · NumPy · Pandas · NetworkX · Plotly · Streamlit · Pytest

## 14. Licencia

Distribuido bajo la licencia MIT. Ver [`LICENSE`](LICENSE).
