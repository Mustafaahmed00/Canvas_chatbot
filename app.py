from flask import Flask, request, jsonify, render_template
import re
from flask_cors import CORS
from spellchecker import SpellChecker

app = Flask(__name__)
CORS(app)

class CanvasAssistantBot:
    negative_responses = ("nothing", "don't", "stop", "sorry")
    exit_commands = ("quit", "pause", "exit", "goodbye", "bye", "later")

    def __init__(self):
        self.matching_phrases = {
            'greetings': [r'hello', r'hi', r'hey', r'good morning', r'good afternoon', r'good evening'],
            'access_canvas': [r'canvas', r'log.*canvas'],
            'get_oriented': [r'get.*oriented', r'overview', r'navigate'],
            'edit_notifications': [r'notifications', r'notification.*settings'],
            'navigate_course': [r'navigate', r'modules', r'course'],
            'view_grades': [r'grades', r'view.*grades'],
            'canvas_app': [r'canvas.*app', r'mobile'],
            'resources_help': [r'help', r'resources', r'support'],
            'modules': [r'modules'],
            'learning_activities': [r'assignments', r'discussions', r'quiz'],
            'student_app_ios': [r'ios', r'apple'],
            'student_app_android': [r'android'],
            'additional_resources': [r'resources', r'guide', r'help']
        }
        self.responses = {
            'greetings': "Hello! Welcome to Canvas Assistant. How can I assist you today?",
            'access_canvas': "To access Canvas, navigate to [umassboston.instructure.com](https://umassboston.instructure.com) and log in with your UMass Boston email username and password.",
            'get_oriented': "You can watch the Canvas Overview video to learn how to navigate through the general areas in your Canvas account. [Watch the video here](https://community.canvaslms.com/t5/Video-Guide/Canvas-Overview-Students/ta-p/383771).",
            'edit_notifications': "You can customize your account notification settings in Canvas. Here's a [tutorial on how to review and choose notifications](https://community.canvaslms.com/t5/Video-Guide/Notification-Settings-All-Users/ta-p/383690).",
            'navigate_course': "Navigate your course by using the menu on the left-hand side of the screen. This includes links to modules, assignments, discussions, and grades. [Learn more about navigating your course](https://bit.ly/GetStartedCanvas_UMBStudent).",
            'view_grades': (
                "To view your grades, go to the 'Grades' section in Canvas. [Here's how you can view your grades](https://community.canvaslms.com/t5/Student-Guide/How-do-I-view-my-grades-in-a-current-course/ta-p/493).\n\n"
                "To view feedback comments from your instructor directly in your assignment submission, here's more detail: "
                "[View Annotation Feedback](https://community.canvaslms.com/t5/Student-Guide/How-do-I-view-annotation-feedback-comments-from-my-instructor/ta-p/523)."
            ),
            'canvas_app': (
                "Canvas has a mobile app available for both iOS and Android. [Learn how to download and use the Canvas Student app](https://bit.ly/GetStartedCanvas_UMBStudent)."
            ),
            'resources_help': (
                "For more in-depth resources, visit the [Canvas Student Guide](https://bit.ly/GetStartedCanvas_UMBStudent) or click the Help button on your Canvas dashboard for more support.\n\n"
                "You can also access the Chat with Canvas Support to start an online chat with a Canvas Expert anytime.\n\n"
                "Additional resources:\n"
                "- [Canvas Student Guide Table of Contents](https://community.canvaslms.com/docs/DOC-10701-canvas-student-guide-table-of-contents)\n"
                "- [Chat with Canvas Support](https://cases.canvaslms.com/liveagentchat?chattype=student&sfid=A5WgTEKARcWFY5IXRv5FT8ePIss19I2qCvHxwOtD)"
            ),
            'modules': (
                "Click on the Modules link in the course menu to see a list of modules organized by your instructor. Modules contain learning materials, readings, assignments, and quizzes grouped together by topic or week. "
                "[More details on viewing Modules](https://community.canvaslms.com/t5/Student-Guide/How-do-I-view-Modules-as-a-student/ta-p/433)."
            ),
            'learning_activities': (
                "Completing graded assignments and activities in Canvas is straightforward. These tasks will typically be accessible through their respective module pages. "
                "Or you can access assignments directly from the Assignments page if your instructor does not use a Module page. For more help:\n\n"
                "- [How do I submit an online assignment?](https://community.canvaslms.com/t5/Student-Guide/How-do-I-submit-an-online-assignment/ta-p/503)\n"
                "- [How do I reply to a discussion as a student?](https://community.canvaslms.com/t5/Student-Guide/How-do-I-reply-to-a-discussion-as-a-student/ta-p/334)\n"
                "- [How do I take a quiz in New Quizzes?](https://community.canvaslms.com/t5/Student-Guide/How-do-I-take-a-quiz-in-New-Quizzes/ta-p/291)"
            ),
            'student_app_ios': (
                "Canvas also has a free mobile app available for iOS. Here's how you can use it:\n\n"
                "- [Download the Canvas Student app on iOS](https://community.canvaslms.com/t5/Canvas-Student-iOS-Guide/How-do-I-download-the-Canvas-Student-app-on-my-iOS-device/ta-p/1932)\n"
                "- [Log in to the Canvas Student app on iOS](https://community.canvaslms.com/t5/Canvas-Student-iOS-Guide/How-do-I-log-in-to-the-Student-app-on-my-iOS-device-with-a/ta-p/1940)\n"
                "- [Use the Canvas Student app on iOS](https://community.canvaslms.com/t5/Canvas-Student-iOS-Guide/How-do-I-use-the-Student-app-on-my-iOS-device/ta-p/1939)"
            ),
            'student_app_android': (
                "Canvas also has a free mobile app available for Android. Here's how you can use it:\n\n"
                "- [Download the Canvas Student app on Android](https://community.canvaslms.com/t5/Canvas-Student-Android-Guide/How-do-I-download-the-Canvas-Student-app-on-my-Android-device/ta-p/1860)\n"
                "- [Log in to the Canvas Student app on Android](https://community.canvaslms.com/t5/Canvas-Student-Android-Guide/How-do-I-log-in-to-the-Student-app-on-my-Android-device-with-a-Canvas-URL/ta-p/1940)\n"
                "- [Use the Canvas Student app on Android](https://community.canvaslms.com/t5/Canvas-Student-Android-Guide/How-do-I-use-the-Student-app-on-my-Android-device/ta-p/1939)"
            ),
            'additional_resources': (
                "For additional learning resources, the Canvas Student Guide has over 200 articles. Each article includes Next and Previous links so you can easily navigate to related content.\n\n"
                "- [Canvas Student Guide Table of Contents](https://community.canvaslms.com/docs/DOC-10701-canvas-student-guide-table-of-contents)\n"
                "- [Chat with Canvas Support](https://cases.canvaslms.com/liveagentchat?chattype=student&sfid=A5WgTEKARcWFY5IXRv5FT8ePIss19I2qCvHxwOtD)"
            )
        }
        self.spell = SpellChecker()

    def autocorrect_input(self, user_input):
        words = user_input.split()
        corrected_words = [self.spell.correction(word) for word in words]
        return ' '.join(corrected_words)
    
    def get_response(self, message):
        corrected_message = self.autocorrect_input(message)
        for key, patterns in self.matching_phrases.items():
            for pattern in patterns:
                if re.search(pattern, corrected_message.lower()):
                    response = self.responses[key]
                    response_html = "<ul>"
                    for line in response.split("\n"):
                         if line.strip():
                              line = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', line)
                              response_html += f"<li>{line}</li>"
                    return response_html
        return "I did not understand you. Can you please ask your question again?"

chatbot = CanvasAssistantBot()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message')
    response = chatbot.get_response(user_input)
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(debug=True)
