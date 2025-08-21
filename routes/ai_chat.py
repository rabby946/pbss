from flask import Blueprint, request, jsonify
from models import News, Gallery, Teacher, Student, Committee, MPO
import google.generativeai as genai
from datetime import datetime

ai_bp = Blueprint("ai", __name__)

# Configure Gemini API (you should set GOOGLE_API_KEY in your app.py)
# genai.configure(api_key=YOUR_KEY)  # already done in app.py

@ai_bp.route("/ai-chat", methods=["POST"])
def ai_chat():
    try:
        data = request.get_json()
        user_input = data.get("message", "").strip()

        if not user_input:
            return jsonify({"answer": "No message received."}), 400

        # -----------------------
        # Load DB data for context
        # -----------------------
        school_info = {}  # you can load from a SchoolInfo table if you have one
        news_data = News.query.all()
        teachers_data = Teacher.query.all()
        committees_data = Committee.query.all()
        students_data = Student.query.all()
        accreditations_data = MPO.query.all()
        gallery_data = Gallery.query.all()

        context_parts = []

        # Example: school info section
        if school_info:
            context_parts.append(
                f"### About Palashbaria Secondary School\n"
                f"- Name: {school_info.get('school_name', 'N/A')}\n"
                f"- EIIN: {school_info.get('eiin', 'N/A')}\n"
                f"- Location: {school_info.get('location', 'N/A')}\n"
                f"- History & Mission: {school_info.get('about_us', 'N/A')}"
            )

        if teachers_data:
            teacher_names = ", ".join([t.title for t in teachers_data])
            context_parts.append(
                f"### Teachers Information\n- Total Teachers: {len(teachers_data)}\n- Names: {teacher_names}"
            )

        if students_data:
            context_parts.append(
                f"### Student Information\n- Total Students: {len(students_data)}. Details hidden for privacy."
            )

        if committees_data:
            committee_titles = ", ".join([c.title for c in committees_data])
            context_parts.append(
                f"### Committees\n- Committees include: {committee_titles}"
            )

        if news_data:
            news_headlines = "\n".join([f"- {n.title}" for n in news_data[:3]])
            context_parts.append(f"### Recent News\n{news_headlines}")

        if accreditations_data:
            acc_titles = ", ".join([a.title for a in accreditations_data])
            context_parts.append(f"### Accreditations (MPO)\n- {acc_titles}")

        if gallery_data:
            # pick first few items for achievements info
            achievements = [g.title for g in gallery_data[:5]]
            context_parts.append(
                f"### Achievements & Gallery Highlights\n- {', '.join(achievements)}"
            )

        school_context = "\n\n".join(context_parts)

        # -----------------------
        # Generate AI response
        # -----------------------
        model = genai.GenerativeModel("gemini-1.5-flash")
        prompt = f"""
You are a helpful AI assistant for "Palashbaria Secondary School". 
Use ONLY the following information to answer questions. 
Do not make up anything. If the answer is not available, politely suggest contacting the school.

--- SCHOOL INFORMATION ---
{school_context}
--------------------------

User's question: "{user_input}"
"""
        response = model.generate_content(prompt)
        return jsonify({"answer": response.text})

    except Exception as e:
        print(f"AI Chat Error: {e}")
        return jsonify({"answer": "Sorry, I'm having trouble processing your question."}), 500
