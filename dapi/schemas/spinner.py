import os, sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from lib import O


class SpinnerCriteriaSchema(O):
	goal             : str  = O.Field(default='', description='Главная цель персонажа в этом диалоге или сцене.')
	style            : str  = O.Field(default='', description='Стиль общения персонажа — лаконично, дерзко, мягко, с юмором, иронично, нейтрально и пр.')
	tension          : str  = O.Field(default='', description='Уровень напряжения или интенсивности чувств: низкое, среднее, высокое, нарастающее, спадает и т.д.')
	emotion          : str  = O.Field(default='', description='Явная эмоция персонажа в данный момент: злость, интерес, смущение, доверие, страх, восхищение, вызов и т.д.')
	constraints      : str  = O.Field(default='', description='Внутренние или внешние ограничения, которые сдерживают действия или речь персонажа.')
	context          : str  = O.Field(default='', description='Краткое описание важного контекста ситуации: место, обстоятельства, отношения, обстановка.')
	scene_type       : str  = O.Field(default='', description='Тип сцены: флирт, конфликт, дружба, деловой спор, соблазнение, примирение и т.д.')
	depth            : str  = O.Field(default='', description='Глубина рефлексии: импульсивно, поверхностно, рассудочно, с самоанализом и т.д.')
	can_retreat      : bool = O.Field(default=True, description='Можно ли персонажу сменить тему, уйти, разрядить ситуацию?')
	actions          : str  = O.Field(default='', description='Какие действия допустимы: только слова, слова+жесты, можно ли касаться, шутить, доминировать и т.п.')
	opponent_emotion : str  = O.Field(default='', description='Какая эмоция чувствуется в собеседнике по мнению героя.')
	opponent_goal    : str  = O.Field(default='', description='Какую цель, по ощущению героя, преследует собеседник.')
	opponent_style   : str  = O.Field(default='', description='Стиль поведения собеседника — открытый, закрытый, давящий, играющий и т.п.')
	opponent_tension : str  = O.Field(default='', description='Уровень напряжения у собеседника: спокойный, напряжённый, игривый и т.д.')

class SpinnerStructureSchema(O):
    spins: dict[str, str]
