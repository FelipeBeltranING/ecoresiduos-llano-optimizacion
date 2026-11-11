# Scripts

## setup_github.py

Configura el repositorio de GitHub del Grupo Orion a partir de `docs/backlog/backlog.json`.

Crea (o actualiza, si ya existen):

1. Etiquetas: tipo, épica, prioridad, área y severidad.
2. Milestones: Sprint 1 y Sprint 2, con su fecha de fin (23:59 de Bogotá, guardada en UTC).
3. Rama `develop` y protección de `main` y `develop` (si el plan de GitHub lo permite).
4. Una issue por historia de usuario (HU-01 … HU-17) y por ítem técnico (T-01a … T-05).
5. El tablero de GitHub Projects con los campos SP, Horas, Sprint, Prioridad, Épica y
   Responsable, y todas las issues agregadas con sus valores.

Es idempotente: si una issue con el mismo identificador ya existe, no la duplica.

### Requisitos

- GitHub CLI (https://cli.github.com) autenticado con permiso de proyectos:

  ```bash
  gh auth login
  gh auth refresh -s project
  ```

- Python 3.10 o superior (solo biblioteca estándar).

### Uso (desde la raíz del repositorio)

```bash
python scripts/setup_github.py --dry-run      # muestra lo que haría, sin tocar GitHub
python scripts/setup_github.py                # lo ejecuta
python scripts/setup_github.py --sin-tablero  # solo etiquetas, milestones, ramas e issues
python scripts/setup_github.py --sin-ramas    # no crea develop ni configura la protección
python scripts/setup_github.py --repo OWNER/NOMBRE
```

Antes de ejecutarlo, completen los usuarios de GitHub en la sección `equipo` de
`docs/backlog/backlog.json` para que las issues queden asignadas.

Al terminar falta un paso manual en el tablero: en la vista Board, editar el campo Status
para que sus columnas sean Backlog, Ready, En curso, En revisión y Hecho, y agrupar por Status.
