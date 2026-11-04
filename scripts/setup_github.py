#!/usr/bin/env python3
"""Configura el repositorio de GitHub del Grupo Orion a partir de docs/backlog/backlog.json.

Crea (o actualiza, si ya existen):
  1. Etiquetas: tipo, épica, prioridad, área y severidad.
  2. Milestones: Sprint 1 y Sprint 2, con su fecha de fin.
  3. Rama develop y protección de main y develop (si el plan de GitHub lo permite).
  4. Una issue por historia de usuario (HU-01 … HU-17) y por ítem técnico (T-01a … T-05).
  5. El tablero de GitHub Projects con los campos SP, Horas, Sprint, Prioridad, Épica y
     Responsable, y todas las issues agregadas con sus valores.

Es idempotente: si una issue con el mismo identificador ya existe, no la duplica.

Requisitos:
  - GitHub CLI (https://cli.github.com) autenticado con permiso de proyectos:
        gh auth login
        gh auth refresh -s project
  - Python 3.10+ (solo biblioteca estándar).

Uso (desde la raíz del repositorio):
  python scripts/setup_github.py --dry-run     # muestra lo que haría, sin tocar GitHub
  python scripts/setup_github.py               # lo ejecuta
  python scripts/setup_github.py --sin-tablero # solo etiquetas, milestones, ramas e issues

Antes de ejecutarlo, completen los usuarios de GitHub en la sección "equipo" de
docs/backlog/backlog.json para que las issues queden asignadas.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
BACKLOG = RAIZ / "docs" / "backlog" / "backlog.json"
TITULO_TABLERO = "Orion · EcoResiduos del Llano"

# El fin de cada sprint es a las 23:59 de Bogotá (UTC-5) → 04:59 UTC del día siguiente.
FIN_SPRINT_UTC = {
    "Sprint 1": "2026-11-04T04:59:59Z",
    "Sprint 2": "2026-11-13T04:59:59Z",
}

ETIQUETAS: list[tuple[str, str, str]] = [
    ("tipo: historia", "1F7A4D", "Historia de usuario del Product Backlog"),
    ("tipo: tarea", "5B6B62", "Ítem técnico (configuración, CI/CD, despliegue, informe)"),
    ("tipo: bug", "C2410C", "Defecto"),
    ("épica: E1", "B7E4C7", "Gestión dinámica de la red logística"),
    ("épica: E2", "95D5B2", "Optimización exacta de la red"),
    ("épica: E3", "74C69D", "Optimización metaheurística con Algoritmo Genético"),
    ("épica: E4", "52B788", "Análisis de sensibilidad"),
    ("épica: E5", "40916C", "Comparación, historial y reportes"),
    ("prioridad: must", "12392A", "MoSCoW: imprescindible para cumplir el enunciado"),
    ("prioridad: should", "B7791F", "MoSCoW: alto valor, se puede simplificar"),
    ("prioridad: could", "DCE3DE", "MoSCoW: primera en recortarse"),
    ("área: backend", "1D4ED8", "FastAPI, servicios, repositorios"),
    ("área: frontend", "7C3AED", "React, interfaz, visualización"),
    ("área: optimización", "0F766E", "Modelo exacto, AG, sensibilidad"),
    ("área: bd", "0369A1", "Modelos ORM, migraciones Alembic, Supabase"),
    ("área: devops", "475569", "CI/CD, Docker, despliegue"),
    ("área: docs", "A16207", "Documentación e informe IEEE"),
    ("sev: crítica", "7F1D1D", "Bloquea el merge"),
    ("sev: alta", "B91C1C", "Defecto de severidad alta"),
    ("sev: media", "F59E0B", "Defecto de severidad media"),
    ("sev: baja", "FDE68A", "Defecto de severidad baja"),
]

AREA_A_ETIQUETA = {
    "backend": "área: backend",
    "frontend": "área: frontend",
    "optimizacion": "área: optimización",
    "bd": "área: bd",
    "devops": "área: devops",
    "docs": "área: docs",
}

DOR = [
    "Asociada a una épica y en formato Como / Quiero / Para",
    "Criterios de aceptación verificables y con datos concretos",
    "Estimada (≤ 13 SP)",
    "Dependencias identificadas",
    "Diagramas de clases y de secuencia esbozados (Documento Base, 12.4)",
    "Mockup aprobado por el PO (si tiene interfaz)",
    "Contrato de API definido (Documento Base, 9.4)",
    "Datos y casos de prueba identificados",
    "Responsable asignado y cabe en el sprint",
]


class GH:
    """Envoltorio mínimo de la GitHub CLI con modo dry-run."""

    def __init__(self, dry_run: bool) -> None:
        self.dry_run = dry_run
        self._contador = 0

    def run(self, *args: str, lectura: bool = False, permitir_error: bool = False) -> str:
        comando = ["gh", *args]
        if self.dry_run and not lectura:
            print("  [dry-run] " + " ".join(_citar(a) for a in comando))
            self._contador += 1
            return ""
        try:
            # gh responde en UTF-8; sin encoding explícito, Windows usa cp1252 y
            # "Épica" o "·" llegan corruptos (y el script no reconoce lo que ya creó).
            resultado = subprocess.run(comando, check=True, capture_output=True,
                                       encoding="utf-8", errors="replace")
        except FileNotFoundError:
            sys.exit("No se encontró 'gh'. Instale GitHub CLI: https://cli.github.com")
        except subprocess.CalledProcessError as error:
            if permitir_error:
                return ""
            sys.exit(f"Falló: {' '.join(comando)}\n{error.stderr.strip()}")
        return resultado.stdout.strip()

    def json(self, *args: str) -> object:
        salida = self.run(*args, lectura=True, permitir_error=self.dry_run)
        return json.loads(salida) if salida else {}


def _citar(arg: str) -> str:
    return f'"{arg}"' if (" " in arg or not arg) else arg


# ─────────────────────────────── Contenido de las issues ───────────────────────────────


def _nombre(equipo: dict, ini: str) -> str:
    return equipo[ini]["nombre"]


def cuerpo_historia(hu: dict, datos: dict) -> str:
    equipo = datos["equipo"]
    epica = f"{hu['epica']} — {datos['epicas'][hu['epica']]}"
    criterios = "\n\n".join(f"**CA{i}.** {c}" for i, c in enumerate(hu["criterios"], start=1))
    tareas = "\n".join(
        f"- [ ] {t} — {_nombre(equipo, r)} — {h} h" for t, r, h in hu["tareas"]
    )
    horas = sum(h for _, _, h in hu["tareas"])
    pruebas = ", ".join(hu.get("pruebas", [])) or "—"
    dor = "\n".join(f"- [ ] {d}" for d in DOR)
    return f"""## Historia

{hu['historia']}

| Épica | Prioridad | SP | Sprint | Responsable |
| --- | --- | --- | --- | --- |
| {epica} | {hu['prioridad']} | {hu['sp']} | {hu['sprint']} | {_nombre(equipo, hu['responsable'])} |

## Criterios de aceptación

{criterios}

## Tareas ({horas} h)

{tareas}

## Casos de prueba

{pruebas} (Documento Base, sección 14.4)

## Definition of Ready

{dor}

---
*Generado desde `docs/backlog/backlog.json`. Detalle de diseño en el Documento Base del proyecto.*
"""


def cuerpo_tecnico(t: dict, datos: dict) -> str:
    equipo = datos["equipo"]
    tareas = "\n".join(
        f"- [ ] {tarea} — {_nombre(equipo, r)} — {h} h" for tarea, r, h in t["tareas"]
    )
    horas = sum(h for _, _, h in t["tareas"])
    return f"""## Descripción

{t['descripcion']}

| Sprint | Responsable |
| --- | --- |
| {t['sprint']} | {_nombre(equipo, t['responsable'])} |

## Subtareas ({horas} h)

{tareas}

## Criterio de terminado

{t['terminado']}

---
*Generado desde `docs/backlog/backlog.json`.*
"""


def opcion_epica(codigo: str, datos: dict) -> str:
    """Nombre de la opción del campo Épica (sin comas: gh las usa como separador)."""
    return f"{codigo} {datos['epicas'][codigo].replace(',', '')}"


def asignados(item: dict, equipo: dict) -> list[str]:
    iniciales = [item["responsable"], *(r for _, r, _ in item["tareas"])]
    usuarios: list[str] = []
    for ini in iniciales:
        usuario = equipo[ini].get("github", "").strip().lstrip("@")
        if usuario and usuario not in usuarios:
            usuarios.append(usuario)
    return usuarios


# ─────────────────────────────────────── Pasos ───────────────────────────────────────


def detectar_repo(gh: GH, repo: str | None) -> str:
    if repo:
        return repo
    datos = gh.json("repo", "view", "--json", "nameWithOwner")
    if not datos:
        sys.exit("No pude detectar el repositorio. Use --repo OWNER/NOMBRE.")
    return datos["nameWithOwner"]


def crear_etiquetas(gh: GH, repo: str) -> None:
    print("\n▶ Etiquetas")
    for nombre, color, descripcion in ETIQUETAS:
        gh.run("label", "create", nombre, "-R", repo, "--color", color,
               "--description", descripcion, "--force")
        if not gh.dry_run:
            print(f"  ✓ {nombre}")


def crear_milestones(gh: GH, repo: str, datos: dict) -> None:
    print("\n▶ Milestones")
    existentes = gh.json("api", f"repos/{repo}/milestones?state=all&per_page=100") or []
    titulos = {m["title"] for m in existentes}
    for sprint in datos["sprints"]:
        if sprint["nombre"] in titulos:
            print(f"  = {sprint['nombre']} ya existe")
            continue
        gh.run("api", "-X", "POST", f"repos/{repo}/milestones",
               "-f", f"title={sprint['nombre']}",
               "-f", f"description={sprint['objetivo']}",
               "-f", f"due_on={FIN_SPRINT_UTC[sprint['nombre']]}")
        if not gh.dry_run:
            print(f"  ✓ {sprint['nombre']}")


def configurar_ramas(gh: GH, repo: str) -> None:
    print("\n▶ Ramas")
    info = gh.json("api", f"repos/{repo}")
    principal = info.get("default_branch", "main") if info else "main"
    ramas = gh.json("api", f"repos/{repo}/branches?per_page=100") or []
    nombres = {r["name"] for r in ramas}
    if "develop" in nombres:
        print("  = develop ya existe")
    else:
        sha = ""
        if not gh.dry_run:
            sha = gh.json("api", f"repos/{repo}/git/ref/heads/{principal}")["object"]["sha"]
        gh.run("api", "-X", "POST", f"repos/{repo}/git/refs",
               "-f", "ref=refs/heads/develop", "-f", f"sha={sha or '<sha-de-main>'}")
        if not gh.dry_run:
            print(f"  ✓ develop creada desde {principal}")

    proteccion = {
        "required_status_checks": None,
        "enforce_admins": False,
        "required_pull_request_reviews": {"required_approving_review_count": 1},
        "restrictions": None,
        "allow_force_pushes": False,
        "allow_deletions": False,
    }
    for rama in (principal, "develop"):
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            json.dump(proteccion, f)
            ruta = f.name
        salida = gh.run("api", "-X", "PUT", f"repos/{repo}/branches/{rama}/protection",
                        "--input", ruta, permitir_error=True)
        Path(ruta).unlink(missing_ok=True)
        if gh.dry_run:
            continue
        if salida:
            print(f"  ✓ {rama} protegida (PR con 1 aprobación)")
        else:
            print(f"  ! No se pudo proteger {rama}. En repos privados de cuentas gratuitas "
                  "GitHub no permite reglas de protección; háganlo público o acuerden "
                  "no hacer push directo.")


def crear_issues(gh: GH, repo: str, datos: dict) -> list[dict]:
    print("\n▶ Issues")
    existentes = gh.json("issue", "list", "-R", repo, "--state", "all", "--limit", "500",
                         "--json", "number,title,url") or []
    por_id = {i["title"].split(" · ")[0]: i for i in existentes}
    creadas: list[dict] = []

    items = [("historia", h) for h in datos["historias"]] + \
            [("tecnico", t) for t in datos["tecnicos"]]

    for tipo, item in items:
        titulo = f"{item['id']} · {item['titulo']}"
        if item["id"] in por_id:
            print(f"  = {titulo} ya existe (#{por_id[item['id']]['number']})")
            creadas.append({"item": item, "tipo": tipo, "url": por_id[item["id"]]["url"]})
            continue

        if tipo == "historia":
            cuerpo = cuerpo_historia(item, datos)
            etiquetas = ["tipo: historia", f"épica: {item['epica']}",
                         f"prioridad: {item['prioridad'].lower()}"]
        else:
            cuerpo = cuerpo_tecnico(item, datos)
            etiquetas = ["tipo: tarea"]
        etiquetas += [AREA_A_ETIQUETA[a] for a in item.get("areas", [])]

        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False,
                                         encoding="utf-8") as f:
            f.write(cuerpo)
            ruta = f.name

        args = ["issue", "create", "-R", repo, "--title", titulo, "--body-file", ruta,
                "--milestone", item["sprint"]]
        for e in etiquetas:
            args += ["--label", e]
        for usuario in asignados(item, datos["equipo"]):
            args += ["--assignee", usuario]

        url = gh.run(*args)
        Path(ruta).unlink(missing_ok=True)
        if not gh.dry_run:
            print(f"  ✓ {titulo}")
        creadas.append({"item": item, "tipo": tipo, "url": url})
    return creadas


def crear_tablero(gh: GH, repo: str, datos: dict, issues: list[dict]) -> None:
    print("\n▶ Tablero de GitHub Projects")
    owner = repo.split("/")[0]

    proyectos = gh.json("project", "list", "--owner", owner, "--format", "json",
                        "--limit", "100")
    proyecto = next((p for p in (proyectos or {}).get("projects", [])
                     if p["title"] == TITULO_TABLERO), None)
    if proyecto:
        print(f"  = '{TITULO_TABLERO}' ya existe (#{proyecto['number']})")
    else:
        salida = gh.run("project", "create", "--owner", owner, "--title", TITULO_TABLERO,
                        "--format", "json")
        if gh.dry_run:
            proyecto = {"number": "<N>", "id": "<ID>"}
        else:
            proyecto = json.loads(salida)
            print(f"  ✓ Tablero creado (#{proyecto['number']})")
    numero, project_id = str(proyecto["number"]), proyecto["id"]

    gh.run("project", "link", numero, "--owner", owner, "--repo", repo, permitir_error=True)

    equipo = datos["equipo"]
    campos_deseados = {
        "SP": ("NUMBER", None),
        "Horas": ("NUMBER", None),
        "Sprint": ("SINGLE_SELECT", [s["nombre"] for s in datos["sprints"]]),
        "Prioridad": ("SINGLE_SELECT", ["Must", "Should", "Could"]),
        "Épica": ("SINGLE_SELECT", [opcion_epica(k, datos) for k in datos["epicas"]]),
        "Responsable": ("SINGLE_SELECT", [m["nombre"] for m in equipo.values()]),
    }
    actuales = {f["name"]: f for f in
                (gh.json("project", "field-list", numero, "--owner", owner,
                         "--format", "json", "--limit", "100") or {}).get("fields", [])}
    for nombre, (tipo, opciones) in campos_deseados.items():
        if nombre in actuales:
            continue
        args = ["project", "field-create", numero, "--owner", owner,
                "--name", nombre, "--data-type", tipo]
        if opciones:
            args += ["--single-select-options", ",".join(opciones)]
        gh.run(*args)
        if not gh.dry_run:
            print(f"  ✓ Campo {nombre}")

    if gh.dry_run:
        print(f"  [dry-run] agregar {len(issues)} issues al tablero y llenar sus campos")
        return

    campos = {f["name"]: f for f in
              gh.json("project", "field-list", numero, "--owner", owner,
                      "--format", "json", "--limit", "100").get("fields", [])}

    def opcion(campo: str, valor: str) -> str | None:
        for o in campos[campo].get("options", []):
            if o["name"] == valor:
                return o["id"]
        return None

    for registro in issues:
        item, url = registro["item"], registro["url"]
        if not url:
            continue
        agregado = json.loads(gh.run("project", "item-add", numero, "--owner", owner,
                                     "--url", url, "--format", "json"))
        item_id = agregado["id"]
        horas = sum(h for _, _, h in item["tareas"])

        valores: list[tuple[str, list[str]]] = [
            ("Horas", ["--number", str(horas)]),
            ("Sprint", ["--single-select-option-id", opcion("Sprint", item["sprint"]) or ""]),
            ("Responsable", ["--single-select-option-id",
                             opcion("Responsable", equipo[item["responsable"]]["nombre"]) or ""]),
        ]
        if registro["tipo"] == "historia":
            valores += [
                ("SP", ["--number", str(item["sp"])]),
                ("Prioridad", ["--single-select-option-id",
                               opcion("Prioridad", item["prioridad"]) or ""]),
                ("Épica", ["--single-select-option-id",
                           opcion("Épica", opcion_epica(item["epica"], datos)) or ""]),
            ]
        for campo, flag in valores:
            if flag[-1] == "":
                continue
            gh.run("project", "item-edit", "--id", item_id, "--project-id", project_id,
                   "--field-id", campos[campo]["id"], *flag, permitir_error=True)
        print(f"  ✓ {item['id']} en el tablero")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--repo", help="OWNER/NOMBRE (por defecto, el repo actual)")
    parser.add_argument("--dry-run", action="store_true", help="Solo muestra los comandos")
    parser.add_argument("--sin-tablero", action="store_true", help="No crea el tablero")
    parser.add_argument("--sin-ramas", action="store_true",
                        help="No crea develop ni configura protección")
    args = parser.parse_args()

    datos = json.loads(BACKLOG.read_text(encoding="utf-8"))
    sin_usuario = [m["nombre"] for m in datos["equipo"].values() if not m.get("github")]
    if sin_usuario:
        print("Aviso: sin usuario de GitHub en backlog.json para: " + ", ".join(sin_usuario)
              + ". Esas issues no quedarán asignadas.")

    gh = GH(args.dry_run)
    repo = detectar_repo(gh, args.repo) if not args.dry_run else (args.repo or "OWNER/REPO")
    print(f"Repositorio: {repo}{'  (dry-run)' if args.dry_run else ''}")

    crear_etiquetas(gh, repo)
    crear_milestones(gh, repo, datos)
    if not args.sin_ramas:
        configurar_ramas(gh, repo)
    issues = crear_issues(gh, repo, datos)
    if not args.sin_tablero:
        crear_tablero(gh, repo, datos, issues)

    print("\nListo.")
    if not args.sin_tablero and not args.dry_run:
        print("Falta un paso manual en el tablero (2 minutos): en la vista Board, edite el "
              "campo Status para que sus columnas sean Backlog, Ready, En curso, En revisión "
              "y Hecho, y agrupe por Status.")


if __name__ == "__main__":
    main()