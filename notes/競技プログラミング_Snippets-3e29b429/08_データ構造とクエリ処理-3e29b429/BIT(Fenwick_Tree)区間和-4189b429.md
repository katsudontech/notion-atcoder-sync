# BIT（Fenwick Tree）区間和

Source: https://www.notion.so/4189b4299e6181c88d99e0bfae9df391

---

## 基本操作 {toggle="true"}
	配列の「一点加算」と「区間和」を高速に処理する。
	```python
#from atcoder.fenwicktree import FenwickTree
# importはもうしてあるはず

bit = FenwickTree(N)       # 長さN、全要素0　初期登録するんだったら、for文回さんといかん
bit.add(p, x)             # 添字pにxを加算（負の値も可）
total = bit.sum(l, r)     # [l, r) の合計
value = bit.sum(p, p + 1) # 添字pの現在値
	```
## 使い方 {toggle="true"}
	```python
A = [2, 5, 3]
bit = FenwickTree(len(A))
for i, a in enumerate(A):
    bit.add(i, a)

print(bit.sum(0, 2))  # 2 + 5 = 7
bit.add(1, 4)        # [2, 9, 3] になる
print(bit.sum(0, 3))  # 14

# 添字1を6に変更：現在値との差分を加算
bit.add(1, 6 - bit.sum(1, 2))
	```
## 注意点・計算量 {toggle="true"}
	- 添字は0始まり。sum(l, r) は右端rを含まない。
	- add(p, x) は代入ではなく加算。setはない。
	- 更新しながら合計・個数を数えるときに使う。最小値・最大値ならセグメント木。
	- 初期化 O(N)、加算・区間和 O(log N)、空間 O(N)。上の配列からの登録は O(N log N)。
## 関連 {toggle="true"}
	<mention-page url="https://app.notion.com/p/4189b4299e618172b184f667622dc68b">10.4 座標圧縮</mention-page>
	<mention-page url="https://app.notion.com/p/4189b4299e6181ac887eeaeac7e61191">SortedList と座標圧縮＋BITの使い分け｜個数と重みの合計</mention-page>
	[ACL Pythonの実装](https://github.com/not522/ac-library-python/blob/master/atcoder/fenwicktree.py)
