import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, send_file

import json
from .utils import load_data, add_student, add_session, remove_session, remove_student, save_data

app_routes = Blueprint('app_routes', __name__)


@app_routes.route('/students', methods=['GET', 'POST'])
def students():
    if request.method == 'POST':
        name = request.form['name']

        # Charger les données actuelles
        data = load_data()

        # Trouver le plus grand ID existant parmi les étudiants
        existing_ids = [student['id'] for student in data.get("students", [])]
        new_id = max(existing_ids) + 1 if existing_ids else 1  # ID suivant disponible

        # Ajouter un nouvel étudiant avec un ID unique
        add_student(name, new_id)

        return redirect(url_for('app_routes.students'))

    data = load_data()
    students = data["students"]
    return render_template('students.html', students=students)



@app_routes.route('/remarks/<int:student_id>', methods=['GET', 'POST'])
def remarks(student_id):
    data = load_data()

    if request.method == 'POST':
        remark = request.form.get('remark', "")
        add_session(remark, student_id)
        flash("Séance ajoutée avec ou sans remarque.", "success")
        return redirect(url_for('app_routes.remarks', student_id=student_id))

    # Trouver l'élève correspondant
    student = next((s for s in data["students"] if s["id"] == student_id), None)
    if student is None:
        flash("Élève introuvable.", "error")
        return redirect(url_for('app_routes.students'))

    # Filtrer les séances de cet élève
    student_sessions = [session for session in data["sessions"] if session["student_id"] == student_id]

    # Récupérer les sessions sélectionnées depuis Flask session
    selected_sessions = set(session.get(f'selected_sessions_{student_id}', []))  # Utilisation correcte de session

    # Compter les séances non cochées (celles qui ne sont pas dans selected_sessions)
    unrecorded_count = sum(1 for s in student_sessions if s["id"] not in selected_sessions)

    return render_template(
        "remarks.html",
        student_id=student_id,
        student_name=student["name"],
        student_school=student.get("school_name", ""),
        student_birth_date=student.get("birth_date", ""),
        student_phone_number=student.get("phone_number", ""),
        sessions=student_sessions,
        selected_sessions=selected_sessions,
        unrecorded_count=unrecorded_count,  # Nombre de séances non cochées
    )





@app_routes.route('/update_info/<int:student_id>', methods=['POST'])
def update_info(student_id):
    data = load_data()

    # Mettre à jour les informations de l'élève
    for student in data["students"]:
        if student["id"] == student_id:
            student["school_name"] = request.form['school_name']
            student["birth_date"] = request.form['birth_date']
            student["phone_number"] = request.form['phone_number']  # Ajout
            break

    save_data(data)
    flash("Les informations de l'élève ont été mises à jour avec succès.", "success")
    return redirect(url_for('app_routes.remarks', student_id=student_id))


@app_routes.route('/save_selection/<int:student_id>', methods=['POST'])
def save_selection(student_id):
    try:
        selected_sessions = request.form.getlist('selected_sessions')
        selected_sessions = list(map(int, selected_sessions))
        
        session[f'selected_sessions_{student_id}'] = selected_sessions
        session.modified = True  # Assure la sauvegarde dans Flask
        
        flash("Les sélections ont été sauvegardées avec succès !", "success")
        return '', 200
    except Exception as e:
        print(f"Erreur lors de la sauvegarde : {e}")
        return "Une erreur s'est produite lors de la sauvegarde.", 500



@app_routes.route('/delete_remark/<int:student_id>/<int:session_id>', methods=['POST'])
def delete_remark(student_id, session_id):
    remove_session(session_id)
    flash("Remarque supprimée avec succès.", "success")
    return redirect(url_for('app_routes.remarks', student_id=student_id))


from flask import jsonify

@app_routes.route('/delete_student/<int:student_id>', methods=['POST'])
def delete_student(student_id):
    # Charger les données depuis le fichier JSON
    data = load_data()

    # Supprimer l'élève correspondant
    data["students"] = [student for student in data.get("students", []) if student["id"] != student_id]

    # Supprimer les remarques associées à l'élève
    data["sessions"] = [session for session in data.get("sessions", []) if session["student_id"] != student_id]

    # Supprimer les sauvegardes de sélection associées à l'élève
    session.pop(f'selected_sessions_{student_id}', None)

    # Ne pas réassigner les IDs des élèves, mais conserver les anciens IDs
    # Supprimer uniquement l'élève, sans affecter les autres IDs
    save_data(data)

    # Rediriger vers la page des étudiants
    flash("Élève et données associées supprimés avec succès.", "success")
    return redirect(url_for('app_routes.students'))

@app_routes.route('/edit_remark/<int:student_id>/<int:session_id>', methods=['POST'])
def edit_remark(student_id, session_id):
    data = load_data()

    # Trouver la session et la modifier
    session_to_edit = next((s for s in data["sessions"] if s["id"] == session_id and s["student_id"] == student_id), None)

    if session_to_edit:
        # Mettre à jour la remarque
        new_remark = request.form.get('remark')  # Utiliser get() pour éviter les KeyError
        if new_remark:
            session_to_edit["remark"] = new_remark
            save_data(data)
            flash("La remarque a été mise à jour avec succès.", "success")
        else:
            flash("La remarque ne peut pas être vide.", "error")

    # Rediriger vers la page des remarques de l'élève
    return redirect(url_for('app_routes.remarks', student_id=student_id))


@app_routes.route('/download_db')
def download_db():
    # Get the correct absolute path to data.json
    db_path = os.path.join(os.path.dirname(__file__), "data.json")
    
    # Ensure the file exists before sending
    if not os.path.exists(db_path):
        return "Database file not found", 404

    # Send the file for download
    return send_file(db_path, as_attachment=True)







