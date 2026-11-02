import { FlaskConical } from "lucide-react";

import { ModulePlaceholder } from "@/components/ui/ModulePlaceholder";

export function SensibilidadPage() {
  return (
    <ModulePlaceholder
      title="Análisis de sensibilidad"
      description="Simulación de escenarios de demanda, capacidad y costos, junto con los precios sombra y rangos de estabilidad del modelo."
      icon={FlaskConical}
      issues={["HU-11", "HU-12"]}
      upcoming={[
        "Escenarios con variaciones de demanda y capacidad",
        "Variación del costo de transporte y de la tarifa",
        "Precios sombra y costos reducidos",
        "Rangos de estabilidad de los coeficientes",
        "Comparación de escenarios en una tabla",
        "Gráficas de sensibilidad por parámetro",
      ]}
    />
  );
}
