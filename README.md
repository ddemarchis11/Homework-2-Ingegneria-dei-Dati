# Avvio dell’applicazione con Elasticsearch e Streamlit

Questo progetto utilizza **Elasticsearch** e una **interfaccia utente Streamlit**.  
Per semplificare l’avvio di tutto l’ambiente, è stato fornito lo script `run_app.sh`.

## Requisiti

- **Docker** installato e configurato  
- **Python + Streamlit** installati  
- Permessi di esecuzione sullo script:

  ```bash
                   chmod +x run_app.sh

## Esecuzione
Lo script run_app.sh eseguirà tutto in automatico: avvio di Docker, Elastic Search e UI Streamlit, così si può lavorare direttamente su questa. 
Nota: è un programma .sh quindi bisogna fare generalmente attenzione, tuttavia il codice è aperto e visibile.

Altrimenti si può procedere come segue:
- avviare Docker manualmente
- avviare Elastic-Search eseguendo ./start.sh all'interno di elastic-start-local (questo è fornito direttamente da ElasticSearch)
- eseguire l'indicizzazione con indexer.py (viene pulita ad ogni avvio, il testing è locale)
- avviare l'app Streamlit eseguendo user_interface.py

I 'Requisiti' rimangono fissi. La relazione, in formato PDF e MD, si trova all'interno della cartella 'relazione_homework', insieme alle immagini utilizzate.