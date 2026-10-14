# セグメント木：一般形・適用例（ACL Python）

Source: https://www.notion.so/3e29b4299e6181e18292d0d9933ed639

---

<callout icon="🌲" color="purple_bg">
	セグメント木は、結合可能な区間情報を持ち、一点更新と区間クエリをともに O(log N) で処理するデータ構造。RMQやRSQは、演算 op と単位元 e を変えた具体例にすぎない。
</callout>
## 一般形
```python
from atcoder.segtree import SegTree


# 左区間の情報 a と右区間の情報 b を結合する
def op(a, b):
    return ...


# op(e, x) == op(x, e) == x となる単位元
e = ...

# 初期配列から構築
seg = SegTree(op, e, A)

# または、全要素を e とした長さ N の配列を作る
seg = SegTree(op, e, N)
```
## セグ木に載せられる条件
### 1. 結合結果が同じ種類の情報になる
2つの区間情報を結合した結果を、さらに別の区間情報と結合できる必要がある。
### 2. opが結合的である
括弧の付け方を変えても結果が同じになる必要がある。
```plain text
op(op(a, b), c) == op(a, op(b, c))
```
加算・最小値・最大値・GCD・XORなどは結合的。減算や除算は一般に結合的ではないため、そのままでは使えない。
### 3. 単位元eが存在する
どちら側から結合しても、相手の値を変えない値を用意する。
```plain text
op(e, x) == op(x, e) == x
```
<callout icon="💡" color="blue_bg">
	opは交換可能でなくてもよい。op(a, b) と op(b, a) が異なっていても、結合的で単位元があれば使える。文字列連結や行列積も対象になる。
</callout>
## 代表的なopとe
<table fit-page-width="true" header-row="true">
<tr>
<td>求める情報</td>
<td>op</td>
<td>e</td>
<td>主な用途</td>
</tr>
<tr>
<td>区間和</td>
<td>`a + b`</td>
<td>`0`</td>
<td>途中で値が変わる区間合計</td>
</tr>
<tr>
<td>区間最小値</td>
<td>`min(a, b)`</td>
<td>`inf`</td>
<td>RMQ</td>
</tr>
<tr>
<td>区間最大値</td>
<td>`max(a, b)`</td>
<td>`-inf`</td>
<td>最大値・境界探索</td>
</tr>
<tr>
<td>最大公約数</td>
<td>`gcd(a, b)`</td>
<td>`0`</td>
<td>区間GCD</td>
</tr>
<tr>
<td>XOR</td>
<td>`a ^ b`</td>
<td>`0`</td>
<td>区間XOR</td>
</tr>
<tr>
<td>積</td>
<td>`a * b`</td>
<td>`1`</td>
<td>区間積・mod積</td>
</tr>
<tr>
<td>文字列連結</td>
<td>`a + b`</td>
<td>`""`</td>
<td>順序を保った区間結合</td>
</tr>
</table>
## 共通API
```python
# A[p]をxへ置き換える
seg.set(p, x)

# A[p]を取得する
value = seg.get(p)

# 半開区間 [l, r) をopで結合する
result = seg.prod(l, r)

# 配列全体をopで結合する
result_all = seg.all_prod()
```
## 適用例1：区間最大値
```python
from atcoder.segtree import SegTree

A = [3, 1, 4, 1, 5]
seg = SegTree(max, float("-inf"), A)

print(seg.prod(1, 4))  # max(1, 4, 1) = 4

seg.set(2, 0)
print(seg.prod(1, 4))  # max(1, 0, 1) = 1
```
使いどころ：値を更新しながら、任意区間の最大値を求める問題。
## 適用例2：区間GCD
```python
from math import gcd
from atcoder.segtree import SegTree

A = [12, 18, 24, 30]
seg = SegTree(gcd, 0, A)

print(seg.prod(0, 3))  # gcd(12, 18, 24) = 6

seg.set(1, 20)
print(seg.prod(0, 3))  # gcd(12, 20, 24) = 4
```
使いどころ：更新を含む区間の最大公約数、区間全体を同じ数で割れるかの判定。
## 適用例3：最小値とその添字を同時に取得
各要素を「値・添字」のタプルにする。Pythonのタプルは辞書順比較なので、値が同じ場合は小さい添字が選ばれる。
```python
from atcoder.segtree import SegTree

A = [5, 2, 8, 2, 7]

values = [(value, index) for index, value in enumerate(A)]
e = (float("inf"), float("inf"))
seg = SegTree(min, e, values)

minimum, index = seg.prod(0, len(A))
print(minimum, index)  # 2 1

# A[1]を10へ変更
seg.set(1, (10, 1))

minimum, index = seg.prod(0, len(A))
print(minimum, index)  # 2 3
```
使いどころ：区間の最小値だけでなく、それが存在する位置も必要な問題。
## 適用例4：複数の情報を1ノードに持たせる
区間平均は平均同士を直接結合できないが、「合計・個数」のペアなら結合できる。
```python
from atcoder.segtree import SegTree


def op(left, right):
    left_sum, left_count = left
    right_sum, right_count = right
    return (left_sum + right_sum, left_count + right_count)


A = [4, 7, 2, 9]
values = [(x, 1) for x in A]
seg = SegTree(op, (0, 0), values)

total, count = seg.prod(1, 4)
average = total / count
print(average)  # (7 + 2 + 9) / 3 = 6.0
```
このように、必要な区間情報をタプルとして設計すると応用範囲が広がる。
## 適用例5：max_rightによる境界探索
`max_right(l, f)` は、左端 `l` を固定し、条件 `f` を満たす最大の右端を O(log N) で探す。
非負配列について、区間和が `limit` 以下になる最大の右端を探す例。
```python
from atcoder.segtree import SegTree

A = [2, 1, 3, 2, 4]
seg = SegTree(lambda a, b: a + b, 0, A)

l = 1
limit = 5

r = seg.max_right(l, lambda total: total <= limit)

print(r)              # 3
print(seg.prod(l, r)) # A[1] + A[2] = 4
```
この例では `A[1:3]` の合計4は条件を満たすが、次の要素を含む `A[1:4]` の合計6は条件を満たさない。
### max_right・min_leftの条件
- 判定関数 `f` は単調である必要がある
- `f(e)` は必ずTrueである必要がある
- 同じ入力に対して同じ結果を返し、副作用を持たせない
- `min_left(r, f)` は右端を固定して、条件を満たす最小の左端を探す
- 区間和で境界探索する場合、負数があると単調性が崩れることがある
## さらにある適用例
- 区間XOR
- modを取りながらの区間積
- 行列積による遷移の合成
- 括弧列について、区間の合計と最小累積値を保持する
- 最大部分配列和について、合計・最大接頭辞・最大接尾辞・区間内最大値を保持する
- 文字列や関数合成など、順序に意味がある区間情報の結合
## どのデータ構造を選ぶか
<table fit-page-width="true" header-row="true">
<tr>
<td>条件</td>
<td>候補</td>
</tr>
<tr>
<td>更新なし・区間和だけ</td>
<td>累積和</td>
</tr>
<tr>
<td>一点加算・区間和</td>
<td>Fenwick Tree</td>
</tr>
<tr>
<td>一点代入・一般的な区間クエリ</td>
<td>SegTree</td>
</tr>
<tr>
<td>区間更新・区間クエリ</td>
<td>LazySegTree</td>
</tr>
</table>
## 注意事項
- `prod(l, r)` は半開区間であり、添字 `r` は含まれない
- `set(p, x)` は加算ではなく代入
- opが結合的か、eが本当に単位元かを必ず確認する
- opは交換可能である必要はないが、左右の順番は維持される
- op自体がO(T)なら、各操作の計算量もO(T log N)になる
- 区間への一括更新は通常のSegTreeでは処理できないため、LazySegTreeを検討する
## よくあるミス
- 減算・除算・単純な平均など、結合的でない演算をそのままopにする
- RMQの単位元を0にする
- max_rightで単調でない条件を使う
- 元配列Aだけを更新し、SegTree側へsetし忘れる
- 1-indexedの入力を0-indexedへ変換し忘れる
## 公式資料
- [ac-library-python SegTreeの実装](https://github.com/not522/ac-library-python/blob/master/atcoder/segtree.py)
- [AtCoder Library SegTreeドキュメント](https://atcoder.github.io/ac-library/production/document_en/segtree.html)
