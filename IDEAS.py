import customtkinter as ctk
import tkinter as tk
import json


class QuizQuestion:
    def __init__(self, data, app):
        self.data = data
        self.app = app
        self.user_input_vars = []

    def display(self):
        question_label = ctk.CTkLabel(
            self.app, text=self.data["prompt"], wraplength=500
        )
        question_label.pack(
            anchor="w", pady=(0, 10), fill="x"
        )  # Ensure label fills the x-axis and is left-aligned

        if self.data["type"] == "single_choice":
            self.user_input_vars = [tk.StringVar()]
            for choice in self.data["choices"]:
                for key, value in choice.items():
                    radio_button = ctk.CTkRadioButton(
                        self.app,
                        text=value,
                        variable=self.user_input_vars[0],
                        value=key,
                    )
                    radio_button.pack(
                        anchor="w", fill="x"
                    )  # Ensure radio button fills the x-axis and is left-aligned
        elif self.data["type"] == "multiple_choice":
            for choice in self.data["choices"]:
                choice_frame = ctk.CTkFrame(self.app)
                choice_frame.pack(fill="x", pady=2)  # Ensure frame fills the x-axis
                var = tk.StringVar()
                checkbox = ctk.CTkCheckBox(
                    choice_frame, text=list(choice.values())[0], variable=var
                )
                checkbox.pack(
                    side="left", anchor="w"
                )  # Align checkbox to the left within the frame
                self.user_input_vars.append(var)

    def validate(self):
        if self.data["type"] == "multiple_choice":
            user_selected_keys = [
                list(choice.keys())[0]
                for choice, var in zip(self.data["choices"], self.user_input_vars)
                if var.get() == "1"
            ]
            return set(user_selected_keys) == set(self.data["answer"])
        elif self.data["type"] == "single_choice":
            return self.user_input_vars[0].get() == self.data["answer"]
        return False


class QuizApp:
    def __init__(self, quiz_data):
        self.app = ctk.CTk()
        self.app.geometry("1200x500")
        self.app.title("Quiz Application")
        ctk.set_appearance_mode("System")  # or "Dark" / "Light"
        ctk.set_default_color_theme("blue")  # Theme color

        self.quiz_data = quiz_data
        self.current_question_id = 1
        self.current_question = None
        self.answer_frame = ctk.CTkFrame(self.app)
        self.frame_question = ctk.CTkFrame(self.app)
        self.frame_question.pack(pady=20, padx=20, fill="both", expand=True)

        self.frame_controls = ctk.CTkFrame(self.app)
        self.frame_controls.pack(pady=10, padx=20, fill="x")

        # Add a message label that will be updated with feedback
        self.message_label = ctk.CTkLabel(self.app, text="")
        self.message_label.pack(pady=(5, 20))

    def start_quiz(self):
        self.display_question(str(self.current_question_id))
        self.app.mainloop()

    def display_question(self, question_id):
        # Clear the previous question's widgets and the answer frame
        for widget in self.frame_question.winfo_children():
            widget.destroy()
        for widget in self.answer_frame.winfo_children():
            widget.destroy()

        # Unpack the answer frame if it's packed
        self.answer_frame.pack_forget()
        # Clear the previous question's widgets
        for widget in self.frame_question.winfo_children():
            widget.destroy()

        # Display the current question
        question_data = self.quiz_data[question_id]
        self.current_question = QuizQuestion(question_data, self.frame_question)
        self.current_question.display()

        # Repack the control frame and buttons for each new question
        self.add_control_buttons()

    def validate_answer(self):
        # Clear any previous message
        self.display_message("")
        if self.current_question.validate():
            self.current_question_id += 1
            if str(self.current_question_id) in self.quiz_data:
                self.display_question(str(self.current_question_id))
            else:
                ctk.CTkLabel(self.app, text="Quiz Complete!").pack()
        else:
            self.display_message("Incorrect answer. Try again!")

    def show_correct_answer(self):
        # Clear any previous message
        self.display_message("")

        # Clear previous answer labels and pack the answer frame
        for widget in self.answer_frame.winfo_children():
            widget.destroy()
        self.answer_frame.pack(pady=(5, 0))

        question_data = self.quiz_data[str(self.current_question_id)]

        # Display the correct answer(s)
        if isinstance(question_data["answer"], list):
            for answer_key in question_data["answer"]:
                answer_text = next(
                    choice[answer_key]
                    for choice in question_data["choices"]
                    if answer_key in choice
                )
                answer_label = ctk.CTkLabel(self.answer_frame, text=answer_text)
                answer_label.pack(anchor="w")
        else:
            correct_answer_key = question_data["answer"]
            correct_answer_text = next(
                choice[correct_answer_key]
                for choice in question_data["choices"]
                if correct_answer_key in choice
            )
            answer_label = ctk.CTkLabel(self.answer_frame, text=correct_answer_text)
        answer_label.pack(anchor="w")

    def display_message(self, message):
        # Update the text of the message label to display feedback
        self.message_label.configure(text=message)

    def add_control_buttons(self):
        # Clear the control frame before repacking the buttons
        for widget in self.frame_controls.winfo_children():
            widget.destroy()

        # Create and pack the control buttons
        submit_button = ctk.CTkButton(
            self.frame_controls,
            text="Submit",
            command=self.validate_answer,
            fg_color="#4CAF50",
            hover_color="#66BB6A",
        )
        submit_button.pack(side=tk.LEFT, padx=10)

        show_answer_button = ctk.CTkButton(
            self.frame_controls,
            text="Show Answer",
            command=self.show_correct_answer,
            fg_color="#FFC107",
            hover_color="#FFD54F",
        )
        show_answer_button.pack(side=tk.RIGHT, padx=10)


# Load quiz data
with open("IDEAS.json") as json_file:
    quiz_data = json.load(json_file)

# Initialize and start the quiz application
quiz_app = QuizApp(quiz_data)
quiz_app.start_quiz()
