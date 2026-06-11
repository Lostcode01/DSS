using DefenceModel;
using System;
using System.Collections.ObjectModel;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Data;

namespace DefenceModel
{
    public partial class EditMatrixWindow : Window
    {
        private ObservableCollection<string> users;
        private ObservableCollection<string> objects;
        private ObservableCollection<ObjectData> objectDataList;
        private int[,] accessMatrix;

        private bool changesMade = false;

        public EditMatrixWindow(
            ObservableCollection<string> users,
            ObservableCollection<string> objects,
            ObservableCollection<ObjectData> objectDataList,
            int[,] accessMatrix)
        {
            InitializeComponent();

            this.users = users;
            this.objects = objects;
            this.objectDataList = objectDataList;
            this.accessMatrix = accessMatrix;

            InitializeWindows();
        }

        private void InitializeWindows()
        {
            // Инициализация списков
            lstEditUsers.ItemsSource = users;
            lstEditObjects.ItemsSource = objects;

            // Инициализация таблицы прав
            InitializeRightsGrid();
        }

        private void InitializeRightsGrid()
        {
            dgEditRights.Columns.Clear();
            dgEditRights.Columns.Add(new DataGridTextColumn
            {
                Header = "Пользователь",
                Binding = new System.Windows.Data.Binding("UserName"),
                IsReadOnly = true,
                Width = 120
            });

            for (int j = 0; j < objects.Count; j++)
            {
                var comboBoxColumn = new DataGridComboBoxColumn
                {
                    Header = objects[j],
                    Width = 120
                };

                comboBoxColumn.ItemsSource = new string[] { "0 - Нет прав", "1 - Чтение", "2 - Модификация" };
                comboBoxColumn.TextBinding = new Binding($"Rights[{j}]");

         

                dgEditRights.Columns.Add(comboBoxColumn);
            }

            dgEditRights.ItemsSource = CreateRightsData();
        }

        private ObservableCollection<RightsRow> CreateRightsData()
        {
            var result = new ObservableCollection<RightsRow>();

            for (int i = 0; i < users.Count; i++)
            {
                var row = new RightsRow
                {
                    UserName = users[i],
                    Index = i
                };

                for (int j = 0; j < objects.Count; j++)
                {
                    int right = accessMatrix[i, j + 1];
                    row.Rights.Add(right == 0 ? "0 - Нет прав" :
                                  right == 1 ? "1 - Чтение" : "2 - Модификация");
                }

                result.Add(row);
            }

            return result;
        }

        // Обработчики для пользователей
        private void lstEditUsers_SelectionChanged(object sender, SelectionChangedEventArgs e)
        {
            if (lstEditUsers.SelectedItem != null)
            {
                string userName = lstEditUsers.SelectedItem.ToString();
                int index = users.IndexOf(userName);

                txtUserName.Text = userName;
                cmbAdminRights.SelectedIndex = accessMatrix[index, 0];
            }
        }

        private void btnAddUser_Click(object sender, RoutedEventArgs e)
        {
            if (string.IsNullOrWhiteSpace(txtUserName.Text))
            {
                MessageBox.Show("Введите имя пользователя!", "Ошибка",
                    MessageBoxButton.OK, MessageBoxImage.Warning);
                return;
            }

            if (users.Contains(txtUserName.Text))
            {
                MessageBox.Show("Пользователь уже существует!", "Ошибка",
                    MessageBoxButton.OK, MessageBoxImage.Warning);
                return;
            }

            users.Add(txtUserName.Text);

            // Расширение матрицы
            int[,] newMatrix = new int[users.Count, objects.Count + 1];
            for (int i = 0; i < accessMatrix.GetLength(0); i++)
                for (int j = 0; j < accessMatrix.GetLength(1); j++)
                    newMatrix[i, j] = accessMatrix[i, j];

            accessMatrix = newMatrix;
            accessMatrix[users.Count - 1, 0] = cmbAdminRights.SelectedIndex;

            changesMade = true;
            InitializeRightsGrid();
            MessageBox.Show("Пользователь добавлен!", "Успех",
                MessageBoxButton.OK, MessageBoxImage.Information);
        }

        private void btnUpdateUser_Click(object sender, RoutedEventArgs e)
        {
            if (lstEditUsers.SelectedItem == null)
            {
                MessageBox.Show("Выберите пользователя для обновления!", "Ошибка",
                    MessageBoxButton.OK, MessageBoxImage.Warning);
                return;
            }

            int index = users.IndexOf(lstEditUsers.SelectedItem.ToString());
            accessMatrix[index, 0] = cmbAdminRights.SelectedIndex;

            changesMade = true;
            MessageBox.Show("Права пользователя обновлены!", "Успех",
                MessageBoxButton.OK, MessageBoxImage.Information);
        }

        private void btnDeleteUser_Click(object sender, RoutedEventArgs e)
        {
            if (lstEditUsers.SelectedItem == null)
            {
                MessageBox.Show("Выберите пользователя для удаления!", "Ошибка",
                    MessageBoxButton.OK, MessageBoxImage.Warning);
                return;
            }

            string userName = lstEditUsers.SelectedItem.ToString();
            int index = users.IndexOf(userName);

            var result = MessageBox.Show($"Удалить пользователя '{userName}'?",
                "Подтверждение", MessageBoxButton.YesNo, MessageBoxImage.Question);

            if (result == MessageBoxResult.Yes)
            {
                users.RemoveAt(index);

                // Сжатие матрицы
                int[,] newMatrix = new int[users.Count, objects.Count + 1];
                int newIdx = 0;
                for (int i = 0; i < accessMatrix.GetLength(0); i++)
                {
                    if (i != index)
                    {
                        for (int j = 0; j < accessMatrix.GetLength(1); j++)
                            newMatrix[newIdx, j] = accessMatrix[i, j];
                        newIdx++;
                    }
                }

                accessMatrix = newMatrix;
                changesMade = true;
                InitializeRightsGrid();
                MessageBox.Show("Пользователь удален!", "Успех",
                    MessageBoxButton.OK, MessageBoxImage.Information);
            }
        }

        // Обработчики для объектов
        private void lstEditObjects_SelectionChanged(object sender, SelectionChangedEventArgs e)
        {
            if (lstEditObjects.SelectedItem != null)
            {
                string objName = lstEditObjects.SelectedItem.ToString();
                int index = objects.IndexOf(objName);

                txtObjectName.Text = objName;
                txtObjectContent.Text = objectDataList[index].Value;
            }
        }

        private void btnAddObject_Click(object sender, RoutedEventArgs e)
        {
            if (string.IsNullOrWhiteSpace(txtObjectName.Text))
            {
                MessageBox.Show("Введите имя объекта!", "Ошибка",
                    MessageBoxButton.OK, MessageBoxImage.Warning);
                return;
            }

            if (objects.Contains(txtObjectName.Text))
            {
                MessageBox.Show("Объект уже существует!", "Ошибка",
                    MessageBoxButton.OK, MessageBoxImage.Warning);
                return;
            }

            objects.Add(txtObjectName.Text);
            objectDataList.Add(new ObjectData
            {
                Name = txtObjectName.Text,
                Value = txtObjectContent.Text
            });

            // Расширение матрицы
            int[,] newMatrix = new int[users.Count, objects.Count + 1];
            for (int i = 0; i < accessMatrix.GetLength(0); i++)
            {
                for (int j = 0; j < accessMatrix.GetLength(1) - 1; j++)
                    newMatrix[i, j] = accessMatrix[i, j];
                newMatrix[i, objects.Count] = 0; // Новые объекты без прав
            }

            accessMatrix = newMatrix;
            changesMade = true;
            InitializeRightsGrid();
            MessageBox.Show("Объект добавлен!", "Успех",
                MessageBoxButton.OK, MessageBoxImage.Information);
        }

        private void btnUpdateObject_Click(object sender, RoutedEventArgs e)
        {
            if (lstEditObjects.SelectedItem == null)
            {
                MessageBox.Show("Выберите объект для обновления!", "Ошибка",
                    MessageBoxButton.OK, MessageBoxImage.Warning);
                return;
            }

            int index = objects.IndexOf(lstEditObjects.SelectedItem.ToString());
            objectDataList[index].Value = txtObjectContent.Text;

            changesMade = true;
            MessageBox.Show("Объект обновлен!", "Успех",
                MessageBoxButton.OK, MessageBoxImage.Information);
        }

        private void btnDeleteObject_Click(object sender, RoutedEventArgs e)
        {
            if (lstEditObjects.SelectedItem == null)
            {
                MessageBox.Show("Выберите объект для удаления!", "Ошибка",
                    MessageBoxButton.OK, MessageBoxImage.Warning);
                return;
            }

            string objName = lstEditObjects.SelectedItem.ToString();
            int index = objects.IndexOf(objName);

            var result = MessageBox.Show($"Удалить объект '{objName}'?",
                "Подтверждение", MessageBoxButton.YesNo, MessageBoxImage.Question);

            if (result == MessageBoxResult.Yes)
            {
                objects.RemoveAt(index);
                objectDataList.RemoveAt(index);

                // Сжатие матрицы
                int[,] newMatrix = new int[users.Count, objects.Count + 1];
                for (int i = 0; i < accessMatrix.GetLength(0); i++)
                {
                    int newIdx = 0;
                    for (int j = 0; j < accessMatrix.GetLength(1); j++)
                    {
                        if (j - 1 != index)
                        {
                            newMatrix[i, newIdx] = accessMatrix[i, j];
                            newIdx++;
                        }
                    }
                }

                accessMatrix = newMatrix;
                changesMade = true;
                InitializeRightsGrid();
                MessageBox.Show("Объект удален!", "Успех",
                    MessageBoxButton.OK, MessageBoxImage.Information);
            }
        }

        private void btnSaveRights_Click(object sender, RoutedEventArgs e)
        {
            var data = dgEditRights.ItemsSource as ObservableCollection<RightsRow>;
            if (data == null) return;

            foreach (var row in data)
            {
                for (int j = 0; j < objects.Count; j++)
                {
                    string rightText = row.Rights[j];
                    int right = rightText.StartsWith("0") ? 0 :
                               rightText.StartsWith("1") ? 1 : 2;

                    accessMatrix[row.Index, j + 1] = right;
                }
            }

            changesMade = true;
            MessageBox.Show("Права доступа сохранены!", "Успех",
                MessageBoxButton.OK, MessageBoxImage.Information);
        }

        private void btnOK_Click(object sender, RoutedEventArgs e)
        {
            DialogResult = true;
            Close();
        }

        private void btnCancel_Click(object sender, RoutedEventArgs e)
        {
            DialogResult = false;
            Close();
        }
    }

    public class RightsRow
    {
        public string UserName { get; set; }
        public ObservableCollection<string> Rights { get; set; } = new ObservableCollection<string>();
        public int Index { get; set; }
    }
}