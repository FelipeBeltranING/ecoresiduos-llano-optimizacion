export interface Empresa {
  codigo: string;
  nombre: string;
  municipio: string;
  residuo: string;
  oferta: number;
}

export interface Planta {
  codigo: "P01" | "P02" | "P03" | "P04";
  nombre: string;
  capacidad: number;
  operacion: number;
  saturada: boolean;
  uso: number;
  precioSombra: number;
  costoTotal: number;
  porcentajeCosto: number;
}

export interface Flujo {
  empresa: string;
  planta: Planta["codigo"];
  toneladas: number;
  costo: number;
}

export const empresas: Empresa[] = [
  {
    codigo: "E01",
    nombre: "Palmas del Upía",
    municipio: "Barranca de Upía",
    residuo: "Palma (raquis, fibra)",
    oferta: 120,
  },
  {
    codigo: "E02",
    nombre: "Arrocera Llano Verde",
    municipio: "Puerto López",
    residuo: "Arroz (cascarilla)",
    oferta: 95,
  },
  {
    codigo: "E03",
    nombre: "Ganadería San Martín",
    municipio: "San Martín",
    residuo: "Ganadería (estiércol)",
    oferta: 80,
  },
  {
    codigo: "E04",
    nombre: "Agroindustrial Guaroa",
    municipio: "San Carlos de Guaroa",
    residuo: "Palma (raquis, fibra)",
    oferta: 140,
  },
  {
    codigo: "E05",
    nombre: "Molino Acacías",
    municipio: "Acacías",
    residuo: "Arroz (cascarilla)",
    oferta: 70,
  },
  {
    codigo: "E06",
    nombre: "Hacienda Cumural",
    municipio: "Cumural",
    residuo: "Ganadería (estiércol)",
    oferta: 60,
  },
  {
    codigo: "E07",
    nombre: "Forestal Cabuyaro",
    municipio: "Cabuyaro",
    residuo: "Forestal (aserrín, corteza)",
    oferta: 85,
  },
  {
    codigo: "E08",
    nombre: "Agrícola Castilla",
    municipio: "Castilla La Nueva",
    residuo: "Arroz (cascarilla)",
    oferta: 75,
  },
  {
    codigo: "E09",
    nombre: "Palmares Fuente de Oro",
    municipio: "Fuente de Oro",
    residuo: "Palma (raquis, fibra)",
    oferta: 110,
  },
  {
    codigo: "E10",
    nombre: "Agropecuaria Lejanías",
    municipio: "Lejanías",
    residuo: "Ganadería y cacao",
    oferta: 55,
  },
];

export const plantas: Planta[] = [
  {
    codigo: "P01",
    nombre: "Villavicencio",
    capacidad: 300,
    operacion: 45_000,
    saturada: true,
    uso: 300,
    precioSombra: -17_750,
    costoTotal: 20_407_250,
    porcentajeCosto: 31.5,
  },
  {
    codigo: "P02",
    nombre: "Restrepo",
    capacidad: 180,
    operacion: 52_000,
    saturada: true,
    uso: 180,
    precioSombra: -14_250,
    costoTotal: 13_854_000,
    porcentajeCosto: 21.4,
  },
  {
    codigo: "P03",
    nombre: "Granada",
    capacidad: 250,
    operacion: 48_000,
    saturada: false,
    uso: 245,
    precioSombra: 0,
    costoTotal: 16_418_500,
    porcentajeCosto: 25.4,
  },
  {
    codigo: "P04",
    nombre: "Puerto Gaitán",
    capacidad: 220,
    operacion: 40_000,
    saturada: false,
    uso: 165,
    precioSombra: 0,
    costoTotal: 14_011_250,
    porcentajeCosto: 21.7,
  },
];

export const flujos: Flujo[] = [
  { empresa: "E01", planta: "P02", toneladas: 120, costo: 86_300 },
  { empresa: "E02", planta: "P04", toneladas: 95, costo: 76_750 },
  { empresa: "E03", planta: "P03", toneladas: 80, costo: 86_500 },
  { empresa: "E04", planta: "P01", toneladas: 140, costo: 76_500 },
  { empresa: "E05", planta: "P01", toneladas: 70, costo: 54_800 },
  { empresa: "E06", planta: "P02", toneladas: 60, costo: 58_300 },
  { empresa: "E07", planta: "P01", toneladas: 15, costo: 78_250 },
  { empresa: "E07", planta: "P04", toneladas: 70, costo: 96_000 },
  { empresa: "E08", planta: "P01", toneladas: 75, costo: 62_500 },
  { empresa: "E09", planta: "P03", toneladas: 110, costo: 55_700 },
  { empresa: "E10", planta: "P03", toneladas: 55, costo: 61_300 },
];

/** Matriz de costos unitarios en COP por tonelada (empresa → planta). */
export const costos: Record<string, Record<Planta["codigo"], number>> = {
  E01: { P01: 83_500, P02: 86_300, P03: 149_500, P04: 145_000 },
  E02: { P01: 74_750, P02: 86_300, P03: 126_750, P04: 76_750 },
  E03: { P01: 69_500, P02: 81_750, P03: 86_500, P04: 129_250 },
  E04: { P01: 76_500, P02: 88_050, P03: 97_000, P04: 104_750 },
  E05: { P01: 54_800, P02: 67_050, P03: 101_200, P04: 116_300 },
  E06: { P01: 55_500, P02: 58_300, P03: 121_500, P04: 117_000 },
  E07: { P01: 78_250, P02: 81_750, P03: 142_500, P04: 96_000 },
  E08: { P01: 62_500, P02: 74_750, P03: 97_000, P04: 120_500 },
  E09: { P01: 101_000, P02: 113_250, P03: 55_700, P04: 159_000 },
  E10: { P01: 118_500, P02: 130_750, P03: 61_300, P04: 180_000 },
};

export const totalOferta = empresas.reduce((total, empresa) => total + empresa.oferta, 0);

export const totalCapacidad = plantas.reduce((total, planta) => total + planta.capacidad, 0);

export const costoOptimo = 64_691_000;

/** Distancia implícita (km) de cada ruta: c = k · d + costo de operación, con k = 350. */
export const distancia = (costo: number, operacion: number) => Math.round((costo - operacion) / 350);

export const flujoDe = (empresa: string, planta: Planta["codigo"]) =>
  flujos.find((flujo) => flujo.empresa === empresa && flujo.planta === planta);
