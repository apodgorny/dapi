class SquareEmbedding:
	def __init__(self, matrix, h_labels, v_labels):
		self.matrix   = matrix  # 2D array, h x v
		self.h_labels = h_labels  # “ности” — строки
		self.v_labels = v_labels  # символы — столбцы

	def __getitem__(self, idx):
		h, v = idx
		return self.matrix[h][v]
	
	def h_slice(self, h):      # вернуть всю строку (одну ность)
		return self.matrix[h]

	def v_slice(self, v):      # вернуть весь столбец (один символ)
		return [row[v] for row in self.matrix]

# Пусть h_labels = ['глубинность', 'яркость', 'злость']
# Пусть v_labels = ['О', 'Г', 'Т']

# --- Тесты ---

E = SquareEmbedding(
	matrix=[
		[0.1, 0.8, 0.4],  # глубинность
		[0.7, 0.0, 0.2],  # яркость
		[0.3, 0.2, 0.9],  # злость
	],
	h_labels=['глубинность', 'яркость', 'злость'],
	v_labels=['О', 'Г', 'Т']
)

# 1. Горизонтальный срез (одна ность)
h = 0  # глубинность
print('Test 1:', E.h_slice(h))

# 2. Смешивание ностей
h1, h2 = 0, 2  # глубинность + злость
mix = [a + b for a, b in zip(E.h_slice(h1), E.h_slice(h2))]
print('Test 2:', mix)

# 3. Вертикальный срез (один символ)
v = 1  # символ "Г"
print('Test 3:', E.v_slice(v))

# 4. Анонимная ность
anon_h = [0.5, 0.5, 0.5]  # искусственная горизонталь
print('Test 4:', anon_h)

# 5. Устойчивость смысла при смене символа
h = 2  # злость
for v in range(len(E.v_labels)):
	print(f'Test 5: h={h}, v={v}:', E[h, v])
