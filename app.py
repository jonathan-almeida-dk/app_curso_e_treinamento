# app.py
"""
Streamlit app simples para importar treinamentos, visualizar pendentes e marcar como concluídos.
Banco: SQLite (trainings.db)
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
import subprocess
import sys

load_dotenv()

# Conexão SQLite (arquivo local)
engine = create_engine('sqlite:///trainings.db', echo=False)
# Usuários do sistema (protótipo interno)
USUARIOS = {
    "gestor": {
        "senha": "gestor123",
        "perfil": "gestor",
        "nome": "Administrador"
    },
    "rh": {
        "senha": "rh123",
        "perfil": "rh",
        "nome": "Equipe de RH"
    }
}

def inicializar_sessao():
    if "logado" not in st.session_state:
        st.session_state["logado"] = False
    if "usuario" not in st.session_state:
        st.session_state["usuario"] = ""
    if "perfil" not in st.session_state:
        st.session_state["perfil"] = ""
    if "nome_exibicao" not in st.session_state:
        st.session_state["nome_exibicao"] = ""


def aplicar_estilo_login():
    st.markdown("""
    <style>

    div.stButton > button,
        div[data-testid="stFormSubmitButton"] > button {
            width: 100%;
            border-radius: 10px;
            font-weight: 600;
            height: 44px;
            background-color: #1f6feb;
            color: white;
            border: none;
        }

        div.stButton > button:hover,
        div[data-testid="stFormSubmitButton"] > button:hover {
            background-color: #388bfd;
        }

    .login-title {
        text-align: center;
        font-size: 30px;
        font-weight: 700;
        margin-bottom: 8px;
    }

    .login-subtitle {
        text-align: center;
        font-size: 15px;
        color: #b0b7c3;
        margin-bottom: 24px;
    }

    .login-footer {
        text-align: center;
        font-size: 13px;
        color: #9aa3af;
        margin-top: 18px;
    }

    div[data-testid="stForm"] {
        border: none !important;
        background: transparent !important;
        box-shadow: none !important;
        padding: 0 !important;
    }

    div[data-testid="stTextInput"] > div {
        border-radius: 10px;
    }

    div.stButton > button,
    div[data-testid="stFormSubmitButton"] > button {
        width: 100%;
        border-radius: 10px;
        font-weight: 600;
        height: 44px;
    }
                
    input:focus {
    outline: none !important;
    box-shadow: 0 0 0 2px #1f6feb !important;
    }
                
    </style>
    """, unsafe_allow_html=True)

def tela_login():
    aplicar_estilo_login()

    col1, col2, col3 = st.columns([1, 1.2, 1])

    with col2:
        col_logo1, col_logo2, col_logo3 = st.columns([1, 2, 1])

        with col_logo2:
            st.image("assets/logo.png", width=120)

        st.markdown('<div class="login-title">📊 Sistema de Treinamentos</div>', unsafe_allow_html=True)
        st.markdown('<div class="login-subtitle"><b>HAIRAM</b> • Sistema interno de treinamentos</div>', unsafe_allow_html=True)

        with st.form("login_form"):
            usuario = st.text_input("Usuário", placeholder="Digite seu usuário")
            senha = st.text_input("Senha", type="password", placeholder="Digite sua senha")

            submitted = st.form_submit_button("Entrar no sistema")

            if submitted:
                if usuario in USUARIOS and USUARIOS[usuario]["senha"] == senha:
                    st.session_state["logado"] = True
                    st.session_state["usuario"] = usuario
                    st.session_state["perfil"] = USUARIOS[usuario]["perfil"]
                    st.session_state["nome_exibicao"] = USUARIOS[usuario]["nome"]
                    st.success("Login realizado com sucesso.")
                    st.rerun()
                else:
                    st.error("Usuário ou senha inválidos.")

        st.markdown('<div class="login-footer">Acesso restrito a usuários autorizados</div>', unsafe_allow_html=True)

def botao_logout():
    if st.sidebar.button("Sair do sistema"):
        st.session_state["logado"] = False
        st.session_state["usuario"] = ""
        st.session_state["perfil"] = ""
        st.session_state["nome_exibicao"] = ""
        st.rerun()

# Inicializa DB se não existir
def init_db():
    with engine.begin() as conn:
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS employees (
            employee_id TEXT PRIMARY KEY,
            employee_name TEXT,
            role TEXT,
            email TEXT
        );
        """))
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS courses (
            course_id TEXT PRIMARY KEY,
            course_name TEXT,
            duration_minutes INTEGER
        );
        """))
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS trainings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id TEXT,
            course_id TEXT,
            date_scheduled TEXT,
            date_completed TEXT,
            frequency_months INTEGER,
            evidence TEXT,
            FOREIGN KEY(employee_id) REFERENCES employees(employee_id),
            FOREIGN KEY(course_id) REFERENCES courses(course_id)
        );
        """))

# Função para importar CSV/XLSX e salvar no DB
def import_file(uploaded):
    if uploaded.name.endswith('xlsx'):
        df = pd.read_excel(uploaded)
    else:
        df = pd.read_csv(uploaded)
    # Normalizar colunas mínimas esperadas
    expected = ['employee_id','employee_name','role','email','course_id','course','date_scheduled','date_completed','frequency_months','evidence']
    for col in expected:
        if col not in df.columns:
            df[col] = None
    # Salvar employees e courses e trainings
    with engine.begin() as conn:
        for _, row in df.iterrows():
            conn.execute(text("""
                INSERT OR REPLACE INTO employees (employee_id, employee_name, role, email)
                VALUES (:employee_id, :employee_name, :role, :email)
            """), dict(employee_id=str(row['employee_id']), employee_name=row['employee_name'] or '',
                     role=row['role'] or '', email=row['email'] or ''))
            conn.execute(text("""
                INSERT OR REPLACE INTO courses (course_id, course_name)
                VALUES (:course_id, :course_name)
            """), dict(course_id=str(row['course_id']), course_name=row['course'] or ''))
            conn.execute(text("""
                INSERT INTO trainings (employee_id, course_id, date_scheduled, date_completed, frequency_months, evidence)
                VALUES (:employee_id, :course_id, :date_scheduled, :date_completed, :frequency_months, :evidence)
            """), dict(employee_id=str(row['employee_id']), course_id=str(row['course_id']),
                       date_scheduled=str(row['date_scheduled']) if pd.notna(row['date_scheduled']) else None,
                       date_completed=str(row['date_completed']) if pd.notna(row['date_completed']) else None,
                       frequency_months=int(row['frequency_months']) if pd.notna(row['frequency_months']) else None,
                       evidence=row['evidence'] or None))
    st.success("Importação concluída")

def compute_status(df_trainings):
    today = datetime.today().date()
    rows = []

    for _, t in df_trainings.iterrows():
        date_scheduled = None
        date_completed = None

        if pd.notna(t['date_scheduled']) and str(t['date_scheduled']).strip() != "":
            try:
                date_scheduled = datetime.fromisoformat(str(t['date_scheduled'])).date()
            except:
                date_scheduled = None

        if pd.notna(t['date_completed']) and str(t['date_completed']).strip() != "":
            try:
                date_completed = datetime.fromisoformat(str(t['date_completed'])).date()
            except:
                date_completed = None

        due_date = None

        # Se já concluiu, calcula o próximo vencimento com base na conclusão
        if date_completed:
            status = "Concluído"

            if pd.notna(t['frequency_months']) and int(t['frequency_months']) > 0:
                month = date_completed.month - 1 + int(t['frequency_months'])
                year = date_completed.year + month // 12
                month = month % 12 + 1
                day = min(date_completed.day, 28)
                due_date = datetime(year, month, day).date()

        # Se ainda não concluiu, o prazo é a própria data agendada
        else:
            status = "Pendente"
            due_date = date_scheduled

        days_overdue = None
        if due_date:
            if today > due_date and status == "Pendente":
                status = "Atrasado"
                days_overdue = (today - due_date).days
            else:
                days_overdue = (due_date - today).days

        rows.append({
            'training_id': t['id'],
            'employee_id': t['employee_id'],
            'employee_name': t['employee_name'],
            'role': t['role'],
            'course_id': t['course_id'],
            'course_name': t['course_name'],
            'date_scheduled': t['date_scheduled'],
            'date_completed': t['date_completed'],
            'frequency_months': t['frequency_months'],
            'due_date': due_date.isoformat() if due_date else None,
            'status': status,
            'days_overdue': days_overdue,
            'evidence': t['evidence']
        })

    return pd.DataFrame(rows)
def preparar_tabela_exibicao(df_base):
    df_exibir = df_base.copy()

    def texto_prazo(row):
        if pd.isna(row["days_overdue"]):
            return "-"
        if row["status"] == "Atrasado":
            return f'{int(abs(row["days_overdue"]))} dia(s) de atraso'
        elif row["status"] == "Pendente":
            return f'{int(row["days_overdue"])} dia(s) restantes'
        elif row["status"] == "Concluído":
            return "Concluído"
        return "-"

    df_exibir["prazo_texto"] = df_exibir.apply(texto_prazo, axis=1)

    df_exibir = df_exibir[
        [
            "employee_name",
            "role",
            "course_name",
            "date_scheduled",
            "date_completed",
            "due_date",
            "status",
            "prazo_texto",
            "evidence"
        ]
        ]
    # Converter datas para formato brasileiro (DD/MM/AAAA)
    for col in ["date_scheduled", "date_completed", "due_date"]:
        df_exibir[col] = pd.to_datetime(df_exibir[col], errors="coerce").dt.strftime("%d/%m/%Y")
        df_exibir[col] = df_exibir[col].fillna("-")
        
    df_exibir = df_exibir.rename(columns={
        "employee_name": "Colaborador",
        "role": "Função",
        "course_name": "Treinamento",
        "date_scheduled": "Data Prevista",
        "date_completed": "Data de Conclusão",
        "due_date": "Próximo Vencimento",
        "status": "Situação",
        "prazo_texto": "Prazo / Atraso",
        "evidence": "Evidência"
    })

    ordem_status = {
        "Atrasado": 0,
        "Pendente": 1,
        "Concluído": 2
    }

    df_exibir["ordem_status"] = df_exibir["Situação"].map(ordem_status)
    df_exibir = df_exibir.sort_values(by=["ordem_status", "Próximo Vencimento"], na_position="last")
    df_exibir = df_exibir.drop(columns=["ordem_status"])

    return df_exibir

def colorir_situacao(valor):
    if valor == "Atrasado":
        return "background-color: #f8d7da; color: #842029; font-weight: bold;"
    elif valor == "Pendente":
        return "background-color: #fff3cd; color: #664d03; font-weight: bold;"
    elif valor == "Concluído":
        return "background-color: #d1e7dd; color: #0f5132; font-weight: bold;"
    return ""

def colorir_prazo(valor):
    texto = str(valor)
    if "atraso" in texto.lower():
        return "background-color: #f8d7da; color: #842029; font-weight: bold;"
    elif "restantes" in texto.lower():
        return "background-color: #fff3cd; color: #664d03; font-weight: bold;"
    elif "concluído" in texto.lower():
        return "background-color: #d1e7dd; color: #0f5132; font-weight: bold;"
    return ""

def estilizar_tabela(df):
    return (
        df.style
        .map(colorir_situacao, subset=["Situação"])
        .map(colorir_prazo, subset=["Prazo / Atraso"])
    )
def enviar_email_gestor_novo_treinamento(emp_name, emp_role, course_name, date_scheduled, freq):
    gestor_email = os.getenv("GESTOR_EMAIL")

    if not gestor_email:
        raise ValueError("GESTOR_EMAIL não foi definido no arquivo .env")

    from notify import send_email

    assunto = "[HAIRAM] Novo treinamento agendado"

    mensagem = f"""
Olá,

Um novo treinamento foi agendado no sistema.

Colaborador: {emp_name}
Função: {emp_role}
Treinamento: {course_name}
Data agendada: {date_scheduled}
Periodicidade: {freq} mês(es)

Acesse o sistema para acompanhar os detalhes.

Equipe de Qualidade
"""
    send_email(gestor_email, assunto, mensagem)

def importar_csv_inicial_se_banco_vazio():
    caminho_csv = "sample_import.csv"

    with engine.begin() as conn:
        resultado = conn.execute(text("SELECT COUNT(*) FROM trainings"))
        total = resultado.scalar()

    if total == 0 and os.path.exists(caminho_csv):
        try:
            df = pd.read_csv(caminho_csv)

            expected = [
                'employee_id', 'employee_name', 'role',
                'email', 'course_id', 'course',
                'date_scheduled', 'date_completed',
                'frequency_months', 'evidence'
            ]

            for col in expected:
                if col not in df.columns:
                    df[col] = None

            with engine.begin() as conn:
                for _, row in df.iterrows():
                    conn.execute(text("""
                        INSERT OR REPLACE INTO employees (employee_id, employee_name, role, email)
                        VALUES (:employee_id, :employee_name, :role, :email)
                    """), dict(
                        employee_id=str(row['employee_id']),
                        employee_name=row['employee_name'] or '',
                        role=row['role'] or '',
                        email=row['email'] if 'email' in row and pd.notna(row['email']) else None
                    ))

                    conn.execute(text("""
                        INSERT OR REPLACE INTO courses (course_id, course_name)
                        VALUES (:course_id, :course_name)
                    """), dict(
                        course_id=str(row['course_id']),
                        course_name=row['course'] or ''
                    ))

                    conn.execute(text("""
                        INSERT INTO trainings (employee_id, course_id, date_scheduled, date_completed, frequency_months, evidence)
                        VALUES (:employee_id, :course_id, :date_scheduled, :date_completed, :frequency_months, :evidence)
                    """), dict(
                        employee_id=str(row['employee_id']),
                        course_id=str(row['course_id']),
                        date_scheduled=str(row['date_scheduled']) if pd.notna(row['date_scheduled']) else None,
                        date_completed=str(row['date_completed']) if pd.notna(row['date_completed']) else None,
                        frequency_months=int(row['frequency_months']) if pd.notna(row['frequency_months']) else None,
                        evidence=row['evidence'] if pd.notna(row['evidence']) else None
                    ))

            return True

        except Exception as e:
            st.error(f"Erro ao importar dados iniciais automaticamente: {e}")

    return False

    send_email(gestor_email, assunto, mensagem)
# Interface Streamlit
def main():
    inicializar_sessao()

    if not st.session_state["logado"]:
        tela_login()
        return
    st.sidebar.success(f"Usuário: {st.session_state['nome_exibicao']}")
    st.sidebar.info(f"Perfil: {st.session_state['perfil'].upper()}")
    botao_logout()
    st.title("Sistema de Gestão de Treinamentos - HAIRAM")
    st.caption("Acompanhamento de treinamentos obrigatórios, pendências, atrasos e conclusões.")
    st.markdown("---")
    init_db()
    with engine.begin() as conn:
        conn.execute(text("""
            DELETE FROM employees
            WHERE employee_name IS NULL OR employee_name = ''
            OR role IS NULL OR role = ''
        """))
    importar_csv_inicial_se_banco_vazio()
    st.sidebar.header("Menu de operações")
    uploaded = st.sidebar.file_uploader("Importar planilha de treinamentos (CSV/XLSX)", type=['csv','xlsx'])
    
    if st.sidebar.button("🔄 Atualizar dados"):
        st.rerun()
    if uploaded:
        import_file(uploaded)

    st.sidebar.markdown("### Filtros de consulta")
    role_filter = st.sidebar.text_input("Filtrar por função", "")
    status_filter = st.sidebar.selectbox("Situação", ["Todos", "Pendente", "Atrasado", "Concluído"])
    # Carregar dados combinados para exibição
    df = pd.read_sql("""
        SELECT t.*, e.employee_name, e.role, c.course_name
        FROM trainings t
        LEFT JOIN employees e ON t.employee_id = e.employee_id
        LEFT JOIN courses c ON t.course_id = c.course_id
    """, engine)

    if df.empty:
        st.info("Nenhum treinamento foi encontrado. Importe uma planilha ou realize um agendamento manual.")
    else:
        df_status = compute_status(df)
        # aplicar filtros
        if role_filter:
            df_status = df_status[df_status['role'].str.contains(role_filter, case=False, na=False)]
        if status_filter != "Todos":
            df_status = df_status[df_status['status'] == status_filter]

        st.subheader("Resumo gerencial")
        
        col1, col2, col3, col4 = st.columns(4)

        total_registros = len(df_status)
        total_atrasados = int((df_status['status'] == 'Atrasado').sum())
        total_pendentes = int((df_status['status'] == 'Pendente').sum())
        total_concluidos = int((df_status['status'] == 'Concluído').sum())

        with col1:
            st.metric("📋 Total de registros", total_registros)

        with col2:
            st.metric("🔴 Treinamentos atrasados", total_atrasados)

        with col3:
            st.metric("🟡 Treinamentos pendentes", total_pendentes)

        with col4:
            st.metric("🟢 Treinamentos concluídos", total_concluidos)

        st.subheader("Painel de Treinamentos")

        if total_atrasados > 0:
            st.error(f"Atenção: existem {total_atrasados} treinamento(s) atrasado(s) que exigem ação imediata.")

        if total_pendentes > 0:
            st.warning(f"Existem {total_pendentes} treinamento(s) pendente(s) aguardando acompanhamento.")

        if total_concluidos > 0:
            st.success(f"{total_concluidos} treinamento(s) já foram concluído(s).")

        st.markdown("### Legenda de status")
        col_leg1, col_leg2, col_leg3 = st.columns(3)

        with col_leg1:
            st.error("🔴 Atrasado")
        with col_leg2:
            st.warning("🟡 Pendente")
        with col_leg3:
            st.success("🟢 Concluído")

        tab1, tab2, tab3, tab4 = st.tabs([
            "📋 Visão Geral",
            "🔴 Atrasados",
            "🟡 Pendentes",
            "🟢 Concluídos"
        ])

        with tab1:
            st.subheader("Visão geral dos treinamentos cadastrados")
            tabela_geral = preparar_tabela_exibicao(df_status)
            st.dataframe(estilizar_tabela(tabela_geral), use_container_width=True, hide_index=True)

        with tab2:
            st.subheader("Treinamentos em atraso")
            df_atrasados = df_status[df_status["status"] == "Atrasado"]
            if df_atrasados.empty:
                st.info("Não há treinamentos atrasados.")
            else:
                tabela_atrasados = preparar_tabela_exibicao(df_atrasados)
                st.dataframe(estilizar_tabela(tabela_atrasados), use_container_width=True, hide_index=True)

        with tab3:
            st.subheader("Treinamentos pendentes")
            df_pendentes = df_status[df_status["status"] == "Pendente"]
            if df_pendentes.empty:
                st.info("Não há treinamentos pendentes.")
            else:
                tabela_pendentes = preparar_tabela_exibicao(df_pendentes)
                st.dataframe(estilizar_tabela(tabela_pendentes), use_container_width=True, hide_index=True)

        with tab4:
            st.subheader("Treinamentos concluídos")
            df_concluidos = df_status[df_status["status"] == "Concluído"]
            if df_concluidos.empty:
                st.info("Não há treinamentos concluídos.")
            else:
                tabela_concluidos = preparar_tabela_exibicao(df_concluidos)
                st.dataframe(estilizar_tabela(tabela_concluidos), use_container_width=True, hide_index=True)

        if st.session_state["perfil"] == "gestor":
            st.subheader("Atualizar conclusão de treinamento")

            df_pendentes_gestor = df_status[df_status["status"].isin(["Pendente", "Atrasado"])].copy()

            if df_pendentes_gestor.empty:
                st.info("Não há treinamentos pendentes ou atrasados para atualização.")
            else:
                df_pendentes_gestor["opcao_exibicao"] = df_pendentes_gestor.apply(
                    lambda row: f'{row["employee_name"]} | {row["course_name"]} | Situação: {row["status"]} | Vencimento: {row["due_date"] if pd.notna(row["due_date"]) else "Não informado"}',
                    axis=1
                )

                opcoes_treinamento = dict(
                    zip(df_pendentes_gestor["opcao_exibicao"], df_pendentes_gestor["training_id"])
                )

                with st.form("mark_complete"):
                    st.write("Selecione abaixo o treinamento que foi concluído.")

                    treinamento_escolhido = st.selectbox(
                        "Treinamento pendente/atrasado",
                        options=list(opcoes_treinamento.keys())
                    )

                    completed_date = st.date_input("Data de conclusão", datetime.today().date())
                    evidence = st.text_input("Link ou observação de evidência")
                    submitted = st.form_submit_button("Registrar conclusão")

                    if submitted:
                        if st.session_state["perfil"] != "gestor":
                            st.error("Você não tem permissão para realizar essa ação.")
                        else:
                            training_id = opcoes_treinamento[treinamento_escolhido]

                            with engine.begin() as conn:
                                conn.execute(text("""
                                    UPDATE trainings
                                    SET date_completed = :dc, evidence = :ev
                                    WHERE id = :tid
                                """), dict(
                                    dc=completed_date.isoformat(),
                                    ev=evidence,
                                    tid=int(training_id)
                                ))

                            st.success("Conclusão registrada com sucesso.")
                            st.rerun()

            st.subheader("Notificações ao gestor")
            if st.button("Enviar resumo de treinamentos ao gestor"):
                try:
                    resultado = subprocess.run(
                        [sys.executable, "notify.py"],
                        capture_output=True,
                        text=True
                    )

                    if resultado.returncode == 0:
                        st.success("Resumo enviado ao gestor com sucesso.")
                        if resultado.stdout:
                            st.text(resultado.stdout)
                    else:
                        st.error("Houve um erro ao executar o envio do resumo.")
                        if resultado.stderr:
                            st.text(resultado.stderr)

                except Exception as e:
                    st.error(f"Erro ao executar notify.py: {e}")

        st.subheader("Cadastro de colaboradores")
        with st.form("add_employee"):
            novo_emp_id = st.text_input("ID do colaborador")
            novo_emp_name = st.text_input("Nome do colaborador")
            novo_emp_role = st.text_input("Função")

            salvar_colaborador = st.form_submit_button("Salvar colaborador")

            if salvar_colaborador:
                if not novo_emp_id or not novo_emp_name or not novo_emp_role:
                    st.warning("Preencha todos os campos do colaborador.")
                else:
                    try:
                        with engine.begin() as conn:
                            conn.execute(text("""
                                INSERT OR REPLACE INTO employees (employee_id, employee_name, role)
                                VALUES (:employee_id, :employee_name, :role)
                            """), dict(
                                employee_id=str(novo_emp_id),
                                employee_name=novo_emp_name.strip(),
                                role=novo_emp_role.strip()
                            ))

                        st.success("Colaborador cadastrado com sucesso.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao cadastrar colaborador: {e}")
        st.subheader("Cadastro de treinamentos")
        with st.form("add_course"):
            novo_course_id = st.text_input("ID do treinamento")
            novo_course_name = st.text_input("Nome do treinamento")

            salvar_treinamento = st.form_submit_button("Salvar treinamento")

            if salvar_treinamento:
                if not novo_course_id or not novo_course_name:
                    st.warning("Preencha todos os campos do treinamento.")
                else:
                    try:
                        with engine.begin() as conn:
                            conn.execute(text("""
                                INSERT OR REPLACE INTO courses (course_id, course_name)
                                VALUES (:course_id, :course_name)
                            """), dict(
                                course_id=str(novo_course_id),
                                course_name=novo_course_name.strip()
                            ))

                        st.success("Treinamento cadastrado com sucesso.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao cadastrar treinamento: {e}")

        st.subheader("Agendar novo treinamento")

        df_employees = pd.read_sql("SELECT employee_id, employee_name, role FROM employees", engine)
        df_invalidos = df_employees[df_employees[['employee_name', 'role']].isna().any(axis=1)]

        if not df_invalidos.empty:
            st.warning("Existem colaboradores com dados incompletos no banco:")
            st.dataframe(df_invalidos, use_container_width=True)
        df_employees = df_employees.dropna(subset=['employee_name', 'role'])
        df_courses = pd.read_sql("SELECT course_id, course_name FROM courses", engine)

        lista_colaboradores = {
            f"{row['employee_name']} ({row['role']})": row['employee_id']
            for _, row in df_employees.iterrows()
        }

        lista_cursos = {
            f"{row['course_name']}": row['course_id']
            for _, row in df_courses.iterrows()
        }

        if df_employees.empty or df_courses.empty:
            st.warning("Cadastre colaboradores e treinamentos antes de agendar.")
        else:
            with st.form("add_training"):
                colaborador_escolhido = st.selectbox(
                    "Selecione o colaborador",
                    options=list(lista_colaboradores.keys())
                )

                curso_escolhido = st.selectbox(
                    "Selecione o treinamento",
                    options=list(lista_cursos.keys())
                )

                date_scheduled = st.date_input("Data agendada", datetime.today().date())
                freq = st.number_input("Periodicidade em meses (use 0 se for único)", min_value=0, value=12)

                add_sub = st.form_submit_button("Adicionar")

                if add_sub:
                    emp_id = lista_colaboradores[colaborador_escolhido]
                    course_id = lista_cursos[curso_escolhido]

                    emp_name = colaborador_escolhido.split(" (")[0]
                    emp_role = colaborador_escolhido.split(" (")[1].replace(")", "")
                    course_name = curso_escolhido

                    with engine.begin() as conn:
                        conn.execute(text("""
                            INSERT INTO trainings (employee_id, course_id, date_scheduled, frequency_months)
                            VALUES (:employee_id, :course_id, :date_scheduled, :frequency_months)
                        """), dict(
                            employee_id=str(emp_id),
                            course_id=str(course_id),
                            date_scheduled=date_scheduled.isoformat(),
                            frequency_months=int(freq)
                        ))

                    st.success("Registro adicionado com sucesso.")
                    try:
                        enviar_email_gestor_novo_treinamento(
                            emp_name=emp_name,
                            emp_role=emp_role,
                            course_name=course_name,
                            date_scheduled=date_scheduled.isoformat(),
                            freq=int(freq)
                        )
                        st.info("E-mail de notificação enviado ao gestor com sucesso.")
                    except Exception as e:
                        st.warning(f"Treinamento salvo, mas houve falha ao enviar o e-mail ao gestor: {e}")
                    st.rerun()
                    try:
                        enviar_email_gestor_novo_treinamento(
                            emp_name=emp_name,
                            emp_role=emp_role,
                            course_name=course_name,
                            date_scheduled=date_scheduled.isoformat(),
                            freq=int(freq)
                        )
                        st.info("E-mail de notificação enviado ao gestor com sucesso.")
                    except Exception as e:
                        st.warning(f"Treinamento salvo, mas houve falha ao enviar o e-mail ao gestor: {e}")
if __name__ == "__main__":
    main()