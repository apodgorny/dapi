import json

from .wordwield import WordWield as ww


class StateItem:
	def __init__(self, data, crumbs):
		self.data   = data
		self.crumbs = crumbs

	def __str__(self):
		crumbs = '\t' + ' → '.join([f'"{c}"' for c in self.crumbs])
		data   = '\t' + json.dumps(self.data, ensure_ascii=False, indent=4).replace('\n', '\n\t')
		return f'\t{"-"*40}\n{crumbs}\n{data}'


class State:
	def __init__(self, name: str):
		self.name  = name
		self.items = []

	def add(self, data, crumbs):
		self.items.append(StateItem(data, crumbs))

	def values(self, key: str) -> list:
		'''Return list of values for a given key across all items.'''
		return [item.data[key] for item in self.items if key in item.data]

	def __str__(self):
		hr = '=' * 40
		title = f'STATE `{self.name}`'
		items = "\n".join([str(item) for item in self.items])
		return f'{hr}\n{hr}\n{title}\n{items}'


class StateGrid:
	def __init__(self, state_names, operator_name, common={}):
		self.states        = [State(name) for name in state_names]
		self.operator_name = operator_name
		self.common        = common or {}

	def __getitem__(self, name: str) -> State:
		for state in self.states:
			if state.name == name:
				return state
		raise KeyError(f'State `{name}` not found')

	def invoke(self, **initial_data):
		self.states[0].add(initial_data, [initial_data])

		for n in range(0, len(self.states)-1):
			for item in self.states[n].items:
				datas = ww.invoke(
					self.operator_name,
					state = self.states[n].name,
					data  = item.data,
					h_ctx = [item.data for item in self.states[n+1].items],
					v_ctx = item.crumbs,
					c_ctx = self.common
				)
				if datas is None: return
				for data in datas:
					crumbs = item.crumbs + [data]
					print('CRUMBS', crumbs)
					self.states[n+1].add(data, crumbs)
			print(self.states[n+1])

