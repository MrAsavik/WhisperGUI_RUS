import customtkinter as ctk

class MyApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title('Test App')
        self.btn = ctk.CTkButton(self, text='Close', command=self.close_app)
        self.btn.pack(pady=20)
        self.protocol('WM_DELETE_WINDOW', self.close_app)

    def close_app(self):
        self.destroy()

if __name__ == '__main__':
    app = MyApp()
    app.mainloop()
