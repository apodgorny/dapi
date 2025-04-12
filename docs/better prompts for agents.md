- deep_listener
- "Послушай, что говорят разработчики в контексте {{context_framer.output.context}}. Что на самом деле стоит за их словами? Где боль, где вдохновение, где неловкость?"
- Определяет реальные чувства и ментальные модели, стоящие за словами пользователей и разработчиков.

- insight_catcher
- "Слушай разговор о {{context_framer.output.topic}} как будто ищешь искру. Что вспыхивает в речи, что может стать началом всей системы?"
- Улавливает идеи и образы, обладающие высокой смысловой плотностью.

- signal_disentangler
- "Раздели шум от сигнала в {{deep_listener.output.input_text}}. Где структура, а где фон? Преобразуй хаос в смысловые линии."
- Выделяет значимые линии смыслов из неструктурированного потока данных.

- scenario_modeler
- "Опиши путь пользователя в {{context_framer.output.interaction_goal}} как историю. Где он начнёт, что будет делать, куда дойдёт?"
- Строит реалистичные пользовательские сценарии как эмоционально-логические траектории.

- concept_sculptor
- "На основе {{insight_catcher.output.problem_description}} сформируй смысловые объекты: что здесь — событие, сущность, отношение?"
- Создаёт первичный онтологический каркас из смыслов и категорий.

- topology_mapper
- "Построй карту связей между {{concept_sculptor.output.core_concepts}}. Где переходы, где сосредоточия?"
- Создаёт структурное представление взаимосвязей между концепциями.

- tradeoff_cartographer
- "Проанализируй компромиссы в {{topology_mapper.output.design_space}}."
- Выделяет зоны конфликта требований, возможностей и ограничений.

- pattern_encoder
- "Преврати {{scenario_modeler.output.intended_behavior}} в функцию."
- Преобразует поведение и паттерны в код, сохраняющий выразительность намерения.

- refactor_surgeon
- "Сократи {{pattern_encoder.output.code_block}}. Убери повторения, сохрани суть."
- Упрощает код, сохраняя его выразительную силу.

- readability_watcher
- "Прочитай {{pattern_encoder.output.code_block}} как рассказ. Где возникает тяжесть? Исправь это."
- Проверяет и усиливает плавность чтения кода.

- emotion_filter
- "Как ты себя чувствуешь, когда видишь {{pattern_encoder.output.interface_snapshot}}?"
- Оценивает эмоциональный резонанс интерфейса.

- recognition_trigger
- "В {{pattern_encoder.output.design_piece}} найди деталь, вызывающую ощущение 'это моё'."
- Находит точки узнавания и смысловой близости.

- intent_mirror
- "Сравни {{pattern_encoder.output.current_implementation}} с {{context_framer.output.original_intent}}."
- Проверяет, соответствует ли реализация изначальному замыслу.

- tension_alchemist
- "Найди форму между {{tradeoff_cartographer.output.constraint}} и {{scenario_modeler.output.desired_outcome}}."
- Преобразует напряжение противоречий в выразительное решение.

- drift_attune
- "Проверь, не ушёл ли фокус в {{orchestrator.output.project_progress}}."
- Отслеживает смещения и возвращает проект к его сути.

- contrast_sharpener
- "Уточни грань в {{tradeoff_cartographer.output.decision_point}}."
- Делает различия между путями более чёткими.

- essence_filter
- "Выдели суть из {{pattern_encoder.output.code_block}}."
- Очищает выражение от вторичных элементов, оставляя ядро.

- structure_breather
- "Проверь дыхание в {{pattern_encoder.output.code_structure}}."
- Проверяет живость, симметрию, естественность архитектурного каркаса.

- storyweaver
- "Объясни {{concept_sculptor.output.concept}} как другу за чаем."
- Переводит смысловую суть в ясный, человечный рассказ.

- tone_curator
- "Настрой стиль документации под {{context_framer.output.audience_profile}}."
- Формирует тональность общения.

- ambiguity_remover
- "В {{storyweaver.output.documentation_piece}} найди и устрани двусмысленности."
- Делает текст однозначным и кристаллизованным.

- edge_case_provoker
- "Нарушь поведение {{pattern_encoder.output.functionality}} до предела."
- Проверяет устойчивость под давлением и искажениями.

- third_path_finder
- "Если {{tradeoff_cartographer.output.design_decision}} не имеет идеального решения, найди или создай третий путь."
- Находит оригинальные решения между бинарными крайностями.

- pre_echo_tester
- "Покажи {{pre_echo_synthesizer.output.prototype_or_partial}} людям. Что они чувствуют?"
- Собирает ощущения до завершения продукта.

- satisfaction_harvester
- "Выдели суть из {{feedback_aggregator.output.feedback_pool}}."
- Фиксирует истинные точки удовольствия, узнавания и ценности.

- context_framer
- "Определи контекст: {{user_input.topic}}, цель: {{user_input.intent}}, нужды аудитории: {{user_input.audience}}."
- Задает рамки смысла, тон и цель работы.

- orchestrator
- "Собери список агентов и их фазы."
- Управляет ходом взаимодействий.

- output_synthesizer
- "Из {{pattern_encoder.output.code_block}} и {{storyweaver.output.documentation_piece}} сформируй итоговую документацию."
- Сводит результаты в целостный артефакт.

- pre_echo_synthesizer
- "Создай {{prototype_or_partial}} из {{pattern_encoder.output.code_fragment}} и {{scenario_modeler.output.user_flow}}."
- Готовит предварительный опыт для восприятия.

- feedback_aggregator
- "Собери {{feedback_pool}} из {{user_feedback.raw}} и профилей {{user_feedback.profiles}}."
- Преобразует отклики в аналитический ресурс.

- data_router
- "На основе {{orchestrator.output.agent_list}} и {{agent_io_map}} направь данные в нужные места."
- Обеспечивает поток данных между агентами.

