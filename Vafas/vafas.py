import tkinter as tk
import sqlite3
from tkinter import messagebox,ttk,filedialog
import matplotlib.pyplot as plt
from fpdf import FDPF

#----------------------------------------BANCO DE DADOS-------------------------------------------------------#

database = sqlite3.connect("vagas.db")
cursor = database.cursor()

#----Tabela de CLientes----#

cursor.execute("""
               
CREATE TABLE IF NOT EXISTS clientes (
    

    nome TEXT,
    cpf PRIMARY KEY INTEGER,
    placa VARCHAR,
    pagamento TEXT
)
""")

database.commit()
#----------------------------#

#------Tabela das Vagas------#


cursor.execute("""
               
CREATE TABLE IF NOT EXISTS vaga (
    
    id PRIMARY KEY INTEGER AUTOINCREMENT
    data TEXT,
    hora_entrada TEXT,
    hora_saida TEXT,
    placa VARHCAR
)
""")


database.commit()

#---------------------------#

#---------------------------------------------------------------------------------------------------------#

cadastro = 0
listar = 0
atualizar = 0
excluir = 0
registros = []
valor = 0



#-------------------------------------------------FUNÇÕES-------------------------------------------------------------#

def cadastro():
    
    
    nome            = entrada_nome.get.strip()
    cpf             = entrada_cpf.get.strip()
    placa           = entrada_placa.get.strip()
    data            = entrada_data.get.strip()
    hora_entrada    = entrada_hora_inicio.get().strip()
    hora_saida      = entrada_hora_saida.get().strip()
    tempo           = entrada_tempo.get().strip()
    pagamento       = entrada_pag.get().strip()
    
    if nome == "" or cpf == "" or placa == "" or data == "" == hora_entrada == "" or hora_saida == "" or tempo == "" or pagamento == "":
        
        messagebox.showerror("Erro", "Todos os campos devem ser preenchidos")
        return
    try:
        float(tempo)
    except ValueError:
        messagebox.showerror("Erro","O valor colocado deve ser em número.")
    
    cursor.execute("""
                   
    INSERT INTO clientes (nome,cpf,placa,tempo,pagamento)
    VALUES (?,?,?,?,?)
    """,(nome,cpf,placa,float(tempo),pagamento))
    database.commit()
    messagebox.showinfo("Sucesso","Cadastro do Cliente feito com sucesso!")
    
    
def listar():
    
    cursor.execute("SELECT * FROM clientes")
    registros = cursor.fetchall()
    listagem.delete(1.0, tk.END)
    for r in registros:
        
        listagem.insert(tk.END, f"{r}\n")
        
        
def atualizar():
    
    cpf_cadastrado = entrada_cpf.get().strip()
    novo_pagamento = entrada_pag.get().strip()
    
    if cpf_cadastrado  == "" or not cpf_cadastrado.isdigit():
        
        messagebox.showerror("Erro","O CPF deve conter somente números.")
        return
    if novo_pagamento not in ["Recebido", "A Pagar"]:
        
        messagebox.showerror("Erro","O Pagamento deve ser 'Recebido' ou 'A Pagar'.")
        
    cursor.execute("UPDATE clientes SET pagamento = ? WHERE cpf = ? ", (novo_pagamento, cpf_cadastrado))
    database.commit()
    messagebox.showinfo("Sucesso","Pagamento atualizado com Sucesso!")
    
def excluir():
    
    cpf_cadastrado = entrada_cpf.get().strip()
    
    if cpf_cadastrado == "" or not cpf_cadastrado.isdigit():
        messagebox.showerror("Erro","O CPF deve conter apenas números.")
        return
    
    cursor.execute("DELETE FROM clientes WHERE cpf = ?", (cpf_cadastrado))
    database.commit()
    messagebox.showinfo("Sucesso","O cliente foi excluído com sucesso!")
    
    
#-------------------------FUNÇÃO DE RELATÓRIOS--------------------#

def pagamentos_pendentes():
    
    
    cursor.execute("SELECT *  FROM clientes WHERE pagamento = 'A pagar'")
    registros = cursor.fetchall()
    relatorio_pag.delete("1.0", tk.END)
    relatorio_pag.insert(tk.END, f"{r}\n")
    
def pagamentos_recebidos():
    
    cursor.execute("SELECT pagamento FROM clientes GROUP BY pagamentos")
    registros = cursor.fetchall()
    relatorio_pag.delete("1.0", tk.END)
    relatorio.pag.insert(tk.END, f"{r[0]}:  R$ {r[1]:.2f}\n")