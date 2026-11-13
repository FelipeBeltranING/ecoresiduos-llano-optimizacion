import numpy as np


def verificar_balanceo(oferta, demanda):
    oferta = np.array(oferta, dtype=float)
    demanda = np.array(demanda, dtype=float)

    suma_oferta = oferta.sum()
    suma_demanda = demanda.sum()

    if np.isclose(suma_oferta, suma_demanda):
        print(f"✔ El problema está BALANCEADO (oferta = demanda = {suma_oferta}).")
        return True, oferta, demanda

    if suma_oferta > suma_demanda:
        diferencia = suma_oferta - suma_demanda
        print(f"✘ Problema DESBALANCEADO. Se agrega un DESTINO ficticio "
              f"con demanda {diferencia} y costo 0.")
        demanda = np.append(demanda, diferencia)
    else:
        diferencia = suma_demanda - suma_oferta
        print(f"✘ Problema DESBALANCEADO. Se agrega un ORIGEN ficticio "
              f"con oferta {diferencia} y costo 0.")
        oferta = np.append(oferta, diferencia)

    return False, oferta, demanda
