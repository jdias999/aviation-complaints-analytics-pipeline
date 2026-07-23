import duckdb

con = duckdb.connect()

con.execute("""

    DROP TABLE IF EXISTS dim_companhia;
    DROP TABLE IF EXISTS dim_status_atendimento;
    DROP TABLE IF EXISTS dim_calendario;
    DROP TABLE IF EXISTS dim_localidades;
    DROP TABLE IF EXISTS fato_reclamacoes;


    CREATE TABLE dim_companhia (
        id_empresa      INTEGER PRIMARY KEY,
        nome_fantasia   VARCHAR,
        gestor          VARCHAR
    );
    CREATE TABLE dim_status_atendimento (
        id_status               INTEGER PRIMARY KEY,
        situacao                VARCHAR,
        avaliacao_reclamacao    VARCHAR,
        forma_contrato          VARCHAR,
        procurou_empresa        VARCHAR,
        respondida              VARCHAR
    );
    CREATE TABLE dim_calendario (
        id_data     INTEGER    PRIMARY KEY,
        data        DATE,
        ano         INTEGER,
        mes         INTEGER,
        dia         INTEGER,
        trimestre   INTEGER
    );
    CREATE TABLE dim_problemas (
        id_problemas                    INTEGER    PRIMARY KEY,
        area                            VARCHAR,
        assunto                         VARCHAR,
        problema                        VARCHAR,
        grupo_problema                  VARCHAR,
        codigo_classificador_anac       VARCHAR
    );
    CREATE TABLE dim_localidades (
        id_localidade   INTEGER    PRIMARY KEY,
        regiao          VARCHAR,
        uf              VARCHAR,
        cidade          VARCHAR
    );
    CREATE TABLE fato_reclamacoes (
        id_reclamacoes                      INTEGER         PRIMARY KEY,
        id_empresa                          INTEGER,
        id_status                           INTEGER,
        id_problemas                        INTEGER,
        id_localidade                       INTEGER,
        data_abertura                       INTEGER,
        data_fechamento                     INTEGER,
        prazo_analise_gestor                VARCHAR,
        prazo_resposta                      DATE,
        nota_consumidor                     VARCHAR
    );
""")

con.execute("""
    INSERT INTO dim_companhia (
        id_empresa, nome_fantasia, gestor         
    ) 
    WITH remover_duplicatas_companhia AS (
        SELECT 
            nome_fantasia,
            MAX(gestor) AS gestor
        FROM
            'data/silver/reclamacoes_limpas.parquet'
        WHERE
            nome_fantasia IS NOT NULL
        GROUP BY nome_fantasia
    )
    SELECT 
        ROW_NUMBER() OVER (ORDER BY nome_fantasia) AS id_empresa,
        nome_fantasia,
        gestor
    FROM
        remover_duplicatas_companhia;
    
        


    INSERT INTO dim_status_atendimento (
        id_status, situacao, avaliacao_reclamacao, forma_contrato, procurou_empresa, respondida          
    )
    WITH remover_duplicatas_status AS (
        SELECT DISTINCT
            situacao, avaliacao_reclamacao, forma_contrato, procurou_empresa, respondida
        FROM
            'data/silver/reclamacoes_limpas.parquet'
    )
    SELECT
        ROW_NUMBER() OVER () as id_status,
        situacao, 
        avaliacao_reclamacao, 
        forma_contrato, 
        procurou_empresa, 
        respondida
    FROM
        remover_duplicatas_status;
""")