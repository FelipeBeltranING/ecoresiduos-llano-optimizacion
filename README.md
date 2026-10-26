# EcoResiduos del Llano — Optimización de la Red Logística de Residuos Agropecuarios

> Aplicación web para optimizar la recepción y el procesamiento de residuos agropecuarios en el departamento del Meta (Colombia). Usa **Programación Lineal (Problema de Transporte / Flujo de Costo Mínimo)** y **Algoritmos Genéticos**. Incluye parametrización dinámica de la red, análisis de sensibilidad y reporte comparativo.

![Python](https://img.shields.io/badge/Python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688)
![React](https://img.shields.io/badge/React-18-61DAFB)
![PostgreSQL](https://img.shields.io/badge/Supabase-PostgreSQL%2015-3ECF8E)
![Licencia](https://img.shields.io/badge/Licencia-MIT-green)
![Estado](https://img.shields.io/badge/Estado-En%20desarrollo-yellow)

**Universidad de los Llanos** · Facultad de Ciencias Básicas e Ingeniería · Programa de Ingeniería de Sistemas
**Asignatura:** Optimización · **Periodo académico:** 2026-II · **Proyecto final de curso** · **Grupo Orion**

---

## Tabla de contenido

1. [Contexto y problemática](#1-contexto-y-problemática)
2. [Objetivos](#2-objetivos)
3. [Equipo y roles](#3-equipo-y-roles)
4. [Funcionalidades](#4-funcionalidades)
5. [Modelo matemático](#5-modelo-matemático)
6. [Diseño del Algoritmo Genético](#6-diseño-del-algoritmo-genético)
7. [Análisis de sensibilidad](#7-análisis-de-sensibilidad)
8. [Reporte comparativo](#8-reporte-comparativo)
9. [Stack tecnológico](#9-stack-tecnológico)
10. [Arquitectura y estructura del repositorio](#10-arquitectura-y-estructura-del-repositorio)
11. [Instalación y ejecución](#11-instalación-y-ejecución)
12. [Base de datos y migraciones](#12-base-de-datos-y-migraciones)
13. [API REST](#13-api-rest)
14. [Datos de prueba](#14-datos-de-prueba)
15. [Pruebas](#15-pruebas)
16. [Flujo de trabajo del equipo](#16-flujo-de-trabajo-del-equipo)
17. [Planificación y entregables](#17-planificación-y-entregables)
18. [Licencia](#18-licencia)

---

## 1. Contexto y problemática

**EcoResiduos del Llano S.A.S.** valoriza y transforma residuos agropecuarios (biomasa y subproductos de palma, arroz, ganadería y plantaciones forestales) en abonos orgánicos, biocombustibles y suplementos para nutrición animal.

La red está compuesta por:

- **10 empresas agropecuarias aliadas** (fuentes), que generan un volumen semanal constante de residuos.
- **4 plantas de recepción y transformación** (destinos), ubicadas en **Villavicencio, Restrepo, Granada y Puerto Gaitán**.

La asignación empírica de rutas y centros de acopio genera sobrecostos operativos. La Gerencia requiere un sistema que **minimice el costo total de transporte y operación** y determine la **distribución óptima de los flujos** de residuos. El sistema debe permitir:

- Agregar nuevas empresas agropecuarias, plantas y centros de acopio (red **totalmente escalable**).
- Modificar los coeficientes del modelo (precio por tonelada, costo de transporte, etc.).
- Visualizar resultados y realizar análisis de sensibilidad ante variaciones en oferta, demanda y costos unitarios.

## 2. Objetivos

### Objetivo general

Diseñar y desarrollar una solución computacional web basada en modelos de optimización de redes, métodos de transporte y algoritmos genéticos para minimizar el costo logístico de la red de recepción de residuos agropecuarios de la empresa.

### Objetivos específicos

- Estructurar y parametrizar el problema de transporte y flujo en redes con la oferta de las empresas y la capacidad de procesamiento de las plantas, sin límite fijo de nodos.
- Implementar el modelo matemático exacto en Python (PuLP + CBC) para hallar el óptimo global.
- Diseñar e implementar un Algoritmo Genético (AG) adaptado a la asignación de flujos de la red para obtener soluciones cuasi-óptimas.
- Realizar el análisis de sensibilidad ante variaciones en costos unitarios, oferta y demanda.
- Comparar el método exacto y el AG en calidad de la función objetivo, tiempo de cómputo, escalabilidad y respuesta ante escenarios de sensibilidad.

## 3. Equipo y roles

**Grupo: Orion**

| Rol | Integrante | Código | Rol Scrum | Responsabilidades | Módulos a cargo |
|---|---|---|---|---|---|
| Líder de Proyecto / Analista de Negocio | **David Felipe Beltrán Tabares** | 160005207 | Product Owner y Scrum Master | Coordinación, cronograma, backlog, validación de las restricciones del negocio, QA, reportes e informe IEEE | `docs/`, `backend/app/reportes/`, `backend/tests/` |
| Ingeniero de Modelado y Optimización | **Julián David Báez Parra** | 160005203 | Equipo de desarrollo | Formulación matemática, modelo de datos y migraciones, modelo exacto, sensibilidad y centros de acopio | `backend/app/optimizacion/exacto/`, `backend/app/optimizacion/sensibilidad/`, `backend/app/db/`, `backend/alembic/` |
| Desarrollador de Metaheurísticas | **Martín Pineda Jaramillo** | 160005227 | Equipo de desarrollo | Diseño, codificación y ajuste del AG, convergencia, comparación y escalabilidad | `backend/app/optimizacion/genetico/`, `backend/app/services/comparacion*` |
| Desarrollador de Software e Interfaz | **Juan David Navarro Bermúdez** | 160005245 | Equipo de desarrollo | Arquitectura, frontend responsive, visualización, CI/CD y despliegue | `frontend/`, `.github/`, `docker-compose.yml` |

## 4. Funcionalidades

Organizadas en 5 épicas y 17 historias de usuario (detalle en `docs/Documento_Base_Proyecto_Orion.docx`).

| Épica | Historias de usuario |
|---|---|
| **E1 Gestión dinámica de la red** | HU-01 Empresas · HU-02 Plantas · HU-03 Rutas y matriz de costos · HU-04 Parámetros globales · HU-05 Importar/exportar y caso base · HU-17 Centros de acopio |
| **E2 Optimización exacta** | HU-06 Validar la red · HU-07 Resolver el modelo exacto · HU-08 Visualizar red y flujos |
| **E3 Algoritmo Genético** | HU-09 Configurar y ejecutar el AG · HU-10 Convergencia |
| **E4 Análisis de sensibilidad** | HU-11 Escenarios · HU-12 Precios sombra, costos reducidos y rangos |
| **E5 Comparación y reportes** | HU-13 Reporte comparativo · HU-14 Escalabilidad · HU-15 Historial · HU-16 Exportar PDF/Excel |

- Aplicación web **responsive** (móvil, tableta y escritorio).
- **Sin inicio de sesión**: acceso directo a todas las funciones.
- **Escalable**: ningún tamaño de red está fijo en el código; agregar nodos es solo insertar registros.

## 5. Modelo matemático

### 5.1 Red como grafo dirigido

La red se define como un grafo dirigido $G = (V, E)$ con $V = O \cup T \cup P$:

- $O$: empresas agropecuarias (fuentes); $T$: centros de acopio (nodos de paso, opcional); $P$: plantas (destinos).
- $E$: arcos $(i, j)$ que representan las rutas viales del Meta, cada uno con su distancia estimada $d_{ij}$ (km) y su costo por tonelada-kilómetro.

En el caso base, $|O| = 10$, $|T| = 0$, $|P| = 4$ y $|E| = 40$.

### 5.2 Parámetros

| Símbolo | Descripción | Unidad |
|---|---|---|
| $a_i$ | Oferta semanal de residuos de la empresa $i$ | t/semana |
| $b_j$ | Capacidad semanal de procesamiento de la planta $j$ | t/semana |
| $d_{ij}$ | Distancia vial entre $i$ y $j$ | km |
| $k$ | Costo de transporte por tonelada-kilómetro | COP/(t·km) |
| $o_j$ | Costo de operación por tonelada en la planta $j$ | COP/t |
| $c_{ij} = k \cdot d_{ij} + o_j$ | Costo unitario total de enviar una tonelada de $i$ a $j$ | COP/t |

### 5.3 Modelo de transporte

**Variables:** $x_{ij} \geq 0$, toneladas semanales enviadas de la empresa $i$ a la planta $j$.

$$\min Z = \sum_{i \in I} \sum_{j \in J} c_{ij} \, x_{ij}$$

Sujeto a:

$$\sum_{j \in J} x_{ij} = a_i \quad \forall i \in I \qquad \text{(oferta)}$$

$$\sum_{i \in I} x_{ij} \leq b_j \quad \forall j \in J \qquad \text{(capacidad)}$$

$$x_{ij} \geq 0 \quad \forall i, j$$

**Balance:** si $\sum a_i > \sum b_j$, el sistema agrega automáticamente una **planta ficticia** con capacidad $\sum a_i - \sum b_j$ y un costo de penalización. El flujo asignado a ella representa el residuo que la red no puede procesar.

### 5.4 Extensión a flujo de costo mínimo (con centros de acopio)

Cuando hay centros de acopio activos, se agrega la conservación de flujo en cada nodo de paso $t \in T$:

$$\sum_{e \in \delta^-(t)} x_e - \sum_{e \in \delta^+(t)} x_e = 0, \qquad \sum_{e \in \delta^-(t)} x_e \leq cap_t$$

## 6. Diseño del Algoritmo Genético

| Componente | Diseño |
|---|---|
| **Cromosoma** | Vector real de longitud $m \cdot n$ (o $\|E\|$ con acopios) que representa la matriz de flujos $x_{ij}$ |
| **Población inicial** | 10 % construida con la heurística de costo mínimo y 90 % aleatoria, que reparte la oferta $a_i$ de cada empresa |
| **Función de aptitud** | $f = \dfrac{1}{Z + \lambda \cdot \text{Pen}}$, con $\text{Pen} = \sum_i \left\| \sum_j x_{ij} - a_i \right\| + \sum_j \max\left(0, \sum_i x_{ij} - b_j\right)$ |
| **Selección** | Torneo ($k = 3$) o ruleta (configurable) |
| **Cruce** | Un punto o dos puntos, con cortes en los límites de fila (por empresa) |
| **Mutación** | Transferencia de flujo de una planta a otra dentro de la misma empresa |
| **Reparación** | Reescalado de cada fila para cumplir la oferta |
| **Elitismo** | Los 2 mejores individuos pasan intactos a la siguiente generación |
| **Parada** | Número de generaciones o 50 generaciones sin mejora |
| **Parámetros ajustables** | Población, generaciones, tasas de cruce y mutación, $\lambda$, tipo de selección y cruce, elitismo y semilla (desde la interfaz) |

## 7. Análisis de sensibilidad

Escenarios soportados desde la interfaz:

- **Costo de combustible/transporte:** variación porcentual de $k$ o de costos $c_{ij}$ específicos.
- **Oferta de residuos:** variación porcentual de $a_i$ (global o por empresa).
- **Cuellos de botella:** reducción de la capacidad $b_j$ de una o varias plantas.

Cada escenario se ejecuta con **ambos métodos** y reporta:

- **Precios sombra (duales)** de las restricciones de oferta y capacidad.
- **Costos reducidos** de las rutas no utilizadas.
- **Rangos de estabilidad** de costos y capacidades sin alterar la base óptima, calculados por re-optimización paramétrica.

## 8. Reporte comparativo

| Métrica | Modelo exacto | Algoritmo Genético |
|---|---|---|
| Costo total (COP/semana) | — | — (mejor, promedio y desviación de N corridas) |
| Tiempo de ejecución (s) | — | — |
| Gap frente al óptimo (%) | 0 | — |
| Violaciones de restricciones | 0 | — |
| Comportamiento por escenario | — | — |

$$\text{Gap}(\%) = \frac{Z_{AG} - Z^{*}}{Z^{*}} \times 100$$

*El reporte se genera desde la aplicación y se puede exportar en PDF o Excel. La escalabilidad se evalúa con instancias sintéticas de 10×4 a 100×20 nodos.*

## 9. Stack tecnológico

| Capa | Tecnologías |
|---|---|
| **Frontend** | React 18 + TypeScript, Vite, Tailwind CSS, React Router, TanStack Query + Axios, React Hook Form + Zod, React Leaflet (mapa), Recharts (gráficas) |
| **Backend** | Python 3.12, FastAPI + Uvicorn, Pydantic v2 |
| **Optimización** | PuLP + CBC (modelo exacto, duales y holguras), NumPy (AG), NetworkX (validación del grafo) |
| **Datos** | Supabase PostgreSQL 15, SQLAlchemy 2.0 (ORM), Alembic (migraciones), psycopg 3 |
| **Reportes** | Pandas + openpyxl (Excel), ReportLab + Matplotlib (PDF) |
| **Calidad** | pytest, pytest-cov, httpx, Vitest + Testing Library, Playwright, Ruff, ESLint, Prettier |
| **DevOps** | Docker + Docker Compose, GitHub Actions, Vercel (frontend), Render (backend) |

> **Nota:** SQLAlchemy y Alembic son los equivalentes en Python de Hibernate y Flyway (Java).

## 10. Arquitectura y estructura del repositorio

```
┌──────────────────────────┐   HTTPS/JSON   ┌───────────────────────────────────────────┐        ┌──────────────────────┐
│ Frontend (React + Vite)  │ ─────────────► │ Backend (FastAPI)                         │ ─────► │ Supabase PostgreSQL  │
│ SPA responsive · Vercel  │                │ Routers → Servicios → Repositorios (ORM)  │        │ (migraciones Alembic)│
└──────────────────────────┘                │ Motores: Exacto · Genético · Sensibilidad │        └──────────────────────┘
                                            └───────────────────────────────────────────┘
```

```
ecoresiduos-llano-optimizacion/
├── backend/
│   ├── app/
│   │   ├── api/v1/routers/      # nodos, rutas, parametros, datos, red, optimizacion,
│   │   │                        # ejecuciones, escenarios, comparaciones, escalabilidad, reportes
│   │   ├── core/                # configuración, errores, logging
│   │   ├── db/                  # engine, sesión y modelos ORM (SQLAlchemy)
│   │   ├── schemas/             # esquemas Pydantic (entrada / salida)
│   │   ├── repositories/        # acceso a datos
│   │   ├── services/            # lógica de negocio
│   │   ├── optimizacion/
│   │   │   ├── red.py           # RedLogistica, RedBuilder, ValidadorRed
│   │   │   ├── exacto/          # ModeloTransporte, ModeloFlujoCostoMinimo, SolverExacto
│   │   │   ├── genetico/        # AlgoritmoGenetico, operadores, reparador
│   │   │   └── sensibilidad/    # AnalizadorSensibilidad
│   │   ├── reportes/            # generación de PDF y Excel
│   │   └── main.py
│   ├── alembic/                 # migraciones V1, V2, V3…
│   ├── tests/                   # unit/, integration/, data/
│   ├── Dockerfile
│   ├── pyproject.toml
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── pages/               # Panel, Red, Rutas, Exacto, AG, Sensibilidad, Comparativo, Historial
│   │   ├── components/          # MapaFlujos, MatrizGrid, KPI, gráficas, formularios
│   │   ├── api/                 # cliente Axios y hooks de TanStack Query
│   │   └── lib/                 # utilidades y formato de cifras
│   ├── tests/
│   ├── package.json
│   └── .env.example
├── docs/                        # documento base, informe IEEE, diagramas (Mermaid)
├── docker-compose.yml
├── .github/workflows/ci.yml
├── LICENSE
└── README.md
```

## 11. Instalación y ejecución

**Requisitos:** Git, Python 3.12, Node.js 20 y Docker (opcional, recomendado).

### Opción A: Docker Compose (todo en local)

```bash
git clone https://github.com/FelipeBeltranING/ecoresiduos-llano-optimizacion.git
cd ecoresiduos-llano-optimizacion
docker compose up --build
```

- API: http://localhost:8000 · Documentación Swagger: http://localhost:8000/docs
- Frontend: http://localhost:5173

### Opción B: ejecución manual

**Backend**

```bash
cd backend
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux / macOS
source .venv/bin/activate

pip install -e ".[dev]"
cp .env.example .env            # completar DATABASE_URL (Supabase o PostgreSQL local)
alembic upgrade head            # crear las tablas
uvicorn app.main:app --reload   # http://localhost:8000
```

**Frontend**

```bash
cd frontend
npm install
cp .env.example .env            # VITE_API_URL=http://localhost:8000/api/v1
npm run dev                     # http://localhost:5173
```

**Cargar los datos de prueba:** desde la aplicación, en *Red logística → Importar / exportar → Cargar caso base*, o con:

```bash
curl -X POST http://localhost:8000/api/v1/datos/caso-base
```

### Variables de entorno

| Variable | Dónde | Ejemplo |
|---|---|---|
| `DATABASE_URL` | backend | `postgresql+psycopg://postgres.<proyecto>:<clave>@aws-0-us-east-1.pooler.supabase.com:5432/postgres?sslmode=require` |
| `CORS_ORIGINS` | backend | `http://localhost:5173,https://ecoresiduos-orion.vercel.app` |
| `VITE_API_URL` | frontend | `http://localhost:8000/api/v1` |

> Las credenciales de Supabase solo van en el backend. El archivo `.env` **no** se sube al repositorio.

## 12. Base de datos y migraciones

Tablas principales:

| Tabla | Descripción |
|---|---|
| `nodo` | Empresas, centros de acopio y plantas (campo `tipo`: FUENTE, ACOPIO, PLANTA) |
| `ruta` | Arcos del grafo: origen, destino, distancia, costo por t·km y estado |
| `parametro_global` | Coeficientes del negocio (costo por t·km, tarifa por tonelada, penalización, λ) |
| `escenario`, `ajuste_escenario` | Escenarios de sensibilidad y sus variaciones porcentuales |
| `ejecucion` | Cada corrida (exacta o AG) con costo, tiempo, parámetros y snapshot de la red |
| `flujo_resultado` | Flujos $x_{ij} > 0$ de cada ejecución |
| `sensibilidad_resultado` | Precios sombra, costos reducidos, holguras y rangos |
| `convergencia_ag` | Mejor costo y costo promedio por generación |
| `comparacion`, `benchmark` | Comparaciones exacto vs. AG y pruebas de escalabilidad |

Comandos de Alembic:

```bash
alembic revision --autogenerate -m "V2_ejecuciones"   # crear una migración desde los modelos
alembic upgrade head                                 # aplicar las migraciones pendientes
alembic downgrade -1                                 # revertir la última migración
```

## 13. API REST

Prefijo `/api/v1`. Documentación interactiva en `/docs`.

| Método | Ruta | Descripción |
|---|---|---|
| `GET` `POST` | `/nodos` | Listar y crear empresas, plantas y acopios (`?tipo=FUENTE\|PLANTA\|ACOPIO`) |
| `PUT` `DELETE` | `/nodos/{id}` | Actualizar o desactivar un nodo |
| `GET` `PUT` | `/rutas/matriz` · `/rutas/lote` | Consultar y editar la matriz de distancias y costos |
| `GET` `PUT` | `/parametros` | Parámetros globales |
| `POST` `GET` | `/datos/importar` · `/datos/exportar` · `/datos/caso-base` | Importación, exportación y caso base |
| `GET` | `/red/validacion` | Validar el balance y la consistencia de la red |
| `POST` | `/optimizacion/exacto` · `/optimizacion/genetico` | Ejecutar el modelo exacto o el AG |
| `GET` | `/ejecuciones` · `/ejecuciones/{id}` | Historial y detalle |
| `GET` | `/ejecuciones/{id}/convergencia` · `/ejecuciones/{id}/sensibilidad` | Convergencia del AG y sensibilidad |
| `POST` | `/escenarios` · `/escenarios/{id}/ejecutar` | Crear y ejecutar escenarios |
| `POST` `GET` | `/comparaciones` · `/escalabilidad` | Reporte comparativo y benchmark |
| `GET` | `/reportes/{id}.pdf` · `/reportes/{id}.xlsx` | Descargar reportes |

## 14. Datos de prueba

El caso base del Meta (10 empresas, 4 plantas y 40 rutas) se carga con un clic o por importación de Excel/CSV. Las empresas son ficticias y las distancias son estimaciones viales para fines académicos.

| Archivo / hoja | Columnas |
|---|---|
| `empresas` | `codigo, nombre, municipio, tipo_residuo, oferta_t, latitud, longitud` |
| `plantas` | `codigo, municipio, capacidad_t, costo_operacion_t, latitud, longitud` |
| `distancias` | `origen_codigo, destino_codigo, distancia_km, habilitada` |
| `parametros` | `clave, valor` |

**Valor de referencia del caso base** (oferta 890 t, capacidad 950 t, $k$ = 350 COP/t·km): **Z\* = $64.691.000 COP por semana**. Villavicencio y Restrepo quedan saturadas.

## 15. Pruebas

```bash
# Backend: unitarias e integración con cobertura
cd backend && pytest --cov=app

# Frontend: componentes
cd frontend && npm run test

# End-to-end
cd frontend && npx playwright test
```

Metas: cobertura ≥ 80 % en servicios y motores de optimización del backend, y ≥ 60 % en el frontend. Los resultados del modelo exacto se validan contra valores de referencia calculados de forma independiente.

## 16. Flujo de trabajo del equipo

- `main`: versión estable y desplegada; solo se actualiza mediante Pull Request revisado y con CI en verde.
- `develop`: integración de los módulos durante el sprint.
- Ramas por historia de usuario: `feature/HU-07-modelo-exacto`, `feature/HU-09-algoritmo-genetico`, etc.
- Correcciones: `fix/descripcion`. Cierre: `release/v1.0.0`.
- Commits con [Conventional Commits](https://www.conventionalcommits.org/es/) en español, por ejemplo: `feat(genetico): agrega cruce de dos puntos`.
- Cada PR enlaza su HU o issue y requiere al menos una revisión.

## 17. Planificación y entregables

Metodología **Scrum** con 2 sprints. Tablero en GitHub Projects.

| Sprint | Fechas | Objetivo |
|---|---|---|
| **Sprint 1** | 26 oct – 3 nov 2026 | Red 100 % parametrizable en la web, modelo exacto, visualización y motor del AG (HU-01 a HU-09) |
| **Sprint 2** | 4 – 12 nov 2026 | Sensibilidad, convergencia, comparación, escalabilidad, historial, reportes, acopios, despliegue e informe (HU-10 a HU-17) |

| Hito | Fecha |
|---|---|
| Incremento 1 (`v0.1.0`) | 3 nov 2026 |
| Congelamiento de código | 10 nov 2026 |
| Entrega final y sustentación (`v1.0.0`) | 12 nov 2026 |

**Entregables:**

- [ ] Informe técnico (formato IEEE) en `docs/`
- [ ] Código fuente documentado y modular (módulos exacto, genético, interfaz y sensibilidad)
- [ ] Sustentación práctica con casos de prueba y análisis de sensibilidad en vivo

## 18. Licencia

Distribuido bajo la licencia MIT. Ver [`LICENSE`](LICENSE).
