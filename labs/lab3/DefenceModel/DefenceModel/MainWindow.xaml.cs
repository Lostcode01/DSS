using DefenceModel;
using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.ComponentModel;
using System.Windows;
using System.Windows.Controls;

namespace DefenceModel
{
    public partial class MainWindow : Window
    {
        // Данные
        private ObservableCollection<string> users;
        private ObservableCollection<string> objects;
        private ObservableCollection<ObjectData> objectDataList;
        private int[,] accessMatrix; // P[N, M+1]

        private string selectedUser;
        private string selectedObject;

        public MainWindow()
        {
            InitializeComponent();
            InitializeData();
            UpdateAccessMatrixGrid();
        }

        private void InitializeData()
        {
            // Инициализация тестовыми данными
            users = new ObservableCollection<string> { "User1", "User2", "Admin" };
            objects = new ObservableCollection<string> { "File1.txt", "File2.doc", "Data.db" };

            objectDataList = new ObservableCollection<ObjectData>
            {
                new ObjectData { Name = "File1.txt", Value = "Содержимое файла 1" },
                new ObjectData { Name = "File2.doc", Value = "Документ 2" },
                new ObjectData { Name = "Data.db", Value = "База данных" }
            };

            // Инициализация матрицы прав доступа [N, M+1]
            // P[I, 0] - админ права, P[I, J] - права к объекту J (0, 1, 2)
            accessMatrix = new int[3, 3 + 1]
            {
                { 1, 2, 2, 1 },  // Admin: админ права=1, к File1=2, File2=2, Data=1
                { 0, 1, 0, 0 },  // User1: админ права=0, к File1=1 (чтение)
                { 0, 0, 1, 1 }   // User2: админ права=0, к File2=1, Data=1
            };

            lstUsers.ItemsSource = users;
            lstObjects.ItemsSource = objects;
            dgAccessMatrix.ItemsSource = CreateMatrixView();
        }

        private ObservableCollection<MatrixRow> CreateMatrixView()
        {
            var result = new ObservableCollection<MatrixRow>();
            for (int i = 0; i < users.Count; i++)
            {
                var row = new MatrixRow
                {
                    UserName = users[i],
                    AdminRights = accessMatrix[i, 0].ToString(),
                    Index = i
                };

                for (int j = 0; j < objects.Count; j++)
                {
                    row.RightValues.Add(GetRightName(accessMatrix[i, j + 1]));
                }

                result.Add(row);
            }
            return result;
        }

        private string GetRightName(int right)
        {
            switch (right)
            {
                case 0: return "Нет прав";
                case 1: return "Чтение";
                case 2: return "Модификация";
                default: return "Неизвестно";
            }
        }

        private void UpdateAccessMatrixGrid()
        {
            dgAccessMatrix.Columns.Clear();
            dgAccessMatrix.Columns.Add(new DataGridTextColumn
            {
                Header = "Пользователь",
                Binding = new System.Windows.Data.Binding("UserName"),
                Width = 120
            });
            dgAccessMatrix.Columns.Add(new DataGridTextColumn
            {
                Header = "Адм. права",
                Binding = new System.Windows.Data.Binding("AdminRights"),
                Width = 80
            });

            for (int j = 0; j < objects.Count; j++)
            {
                dgAccessMatrix.Columns.Add(new DataGridTextColumn
                {
                    Header = objects[j],
                    Binding = new System.Windows.Data.Binding($"RightValues[{j}]"),
                    Width = 100
                });
            }

            dgAccessMatrix.ItemsSource = CreateMatrixView();
        }

        private void lstUsers_SelectionChanged(object sender, SelectionChangedEventArgs e)
        {
            if (lstUsers.SelectedItem != null)
            {
                selectedUser = lstUsers.SelectedItem.ToString();
                int userIndex = users.IndexOf(selectedUser);

                // Проверка административных прав
                btnEditMatrix.IsEnabled = (accessMatrix[userIndex, 0] == 1);

                UpdateObjectAccess();
            }
        }

        private void lstObjects_SelectionChanged(object sender, SelectionChangedEventArgs e)
        {
            if (lstObjects.SelectedItem != null)
            {
                selectedObject = lstObjects.SelectedItem.ToString();
                UpdateObjectAccess();
            }
        }

        private void UpdateObjectAccess()
        {
            if (string.IsNullOrEmpty(selectedUser) || string.IsNullOrEmpty(selectedObject))
                return;

            int userIndex = users.IndexOf(selectedUser);
            int objectIndex = objects.IndexOf(selectedObject);

            int userRights = accessMatrix[userIndex, objectIndex + 1];

            // Обновление информации о правах
            string rightsText = $"Права: {GetRightName(userRights)}";
            txtAccessInfo.Text = rightsText;

            // Поиск данных объекта
            var objData = objectDataList[objectIndex];

            // Применение прав доступа
            if (userRights == 0)
            {
                // Нет прав
                txtObjectValue.IsReadOnly = true;
                txtObjectValue.Text = "";
                txtAccessInfo.Text += "\nДоступ запрещен!";
            }
            else if (userRights == 1)
            {
                // Только чтение
                txtObjectValue.IsReadOnly = true;
                txtObjectValue.Text = objData.Value;
                txtAccessInfo.Text += "\nРежим: только чтение";
            }
            else if (userRights == 2)
            {
                // Чтение и модификация
                txtObjectValue.IsReadOnly = false;
                txtObjectValue.Text = objData.Value;
                txtAccessInfo.Text += "\nРежим: чтение и запись";
            }
        }

        private void txtObjectValue_TextChanged(object sender, TextChangedEventArgs e)
        {
            // Сохранение изменений в объекте
            if (!string.IsNullOrEmpty(selectedObject) && !txtObjectValue.IsReadOnly)
            {
                int objectIndex = objects.IndexOf(selectedObject);
                if (objectIndex >= 0)
                {
                    objectDataList[objectIndex].Value = txtObjectValue.Text;
                }
            }
        }

        private void btnEditMatrix_Click(object sender, RoutedEventArgs e)
        {
            var editWindow = new EditMatrixWindow(
                users,
                objects,
                objectDataList,
                accessMatrix
            );

            if (editWindow.ShowDialog() == true)
            {
                // Обновление данных после редактирования
                UpdateAccessMatrixGrid();
                lstUsers.Items.Refresh();
                lstObjects.Items.Refresh();
            }
        }
    }

    // Вспомогательные классы
    public class ObjectData : INotifyPropertyChanged
    {
        public string Name { get; set; }

        private string value;
        public string Value
        {
            get => value;
            set
            {
                this.value = value;
                OnPropertyChanged(nameof(Value));
            }
        }

        public event PropertyChangedEventHandler PropertyChanged;
        protected void OnPropertyChanged(string name) =>
            PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(name));
    }

    public class MatrixRow
    {
        public string UserName { get; set; }
        public string AdminRights { get; set; }
        public ObservableCollection<string> RightValues { get; set; } = new ObservableCollection<string>();
        public int Index { get; set; }
    }
}