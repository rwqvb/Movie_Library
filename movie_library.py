"""
Movie Library — Личная кинотека
Автор: Иван Петров
Описание: GUI-приложение для хранения информации о фильмах
          с фильтрацией, сохранением в JSON и поддержкой Git.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

DATA_FILE = "movies.json"


# ─────────────────────────────────────────────
#  Работа с данными (JSON)
# ─────────────────────────────────────────────

def load_movies() -> list[dict]:
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    return []


def save_movies(movies: list[dict]) -> None:
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(movies, f, ensure_ascii=False, indent=2)


# ─────────────────────────────────────────────
#  Валидация
# ─────────────────────────────────────────────

def validate_year(value: str) -> tuple[bool, str]:
    try:
        year = int(value)
    except ValueError:
        return False, "Год должен быть целым числом."
    current_year = datetime.now().year
    if not (1888 <= year <= current_year + 5):
        return False, f"Год должен быть в диапазоне 1888–{current_year + 5}."
    return True, ""


def validate_rating(value: str) -> tuple[bool, str]:
    try:
        rating = float(value)
    except ValueError:
        return False, "Рейтинг должен быть числом (например, 7.5)."
    if not (0.0 <= rating <= 10.0):
        return False, "Рейтинг должен быть от 0 до 10."
    return True, ""


# ─────────────────────────────────────────────
#  Главное окно
# ─────────────────────────────────────────────

class MovieLibraryApp(tk.Tk):
    GENRES = [
        "Все жанры", "Боевик", "Документальный", "Драма",
        "Комедия", "Мелодрама", "Мультфильм", "Приключения",
        "Триллер", "Ужасы", "Фантастика", "Фэнтези",
    ]

    COLUMNS = ("title", "genre", "year", "rating")
    COL_LABELS = {
        "title": "Название",
        "genre": "Жанр",
        "year": "Год",
        "rating": "Рейтинг",
    }

    def __init__(self):
        super().__init__()
        self.title("🎬 Movie Library — Личная кинотека")
        self.geometry("960x640")
        self.resizable(True, True)
        self.configure(bg="#0f0f1a")
        self.movies: list[dict] = load_movies()
        self._build_ui()
        self._refresh_table()

    # ── UI построение ──────────────────────────

    def _build_ui(self):
        self._apply_styles()
        self._build_header()
        self._build_form()
        self._build_filter_bar()
        self._build_table()
        self._build_status_bar()

    def _apply_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")

        # Таблица
        style.configure("Treeview",
                        background="#12122b",
                        foreground="#e0e0f5",
                        fieldbackground="#12122b",
                        rowheight=32,
                        font=("Courier New", 11))
        style.configure("Treeview.Heading",
                        background="#1e1e40",
                        foreground="#a78bfa",
                        font=("Courier New", 11, "bold"),
                        relief="flat")
        style.map("Treeview",
                  background=[("selected", "#6d28d9")],
                  foreground=[("selected", "#ffffff")])
        style.map("Treeview.Heading",
                  background=[("active", "#2d2d60")])

        # Скроллбар
        style.configure("Vertical.TScrollbar",
                        background="#1e1e40",
                        troughcolor="#0f0f1a",
                        arrowcolor="#a78bfa")

        # Combobox
        style.configure("TCombobox",
                        fieldbackground="#1e1e40",
                        background="#1e1e40",
                        foreground="#e0e0f5",
                        selectbackground="#6d28d9",
                        arrowcolor="#a78bfa")
        style.map("TCombobox",
                  fieldbackground=[("readonly", "#1e1e40")],
                  foreground=[("readonly", "#e0e0f5")])

    def _build_header(self):
        hdr = tk.Frame(self, bg="#0f0f1a")
        hdr.pack(fill="x", padx=24, pady=(20, 4))
        tk.Label(hdr, text="🎬 MOVIE LIBRARY",
                 bg="#0f0f1a", fg="#a78bfa",
                 font=("Courier New", 22, "bold")).pack(side="left")
        tk.Label(hdr, text="Личная кинотека",
                 bg="#0f0f1a", fg="#6b7280",
                 font=("Courier New", 11)).pack(side="left", padx=12, pady=6)

    def _entry(self, parent, placeholder: str, width: int = 20) -> tk.Entry:
        e = tk.Entry(parent, bg="#1e1e40", fg="#e0e0f5",
                     insertbackground="#a78bfa",
                     font=("Courier New", 11),
                     relief="flat", bd=0,
                     width=width,
                     highlightthickness=1,
                     highlightbackground="#2d2d60",
                     highlightcolor="#a78bfa")
        e.insert(0, placeholder)
        e.bind("<FocusIn>",  lambda ev, p=placeholder, w=e: self._clear_placeholder(ev, p, w))
        e.bind("<FocusOut>", lambda ev, p=placeholder, w=e: self._restore_placeholder(ev, p, w))
        return e

    @staticmethod
    def _clear_placeholder(_, placeholder, widget):
        if widget.get() == placeholder:
            widget.delete(0, tk.END)
            widget.config(fg="#e0e0f5")

    @staticmethod
    def _restore_placeholder(_, placeholder, widget):
        if not widget.get():
            widget.insert(0, placeholder)
            widget.config(fg="#4b5563")

    def _build_form(self):
        card = tk.Frame(self, bg="#12122b", bd=0,
                        highlightthickness=1,
                        highlightbackground="#2d2d60")
        card.pack(fill="x", padx=24, pady=(8, 0))

        inner = tk.Frame(card, bg="#12122b")
        inner.pack(fill="x", padx=16, pady=12)

        # Метки + поля
        labels = ["Название", "Жанр", "Год выпуска", "Рейтинг (0-10)"]
        for i, lbl in enumerate(labels):
            tk.Label(inner, text=lbl, bg="#12122b", fg="#a78bfa",
                     font=("Courier New", 9, "bold")).grid(
                row=0, column=i, padx=8, sticky="w")

        self.ent_title  = self._entry(inner, "Например: Интерстеллар", 26)
        self.ent_title.grid(row=1, column=0, padx=8, pady=(2, 0), ipady=6)

        self.cmb_genre = ttk.Combobox(inner,
                                      values=self.GENRES[1:],
                                      font=("Courier New", 11),
                                      width=18, state="readonly")
        self.cmb_genre.set("Драма")
        self.cmb_genre.grid(row=1, column=1, padx=8, pady=(2, 0), ipady=4)

        self.ent_year   = self._entry(inner, "2024", 10)
        self.ent_year.grid(row=1, column=2, padx=8, pady=(2, 0), ipady=6)

        self.ent_rating = self._entry(inner, "8.5", 12)
        self.ent_rating.grid(row=1, column=3, padx=8, pady=(2, 0), ipady=6)

        btn = tk.Button(inner, text="+ Добавить фильм",
                        command=self._add_movie,
                        bg="#6d28d9", fg="#ffffff",
                        activebackground="#7c3aed",
                        activeforeground="#ffffff",
                        font=("Courier New", 11, "bold"),
                        relief="flat", bd=0,
                        padx=18, pady=8,
                        cursor="hand2")
        btn.grid(row=1, column=4, padx=(16, 0), pady=(2, 0))

        del_btn = tk.Button(inner, text="🗑 Удалить",
                            command=self._delete_selected,
                            bg="#1e1e40", fg="#ef4444",
                            activebackground="#2d2d60",
                            activeforeground="#ef4444",
                            font=("Courier New", 10),
                            relief="flat", bd=0,
                            padx=12, pady=8,
                            cursor="hand2")
        del_btn.grid(row=1, column=5, padx=8, pady=(2, 0))

    def _build_filter_bar(self):
        bar = tk.Frame(self, bg="#0f0f1a")
        bar.pack(fill="x", padx=24, pady=(10, 4))

        tk.Label(bar, text="Фильтры:", bg="#0f0f1a", fg="#6b7280",
                 font=("Courier New", 10, "bold")).pack(side="left")

        # Жанр
        tk.Label(bar, text="Жанр:", bg="#0f0f1a", fg="#9ca3af",
                 font=("Courier New", 10)).pack(side="left", padx=(12, 4))
        self.filter_genre = ttk.Combobox(bar, values=self.GENRES,
                                         font=("Courier New", 10),
                                         width=16, state="readonly")
        self.filter_genre.set("Все жанры")
        self.filter_genre.pack(side="left")
        self.filter_genre.bind("<<ComboboxSelected>>", lambda _: self._refresh_table())

        # Год — от
        tk.Label(bar, text="Год от:", bg="#0f0f1a", fg="#9ca3af",
                 font=("Courier New", 10)).pack(side="left", padx=(16, 4))
        self.filter_year_from = tk.Entry(bar, bg="#1e1e40", fg="#e0e0f5",
                                         insertbackground="#a78bfa",
                                         font=("Courier New", 10),
                                         width=6, relief="flat",
                                         highlightthickness=1,
                                         highlightbackground="#2d2d60",
                                         highlightcolor="#a78bfa")
        self.filter_year_from.pack(side="left", ipady=4)
        self.filter_year_from.bind("<KeyRelease>", lambda _: self._refresh_table())

        # Год — до
        tk.Label(bar, text="до:", bg="#0f0f1a", fg="#9ca3af",
                 font=("Courier New", 10)).pack(side="left", padx=(6, 4))
        self.filter_year_to = tk.Entry(bar, bg="#1e1e40", fg="#e0e0f5",
                                       insertbackground="#a78bfa",
                                       font=("Courier New", 10),
                                       width=6, relief="flat",
                                       highlightthickness=1,
                                       highlightbackground="#2d2d60",
                                       highlightcolor="#a78bfa")
        self.filter_year_to.pack(side="left", ipady=4)
        self.filter_year_to.bind("<KeyRelease>", lambda _: self._refresh_table())

        # Сброс
        tk.Button(bar, text="✕ Сбросить",
                  command=self._reset_filters,
                  bg="#0f0f1a", fg="#6b7280",
                  activebackground="#1e1e40",
                  activeforeground="#a78bfa",
                  font=("Courier New", 9),
                  relief="flat", bd=0,
                  padx=10, pady=4,
                  cursor="hand2").pack(side="left", padx=12)

    def _build_table(self):
        frame = tk.Frame(self, bg="#0f0f1a")
        frame.pack(fill="both", expand=True, padx=24, pady=(4, 0))

        self.tree = ttk.Treeview(frame,
                                 columns=self.COLUMNS,
                                 show="headings",
                                 selectmode="browse")

        widths = {"title": 320, "genre": 160, "year": 90, "rating": 100}
        for col in self.COLUMNS:
            self.tree.heading(col, text=self.COL_LABELS[col],
                              command=lambda c=col: self._sort_by(c))
            self.tree.column(col, width=widths[col],
                             anchor="center" if col != "title" else "w")

        vsb = ttk.Scrollbar(frame, orient="vertical",
                            command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)

        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        # Чередование строк
        self.tree.tag_configure("even", background="#12122b")
        self.tree.tag_configure("odd",  background="#0f0f1a")

    def _build_status_bar(self):
        self.status_var = tk.StringVar(value="Готово.")
        bar = tk.Frame(self, bg="#0a0a14", height=26)
        bar.pack(fill="x", side="bottom")
        tk.Label(bar, textvariable=self.status_var,
                 bg="#0a0a14", fg="#4b5563",
                 font=("Courier New", 9),
                 anchor="w").pack(side="left", padx=16, pady=3)
        self.count_var = tk.StringVar()
        tk.Label(bar, textvariable=self.count_var,
                 bg="#0a0a14", fg="#6d28d9",
                 font=("Courier New", 9, "bold"),
                 anchor="e").pack(side="right", padx=16, pady=3)

    # ── Логика ─────────────────────────────────

    def _get_entry_value(self, widget: tk.Entry, placeholder: str) -> str:
        val = widget.get().strip()
        return "" if val == placeholder else val

    def _add_movie(self):
        title  = self._get_entry_value(self.ent_title,  "Например: Интерстеллар")
        genre  = self.cmb_genre.get().strip()
        year   = self._get_entry_value(self.ent_year,   "2024")
        rating = self._get_entry_value(self.ent_rating, "8.5")

        # Валидация
        errors = []
        if not title:
            errors.append("Введите название фильма.")
        ok, msg = validate_year(year)
        if not ok:
            errors.append(msg)
        ok, msg = validate_rating(rating)
        if not ok:
            errors.append(msg)

        if errors:
            messagebox.showerror("Ошибка ввода", "\n".join(errors))
            return

        movie = {
            "title":  title,
            "genre":  genre,
            "year":   int(year),
            "rating": round(float(rating), 1),
        }
        self.movies.append(movie)
        save_movies(self.movies)
        self._refresh_table()
        self._set_status(f"Добавлен: «{title}»")

        # Очистить поля
        self.ent_title.delete(0, tk.END)
        self.ent_title.insert(0, "Например: Интерстеллар")
        self.ent_title.config(fg="#4b5563")
        self.ent_year.delete(0, tk.END)
        self.ent_year.insert(0, "2024")
        self.ent_year.config(fg="#4b5563")
        self.ent_rating.delete(0, tk.END)
        self.ent_rating.insert(0, "8.5")
        self.ent_rating.config(fg="#4b5563")

    def _delete_selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Удаление", "Выберите фильм для удаления.")
            return
        idx = self.tree.index(sel[0])
        filtered = self._get_filtered()
        movie = filtered[idx]
        if messagebox.askyesno("Удаление",
                               f"Удалить «{movie['title']}»?"):
            self.movies.remove(movie)
            save_movies(self.movies)
            self._refresh_table()
            self._set_status(f"Удалён: «{movie['title']}»")

    def _get_filtered(self) -> list[dict]:
        genre_filter = self.filter_genre.get()
        year_from_s  = self.filter_year_from.get().strip()
        year_to_s    = self.filter_year_to.get().strip()

        year_from = int(year_from_s) if year_from_s.isdigit() else None
        year_to   = int(year_to_s)   if year_to_s.isdigit()   else None

        result = []
        for m in self.movies:
            if genre_filter != "Все жанры" and m["genre"] != genre_filter:
                continue
            if year_from and m["year"] < year_from:
                continue
            if year_to and m["year"] > year_to:
                continue
            result.append(m)
        return result

    def _refresh_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        filtered = self._get_filtered()
        for i, m in enumerate(filtered):
            tag = "even" if i % 2 == 0 else "odd"
            self.tree.insert("", "end", values=(
                m["title"],
                m["genre"],
                m["year"],
                f"⭐ {m['rating']:.1f}",
            ), tags=(tag,))

        total   = len(self.movies)
        showing = len(filtered)
        self.count_var.set(
            f"Показано: {showing} / {total} фильмов"
        )

    def _sort_by(self, col: str):
        key_map = {
            "title":  lambda m: m["title"].lower(),
            "genre":  lambda m: m["genre"].lower(),
            "year":   lambda m: m["year"],
            "rating": lambda m: m["rating"],
        }
        self.movies.sort(key=key_map[col])
        save_movies(self.movies)
        self._refresh_table()
        self._set_status(f"Отсортировано по: {self.COL_LABELS[col]}")

    def _reset_filters(self):
        self.filter_genre.set("Все жанры")
        self.filter_year_from.delete(0, tk.END)
        self.filter_year_to.delete(0, tk.END)
        self._refresh_table()
        self._set_status("Фильтры сброшены.")

    def _set_status(self, msg: str):
        self.status_var.set(msg)


# ─────────────────────────────────────────────

if __name__ == "__main__":
    app = MovieLibraryApp()
    app.mainloop()
