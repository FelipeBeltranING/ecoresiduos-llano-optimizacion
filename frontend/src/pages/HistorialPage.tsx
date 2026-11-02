import { History } from "lucide-react";

import { ModulePlaceholder } from "@/components/ui/ModulePlaceholder";

export function HistorialPage() {
  return (
    <ModulePlaceholder
      title="Historial y reportes"
      description="Consulta de ejecuciones anteriores, escenarios guardados y exportación de resultados en PDF y Excel."
      icon={History}
      issues={["HU-15", "HU-16"]}
      upcoming={[
        "Listado de ejecuciones con fecha y método",
        "Detalle de parámetros y resultados por ejecución",
        "Filtros por sprint, método y estado",
        "Exportación de reportes en PDF",
        "Exportación de resultados en Excel",
        "Comparación de ejecuciones históricas",
      ]}
    />
  );
}
