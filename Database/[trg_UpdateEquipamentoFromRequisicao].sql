CREATE OR ALTER TRIGGER [dbo].[trg_UpdateEquipamentoFromRequisicao]
ON [dbo].[Requisicao]
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;

    -- Atualizar estado do equipamento para "em uso" quando a requisição estiver ativa
    UPDATE e
    SET e.Estado_Equipamento = 'em uso'
    FROM Equipamento e
    INNER JOIN inserted req ON e.ID_Equipamento = req.ID_Equipamento
    WHERE req.Estado_Requisicao = 'active';

    -- Atualizar estado do equipamento para "disponível" quando a requisição for encerrada
    UPDATE e
    SET e.Estado_Equipamento = 'disponível'
    FROM Equipamento e
    INNER JOIN inserted req ON e.ID_Equipamento = req.ID_Equipamento
    WHERE req.Estado_Requisicao = 'closed';
END;
