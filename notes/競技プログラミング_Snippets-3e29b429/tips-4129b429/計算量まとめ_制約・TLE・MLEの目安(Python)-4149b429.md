# 計算量まとめ｜制約・TLE・MLEの目安（Python）

Source: https://www.notion.so/4149b4299e61814cb4bdea7eb0431873

---

**最大入力・時間制限・メモリ制限を確認し、処理回数と保存量を別々に見積もる。**
## 1. 制約から選ぶ計算量
Pythonで数秒の制限を想定した、解法を探す目安。ACを保証する境界ではない。
<table header-row="true">
<tr>
<td>Nの上限</td>
<td>候補になる計算量</td>
<td>典型・注意</td>
</tr>
<tr>
<td>8〜10</td>
<td>O(N!)</td>
<td>順列全探索。10! ≈ 363万。各候補の処理も数える</td>
</tr>
<tr>
<td>20前後</td>
<td>O(2\^N)、O(N × 2\^N)</td>
<td>部分集合・bit DP。20 × 2²⁰ ≈ 2100万なので後者は要注意</td>
</tr>
<tr>
<td>100前後</td>
<td>O(N³)</td>
<td>三重ループ。100³ = 100万</td>
</tr>
<tr>
<td>2,000前後</td>
<td>O(N²)</td>
<td>二重ループ・区間DP。2000² = 400万</td>
</tr>
<tr>
<td>10,000前後</td>
<td>O(N²)は慎重に</td>
<td>N² = 1億。まず O(N log N) 以下を探す</td>
</tr>
<tr>
<td>200,000前後</td>
<td>O(N log N)、O(N)</td>
<td>ソート・二分探索・累積和など</td>
</tr>
<tr>
<td>1,000,000前後</td>
<td>O(N)を優先</td>
<td>入力・保存量も確認。O(N log N) は組み込みソートなど処理次第</td>
</tr>
<tr>
<td>10⁹以上</td>
<td>O(log N)、O(√N)、O(1)など</td>
<td>N回は回さず、二分探索・約数列挙・数式を検討</td>
</tr>
</table>
M・Qもあれば **O(NQ)、O(NM)、全テストケースの合計**まで確認する。
## 2. TLE：何回くらいのループが危ない？
**「1秒で必ず○回」ではない。** Pythonで書く軽いループを数秒で実行する場合の、粗い目安。
<table header-row="true">
<tr>
<td>合計反復回数</td>
<td>判断</td>
</tr>
<tr>
<td>10⁶程度</td>
<td>軽い処理なら候補にしやすい</td>
</tr>
<tr>
<td>10⁷程度</td>
<td>処理内容・時間制限を確認。環境による差も大きい</td>
</tr>
<tr>
<td>10⁸程度</td>
<td>高リスク。回数削減や別解を検討し、必要なら最大ケースで測る</td>
</tr>
<tr>
<td>10⁹以上</td>
<td>通常のPythonループでは避ける</td>
</tr>
</table>
- **内側の処理も掛け算する。** N回のループ内で長さNのリストを検索・コピーすると O(N²)。
- **二重ループでも必ず O(N²) ではない。** 各ポインタが合計N回しか動かないなら O(N) の場合もある。
- 組み込みの `sort`・`sum` と手書きループは速度が違う。CPython / PyPyでも変わる。
- **定数倍に注意！！！！典型90より、O(N\*\*5)だけど、nC5=1/120N\*\*5で定数倍でめっちゃちっちゃくなるから間に合う**
### よく使う処理
<table header-row="true">
<tr>
<td>処理</td>
<td>計算量</td>
</tr>
<tr>
<td>listの添字アクセス、len</td>
<td>O(1)</td>
</tr>
<tr>
<td>list.append</td>
<td>ならし O(1)</td>
</tr>
<tr>
<td>x in list、list.pop(0)</td>
<td>O(N)</td>
</tr>
<tr>
<td>x in set / dict</td>
<td>平均 O(1)</td>
</tr>
<tr>
<td>dequeの両端の追加・削除</td>
<td>O(1)</td>
</tr>
<tr>
<td>bisectで位置を探す</td>
<td>O(log N)</td>
</tr>
<tr>
<td>list.insertで挿入する</td>
<td>O(N)</td>
</tr>
<tr>
<td>heapへの追加・取り出し</td>
<td>O(log N)</td>
</tr>
<tr>
<td>sort / sorted</td>
<td>O(N log N)</td>
</tr>
<tr>
<td>sum、min、maxで全要素を調べる</td>
<td>O(N)</td>
</tr>
<tr>
<td>長さKのリストのスライス・コピー</td>
<td>O(K)</td>
</tr>
</table>
## 3. MLE：計算回数ではなく、同時に持つデータ量
**ピーク時のメモリ使用量が制限を超えるとMLE。** 配列以外に、入力・コピー・辞書・実行環境の使用分も含まれる。
### 配列のメモリ目安
代表的な64bit CPythonでの概算。MBは10⁶バイト。**PyPyでは内部表現が異なるので、そのまま当てはめない。**
<table header-row="true">
<tr>
<td>保存するもの</td>
<td>10⁶要素</td>
<td>10⁷要素</td>
<td>10⁸要素</td>
</tr>
<tr>
<td>`[False] * N` のlist</td>
<td>約8 MB</td>
<td>約80 MB</td>
<td>約800 MB</td>
</tr>
<tr>
<td>小さな整数を各要素で別々に持つlist</td>
<td>約36 MB</td>
<td>約360 MB</td>
<td>約3.6 GB</td>
</tr>
<tr>
<td>`bytearray(N)`</td>
<td>約1 MB</td>
<td>約10 MB</td>
<td>約100 MB</td>
</tr>
</table>
- listは参照だけで概ね **1要素8バイト**。整数などの本体は別途必要。同じ値を共有する `[0] * N` は、整数がN個別々にある場合とは異なる。
- 二次元配列は **行数 × 列数 × 1要素の目安 × 枚数**。各行の管理分も加わる。
- `bytearray` は0〜255の値を保存でき、boolのDPにも使える。
- `sys.getsizeof` は参照先のデータを含めないため、二次元list全体の使用量は一発では測れない。
**例：N = 10⁴のbool二次元listを2枚持つと、参照部分だけで約1.6 GB。1024 MiB（約1.07 GB）の制限を超える。**
## 4. TLE・MLEになったら
<table header-row="true">
<tr>
<td>症状</td>
<td>最初に確認すること</td>
</tr>
<tr>
<td>TLE</td>
<td>最大入力で何回処理する？ ループ内に検索・コピー・ソートが隠れていない？</td>
</tr>
<tr>
<td>MLE</td>
<td>今後参照しない結果まで保存していない？ 全件保存やコピーは必要？</td>
</tr>
<tr>
<td>配列の使い回しでWA</td>
<td>状態の意味・参照先・更新順は合っている？</td>
</tr>
</table>
## 5. 今回の教訓：区間DP
**必要な結果だけ保存し、答えは計算と同時に数える。**
- **メモリ：** 2つ短い区間の結果だけ残し、空間 O(N²) → O(N)。
- **時間：** DP更新時に加算し、集計用の約1億回の走査を削除。時間計算量自体は O(N²) のまま。
- **状態管理：** 奇数長と偶数長を分け、内側の区間を `prev[i+1]` で参照。
- **上書き順：** iを小さい順に進めれば、参照する `prev[i+1]` は未更新。
題材：[ABC468 D — Pre-Palindrome](https://atcoder.jp/contests/abc468/tasks/abc468_d)
### 参考
計算量の基礎：[AtCoder Python教材](https://atcoder.jp/contests/APG4bPython/tasks/APG4bPython_u?lang=ja)。上の反復回数表はAC保証ではなく、Python向けの慎重な判断目安。
メモリ計測の注意：[Python公式 — sys.getsizeof](https://docs.python.org/3/library/sys.html#sys.getsizeof)。
