CREATE OR ALTER VIEW HistoricoCompleto AS
SELECT 
    hr.ID_Historico,
    hr.ID_Reserva,
    NULL AS ID_Requisicao, -- Não aplicável para reservas
    hr.ID_Utilizador,
    u.Nome AS Nome_Utilizador,
    hr.ID_Equipamento,
    e.Nome_Equipamento,
    hr.Estado,
    hr.Data_Inicio_Pedido AS Data_Inicio,
    hr.Data_Registro
FROM Historico_Reservas hr
LEFT JOIN Utilizador u ON hr.ID_Utilizador = u.ID_Utilizador
LEFT JOIN Equipamento e ON hr.ID_Equipamento = e.ID_Equipamento
UNION ALL
SELECT 
    hq.ID_Historico,
    NULL AS ID_Reserva, -- Não aplicável para requisições
    hq.ID_Requisicao,
    hq.ID_Utilizador,
    u.Nome AS Nome_Utilizador,
    hq.ID_Equipamento,
    e.Nome_Equipamento,
    hq.Estado_Requisicao AS Estado,
    hq.Data_Requisicao AS Data_Inicio,
    hq.Data_Registro
FROM Historico_Requisicoes hq
LEFT JOIN Utilizador u ON hq.ID_Utilizador = u.ID_Utilizador
LEFT JOIN Equipamento e ON hq.ID_Equipamento = e.ID_Equipamento;



CREATE VIEW ReservasPreemptadas AS
SELECT 
    r.ID_Reserva AS Reserva_Impactada,
    r.ID_Utilizador AS Utilizador_Impactado,
    u1.Nome AS Nome_Impactado,
    r.Data_Inicio_Pedido AS Data_Impactada,
    r.Estado AS Estado_Atual,
    rp.ID_Reserva AS Reserva_Prioritaria,
    rp.ID_Utilizador AS Utilizador_Prioritario,
    u2.Nome AS Nome_Prioritario,
    rp.Data_Inicio_Pedido AS Data_Prioritaria
FROM Reserva r
INNER JOIN ReservaEquipamento re1 ON r.ID_Reserva = re1.ID_Reserva
INNER JOIN ReservaEquipamento re2 ON re1.ID_Equipamento = re2.ID_Equipamento
INNER JOIN Reserva rp ON re2.ID_Reserva = rp.ID_Reserva
INNER JOIN Utilizador u1 ON r.ID_Utilizador = u1.ID_Utilizador
INNER JOIN Utilizador u2 ON rp.ID_Utilizador = u2.ID_Utilizador
WHERE r.Estado = 'waiting' -- Reservas impactadas
  AND rp.Estado = 'active' -- Reservas prioritárias que causaram o impacto
  AND r.ID_Reserva <> rp.ID_Reserva; -- Evitar que a reserva impactada e prioritária sejam a mesma


CREATE VIEW PenalizacoesUtilizadores AS
SELECT 
    p.ID_Penalizacao,
    p.ID_Utilizador,
    u.Nome AS Nome_Utilizador,
    p.Motivo_Penalizacao AS Tipo_Penalizacao,
    p.Data_Penalizacao,
    p.Valor_Penalizacao AS Faltas_Acumuladas,
    CASE 
        WHEN p.Valor_Penalizacao >= 5 THEN 'Reduzida'
        ELSE 'Normal'
    END AS Estado_Prioridade
FROM Penalizacao p
INNER JOIN Utilizador u ON p.ID_Utilizador = u.ID_Utilizador;



CREATE VIEW ResourceState AS
SELECT 
    e.ID_Equipamento,
    e.Nome_Equipamento,
    CASE 
        WHEN e.Estado_Equipamento = 'disponível' THEN 'Available'
        WHEN e.Estado_Equipamento = 'reservado' THEN 'Reserved'
        WHEN e.Estado_Equipamento = 'em uso' THEN 'InUse'
        ELSE 'Unknown'
    END AS Estado,
    ISNULL(r.ID_Reserva, rq.ID_Requisicao) AS ID, -- ID da reserva ou requisição
    ISNULL(u.ID_Utilizador, 'N/A') AS ID_Utilizador,
    ISNULL(u.Nome, 'N/A') AS Nome_Utilizador
FROM Equipamento e
LEFT JOIN ReservaEquipamento re ON e.ID_Equipamento = re.ID_Equipamento
LEFT JOIN Reserva r ON re.ID_Reserva = r.ID_Reserva
LEFT JOIN Requisicao rq ON e.ID_Equipamento = rq.ID_Equipamento
LEFT JOIN Utilizador u ON ISNULL(r.ID_Utilizador, rq.ID_Utilizador) = u.ID_Utilizador;


CREATE VIEW RequisicoesAtivas AS
SELECT 
    rq.ID_Requisicao,
    rq.ID_Utilizador,
    u.Nome AS Nome_Utilizador,
    rq.ID_Equipamento,
    e.Nome_Equipamento,
    rq.Data_Inicio_Requisicao,
    rq.Data_Fim_Requisicao,
    rq.Estado_Requisicao
FROM Requisicao rq
INNER JOIN Utilizador u ON rq.ID_Utilizador = u.ID_Utilizador
INNER JOIN Equipamento e ON rq.ID_Equipamento = e.ID_Equipamento
WHERE rq.Estado_Requisicao = 'active';



CREATE VIEW EquipamentosPorTipoUtilizador AS
SELECT 
    e.ID_Equipamento,
    e.Nome_Equipamento,
    tu.Tipo_Utilizador,
    COUNT(r.ID_Reserva) AS Total_Reservas
FROM Equipamento e
LEFT JOIN ReservaEquipamento re ON e.ID_Equipamento = re.ID_Equipamento
LEFT JOIN Reserva r ON re.ID_Reserva = r.ID_Reserva
LEFT JOIN Utilizador u ON r.ID_Utilizador = u.ID_Utilizador
LEFT JOIN Tipo_Utilizador tu ON u.ID_TipoUtilizador = tu.ID_TipoUtilizador
GROUP BY e.ID_Equipamento, e.Nome_Equipamento, tu.Tipo_Utilizador;


