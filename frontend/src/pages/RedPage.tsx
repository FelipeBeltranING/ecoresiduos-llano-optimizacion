import { Download, Plus, Power, Upload } from "lucide-react";
import { useRef, useState, type FormEvent } from "react";

import {
  URL_EXPORTAR_RED,
  useActualizarNodo,
  useCrearNodo,
  useDesactivarNodo,
  useFuentesCasoReal,
  useImportarRed,
  useMatriz,
  useNodos,
} from "@/api/hooks";
import type { Nodo, NodoEntrada, TipoNodo } from "@/api/tipos";
import { MapaReal } from "@/components/mapa/MapaReal";
import { Boton } from "@/components/ui/Boton";
import { Campo } from "@/components/ui/Campo";
import { Cargando, ErrorApi, Vacio } from "@/components/ui/Estado";
import { Etiqueta } from "@/components/ui/Etiqueta";
import { PageBody, PageHero } from "@/components/ui/PageHero";
import { Segmentado } from "@/components/ui/Segmentado";
import { Tarjeta } from "@/components/ui/Tarjeta";
import { formatCurrency, formatNumber, formatPercent } from "@/lib/format";
import { activos, descargar } from "@/lib/red";

const pestanas = [
  { label: "Empresas", value: "FUENTE" },
  { label: "Plantas", value: "PLANTA" },
  { label: "Centros de acopio", value: "ACOPIO" },
];

const vacio = {
  codigo: "",
  nombre: "",
  municipio: "",
  tipo_residuo: "",
  cantidad: "",
  costo_operacion_t: "",
  latitud: "",
  longitud: "",
};

const numero = (texto: string) => Number(texto.replace(",", "."));

function FilaNodo({ nodo }: { nodo: Nodo }) {
  const actualizar = useActualizarNodo();
  const desactivar = useDesactivarNodo();
  const esFuente = nodo.tipo === "FUENTE";
  const actual = esFuente ? nodo.oferta_t : nodo.capacidad_t;
  const [valor, setValor] = useState(String(actual ?? ""));

  const guardar = () => {
    const nuevo = numero(valor);
    if (!Number.isFinite(nuevo) || nuevo === actual) return;
    actualizar.mutate({
      codigo: nodo.codigo,
      cambios: esFuente ? { oferta_t: nuevo } : { capacidad_t: nuevo },
    });
  };

  return (
    <tr className={nodo.activo ? "" : "opacity-50"}>
      <td className="font-semibold text-text">{nodo.codigo}</td>
      <td>
        <span className="text-text">{nodo.nombre}</span>
        <span className="block text-xs text-muted">
          {nodo.municipio}
          {nodo.tipo_residuo ? ` · ${nodo.tipo_residuo}` : ""}
        </span>
      </td>
      <td className="text-right">
        <input
          aria-label={`${esFuente ? "Oferta" : "Capacidad"} de ${nodo.codigo}`}
          className="h-8 w-24 rounded-control border border-border bg-surface px-2 text-right text-sm tabular-nums focus:border-primary"
          value={valor}
          onChange={(e) => setValor(e.target.value)}
          onBlur={guardar}
          onKeyDown={(e) => e.key === "Enter" && guardar()}
          disabled={!nodo.activo}
        />
      </td>
      {!esFuente ? (
        <td className="text-right tabular-nums">{formatCurrency(nodo.costo_operacion_t)}</td>
      ) : null}
      <td className="text-right">
        {nodo.activo ? (
          <Boton
            variante="fantasma"
            aria-label={`Desactivar ${nodo.codigo}`}
            icono={<Power className="size-4" aria-hidden="true" />}
            onClick={() => desactivar.mutate(nodo.codigo)}
          >
            <span className="hidden xl:inline">Desactivar</span>
          </Boton>
        ) : (
          <Boton
            variante="fantasma"
            onClick={() => actualizar.mutate({ codigo: nodo.codigo, cambios: { activo: true } })}
          >
            Activar
          </Boton>
        )}
      </td>
    </tr>
  );
}

export function RedPage() {
  const nodos = useNodos();
  const matriz = useMatriz();
  const crear = useCrearNodo();
  const importar = useImportarRed();
  const fuentes = useFuentesCasoReal();
  const [tipo, setTipo] = useState<TipoNodo>("FUENTE");
  const [form, setForm] = useState(vacio);
  const [mostrarInactivos, setMostrarInactivos] = useState(false);
  const archivo = useRef<HTMLInputElement>(null);

  const nodosActivos = activos(nodos.data);
  const lista = (nodos.data ?? []).filter((n) => n.tipo === tipo && (mostrarInactivos || n.activo));
  const empresas = nodosActivos.filter((n) => n.tipo === "FUENTE");
  const plantas = nodosActivos.filter((n) => n.tipo === "PLANTA");
  const oferta = empresas.reduce((s, n) => s + (n.oferta_t ?? 0), 0);
  const capacidad = plantas.reduce((s, n) => s + (n.capacidad_t ?? 0), 0);
  const esCasoReal = empresas.some((e) => e.codigo.startsWith("R"));
  const esFuente = tipo === "FUENTE";

  const cambiar = (campo: keyof typeof vacio) => (e: { target: { value: string } }) =>
    setForm((f) => ({ ...f, [campo]: e.target.value }));

  const enviar = (evento: FormEvent) => {
    evento.preventDefault();
    const cantidad = numero(form.cantidad);
    const entrada: NodoEntrada = {
      codigo: form.codigo.trim().toUpperCase(),
      tipo,
      nombre: form.nombre.trim(),
      municipio: form.municipio.trim(),
      tipo_residuo: esFuente ? form.tipo_residuo.trim() || null : null,
      oferta_t: esFuente ? cantidad : null,
      capacidad_t: esFuente ? null : cantidad,
      costo_operacion_t: esFuente ? 0 : numero(form.costo_operacion_t || "0"),
      latitud: numero(form.latitud),
      longitud: numero(form.longitud),
    };
    crear.mutate(entrada, { onSuccess: () => setForm(vacio) });
  };

  const punto =
    form.latitud && form.longitud
      ? ([numero(form.latitud), numero(form.longitud)] as [number, number])
      : null;

  return (
    <>
      <PageHero
        eyebrow="Red logística · HU-01 · HU-02 · HU-05 · HU-18 · HU-19"
        title="Empresas aliadas"
        description={
          esCasoReal
            ? "Caso real: producción EVA 2018 (MinAgricultura), inventario bovino ICA/FNG 2025, coordenadas DIVIPOLA (DANE) y rutas OSRM sobre OpenStreetMap"
            : "Registre, edite o desactive empresas, plantas y centros de acopio; la red crece sin tocar el código"
        }
        kpis={[
          { valor: String(empresas.length), etiqueta: "Empresas activas" },
          { valor: `${formatNumber(oferta)} t`, etiqueta: "Oferta semanal" },
          {
            valor: `${formatNumber(capacidad)} t`,
            etiqueta: "Capacidad de plantas",
            tono: oferta > capacidad ? "peligro" : "claro",
          },
        ]}
        actions={
          <>
            <Boton
              variante="acento"
              icono={<Download className="size-4" aria-hidden="true" />}
              onClick={() => descargar(URL_EXPORTAR_RED)}
            >
              Exportar Excel
            </Boton>
            <Boton
              variante="acento"
              icono={<Upload className="size-4" aria-hidden="true" />}
              onClick={() => archivo.current?.click()}
              disabled={importar.isPending}
            >
              Importar Excel
            </Boton>
            <input
              ref={archivo}
              type="file"
              accept=".xlsx"
              className="hidden"
              aria-label="Archivo Excel de la red"
              onChange={(e) => {
                const elegido = e.target.files?.[0];
                if (elegido) importar.mutate(elegido);
                e.target.value = "";
              }}
            />
          </>
        }
      />

      <PageBody>
        {importar.data ? (
          <Tarjeta className="mb-4">
            {importar.data.importado ? (
              <Etiqueta>
                Importado: {importar.data.empresas} empresas, {importar.data.plantas} plantas,{" "}
                {importar.data.rutas} rutas
              </Etiqueta>
            ) : (
              <>
                <p className="type-cuerpo-strong text-danger">
                  No se importó nada: corrija estas filas y vuelva a intentar
                </p>
                <ul className="mt-2 space-y-1 text-sm">
                  {importar.data.errores.map((error) => (
                    <li key={`${error.hoja}-${error.fila}-${error.mensaje}`}>
                      <strong>
                        {error.hoja}, fila {error.fila}:
                      </strong>{" "}
                      {error.mensaje}
                    </li>
                  ))}
                </ul>
              </>
            )}
          </Tarjeta>
        ) : null}
        {importar.isError ? <ErrorApi error={importar.error} /> : null}

        <div className="grid gap-4 xl:grid-cols-[minmax(0,1.1fr)_minmax(0,1fr)]">
          <Tarjeta relleno="none" className="min-w-0 overflow-hidden">
            <div className="flex flex-wrap items-center justify-between gap-3 px-5 pt-5">
              <Segmentado
                items={pestanas}
                value={tipo}
                onChange={(v) => setTipo(v as TipoNodo)}
                ariaLabel="Tipo de nodo"
              />
              <label className="flex items-center gap-2 text-xs text-muted">
                <input
                  type="checkbox"
                  checked={mostrarInactivos}
                  onChange={(e) => setMostrarInactivos(e.target.checked)}
                />
                Ver inactivos
              </label>
            </div>
            <div className="mt-4 overflow-x-auto scroll-fino">
              {nodos.isLoading ? (
                <div className="px-5 pb-5">
                  <Cargando />
                </div>
              ) : nodos.isError ? (
                <div className="px-5 pb-5">
                  <ErrorApi error={nodos.error} />
                </div>
              ) : lista.length ? (
                <table className="tabla tabla--compacta min-w-[560px]">
                  <thead>
                    <tr>
                      <th className="w-16">Código</th>
                      <th>Nombre</th>
                      <th className="w-32 text-right">
                        {esFuente ? "Oferta (t)" : "Capacidad (t)"}
                      </th>
                      {!esFuente ? <th className="w-32 text-right">Operación/t</th> : null}
                      <th className="w-24 text-right">Estado</th>
                    </tr>
                  </thead>
                  <tbody>
                    {lista.map((nodo) => (
                      <FilaNodo
                        key={`${nodo.codigo}-${nodo.oferta_t}-${nodo.capacidad_t}`}
                        nodo={nodo}
                      />
                    ))}
                  </tbody>
                </table>
              ) : (
                <div className="px-5 pb-5">
                  <Vacio>No hay nodos de este tipo.</Vacio>
                </div>
              )}
            </div>
          </Tarjeta>

          <Tarjeta>
            <h2 className="type-title-15 text-text">Mapa real de la red</h2>
            <p className="mt-1 text-xs text-muted">
              Clic en el mapa para ubicar el nodo nuevo. Trazados viales de OSRM.
            </p>
            <div className="mt-3">
              <MapaReal
                nodos={nodosActivos}
                rutas={matriz.data?.rutas}
                mostrarRutas
                alto="h-[380px]"
                puntoNuevo={punto}
                onClicMapa={(lat, lon) =>
                  setForm((f) => ({ ...f, latitud: lat.toFixed(5), longitud: lon.toFixed(5) }))
                }
              />
            </div>
          </Tarjeta>
        </div>

        <Tarjeta className="mt-4">
          <h2 className="type-title-18 text-text">
            Agregar {esFuente ? "empresa" : tipo === "PLANTA" ? "planta" : "centro de acopio"}
          </h2>
          <p className="mt-1 text-xs text-muted">
            Las rutas hacia (o desde) los demás nodos se crean solas con la distancia vial real
            (OSRM) o, sin conexión, con Haversine × 1,3.
          </p>
          <form className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-4" onSubmit={enviar}>
            <Campo
              etiqueta="Código"
              value={form.codigo}
              onChange={cambiar("codigo")}
              required
              maxLength={10}
              placeholder="E11"
            />
            <Campo etiqueta="Nombre" value={form.nombre} onChange={cambiar("nombre")} required />
            <Campo
              etiqueta="Municipio"
              value={form.municipio}
              onChange={cambiar("municipio")}
              required
            />
            {esFuente ? (
              <Campo
                etiqueta="Tipo de residuo"
                value={form.tipo_residuo}
                onChange={cambiar("tipo_residuo")}
              />
            ) : (
              <Campo
                etiqueta="Costo de operación (COP/t)"
                value={form.costo_operacion_t}
                onChange={cambiar("costo_operacion_t")}
                inputMode="decimal"
              />
            )}
            <Campo
              etiqueta={esFuente ? "Oferta (t/semana)" : "Capacidad (t/semana)"}
              value={form.cantidad}
              onChange={cambiar("cantidad")}
              required
              inputMode="decimal"
            />
            <Campo
              etiqueta="Latitud"
              value={form.latitud}
              onChange={cambiar("latitud")}
              required
              inputMode="decimal"
            />
            <Campo
              etiqueta="Longitud"
              value={form.longitud}
              onChange={cambiar("longitud")}
              required
              inputMode="decimal"
            />
            <div className="flex items-end">
              <Boton
                type="submit"
                disabled={crear.isPending}
                icono={<Plus className="size-4" aria-hidden="true" />}
              >
                {crear.isPending ? "Guardando…" : "Agregar"}
              </Boton>
            </div>
          </form>
          {crear.isError ? (
            <div className="mt-3">
              <ErrorApi error={crear.error} />
            </div>
          ) : null}
        </Tarjeta>

        {esCasoReal && fuentes.data ? (
          <Tarjeta relleno="none" className="mt-4 overflow-hidden">
            <div className="px-5 pt-5">
              <h2 className="type-title-18 text-text">Origen de los datos del caso real</h2>
              <p className="mt-1 text-xs text-muted">{fuentes.data.descripcion}</p>
            </div>
            <div className="mt-4 overflow-x-auto scroll-fino">
              <table className="tabla tabla--compacta min-w-[640px]">
                <thead>
                  <tr>
                    <th>Código</th>
                    <th>Municipio</th>
                    <th className="text-right">Producción</th>
                    <th>Unidad (fuente)</th>
                    <th className="text-right">Residuo anual (t)</th>
                    <th className="text-right">Captación</th>
                  </tr>
                </thead>
                <tbody>
                  {fuentes.data.empresas.map((e) => (
                    <tr key={e.codigo}>
                      <td className="font-semibold">{e.codigo}</td>
                      <td>{e.municipio}</td>
                      <td className="text-right tabular-nums">{formatNumber(e.produccion)}</td>
                      <td className="text-xs text-muted">{e.unidad}</td>
                      <td className="text-right tabular-nums">{formatNumber(e.residuo_anual_t)}</td>
                      <td className="text-right tabular-nums">{formatPercent(e.captacion, 1)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Tarjeta>
        ) : null}
      </PageBody>
    </>
  );
}
