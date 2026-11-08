# deque（スタック・キュー）

Source: https://www.notion.so/3e29b4299e6181d8b71de2acb651e3eb

---

`deque` は両端から追加・取り出しができる。
```python
from collections import deque
```
## スタック：後に入れたものから取り出す
```python
s = deque()
s.append(1)
s.append(2)
x = s.pop()  # 2
```
## キュー：先に入れたものから取り出す
```python
q = deque()
q.append(1)
q.append(2)
x = q.popleft()  # 1
```
## その他の基本操作
```python
q.appendleft(0)  # 左端に追加
q[0]            # 左端を見る
q[-1]           # 右端を見る
len(q)          # 要素数

if q:           # 空でなければ取り出す
    x = q.popleft()
```
両端の追加・取り出しはO(1)。空の状態で `pop()`・`popleft()` を呼ぶとエラー。
<details>
<summary>旧ページ（統合済み）</summary>
	<page url="https://app.notion.com/p/3e29b4299e6181ce976cf243b8ff434c">8.2 キュー</page>
</details>
