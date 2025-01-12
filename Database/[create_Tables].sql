
CREATE TABLE Tipo_Utilizador
(
  ID_TipoUtilizador VARCHAR(2) NOT NULL,
  Tipo_Utilizador VARCHAR(50) NOT NULL,
  PRIMARY KEY (ID_TipoUtilizador)
);

CREATE TABLE Utilizador
(
  ID_Utilizador VARCHAR(10) NOT NULL,
  Nome VARCHAR(100) NOT NULL,
  Telefone VARCHAR(15) NOT NULL,
  Email VARCHAR(100) NOT NULL,
  Prioridade VARCHAR(20) NOT NULL,
  ID_TipoUtilizador VARCHAR(2) NOT NULL,
  PRIMARY KEY (ID_Utilizador),
  FOREIGN KEY (ID_TipoUtilizador) REFERENCES Tipo_Utilizador(ID_TipoUtilizador),
);

CREATE TABLE Equipamento
(
  ID_Equipamento INT NOT NULL,
  Nome_Equipamento VARCHAR(100) NOT NULL,
  Estado_Equipamento VARCHAR(20) NOT NULL,
  PRIMARY KEY (ID_Equipamento),
);


CREATE TABLE Reserva
(
  ID_Reserva VARCHAR(8) NOT NULL,
  TimeStamp_Reserva DATETIME NOT NULL DEFAULT GETDATE(),
  Data_Inicio_Pedido DATETIME NOT NULL,
  Data_Fim_Pedido DATETIME NOT NULL,
  Data_Inicio_Real DATETIME,
  Data_Fim_Real DATETIME,
  Data_Alterada DATETIME,
  Data_Cancelamento DATETIME,
  Motivo_Reserva VARCHAR(255),
  Estado VARCHAR(20) NOT NULL,
  ID_Utilizador VARCHAR(10) NOT NULL,
  PRIMARY KEY (ID_Reserva),
  FOREIGN KEY (ID_Utilizador) REFERENCES Utilizador(ID_Utilizador),
);

CREATE TABLE Requisicao
(
  ID_Requisicao INT NOT NULL,
  Data_Inicio_Requisicao DATETIME NOT NULL,
  Estado_Requisicao VARCHAR(20) NOT NULL,
  Data_Fim_Requisicao DATETIME,
  ID_Reserva VARCHAR(8),
  ID_Equipamento INT NOT NULL,
  ID_Utilizador VARCHAR(10) NOT NULL,
  PRIMARY KEY (ID_Requisicao),
  FOREIGN KEY (ID_Reserva) REFERENCES Reserva(ID_Reserva),
  FOREIGN KEY (ID_Equipamento) REFERENCES Equipamento(ID_Equipamento),
  FOREIGN KEY (ID_Utilizador) REFERENCES Utilizador(ID_Utilizador),
);

CREATE TABLE Penalizacao
(
  ID_Penalizacao INT NOT NULL,
  Data_Penalizacao DATETIME NOT NULL,
  Valor_Penalizacao INT NOT NULL CHECK (Valor_Penalizacao >= 0),
  Motivo_Penalizacao VARCHAR(255) NOT NULL,
  ID_Requisicao INT,
  ID_Reserva VARCHAR(8),
  ID_Utilizador VARCHAR(10) NOT NULL,
  PRIMARY KEY (ID_Penalizacao),
  FOREIGN KEY (ID_Requisicao) REFERENCES Requisicao(ID_Requisicao)
     ON DELETE CASCADE,
  FOREIGN KEY (ID_Reserva) REFERENCES Reserva(ID_Reserva)
     ON DELETE CASCADE,
  FOREIGN KEY (ID_Utilizador) REFERENCES Utilizador(ID_Utilizador)
	ON DELETE CASCADE,
);


CREATE TABLE ReservaEquipamento
(
  imprescindivel VARCHAR(1) NOT NULL CHECK (imprescindivel IN ('Y', 'N')),
  ID_Equipamento INT NOT NULL,
  ID_Reserva VARCHAR(8) NOT NULL,
  PRIMARY KEY (ID_Equipamento, ID_Reserva),
  FOREIGN KEY (ID_Equipamento) REFERENCES Equipamento(ID_Equipamento),
  FOREIGN KEY (ID_Reserva) REFERENCES Reserva(ID_Reserva)
);
