import tkinter as tk
import sqlite3
from tkinter import messagebox, ttk
from datetime import datetime
import customtkinter as ctk


#-----------------------------------------------------------PALETA DE CORES------------------------------------------------------------------------------------#

#--------------------------------------------------------------------------------------------------------------------------------------------------------------#



# ============================================================
# 1. CONEXÃO COM O BANCO
# ============================================================
conexao = sqlite3.connect("estacionamento.db")
cursor = conexao.cursor()

# Tabela de clientes
cursor.execute("""
CREATE TABLE IF NOT EXISTS clientes (
    cpf TEXT PRIMARY KEY,
    nome TEXT NOT NULL,
    placa TEXT NOT NULL
)
""")

# Tabela de movimentação
cursor.execute("""
CREATE TABLE IF NOT EXISTS movimentacao (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data TEXT NOT NULL,
    hora_entrada TEXT NOT NULL,
    hora_saida TEXT,
    placa TEXT NOT NULL,
    tempo REAL,
    valor REAL,
    pagamento TEXT DEFAULT 'A Pagar'
)
""")

conexao.commit()

VALOR_HORA = 10.0

# ============================================================
# 2. FUNÇÕES CLIENTES (CRUD)
# ============================================================
def cadastrar_cliente():
    nome = entrada_nome.get().strip()
    cpf = entrada_cpf.get().strip()
    placa = entrada_placa.get().strip().upper()

    if nome == "" or cpf == "" or placa == "":
        messagebox.showerror("Erro", "Todos os campos devem ser preenchidos.")
        return

    if not cpf.isdigit():
        messagebox.showerror("Erro", "O CPF deve conter apenas números.")
        return

    if len(cpf) !=11:
        messagebox.showerror("Erro", "O CPF deve ter exatamente 11 caracteres")
        return
    if len(placa) !=7:
        messagebox.showerror("Erro", "A placa deve ter exatamente 7 caracteres")
        return
    
    try:
        cursor.execute("""
        INSERT INTO clientes (cpf, nome, placa)
        VALUES (?, ?, ?)
        """, (cpf, nome, placa))
        conexao.commit()
        messagebox.showinfo("Sucesso", "Cliente cadastrado com sucesso!")

        entrada_nome.delete(0, tk.END)
        entrada_cpf.delete(0, tk.END)
        entrada_placa.delete(0, tk.END)

    except sqlite3.IntegrityError:
        messagebox.showerror("Erro", "Este CPF já está cadastrado.")


def listar_clientes():
    lista_clientes.delete("1.0", tk.END)

    cursor.execute("SELECT cpf, nome, placa FROM clientes ORDER BY nome")
    registros = cursor.fetchall()

    if not registros:
        lista_clientes.insert(tk.END, "Nenhum cliente cadastrado.\n")
        return

    for cpf, nome, placa in registros:
        lista_clientes.insert(tk.END, f"CPF: {cpf} | Nome: {nome} | Placa: {placa}\n")


def atualizar_cliente():
    nome = entrada_nome.get().strip()
    cpf = entrada_cpf.get().strip()
    placa = entrada_placa.get().strip().upper()

    if nome == "" or cpf == "" or placa == "":
        messagebox.showerror("Erro", "Preencha nome, CPF e placa.")
        return

    cursor.execute("""
    UPDATE clientes
    SET nome = ?, placa = ?
    WHERE cpf = ?
    """, (nome, placa, cpf))
    conexao.commit()

    if cursor.rowcount == 0:
        messagebox.showerror("Erro", "Cliente não encontrado.")
    else:
        messagebox.showinfo("Sucesso", "Cliente atualizado com sucesso!")


def excluir_cliente():
    cpf = entrada_cpf.get().strip()

    if cpf == "":
        messagebox.showerror("Erro", "Informe o CPF.")
        return

    cursor.execute("DELETE FROM clientes WHERE cpf = ?", (cpf,))
    conexao.commit()

    if cursor.rowcount == 0:
        messagebox.showerror("Erro", "Cliente não encontrado.")
    else:
        messagebox.showinfo("Sucesso", "Cliente excluído com sucesso!")

# ============================================================
# 3. MOVIMENTAÇÃO
# ============================================================
def registrar_entrada():
    placa = entrada_mov_placa.get().strip().upper()

    if placa == "":
        messagebox.showerror("Erro", "Informe a placa.")
        return

    data = datetime.now().strftime("%d/%m/%Y")
    hora_entrada = datetime.now().strftime("%H:%M:%S")

    cursor.execute("""
    INSERT INTO movimentacao (data, hora_entrada, placa, pagamento)
    VALUES (?, ?, ?, ?)
    """, (data, hora_entrada, placa, "A Pagar"))
    conexao.commit()

    messagebox.showinfo("Sucesso", f"Entrada registrada às {hora_entrada}.")
    entrada_mov_placa.delete(0, tk.END)


def registrar_saida():
    placa = entrada_mov_placa.get().strip().upper()

    if placa == "":
        messagebox.showerror("Erro", "Informe a placa.")
        return

    cursor.execute("""
    SELECT id, data, hora_entrada
    FROM movimentacao
    WHERE placa = ? AND hora_saida IS NULL
    ORDER BY id DESC
    LIMIT 1
    """, (placa,))
    registro = cursor.fetchone()

    if not registro:
        messagebox.showerror("Erro", "Nenhuma entrada em aberto encontrada para esta placa.")
        return

    id_mov, data, hora_entrada = registro
    hora_saida = datetime.now().strftime("%H:%M:%S")

    dt_entrada = datetime.strptime(data + " " + hora_entrada, "%d/%m/%Y %H:%M:%S")
    dt_saida = datetime.strptime(data + " " + hora_saida, "%d/%m/%Y %H:%M:%S")

    tempo = (dt_saida - dt_entrada).total_seconds() / 3600

    if tempo <= 0:
        tempo = 1
    else:
        tempo = round(tempo, 2)

    valor = round(tempo * VALOR_HORA, 2)

    cursor.execute("""
    UPDATE movimentacao
    SET hora_saida = ?, tempo = ?, valor = ?
    WHERE id = ?
    """, (hora_saida, tempo, valor, id_mov))
    conexao.commit()

    messagebox.showinfo(
        "Sucesso",
        f"Saída registrada!\n\nHora Saída: {hora_saida}\nTempo: {tempo} hora(s)\nValor: R$ {valor:.2f}"
    )
    entrada_mov_placa.delete(0, tk.END)


def listar_movimentacao():
    lista_mov.delete("1.0", tk.END)

    cursor.execute("""
    SELECT id, data, hora_entrada, hora_saida, placa, tempo, valor, pagamento
    FROM movimentacao
    ORDER BY id DESC
    """)
    registros = cursor.fetchall()

    if not registros:
        lista_mov.insert(tk.END, "Nenhuma movimentação cadastrada.\n")
        return

    for r in registros:
        lista_mov.insert(tk.END, f"{r}\n")

# ============================================================
# 4. RECEBIMENTOS
# ============================================================
def listar_recebimentos_aberto():
    lista_recebimentos.delete("1.0", tk.END)

    cursor.execute("""
    SELECT id, placa, data, valor, pagamento
    FROM movimentacao
    WHERE valor IS NOT NULL AND pagamento = 'A Pagar'
    ORDER BY id DESC
    """)
    registros = cursor.fetchall()

    if not registros:
        lista_recebimentos.insert(tk.END, "Nenhum recebimento em aberto.\n")
        return

    for r in registros:
        lista_recebimentos.insert(tk.END, f"{r}\n")


def dar_baixa_pagamento():
    id_mov = entrada_recebimento_id.get().strip()

    if id_mov == "":
        messagebox.showerror("Erro", "Informe o ID da movimentação.")
        return

    cursor.execute("""
    UPDATE movimentacao
    SET pagamento = 'Recebido'
    WHERE id = ? AND valor IS NOT NULL
    """, (id_mov,))
    conexao.commit()

    if cursor.rowcount == 0:
        messagebox.showerror("Erro", "Movimentação não encontrada ou ainda sem valor calculado.")
    else:
        messagebox.showinfo("Sucesso", "Pagamento baixado com sucesso!")
        entrada_recebimento_id.delete(0, tk.END)
        listar_recebimentos_aberto()

# ============================================================
# 5. RELATÓRIOS
# ============================================================
def relatorio_clientes():
    texto_relatorios.delete("1.0", tk.END)

    cursor.execute("SELECT cpf, nome, placa FROM clientes ORDER BY nome")
    registros = cursor.fetchall()

    texto_relatorios.insert(tk.END, "RELATÓRIO DE CLIENTES\n\n")

    if not registros:
        texto_relatorios.insert(tk.END, "Nenhum cliente cadastrado.\n")
        return

    for r in registros:
        texto_relatorios.insert(tk.END, f"{r}\n")


def relatorio_abertos():
    texto_relatorios.delete("1.0", tk.END)

    cursor.execute("""
    SELECT id, placa, data, valor, pagamento
    FROM movimentacao
    WHERE pagamento = 'A Pagar' AND valor IS NOT NULL
    ORDER BY id DESC
    """)
    registros = cursor.fetchall()

    texto_relatorios.insert(tk.END, "RECEBIMENTOS EM ABERTO\n\n")

    if not registros:
        texto_relatorios.insert(tk.END, "Nenhum recebimento em aberto.\n")
        return

    for r in registros:
        texto_relatorios.insert(tk.END, f"{r}\n")


def relatorio_recebidos():
    texto_relatorios.delete("1.0", tk.END)

    cursor.execute("""
    SELECT id, placa, data, valor, pagamento
    FROM movimentacao
    WHERE pagamento = 'Recebido'
    ORDER BY id DESC
    """)
    registros = cursor.fetchall()

    texto_relatorios.insert(tk.END, "RECEBIMENTOS\n\n")

    if not registros:
        texto_relatorios.insert(tk.END, "Nenhum recebimento registrado.\n")
        return

    total = 0

    for r in registros:
        texto_relatorios.insert(tk.END, f"{r}\n")
        total += r[3]

    texto_relatorios.insert(tk.END, f"\nTOTAL RECEBIDO: R$ {total:.2f}\n")


def top_5_clientes():
    texto_relatorios.delete("1.0", tk.END)

    cursor.execute("""
    SELECT placa, COUNT(*) as total
    FROM movimentacao
    GROUP BY placa
    ORDER BY total DESC
    LIMIT 5
    """)
    registros = cursor.fetchall()

    texto_relatorios.insert(tk.END, "TOP 5 CLIENTES QUE MAIS USARAM O ESTACIONAMENTO\n\n")

    if not registros:
        texto_relatorios.insert(tk.END, "Nenhum registro encontrado.\n")
        return

    posicao = 1
    for placa, total in registros:
        texto_relatorios.insert(tk.END, f"{posicao}º - Placa: {placa} | Usos: {total}\n")
        posicao += 1

# ============================================================
# 6. JANELA PRINCIPAL
# ============================================================

preto           = "#0a0709"
azul_escuro     = "#0347ad"
branco          = "#fff4f0"
vermelho_vinho  = "#880d0d"
verde           = "#149903"


janela = ctk.CTk()
janela.title("Controle de Estacionamento")
janela.geometry("850x600")

abas = ttk.Notebook(janela)
abas.pack(expand=True, fill="both")

# ============================================================
# ABA CLIENTES
# ============================================================
aba_clientes = ctk.CTkFrame(abas, fg_color = "#B9B9B9")
aba_clientes.grid_columnconfigure(0, weight=1)
aba_clientes.grid_columnconfigure(1, weight=0)
aba_clientes.grid_columnconfigure(2, weight=1)
aba_clientes.grid_rowconfigure(6, weight=1)
abas.add(aba_clientes, text="Cadastro de Clientes")

#-----------------------------------------------------------------------FRAME DE FORMULARIOS-------------------------------------------------------------------#

frame_form = ctk.CTkFrame(aba_clientes, fg_color= "transparent")
frame_form.grid(row = 0, column = 0, sticky = "nw", padx = 20, pady = 20)

#--------------------------------------------------------------------------------------------------------------------------------------------------------------#

#-----------------------------------------------------------------LABELS e Entrys------------------------------------------------------------------------------#

ctk.CTkLabel(frame_form, text="Nome:", text_color = "#000000").grid(row=0, column=0, padx=(10,2), pady=5, sticky="e")
entrada_nome = ctk.CTkEntry(frame_form, width=300)
entrada_nome.configure(corner_radius = 15, fg_color = "#FFFFFF", text_color = "#000000")
entrada_nome.grid(row=0, column=1, padx=(2,10), pady=5, sticky = "w")

ctk.CTkLabel(frame_form, text="CPF:", text_color = "#000000").grid(row=1, column=0, padx=(10,2), pady=10, sticky="e")
entrada_cpf = ctk.CTkEntry(frame_form, width=300)
entrada_cpf.configure(corner_radius = 15, fg_color = "#FFFFFF", text_color = "#000000" )
entrada_cpf.grid(row=1, column=1, padx=(2,10), pady=10, sticky = "w")

ctk.CTkLabel(frame_form, text="Placa:", text_color = "#000000").grid(row=2, column=0, padx=(10,2), pady=10, sticky="e")
entrada_placa = ctk.CTkEntry(frame_form, width=300)
entrada_placa.configure(corner_radius = 15, fg_color = "#FFFFFF", text_color = "#000000")
entrada_placa.grid(row=2, column=1, padx=(2,10), pady=10, sticky = "w")

#--------------------------------------------------------------------------------------------------------------------------------------------------------------#

#-------------------------------------------------------------------FRAMES DE BOTÕES---------------------------------------------------------------------------#

frame_botoes = ctk.CTkFrame(aba_clientes,fg_color="transparent")
frame_botoes.grid(row = 3, column = 0, columnspan = 3, pady = 20)




ctk.CTkButton(frame_botoes, text="Listar", command=listar_clientes, width=120, fg_color = "#CF0505", corner_radius= 15, text_color = "#000000").grid(row=0, column=0, padx=5)
ctk.CTkButton(frame_botoes, text="Atualizar", command=atualizar_cliente, width=120, corner_radius=15, text_color = "#000000").grid(row=0, column=1, padx=5)

ctk.CTkButton(frame_botoes, text="Cadastrar", command=cadastrar_cliente, width=120, fg_color = verde, corner_radius= 15, text_color = '#000000' ).grid(row=1, column=0, padx=5, pady= 8)
ctk.CTkButton(frame_botoes, text="Excluir", command=excluir_cliente,width=120, fg_color = "#CF0505", corner_radius= 15, text_color = "#000000").grid(row=1, column=1, padx=5, pady = 8)

#--------------------------------------------------------------------------------------------------------------------------------------------------------------#

lista_clientes = tk.Text(aba_clientes, width=750, height=20)
lista_clientes.grid(row=5, column=0, columnspan=3, padx=10, pady=10)

# ============================================================
# ABA MOVIMENTAÇÃO
# ============================================================
aba_mov = tk.Frame(abas)
abas.add(aba_mov, text="Movimentação")
aba_mov.columnconfigure(0, weight= 1)
aba_mov.columnconfigure(1, weight= 0)
aba_mov.columnconfigure(2, weight= 1)

frame_movimentacao = ctk.CTkFrame(aba_mov, fg_color = "transparent")
frame_movimentacao.grid(row = 0, column = 0, columnspan = 3, pady = 20)

ctk.CTkLabel(frame_movimentacao, text="Placa:", text_color = "#000000").grid(row=0, column=0, padx=10, pady=10, sticky="w")
entrada_mov_placa = ctk.CTkEntry(frame_movimentacao, width=300)
entrada_mov_placa.configure(corner_radius= 15, fg_color = "#ffffff", text_color = "#000000")
entrada_mov_placa.grid(row=0, column=1, padx=10, pady=10)

ctk.CTkButton(frame_movimentacao, text="Registrar Entrada", command=registrar_entrada, width=20, corner_radius= 15, fg_color = "#FFFFFF", text_color= "#000000", border_color= "#000000").grid(row=1, column=0, padx=10, pady=10)
ctk.CTkButton(frame_movimentacao, text="Registrar Saída", command=registrar_saida, width=20, corner_radius= 15, fg_color= "#FFFFFF", text_color = "#000000", border_color= "#000000").grid(row=1, column=1, padx=10, pady=10)
ctk.CTkButton(frame_movimentacao, text="Listar Movimentações", command=listar_movimentacao, width=20, corner_radius= 15, fg_color= "#FFFFFF", text_color = "#000000", border_color= "#000000").grid(row=1, column=2, padx=10, pady=10)

lista_mov = tk.Text(aba_mov, width=95, height=25)
lista_mov.grid(row=2, column=0, columnspan=4, padx=10, pady=10)

# ============================================================
# ABA RECEBIMENTOS
# ============================================================
aba_recebimentos = tk.Frame(abas)
abas.add(aba_recebimentos, text="Recebimentos")


aba_recebimentos.columnconfigure(0, weight= 1)
aba_recebimentos.columnconfigure(1, weight=0)
aba_recebimentos.columnconfigure(2, weight=1)


frame_recebimentos = ctk.CTkFrame(aba_recebimentos, fg_color = "transparent")
frame_recebimentos.grid(row =  0, column = 0, columnspan = 3, pady = 20)


tk.Label(frame_recebimentos, text="ID da Movimentação:").grid(row=0, column=0, padx=10, pady=10, sticky="w")

entrada_recebimento_id = ctk.CTkEntry(frame_recebimentos, width=200)
entrada_recebimento_id.configure(corner_radius = 15, fg_color = "#ffffff", text_color = "#000000")
entrada_recebimento_id.grid(row=0, column=1, padx=10, pady=10)


ctk.CTkButton(frame_recebimentos, text="Listar em Aberto", command=listar_recebimentos_aberto, width=20, corner_radius = 15, fg_color = "#ffffff", text_color = "#000000").grid(row=1, column=0, padx=10, pady=10)
ctk.CTkButton(frame_recebimentos, text="Dar Baixa no Pagamento", command=dar_baixa_pagamento, width=20, corner_radius = 15, fg_color = "#ffffff", text_color = "#000000").grid(row=1, column=1, padx=10, pady=10)


lista_recebimentos = tk.Text(aba_recebimentos, width=95, height=25)
lista_recebimentos.grid(row=2, column=0, columnspan=4, padx=10, pady=10)

# ============================================================
# ABA RELATÓRIOS
# ============================================================
aba_relatorios = tk.Frame(abas)
abas.add(aba_relatorios, text="Relatórios")

aba_relatorios.columnconfigure(0, weight= 1)
aba_relatorios.columnconfigure(1, weight= 0)
aba_relatorios.columnconfigure(2, weight= 1)

frame_relatorios = ctk.CTkFrame(aba_relatorios, fg_color = "transparent")
frame_relatorios.grid(row = 0, column = 0, columnspan = 3, pady = 20)

ctk.CTkButton(frame_relatorios, text="Clientes", command=relatorio_clientes, width=20, fg_color = "#ffffff", corner_radius= 15, text_color = "#000000").grid(row=0, column=0, padx=10, pady=10)
ctk.CTkButton(frame_relatorios, text="Recebimentos em Aberto", command=relatorio_abertos, width=20, fg_color = "#ffffff", corner_radius= 15, text_color="#000000").grid(row=0, column=1, padx=10, pady=10)
ctk.CTkButton(frame_relatorios, text="Recebimentos", command=relatorio_recebidos, width=20, fg_color = "#ffffff", corner_radius= 15, text_color = "#000000").grid(row=0, column=2, padx=10, pady=10)
ctk.CTkButton(frame_relatorios, text="Top 5 Clientes", command=top_5_clientes, width=20, fg_color = "#ffffff", corner_radius= 15, text_color = "#000000").grid(row=0, column=3, padx=10, pady=10)

texto_relatorios = tk.Text(aba_relatorios, width=100, height=28)
texto_relatorios.grid(row=1, column=0, columnspan=4, padx=10, pady=10)

# ============================================================
# 7. INICIAR PROGRAMA
# ============================================================
janela.mainloop()
conexao.close()
