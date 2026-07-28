import duckdb
import pandas as pd

con = duckdb.connect()


#aqui, vamos criar o DF da tabela Dim_companhia

def criar_companhia(df_prata):
    df_companhia = df_prata[['nome_fantasia', 'gestor']].copy()
    df_companhia = df_companhia.drop_duplicates(subset=['nome_fantasia'])
    df_companhia['ID_empresa'] = range(1, len(df_companhia) + 1)
    df_companhia = df_companhia[['ID_empresa', 'nome_fantasia', 'gestor']]
    return df_companhia

#agora, o DF de status_atendimento

def criar_status_atendimento(df_prata):
    df_status_atendimento = df_prata[['situacao', 
        'avaliacao_reclamacao', 'forma_contrato', 'procurou_empresa', 'respondida']].copy()
    df_status_atendimento = df_status_atendimento.drop_duplicates()
    df_status_atendimento['ID_status_atendimento'] = range(1, len(df_status_atendimento) + 1)
    df_status_atendimento = df_status_atendimento[['ID_status_atendimento', 'situacao', 'avaliacao_reclamacao', 
        'forma_contrato', 'procurou_empresa', 'respondida']]
    return df_status_atendimento

#df_localidade

def criar_localidade(df_prata):
    df_localidade = df_prata[['regiao', 'uf', 'cidade']].copy()
    df_localidade = df_localidade.drop_duplicates()
    df_localidade['ID_localidade'] = range(1, len(df_localidade) + 1)
    df_localidade = df_localidade[['ID_localidade', 'regiao', 'uf', 'cidade']]
    return df_localidade

#nome irônico 

def criar_problemas(df_prata):
    df_problemas = df_prata[['area', 'assunto', 'problema', 'grupo_problema', 'codigo_classificador_anac']].copy()
    df_problemas = df_problemas.drop_duplicates()
    df_problemas['ID_problemas'] = range(1, len(df_problemas) + 1)
    df_problemas = df_problemas[['ID_problemas', 'area', 'assunto', 'problema', 'grupo_problema', 'codigo_classificador_anac' ]]
    return df_problemas

#Última dim, a data

def criar_calendario(df_prata):
    datas_abertura = pd.to_datetime(df_prata['data_abertura'], errors='coerce')
    datas_finalizacao = pd.to_datetime(df_prata['data_finalizacao'], errors='coerce')

    todas_as_datas = pd.concat([datas_abertura, datas_finalizacao]).dropna()

    df_calendario = pd.DataFrame({'data_completa': todas_as_datas})
    df_calendario = df_calendario.drop_duplicates().sort_values('data_completa').reset_index(drop=True)

    df_calendario['dia'] = df_calendario['data_completa'].dt.day
    df_calendario['mes'] = df_calendario['data_completa'].dt.month
    df_calendario['ano'] = df_calendario['data_completa'].dt.year

    df_calendario['ID_data'] = df_calendario['data_completa'].dt.strftime('%Y%m%d').astype(int)

    df_calendario['data_completa'] = df_calendario['data_completa'].dt.strftime('%Y-%m-%d')
    df_calendario = df_calendario[['ID_data', 'data_completa', 'dia', 'mes', 'ano']]

    return df_calendario





#Agora, a tabela fato
def criar_fato_reclamacao(df_prata, df_companhia, df_status_atendimento, df_problemas, df_calendario, df_localidade):
    df_fato = df_prata.copy()
    df_fato = pd.merge(
    df_fato, 
    df_companhia[['nome_fantasia', 'ID_empresa']], 
    left_on = 'nome_fantasia',   
    right_on = 'nome_fantasia',  
    how='left'
    )

    #puxar id do status

    colunas_status = ['situacao', 'avaliacao_reclamacao', 'forma_contrato', 'procurou_empresa', 'respondida']
    df_fato = pd.merge(
    df_fato,
    df_status_atendimento[['situacao', 'avaliacao_reclamacao', 'forma_contrato', 'procurou_empresa', 'respondida', 'ID_status_atendimento']],
    left_on = colunas_status,
    right_on=['situacao', 'avaliacao_reclamacao', 'forma_contrato', 'procurou_empresa', 'respondida'],
    how='left'
    )

    #puxar fk das datas

    df_fato['FK_data_abertura'] = pd.to_datetime(df_fato['data_abertura'], errors='coerce').dt.strftime('%Y%m%d')
    df_fato['FK_data_abertura'] = df_fato['FK_data_abertura'].fillna('-1').astype(int)

    df_fato['FK_data_finalizacao'] = pd.to_datetime(df_fato['data_finalizacao'], errors='coerce').dt.strftime('%Y%m%d')
    df_fato['FK_data_finalizacao'] = df_fato['FK_data_finalizacao'].fillna('-1').astype(int)

    #puxar id dos problemas
    
    colunas_problemas = ['area', 'assunto', 'problema', 'grupo_problema', 'codigo_classificador_anac']
    df_fato = pd.merge(
    df_fato,
    df_problemas[['area', 'assunto', 'problema', 'grupo_problema', 'codigo_classificador_anac', 'ID_problemas']],
    left_on = colunas_problemas,
    right_on = ['area', 'assunto', 'problema', 'grupo_problema', 'codigo_classificador_anac'],
    how='left'
     )

    #id da localidade

    colunas_localidade = ['regiao', 'uf', 'cidade']
    df_fato = pd.merge(
    df_fato,
    df_localidade[['regiao', 'uf', 'cidade', 'ID_localidade']],
    left_on = colunas_localidade,
    right_on = ['regiao', 'uf', 'cidade'],
    how = 'left'
    )

    #criar o id

    df_fato['ID_reclamacao'] = range(1, len(df_fato) + 1)

    #colunas finais

    colunas_finais = [
        
        'ID_reclamacao', 
        'ID_empresa',
        'ID_status_atendimento',
        'ID_localidade',
        'ID_problemas',
        'FK_data_abertura',
        'FK_data_finalizacao',
        'prazo_analise_gestor_em_dias',
        'prazo_resposta',
        'nota_do_consumidor',
        'tempo_resposta_em_dias'
    ]
    df_fato_final = df_fato[colunas_finais]
    
    return df_fato_final

#lê o arquivo

caminho_parquet = 'data/silver/reclamacoes_limpas.parquet'
df_prata = pd.read_parquet(caminho_parquet)

#constrói as Dimensões

df_companhia = criar_companhia(df_prata)
df_status_atendimento = criar_status_atendimento(df_prata)
df_calendario = criar_calendario(df_prata)
df_problemas = criar_problemas(df_prata)
df_localidade = criar_localidade(df_prata)
df_fato_reclamacoes = criar_fato_reclamacao(df_prata, df_companhia, df_status_atendimento, df_problemas, df_calendario, df_localidade)


print("Iniciando a validação de dados (Data Quality Checks)...")

#aqui, um pequeno data validation

assert df_companhia['ID_empresa'].is_unique, "ERRO DE INTEGRIDADE: ID_empresa duplicado na dim_companhia."
assert df_problemas['ID_problemas'].is_unique, "ERRO DE INTEGRIDADE: ID_problemas duplicado na dim_problemas."
assert df_localidade['ID_localidade'].is_unique, "ERRO DE INTEGRIDADE: ID_localidade duplicado na dim_localidade."
assert df_status_atendimento['ID_status_atendimento'].is_unique, "ERRO DE INTEGRIDADE: ID_status_atendimento duplicado."


colunas_chaves_fato = [
    'ID_reclamacao', 'ID_empresa', 'ID_status_atendimento', 
    'ID_localidade', 'ID_problemas', 'FK_data_abertura', 'FK_data_finalizacao'
]

for col in colunas_chaves_fato:
    assert df_fato_reclamacoes[col].notnull().all(), \
        f"ERRO DE NULOS: valores ausentes encontrados na coluna {col} da tabela fato."

print("Validação concluída com sucesso! Os dados estão íntegros.")


print("Iniciando a carga no banco DuckDB...")

#aqui, conectei com o arquivo do DW

con_gold = duckdb.connect('data/gold/data_warehouse.duckdb')

#cria as tabelas a partir dos dataframes

con_gold.execute("CREATE TABLE IF NOT EXISTS dim_companhia AS SELECT * FROM df_companhia")
con_gold.execute("CREATE TABLE IF NOT EXISTS dim_status AS SELECT * FROM df_status_atendimento")
con_gold.execute("CREATE TABLE IF NOT EXISTS dim_localidade AS SELECT * FROM df_localidade")
con_gold.execute("CREATE TABLE IF NOT EXISTS dim_problemas AS SELECT * FROM df_problemas")
con_gold.execute("CREATE TABLE IF NOT EXISTS dim_calendario AS SELECT * FROM df_calendario")
con_gold.execute("CREATE TABLE IF NOT EXISTS fato_reclamacoes AS SELECT * FROM df_fato_reclamacoes")

#no final, fecha a conexão para salvar as alterações no disco
con_gold.close()

print("Sucesso! Modelo Star Schema salvo no DuckDB na camada Gold.")




