# Counter（出現回数の集計）

Source: https://www.notion.so/3f19b4299e618119975ad4ad98b49066

---

## コピペ用コード
```python
from collections import Counter

A = [1, 2, 1, 3, 2, 1]
cnt = Counter(A)

print(cnt[1])  # 3
print(cnt[9])  # 0（存在しない値）

for value, count in cnt.items():
    print(value, count)
# 1 3
# 2 2
# 3 1
```
**値ごとの出現回数を管理する、dictの仲間。** 配列を渡すだけで集計できる。
## 使い方
### 文字列の文字数を数える
```python
cnt = Counter("aaabbcaa")
print(cnt)  # Counter({'a': 5, 'b': 2, 'c': 1})
```
離れた場所にある同じ文字も合計する。
### 入力から集計する
```python
N = int(input())
A = list(map(int, input().split()))
cnt = Counter(A)
```
### 回数を取得・追加・削減する
```python
cnt = Counter()
cnt[5] += 1
cnt[5] += 2
print(cnt[5])  # 3

cnt[5] -= 1
print(cnt[5])  # 2

cnt.update([5, 7, 7])  # 各要素の出現回数を加算
# 5が3個、7が2個
```
通常のdictと異なり、存在しないキーでも `cnt[x]` は0を返すので、そのまま `+= 1` できる。
### よく使う操作
```python
cnt = Counter([1, 2, 1, 3, 2, 1])

kinds = len(cnt)                    # 種類数：3（0・負の回数がない場合）
total = sum(cnt.values())           # 回数の合計：6
max_count = max(cnt.values(), default=0)  # 最大の出現回数：3
top = cnt.most_common(2)            # [(1, 3), (2, 2)]

for value in sorted(cnt):           # 値の昇順
    print(value, cnt[value])

for value, count in cnt.items():    # 値と回数を同時に取得
    pass
```
`most_common(k)` は出現回数が多い順の `(値, 回数)` を最大k件返す。同数なら最初に登場した順になる。
## 注意点・計算量
### 0個になってもキーは残る
```python
cnt = Counter([5])
cnt[5] -= 1

print(cnt[5])   # 0
print(5 in cnt) # True
print(len(cnt)) # 1

if cnt[5] == 0:
    del cnt[5]

print(5 in cnt) # False
```
- `x in cnt` は「キーが登録されているか」の判定。
- 「1個以上あるか」を調べるなら `cnt[x] > 0`。
- 減算すると回数が負になることもある。要素の削除を表す場合は、存在数を確認してから減らす。
- 追加・削除しながら `len(cnt)` を種類数として使うなら、0個になったキーを `del cnt[x]` で消す。
- 存在しないキーの `cnt[x]` を読むだけではキーは追加されない。
### ループと集計の注意
- `for x in cnt:` で取り出すのはキーだけ。値と回数なら `cnt.items()`。
- `cnt.update(...)` は上書きではなく加算。通常のdictのupdateと違う。
- Counterのキーには整数・文字列・タプルなど、ハッシュ可能な値を使う。リストはキーにできない。
- 入力全体がN要素、異なる値がK種類なら、作成は平均O(N)、領域はO(K)。
- 1つのキーの取得・加算・削除は平均O(1)。全種類の走査はO(K)。
- `sum(cnt.values())` や `max(cnt.values())` はO(K)。ループ内で毎回実行すると重くなる。
- 値でソートする `sorted(cnt)` や全件の頻度順ソート `cnt.most_common()` はO(K log K)。
## 競プロでの典型例
### 同じ値を持つペアの個数
同じ値がc個あれば、異なる2つの位置を選ぶ方法は `c * (c - 1) // 2` 通り。
```python
A = [1, 2, 1, 3, 2, 1]
cnt = Counter(A)
ans = sum(c * (c - 1) // 2 for c in cnt.values())
print(ans)  # 4（1のペアが3通り、2のペアが1通り）
```
### すべての値が何回ずつ現れるかで判定
```python
cnt = Counter(A)

# すべての種類がちょうど2回ずつ現れるか
ok = all(c == 2 for c in cnt.values())
```
空のCounterに対する `all(...)` はTrue。1種類以上必要なら `bool(cnt) and all(...)` にする。
### 並べ替えて同じ列になるか
```python
S = "aabc"
T = "caba"
print(Counter(S) == Counter(T))  # True
```
順序を無視して、値と出現回数が一致するかを調べられる。
## ランレングス圧縮との違い
入力が `"aaabbcaa"` の場合：
- **Counter**：`{'a': 5, 'b': 2, 'c': 1}`。全体で各文字が何個あるか。
- **ランレングス圧縮**：`[['a', 3], ['b', 2], ['c', 1], ['a', 2]]`。どの順番で何個ずつ連続するか。
**全体の個数ならCounter、連続区間ならランレングス圧縮。** Counterから元の並び順を復元することはできない。
<mention-page url="https://app.notion.com/p/3f19b4299e618152b852e96b2659a7ab"/>
## dict / defaultdictとの使い分け
- **Counter**：出現回数を数える。既存の配列・文字列を一括で集計するときに便利。
- **defaultdict(int)**：0から始まる数値を自分で加算して管理する。頻度だけでなく、値ごとの合計などにも使う。
- **dict**：名前→点数など、一般的なキーと値の対応を管理する。存在しないキーへの直接アクセスはKeyErrorになる。
