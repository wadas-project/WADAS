# Usa una base image Python preinstallato
FROM python:3.10.15-slim


# Imposta la directory di lavoro all'interno del container
WORKDIR /app

# Installa Ray e altre dipendenze necessarie
RUN pip install ray==2.44.1


# Avvia una shell interattiva quando il container parte
CMD ["bash"]
