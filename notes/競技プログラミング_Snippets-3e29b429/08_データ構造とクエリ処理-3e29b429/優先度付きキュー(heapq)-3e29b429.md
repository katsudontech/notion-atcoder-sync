# 優先度付きキュー（heapq）

Source: https://www.notion.so/3e29b4299e618158a66eca986db60d55

---

## テンプレ {toggle="true"}
	```python
hq = []
heappush(hq, value)
minimum = heappop(hq)

# 最大値を取りたい場合は符号を反転
heappush(hq, -value)
maximum = -heappop(hq)
	```
## 注意事項 {toggle="true"}
	- heapqは最小ヒープ
	- 空のheapからpopしない
	- タプルを入れると先頭要素から辞書順で比較される
	- valueは、配列(ベクトル？も指定できて、先頭のやつで大小比較)
## 計算量 {toggle="true"}
	- push / pop：O(log N)
	- 最小値の参照：O(1)
