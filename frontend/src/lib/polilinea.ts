
export function decodificarPolilinea(texto: string, precision = 5): [number, number][] {
  const factor = 10 ** precision;
  const puntos: [number, number][] = [];
  let indice = 0;
  let lat = 0;
  let lon = 0;

  const leerValor = () => {
    let resultado = 0;
    let desplazamiento = 0;
    let byte: number;
    do {
      byte = texto.charCodeAt(indice++) - 63;
      resultado |= (byte & 0x1f) << desplazamiento;
      desplazamiento += 5;
    } while (byte >= 0x20);
    return resultado & 1 ? ~(resultado >> 1) : resultado >> 1;
  };

  while (indice < texto.length) {
    lat += leerValor();
    lon += leerValor();
    puntos.push([lat / factor, lon / factor]);
  }
  return puntos;
}
