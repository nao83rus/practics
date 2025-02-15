# экспорт - импорт на внешний ностиель
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
# from kivy.uix.datepicker import DatePicker
from kivy.uix.filechooser import FileChooserListView
from datetime import datetime, timedelta
import os
import json

class Note:
    # def __init__(self, date, start_time, end_time, description, work_time):
    def __init__(self, date, description, work_time):
        self.date = date
        # self.start_time = start_time
        # self.end_time = end_time
        self.description = description
        self.work_time = work_time

class MainApp(App):
    def build(self):
        self.techniques = []  # Список техники
        self.notes = {}  # Заметки для каждой техники
        self.current_technique = None  # Выбранная техника
        self.start_time = None
        self.end_time = None
        self.selected_date = datetime.now().strftime("%Y-%m-%d")  # Текущая дата

        # Основной интерфейс
        self.layout = BoxLayout(orientation="vertical", padding=10, spacing=10)

        # Выбор техники
        self.technique_spinner = Spinner(text="Выберите технику", values=self.techniques)
        self.technique_spinner.bind(text=self.select_technique)
        self.layout.add_widget(self.technique_spinner)

        # Кнопки для управления техникой
        self.technique_buttons = BoxLayout(size_hint_y=None, height=50)
        self.add_technique_button = Button(text="Добавить технику")
        self.add_technique_button.bind(on_press=self.add_technique)
        self.delete_technique_button = Button(text="Удалить технику")
        self.delete_technique_button.bind(on_press=self.delete_technique)
        self.technique_buttons.add_widget(self.add_technique_button)
        self.technique_buttons.add_widget(self.delete_technique_button)
        self.layout.add_widget(self.technique_buttons)

        # Поле для описания
        self.description_input = TextInput(hint_text="Описание", multiline=False)
        self.layout.add_widget(self.description_input)

        # Кнопка для выбора даты
        self.date_button = Button(text=f"Выбрать дату: {self.selected_date}")
        self.date_button.bind(on_press=self.show_date_picker)
        self.layout.add_widget(self.date_button)

        # Кнопки для времени
        self.time_buttons = BoxLayout(size_hint_y=None, height=50)
        self.start_button = Button(text="Начало")
        self.start_button.bind(on_press=self.record_start_time)
        self.end_button = Button(text="Окончание")
        self.end_button.bind(on_press=self.record_end_time)
        self.time_buttons.add_widget(self.start_button)
        self.time_buttons.add_widget(self.end_button)
        self.layout.add_widget(self.time_buttons)

        # Отображение времени начала и окончания
        self.time_labels = BoxLayout(orientation="vertical", spacing=10)
        self.start_time_label = Label(text="Время начала: --:--")
        self.end_time_label = Label(text="Время окончания: --:--")
        self.time_labels.add_widget(self.start_time_label)
        self.time_labels.add_widget(self.end_time_label)
        self.layout.add_widget(self.time_labels)

        # Кнопка для добавления заметки
        self.add_note_button = Button(text="Добавить заметку")
        self.add_note_button.bind(on_press=self.add_note)
        self.layout.add_widget(self.add_note_button)

        # Кнопки для экспорта и импорта
        self.export_import_buttons = BoxLayout(size_hint_y=None, height=50)
        self.export_button = Button(text="Экспорт данных")
        self.export_button.bind(on_press=self.show_export_filechooser)
        self.import_button = Button(text="Импорт данных")
        self.import_button.bind(on_press=self.show_import_filechooser)
        self.export_import_buttons.add_widget(self.export_button)
        self.export_import_buttons.add_widget(self.import_button)
        self.layout.add_widget(self.export_import_buttons)

        # Список заметок
        self.notes_scroll = ScrollView()
        self.notes_layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.notes_layout.bind(minimum_height=self.notes_layout.setter("height"))
        self.notes_scroll.add_widget(self.notes_layout)
        self.layout.add_widget(self.notes_scroll)

        # Общее время работы
        self.total_time_label = Label(text="Общее время работы: 00:00")
        self.layout.add_widget(self.total_time_label)

        # Загрузка данных при запуске
        self.load_data()

        return self.layout

    def show_date_picker(self, instance):
        """Отображение DatePicker для выбора даты."""
        content = BoxLayout(orientation="vertical", padding=10, spacing=10)
        date_picker = DatePicker(date=datetime.strptime(self.selected_date, "%Y-%m-%d"))
        save_button = Button(text="Выбрать")
        popup = Popup(title="Выберите дату", size_hint=(0.8, 0.8))

        def save(instance):
            self.selected_date = date_picker.date.strftime("%Y-%m-%d")
            self.date_button.text = f"Выбрать дату: {self.selected_date}"
            popup.dismiss()

        save_button.bind(on_press=save)
        content.add_widget(date_picker)
        content.add_widget(save_button)
        popup.content = content
        popup.open()

    def select_technique(self, spinner, text):
        """Выбор техники."""
        self.current_technique = text
        self.update_notes()

    def add_technique(self, instance):
        """Добавление новой техники."""
        content = BoxLayout(orientation="vertical", padding=10, spacing=10)
        name_input = TextInput(hint_text="Название техники")
        save_button = Button(text="Сохранить")
        popup = Popup(title="Добавить технику", size_hint=(0.8, 0.4))

        def save(instance):
            if name_input.text:
                self.techniques.append(name_input.text)
                self.technique_spinner.values = self.techniques
                self.notes[name_input.text] = []
                self.save_data()  # Сохранение данных
                popup.dismiss()

        save_button.bind(on_press=save)
        content.add_widget(name_input)
        content.add_widget(save_button)
        popup.content = content
        popup.open()

    def delete_technique(self, instance):
        """Удаление техники."""
        if self.current_technique:
            self.techniques.remove(self.current_technique)
            self.technique_spinner.values = self.techniques
            del self.notes[self.current_technique]
            self.current_technique = None
            self.update_notes()
            self.save_data()  # Сохранение данных

    def record_start_time(self, instance):
        """Фиксация времени начала."""
        self.start_time = datetime.now().strftime("%H:%M")
        self.start_time_label.text = f"Время начала: {self.start_time}"

    def record_end_time(self, instance):
        """Фиксация времени окончания."""
        self.end_time = datetime.now().strftime("%H:%M")
        self.end_time_label.text = f"Время окончания: {self.end_time}"

    def add_note(self, instance):
        """Добавление заметки."""
        if self.current_technique and self.start_time and self.end_time:
            # Расчет времени работы
            start = datetime.strptime(self.start_time, "%H:%M")
            end = datetime.strptime(self.end_time, "%H:%M")
            delta = end - start
            minutes = delta.seconds // 60
            if delta.seconds % 60 != 0:
                minutes += 1  # Округление в большую сторону
            work_time = timedelta(minutes=minutes)

            # Создание заметки
            note = Note(
                date=self.selected_date,
                # start_time=self.start_time,
                # end_time=self.end_time,
                description=self.description_input.text,
                work_time=work_time
            )

            # Добавление заметки
            self.notes[self.current_technique].append(note)
            self.update_notes()
            self.save_data()  # Сохранение данных

            # Очистка полей
            self.start_time = None
            self.end_time = None
            self.description_input.text = ""
            self.start_time_label.text = "Время начала: --:--"
            self.end_time_label.text = "Время окончания: --:--"

    def update_notes(self):
        """Обновление списка заметок."""
        self.notes_layout.clear_widgets()
        if self.current_technique:
            total_time = timedelta()
            for note in self.notes[self.current_technique]:
                note_layout = BoxLayout(size_hint_y=None, height=40)
                # note_label = Label(text=f"{note.date} {note.start_time}-{note.end_time} {note.description} (Время работы: {note.work_time})")
                note_label = Label(text=f"{note.date} {note.description} {note.work_time}")
                edit_button = Button(text="Изменить", size_hint_x=None, width=100)
                edit_button.bind(on_press=lambda btn, n=note: self.edit_note(n))
                delete_button = Button(text="Удалить", size_hint_x=None, width=100)
                delete_button.bind(on_press=lambda btn, n=note: self.delete_note(n))
                note_layout.add_widget(note_label)
                note_layout.add_widget(edit_button)
                note_layout.add_widget(delete_button)
                self.notes_layout.add_widget(note_layout)
                total_time += note.work_time
            self.total_time_label.text = f"Общее время работы: {total_time.seconds // 3600:02}:{(total_time.seconds % 3600) // 60:02}"

    def edit_note(self, note):
        """Редактирование времени работы заметки."""
        content = BoxLayout(orientation="vertical", padding=10, spacing=10)
        work_time_input = TextInput(hint_text="Время работы (минуты)", text=str(note.work_time.seconds // 60))
        save_button = Button(text="Сохранить")
        popup = Popup(title="Редактирование времени работы", size_hint=(0.8, 0.4))

        def save(instance):
            try:
                minutes = int(work_time_input.text)
                note.work_time = timedelta(minutes=minutes)
                self.update_notes()
                self.save_data()  # Сохранение данных
                popup.dismiss()
            except ValueError:
                pass

        save_button.bind(on_press=save)
        content.add_widget(work_time_input)
        content.add_widget(save_button)
        popup.content = content
        popup.open()

    def delete_note(self, note):
        """Удаление заметки."""
        if self.current_technique:
            self.notes[self.current_technique].remove(note)
            self.update_notes()
            self.save_data()  # Сохранение данных

    def save_data(self):
        """Сохранение данных в файл."""
        data = {
            "techniques": self.techniques,
            "notes": {
                technique: [
                    {
                        "date": note.date,
                        # "start_time": note.start_time,
                        # "end_time": note.end_time,
                        "description": note.description,
                        "work_time": note.work_time.seconds
                    }
                    for note in notes
                ]
                for technique, notes in self.notes.items()
            }
        }
        file_path = os.path.join(self.user_data_dir, "data.json")
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

    def load_data(self):
        """Загрузка данных из файла."""
        file_path = os.path.join(self.user_data_dir, "data.json")
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as file:
                data = json.load(file)
                self.techniques = data["techniques"]
                self.technique_spinner.values = self.techniques
                self.notes = {
                    technique: [
                        Note(
                            note["date"],
                            # note["start_time"],
                            # note["end_time"],
                            note["description"],
                            timedelta(seconds=note["work_time"])
                        )
                        for note in notes
                    ]
                    for technique, notes in data["notes"].items()
                }
                self.update_notes()

    def show_export_filechooser(self, instance):
        """Отображение FileChooser для экспорта данных."""
        content = BoxLayout(orientation="vertical", padding=10, spacing=10)
        filechooser = FileChooserListView()
        save_button = Button(text="Экспорт")
        popup = Popup(title="Экспорт данных", size_hint=(0.9, 0.9))

        def save(instance):
            if filechooser.selection:
                file_path = filechooser.selection[0]
                self.export_data(file_path)
                popup.dismiss()

        save_button.bind(on_press=save)
        content.add_widget(filechooser)
        content.add_widget(save_button)
        popup.content = content
        popup.open()

    def show_import_filechooser(self, instance):
        """Отображение FileChooser для импорта данных."""
        content = BoxLayout(orientation="vertical", padding=10, spacing=10)
        filechooser = FileChooserListView()
        load_button = Button(text="Импорт")
        popup = Popup(title="Импорт данных", size_hint=(0.9, 0.9))

        def load(instance):
            if filechooser.selection:
                file_path = filechooser.selection[0]
                self.import_data(file_path)
                popup.dismiss()

        load_button.bind(on_press=load)
        content.add_widget(filechooser)
        content.add_widget(load_button)
        popup.content = content
        popup.open()

    def export_data(self, file_path):
        """Экспорт данных в выбранный файл."""
        data = {
            "techniques": self.techniques,
            "notes": {
                technique: [
                    {
                        "date": note.date,
                        # "start_time": note.start_time,
                        # "end_time": note.end_time,
                        "description": note.description,
                        "work_time": note.work_time.seconds
                    }
                    for note in notes
                ]
                for technique, notes in self.notes.items()
            }
        }
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        print(f"Данные экспортированы в файл: {file_path}")

    def import_data(self, file_path):
        """Импорт данных из выбранного файла."""
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as file:
                data = json.load(file)
                self.techniques = data["techniques"]
                self.technique_spinner.values = self.techniques
                self.notes = {
                    technique: [
                        Note(
                            note["date"],
                            # note["start_time"],
                            # note["end_time"],
                            note["description"],
                            timedelta(seconds=note["work_time"])
                        )
                        for note in notes
                    ]
                    for technique, notes in data["notes"].items()
                }
                self.update_notes()
                self.save_data()  # Сохранение данных в приложение
                print(f"Данные импортированы из файла: {file_path}")
        else:
            print(f"Файл не найден: {file_path}")

if __name__ == "__main__":
    MainApp().run()