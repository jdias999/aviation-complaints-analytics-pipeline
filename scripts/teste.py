import duckdb
import pandas

con = duckdb.connect()


resultado = con.execute("DESCRIBE SELECT * FROM 'data/silver/reclamacoes_limpas.parquet'").df()

print(resultado)