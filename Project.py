import tkinter as tk #for tkinter 
from tkinter import ttk, messagebox #for displaying messages
import ttkbootstrap as tb  #for improving theme
import mysql.connector #for connecting python to MySQL
 
 
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="Python_Quiz"
)  #Code to make connection with MySQL
cursor = db.cursor()  #works as iterator in sql
 
 
class PythonQuizApp:
    def __init__(self, root):
        self.root = root   #parent window
        self.root.title("Python Quiz")
        self.style = tb.Style("solar")  #bootstrap theme
        self.root.geometry("1200x1200")
        #to initialize the variables
        self.user_id = None
        self.chapter = tk.StringVar()  #to capture dynamic values of dropdown
        self.score = 0
        self.timer_seconds = 30
        self.questions = []
        self.current_question_index = 0
        self.timer_label = None
        self.timer_job = None
 
        self.set_main_menu()
 
    def set_main_menu(self):
        for widget in self.root.winfo_children():  
            widget.destroy()  #to clear the child windows
 
        
        frame = ttk.Frame(self.root, padding=20)
        frame.pack(expand=True)
 
        ttk.Label(frame, text="Welcome to the Python Quiz!", font=("Times New Roman", 18, "bold")).pack(pady=20)
        ttk.Button(frame, text="Login & Start Quiz", style="success.TButton", command=self.login).pack(pady=10, fill="x")
        ttk.Button(frame, text="Exit", style="danger.TButton", command=self.root.destroy).pack(pady=10, fill="x")
 
    def login(self):
        for widget in self.root.winfo_children():
            widget.destroy() #to clear the child windows
 
        
        frame = ttk.Frame(self.root, padding=20)
        frame.pack(expand=True)
 
        ttk.Label(frame, text="Enter User ID:", font=("Times New Roman", 12)).pack(pady=5)
        self.user_id_entry = ttk.Entry(frame, font=("Times New Roman", 12))
        self.user_id_entry.pack(pady=5, fill="x")
 
        ttk.Label(frame, text="Select Chapter:", font=("Times New Roman", 12)).pack(pady=5) #dropdown for getting chapters
        chapters = self.fetch_chapters()
        self.chapter_dropdown = ttk.Combobox(frame, textvariable=self.chapter, values=chapters, state="readonly", font=("Times New Roman", 12)) #dropdown for populating the chapters
        self.chapter_dropdown.pack(pady=5, fill="x")
 
        ttk.Button(frame, text="Start Quiz", style="primary.TButton", command=self.start_quiz).pack(pady=20, fill="x")
        ttk.Button(frame, text="Back to Main Menu", style="secondary.TButton", command=self.set_main_menu).pack(pady=10, fill="x")
 
    def fetch_chapters(self):
        cursor.execute("SELECT DISTINCT chapter FROM questions")
        chapters = [row[0] for row in cursor.fetchall()] #looping to get all the chapters
        return chapters if chapters else []
 
    def start_quiz(self):
        user_id = self.user_id_entry.get() #capture entered userid
        chapter = self.chapter_dropdown.get()   #capture selected chapter
 
        if not user_id or not chapter:
            messagebox.showerror("Error", "User ID and Chapter are required!")
            return
 
        cursor.execute("SELECT attempts, test_status FROM users WHERE username=%s AND chapter=%s", (user_id, chapter)) #to fetch data of the attempts,test status for particular chapter and user
        user_data = cursor.fetchone() #to fetch the result one at a time
 
        if user_data:
            attempts, test_status = user_data
            if attempts >= 3:
                messagebox.showinfo("Info", "You have reached the maximum number of attempts for this chapter.")
                return
            if test_status == "Completed" and attempts >= 3:
                messagebox.showinfo("Info", "You have already completed this test.")
                return  #code to limit the test attempt to 3 for a chapter
        else:
            cursor.execute("INSERT INTO users (username, chapter, attempts, test_status) VALUES (%s, %s, %s, %s)", 
                           (user_id, chapter, 0, "Not Started"))  #if first attempt then insert data in the table users
            db.commit() #finish the transaction
 
        cursor.execute("SELECT id, question, option_a, option_b, option_c, option_d, correct_answer FROM questions WHERE chapter=%s", (chapter,)) # to fetch questions for particular chapter
        self.questions = cursor.fetchall()
 
        if not self.questions:
            messagebox.showerror("Error", "No questions available for the selected chapter!")
            return
 
        self.user_id = user_id
        self.chapter = chapter
        self.score = 0
        self.current_question_index = 0
        cursor.execute("UPDATE users SET attempts = attempts + 1 WHERE username = %s AND chapter = %s", (user_id, chapter))  #update the attempt
        db.commit() #finish the transaction
 
        self.display_question()
 
    def display_question(self):
        if self.current_question_index >= len(self.questions): #to check the count of question number is not greater or equal to lenght of preset questions
            self.end_quiz()
            return
 
        for widget in self.root.winfo_children(): #clear child  window
            widget.destroy()
 
        frame = ttk.Frame(self.root, padding=20)
        frame.pack(expand=True)
 
        question = self.questions[self.current_question_index] #self questions works as list and current_question_index as the index for the question 
        self.current_question_index += 1
 
        ttk.Label(frame, text=f"Question {self.current_question_index}:", font=("Times New Roman", 14, "bold")).pack(anchor="w", pady=5)
        ttk.Label(frame, text=question[1], font=("Times New Roman", 12), wraplength=700).pack(anchor="w", pady=10)
 
        options_frame = ttk.Frame(frame)
        options_frame.pack(anchor="w", pady=10)
 
        options = [question[2], question[3], question[4], question[5]] #set value for options 
        for idx, option in enumerate(options):
            ttk.Button(options_frame, text=option, style="info.TButton", 
                       command=lambda opt=option, ans=question[6]: self.check_answer(opt, ans)).pack(anchor="w", pady=5, fill="x")
 
        self.timer_label = ttk.Label(self.root, text=f"Time Left: {self.timer_seconds}s", font=("Times New Roman", 12), foreground="red")
        self.timer_label.pack(pady=5)
        self.timer_seconds = 30
        self.start_timer()  #timer for each question
 
    def start_timer(self):
        if self.timer_seconds > 0:
            self.timer_label.config(text=f"Time Left: {self.timer_seconds}s") 
            self.timer_seconds -= 1
            self.timer_job = self.root.after(1000, self.start_timer) #to call a function after 1 sec as clock time is reducing by a second
        else:
            self.root.after_cancel(self.timer_job) #to cancel the current timer
            messagebox.showinfo("Time's Up!", "Off to the next question.")
            self.display_question()
 
    def check_answer(self, selected_option, correct_answer):
        if self.timer_job:
            self.root.after_cancel(self.timer_job) #to stop/kill the running task
 
        if selected_option.strip() == correct_answer.strip(): #strip() - to remove whitespaces if any
            self.score += 1
            # score_text = "Correct Answer"
            # score_color = "green"
        # else:
            # score_text = "Wrong Answer"
            # score_color = "red"
        # self.score_label = ttk.Label(self.root, text=score_text, font=("Times New Roman", 12), foreground=score_color)
        # self.score_label.pack(pady=5)
 
            
        self.display_question()
 
    def end_quiz(self):
        if self.timer_job:
            self.root.after_cancel(self.timer_job)
 
        cursor.execute("UPDATE users SET score=%s, test_status=%s WHERE username=%s AND chapter=%s",
                       (self.score, "Completed", self.user_id, self.chapter)) #to update score for the chapter
        db.commit()

        for widget in self.root.winfo_children():
            widget.destroy()
 
        frame = ttk.Frame(self.root, padding=20)
        frame.pack(expand=True)
 
        ttk.Label(frame, text=f"Quiz Completed!\nYour Score: {self.score}", font=("Times New Roman", 16, "bold")).pack(pady=20)
        ttk.Button(frame, text="Main Menu", style="primary.TButton", command=self.set_main_menu).pack(pady=10, fill="x")
        
        
 
 
if __name__ == "__main__":
    root = tb.Window(themename="solar")
    app = PythonQuizApp(root)
    root.mainloop()