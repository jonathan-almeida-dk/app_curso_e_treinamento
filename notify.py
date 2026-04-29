# notify.py
"""
Script simples para enviar notificações por e-mail sobre treinamentos próximos e atrasados.
Agende este script para rodar diariamente (cron ou Task Scheduler).
"""

import os
import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

SMTP_HOST = os.getenv('SMTP_HOST')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
SMTP_USER = os.getenv('SMTP_USER')
SMTP_PASS = os.getenv('SMTP_PASS')
FROM_EMAIL = os.getenv('FROM_EMAIL')
GESTOR_EMAIL = os.getenv("GESTOR_EMAIL")

engine = create_engine('sqlite:///trainings.db', echo=False)

def compute_due(df):
    today = datetime.today().date()
    alerts = []

    for _, t in df.iterrows():
        last_completed = None
        if pd.notna(t['date_completed']) and str(t['date_completed']).strip() != "":
            try:
                last_completed = datetime.fromisoformat(str(t['date_completed'])).date()
            except:
                last_completed = None

        due_date = None

        # Se já concluiu → calcula próximo vencimento
        if last_completed:
            freq = t['frequency_months']

            if pd.notna(freq):
                try:
                    freq = int(freq)
                except:
                    freq = 0

                if freq > 0:
                    month = last_completed.month - 1 + freq
                    year = last_completed.year + month // 12
                    month = month % 12 + 1
                    day = min(last_completed.day, 28)
                    due_date = datetime(year, month, day).date()

        # Se NÃO concluiu → usa a data agendada (ESSENCIAL)
        else:
            if pd.notna(t['date_scheduled']) and str(t['date_scheduled']).strip() != "":
                try:
                    due_date = datetime.fromisoformat(str(t['date_scheduled'])).date()
                except:
                    due_date = None

        status = 'Concluído' if pd.notna(t['date_completed']) and str(t['date_completed']).strip() != "" else 'Pendente'

        if due_date:
            if status == 'Pendente':
                if today > due_date:
                    alerts.append(('Atrasado', t, due_date, (today - due_date).days))
                else:
                    days_left = (due_date - today).days
                    if 0 <= days_left <= 7:
                        alerts.append(('Próximo', t, due_date, days_left))

    return alerts

def send_email(to_email, subject, body):
    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = subject
    msg['From'] = FROM_EMAIL
    msg['To'] = to_email.strip()

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as s:
        s.starttls()
        s.login(SMTP_USER, SMTP_PASS)
        s.send_message(msg)

def main():
    print("Resumo enviado ao gestor com sucesso.")

    if not GESTOR_EMAIL:
        print("Erro: GESTOR_EMAIL não foi definido no arquivo .env")
        return

    df = pd.read_sql("""
        SELECT t.*, e.employee_name, e.role, c.course_name
        FROM trainings t
        LEFT JOIN employees e ON t.employee_id = e.employee_id
        LEFT JOIN courses c ON t.course_id = c.course_id
    """, engine)

    print("Total de registros no banco:", len(df))

    if df.empty:
        print("Nenhum registro encontrado no banco.")
        return

    alerts = compute_due(df)
    print("Total de alertas encontrados:", len(alerts))

    if not alerts:
        print("Nenhum alerta para enviar.")
        return

    linhas = []
    linhas.append("Olá,\n")
    linhas.append("Segue o resumo automático de treinamentos que exigem acompanhamento:\n")

    for kind, t, due_date, days in alerts:
        if kind == "Atrasado":
            linhas.append(
                f"- ATRASADO | Colaborador: {t['employee_name']} | Função: {t['role']} | "
                f"Treinamento: {t['course_name']} | Vencimento: {due_date} | "
                f"Atraso: {days} dia(s)"
            )
        else:
            linhas.append(
                f"- PRÓXIMO DO VENCIMENTO | Colaborador: {t['employee_name']} | Função: {t['role']} | "
                f"Treinamento: {t['course_name']} | Vencimento: {due_date} | "
                f"Faltam: {days} dia(s)"
            )

    linhas.append("\nAcesse o sistema para acompanhamento detalhado.")
    linhas.append("\nEquipe de Qualidade")

    corpo_email = "\n".join(linhas)
    assunto = "[HAIRAM] Resumo de treinamentos pendentes e atrasados"

    try:
        send_email(GESTOR_EMAIL, assunto, corpo_email)
        print(f"Resumo enviado com sucesso para o gestor: {GESTOR_EMAIL}")
    except Exception as e:
        print("Erro ao enviar resumo ao gestor:", e)

if __name__ == "__main__":
    main()