from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from datetime import datetime, timedelta
import json
import os
import math


class NoteApp(App):
    def build(self):
        self.notes_file = "notes.json"
        self.notes = self.load_notes()

        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        self.date_label = Label(text="Дата: " + datetime.now().strftime('%Y-%m-%d'))
        self.layout.add_widget(self.date_label)

        self.description_input = TextInput(hint_text="Описание", multiline=False)
        self.layout.add_widget(self.description_input)

        self.start_time_button = Button(text="Зафиксировать время начала")
        self.start_time_button.bind(on_press=self.record_start_time)
        self.layout.add_widget(self.start_time_button)

        self.end_time_button = Button(text="Зафиксировать время окончания")
        self.end_time_button.bind(on_press=self.record_end_time)
        self.layout.add_widget(self.end_time_button)

        self.worked_time_label = Label(text="Отработанное время: 00:00:00")
        self.layout.add_widget(self.worked_time_label)

        self.save_button = Button(text="Сохранить заметку")
        self.save_button.bind(on_press=self.save_note)
        self.layout.add_widget(self.save_button)

        self.notes_scroll = ScrollView(size_hint=(1, None), size=(400, 300))
        self.notes_grid = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.notes_grid.bind(minimum_height=self.notes_grid.setter('height'))
        self.notes_scroll.add_widget(self.notes_grid)
        self.layout.add_widget(self.notes_scroll)

        self.start_time = None
        self.end_time = None

        self.update_notes_list()

        return self.layout

    def load_notes(self):
        if os.path.exists(self.notes_file):
            with open(self.notes_file, "r", encoding="utf-8") as file:
                return json.load(file)
        return []

    def save_notes(self):
        with open(self.notes_file, "w", encoding="utf-8") as file:
            json.dump(self.notes, file, ensure_ascii=False, indent=4)

    def record_start_time(self, instance):
        self.start_time = datetime.now()
        self.show_popup("Время начала", self.start_time.strftime('%H:%M:%S'))

    def record_end_time(self, instance):
        if self.start_time is None:
            self.show_popup("Ошибка", "Сначала зафиксируйте время начала")
            return

        self.end_time = datetime.now()
        worked_time = self.end_time - self.start_time
        worked_time_rounded = self.round_up_to_minute(worked_time)
        self.worked_time_label.text = f"Отработанное время: {worked_time_rounded}"
        self.show_popup("Время окончания", self.end_time.strftime('%H:%M:%S'))

    def round_up_to_minute(self, timedelta_obj):
        # Округляем секунды в большую сторону до минут
        seconds = timedelta_obj.total_seconds()
        minutes = math.ceil(seconds / 60)
        return f"{minutes // 60:02}:{minutes % 60:02}:00"

    def save_note(self, instance):
        if self.start_time is None or self.end_time is None:
            self.show_popup("Ошибка", "Зафиксируйте время начала и окончания")
            return

        note = {
            "Дата": self.date_label.text,
            "Описание": self.description_input.text,
            "Время начала": self.start_time.strftime('%H:%M:%S'),
            "Время окончания": self.end_time.strftime('%H:%M:%S'),
            "Отработанное время": self.worked_time_label.text
        }

        self.notes.append(note)
        self.save_notes()
        self.update_notes_list()
        self.show_popup("Сохранено", "Заметка успешно сохранена")

    def update_notes_list(self):
        self.notes_grid.clear_widgets()
        for i, note in enumerate(self.notes):
            note_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
            note_text = f"{note['Дата']} - {note['Описание']} ({note['Отработанное время']})"
            note_label = Label(text=note_text, size_hint_x=0.8)
            delete_button = Button(text="Удалить", size_hint_x=0.2)
            delete_button.bind(on_press=lambda btn, idx=i: self.delete_note(idx))
            note_layout.add_widget(note_label)
            note_layout.add_widget(delete_button)
            self.notes_grid.add_widget(note_layout)

    def delete_note(self, index):
        del self.notes[index]
        self.save_notes()
        self.update_notes_list()
        self.show_popup("Удалено", "Заметка успешно удалена")

    def show_popup(self, title, message):
        popup_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        popup_label = Label(text=message)
        close_button = Button(text="Закрыть")
        popup_layout.add_widget(popup_label)
        popup_layout.add_widget(close_button)

        popup = Popup(title=title, content=popup_layout, size_hint=(0.8, 0.4))
        close_button.bind(on_press=popup.dismiss)
        popup.open()

if __name__ == '__main__':
    NoteApp().run()