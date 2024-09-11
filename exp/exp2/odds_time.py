import easyocr
import mss
import cv2
import numpy as np

def capture_screenshot(left: int, top: int, width: int, height: int):
    """指定した範囲のスクリーンショットを取得し、OCRを実行、テキスト情報を返す

    Args:
        left (int): スクリーンショットの左上のx座標
        top (int): スクリーンショットの左上のy座標
        width (int): スクリーンショットの幅
        height (int): スクリーンショットの高さ

    Returns:
        str: スクリーンショットのテキスト情報
    """

    monitor = {"top": top, "left": left, "width": width, "height": height}

    with mss.mss() as sct:
        screentshot = sct.grab(monitor)
    
    img = np.array(screentshot)

    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    reader = easyocr.Reader(['ja'])

    result = reader.readtext(img_rgb)

    return result

def get_mouse_drug_posu():
    """マウスのドラッグ開始位置と終了位置を取得する
        マウスの左クリックを押した位置をドラッグ開始位置、
        離した位置をドラッグ終了位置とする。
        マウスの左クリックが開始されるまで待機する。

    Returns:
        tuple: マウスのドラッグ開始位置と終了位置
    """

    start_pos = None
    end_pos = None

    def on_mouse(event, x, y, flags, param):
        nonlocal start_pos
        nonlocal end_pos

        if event == cv2.EVENT_LBUTTONDOWN:
            start_pos = (x, y)
        elif event == cv2.EVENT_LBUTTONUP:
            end_pos = (x, y)

    cv2.namedWindow("get_mouse_drug_posu")
    cv2.setMouseCallback("get_mouse_drug_posu", on_mouse)

    while True:
        cv2.waitKey(1)

        if start_pos is not None and end_pos is not None:
            break

    return start_pos, end_pos

def mouse_click():
    """指定した座標群をクリックする。
        座標の指定にはdボタンを押して、クリックしたい位置を指定する。
        座標の指定が終了したら、qボタンを押して終了する。
        qボタンを押すまで、座標の指定を続ける。

    Returns:
        None
    """

    pos = []

    def on_mouse(event, x, y, flags, param):
        nonlocal pos

        if event == cv2.EVENT_LBUTTONDOWN:
            pos.append((x, y))

    cv2.namedWindow("mouse_click")
    cv2.setMouseCallback("mouse_click", on_mouse)

    while True:
        cv2.waitKey(1)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    return pos

def automate():
    """自動化処理を行う。
        1. マウスのドラッグ開始位置と終了位置を取得する。
        2. クリックしたい位置を取得する。
        3. ドラッグ開始位置と終了位置をそれぞれleft, top, width, heightとして、
            スクリーンショットを取得する。
        4. OCRを実行し、テキスト情報を取得する。
        5. テキスト情報を基に行数を取得する。
        6. クリックしたい位置に対して、行数分クリックを行う。

    Returns:
        None
    """

    # マウスのドラッグ開始位置と終了位置を取得
    start_pos, end_pos = get_mouse_drug_posu()

    # クリックしたい位置を取得
    click_pos = mouse_click()

    # ドラッグ開始位置と終了位置を取得
    left = min(start_pos[0], end_pos[0])
    top = min(start_pos[1], end_pos[1])

    width = abs(start_pos[0] - end_pos[0])
    height = abs(start_pos[1] - end_pos[1])

    # スクリーンショットを取得後、OCRを実行
    texts = capture_screenshot(left, top, width, height)

    # 指定単語を数を取得 ⇒ 行数とする
    search_word = "R"
    line = 0
    for text in texts:
        if search_word in text[1]:
            line += 1

    # クリックしたい位置に対して、行数分クリックを行う
    for _ in range(line):
        for pos in click_pos:
            x, y = pos
            cv2.mouseMove(x, y)
            cv2.click()

if __name__ == "__main__":
    automate()
