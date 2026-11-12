# Guía: conectar el modelo exacto (HU-07)

> **Estado (10 nov 2026): conectado.** La implementación está en `app/optimizacion/exacto/modelo_transporte.py` (PuLP + CBC) y el verificador en `app/optimizacion/verificador.py`. Las pruebas de aceptación de `tests/unit/test_aceptacion_exacto.py` están activas y pasan.

Esta guía explica qué falta para que `POST /api/v1/optimizacion/exacto` deje de responder
501. Todo lo que está alrededor del modelo ya funciona: construir la red desde la base, validarla,
agregar la planta ficticia, guardar el resultado y consultarlo. **Solo falta el modelo.**

## 1. Formulación

**Conjuntos**

- `I`: empresas (filas de la red), en el orden de `red.codigos_empresas`.
- `J`: plantas (columnas), en el orden de `red.codigos_plantas`. Si la oferta supera la
  capacidad, la última columna es la planta `FICTICIA`.

**Parámetros** (todos vienen en la `RedLogistica`)

| Símbolo | Campo | Significado |
|---|---|---|
| `a_i` | `red.oferta[i]` | Oferta semanal de la empresa `i` (t) |
| `b_j` | `red.capacidad[j]` | Capacidad semanal de la planta `j` (t) |
| `c_ij` | `red.costos[i, j]` | `k · d_ij + o_j` (COP/t); `k` es el `costo_km_t` de la ruta o el global |
| — | `red.rutas_habilitadas[i, j]` | `True` si la ruta existe, está habilitada y tiene distancia |

**Variables:** `x_ij ≥ 0`, las toneladas que la empresa `i` envía a la planta `j`.

**Función objetivo:** `min Z = Σ_i Σ_j c_ij · x_ij`

**Restricciones**

- Oferta, con **igualdad**: `Σ_j x_ij = a_i` para cada empresa.
- Capacidad, con **menor o igual**: `Σ_i x_ij ≤ b_j` para cada planta.
- Rutas no habilitadas: `x_ij = 0`. Puede crear la variable con cota superior 0 o no crearla.

> **Cuidado:** en las rutas no habilitadas `red.costos[i, j]` vale 0. Si el modelo no las
> excluye, enviará residuo por ellas "gratis".

## 2. Planta ficticia

- Hace falta cuando `Σ a_i > Σ b_j`. `ValidadorRed` lo detecta y el servicio
  (`preparar_red_para_motor`) ya la agrega **antes** de llamar al motor, con estos datos:
  - Capacidad `Σ a_i − Σ b_j`.
  - Costo `M = penalizacion_ficticia`, el parámetro global (1.000.000 COP/t).
  - Código `FICTICIA`, en la última columna.
- El modelo **no** debe agregarla otra vez. Con `red.tiene_planta_ficticia()` sabe si viene.
- Sus flujos se guardan con `destino_id` nulo y en la API aparecen con destino `FICTICIA`.
- Cuando `Σ a_i ≤ Σ b_j` no se agrega nada: la holgura queda en las restricciones `≤`.

## 3. Sacar los resultados de PuLP

El proyecto fija `pulp>=2.8,<4`. **PuLP 4 cambió la API** (por ejemplo, ya no existe
`LpVariable(..., lowBound=0)`), así que usen la API clásica.

- **Nombren cada restricción** al agregarla, por ejemplo `oferta_E01` o `capacidad_P01`, para
  encontrarla después en `prob.constraints[nombre]`.
- **Resuelvan con CBC sin mensajes:** `pulp.PULP_CBC_CMD(msg=0)`.
- **Estado:** `pulp.LpStatus[prob.status]`. Conviertan `"Optimal"` a la constante
  `ESTADO_OPTIMO` (`"Óptimo"`) de `contratos.py`.
- **Costo total:** `pulp.value(prob.objective)`.
- **Flujos:** `variable.varValue`, en una matriz `m × n`.
- **Duales:** `.pi` de cada restricción. En un problema de minimización, el dual de una
  restricción `≤` es `≤ 0`. Por ejemplo, P01 da −17.750.
- **Costos reducidos:** `.dj` de cada variable.
- **Holguras:** `.slack` de cada restricción de capacidad (`b_j − Σ_i x_ij`). PuLP puede
  devolver `-0.0`; es cero.
- **Tiempo:** midan con `time.perf_counter()` y conviértanlo a milisegundos.

## 4. Dónde conectarlo

1. Escriban la implementación en `app/optimizacion/exacto/`. Debe recibir una `RedLogistica` y
   devolver un `ResultadoExacto`.
2. En `app/optimizacion/contratos.py`, cambien el `raise NotImplementedError` de
   `resolver_exacto` por la llamada a su implementación.
3. Formas que espera el servicio para guardar (`n` incluye la ficticia si viene):

| Campo | Forma |
|---|---|
| `flujos` | `(m, n)` |
| `duales_oferta` | `(m,)` |
| `duales_capacidad` | `(n,)` |
| `costos_reducidos` | `(m, n)` |
| `holguras` | `(n,)` |
| `estado`, `costo_total`, `tiempo_ms` | escalares |

El servicio guarda la ejecución, los flujos mayores que 0, los duales de oferta y capacidad,
las holguras y los costos reducidos de cada ruta. Ustedes no tienen que tocar la base de datos.

## 5. Pruebas que deben quitar del skip

- En `tests/unit/test_aceptacion_exacto.py`, quiten `@PENDIENTE` de las 6 pruebas.
- En `tests/unit/test_contratos.py`, borren `test_resolver_exacto_pendiente`.
- En `tests/integration/test_api_optimizacion.py`, cambien `test_exacto_pendiente_responde_501`:
  ahora debe esperar 201 y una ejecución guardada.

## 6. Valores de referencia (caso base: oferta 890 t, capacidad 950 t, k = 350)

| Prueba | Valor esperado |
|---|---|
| Estado | `Óptimo` |
| Z* | 64.691.000 COP/semana |
| Rutas con flujo > 0 | 11 |
| Duales de capacidad P01..P04 | −17.750, −14.250, 0, 0 |
| Holguras de capacidad P01..P04 | 0, 0, 5, 55 |
| Violaciones (tolerancia 1e-6) | 0 |
| Oferta +10 % (979 t) | la planta ficticia recibe 29 t |
| Ejemplo de costo | c(E04, P04) = 350 · 185 + 40.000 = 104.750 |

Estos valores se comprobaron con PuLP 3.3.2 y CBC usando la formulación de la sección 1.

## 7. Observaciones sobre el código actual de `exacto/`

1. **`vogel.py` no se puede importar.** La línea `import verificar_balanceo.py` debe ser
   `from .verificar_balanceo import verificar_balanceo`. Como `exacto/` no tiene
   `__init__.py`, conviene agregarlo para que sea un paquete normal.
2. **`MODI.py`, clase `SolverExacto`: la restricción de capacidad usa `==` y no `<=`.**
   Para lograrlo, `_balancear` agrega una fila u origen ficticio con costo 0. En el caso base
   (950 > 890) el Z* sale igual, pero:
   - el modelo del README y de HU-07 usa `≤`;
   - en un problema balanceado con solo igualdades, los duales no son únicos y pueden salir
     desplazados, así que no van a coincidir con −17.750 y −14.250;
   - las holguras quedan escondidas en la fila ficticia y no en `.slack`.

   Con `≤` directamente no hace falta ningún origen ficticio.
3. **`MODI.py` y `verificar_balanceo.py`: la planta ficticia tiene costo 0 y no M.** Cuando la
   oferta supera la capacidad, el proyecto define una penalización `M = penalizacion_ficticia`
   (README 5.3 y HU-06). Con costo 0, el Z reportado no incluye esa penalización y no se puede
   comparar con el del AG. En este backend la planta ficticia ya llega en la red con costo M.
4. **Los `print` de `vogel.py`, `verificar_balanceo.py` y `MODI.py` ensucian la salida de la
   API.** Quítenlos del camino que use el endpoint.
5. **Ruff no revisa `exacto/` por ahora** (`extend-exclude` en `pyproject.toml`). Cuando
   terminen, quiten la exclusión y corran `ruff check .`.
