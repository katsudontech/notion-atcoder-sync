# 遅延セグメント木（ACL Python）

Source: https://www.notion.so/3e29b4299e6181b7a5b3d132ed547992

---

<callout icon="⏳" color="orange_bg">
	遅延セグメント木は、区間全体への更新と区間クエリをどちらも O(log N) で処理する。通常のSegTreeに「更新を必要になるまで保留する仕組み」を加えたもの。
</callout>
## いつ使うか
- 区間内の全要素に値を足しながら、区間和・最小値・最大値を求める
- 区間内の全要素を同じ値へ変更しながら、区間クエリを処理する
- 区間に一次関数を作用させる
- 更新と取得が交互に来るため、いもす法や累積和だけでは処理できない
一点更新だけなら、通常のSegTreeのほうが設計も実装も簡単。
## 一般形
```python
from atcoder.lazysegtree import LazySegTree


# データ同士を結合する
def op(left, right):
    return ...


# データ側の単位元
e = ...


# 更新 f をデータ x に反映する
def mapping(f, x):
    return ...


# 既存の更新 g の後に、新しい更新 f を行う合成
# 戻り値は f ∘ g
def composition(f, g):
    return ...


# 何もしない更新
id_ = ...


seg = LazySegTree(
    op,
    e,
    mapping,
    composition,
    id_,
    values,
)
```
## 5つの定義
<table fit-page-width="true" header-row="true">
<tr>
<td>名前</td>
<td>役割</td>
</tr>
<tr>
<td>`op(left, right)`</td>
<td>左右の区間情報を結合する</td>
</tr>
<tr>
<td>`e`</td>
<td>データ側の単位元</td>
</tr>
<tr>
<td>`mapping(f, x)`</td>
<td>更新fを区間情報xへ反映する</td>
</tr>
<tr>
<td>`composition(f, g)`</td>
<td>既存の更新gの後に新しい更新fを行う合成。f ∘ gを返す</td>
</tr>
<tr>
<td>`id_`</td>
<td>何も変更しない更新</td>
</tr>
</table>
## 成り立つ必要がある条件
- `op` は結合的で、単位元 `e` を持つ
- 更新集合は、合成しても同じ種類の更新になる
- `id_` を作用させてもデータが変わらない
- 区間を結合してから更新しても、各区間を更新してから結合しても同じ結果になる
```plain text
mapping(f, op(x, y))
== op(mapping(f, x), mapping(f, y))
```
<callout icon="⚠️" color="yellow_bg">
	composition(f, g) は「既存のgを行った後に、新しいfを行う更新」を返す。加算では順序が目立たないが、代入や一次関数では順番を逆にすると誤答になる。
</callout>
## 実戦テンプレ：区間加算＋区間和
区間和では、ノードに「合計・要素数」の2つを持たせる。区間へxを加えると、合計は x × 要素数だけ増えるため。
```python
from atcoder.lazysegtree import LazySegTree


# S = (区間の合計, 区間の要素数)
def op(left, right):
    left_sum, left_size = left
    right_sum, right_size = right
    return (left_sum + right_sum, left_size + right_size)


e = (0, 0)


# F = 区間へ加える値
def mapping(f, x):
    total, size = x
    return (total + f * size, size)


# 先にgを加え、その後fを加える
def composition(f, g):
    return f + g


# 0を加えても変化しない
id_ = 0


A = list(map(int, input().split()))
values = [(x, 1) for x in A]

seg = LazySegTree(
    op,
    e,
    mapping,
    composition,
    id_,
    values,
)
```
## 基本操作
```python
# 半開区間 [l, r) の全要素に x を加える
seg.apply(l, r, x)

# 1要素だけに更新xを適用する
# Python版ではfをキーワード引数で渡す
seg.apply(p, f=x)

# 半開区間 [l, r) の合計
total = seg.prod(l, r)[0]

# A[p] の現在値
value = seg.get(p)[0]

# A[p] を x へ置き換える
seg.set(p, (x, 1))

# 配列全体の合計
total_all = seg.all_prod()[0]
```
## 動作例
```python
A = [1, 2, 3, 4, 5]
values = [(x, 1) for x in A]

seg = LazySegTree(
    op, e, mapping, composition, id_, values
)

# A[1:4]の全要素に10を加える
seg.apply(1, 4, 10)

# 配列は [1, 12, 13, 14, 5] の状態
print(seg.prod(1, 4)[0])  # 39
print(seg.all_prod()[0])  # 45
print(seg.get(2)[0])      # 13
```
## なぜ要素数を持たせるのか
区間の合計だけを持つと、更新値を何回足すべきか分からない。
たとえば3要素を含む区間へ10を加えると、区間和は10ではなく30増える。そのため `S = (合計, 要素数)` として、`mapping` で `f * size` を加算する。
<callout icon="⚠️" color="red_bg">
	区間加算＋区間和を長さNだけで初期化してはいけない。LazySegTree(..., N) では各要素がe=(0, 0)になり、要素数が0のままになる。0配列から始める場合も \[(0, 1) for _ in range(N)\] を渡す。
</callout>
```python
# 0がN個ある配列から始める正しい方法
values = [(0, 1) for _ in range(N)]
seg = LazySegTree(
    op, e, mapping, composition, id_, values
)
```
## 適用例2：区間加算＋区間最小値
最小値は区間の長さを必要としないため、データSを整数のまま扱える。
```python
from atcoder.lazysegtree import LazySegTree


def op(a, b):
    return min(a, b)


e = float("inf")


def mapping(f, x):
    return x + f


def composition(f, g):
    return f + g


id_ = 0

A = [5, 2, 8, 6, 1]
seg = LazySegTree(op, e, mapping, composition, id_, A)

# A[1:4]に3を加える
seg.apply(1, 4, 3)

print(seg.prod(1, 4))  # min(5, 11, 9) = 5
print(seg.all_prod())  # 1
```
## 適用例3：区間代入＋区間和
更新Fを「代入する値」、`None` を「何もしない更新」として扱う。
```python
from atcoder.lazysegtree import LazySegTree


# S = (区間の合計, 区間の要素数)
def op(left, right):
    return (left[0] + right[0], left[1] + right[1])


e = (0, 0)


# fがNoneなら何もしない
# それ以外なら区間全体をfへ変更する
def mapping(f, x):
    total, size = x

    if f is None:
        return x

    return (f * size, size)


# 新しい代入fがあれば、以前の代入gを上書きする
def composition(f, g):
    if f is None:
        return g

    return f


id_ = None

A = [1, 2, 3, 4, 5]
values = [(x, 1) for x in A]
seg = LazySegTree(
    op, e, mapping, composition, id_, values
)

# A[1:4]をすべて10へ変更
seg.apply(1, 4, 10)

# 配列は [1, 10, 10, 10, 5] の状態
print(seg.prod(0, 5)[0])  # 36
```
この例では `composition(新しい更新, 既存の更新)` の順番が重要。新しい代入は以前の代入を上書きする。
## ACL Pythonの主なAPI
<table fit-page-width="true" header-row="true">
<tr>
<td>操作</td>
<td>意味</td>
<td>計算量</td>
</tr>
<tr>
<td>`set(p, x)`</td>
<td>1要素をxへ置き換える</td>
<td>O(log N)</td>
</tr>
<tr>
<td>`get(p)`</td>
<td>1要素を取得する</td>
<td>O(log N)</td>
</tr>
<tr>
<td>`prod(l, r)`</td>
<td>半開区間をopで結合する</td>
<td>O(log N)</td>
</tr>
<tr>
<td>`all_prod()`</td>
<td>配列全体をopで結合する</td>
<td>O(1)</td>
</tr>
<tr>
<td>`apply(p, f=f)`</td>
<td>1要素へ更新fを適用する</td>
<td>O(log N)</td>
</tr>
<tr>
<td>`apply(l, r, f)`</td>
<td>半開区間へ更新fを適用する</td>
<td>O(log N)</td>
</tr>
<tr>
<td>`max_right(l, g)`</td>
<td>左端を固定した境界探索</td>
<td>O(log N)</td>
</tr>
<tr>
<td>`min_left(r, g)`</td>
<td>右端を固定した境界探索</td>
<td>O(log N)</td>
</tr>
</table>
構築はO(N)。各関数自体がO(T)なら、操作の計算量にもO(T)が掛かる。
## 通常のSegTreeとの使い分け
<table fit-page-width="true" header-row="true">
<tr>
<td>必要な操作</td>
<td>選択</td>
</tr>
<tr>
<td>一点更新＋区間取得</td>
<td>SegTree</td>
</tr>
<tr>
<td>区間更新＋区間取得</td>
<td>LazySegTree</td>
</tr>
<tr>
<td>最後にまとめて区間加算の結果だけ欲しい</td>
<td>いもす法</td>
</tr>
</table>
## 注意事項
- `apply(l, r, f)` と `prod(l, r)` はどちらも半開区間
- ACL Pythonで一点だけに適用するときは `apply(p, f=f)` とキーワード引数を使う
- `set` は値の置き換え、`apply` は定義した更新の適用
- `composition(f, g)` は新しいfを既存のgの後に作用させる
- データS・更新F・e・id_の型と意味を最初に明確にする
- `mapping` の戻り値はデータS、`composition` の戻り値は更新F
- 代入更新のid_には、実際の更新値と衝突しない値を使う
- 通常のSegTreeと違い、`get` も遅延更新を伝播するためO(log N)
## よくあるミス
- 区間加算＋区間和で、ノードに要素数を持たせない
- compositionの引数順を逆にする
- 0を代入する更新と「何もしない更新」を同じ0で表す
- `apply(l, r, f)` の右端rを含むと思い込む
- 区間更新が必要なのに通常のSegTreeを使う
- 長さNで初期化し、各葉の要素数が0になる
## 関連
- <mention-page url="https://app.notion.com/p/3e29b4299e6181e18292d0d9933ed639"/>
- <mention-page url="https://app.notion.com/p/3e29b4299e61816eaaaee0d5aace01ef"/>
- <mention-page url="https://app.notion.com/p/3e29b4299e61818780e2d000de2a3332"/>
## 公式資料
- [AtCoder Library Lazy Segtreeドキュメント](https://atcoder.github.io/ac-library/production/document_en/lazysegtree.html)
- [ac-library-python](https://github.com/not522/ac-library-python)
