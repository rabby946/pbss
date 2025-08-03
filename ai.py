from flask import Blueprint, request, jsonify

ai_chat = Blueprint('ai_chat', __name__)

def category_reply(text, url_name):
    return f"{text} To know more, please visit the <a href='/{url_name}'><strong>{url_name.capitalize()}</strong></a> page."

@ai_chat.route("/ai-chat", methods=["POST"])
def handle_ai_chat():
    data = request.get_json()
    message = data.get("message", "").lower().strip()

    if any(word in message for word in ["teacher", "teachers"]):
        reply = category_reply("We have a group of experienced teachers. Almost 29 teachers and officials are available who work here. We have detailed information about them.", "teachers")
    elif any(word in message for word in ["student", "students", "courses", "curriculum"]):
        reply = category_reply("Our students participate actively in both academics and extra-curriculars. We are serving both general courses and vocational education among our students. We have detailed information about them.", "students")
    elif any(word in message for word in ["news", "info", "notice", "information"]):
        reply = category_reply("Stay updated with the latest school news. We have a news section for detailed news.", "news")
    elif "committee" in message:
        reply = category_reply("Our committee is formed with dedicated members. We have currently an ad-hoc committee.", "committee")
    elif "routine" in message:
        reply = category_reply("You can check the class routine on our website.", "routine")
    elif "result" in message or "results" in message:
        reply = category_reply("Examination results are published regularly.", "result")
    elif any(word in message for word in ["achievement", "campus", "facility", "extra-curricular"]):
        reply = category_reply("Explore our gallery to see campus life and achievements.", "gallery")
    elif any(word in message for word in ["complain", "issue", "report"]):
        reply = category_reply("Please reach out to us for any complaints or feedback.", "contact")
    elif any(word in message for word in ["mpo", "proof", "documents"]):
        reply = category_reply("You can find MPO and related documents here.", "accreditation")
    elif any(word in message for word in ["admin", "control panel"]):
        reply = category_reply("Admin login is restricted to authorized users.", "login")
    else:
        reply = "Sorry, I couldn't understand your question. You may ask about teachers, students, news, results, etc."

    return jsonify({"reply": reply})
