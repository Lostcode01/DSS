#include <graphics.h>
#include <conio.h>

int main() {
    initgraph(640, 480);

    setbkcolor(WHITE);
    cleardevice();

    setcolor(RED);
    setfillcolor(YELLOW);
    fillcircle(320, 240, 100);

    settextcolor(BLACK);
    settextstyle(30, 0, "Arial");
    outtextxy(250, 390, "Hello EasyX!");

    _getch();       // Wait for keypress before closing
    closegraph();
    return 0;
}
