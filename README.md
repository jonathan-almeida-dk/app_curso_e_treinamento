# 📊 Sistema de Gestão de Treinamentos - HAIRAM

## 📌 Sobre o projeto

Este é um sistema interno desenvolvido em Python utilizando Streamlit para gerenciar treinamentos obrigatórios de colaboradores.

O objetivo principal é facilitar o controle de:

* Treinamentos pendentes
* Treinamentos concluídos
* Treinamentos atrasados
* Datas de vencimento
* Evidências de conclusão

O sistema foi pensado para uso corporativo simples, com foco em praticidade para gestores e equipe de RH.

---

## ⚙️ Tecnologias utilizadas

* Python
* Streamlit (interface web)
* SQLite (banco de dados local)
* Pandas (manipulação de dados)
* SQLAlchemy (conexão com banco)
* Dotenv (variáveis de ambiente)

---

## 🧠 Como funciona

O sistema permite:

### 🔹 Cadastro e importação

* Importar planilhas CSV ou Excel com dados de treinamentos
* Cadastrar manualmente colaboradores e treinamentos

### 🔹 Controle automático

* Cálculo automático de vencimento com base na periodicidade
* Classificação dos treinamentos em:

  * 🟢 Concluído
  * 🟡 Pendente
  * 🔴 Atrasado

### 🔹 Atualização de status

* O gestor pode registrar a conclusão dos treinamentos
* Adicionar evidências (links ou observações)

### 🔹 Visualização

* Dashboard com resumo geral
* Filtros por função e status
* Tabelas organizadas e coloridas para fácil leitura

### 🔹 Notificações

* Envio de e-mail para o gestor ao agendar treinamentos
* Possibilidade de envio de resumo geral

---

## 👥 Perfis de acesso

O sistema possui dois perfis:

* **Gestor**

  * Controle total
  * Cadastro e atualização de treinamentos
  * Recebimento de notificações

* **RH**

  * Visualização dos dados
  * Cadastro de treinamentos e colaboradores
  * Acompanhamento dos treinamentos

---

## 🚀 Como executar o projeto

1. Instale as dependências:

```
pip install -r requirements.txt
```

2. Execute o sistema:

```
streamlit run app.py
```

3. Acesse no navegador:

```
http://localhost:8501
```

---

## 🔐 Observações

* O sistema roda localmente (localhost)
* Não utiliza HTTPS por padrão (uso interno)
* Dados são armazenados em banco SQLite local

---

## 📈 Objetivo

Este projeto foi desenvolvido com foco em:

* Organização de treinamentos obrigatórios
* Redução de atrasos
* Melhor controle gerencial
* Simplicidade de uso no dia a dia

---

## 🏁 Status do projeto

🚧 Em desenvolvimento
Melhorias futuras incluem:

* Controle de usuários mais robusto
* Deploy em servidor
* Melhorias de interface
* Relatórios avançados

---

## 📄 Licença

Projeto de uso interno corporativo.
