# Frontend — React + TypeScript + Vite + Tailwind

Aplicación de una sola página (SPA) para operar la red logística de EcoResiduos del Llano.

```
src/
├── api/          # cliente Axios, cliente de TanStack Query y errores normalizados
├── components/   # layout y componentes reutilizables
├── features/     # lógica por funcionalidad (se agrega con cada historia)
├── hooks/        # hooks compartidos (useX)
├── lib/          # utilidades (formato es-CO, validaciones Zod)
├── pages/        # una página por ruta del mapa de navegación (Documento Base 13.1)
├── styles/       # tokens de la guía de estilo (Tailwind)
└── test/         # configuración de Vitest + Testing Library
public/           # recursos estáticos
```

## Requisitos

- Node.js 20.19 o superior (el CI usa Node 22).
- Una copia de `.env.example` como `.env`:

```bash
cd frontend
cp .env.example .env    # VITE_API_URL=http://localhost:8000/api/v1
npm install
npm run dev             # http://localhost:5173
```

## Scripts

| Comando | Descripción |
| --- | --- |
| `npm run dev` | Servidor de desarrollo en `http://localhost:5173`. |
| `npm run build` | Verificación de tipos (`tsc -b`) y build de producción en `dist/`. |
| `npm run preview` | Sirve el build de producción en `http://localhost:4173`. |
| `npm run lint` | ESLint con TypeScript, React Hooks y Fast Refresh. |
| `npm run test` | Pruebas unitarias y de componentes con Vitest (una sola pasada). |
| `npm run test:watch` | Vitest en modo interactivo. |
| `npm run format` | Aplica Prettier a todo el workspace. |
| `npm run format:check` | Verifica el formato sin modificar archivos. |

## Configuración

- `VITE_API_URL` define la URL base de la API e incluye el prefijo `/api/v1`. Si no se
  define, el cliente usa `/api/v1` (útil detrás de un proxy inverso).
- `@/` es un alias de `src/` tanto en TypeScript como en Vite.
- El layout es responsive: barra inferior en móvil y menú lateral desde 1024 px. Se debe
  verificar a 360, 768 y 1280 px.

## Integración continua

`.github/workflows/ci.yml` ejecuta en cada push y en cada PR hacia `main` o `develop`:
`npm ci`, `npm run lint`, `npm run test` y `npm run build`. El job del backend se agregará
cuando T-01b deje disponible `backend/pyproject.toml`.

**Estado:** T-01c (base del frontend) y la parte de frontend de T-01d están implementadas.
Los módulos de `src/pages/` son marcadores de posición que se completan con sus historias.
