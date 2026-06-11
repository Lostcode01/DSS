using System;
using System.Collections.Generic;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Media;
using System.Windows.Shapes;

namespace lab5
{
    public partial class MainWindow : Window
    {
        // Константы таблицы
        private const int ROWS = 5;
        private const int COLS = 8;
        private const int BLOCK_SIZE = ROWS * COLS; // 40 символов

        // Текущий маршрут
        private enum RouteType { Snake, Spiral, Columns, Diagonal }
        private RouteType currentRoute = RouteType.Snake;

        // Массивы для визуализации
        private TextBlock[,] cells;
        private int[] readOrder; // Порядок чтения ячеек

        public MainWindow()
        {
            InitializeComponent();
            InitializeTable();
            cmbRoute.SelectionChanged += CmbRoute_SelectionChanged;
        }

        // Инициализация таблицы 5×8
        private void InitializeTable()
        {
            gridTable.Children.Clear();
            cells = new TextBlock[ROWS, COLS];

            // Создаем сетку
            for (int row = 0; row < ROWS; row++)
            {
                for (int col = 0; col < COLS; col++)
                {
                    var cell = new TextBlock
                    {
                        Width = 50,
                        Height = 50,
                        HorizontalAlignment = HorizontalAlignment.Center,
                        VerticalAlignment = VerticalAlignment.Center,
                        FontSize = 16,
                        FontWeight = FontWeights.Bold,
                        Margin = new Thickness(1),
                        TextAlignment = TextAlignment.Center
                    };

                    Grid.SetRow(cell, row);
                    Grid.SetColumn(cell, col);

                    cells[row, col] = cell;
                    gridTable.Children.Add(cell);
                }
            }

            // Настройка сетки
            for (int i = 0; i < ROWS; i++)
                gridTable.RowDefinitions.Add(new RowDefinition { Height = new GridLength(50) });
            for (int i = 0; i < COLS; i++)
                gridTable.ColumnDefinitions.Add(new ColumnDefinition { Width = new GridLength(50) });

            // Генерация порядка чтения для текущего маршрута
            GenerateReadOrder();
        }

        // Генерация порядка чтения в зависимости от маршрута
        private void GenerateReadOrder()
        {
            readOrder = new int[BLOCK_SIZE];

            switch (currentRoute)
            {
                case RouteType.Snake:
                    GenerateSnakeOrder();
                    break;
                case RouteType.Spiral:
                    GenerateSpiralOrder();
                    break;
                case RouteType.Columns:
                    GenerateColumnOrder();
                    break;
                case RouteType.Diagonal:
                    GenerateDiagonalOrder();
                    break;
            }
        }

        // Маршрут "Змейка" (горизонтальная)
        private void GenerateSnakeOrder()
        {
            int index = 0;
            for (int row = 0; row < ROWS; row++)
            {
                if (row % 2 == 0)
                {
                    // Четная строка: слева направо
                    for (int col = 0; col < COLS; col++)
                        readOrder[index++] = row * COLS + col;
                }
                else
                {
                    // Нечетная строка: справа налево
                    for (int col = COLS - 1; col >= 0; col--)
                        readOrder[index++] = row * COLS + col;
                }
            }
        }

        // Маршрут "Спираль"
        private void GenerateSpiralOrder()
        {
            int index = 0;
            int top = 0, bottom = ROWS - 1, left = 0, right = COLS - 1;

            while (top <= bottom && left <= right)
            {
                // Вправо по верхней строке
                for (int col = left; col <= right; col++)
                    readOrder[index++] = top * COLS + col;
                top++;

                // Вниз по правому столбцу
                for (int row = top; row <= bottom; row++)
                    readOrder[index++] = row * COLS + right;
                right--;

                // Влево по нижней строке
                if (top <= bottom)
                {
                    for (int col = right; col >= left; col--)
                        readOrder[index++] = bottom * COLS + col;
                    bottom--;
                }

                // Вверх по левому столбцу
                if (left <= right)
                {
                    for (int row = bottom; row >= top; row--)
                        readOrder[index++] = row * COLS + left;
                    left++;
                }
            }
        }

        // Маршрут "По столбцам"
        private void GenerateColumnOrder()
        {
            int index = 0;
            for (int col = 0; col < COLS; col++)
            {
                for (int row = 0; row < ROWS; row++)
                    readOrder[index++] = row * COLS + col;
            }
        }

        // Маршрут "Диагональный"
        private void GenerateDiagonalOrder()
        {
            int index = 0;
            bool[] used = new bool[BLOCK_SIZE];

            for (int sum = 0; sum < ROWS + COLS - 1; sum++)
            {
                for (int row = 0; row < ROWS; row++)
                {
                    int col = sum - row;
                    if (col >= 0 && col < COLS && !used[row * COLS + col])
                    {
                        readOrder[index++] = row * COLS + col;
                        used[row * COLS + col] = true;
                    }
                }
            }
        }

        private double Factorial(int n)
        {
            double result = 1;
            for (int i = 2; i <= n; i++)
                result *= i;
            return result;
        }

        // Обработка выбора маршрута
        private void CmbRoute_SelectionChanged(object sender, SelectionChangedEventArgs e)
        {
            if (cmbRoute.SelectedItem is ComboBoxItem item)
            {
                if (item.Content.ToString().Contains("Змейка"))
                    currentRoute = RouteType.Snake;
                else if (item.Content.ToString().Contains("Спираль"))
                    currentRoute = RouteType.Spiral;
                else if (item.Content.ToString().Contains("Диагональный"))
                    currentRoute = RouteType.Diagonal;

                GenerateReadOrder();
                VisualizeRoute();
            }
        }

        // Визуализация маршрута на таблице
        private void VisualizeRoute()
        {
            // Очистка цветов
            for (int row = 0; row < ROWS; row++)
            {
                for (int col = 0; col < COLS; col++)
                {
                    cells[row, col].Background = Brushes.White;
                    cells[row, col].Text = "";
                    cells[row, col].Foreground = Brushes.Black;
                }
            }

            // Раскраска ячеек по порядку чтения
            for (int i = 0; i < BLOCK_SIZE; i++)
            {
                int pos = readOrder[i];
                int row = pos / COLS;
                int col = pos % COLS;

                // Градиент цвета от зеленого к красному
                byte intensity = (byte)(255 - (i * 255 / BLOCK_SIZE));
                cells[row, col].Background = new SolidColorBrush(
                    Color.FromRgb(intensity, (byte)(255 - intensity), 100));

                cells[row, col].Text = (i + 1).ToString();
                cells[row, col].Foreground = Brushes.White;
            }
        }

        // Шифрование
        private void Encrypt(string input)
        {
            // Подготовка текста: удаление пробелов, приведение к верхнему регистру
            string cleanText = input.ToUpper().Replace(" ", "");

            // Дополнение до кратного BLOCK_SIZE
            int paddedLength = ((cleanText.Length + BLOCK_SIZE - 1) / BLOCK_SIZE) * BLOCK_SIZE;
            cleanText = cleanText.PadRight(paddedLength, ' ');

            string result = "";

            // Обработка каждого блока
            for (int block = 0; block < paddedLength / BLOCK_SIZE; block++)
            {
                char[] blockData = new char[BLOCK_SIZE];

                // Запись в таблицу (построчно)
                for (int i = 0; i < BLOCK_SIZE; i++)
                {
                    blockData[i] = cleanText[block * BLOCK_SIZE + i];
                }

                // Чтение по маршруту
                for (int i = 0; i < BLOCK_SIZE; i++)
                {
                    result += blockData[readOrder[i]];
                }
            }

            txtOutput.Text = result.Trim();
            UpdateStats(cleanText.Length, paddedLength / BLOCK_SIZE);
            //VisualizeEncryption(cleanText);
        }

        // Расшифрование
        private void Decrypt(string input)
        {
            string cleanText = input.ToUpper().Replace(" ", "");

            // Дополнение до кратного BLOCK_SIZE
            int paddedLength = ((cleanText.Length + BLOCK_SIZE - 1) / BLOCK_SIZE) * BLOCK_SIZE;
            cleanText = cleanText.PadRight(paddedLength, ' ');

            string result = "";

            // Обработка каждого блока
            for (int block = 0; block < paddedLength / BLOCK_SIZE; block++)
            {
                char[] blockData = new char[BLOCK_SIZE];
                char[] encryptedBlock = new char[BLOCK_SIZE];

                // Копирование зашифрованного блока
                for (int i = 0; i < BLOCK_SIZE; i++)
                {
                    encryptedBlock[i] = cleanText[block * BLOCK_SIZE + i];
                }

                // Обратное преобразование: запись по маршруту, чтение постаточно
                for (int i = 0; i < BLOCK_SIZE; i++)
                {
                    blockData[i] = encryptedBlock[i];
                }

                // Чтение постаточно
                for (int i = 0; i < BLOCK_SIZE; i++)
                {
                    result += blockData[i];
                }
            }

            txtOutput.Text = result.Trim();
            UpdateStats(cleanText.Length, paddedLength / BLOCK_SIZE);
            VisualizeDecryption(cleanText);
        }


        // Визуализация процесса шифрования
        private void VisualizeEncryption(string text)
        {
            // Очистка
            for (int row = 0; row < ROWS; row++)
            {
                for (int col = 0; col < COLS; col++)
                {
                    cells[row, col].Background = Brushes.White;
                    cells[row, col].Text = "";
                    cells[row, col].Foreground = Brushes.Black;
                }
            }

            // Запись первого блока в таблицу
            for (int i = 0; i < Math.Min(BLOCK_SIZE, text.Length); i++)
            {
                int row = i / COLS;
                int col = i % COLS;
                cells[row, col].Text = text[i].ToString();
                cells[row, col].Background = Brushes.LightBlue;
            }
        }

        // Визуализация процесса расшифрования
        private void VisualizeDecryption(string text)
        {
            // Очистка
            for (int row = 0; row < ROWS; row++)
            {
                for (int col = 0; col < COLS; col++)
                {
                    cells[row, col].Background = Brushes.White;
                    cells[row, col].Text = "";
                    cells[row, col].Foreground = Brushes.Black;
                }
            }

            // Запись зашифрованного текста по маршруту
            for (int i = 0; i < Math.Min(BLOCK_SIZE, text.Length); i++)
            {
                int pos = readOrder[i];
                int row = pos / COLS;
                int col = pos % COLS;
                cells[row, col].Text = text[i].ToString();
                cells[row, col].Background = Brushes.LightGreen;
            }
        }

        // Обновление статистики
        private void UpdateStats(int charCount, int blockCount)
        {
            txtStats.Text = $"Символов: {charCount}";
            txtBlocks.Text = $"Блоков: {blockCount} (по {BLOCK_SIZE} символов)";
        }

        // Обработчики кнопок
        private void btnEncrypt_Click(object sender, RoutedEventArgs e)
        {
            if (string.IsNullOrWhiteSpace(txtInput.Text))
            {
                MessageBox.Show("Введите текст для шифрования!", "Ошибка",
                    MessageBoxButton.OK, MessageBoxImage.Warning);
                return;
            }

            Encrypt(txtInput.Text);
        }

        private void btnDecrypt_Click(object sender, RoutedEventArgs e)
        {
            if (string.IsNullOrWhiteSpace(txtInput.Text))
            {
                MessageBox.Show("Введите текст для расшифрования!", "Ошибка",
                    MessageBoxButton.OK, MessageBoxImage.Warning);
                return;
            }

            Decrypt(txtInput.Text);
        }

        private void btnClear_Click(object sender, RoutedEventArgs e)
        {
            txtInput.Text = "";
            txtOutput.Text = "";
            txtStats.Text = "Символов: 0";
            txtBlocks.Text = "Блоков: 0";

            // Очистка таблицы
            for (int row = 0; row < ROWS; row++)
            {
                for (int col = 0; col < COLS; col++)
                {
                    cells[row, col].Text = "";
                    cells[row, col].Background = Brushes.White;
                    cells[row, col].Foreground = Brushes.Black;
                }
            }
        }
    }
}