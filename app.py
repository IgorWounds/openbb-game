import customtkinter as ctk
from PIL import Image, ImageTk
import tkinter as tk
import json
import os


class QuizQuestion:
    def __init__(self, data, app):
        self.data = data
        self.app = app
        self.user_input_vars = []

    def display(self):
        # Dynamically set the wraplength based on the width of the window
        window_width = self.app.winfo_width()
        font_style = ("Roboto", 16, "bold")

        # Check if the question type is 'text' and adjust the font style
        if self.data["type"] == "text":
            font_style = ("Roboto", 16)  # Regular font style

        question_label = ctk.CTkLabel(
            self.app,
            text=self.data["prompt"],
            wraplength=window_width - 20,  # Adjust the wraplength dynamically
            font=font_style,
            anchor="center",  # Align the text in the center of the label
            justify="center",  # Justify the text in the center
        )
        question_label.pack(pady=(0, 10), fill="x")

        if self.data["type"] == "multiple_choice":
            self.user_input_vars = []
            for choice in self.data["choices"]:
                # choice_frame = ctk.CTkFrame(self.app)
                choice_frame = ctk.CTkFrame(
                    self.app,
                    bg_color="transparent",
                )
                choice_frame.pack(fill="x", pady=2)
                var = tk.BooleanVar()
                checkbox = ctk.CTkCheckBox(
                    choice_frame, text=list(choice.values())[0], variable=var
                )
                checkbox.pack(side="left", anchor="w")
                self.user_input_vars.append(var)

        elif self.data["type"] == "single_choice":
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

    def display_image(self, image_path):
        if image_path:
            # Check if the file exists
            if os.path.exists(image_path):
                pil_image = Image.open(image_path)
                # Resize or process the image as needed
                # pil_image = pil_image.resize((desired_width, desired_height))

                tk_image = ImageTk.PhotoImage(pil_image)
                image_label = tk.Label(self.app, image=tk_image)
                image_label.image = tk_image  # Keep a reference
                image_label.pack(pady=(10, 0))
            else:
                print(f"Image not found: {image_path}")

    def validate(self):
        if self.data["type"] == "multiple_choice":
            user_selected_keys = {
                list(choice.keys())[0]
                for choice, var in zip(self.data["choices"], self.user_input_vars)
                if var.get()
            }
            correct_answers = set(self.data["answer"])
            return user_selected_keys == correct_answers
        elif self.data["type"] == "single_choice":
            return self.user_input_vars[0].get() == self.data["answer"]
        return False


class QuizApp:
    def __init__(self, quiz_data):
        self.app = ctk.CTk()
        self.app.geometry("1200x650")
        self.app.title("Quiz Application")
        self.bg_image_path = "static/BG.png"

        # Load the background image
        self.original_background_image = Image.open(self.bg_image_path)
        self.background_photo = ImageTk.PhotoImage(self.original_background_image)

        # Create a background label
        self.background_label = tk.Label(self.app, image=self.background_photo)
        self.background_label.place(x=0, y=0, relwidth=1, relheight=1)

        # Bind the resize event
        self.app.bind("<Configure>", self.on_resize)

        ctk.set_appearance_mode("System")  # or "Dark" / "Light"
        ctk.set_default_color_theme("blue")  # Theme color

        self.question_frame = ctk.CTkFrame(self.app, bg_color="transparent")
        self.frame_controls = ctk.CTkFrame(self.app, bg_color="transparent")

        self.quiz_data = quiz_data
        self.current_question_id = 1
        self.current_question = None
        self.user_selections = {}
        self.answer_frame = ctk.CTkFrame(self.app)

        self.question_frame = ctk.CTkFrame(self.app)
        self.question_frame.pack(pady=20, padx=20, fill="both", expand=True)

        self.message_label = ctk.CTkLabel(self.app, text="", bg_color="transparent")
        self.message_label.pack_configure(padx=20, pady=10, fill="x")

        self.frame_controls = ctk.CTkFrame(self.app)
        self.frame_controls.pack(pady=10, padx=20, fill="x")

        self.resize_job = None

    def on_resize(self, event):
        # Cancel the previous resize job
        if self.resize_job is not None:
            self.app.after_cancel(self.resize_job)
        self.resize_job = self.app.after(
            100, self.perform_resize, event.width, event.height
        )

    def perform_resize(self, new_width, new_height):
        # Resize the background image to fit the window using a faster method
        resized_image = self.original_background_image.resize(
            (new_width, new_height),
            Image.Resampling.NEAREST,  # NEAREST is a faster method
        )
        self.background_photo = ImageTk.PhotoImage(resized_image)
        self.background_label.config(image=self.background_photo)
        self.background_label.image = (
            self.background_photo
        )  # Keep a reference to avoid garbage collection

    def update_message(self, message):
        self.message_label.configure(text=message, bg_color="transparent")
        self.message_label.pack_configure(padx=20, pady=10, fill="x")

    def start_quiz(self):
        self.display_question(str(self.current_question_id))
        self.app.mainloop()

    def display_question(self, question_id):
        # Clear the previous question's widgets and the answer frame
        for widget in self.question_frame.winfo_children():
            widget.destroy()
        for widget in self.answer_frame.winfo_children():
            widget.destroy()

        # Unpack the answer frame if it's packed
        self.answer_frame.pack_forget()

        # Display the current question
        question_data = self.quiz_data[question_id]
        self.current_question = QuizQuestion(question_data, self.question_frame)
        self.current_question.display()

        if self.quiz_data[question_id].get("url", None):
            image_path = os.path.join("static/", self.quiz_data[question_id].get("url"))
            self.current_question.display_image(image_path)

        # Restore previous selections if any
        if question_id in self.user_selections:
            previous_selections = self.user_selections[question_id]
            if self.current_question.data["type"] == "multiple_choice":
                for var, selected in zip(
                    self.current_question.user_input_vars, previous_selections
                ):
                    var.set(selected)
            elif self.current_question.data["type"] == "single_choice":
                self.current_question.user_input_vars[0].set(previous_selections)

        # Repack the control frame and buttons for each new question
        self.add_control_buttons()

    def validate_answer(self):
        # Clear any previous message
        self.update_message("")  # Clear any previous message

        # Save the user's selections
        if self.current_question.data["type"] == "multiple_choice":
            self.user_selections[str(self.current_question_id)] = [
                var.get() for var in self.current_question.user_input_vars
            ]
        elif self.current_question.data["type"] == "single_choice":
            self.user_selections[
                str(self.current_question_id)
            ] = self.current_question.user_input_vars[0].get()

        if self.current_question.validate():
            self.current_question_id += 1
            if str(self.current_question_id) in self.quiz_data:
                self.display_question(str(self.current_question_id))
            else:
                self.update_message("Quiz Completed!")
                self.app.after(
                    500, self.app.destroy
                )  # Close the app after a short delay
        else:
            self.update_message("One or more answer is incorrect. Please try again!")

    def show_correct_answer(self):
        # Clear any previous message
        self.update_message("")  # Clear any previous message

        # Set the correct answer(s)
        question_data = self.quiz_data[str(self.current_question_id)]

        if self.current_question.data["type"] == "multiple_choice":
            correct_answers = set(question_data["answer"])
            for choice, var in zip(
                question_data["choices"], self.current_question.user_input_vars
            ):
                choice_key = next(iter(choice.keys()))
                var.set(choice_key in correct_answers)
        elif self.current_question.data["type"] == "single_choice":
            correct_answer_key = question_data["answer"]
            self.current_question.user_input_vars[0].set(correct_answer_key)

    def add_control_buttons(self):
        # Clear the control frame before repacking the buttons
        for widget in self.frame_controls.winfo_children():
            widget.destroy()

        # Only create and display control buttons if the question type is not 'text'
        if self.current_question.data["type"] != "text":
            control_button_frame = ctk.CTkFrame(self.frame_controls)
            control_button_frame.pack(pady=10, padx=20)

            show_answer_button = ctk.CTkButton(
                control_button_frame,
                text="Show Answer",
                command=self.show_correct_answer,
                fg_color="#FFC107",
                hover_color="#FFD54F",
            )
            show_answer_button.pack(side=tk.LEFT, padx=5)

            submit_button = ctk.CTkButton(
                control_button_frame,
                text="Submit",
                command=self.validate_answer,
                fg_color="#4CAF50",
                hover_color="#66BB6A",
            )
            submit_button.pack(side=tk.LEFT, padx=5)

        # Create a frame to hold the navigation buttons
        navigation_button_frame = ctk.CTkFrame(self.frame_controls)
        navigation_button_frame.pack(pady=10, padx=20)

        # Conditionally add the Back button
        if self.current_question_id > 1:
            back_button = ctk.CTkButton(
                navigation_button_frame,
                text="Back",
                command=self.go_to_previous_question,
                fg_color="#FF5722",
                hover_color="#FF7043",
            )
            back_button.pack(side=tk.LEFT, padx=5)

        next_button = ctk.CTkButton(
            navigation_button_frame,
            text="Next",
            command=self.go_to_next_question,
            fg_color="#FF5722",
            hover_color="#FF7043",
        )
        next_button.pack(side=tk.LEFT, padx=5)

    def go_to_next_question(self):
        if str(self.current_question_id + 1) in self.quiz_data:
            self.current_question_id += 1
            self.display_question(str(self.current_question_id))

    def go_to_previous_question(self):
        if self.current_question_id > 1:
            self.current_question_id -= 1
            self.display_question(str(self.current_question_id))


if __name__ == "__main__":
    # Load quiz data
    with open("data.json") as json_file:
        quiz_data = json.load(json_file)

    # Initialize and start the quiz application
    quiz_app = QuizApp(quiz_data)
    quiz_app.start_quiz()
