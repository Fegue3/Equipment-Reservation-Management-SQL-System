
CREATE OR ALTER TRIGGER [dbo].[trg_HandleAllPreemptions]
ON [dbo].[Reserva]
AFTER INSERT, UPDATE
AS
BEGIN
    SET NOCOUNT ON;

    -- Criar tabela temporária para armazenar estados calculados
    CREATE TABLE #ReservasAtualizadas (
        ID_Reserva NVARCHAR(10),
        Estado NVARCHAR(10)
    );

    -- Determinar a reserva vencedora acima de 48 horas
    INSERT INTO #ReservasAtualizadas (ID_Reserva, Estado)
    SELECT 
        rc.ID_Reserva,
        CASE 
            WHEN rc.ID_Reserva = vencedoras.ID_Reserva THEN 'active'
            ELSE 'waiting'
        END AS Estado
    FROM dbo.ReservaEquipamento re
    INNER JOIN dbo.Reserva rc ON re.ID_Reserva = rc.ID_Reserva
    INNER JOIN (
        SELECT 
            re.ID_Equipamento,
            rc.ID_Reserva,
            ROW_NUMBER() OVER (
                PARTITION BY re.ID_Equipamento
                ORDER BY 
                    CASE 
                        WHEN DATEDIFF(HOUR, GETDATE(), rc.Data_Inicio_Pedido) > 48 THEN
                            CASE u.Prioridade
                                WHEN 'Maxima' THEN 5
                                WHEN 'Acima da Media' THEN 4
                                WHEN 'Media' THEN 3
                                WHEN 'Abaixo da Media' THEN 2
                                WHEN 'Minima' THEN 1
                                ELSE 0
                            END
                        ELSE 0
                    END DESC,
                    rc.TimeStamp_Reserva ASC
            ) AS RN
        FROM dbo.ReservaEquipamento re
        INNER JOIN dbo.Reserva rc ON re.ID_Reserva = rc.ID_Reserva
        INNER JOIN dbo.Utilizador u ON rc.ID_Utilizador = u.ID_Utilizador
        WHERE DATEDIFF(HOUR, GETDATE(), rc.Data_Inicio_Pedido) > 48
          AND rc.Estado IN ('active', 'waiting')
    ) AS vencedoras
    ON re.ID_Equipamento = vencedoras.ID_Equipamento
       AND vencedoras.RN = 1;

-- Determinar a reserva vencedora abaixo de 48 horas
INSERT INTO #ReservasAtualizadas (ID_Reserva, Estado)
SELECT 
    rc.ID_Reserva,
    CASE 
        WHEN rc.TimeStamp_Reserva = ISNULL(vencedoras.MaisAntigaPresidente, vencedoras.MaisAntigaOutro) THEN 'active'
        ELSE 'waiting'
    END AS Estado
FROM dbo.ReservaEquipamento re
INNER JOIN dbo.Reserva rc ON re.ID_Reserva = rc.ID_Reserva
INNER JOIN dbo.Utilizador u ON rc.ID_Utilizador = u.ID_Utilizador
INNER JOIN (
    -- Determinar a reserva mais antiga para cada equipamento, priorizando o Presidente
    SELECT 
        re.ID_Equipamento,
        MIN(CASE 
                WHEN u.ID_TipoUtilizador = 'PD' THEN rc.TimeStamp_Reserva 
                ELSE NULL 
            END) AS MaisAntigaPresidente,
        MIN(CASE 
                WHEN u.ID_TipoUtilizador <> 'PD' THEN rc.TimeStamp_Reserva
                ELSE NULL 
            END) AS MaisAntigaOutro
    FROM dbo.ReservaEquipamento re
    INNER JOIN dbo.Reserva rc ON re.ID_Reserva = rc.ID_Reserva
    INNER JOIN dbo.Utilizador u ON rc.ID_Utilizador = u.ID_Utilizador
    WHERE DATEDIFF(HOUR, GETDATE(), rc.Data_Inicio_Pedido) <= 48
      AND rc.Estado IN ('active', 'waiting')
    GROUP BY re.ID_Equipamento
) AS vencedoras
ON re.ID_Equipamento = vencedoras.ID_Equipamento;
    -- Atualizar os estados na tabela Reserva
    UPDATE r
    SET r.Estado = ru.Estado
    FROM dbo.Reserva r
    INNER JOIN #ReservasAtualizadas ru ON r.ID_Reserva = ru.ID_Reserva
	WHERE r.Estado NOT IN ('forgotten', 'canceled', 'satisfied');

    -- Limpar tabela temporária
    DROP TABLE #ReservasAtualizadas;
END;