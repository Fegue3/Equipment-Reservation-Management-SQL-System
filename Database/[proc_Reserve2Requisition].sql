CREATE PROCEDURE [dbo].[Reserve2Requisition] (@ID_Reserva VARCHAR(8))
AS
BEGIN
    SET NOCOUNT ON;

    -- Variáveis auxiliares
    DECLARE @Data_Inicio DATETIME;
    DECLARE @Data_Fim DATETIME;
    DECLARE @ID_Utilizador VARCHAR(50);

    -- Obter dados da reserva
    SELECT 
        @Data_Inicio = Data_Inicio_Real,
        @Data_Fim = Data_Fim_Real,
        @ID_Utilizador = ID_Utilizador
    FROM Reserva
    WHERE ID_Reserva = @ID_Reserva AND Estado = 'satisfied';


    INSERT INTO Requisicao (ID_Requisicao, Data_Inicio_Requisicao, Estado_Requisicao, Data_Fim_Requisicao, ID_Reserva, ID_Equipamento, ID_Utilizador)
    SELECT 
        ISNULL((SELECT MAX(ID_Requisicao) FROM Requisicao), 0) + ROW_NUMBER() OVER (ORDER BY ID_Equipamento) AS ID_Requisicao,
        GETDATE(),
        'active',
        @Data_Fim,
        @ID_Reserva,
        ID_Equipamento,
        @ID_Utilizador
    FROM ReservaEquipamento RE
    WHERE ID_Reserva = @ID_Reserva
      AND NOT EXISTS (
          SELECT 1 
          FROM Requisicao R
          WHERE R.ID_Reserva = RE.ID_Reserva
            AND R.ID_Equipamento = RE.ID_Equipamento
      );
END;
