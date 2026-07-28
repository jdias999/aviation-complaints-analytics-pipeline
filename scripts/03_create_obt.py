import duckdb

print("conectando ao banco gold para criar a OBT...")

#conecta no mesmo banco onde estão a fato e as dimensões

with duckdb.connect('data/gold/data_warehouse.duckdb') as con:
    con.execute("DROP SCHEMA IF EXISTS mart CASCADE; CREATE SCHEMA mart; ")

    query_obt = """

    CREATE OR REPLACE TABLE mart.big_table AS
    SELECT

        fr.ID_reclamacao, 
        fr.ID_empresa,
        fr.ID_status_atendimento,
        fr.ID_localidade,
        fr.ID_problemas,
        fr.FK_data_abertura,
        fr.FK_data_finalizacao,
        fr.prazo_analise_gestor_em_dias,
        fr.prazo_resposta,
        fr.nota_do_consumidor,
        fr.tempo_resposta_em_dias,
        dc.nome_fantasia,
        dc.gestor,
        sa.situacao, 
        sa.avaliacao_reclamacao,
        sa.forma_contrato, 
        sa.procurou_empresa, 
        sa.respondida,
        dl.regiao,
        dl.uf,
        dl.cidade,
        dp.area, 
        dp.assunto, 
        dp.problema, 
        dp.grupo_problema, 
        dp.codigo_classificador_anac,
        fc.data_completa AS data_abertura_completa,
        fc.dia AS dia_abertura, 
        fc.mes AS mes_abertura,
        fc.ano AS ano_abertura,
        fcf.data_completa AS data_finalizacao_completa,
        fcf.dia AS dia_finalizacao, 
        fcf.mes AS mes_finalizacao,
        fcf.ano AS ano_finalizacao
        

    FROM
        fato_reclamacoes AS fr
    LEFT JOIN
        dim_companhia AS dc
    ON
        fr.ID_empresa = dc.ID_empresa
    LEFT JOIN
        dim_status AS sa
    ON
        fr.ID_status_atendimento = sa.ID_status_atendimento
    LEFT JOIN
        dim_localidade AS dl
    ON
        fr.ID_localidade = dl.ID_localidade
    LEFT JOIN
        dim_problemas AS dp
    ON 
        fr.ID_problemas = dp.ID_problemas
    LEFT JOIN
        dim_calendario AS fc
    ON 
        fr.FK_data_abertura = fc.ID_data
    LEFT JOIN
        dim_calendario AS fcf
    ON 
        fr.FK_data_finalizacao = fcf.ID_data

    """

    con.execute(query_obt)

print("Sucesso! OBT criada no schema mart.")

