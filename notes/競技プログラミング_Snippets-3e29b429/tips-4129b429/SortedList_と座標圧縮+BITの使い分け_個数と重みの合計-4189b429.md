# SortedList と座標圧縮＋BITの使い分け｜個数と重みの合計

Source: https://www.notion.so/4189b4299e6181ac887eeaeac7e61191

---

**個数を数えるだけなら両方でできる。タプルに情報を保存しても、その情報の範囲合計まで高速になるわけではない。**
### まず比較
<table header-row="true">
<tr>
<td>やりたいこと</td>
<td>SortedList</td>
<td>座標圧縮＋BIT</td>
</tr>
<tr>
<td>値を1個追加・削除</td>
<td>add / remove などで管理</td>
<td>対応する座標の出現回数を＋1 / −1</td>
</tr>
<tr>
<td>値が L 以上 R 以下の要素数</td>
<td>bisect_right(R) − bisect_left(L)</td>
<td>出現回数配列の該当範囲の合計</td>
</tr>
<tr>
<td>重み・点数・在庫数の範囲合計</td>
<td>標準機能だけでは高速に集計できない</td>
<td>各座標に重みを持たせて区間和</td>
</tr>
<tr>
<td>未知の値が途中で登場</td>
<td>そのまま追加できる</td>
<td>通常の座標圧縮では更新対象の値を事前に集める必要がある</td>
</tr>
</table>
SortedListは値を重複込みでソート順に保持する。BITは配列の一点加算と区間和を高速に処理する。「出現回数＋BIT」は、要素1個につき重み1を足す特殊ケースなので、SortedListによる範囲内の個数と同じことができる。
### タプルを入れれば範囲合計もできる？
例えば (価格, 在庫数) を格納する。
```python
sl = SortedList([(100, 5), (200, 2), (300, 8)])
```
価格100〜200円の範囲は二分探索で探せる。しかし、位置の差で分かるのは「商品が2種類」ということ。求めたい在庫合計は 5 + 2 = 7。
該当する添字の範囲を \[lo, hi) とすると、
```python
total = sum(stock for _, stock in sl.islice(lo, hi))
```
は該当する K 個を全部読むので O(K)。範囲を見つける二分探索が速くても、その後の集計が速いとは限らない。
BITなら価格を座標圧縮し、対応する添字に在庫数を格納する。部分的な合計を内部に保持するので、在庫更新も範囲合計も O(log M)（Mは座標数）。
在庫数ぶん価格をSortedListに入れる方法もあるが、在庫が10⁹個なら現実的ではない。BITなら、その座標に10⁹を1回加算できる。
タプルは辞書順に並ぶため、価格が同じなら第2要素も比較される。タプルで二分探索するときは同価格の要素を漏らさない境界にも注意する。
### ABC484 Eではどちらでも同じ方針
[ABC484 E - Subsegment Sum Finder](https://atcoder.jp/contests/abc484/tasks/abc484_e)
S\[i\] = sum(A\[:i\]) とする。右端 r を固定すると、
```plain text
L ≤ S[r] − S[l] ≤ R
⇔ S[r] − R ≤ S[l] ≤ S[r] − L
```
つまり「過去の累積和のうち、指定範囲にあるものの個数」を数える。
- SortedList：過去の累積和を追加し、二分探索の位置の差で個数を数える。
- 座標圧縮＋BIT：過去の累積和の出現回数を加算し、範囲の出現回数を合計する。
**この問題ではSortedListで代替できる。BITに変える必要があるわけではない。**
実装上は S\[0\] = 0 を登録し、各 r について検索してから S\[r\] を登録する。これで l \< r が守られ、空区間を数えない。同じ累積和も位置が違えば別の候補なので重複を数える。
### 座標圧縮＋BITの基本形
```python
from bisect import bisect_left, bisect_right
from atcoder.fenwicktree import FenwickTree

# 更新する値を事前にすべて集めておく
values = sorted(set(all_values))
index = {v: i for i, v in enumerate(values)}
bit = FenwickTree(len(values))

# 値 x の重みを w 増やす（個数を数えるなら w = 1）
bit.add(index[x], w)

# 値が L 以上 R 以下の重みの合計
lo = bisect_left(values, L)
hi = bisect_right(values, R)
total = bit.sum(lo, hi)
```
座標の一覧では重複を除くが、登録時には毎回加算する。検索境界 L, R は values に含まれていなくてもよい。圧縮が保存するのは大小関係であり、元の値同士の距離ではない。
### 計算量と選び方
- 座標圧縮＋BIT：前処理 O(N log N)、加算・区間和 O(log M)、BITの領域 O(M)。
- sortedcontainers.SortedList：公式文書では追加・二分探索などを「おおよそ O(log N)」と表現。厳密な最悪 O(log N) 保証とは区別する。
- 普通の list ＋ bisect.insort は挿入 O(N)。SortedListと混同しない。
- 更新がなく範囲合計を聞かれるだけなら、ソート＋累積和でもよい。BITが役立つのは更新と集計を繰り返す場合。
**判断基準：順序・順位・個数ならSortedListを候補にする。更新しながら重みの範囲合計を求めるならBITを候補にする。**
### 関連
<mention-page url="https://app.notion.com/p/3e29b4299e618103b4ffd8002c1c5488">2.1–2.2 一次元累積和</mention-page>
<mention-page url="https://app.notion.com/p/3e29b4299e61818780e2d000de2a3332">8.9 セグメント木：RSQ和</mention-page>
[SortedList公式ドキュメント](https://grantjenks.com/docs/sortedcontainers/sortedlist.html)
