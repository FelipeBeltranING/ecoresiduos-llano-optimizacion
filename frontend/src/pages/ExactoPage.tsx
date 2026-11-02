import { Gauge } from "lucide-react";

import { ModulePlaceholder } from "@/components/ui/ModulePlaceholder";

export function ExactoPage() {
  return (
    <ModulePlaceholder
      title="Modelo exacto"
      description="Resolución del modelo de transporte con programación lineal entera y análisis de la solución óptima de la red."
      icon={Gauge}
      issues={["HU-07", "HU-08"]}
      upcoming={[
        "Ejecución del solver PuLP + CBC",
        "Costo total mínimo y estado de la solución",
        "Flujos óptimos empresa → planta",
        "Visualización de la red y de los flujos",
        "Holguras y uso de la capacidad instalada",
        "Descarga del resultado de la ejecución",
      ]}
    />
  );
}
