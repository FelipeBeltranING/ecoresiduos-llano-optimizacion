import { Sprout } from "lucide-react";

import { ModulePlaceholder } from "@/components/ui/ModulePlaceholder";

export function GeneticoPage() {
  return (
    <ModulePlaceholder
      title="Algoritmo genético"
      description="Configuración y ejecución de la metaheurística para encontrar soluciones de alta calidad en instancias grandes."
      icon={Sprout}
      issues={["HU-09", "HU-10"]}
      upcoming={[
        "Parámetros de población, generaciones, cruce y mutación",
        "Ejecución asíncrona y estado del progreso",
        "Curva de convergencia del mejor individuo",
        "Comparación de la mejor solución con el óptimo",
        "Restricciones de capacidad y reparación de individuos",
        "Historial de ejecuciones del algoritmo",
      ]}
    />
  );
}
