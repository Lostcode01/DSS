using lab4;
using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.ComponentModel;
using System.Windows;
using System.Windows.Controls;

namespace lab4
{
    public partial class MainWindow : Window
    {
        // Данные
        private ObservableCollection<string> users;
        private ObservableCollection<string> objects;
        private ObservableCollection<ObjectData> objectDataList;
        private int[,] accessMatrix; // P[N, M+1]
        private int[] privilegesUser; // Уровни привилегий пользователей
        private int[] privilegesObject; // Уровни привилегий объектов

        private string selectedUser;
        private string selectedObject;
        private string bufferContent = "";
        private int privilegesBuffer = -1;

        public MainWindow()
        {
            InitializeComponent();
            InitializeData();
            UpdateAccessMatrixGrid();
        }

        private void InitializeData()
        {
            // Инициализация тестовыми данными
            users = new ObservableCollection<string> { "User1", "User2", "Admin", "Guest" };
            objects = new ObservableCollection<string> { "File1.txt", "File2.doc", "Secret.db", "TopSecret.dat" };

            objectDataList = new ObservableCollection<ObjectData>
            {
                new ObjectData { Name = "File1.txt", Value = "Открытая информация" },
                new ObjectData { Name = "File2.doc", Value = "Конфиденциальный документ" },
                new ObjectData { Name = "Secret.db", Value = "Секретная база данных" },
                new ObjectData { Name = "TopSecret.dat", Value = "Совершенно секретные данные" }
            };

            // Уровни привилегий пользователей (0-3)
            privilegesUser = new int[] { 1, 2, 3, 0 }; // User1=1, User2=2, Admin=3, Guest=0

            // Уровни привилегий объектов (0-3)
            privilegesObject = new int[] { 0, 1, 2, 3 }; // File1=0, File2=1, Secret=2, TopSecret=3

            // Инициализация матрицы прав доступа [N, M+1]
            accessMatrix = new int[4, 5]
            {
                { 1, 1, 1, 0, 0 },  // User1 (level 1): админ=1, к File1=1, File2=1, Secret=0, TopSecret=0
                { 0, 1, 2, 1, 0 },  // User2 (level 2): админ=0, к File1=1, File2=2, Secret=1, TopSecret=0
                { 1, 2, 2, 2, 1 },  // Admin (level 3): админ=1, ко всем=2 кроме TopSecret=1
                { 0, 1, 0, 0, 0 }   // Guest (level 0): админ=0, только File1=1
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
                    UserLevel = privilegesUser[i].ToString(),
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

        private string GetPrivilegeName(int level)
        {
            switch (level)
            {
                case 0: return "Несекретно";
                case 1: return "Конфиденциально";
                case 2: return "Секретно";
                case 3: return "Совершенно секретно";
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
                Header = "Уровень",
                Binding = new System.Windows.Data.Binding("UserLevel"),
                Width = 60
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
                    Header = $"{objects[j]}\n(ур.{privilegesObject[j]})",
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

                // Отображение привилегии пользователя
                txtUserPrivilege.Text = $"Уровень: {privilegesUser[userIndex]} - {GetPrivilegeName(privilegesUser[userIndex])}";

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
            int userPriv = privilegesUser[userIndex];
            int objPriv = privilegesObject[objectIndex];

            // Обновление информации о привилегии объекта
            txtObjectPrivilege.Text = $"Уровень: {objPriv} - {GetPrivilegeName(objPriv)}";

            // Проверка правил Белла-ЛаПадула
            bool bellLaPadulaCheck = (userPriv >= objPriv); // No Read Up

            string accessText = $"Права: {GetRightName(userRights)}\n";
            accessText += $"BLP проверка: {(bellLaPadulaCheck ? "Разрешено" : "Запрещено (No Read Up)")}";

            // Применение прав доступа с учетом BLP
            if (userRights == 0 || !bellLaPadulaCheck)
            {
                // Нет прав или нарушение BLP
                txtObjectValue.IsReadOnly = true;
                txtObjectValue.Text = "";
                accessText += "\nДоступ запрещен!";
                txtAccessInfo.Text = accessText;
            }
            else if (userRights == 1)
            {
                // Только чтение
                txtObjectValue.IsReadOnly = true;
                txtObjectValue.Text = objectDataList[objectIndex].Value;
                accessText += "\nРежим: только чтение";
                txtAccessInfo.Text = accessText;
            }
            else if (userRights == 2)
            {
                // Чтение и модификация (с проверкой No Write Down)
                txtObjectValue.IsReadOnly = false;
                txtObjectValue.Text = objectDataList[objectIndex].Value;
                accessText += "\nРежим: чтение и запись";
                txtAccessInfo.Text = accessText;
            }

            // Обновление кнопок буфера
            UpdateBufferButtons(userIndex, objectIndex);
        }

        private void UpdateBufferButtons(int userIndex, int objectIndex)
        {
            int userPriv = privilegesUser[userIndex];
            int objPriv = privilegesObject[objectIndex];

            // Кнопка 6: Копировать ИЗ объекта в буфер
            // Доступна если PrivilegesUser[I] > PrivilegesObject[J]
            btnCopyToBuffer.IsEnabled = (userPriv > objPriv);

            // Кнопка 5: Копировать ИЗ буфера в объект
            // Доступна если PrivilegesBuffer < PrivilegesObject[J]
            btnCopyFromBuffer.IsEnabled = (privilegesBuffer >= 0 && privilegesBuffer < objPriv);
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

        private void btnCopyToBuffer_Click(object sender, RoutedEventArgs e)
        {
            if (string.IsNullOrEmpty(selectedObject))
                return;

            int userIndex = users.IndexOf(selectedUser);
            int objectIndex = objects.IndexOf(selectedObject);

            // Копирование из объекта в буфер
            bufferContent = objectDataList[objectIndex].Value;
            privilegesBuffer = privilegesObject[objectIndex];

            txtBuffer.Text = bufferContent;
            txtBufferPrivilege.Text = $"Привилегия буфера: {privilegesBuffer} - {GetPrivilegeName(privilegesBuffer)}";

            MessageBox.Show($"Данные скопированы в буфер (уровень {privilegesBuffer})", "Буфер",
                MessageBoxButton.OK, MessageBoxImage.Information);

            UpdateObjectAccess();
        }

        private void btnCopyFromBuffer_Click(object sender, RoutedEventArgs e)
        {
            if (string.IsNullOrEmpty(selectedObject) || string.IsNullOrEmpty(bufferContent))
                return;

            int objectIndex = objects.IndexOf(selectedObject);
            int objPriv = privilegesObject[objectIndex];

            // Проверка правила No Write Down
            if (privilegesBuffer >= objPriv)
            {
                MessageBox.Show("Нарушение правила *-защиты (No Write Down)!\n" +
                               "Нельзя записывать данные с более высоким уровнем в объект с более низким уровнем.",
                               "Ошибка доступа", MessageBoxButton.OK, MessageBoxImage.Warning);
                return;
            }

            // Копирование из буфера в объект
            objectDataList[objectIndex].Value = bufferContent;
            txtObjectValue.Text = bufferContent;

            MessageBox.Show("Данные скопированы из буфера", "Успех",
                MessageBoxButton.OK, MessageBoxImage.Information);
        }

        private void btnEditMatrix_Click(object sender, RoutedEventArgs e)
        {
            var editWindow = new EditMatrixWindow(
                users,
                objects,
                objectDataList,
                accessMatrix,
                privilegesUser,
                privilegesObject
            );

            if (editWindow.ShowDialog() == true)
            {
                // Обновление данных после редактирования
                UpdateAccessMatrixGrid();
                lstUsers.Items.Refresh();
                lstObjects.Items.Refresh();
                UpdateObjectAccess();
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
        public string UserLevel { get; set; }
        public string AdminRights { get; set; }
        public ObservableCollection<string> RightValues { get; set; } = new ObservableCollection<string>();
        public int Index { get; set; }
    }
}