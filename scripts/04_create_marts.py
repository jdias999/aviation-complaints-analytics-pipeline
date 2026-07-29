import duckdb

print("conectando ao banco gold para criar os marts...")

with duckdb.connect('data/gold/data_warehouse.duckdb') as con:
    con.execute("DROP SCHEMA IF EXISTS mart2 CASCADE; CREATE SCHEMA mart2; ")

#o objetivo desse mart é entregar uma tabela mastigada que 
# mostre o "boletim de desempenho" de cada companhia aérea mês a mês.
    query_marts = """
        CREATE OR REPLACE VIEW mart2.desempenho AS
        SELECT
            dc.nome_fantasia AS companhia,
            fc.ano AS ano_abertura,
            fc.mes AS mes_abertura,
            COUNT(ID_reclamacao) AS contagem_reclamacoes,
            ROUND(AVG(TRY_CAST(fr.tempo_resposta_em_dias AS FLOAT)), 1) AS tempo_resposta,
            ROUND(COUNT(CASE WHEN ds.respondida = 'S' THEN 1 END) * 100.0 
            / COUNT(fr.ID_reclamacao), 1) AS taxa_resposta_pct
        FROM
            fato_reclamacoes AS fr
        INNER JOIN
            dim_companhia AS dc
        ON
            fr.ID_empresa = dc.ID_empresa
        INNER JOIN
            dim_calendario AS fc
        ON
            fr.FK_data_abertura = fc.ID_data
        INNER JOIN
            dim_status AS ds
        ON
            fr.ID_status_atendimento = ds.ID_status_atendimento
        GROUP BY ALL
        ORDER BY 
            ano_abertura DESC, 
            mes_abertura ASC, 
            contagem_reclamacoes DESC;
    """
    con.execute(query_marts)
    print("view 'mart2.desempenho' criada com sucesso!")

    print("\n--- PREVIEW DAS 15 PRIMEIRAS LINHAS ---")
    con.sql("SELECT * FROM mart2.desempenho LIMIT 15").show()

# quais são os motivos que mais fazem os clientes reclamarem, 
# onde estão esses problemas e quanto tempo levamos para responder cada tipo de dor?

    query_mart_problemas = """
        CREATE OR REPLACE VIEW mart2.causa_raiz_problemas AS
        SELECT
            fc.ano AS ano_abertura,
            fc.mes AS mes_abertura,
            dp.problema AS motivo_problema,
            COUNT(fr.ID_reclamacao) AS total_reclamacoes,
            ROUND(AVG(TRY_CAST(fr.tempo_resposta_em_dias AS FLOAT)), 1) AS tempo_resposta_dias,
            ROUND(
                COUNT(CASE WHEN ds.respondida = 'S' THEN 1 END) * 100.0 
                / COUNT(fr.ID_reclamacao), 
            1) AS taxa_resposta_pct
        FROM
            fato_reclamacoes AS fr
        INNER JOIN
            dim_calendario AS fc
            ON fr.FK_data_abertura = fc.ID_data
        INNER JOIN
            dim_problemas AS dp
            ON fr.ID_problemas = dp.ID_problemas
        INNER JOIN
            dim_status AS ds
            ON fr.ID_status_atendimento = ds.ID_status_atendimento
        GROUP BY ALL
        ORDER BY 
            ano_abertura DESC, 
            mes_abertura ASC, 
            total_reclamacoes DESC;
    """
    con.execute(query_mart_problemas)
    print("view 'mart2.causa_raiz_problemas' criada com sucesso!")

    print("\n--- PREVIEW DAS 15 PRIMEIRAS LINHAS ---")
    con.sql("SELECT * FROM mart2.causa_raiz_problemas LIMIT 15").show()

#Dentro de cada mês, qual é a posição de ranking de cada problema e qual é a porcentagem
#que esse problema representou do total de reclamações daquele mês?

    query_mart_problemas_ranking = """
        CREATE OR REPLACE VIEW mart2.ranking_problemas AS
        WITH agrupamento AS (
            SELECT
                fc.ano AS ano_abertura,
                fc.mes AS mes_abertura,
                dp.problema AS motivo_problema,
                COUNT(fr.ID_reclamacao) AS total_reclamacoes
            FROM
                fato_reclamacoes AS fr
            INNER JOIN
                dim_calendario AS fc
                ON fr.FK_data_abertura = fc.ID_data
            INNER JOIN
                dim_problemas AS dp
                ON fr.ID_problemas = dp.ID_problemas
            GROUP BY ALL
                )
        SELECT
            ano_abertura,
            mes_abertura,
            motivo_problema,
            total_reclamacoes,
            ROW_NUMBER() OVER (
                PARTITION BY ano_abertura, mes_abertura
                ORDER BY total_reclamacoes DESC
            ) AS posicao_ranking
        FROM
            agrupamento
        ORDER BY
            ano_abertura DESC, mes_abertura ASC, posicao_ranking ASC;
    """

    con.execute(query_mart_problemas_ranking)
    print("view 'mart2.ranking_problemas' criada com sucesso!")

    print("\n--- PREVIEW DAS 15 PRIMEIRAS LINHAS ---")
    con.sql("SELECT * FROM mart2.ranking_problemas LIMIT 15").show()
