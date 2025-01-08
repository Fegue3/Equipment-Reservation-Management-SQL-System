import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, scrolledtext
import pyodbc


class DatabaseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Aplicação")

        self.conn = None
        self.cursor = None

        self.create_menu()

    def create_menu(self):
        menu_bar = tk.Menu(self.root)

        # Menu de Conexão
        db_menu = tk.Menu(menu_bar, tearoff=0)
        db_menu.add_command(label="Ligar à Base de Dados", command=self.connect_to_db)
        db_menu.add_separator()
        db_menu.add_command(label="Sair", command=self.root.quit)
        menu_bar.add_cascade(label="Início", menu=db_menu)

        # Menu CRUD
        crud_menu = tk.Menu(menu_bar, tearoff=0)
        crud_menu.add_command(label="Adicionar Dados", command=self.add_data)
        crud_menu.add_command(label="Atualizar Dados", command=self.update_data)
        crud_menu.add_command(label="Apagar Dados", command=self.delete_data)
        crud_menu.add_command(label="Visualizar Dados", command=self.view_data)
        crud_menu.add_command(label="Query Genérica", command=self.generic_query)
        menu_bar.add_cascade(label="Operações CRUD", menu=crud_menu)

        # Menu Reserva
        reserva_menu = tk.Menu(menu_bar, tearoff=0)
        reserva_menu.add_command(label="Registar Reserva", command=self.add_reserva)
        reserva_menu.add_command(label="Alterar Estado de Reserva", command=self.alterar_estado_reserva)
        menu_bar.add_cascade(label="Reservas", menu=reserva_menu)

        # Menu Requisição
        requisicao_menu = tk.Menu(menu_bar, tearoff=0)
        requisicao_menu.add_command(label="Gerir Requisições", command=self.gerir_requisicoes)
        menu_bar.add_cascade(label="Requisições", menu=requisicao_menu)

        # Menu Views
        views_menu = tk.Menu(menu_bar, tearoff=0)
        views_menu.add_command(label="Visualizar Views", command=self.visualizar_views)
        menu_bar.add_cascade(label="Views", menu=views_menu)

        # Menu Penalizações e Prioridade
        prioridade_menu = tk.Menu(menu_bar, tearoff=0)
        prioridade_menu.add_command(label="Consultar Prioridade", command=self.visualizar_penalizacoes)
        menu_bar.add_cascade(label="Penalizações e Prioridades", menu=prioridade_menu)

        # Menu Sobre
        about_menu = tk.Menu(menu_bar, tearoff=0)
        about_menu.add_command(label="Sobre", command=lambda: messagebox.showinfo("Sobre", "Aplicação CRUD com Tkinter e PyODBC"))
        menu_bar.add_cascade(label="Ajuda", menu=about_menu)

        self.root.config(menu=menu_bar)

    def connect_to_db(self):
        if self.conn:
            messagebox.showinfo("Ligação", "Já está ligado à base de dados.")
            return

        connect_window = tk.Toplevel(self.root)
        connect_window.title("Ligar à Base de Dados")

        tk.Label(connect_window, text="IP do Servidor:").pack(pady=5)
        ip_entry = tk.Entry(connect_window)
        ip_entry.pack(pady=5)

        tk.Label(connect_window, text="Utilizador:").pack(pady=5)
        user_entry = tk.Entry(connect_window)
        user_entry.pack(pady=5)

        tk.Label(connect_window, text="Password:").pack(pady=5)
        pass_entry = tk.Entry(connect_window, show="*")
        pass_entry.pack(pady=5)

        tk.Label(connect_window, text="Base de Dados:").pack(pady=5)
        db_entry = tk.Entry(connect_window)
        db_entry.pack(pady=5)

        def connect():
            try:
                ip = ip_entry.get()
                user = user_entry.get()
                password = pass_entry.get()
                database = db_entry.get()

                self.conn = pyodbc.connect(
                    f"DRIVER={{SQL Server}};SERVER={ip};DATABASE={database};UID={user};PWD={password}")
                self.cursor = self.conn.cursor()
                messagebox.showinfo("Sucesso", "Ligação efetuada com sucesso!")
                connect_window.destroy()
            except Exception as e:
                messagebox.showerror("Erro na ligação", f"Erro no acesso à base de dados: {e}")

        tk.Button(connect_window, text="Conectar", command=connect).pack(pady=10)

    def add_data(self):
        if self.cursor:
            table = simpledialog.askstring("Adicionar Dados", "Nome da Tabela:")
            columns = simpledialog.askstring("Adicionar Dados", "Colunas (separadas por vírgula):")
            values = simpledialog.askstring("Adicionar Dados", "Valores (separados por vírgula):")
            try:
                self.cursor.execute(f"INSERT INTO {table} ({columns}) VALUES ({values})")
                self.conn.commit()
                messagebox.showinfo("Sucesso", "Dados adicionados com sucesso!")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao adicionar dados: {e}")
        else:
            messagebox.showwarning("Aviso", "Precisa de se ligar à base de dados primeiro.")

    def update_data(self):
        if self.cursor:
            table = simpledialog.askstring("Atualizar Dados", "Nome da Tabela:")
            set_clause = simpledialog.askstring("Atualizar Dados", "SET (ex: coluna='valor'):")
            condition = simpledialog.askstring("Atualizar Dados", "Condição WHERE (opcional):")
            query = f"UPDATE {table} SET {set_clause}"
            if condition:
                query += f" WHERE {condition}"
            try:
                self.cursor.execute(query)
                self.conn.commit()
                messagebox.showinfo("Sucesso", "Dados atualizados com sucesso!")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao atualizar dados: {e}")
        else:
            messagebox.showwarning("Aviso", "Ligue-se à base de dados primeiro.")

    def delete_data(self):
        if self.cursor:
            table = simpledialog.askstring("Apagar Dados", "Nome da Tabela:")
            condition = simpledialog.askstring("Apagar Dados", "Condição WHERE:")
            try:
                self.cursor.execute(f"DELETE FROM {table} WHERE {condition}")
                self.conn.commit()
                messagebox.showinfo("Sucesso", "Dados apagados com sucesso!")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao apagar dados: {e}")
        else:
            messagebox.showwarning("Aviso", "Ligue-se à base de dados primeiro.")

    def view_data(self):
        if self.cursor:
            try:
                self.cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'")
                tables = [row.TABLE_NAME for row in self.cursor.fetchall()]

                def fetch_table_data():
                    selected_table = table_dropdown.get()
                    if selected_table:
                        self.cursor.execute(f"SELECT * FROM {selected_table}")
                        columns = [desc[0] for desc in self.cursor.description]
                        rows = self.cursor.fetchall()
                        output.delete("1.0", tk.END)
                        output.insert(tk.END, f"Colunas: {', '.join(columns)}\n\n")
                        for row in rows:
                            output.insert(tk.END, f"{row}\n")
                    else:
                        messagebox.showwarning("Aviso", "Selecione uma tabela.")

                view_window = tk.Toplevel(self.root)
                view_window.title("Visualizar Tabela")

                table_dropdown = ttk.Combobox(view_window, values=tables)
                table_dropdown.pack(pady=5)

                view_button = ttk.Button(view_window, text="Visualizar", command=fetch_table_data)
                view_button.pack(pady=5)

                output = scrolledtext.ScrolledText(view_window, width=80, height=20)
                output.pack(pady=5)

            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao obter tabelas: {e}")
        else:
            messagebox.showwarning("Aviso", "Ligue-se à base de dados primeiro.")

    def generic_query(self):
        if self.cursor:
            query = simpledialog.askstring("Query Genérica", "Escreva a query SQL:")
            try:
                self.cursor.execute(query)
                columns = [desc[0] for desc in self.cursor.description]
                rows = self.cursor.fetchall()

                result_window = tk.Toplevel(self.root)
                result_window.title("Resultados da Query Genérica")

                output = scrolledtext.ScrolledText(result_window, width=80, height=20)
                output.pack(pady=5)
                output.insert(tk.END, f"Colunas: {', '.join(columns)}\n\n")
                for row in rows:
                    output.insert(tk.END, f"{row}\n")

            except Exception as e:
                messagebox.showerror("Erro", f"Erro na execução da query: {e}")
        else:
            messagebox.showwarning("Aviso", "Ligue-se à base de dados primeiro.")

    def add_reserva(self):
        if self.cursor:
            try:
                # Criar uma janela para o registo da reserva
                reserva_window = tk.Toplevel(self.root)
                reserva_window.title("Criar Reserva")

                # Campos para inserção dos dados
                tk.Label(reserva_window, text="ID do Utilizador:").pack(pady=5)
                id_utilizador = tk.Entry(reserva_window)
                id_utilizador.pack(pady=5)

                tk.Label(reserva_window, text="Data de Início (YYYY-MM-DD HH:MM):").pack(pady=5)
                data_inicio = tk.Entry(reserva_window)
                data_inicio.pack(pady=5)

                tk.Label(reserva_window, text="Data de Fim (YYYY-MM-DD HH:MM):").pack(pady=5)
                data_fim = tk.Entry(reserva_window)
                data_fim.pack(pady=5)

                # Obter equipamentos disponíveis
                self.cursor.execute("SELECT ID_Equipamento, Nome_Equipamento, Estado_Equipamento FROM Equipamento")
                equipamentos = self.cursor.fetchall()

                if not equipamentos:
                    messagebox.showinfo("Informação", "Nenhum equipamento disponível no momento.")
                    return

                # Adicionar uma seção para listar equipamentos e checkbox para "Imprescindível"
                tk.Label(reserva_window, text="Selecione os Equipamentos e se são Imprescindíveis:").pack(pady=10)

                equipamento_frame = tk.Frame(reserva_window)
                equipamento_frame.pack(fill=tk.BOTH, expand=True)

                canvas = tk.Canvas(equipamento_frame)
                scrollbar = tk.Scrollbar(equipamento_frame, orient=tk.VERTICAL, command=canvas.yview)
                scrollable_frame = tk.Frame(canvas)

                scrollable_frame.bind(
                    "<Configure>",
                    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
                )

                canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
                canvas.configure(yscrollcommand=scrollbar.set)

                canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
                scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

                # Dicionários para armazenar seleção e imprescindibilidade
                equipamento_selecionado = {}
                imprescindivel_selecionado = {}

                for equipamento in equipamentos:
                    equipamento_id = equipamento[0]
                    equipamento_nome = equipamento[1]
                    estado_equipamento = equipamento[2]

                    # Checkbox para selecionar o equipamento
                    equipamento_selecionado[equipamento_id] = tk.IntVar()
                    tk.Checkbutton(
                        scrollable_frame,
                        text=f"{equipamento_nome} ({estado_equipamento})",
                        variable=equipamento_selecionado[equipamento_id]
                    ).pack(anchor="w", padx=20)

                    # Checkbox para marcar "Imprescindível"
                    imprescindivel_selecionado[equipamento_id] = tk.IntVar()
                    tk.Checkbutton(
                        scrollable_frame,
                        text="Imprescindível",
                        variable=imprescindivel_selecionado[equipamento_id]
                    ).pack(anchor="w", padx=40)

                def confirmar_reserva():
                    if not id_utilizador.get() or not data_inicio.get() or not data_fim.get():
                        messagebox.showwarning("Aviso", "Preencha todos os campos da reserva.")
                        return

                    try:
                        # Criar a reserva
                        estado = "active"
                        self.cursor.execute(
                            """
                            INSERT INTO Reserva (ID_Utilizador, Data_Inicio_Pedido, Data_Fim_Pedido, Estado)
                            VALUES (?, ?, ?, ?)
                            """,
                            (id_utilizador.get(), data_inicio.get(), data_fim.get(), estado),
                        )
                        self.conn.commit()

                        # Obter o ID da reserva recém-criada
                        self.cursor.execute("SELECT MAX(ID_Reserva) FROM Reserva")
                        id_reserva = self.cursor.fetchone()[0]

                        # Associar os equipamentos selecionados à reserva
                        for equipamento_id, var in equipamento_selecionado.items():
                            if var.get() == 1:  # Se o equipamento foi selecionado
                                imprescindivel = 'y' if imprescindivel_selecionado[equipamento_id].get() == 1 else 'n'
                                self.cursor.execute(
                                    """
                                    INSERT INTO ReservaEquipamento (ID_Reserva, ID_Equipamento, Imprescindivel)
                                    VALUES (?, ?, ?)
                                    """,
                                    (id_reserva, equipamento_id, imprescindivel),
                                )
                        self.conn.commit()

                        messagebox.showinfo("Sucesso", "Reserva criada com sucesso!")
                        reserva_window.destroy()

                    except Exception as e:
                        messagebox.showerror("Erro", f"Erro ao criar a reserva: {e}")

                # Botão para confirmar a reserva
                tk.Button(reserva_window, text="Confirmar Reserva", command=confirmar_reserva).pack(pady=20)

            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao criar a reserva: {e}")
        else:
            messagebox.showwarning("Aviso", "Precisa de se ligar à base de dados primeiro.")

    def alterar_estado_reserva(self):
        if self.cursor:
            try:
                # Solicita o ID da reserva e o novo estado
                id_reserva = simpledialog.askstring("Alterar Estado", "ID da Reserva:")
                novo_estado = simpledialog.askstring("Alterar Estado", "Novo Estado (satisfied, canceled, forgotten):")

                # Verifica se a reserva existe
                self.cursor.execute("""
                    SELECT ID_Reserva FROM Reserva WHERE ID_Reserva = ?
                """, (id_reserva,))
                reserva_existe = self.cursor.fetchone()

                if not reserva_existe:
                    messagebox.showwarning("Aviso", "Reserva não encontrada!")
                    return

                # Atualiza o estado da reserva
                self.cursor.execute("""
                    UPDATE Reserva
                    SET Estado = ?
                    WHERE ID_Reserva = ?
                """, (novo_estado, id_reserva))
                self.conn.commit()

                # Se o estado for "satisfied", chama o procedimento armazenado para gerar as requisições
                if novo_estado == "satisfied":
                    try:
                        # Chama o procedimento armazenado
                        self.cursor.execute("EXEC Reserve2Requisition ?", (id_reserva,))
                        self.conn.commit()

                        messagebox.showinfo("Sucesso", "Requisições geradas com sucesso para a reserva.")
                    except Exception as e:
                        messagebox.showerror("Erro", f"Erro ao gerar requisições: {e}")
                else:
                    messagebox.showinfo("Sucesso", "Estado da reserva atualizado com sucesso.")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao alterar o estado da reserva: {e}")
        else:
            messagebox.showwarning("Aviso", "Precisa de se ligar à base de dados primeiro.")

    def gerir_requisicoes(self):
        if self.cursor:
            try:
                # Criar janela para gerenciar requisições
                requisicoes_window = tk.Toplevel(self.root)
                requisicoes_window.title("Gerir Requisições")

                # Botão para registar uma requisição
                def registar_requisicao():
                    requisicao_window = tk.Toplevel(requisicoes_window)
                    requisicao_window.title("Registar Requisição")

                    tk.Label(requisicao_window, text="ID do Utilizador:").pack(pady=5)
                    id_utilizador_entry = tk.Entry(requisicao_window)
                    id_utilizador_entry.pack(pady=5)

                    # Obter equipamentos disponíveis
                    try:
                        self.cursor.execute("""
                            SELECT ID_Equipamento, Nome_Equipamento, Estado_Equipamento
                            FROM Equipamento
                            WHERE Estado_Equipamento = 'disponível'
                        """)
                        equipamentos = self.cursor.fetchall()

                        if not equipamentos:
                            messagebox.showinfo("Informação", "Nenhum equipamento disponível no momento.")
                            requisicao_window.destroy()
                            return

                        tk.Label(requisicao_window, text="Selecione o Equipamento:").pack(pady=5)
                        equipamento_var = tk.StringVar(requisicao_window)
                        equipamento_dropdown = ttk.Combobox(
                            requisicao_window,
                            textvariable=equipamento_var,
                            values=[f"{row[1]} (ID: {row[0]})" for row in equipamentos]
                        )
                        equipamento_dropdown.pack(pady=5)

                    except Exception as e:
                        messagebox.showerror("Erro", f"Erro ao carregar equipamentos: {e}")
                        requisicao_window.destroy()
                        return

                    tk.Label(requisicao_window, text="Estado da Requisição:").pack(pady=5)
                    estado_requisicao_entry = tk.Entry(requisicao_window)
                    estado_requisicao_entry.insert(0, "active")  # Estado padrão é 'active'
                    estado_requisicao_entry.pack(pady=5)

                    def confirmar_registo():
                        id_utilizador = id_utilizador_entry.get()
                        equipamento_selecionado = equipamento_var.get()
                        estado_requisicao = estado_requisicao_entry.get()

                        # Validar campos
                        if not id_utilizador or not equipamento_selecionado:
                            messagebox.showwarning("Aviso", "Preencha todos os campos obrigatórios!")
                            return

                        # Extrair ID do equipamento da seleção
                        try:
                            id_equipamento = equipamento_selecionado.split("ID: ")[1].strip(")")
                        except IndexError:
                            messagebox.showerror("Erro", "Erro ao processar o equipamento selecionado.")
                            return

                        try:
                            # Obter o próximo ID_Requisicao manualmente
                            self.cursor.execute("SELECT ISNULL(MAX(ID_Requisicao), 0) + 1 FROM Requisicao")
                            id_requisicao = self.cursor.fetchone()[0]

                            # Inserir a nova requisição
                            self.cursor.execute("""
                                INSERT INTO Requisicao (ID_Requisicao, ID_Equipamento, Estado_Requisicao, Data_Inicio_Requisicao, ID_Utilizador)
                                VALUES (?, ?, ?, GETDATE(), ?)
                            """, (id_requisicao, id_equipamento, estado_requisicao, id_utilizador))
                            self.conn.commit()
                            messagebox.showinfo("Sucesso", "Requisição registrada com sucesso!")
                            requisicao_window.destroy()
                        except Exception as e:
                            messagebox.showerror("Erro", f"Erro ao registar a requisição: {e}")

                    tk.Button(requisicao_window, text="Confirmar Requisição", command=confirmar_registo).pack(pady=10)

                # Botão para aceitar devolução
                def aceitar_devolucao():
                    devolucao_window = tk.Toplevel(requisicoes_window)
                    devolucao_window.title("Aceitar Devolução")

                    tk.Label(devolucao_window, text="ID da Requisição:").pack(pady=5)
                    id_requisicao_entry = tk.Entry(devolucao_window)
                    id_requisicao_entry.pack(pady=5)

                    def confirmar_devolucao():
                        id_requisicao = id_requisicao_entry.get()

                        if not id_requisicao:
                            messagebox.showwarning("Aviso", "O ID da requisição é obrigatório!")
                            return

                        try:
                            # Alterar o estado da requisição para 'closed'
                            self.cursor.execute("""
                                UPDATE Requisicao
                                SET Estado_Requisicao = 'closed', Data_Fim_Requisicao = GETDATE()
                                WHERE ID_Requisicao = ?
                            """, (id_requisicao,))
                            self.conn.commit()

                            # Alterar o estado do equipamento associado para 'disponível'
                            self.cursor.execute("""
                                UPDATE Equipamento
                                SET Estado_Equipamento = 'disponível'
                                WHERE ID_Equipamento IN (
                                    SELECT ID_Equipamento
                                    FROM Requisicao
                                    WHERE ID_Requisicao = ?
                                )
                            """, (id_requisicao,))
                            self.conn.commit()

                            messagebox.showinfo("Sucesso", "Devolução aceita com sucesso!")
                            devolucao_window.destroy()
                        except Exception as e:
                            messagebox.showerror("Erro", f"Erro ao aceitar a devolução: {e}")

                    tk.Button(devolucao_window, text="Confirmar Devolução", command=confirmar_devolucao).pack(pady=10)

                # Botões principais
                tk.Button(requisicoes_window, text="Registar Requisição", command=registar_requisicao).pack(pady=10)
                tk.Button(requisicoes_window, text="Aceitar Devolução", command=aceitar_devolucao).pack(pady=10)

            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao abrir a janela de gestão de requisições: {e}")
        else:
            messagebox.showwarning("Aviso", "Precisa de se ligar à base de dados primeiro.")

    def visualizar_views(self):
        if self.cursor:
            try:
                # Obter a lista de views do banco de dados
                self.cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.VIEWS")
                views = [row.TABLE_NAME for row in self.cursor.fetchall()]

                if not views:
                    messagebox.showinfo("Informação", "Nenhuma view encontrada no banco de dados.")
                    return

                # Criar uma nova janela para exibir as views
                views_window = tk.Toplevel(self.root)
                views_window.title("Visualizar Views")

                tk.Label(views_window, text="Selecione uma View:").pack(pady=5)

                view_dropdown = ttk.Combobox(views_window, values=views)
                view_dropdown.pack(pady=5)

                def fetch_view_data():
                    selected_view = view_dropdown.get()
                    if selected_view:
                        try:
                            self.cursor.execute(f"SELECT * FROM {selected_view}")
                            columns = [desc[0] for desc in self.cursor.description]
                            rows = self.cursor.fetchall()

                            output.delete("1.0", tk.END)
                            output.insert(tk.END, f"Colunas: {', '.join(columns)}\n\n")
                            for row in rows:
                                output.insert(tk.END, f"{row}\n")
                        except Exception as e:
                            messagebox.showerror("Erro", f"Erro ao buscar dados da view: {e}")
                    else:
                        messagebox.showwarning("Aviso", "Selecione uma view para visualizar.")

                view_button = ttk.Button(views_window, text="Visualizar Dados", command=fetch_view_data)
                view_button.pack(pady=10)

                output = scrolledtext.ScrolledText(views_window, width=80, height=20)
                output.pack(pady=5)

            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao buscar views: {e}")
        else:
            messagebox.showwarning("Aviso", "Conecte-se ao banco de dados primeiro.")

    def visualizar_penalizacoes(self):
        if self.cursor:
            try:
                id_utilizador = simpledialog.askstring("Visualizar Penalizações", "ID do Utilizador:")

                # Buscar penalizações associadas ao utilizador
                self.cursor.execute("""
                    SELECT P.Data_Penalizacao, P.Valor_Penalizacao, P.Motivo_Penalizacao, COALESCE(R.ID_Reserva, Re.ID_Requisicao) AS ID_Origem
                    FROM Penalizacao P
                    LEFT JOIN Reserva R ON P.ID_Reserva = R.ID_Reserva
                    LEFT JOIN Requisicao Re ON P.ID_Requisicao = Re.ID_Requisicao
                    WHERE R.ID_Utilizador = ? OR Re.ID_Utilizador = ?
                    ORDER BY P.Data_Penalizacao DESC
                """, (id_utilizador, id_utilizador))
                penalizacoes = self.cursor.fetchall()

                # Exibir penalizações
                if penalizacoes:
                    output = "\n".join(
                        [f"Data: {row[0]}, Valor: {row[1]}, Motivo: {row[2]}, Origem: {row[3]}" for row in
                         penalizacoes])
                    messagebox.showinfo("Penalizações", output)
                else:
                    messagebox.showinfo("Penalizações", "Nenhuma penalização encontrada para este utilizador.")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao buscar penalizações: {e}")
        else:
            messagebox.showwarning("Aviso", "Precisa de se ligar à base de dados primeiro.")

if __name__ == "__main__":
    root = tk.Tk()
    app = DatabaseApp(root)
    root.mainloop()
