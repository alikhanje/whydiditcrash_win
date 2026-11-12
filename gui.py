import threading
import tkinter as tk
from tkinter import ttk

from backend.reader import get_events, group_incidents
from backend.report import build_report


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("WhyDidItCrash")
        self.geometry("820x520")
        self.incidents = []

        # --- верхняя панель: период и кнопка ---
        top = ttk.Frame(self, padding=10)
        top.pack(fill="x")
        ttk.Label(top, text="Период, дней:").pack(side="left")
        self.days = tk.StringVar(value="30")
        ttk.Combobox(
            top, textvariable=self.days, values=["1", "7", "30", "90"],
            width=5, state="readonly",
        ).pack(side="left", padx=6)
        self.button = ttk.Button(top, text="Проверить", command=self.start_scan)
        self.button.pack(side="left", padx=12)
        self.status = ttk.Label(top, text="Нажмите «Проверить»")
        self.status.pack(side="left")

        # --- основная часть: список слева, отчёт справа ---
        body = ttk.Frame(self, padding=(10, 0, 10, 10))
        body.pack(fill="both", expand=True)
        self.listbox = tk.Listbox(body, width=32, exportselection=False)
        self.listbox.pack(side="left", fill="y")
        self.listbox.bind("<<ListboxSelect>>", self.show_selected)
        self.text = tk.Text(body, wrap="word", state="disabled")
        self.text.pack(side="left", fill="both", expand=True, padx=(10, 0))

    def start_scan(self):
        self.button.config(state="disabled")
        self.status.config(text="Проверяю журнал Windows...")
        hours = int(self.days.get()) * 24
        # чтение журнала занимает пару секунд, поэтому делаем его в отдельном потоке,
        # иначе окно «замёрзнет»
        threading.Thread(target=self.scan, args=(hours,), daemon=True).start()

    def scan(self, hours):
        try:
            incidents = group_incidents(get_events([41, 1001], hours=hours))
            self.after(0, self.show_results, incidents)
        except Exception as error:
            self.after(0, self.show_error, str(error))

    def show_results(self, incidents):
        self.incidents = list(reversed(incidents))  # сначала самые свежие
        self.listbox.delete(0, "end")
        for incident in self.incidents:
            when = incident["first_time"].strftime("%d.%m.%Y %H:%M")
            kind = "Синий экран" if incident["type"] == "bsod" else "Выключение"
            self.listbox.insert("end", f"{when}  {kind}")

        if self.incidents:
            self.status.config(text=f"Найдено вылетов: {len(self.incidents)}")
            self.listbox.selection_set(0)
            self.show_selected()
        else:
            self.status.config(text="Вылетов за этот период не найдено")
            self.set_text("Всё спокойно: за выбранный период синих экранов и "
                          "неожиданных выключений не было.")
        self.button.config(state="normal")

    def show_error(self, message):
        self.status.config(text="Ошибка при чтении журнала")
        self.set_text(f"Не удалось прочитать журнал событий:\n{message}")
        self.button.config(state="normal")

    def show_selected(self, event=None):
        selection = self.listbox.curselection()
        if selection:
            self.set_text(build_report(self.incidents[selection[0]]))

    def set_text(self, content):
        self.text.config(state="normal")
        self.text.delete("1.0", "end")
        self.text.insert("1.0", content)
        self.text.config(state="disabled")


if __name__ == "__main__":
    App().mainloop()