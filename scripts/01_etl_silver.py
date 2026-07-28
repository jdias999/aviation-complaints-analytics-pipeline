import duckdb
import pandas as pd


con = duckdb.connect()

print("Iniciando o processamento da camada Silver...")

# aqui, criei uma view para ser o "espelho" do csv, e usada para ler ele inteiro.
# também utilizado normalize_names, para normalizar os nomes das colunas em tudo minúsculo e sem espaço
con.execute("""
    CREATE OR REPLACE VIEW dados_brutos AS 
    SELECT * 
    FROM 
        read_csv_auto('data/bronze/reclamacoes.csv', normalize_names=True)
""")

# no final, usei o copy para pegar essa view e criá-la em formato parquet,
con.execute("""
    COPY 
        (SELECT * FROM dados_brutos) 
    TO 'data/silver/reclamacoes_limpas.parquet' 
    (FORMAT PARQUET)
""")

print("Sucesso! Arquivo Parquet gerado na pasta data/silver/")


