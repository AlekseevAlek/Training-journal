import tkinter as tk
from tkinter import ttk, Toplevel, messagebox, Label, Entry, Button
import json
from datetime import datetime, timedelta
import csv
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


# Файл для сохранения данных
data_file = 'training_log.json'


def load_data():
    """Загрузка данных о тренировках из файла."""
    try:
        with open(data_file, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_data(data):
    """Сохранение данных о тренировках в файл."""
    with open(data_file, 'w') as file:
        json.dump(data, file, indent=4)


class TrainingLogApp:
    def __init__(self, root):
        """ Конструктор класса __init__ принимает объект root, который является главным окном приложения."""
        self.root = root
        root.title("Дневник тренировок")
        self.create_widgets()

    def create_widgets(self):
        """Создание виджетов для ввода данных."""
        self.exercise_label = ttk.Label(self.root, text="Упражнение:")
        self.exercise_label.grid(column=0, row=0, sticky=tk.W, padx=5, pady=5)

        self.exercise_entry = ttk.Entry(self.root)
        self.exercise_entry.grid(column=1, row=0, sticky=tk.EW, padx=5, pady=5)

        self.weight_label = ttk.Label(self.root, text="Вес:")
        self.weight_label.grid(column=0, row=1, sticky=tk.W, padx=5, pady=5)

        self.weight_entry = ttk.Entry(self.root)
        self.weight_entry.grid(column=1, row=1, sticky=tk.EW, padx=5, pady=5)

        self.repetitions_label = ttk.Label(self.root, text="Повторения:")
        self.repetitions_label.grid(column=0, row=2, sticky=tk.W, padx=5, pady=5)

        self.repetitions_entry = ttk.Entry(self.root)
        self.repetitions_entry.grid(column=1, row=2, sticky=tk.EW, padx=5, pady=5)

        self.add_button = ttk.Button(self.root, text="Добавить запись", command=self.add_entry)
        self.add_button.grid(column=0, row=3, columnspan=2, pady=10)

        self.view_button = ttk.Button(self.root, text="Просмотреть записи", command=self.view_records)
        self.view_button.grid(column=0, row=4, columnspan=2, pady=10)

        # Поле для выбора периода
        self.start_date_label = ttk.Label(self.root, text="Начало периода:")
        self.start_date_label.grid(column=0, row=5, sticky=tk.W, padx=5, pady=5)

        self.start_date_entry = ttk.Entry(self.root)
        self.start_date_entry.grid(column=1, row=5, sticky=tk.EW, padx=5, pady=5)

        self.end_date_label = ttk.Label(self.root, text="Конец периода:")
        self.end_date_label.grid(column=0, row=6, sticky=tk.W, padx=5, pady=5)

        self.end_date_entry = ttk.Entry(self.root)
        self.end_date_entry.grid(column=1, row=6, sticky=tk.EW, padx=5, pady=5)

        # Выпадающий список для выбора упражнения
        self.exercise_label = ttk.Label(self.root, text="Упражнение:")
        self.exercise_label.grid(column=0, row=7, sticky=tk.W, padx=5, pady=5)

        self.exercise_var = tk.StringVar()
        self.exercise_combo = ttk.Combobox(self.root, textvariable=self.exercise_var)
        self.exercise_combo['values'] = sorted(set(entry['exercise'] for entry in load_data()))
        self.exercise_combo.grid(column=1, row=7, sticky=tk.EW, padx=5, pady=5)

        self.export_button = ttk.Button(self.root, text="Экспортировать в CSV", command=self.export_to_csv)
        self.export_button.grid(column=0, row=8, columnspan=2, pady=10)

        self.import_button = ttk.Button(self.root, text="Импортировать из CSV", command=self.import_from_csv)
        self.import_button.grid(column=0, row=9, columnspan=2, pady=10)

        self.edit_button = ttk.Button(self.root, text="Редактировать запись", command=self.edit_entry)
        self.edit_button.grid(column=0, row=10, columnspan=2, pady=10)

        self.delete_button = ttk.Button(self.root, text="Удалить запись", command=self.delete_entry)
        self.delete_button.grid(column=0, row=11, columnspan=2, pady=10)

        # Treeview для отображения всех записей
        self.tree_frame = ttk.Frame(self.root)
        self.tree_frame.grid(row=12, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
        self.root.grid_rowconfigure(12, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Заполняем Treeview данными
        data = load_data()
        self.tree = ttk.Treeview(self.tree_frame, columns=("Дата", "Упражнение", "Вес", "Повторения"), show="headings")
        self.tree.heading('Дата', text="Дата")
        self.tree.heading('Упражнение', text="Упражнение")
        self.tree.heading('Вес', text="Вес")
        self.tree.heading('Повторения', text="Повторения")

        for entry in data:
            self.tree.insert('', tk.END,
                             values=(entry['date'], entry['exercise'], entry['weight'], entry['repetitions']))

        self.tree.pack(expand=True, fill=tk.BOTH)

        self.statistics_button = ttk.Button(self.root, text="Статистика", command=self.display_statistics)
        self.statistics_button.grid(column=0, row=13, columnspan=2, pady=10)

        self.visualize_button = ttk.Button(self.root, text="Визуализация прогресса", command=self.visualize_progress)
        self.visualize_button.grid(column=0, row=14, columnspan=2, pady=10)

    def show_treeview(self):
        """Отображение таблицы."""
        if not hasattr(self, 'tree'):
            self.create_treeview()
        self.tree_frame.grid()

    def hide_treeview(self):
        """Закрытие таблицы."""
        if hasattr(self, 'tree'):
            self.tree_frame.grid_forget()

    def add_entry(self):
        """Считывание данных из полей ввода."""
        date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        exercise = self.exercise_entry.get()
        weight = self.weight_entry.get()
        repetitions = self.repetitions_entry.get()

        if not (exercise and weight and repetitions):
            messagebox.showerror("Ошибка", "Все поля должны быть заполнены!")
            return

        entry = {
            'date': date,
            'exercise': exercise,
            'weight': weight,
            'repetitions': repetitions
        }

        data = load_data()
        data.append(entry)
        save_data(data)

        # Очистка полей ввода после добавления
        self.exercise_entry.delete(0, tk.END)
        self.weight_entry.delete(0, tk.END)
        self.repetitions_entry.delete(0, tk.END)
        messagebox.showinfo("Успешно", "Запись успешно добавлена!")
        self.show_treeview()

    def view_records(self):
        """Загрузка сохраненных данных."""
        data = self.filter_data()
        records_window = Toplevel(self.root)
        records_window.title("Записи тренировок")

        tree = ttk.Treeview(records_window, columns=("Дата", "Упражнение", "Вес", "Повторения"), show="headings")
        tree.heading('Дата', text="Дата")
        tree.heading('Упражнение', text="Упражнение")
        tree.heading('Вес', text="Вес")
        tree.heading('Повторения', text="Повторения")

        for entry in data:
            tree.insert('', tk.END, values=(entry['date'], entry['exercise'], entry['weight'], entry['repetitions']))

        tree.pack(expand=True, fill=tk.BOTH)

    def filter_data(self):
        """Фильтрует данные по дате."""
        start_date = self.start_date_entry.get()
        end_date = self.end_date_entry.get()
        exercise = self.exercise_var.get()

        filtered_data = load_data()

        if start_date and end_date:
            try:
                start = datetime.strptime(start_date, '%Y-%m-%d')
                end = datetime.strptime(end_date, '%Y-%m-%d')
                filtered_data = [entry for entry in filtered_data
                                 if start <= datetime.strptime(entry['date'], '%Y-%m-%d %H:%M:%S') <= end]
            except ValueError:
                messagebox.showerror("Ошибка", "Неверный формат даты!")

        if exercise:
            filtered_data = self.filter_by_exercise(filtered_data, exercise)

        return filtered_data

    def filter_by_exercise(self, data, exercise):
        """Фильтрует данные по упражнению."""
        return [entry for entry in data if entry['exercise'] == exercise]

    def export_to_csv(self):
        """Экспортирует все данные в CSV файл."""
        data = load_data()

        if not data:
            messagebox.showinfo("Информация", "В данный момент нет записей для экспорта.")
            return

        csv_file = 'training_log.csv'

        with open(csv_file, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Дата', 'Упражнение', 'Вес', 'Повторения'])

            for entry in data:
                writer.writerow([
                    entry['date'],
                    entry['exercise'],
                    entry['weight'],
                    entry['repetitions']
                ])

        messagebox.showinfo("Информация", f"Данные успешно сохранены в {csv_file}")

    def import_from_csv(self):
        """Импортирует данные из CSV файла."""
        csv_file = 'training_log.csv'

        try:
            with open(csv_file, 'r', newline='', encoding='utf-8') as file:
                reader = csv.reader(file)
                next(reader)  # Пропускаем заголовок

                data = []
                for row in reader:
                    if len(row) == 4:
                        entry = {
                            'date': row[0],
                            'exercise': row[1],
                            'weight': row[2],
                            'repetitions': row[3]
                        }
                        data.append(entry)

                save_data(data)
            messagebox.showinfo("Информация", "Данные успешно импортированы.")
        except FileNotFoundError:
            messagebox.showerror("Ошибка", f"Файл {csv_file} не найден.")
        except Exception as e:
            messagebox.showerror("Ошибка", f"При импорте произошла ошибка: {str(e)}")

    def edit_entry(self):
        """Редактирует выбранную запись."""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Ошибка", "Пожалуйста, выберите запись для редактирования.")
            return

        selected_item = selected_item[0]
        entry_data = self.tree.item(selected_item, 'values')

        edit_window = Toplevel(self.root)
        edit_window.title("Редактирование записи")

        Label(edit_window, text="Дата").grid(row=0, column=0)
        Label(edit_window, text="Упражнение").grid(row=1, column=0)
        Label(edit_window, text="Вес").grid(row=2, column=0)
        Label(edit_window, text="Повторения").grid(row=3, column=0)

        date_entry = Entry(edit_window)
        exercise_entry = Entry(edit_window)
        weight_entry = Entry(edit_window)
        repetitions_entry = Entry(edit_window)

        date_entry.insert(0, entry_data[0])
        exercise_entry.insert(0, entry_data[1])
        weight_entry.insert(0, entry_data[2])
        repetitions_entry.insert(0, entry_data[3])

        date_entry.grid(row=0, column=1)
        exercise_entry.grid(row=1, column=1)
        weight_entry.grid(row=2, column=1)
        repetitions_entry.grid(row=3, column=1)

        def save_changes():
            """Сохранение изменений."""
            new_data = {
                'date': date_entry.get(),
                'exercise': exercise_entry.get(),
                'weight': weight_entry.get(),
                'repetitions': repetitions_entry.get()
            }

            data = load_data()
            data[self.tree.index(selected_item)] = new_data
            save_data(data)

            self.tree.item(selected_item,
                           values=(new_data['date'], new_data['exercise'], new_data['weight'], new_data['repetitions']))
            edit_window.destroy()

        Button(edit_window, text="Сохранить изменения", command=save_changes).grid(row=4, column=0, columnspan=2)

    def delete_entry(self):
        """Удаляет выбранную запись."""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Ошибка", "Пожалуйста, выберите запись для удаления.")
            return

        selected_item = selected_item[0]

        response = messagebox.askyesno("Подтверждение", f"Вы уверены, что хотите удалить эту запись?")

        if response:
            data = load_data()

            # Получаем значение из Treeview
            values = self.tree.item(selected_item, 'values')

            # Находим индекс записи в данных
            index = next(i for i, entry in enumerate(data) if entry['date'] == values[0])

            # Удаляем запись из данных
            data.pop(index)

            save_data(data)

            # Удаляем запись из Treeview
            self.tree.delete(selected_item)

            messagebox.showinfo("Успешно", "Запись успешно удалена!")
            self.show_treeview()

    def calculate_monthly_statistics(self):
        """Расчёт статистики."""
        data = load_data()
        current_date = datetime.now().replace(day=1)
        monthly_stats = {}

        while current_date.year == datetime.now().year or current_date.month == datetime.now().month:
            month_start = current_date.strftime("%Y-%m-%d")
            month_end = (current_date + timedelta(days=32)).strftime("%Y-%m-%d")[:-3]

            month_data = [entry for entry in data if month_start <= entry['date'] <= month_end]

            total_weight = sum(float(entry['weight']) for entry in month_data)
            total_repetitions = sum(int(entry['repetitions']) for entry in month_data)

            monthly_stats[current_date.strftime("%B %Y")] = {
                'total_weight': total_weight,
                'total_repetitions': total_repetitions
            }

            current_date += timedelta(days=32)
            if current_date > datetime.now():
                break

        return monthly_stats

    def display_statistics(self):
        """Отображуние статистики."""
        stats_window = Toplevel(self.root)
        stats_window.title("Статистика упражнений")

        label_frame = ttk.Frame(stats_window)
        label_frame.pack(padx=10, pady=10, fill=tk.X)

        for exercise, stats in self.calculate_monthly_statistics().items():
            ttk.Label(label_frame, text=f"{exercise}:").pack(side=tk.LEFT)
            ttk.Label(label_frame, text=f"Общий вес: {stats['total_weight']:.2f} кг").pack(side=tk.LEFT)
            ttk.Label(label_frame, text=f"Общее количество повторений: {stats['total_repetitions']}").pack(side=tk.LEFT)
            ttk.Label(label_frame, text="").pack(side=tk.LEFT)  # Отступ между упражнениями

    def prepare_data_for_visualization(self):
        """Подготовка данных для визуализации."""
        data = self.filter_data()

        # Группировка данных по упражнениям
        exercise_data = {}
        for entry in data:
            exercise = entry['exercise']
            if exercise not in exercise_data:
                exercise_data[exercise] = []
            exercise_data[exercise].append({
                'date': datetime.strptime(entry['date'], '%Y-%m-%d %H:%M:%S'),
                'weight': float(entry['weight']),
                'repetitions': int(entry['repetitions'])
            })

        return exercise_data

    def visualize_progress(self):
        """Визуализация в виде графика."""
        data = self.prepare_data_for_visualization()

        # Создаем новое главное окно
        progress_window = Toplevel(self.root)
        progress_window.title("Визуализация прогресса")

        # Создаем фигуру и канвас
        fig, ax = plt.subplots(figsize=(10, 6))
        canvas = FigureCanvasTkAgg(fig, master=progress_window)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        # Добавляем подписи осей
        ax.set_xlabel('Дата')
        ax.set_ylabel('Значение')

        # Цикл по упражнениям
        for exercise, entries in data.items():
            dates = [entry['date'] for entry in entries]
            weights = [entry['weight'] for entry in entries]
            repetitions = [entry['repetitions'] for entry in entries]

            ax.plot(dates, weights, label=f'Вес ({exercise})', color='blue')

            ax.plot(dates, repetitions, label=f'Повторения ({exercise})', color='red')

        # Добавляем легенду
        ax.legend()

        # Настройка масштаба осей
        ax.set_xlim(min(dates), max(dates))
        ax.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))
        plt.gcf().autofmt_xdate()

        # Создаем кнопку для закрытия окна
        close_button = ttk.Button(progress_window, text="Закрыть", command=progress_window.destroy)
        close_button.pack(side=tk.BOTTOM, pady=10)


def main():
    """Запускает главный цикл обработки событий Tkinter."""
    root = tk.Tk()
    app = TrainingLogApp(root)
    app.show_treeview()
    root.mainloop()


if __name__ == "__main__":
    main()
