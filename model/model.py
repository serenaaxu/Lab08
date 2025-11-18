from database.impianto_DAO import ImpiantoDAO
'''
    MODELLO:
    - Rappresenta la struttura dati
    - Si occupa di gestire lo stato dell'applicazione
    - Interagisce con il database
'''

class Model:
    def __init__(self):
        self._impianti = None
        self.load_impianti()

        self.__sequenza_ottima = []
        self.__costo_ottimo = -1

    def load_impianti(self):
        """ Carica tutti gli impianti e li setta nella variabile self._impianti """
        self._impianti = ImpiantoDAO.get_impianti()

    def get_consumo_medio(self, mese:int):
        """
        Calcola, per ogni impianto, il consumo medio giornaliero per il mese selezionato.
        :param mese: Mese selezionato (un intero da 1 a 12)
        :return: lista di tuple --> (nome dell'impianto, media), es. (Impianto A, 123)
        """
        # TODO
        result = []
        if self._impianti is None:
            return []

        for impianto in self._impianti:
            # carica i consumi
            lista_consumi = impianto.get_consumi()
            # filtra consumi per il mese
            consumi_mese = [
                c.kwh for c in lista_consumi
                if c.data.month == mese
            ]

            # calcolo della media
            if consumi_mese:
                media = sum(consumi_mese) / len(consumi_mese)
            else:
                media = 0
            result.append((impianto.nome, media))
        return result


    def get_sequenza_ottima(self, mese:int):
        """
        Calcola la sequenza ottimale di interventi nei primi 7 giorni
        :return: sequenza di nomi impianto ottimale
        :return: costo ottimale (cioè quello minimizzato dalla sequenza scelta)
        """
        self.__sequenza_ottima = []
        self.__costo_ottimo = -1
        consumi_settimana = self.__get_consumi_prima_settimana_mese(mese)

        self.__ricorsione([], 1, None, 0, consumi_settimana)

        # Traduci gli ID in nomi
        id_to_nome = {impianto.id: impianto.nome for impianto in self._impianti}
        sequenza_nomi = [f"Giorno {giorno}: {id_to_nome[i]}" for giorno, i in enumerate(self.__sequenza_ottima, start=1)]
        return sequenza_nomi, self.__costo_ottimo

    def __ricorsione(self, sequenza_parziale, giorno, ultimo_impianto, costo_corrente, consumi_settimana):
        """ Implementa la ricorsione """
        # TODO
        # Caso terminale
        # se sta per iniziare il giorno 8 la settimana è terminata, non occorre continuare
        if giorno == 8:
            if self.__costo_ottimo == -1 or costo_corrente < self.__costo_ottimo:
                self.__costo_ottimo = costo_corrente
                self.__sequenza_ottima = sequenza_parziale.copy()
            return

        # se il costo corrente è già peggiore di quello ottimo inutile continuare
        if self.__costo_ottimo != -1 and costo_corrente >= self.__costo_ottimo:
            return

        # Caso ricorsivo
        # prova a visitare entrambi gli impianti
        for impianto in self._impianti:
            # calcolo costo spostamento
            costo_spostamento = 0
            if ultimo_impianto is not None and impianto.id != ultimo_impianto:
                costo_spostamento = 5
            # costo energetico
            costo_energia = consumi_settimana[impianto.id][giorno-1]

            costo_totale_scelta = costo_energia + costo_spostamento

            # aggiunge scelta al percorso
            sequenza_parziale.append(impianto.id)
            self.__ricorsione(
                sequenza_parziale,
                giorno + 1,                # passa alla giornata successiva
                impianto.id,               # ultimo impianto visitato
                costo_corrente + costo_totale_scelta,
                consumi_settimana
            )
            # rimuove la scelta per provare l'altro impianto
            sequenza_parziale.pop()


    def __get_consumi_prima_settimana_mese(self, mese: int):
        """
        Restituisce i consumi dei primi 7 giorni del mese selezionato per ciascun impianto.
        :return: un dizionario: {id_impianto: [kwh_giorno1, ..., kwh_giorno7]}
        """
        # TODO
        dati_settimana = {}

        if not self._impianti:
            return {}

        for impianto in self._impianti:
            lista_consumi = impianto.get_consumi()

            # filtra consumi per mese e giorno
            consumi_validi = []
            for c in lista_consumi:
                if c.data.month == mese and 1 <= c.data.day <= 7:
                    consumi_validi.append(c)

            # ordina per giorno
            consumi_ordinati = sorted(consumi_validi, key=lambda c: c.data.day)

            # estrae solo i kwh
            lista_kwh = [c.kwh for c in consumi_ordinati]

            dati_settimana[impianto.id] = lista_kwh
        return dati_settimana



