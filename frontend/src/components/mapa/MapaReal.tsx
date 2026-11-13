import "leaflet/dist/leaflet.css";

import type { LatLngBoundsExpression, LatLngExpression } from "leaflet";
import { useEffect, useMemo } from "react";
import {
  CircleMarker,
  MapContainer,
  Polyline,
  TileLayer,
  Tooltip,
  useMap,
  useMapEvents,
} from "react-leaflet";

import type { Flujo, Nodo, Ruta } from "@/api/tipos";
import { decodificarPolilinea } from "@/lib/polilinea";
import { formatCurrency, formatNumber } from "@/lib/format";

export interface UsoPlanta {
  uso: number;
  capacidad: number;
}

interface MapaRealProps {
  nodos: Nodo[];
  rutas?: Ruta[];
  flujos?: Flujo[];
  usoPlantas?: Record<string, UsoPlanta>;
  
  mostrarRutas?: boolean;
  alto?: string;
  etiqueta?: string;
  onSeleccionarNodo?: (codigo: string) => void;
  
  onClicMapa?: (latitud: number, longitud: number) => void;
  
  puntoNuevo?: [number, number] | null;
}

function EscucharClic({ onClic }: { onClic: (lat: number, lon: number) => void }) {
  useMapEvents({ click: (evento) => onClic(evento.latlng.lat, evento.latlng.lng) });
  return null;
}

const COLOR_EMPRESA = "#B7791F";
const COLOR_PLANTA = "#1F7A4D";
const COLOR_SATURADA = "#C2410C";
const COLOR_ACOPIO = "#2563EB";
const COLOR_FLUJO = "#12392A";
const CENTRO_META: LatLngExpression = [3.9, -73.2];

function AjustarVista({ limites }: { limites: LatLngBoundsExpression | null }) {
  const mapa = useMap();
  useEffect(() => {
    if (limites) mapa.fitBounds(limites, { padding: [28, 28] });
  }, [mapa, limites]);
  return null;
}

function trazado(ruta: Ruta | undefined, origen: Nodo, destino: Nodo): LatLngExpression[] {
  if (ruta?.geometria) {
    const puntos = decodificarPolilinea(ruta.geometria);
    if (puntos.length > 1) return puntos;
  }
  return [
    [origen.latitud, origen.longitud],
    [destino.latitud, destino.longitud],
  ];
}


export function MapaReal({
  nodos,
  rutas = [],
  flujos = [],
  usoPlantas = {},
  mostrarRutas = false,
  alto = "h-[420px]",
  etiqueta = "Mapa de la red logística sobre OpenStreetMap",
  onSeleccionarNodo,
  onClicMapa,
  puntoNuevo,
}: MapaRealProps) {
  const porCodigo = useMemo(() => new Map(nodos.map((n) => [n.codigo, n])), [nodos]);
  const porRuta = useMemo(
    () => new Map(rutas.map((r) => [`${r.origen}->${r.destino}`, r])),
    [rutas],
  );

  const limites = useMemo<LatLngBoundsExpression | null>(() => {
    if (nodos.length === 0) return null;
    return nodos.map((n) => [n.latitud, n.longitud] as [number, number]);
  }, [nodos]);

  const maximo = Math.max(1, ...flujos.map((f) => f.toneladas));
  const ancho = (toneladas: number) => 2 + (toneladas / maximo) * 8;

  return (
    <div className={["relative w-full overflow-hidden rounded-card", alto].join(" ")}>
      <MapContainer
        center={CENTRO_META}
        zoom={8}
        scrollWheelZoom={false}
        className="h-full w-full"
        aria-label={etiqueta}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> · rutas <a href="https://project-osrm.org">OSRM</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <AjustarVista limites={limites} />
        {onClicMapa ? <EscucharClic onClic={onClicMapa} /> : null}
        {puntoNuevo ? (
          <CircleMarker
            center={puntoNuevo}
            radius={9}
            pathOptions={{ color: COLOR_ACOPIO, weight: 3, fillOpacity: 0.2, dashArray: "3 3" }}
          >
            <Tooltip permanent direction="top" offset={[0, -8]}>
              Nuevo nodo
            </Tooltip>
          </CircleMarker>
        ) : null}

        {mostrarRutas
          ? rutas
              .filter((r) => r.habilitada)
              .map((ruta) => {
                const origen = porCodigo.get(ruta.origen);
                const destino = porCodigo.get(ruta.destino);
                if (!origen || !destino) return null;
                return (
                  <Polyline
                    key={`ruta-${ruta.origen}-${ruta.destino}`}
                    positions={trazado(ruta, origen, destino)}
                    pathOptions={{ color: "#5B6B62", weight: 1.5, opacity: 0.35, dashArray: "4 4" }}
                  />
                );
              })
          : null}

        {flujos.map((flujo) => {
          const origen = porCodigo.get(flujo.origen);
          const destino = porCodigo.get(flujo.destino);
          if (!origen || !destino) return null;
          const ruta = porRuta.get(`${flujo.origen}->${flujo.destino}`);
          return (
            <Polyline
              key={`flujo-${flujo.origen}-${flujo.destino}`}
              positions={trazado(ruta, origen, destino)}
              pathOptions={{ color: COLOR_FLUJO, weight: ancho(flujo.toneladas), opacity: 0.75 }}
            >
              <Tooltip sticky>
                <strong>
                  {flujo.origen} → {flujo.destino}
                </strong>
                <br />
                {formatNumber(flujo.toneladas)} t/semana · {formatCurrency(flujo.costo_unitario)}/t
                {ruta?.distancia_km ? (
                  <>
                    <br />
                    {formatNumber(ruta.distancia_km)} km
                    {ruta.duracion_min ? ` · ${formatNumber(ruta.duracion_min)} min` : ""}
                  </>
                ) : null}
              </Tooltip>
            </Polyline>
          );
        })}

        {nodos.map((nodo) => {
          const esPlanta = nodo.tipo === "PLANTA";
          const uso = usoPlantas[nodo.codigo];
          const saturada = esPlanta && uso && uso.uso >= uso.capacidad - 1e-6;
          const color =
            nodo.tipo === "FUENTE"
              ? COLOR_EMPRESA
              : nodo.tipo === "ACOPIO"
                ? COLOR_ACOPIO
                : saturada
                  ? COLOR_SATURADA
                  : COLOR_PLANTA;
          return (
            <CircleMarker
              key={nodo.codigo}
              center={[nodo.latitud, nodo.longitud]}
              radius={esPlanta ? 11 : 7}
              pathOptions={{
                color: "#ffffff",
                weight: 2,
                fillColor: color,
                fillOpacity: 0.95,
              }}
              eventHandlers={
                onSeleccionarNodo ? { click: () => onSeleccionarNodo(nodo.codigo) } : undefined
              }
            >
              <Tooltip direction="top" offset={[0, -8]}>
                <strong>
                  {nodo.codigo} · {nodo.nombre}
                </strong>
                <br />
                {nodo.municipio}
                <br />
                {nodo.tipo === "FUENTE"
                  ? `Oferta ${formatNumber(nodo.oferta_t ?? 0)} t/semana`
                  : `Capacidad ${formatNumber(nodo.capacidad_t ?? 0)} t/semana`}
                {uso ? ` · uso ${formatNumber(uso.uso)} t` : ""}
              </Tooltip>
            </CircleMarker>
          );
        })}
      </MapContainer>

      <div className="pointer-events-none absolute bottom-2 left-2 z-[500] flex flex-wrap gap-3 rounded-control bg-white/90 px-3 py-1.5 text-[11px] font-medium text-text shadow-card">
        <span className="flex items-center gap-1">
          <span className="size-2.5 rounded-full" style={{ background: COLOR_EMPRESA }} /> Empresa
        </span>
        <span className="flex items-center gap-1">
          <span className="size-3 rounded-full" style={{ background: COLOR_PLANTA }} /> Planta
        </span>
        <span className="flex items-center gap-1">
          <span className="size-3 rounded-full" style={{ background: COLOR_SATURADA }} /> Saturada
        </span>
        {flujos.length ? (
          <span className="flex items-center gap-1">
            <span className="h-1 w-4 rounded" style={{ background: COLOR_FLUJO }} /> Flujo (t)
          </span>
        ) : null}
      </div>
    </div>
  );
}
