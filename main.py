from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.togglebutton import ToggleButton
from kivy.core.window import Window
import mysql.connector
from mysql.connector import Error
import re  

# Setting window size (mobile portrait size)
Window.size = (360, 640)

class MCQEntryScreen(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cols = 1
        self.padding = 10
        self.spacing = 10

        # Title and Instructions
        self.add_widget(Label(text="MCQ Quiz Entry 12th", font_size=24, size_hint=(1, 0.1)))

        # Roll Number and Date Input
        self.add_widget(Label(text="Roll No:", size_hint=(1, 0.05)))
        self.roll_no = TextInput(multiline=False, size_hint=(1, 0.1))
        self.add_widget(self.roll_no)

        self.add_widget(Label(text="Date (dd-mm-yyyy):", size_hint=(1, 0.05)))
        self.date_input = TextInput(hint_text="Enter date", multiline=False, size_hint=(1, 0.1))
        self.add_widget(self.date_input)

        # Question Entry Section
        self.add_widget(Label(text="Enter 3 Multiple Choice Questions:", size_hint=(1, 0.1)))
        self.questions_layout = BoxLayout(orientation='vertical', size_hint_y=None)
        self.questions_layout.bind(minimum_height=self.questions_layout.setter('height'))

        scroll_view = ScrollView(size_hint=(1, 0.6), do_scroll_x=False, do_scroll_y=True, bar_width=10, bar_color=[1, 0, 0, 1], scroll_type=['bars'], scroll_distance=20, scroll_timeout=250)
        scroll_view.add_widget(self.questions_layout)
        self.add_widget(scroll_view)

        # Initialize questions data
        self.questions_data = []
        for i in range(5):
            self.add_question(i + 1)

        # Submit Button
        self.submit_btn = Button(text="Submit", size_hint=(1, 0.1))
        self.submit_btn.bind(on_press=self.submit)
        self.add_widget(self.submit_btn)

    def add_question(self, q_num):
        question_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=250)
        question_layout.padding = [10, 5, 10, 5]

        question_layout.add_widget(Label(text=f"Question {q_num}:", size_hint_y=None, height=40))
        question_text = TextInput(hint_text="Enter question text", multiline=False, size_hint_y=None, height=40)
        question_layout.add_widget(question_text)

        options_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=180)
        options_layout.spacing = 10

        correct_option = [None]  # Store the correct option for each question
        options = []  # Store references to option inputs

        for option_num in range(4):
            option_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
            option_input = TextInput(hint_text=f"Option {chr(65 + option_num)}", multiline=False, size_hint_x=0.8)
            options.append(option_input)
            option_layout.add_widget(option_input)

            option_btn = ToggleButton(text="Correct", group=f"question_{q_num}", size_hint_x=0.2)

            # Bind the button to select the correct answer for this question
            def on_select(btn, idx=option_num):
                correct_option[0] = idx

            option_btn.bind(on_press=on_select)
            option_layout.add_widget(option_btn)
            options_layout.add_widget(option_layout)

        question_layout.add_widget(options_layout)
        self.questions_layout.add_widget(question_layout)

        # Store question data in questions_data list
        self.questions_data.append((question_text, options, correct_option))

    def submit(self, instance):
        roll_no = self.roll_no.text
        date = self.date_input.text

        if not roll_no or not date:
            popup = Popup(title="Error", content=Label(text="Please enter Roll No and a date"), size_hint=(0.6, 0.3))
            popup.open()
            return

        # Validate date format (dd-mm-yyyy)
        if not self.validate_date(date):
            popup = Popup(title="Error", content=Label(text="Date must be in the format dd-mm-yyyy"), size_hint=(0.6, 0.3))
            popup.open()
            return

        # Save questions to the database
        self.save_questions(roll_no, date)

    def validate_date(self, date):
        date_regex = r'^\d{2}-\d{2}-\d{4}$'
        if re.match(date_regex, date):
            return True
        return False

    def save_questions(self, roll_no, date):
        try:
            conn = mysql.connector.connect(
                host='sql12.freesqldatabase.com',            
                database='sql12731483',    
                user='sql12731483',        
                password='VsHQsDTI5L'     
            )
            if conn.is_connected():
                cursor = conn.cursor()

                # Iterate over each question, options, and correct option in the questions_data
                for question_text, options, correct_option in self.questions_data:
                    question = question_text.text
                    option_a = options[0].text
                    option_b = options[1].text
                    option_c = options[2].text
                    option_d = options[3].text
                    correct_opt_index = correct_option[0]

                    if correct_opt_index is None:
                        popup = Popup(title="Error", content=Label(text="Please select a correct option for each question"), size_hint=(0.6, 0.3))
                        popup.open()
                        return

                    correct_opt = chr(65 + correct_opt_index)

                    # Insert question and options into the database
                    cursor.execute('''
                        INSERT INTO questions (roll_no, date, question, option_a, option_b, option_c, option_d, correct_option)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ''', (roll_no, date, question, option_a, option_b, option_c, option_d, correct_opt))

                conn.commit()

                popup = Popup(title="Success", content=Label(text="Questions Submitted Successfully!"), size_hint=(0.6, 0.3))
                popup.open()

        except Error as e:
            popup = Popup(title="Database Error", content=Label(text=f"Error: {e}"), size_hint=(0.6, 0.3))
            popup.open()
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

class QuizApp(App):
    def build(self):
        return MCQEntryScreen()

if __name__ == "__main__":
    QuizApp().run()
