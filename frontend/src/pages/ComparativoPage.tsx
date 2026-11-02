import { GitCompareArrows } from "lucide-react";

import { ModulePlaceholder } from "@/components/ui/ModulePlaceholder";

export function ComparativoPage() {
  return (
    <ModulePlaceholder
      title="Comparativo exacto vs. AG"
      description="Reporte comparativo entre la solución exacta y la metaheurística, con brecha, tiempos y comportamiento por tamaño de instancia."
      icon={GitCompareArrows}
      issues={["HU-13", "HU-14"]}
      upcoming={[
        "Tabla comparativa de costo, tiempo y brecha",
        "Cálculo del gap porcentual entre métodos",
        "Pruebas de escalabilidad por número de nodos",
        "Gráficas de tiempo y calidad de la solución",
        "Exportación del reporte comparativo",
        "Conclusión automática sobre el método recomendado",
      ]}
    />
  );
}
