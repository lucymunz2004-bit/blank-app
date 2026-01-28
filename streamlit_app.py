import streamlit as st
import pandas as pd
import os
# ======================================================
# Dateinamen
# ======================================================
EXAMS_FILE = "exams.csv"
QUESTIONS_FILE = "questions.csv"
ANSWERS_FILE = "answers.csv"
# ======================================================
# Initialisierung der CSV-Dateien
# ======================================================
if not os.path.exists(EXAMS_FILE):
pd.DataFrame(columns=["exam_id", "exam_name"]).to_csv(EXAMS_FILE,
index=False)
if not os.path.exists(QUESTIONS_FILE):
pd.DataFrame(columns=[
"exam_id",
"question_id",
"question",
"option_a",
"option_b",
"option_c",
"correct"
]).to_csv(QUESTIONS_FILE, index=False)
if not os.path.exists(ANSWERS_FILE):
pd.DataFrame(columns=[
"exam_id",
"student",
"question_id",
"answer"
]).to_csv(ANSWERS_FILE, index=False)
# ======================================================
# Hilfsfunktionen
# ======================================================
def reset_all():
for f in [EXAMS_FILE, QUESTIONS_FILE, ANSWERS_FILE]:
if os.path.exists(f):
os.remove(f)
st.rerun()
# ======================================================
# App Start
# ======================================================
st.title("Online Klassenarbeit – Prototyp (CSV)")
role = st.sidebar.selectbox("Rolle auswählen", ["Lehrer", "Schüler"])
exams = pd.read_csv(EXAMS_FILE)
# ======================================================
# ========================= LEHRER =====================
# ======================================================
if role == "Lehrer":
st.header("Klassenarbeiten verwalten")
# ---------- Reset ----------
st.warning(" Achtung: Alle Daten werden gelöscht")
if st.button("Alles zurücksetzen (neue Klassenarbeit starten)"):
reset_all()
st.divider()
# ---------- Neue Klassenarbeit ----------
st.subheader("Neue Klassenarbeit anlegen")
with st.form("new_exam_form", clear_on_submit=True):
exam_name = st.text_input("Name der Klassenarbeit")
create_exam = st.form_submit_button("Anlegen")
if create_exam:
if exam_name:
new_id = 1 if exams.empty else exams.exam_id.max() + 1
exams.loc[len(exams)] = [new_id, exam_name]
exams.to_csv(EXAMS_FILE, index=False)
st.success("Klassenarbeit angelegt")
st.rerun()
else:
st.warning("Bitte einen Namen eingeben.")
if exams.empty:
st.info("Noch keine Klassenarbeit vorhanden.")
st.stop()
# ---------- Auswahl ----------
exam_map = dict(zip(exams.exam_name, exams.exam_id))
selected_exam_name = st.selectbox(
"Klassenarbeit auswählen",
list(exam_map.keys())
)
exam_id = exam_map[selected_exam_name]
# ---------- Fragen ----------
st.subheader("Fragen hinzufügen")
with st.form("question_form", clear_on_submit=True):
q_text = st.text_input("Frage")
a = st.text_input("Antwort A")
b = st.text_input("Antwort B")
c = st.text_input("Antwort C")
correct = st.selectbox("Richtige Antwort", ["a", "b", "c"])
save_question = st.form_submit_button("Frage speichern")
if save_question:
if q_text and a and b and c:
questions = pd.read_csv(QUESTIONS_FILE)
next_q_id = (
1 if questions[questions.exam_id == exam_id].empty
else questions[questions.exam_id == exam_id].question_id.max() + 1
)
questions.loc[len(questions)] = [
exam_id,
next_q_id,
q_text,
a,
b,
c,
correct
]
else:
questions.to_csv(QUESTIONS_FILE, index=False)
st.success("Frage gespeichert")
st.warning("Bitte alle Felder ausfüllen.")
# ---------- Ergebnisse ----------
st.divider()
st.subheader("Ergebnisse")
answers = pd.read_csv(ANSWERS_FILE)
questions = pd.read_csv(QUESTIONS_FILE)
result_df = answers[answers.exam_id == exam_id].merge(
questions,
on=["exam_id", "question_id"]
)
if not result_df.empty:
result_df["Richtig"] = result_df.answer == result_df.correct
st.dataframe(
result_df[
["student", "question", "answer", "correct", "Richtig"]
]
)
else:
st.info("Noch keine Abgaben vorhanden.")
# ======================================================
# ======================== SCHÜLER =====================
# ======================================================
if role == "Schüler":
st.header("Klassenarbeit schreiben")
if exams.empty:
st.info("Keine Klassenarbeit verfügbar.")
st.stop()
exam_map = dict(zip(exams.exam_name, exams.exam_id))
selected_exam_name = st.selectbox(
"Klassenarbeit auswählen",
list(exam_map.keys())
)
exam_id = exam_map[selected_exam_name]
name = st.text_input("Name des Schülers")
questions = pd.read_csv(QUESTIONS_FILE)
qs = questions[questions.exam_id == exam_id]
if qs.empty:
st.warning("Diese Klassenarbeit enthält noch keine Fragen.")
st.stop()
answers = []
for _, q in qs.iterrows():
ans = st.radio(
q.question,
["a", "b", "c"],
format_func=lambda x: q[f"option_{x}"],
index=None,
key=f"{exam_id}_{q.question_id}"
)
answers.append((exam_id, name, q.question_id, ans))
if st.button("Abgeben"):
if not name:
st.warning("Bitte einen Namen eingeben.")
elif None in [a[3] for a in answers]:
st.warning("Bitte alle Fragen beantworten.")
else:
df = pd.read_csv(ANSWERS_FILE)
for a in answers:
df.loc[len(df)] = a
df.to_csv(ANSWERS_FILE, index=False)
st.success("Klassenarbeit erfolgreich abgegeben!")
