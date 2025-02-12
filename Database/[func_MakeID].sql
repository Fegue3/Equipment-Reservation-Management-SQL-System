CREATE FUNCTION [dbo].[MakeID] (@Data DATETIME, @Numero INT)
RETURNS NVARCHAR(8)
AS
BEGIN
    DECLARE @Ano NVARCHAR(4);
    DECLARE @Sequencia NVARCHAR(4);

    -- Extrair o ano diretamente
    SET @Ano = LEFT(YEAR(@Data), 4);

    -- Construir a sequ�ncia de 4 d�gitos manualmente
    IF @Numero < 10 
        SET @Sequencia = '000' + RTRIM(@Numero);
    ELSE IF @Numero < 100 
        SET @Sequencia = '00' + RTRIM(@Numero);
    ELSE IF @Numero < 1000 
        SET @Sequencia = '0' + RTRIM(@Numero);
    ELSE
        SET @Sequencia = RTRIM(@Numero);

    -- Concatenar ano e sequ�ncia
    RETURN @Ano + @Sequencia;
END;
