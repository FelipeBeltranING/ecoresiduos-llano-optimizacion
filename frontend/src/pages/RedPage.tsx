import { Network } from "lucide-react";

import { ModulePlaceholder } from "@/components/ui/ModulePlaceholder";

export function RedPage() {
  return (
    <ModulePlaceholder
      title="Red logística"
      description="Empresas agropecuarias, plantas de procesamiento y centros de acopio que conforman la red de EcoResiduos del Llano."
      icon={Network}
      issues={["HU-01", "HU-02", "HU-17"]}
      upcoming={[
        "CRUD de empresas con municipio, residuo, oferta y coordenadas",
        "Plantas con capacidad semanal y costo de operación",
        "Centros de acopio como nodos de paso",
        "Mapa interactivo y filtros por estado",
        "Validación de códigos, ofertas y coordenadas",
        "Exportación de la red en CSV y Excel",
      ]}
    />
  );
}
