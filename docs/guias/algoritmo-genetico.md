# Guía: conectar el Algoritmo Genético (HU-09)

> **Estado (10 nov 2026): conectado.** El adaptador `app/optimizacion/genetico/adaptador.py` lleva la `RedLogistica` al `MotorAG`; el AG admite cruce de uno o dos puntos y selección por torneo o ruleta. Las pruebas de `tests/unit/test_aceptacion_genetico.py` están activas y pasan.

Esta guía explica qué falta para que `POST /api/v1/optimizacion/genetico` deje de responder
501. La API ya hace todo lo demás:

- valida los parámetros: una tasa fuera de [0, 1] o una población menor que 10 dan 422;
- arma la red desde la base y agrega la planta ficticia si hace falta;
- guarda la ejecución, los flujos, los parámetros y la convergencia, y los devuelve en
  `GET /api/v1/ejecuciones/{id}`.

## 1. Qué ya existe en `genetico/algoritmo.py` (después del PR #37)

| Clase | Qué hace |
|---|---|
| `Individuo` | Cromosoma como matriz `m × n` de flujos, con `fitness`, `costo_total` y `violaciones` |
| `InicializadorAG` | Población inicial: 10 % con la heurística de costo mínimo y 90 % aleatoria (Dirichlet por fila) |
| `EvaluadorAG` | Repara cada fila para que sume `a_i`, calcula Z, la penalización y `fitness = 1 / (Z + λ·Pen)` |
| `OperadoresGeneticos` | Selección por torneo (k = 3) y por ruleta, cruce de un punto por filas, mutación por transferencia |
| `MotorAG.ejecutar` | Bucle de generaciones con elitismo de 2, selección, cruce, mutación y parada tras 50 generaciones sin mejora |

## 2. Qué falta o hay que corregir

1. **Adaptador al contrato.** Escriban una función que reciba `RedLogistica` y `ParametrosAG`,
   arme `InicializadorAG`, `EvaluadorAG`, `OperadoresGeneticos` y `MotorAG`, y devuelva un
   `ResultadoGenetico`. Conéctenla en `contratos.ejecutar_genetico`.
2. **Registro de convergencia.** En cada generación agreguen un
   `RegistroConvergencia(generacion, mejor_costo, costo_promedio)`. `mejor_costo` es el mejor
   costo hasta esa generación, así que la serie nunca sube. Hoy `MotorAG` no guarda nada de esto.
3. **Semilla reproducible.** `InicializadorAG` y `OperadoresGeneticos` crean cada uno su propio
   generador aleatorio. Usen `parametros.semilla` en los dos, o compartan un solo
   `np.random.default_rng(semilla)`. Con la misma semilla, dos corridas deben dar exactamente
   el mismo resultado.
4. **Elitismo.**
   - Las copias de la élite se crean como `Individuo` nuevos, con `fitness = 0` y
     `costo_total = 0`, y no se vuelven a evaluar. En la generación siguiente quedan de últimas
     y casi nunca ganan un torneo. Hay que copiarles `fitness`, `costo_total` y `violaciones`,
     o evaluarlas.
   - Usen `parametros.elitismo` en vez del 2 fijo, y contemplen `elitismo = 0`.
5. **Nombres de los parámetros.** `ejecutar` usa `tasa_cruce` y `tasa_mutacion`; el contrato
   usa `prob_cruce` y `prob_mutacion`. `lambda_pen` va a `EvaluadorAG`.
6. **Rutas no habilitadas.** En esas rutas `red.costos[i, j]` vale 0, así que un flujo ahí sale
   "gratis". Usen `red.rutas_habilitadas` en estos cuatro puntos:
   - **inicialización:** Dirichlet solo sobre las columnas habilitadas;
   - **heurística:** que no tome rutas deshabilitadas, aunque el costo 0 las ponga primeras en
     el orden;
   - **mutación:** `j_prima` debe estar habilitada;
   - **reparación:** reescalar solo las columnas habilitadas.
7. **Planta ficticia.** Si la red trae la columna `FICTICIA` (con `red.tiene_planta_ficticia()`
   lo saben), trátenla como una planta más: su costo ya es `M` y su capacidad es `Σa − Σb`.
8. **Reparación después de cada operador.** Hoy la reparación ocurre dentro de `evaluar`, que se
   llama después del cruce y la mutación. Si cambian el orden, mantengan esa regla: ningún
   individuo se evalúa sin reparar.
9. **Cruce de dos puntos.** Falta; el README lo pide como opción. Además, con `m = 1`,
   `cruce_un_punto` falla porque `integers(1, 1)` no tiene valores.
10. **Tipo de selección y de cruce.** Si los quieren configurables desde la interfaz, agréguenlos
    a `ParametrosAG` (contratos) y a `ParametrosAGEntrada` (schemas). El servicio guarda los
    parámetros con `asdict`, así que se guardan solos.
11. **Salida.**
    - `costo_total` es el Z sin penalización del mejor individuo.
    - `violaciones` es la violación de oferta y capacidad del mejor individuo.
    - `tiempo_ms` se mide con `time.perf_counter()`.
    - `flujos` es la matriz `m × n` del mejor individuo.

## 3. Contrato (`app/optimizacion/contratos.py`)

- **Entrada:** `RedLogistica` y `ParametrosAG`.
  - Red: `oferta`, `capacidad`, `costos`, `rutas_habilitadas`, `codigos_empresas`,
    `codigos_plantas`.
  - Parámetros: `tamano_poblacion`, `generaciones`, `prob_cruce`, `prob_mutacion`, `elitismo`,
    `lambda_pen` y `semilla`.
- **Salida:** `ResultadoGenetico(costo_total, flujos, violaciones, convergencia, tiempo_ms)`.
- **Valores por defecto** (README, sección 6): población 100, 300 generaciones, cruce 0,85,
  mutación 0,10, elitismo 2. Si la petición no trae `lambda_pen`, se usa el parámetro global
  `lambda_ag` (1.000.000).

## 4. Pruebas que deben pasar

- En `tests/unit/test_aceptacion_genetico.py`, quiten `@PENDIENTE`. Son 4 pruebas:
  - dos corridas con semilla 42 dan el mismo resultado;
  - cada fila cumple `Σ_j x_ij = a_i` (tolerancia 1e-6);
  - el gap promedio en 10 corridas (semillas 0 a 9) es menor o igual a 2 %;
  - con elitismo, la serie del mejor costo nunca sube.
- En `tests/unit/test_contratos.py`, borren `test_ejecutar_genetico_pendiente`.
- En `tests/integration/test_api_optimizacion.py`, cambien `test_genetico_pendiente_responde_501`:
  ahora debe esperar 201.
- `prob_cruce = 1.5 → 422` ya pasa (`tests/unit/test_api_validacion_ag.py`), porque la validación
  la hace la API.

## 5. Cómo calcular el gap

```
gap (%) = (Z_AG − Z*) / Z* · 100
```

Con Z* = 64.691.000 COP/semana (caso base). El gap no puede ser negativo: si sale negativo, la
solución del AG está violando alguna restricción.

## 6. Notas

- Ruff no revisa `genetico/` por ahora (`extend-exclude` en `pyproject.toml`). Cuando terminen,
  quiten la exclusión y corran `ruff check .`.
- Prueben primero el adaptador con la red del caso base que arma `tests/utilidades.py`
  (`construir_red_caso_base()`), que no necesita base de datos.
