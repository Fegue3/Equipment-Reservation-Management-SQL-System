
# Equipment Reservation Management System

## Summary
This project implements an equipment reservation and requisition management system for the Department of Informatics. It regulates the use of shared resources, such as laptops and projectors, applying priority rules and business logic to ensure fair and efficient allocation.

---

## Objectives
- Manage reservations and requisitions for shared equipment.
- Implement dynamic priority rules based on user type and history.
- Automate state transitions and apply penalties automatically.

---

## Technologies Used
- **Database**: Microsoft SQL Server
- **Frontend**: Python (or other suggested environments)
- **Modeling Tools**: ERD Plus for entity-relationship diagrams

---

## Key Features
1. **Reservations**:
   - Generate unique IDs for reservations.
   - Manage states: *active*, *waiting*, *satisfied*, *canceled*, and *forgotten*.
   - Support preemption based on priority.

2. **Requisitions**:
   - Automatically convert satisfied reservations into requisitions.
   - Track equipment usage states.

3. **Priority Rules**:
   - Initial assignment based on user type.
   - Dynamic penalties and promotions based on user behavior.

4. **Automation with Triggers and Procedures**:
   - Automate state updates.
   - Apply penalties for delays and cancellations.

---

## Data Modeling
- Entity-Relationship Diagram.
  ![Entity-Relationship Diagram](https://github.com/user-attachments/assets/2e679a85-b9c6-48e9-97c9-64de01fed88c)
- Relational Schema (well-defined tables with relationships and constraints).
  ![Relational Schema](https://github.com/user-attachments/assets/e2ad1a05-d239-409e-8ba9-3ff7bac07371)

---

## Code Highlights
### **Stored Procedure: Reserve2Requisition**
```sql
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

```

### **Trigger: Handle All Preemptions**
```sql

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
```

---

## Screenshots
  ![API](https://github.com/user-attachments/assets/b46fc661-f652-40c0-a042-516393c9253b)

---

## Challenges and Lessons Learned
- **Challenges**: Ensuring business rule consistency with complex triggers.
- **Lessons Learned**: Developing robust systems with dynamic business logic.

---

## How to Run the Project
1. Set up Microsoft SQL Server and import the provided scripts.
2. Install the dependencies for the Python frontend.
3. Follow the instructions in `API.py` to set up the database connection.
4. Run the application using `API.py`.

---

## Authors
Developed by Francisco Pereira, Daniel Cardoso and Fábio Horta.

---

## License
This project was created to showcase and demonstrate advanced skills in database design, implementation, and integration with real-world business logic. It highlights expertise in areas such as:
- Relational database modeling and normalization.
- Development of stored procedures, triggers, and views.
- Implementation of dynamic rules and automated processes.

