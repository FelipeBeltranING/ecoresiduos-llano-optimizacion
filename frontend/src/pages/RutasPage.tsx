import { Route as RouteIcon } from "lucide-react";

import { ModulePlaceholder } from "@/components/ui/ModulePlaceholder";

export function RutasPage() {
  return (
    <ModulePlaceholder
      title="Rutas y costos"
      description="Matriz editable de distancias entre empresas y plantas, con cálculo automático del costo unitario de transporte."
      icon={RouteIcon}
      issues={["HU-03"]}
      upcoming={[
        "Grilla editable con columna fija en móvil",
        "Cálculo de costo por tonelada-kilómetro",
        "Rutas habilitadas y deshabilitadas",
        "Generación automática de rutas faltantes",
        "Validación de distancias mayores que cero",
        "Actualización por lote y recálculo de la matriz",
      ]}
    />
  );
}
