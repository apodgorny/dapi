from lib import O


class Resource(O):
	'''Describes pleasant pro-survival vibe or input provided by another.'''
	emotional : str = O.Field('', description='Emotional support or validation this authority provides')
	physical  : str = O.Field('', description='Physical help or care this authority provides')
	mental    : str = O.Field('', description='Ideas, knowledge, or advice provided')
	spiritual : str = O.Field('', description='Belief systems or values transmitted')


class Authority(O):
	'''Represents a person who served as an authority figure providing formative influence.'''
	name      : str      = O.Field('', description='Name of the authority figure')
	sex       : str      = O.Field('', description='Sex of the authority figure')
	relation  : str      = O.Field('', description='Relation of the authority to the person')
	age_diff  : int      = O.Field(0,  description='Age difference between authority and person')
	since_age : int      = O.Field(0,  description='Since what age this authority was perceived as such')
	resource  : Resource = O.Field(default_factory=Resource, description='Resources this authority provides')


class PodgornySquare(O):
	'''Describes key psychological ratios of behavior and emotional tendency.'''
	offended_guilty_ratio : float = O.Field(0.5, description='How much side feels offended vs guilty')
	active_passive_ratio  : float = O.Field(0.5, description='How active vs passive the strategy is')


class Side(O):
	'''Represents one pole (side) of a duality.'''
	name                  : str            = O.Field('', description='Name or label of this side')
	authority             : Authority      = O.Field(default_factory=Authority, description='The authority figure associated with this side')
	judgement_to_self     : str            = O.Field('', description='What this side judges in self')
	judgement_to_opposite : str            = O.Field('', description='What this side judges in the opposite side')
	square                : PodgornySquare = O.Field(default_factory=PodgornySquare, description='Key psychological ratios of this side')


class TraumaAttributes(O):
	'''Describes symptomatic patterns and triggers linked to a trauma.'''
	triggers       : list[str] = O.Field(default_factory=list, description='What situations trigger the trauma')
	psychosomatics : list[str] = O.Field(default_factory=list, description='Somatic symptoms linked to trauma')
	key_phrases    : list[str] = O.Field(default_factory=list, description='Internalized traumatic phrases')


class TraumaComponents(O):
	'''Breakdown of the trauma into its physical, emotional, mental, and spiritual aspects.'''
	physical  : str = O.Field('', description='Body sensations and physical effects')
	emotional : str = O.Field('', description='Emotional content of the trauma')
	mental    : str = O.Field('', description='Beliefs formed through trauma')
	spiritual : str = O.Field('', description='Existential or spiritual injury')


class TraumaCoping(O):
	'''Strategies and dependencies used to survive or adapt to the trauma.'''
	resource  : str       = O.Field('',                        description='Pleasant feeling obtained from coping actions')
	actions   : list[str] = O.Field(default_factory=list,      description='Typical coping behaviors')
	authority : Authority = O.Field(default_factory=Authority, description='Who first introduced this coping mechanism to the subject')


class Trauma(O):
	'''Encapsulates the full structure and history of a trauma.'''
	description : str              = O.Field('', description='Description of traumatic event')
	setting     : str              = O.Field('', description='Context in which trauma occurred')
	actors      : list[str]        = O.Field(default_factory=list, description='Who was involved')
	since_age   : int              = O.Field(0, description='Approximate age when it started')
	attributes  : TraumaAttributes = O.Field(default_factory=TraumaAttributes, description='Triggers, psychosomatics, phrases')
	components  : TraumaComponents = O.Field(default_factory=TraumaComponents, description='Core trauma layers')
	coping      : TraumaCoping     = O.Field(default_factory=TraumaCoping, description='Survival mechanisms')


class Duality(O):
	'''Represents a core psychological polarity anchored in a trauma.'''
	name   : str    = O.Field('', description='The core polarity name, like yin_side vs. yang_side')
	yin    : Side   = O.Field(default_factory=Side, description='Yin side (usually submissive or adaptive)')
	yang   : Side   = O.Field(default_factory=Side, description='Yang side (usually rebellious or expansive)')
	# trauma : Trauma = O.Field(default_factory=Trauma, description='Underlying trauma that anchors the polarity')


class Subpersonality(O):
	'''Represents a coherent internal role composed of harmonized sides from various dualities.'''
	name  : str       = O.Field('', description='Name or label of the subpersonality')
	sides : list[str] = O.Field(default_factory=list, description='List of Side names that make up this subpersonality')


class Personality(O):
	'''Represents the whole psyche as a network of subpersonalities.'''
	subpersonalities : list[Subpersonality] = O.Field(default_factory=list, description='All inner subpersonalities')
