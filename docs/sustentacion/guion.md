# Guion de la sustentación · Grupo Orion

**Duración:** 12 min + preguntas · **Fecha:** jueves 12 de noviembre de 2026

## Antes de entrar (15 min antes)

1. Levantar todo local: `docker compose up` (plan A) o la versión desplegada (si existe).
2. **Calentar la API:** cargar el caso base y ejecutar el exacto una vez antes de presentar. El exacto (MODI propio, sin solver externo) resuelve el caso base en milisegundos.
3. Dejar abiertas cuatro pestañas: Panel, Exacto, Sensibilidad y Riesgo.
4. Tener a mano los PDF de respaldo (comparativo y exacto) en `Orion/Artefactos/02_Reportes`.

## Cifras que hay que decir de memoria

| Dato | Valor |
|---|---|
| Z* caso base | **$64.691.000 / semana** |
| Plantas saturadas | Villavicencio (−17.750 COP/t) y Restrepo (−14.250 COP/t) |
| Z* caso real del Meta | $59.295.262 / semana |
| AG en el caso base | Llega al óptimo en 10 de 10 corridas |
| AG en 100 × 20 | Brecha de 0,91 % |
| Combustible +20 % | +7,3 % de costo, misma asignación |
| Con acopios (Puerto López y San Martín) | $61.761.025 (−4,5 %) |
| ICE | Villavicencio es la más crítica; ρ = 0,80 (base) y 1,00 (caso real) |

## Minuto a minuto

| Min | Quién | Qué se muestra en vivo | Frase clave |
|---|---|---|---|
| 0–1 | David | Problema y objetivo; equipo y roles | “Asignar a ojo satura unas plantas y deja otras vacías; queremos el costo mínimo y saber qué pasa si algo cambia.” |
| 1–3 | Juan David | **Panel** → “Cargar caso real del Meta” → mapa con rutas reales. **Red** → agregar una empresa con un clic en el mapa (las rutas se crean solas) | “La red crece sin tocar el código.” |
| 3–5 | Julián | **Exacto** → ejecutar: Z*, plantas saturadas y precio sombra | “Ampliar Villavicencio una tonelada ahorra 17.750 pesos por semana.” |
| 5–7 | Martín | **Genético** → ejecutar con semilla 42: convergencia; **Comparativo**: exacto frente a AG y brecha | “El AG llega al mismo óptimo; con 100 empresas queda a menos del 1 %.” |
| 7–9 | Julián | **Sensibilidad** → “Combustible +20 %” y cierre de Villavicencio → antes y después; rangos | “El combustible sube el costo, pero lo que de verdad rompe la red es la capacidad.” |
| 9–10 | David | **Panel** → “Agregar centros de acopio” → Exacto (columnas “vía A01/A02”). **Riesgo**: ranking ICE, mover α y β, “Usar pesos calibrados” | “Adaptamos nuestro índice del CICI 2026 y ordena las plantas igual que la falla simulada.” |
| 10–11 | Martín | **Comparativo** → escalabilidad y descarga del PDF | — |
| 11–12 | David | Conclusiones y trabajo futuro (GAT, costos fijos de acopio) | — |

> El caso base se usa en los minutos 3 a 10 porque sus cifras son las del informe. Después de mostrar el caso real, recargar el caso base al llegar al minuto 3.

## Preguntas probables

- **¿Por qué la planta ficticia?** Si la oferta supera la capacidad, el modelo sería infactible. La ficticia absorbe el exceso con una penalización de 10⁶ COP/t y muestra cuántas toneladas no caben.
- **¿Por qué usar un AG si el exacto da el óptimo?** En redes pequeñas el exacto es más rápido, pero nuestro MODI en Python tarda entre 5 y 11 s en 100 × 20, lo mismo que el AG (brecha de 0,91 %). Además, el AG sirve cuando entran costos fijos o no linealidades; su estructura no cambia.
- **¿Por qué no usan PuLP?** Se usó en el Sprint 1. En el PR #58 el exacto pasó a un transbordo con flujo máximo y MODI propios, sin solver externo; los valores de referencia (Z*, duales, escenarios) no cambiaron.
- **¿Cómo se calculan los rangos?** Con re-optimización paramétrica: se mueve cada parámetro hasta que cambia la base óptima (o los duales), con búsqueda y bisección.
- **¿Qué significa ρ = 0,80?** Que el ranking del ICE y el ranking del impacto real se parecen mucho. Con 4 plantas es evidencia preliminar, y así lo decimos.
- **¿Los acopios siempre ahorran?** No. Sin flete consolidado, ir por el acopio cuesta más que ir directo. El ahorro sale de la tarifa de 200 frente a 350 COP/t·km.

## Plan B

- Sin red: todo corre local con Docker; OSRM solo se usa al crear nodos nuevos (los datos ya están guardados).
- Si algo falla en la demo: mostrar los PDF de respaldo y seguir con el guion.
