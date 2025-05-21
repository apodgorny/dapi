from gensim.models import Word2Vec
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# 1. Тренируем простую модель
sentences = [
	['king', 'queen', 'man', 'woman', 'throne', 'royal'],
	['dog', 'cat', 'pet', 'animal', 'bark', 'meow'],
	['car', 'truck', 'vehicle', 'road', 'wheel']
]
model = Word2Vec(sentences, vector_size=10, sg=1, negative=5, epochs=100, min_count=1)

# 2. Берём вектора W_in и W_out для одного слова
word = 'king'
vec_in  = model.wv[word]         # стандартный embedding (W_in)
idx     = model.wv.key_to_index[word]
vec_out = model.syn1neg[idx]     # output embedding (W_out)

# 3. Сравним похожих по смыслу слов по обоим пространствам
def top_similar(vec, space, wv, topn=3):
	# Сравниваем с каждым словом в векторном пространстве
	sims = cosine_similarity([vec], space)[0]
	top_idx = np.argsort(-sims)[:topn+1]   # +1, чтобы исключить само слово
	return [wv.index_to_key[i] for i in top_idx if wv.index_to_key[i] != word][:topn]

print('W_in похожие:', top_similar(vec_in, model.wv.vectors, model.wv))
print('W_out похожие:', top_similar(vec_out, model.syn1neg, model.wv))

# 4. Сравни “аналогии” на сложении векторов (W_in vs W_out)
vec_in_analogy  = model.wv['queen'] - model.wv['woman'] + model.wv['man']
vec_out_analogy = model.syn1neg[model.wv.key_to_index['queen']] \
                - model.syn1neg[model.wv.key_to_index['woman']] \
                + model.syn1neg[model.wv.key_to_index['man']]

print('W_in аналогия:', top_similar(vec_in_analogy, model.wv.vectors, model.wv))
print('W_out аналогия:', top_similar(vec_out_analogy, model.syn1neg, model.wv))
