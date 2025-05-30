from lib import O, Agent

from client.schemas.narrative_schemas import (
	BeatSchema,
	TimelineSchema,
	ThreadSchema
)

class Timeline(Agent):
	class InputType(O):
		text: str

	class OutputType(O):
		text: str

	async def invoke(self, text):
		# BeatSchema.load(1).delete()
		# VoiceSchema.delete(1)

		# beat = BeatSchema(
		# 	timestamp = 123,
		# 	text      = 'foobar'
		# )
		# voice = VoiceSchema(
		# 	name   = 'test',
		# 	tone   = 'neutral',
		# 	style  = 'flat',
		# 	intent = 'say something'
		# )

		# voice.save()
		# beat.save()

		# voice = VoiceSchema.load(1)
		# beat  = BeatSchema.load(1)

		# voice.style = 'foo'

		# print(beat)
		# print(voice)

		# thread = ThreadSchema(
		# 	voice = voice,
		# 	beats = [beat]
		# )
		# print(thread)
		# thread.save()

		# thread = ThreadSchema.load(1)
		# print(thread)
		# thread.voice.style = 'bar'
		# thread.save()
		# thread = ThreadSchema.load(1)
		# print(thread)

		# beat1 = BeatSchema(
		# 	timestamp = 1232,
		# 	text = "baz"
		# )
		# thread.beats.append(beat1)
		# thread.save()
		# thread = ThreadSchema.load(1)
		# print(thread)

		# BeatSchema.load(1).delete()
		# thread.save()
		# thread = ThreadSchema.load(1)
		# print(thread)

		# Создание базовых объектов
		# voice = VoiceSchema(name='test', tone='neutral', style='flat', intent='say something')
		# beat1 = BeatSchema(timestamp=123, text='first')
		# beat2 = BeatSchema(timestamp=456, text='second')

		# voice.save()
		# beat1.save()
		# beat2.save()

		# # Связь с thread
		# thread = ThreadSchema(voice=voice, beats=[beat1, beat2])
		# thread.save()
		# print('▶️ Created:', thread)

		# # Удаляем один beat
		# beat1.delete()
		# thread.save()
		# thread = ThreadSchema.load(thread.id)
		# print('❌ After beat1 deletion:', thread)

		# # Удаляем voice
		# voice.delete()
		# thread.save()
		# thread = ThreadSchema.load(thread.id)
		# print('❌ After voice deletion:', thread)

		# # Добавляем новый beat
		# beat3 = BeatSchema(timestamp=789, text='third')
		# beat3.save()
		# thread.beats.append(beat3)
		# thread.save()
		# thread = ThreadSchema.load(thread.id)
		# print('➕ After adding beat3:', thread)
		############
		# v  = VoiceSchema(name='v', tone='soft', style='x', intent='says')
		# b1 = BeatSchema(timestamp=1, text='b1')
		# b2 = BeatSchema(timestamp=2, text='b2')

		# t1 = ThreadSchema(voice=v, beats=[b1, b2])
		# t2 = ThreadSchema(voice=v, beats=[b2])

		# v.save()
		# b1.save()
		# b2.save()
		# t1.save()
		# t2.save()

		# b2.delete()     # ⛔ удаляем объект, входящий в оба ThreadSchema

		# t1.save()       # 💥 должно сохраниться без ошибок
		# t2.save()

		# print(t1)
		# print(t2)
		#######
		# v = VoiceSchema(name='x', tone='t', style='s', intent='foo')
		# v.save()

		# v = VoiceSchema.load(1)
		# v.style = 'new'
		# v.save()

		# v2 = VoiceSchema.load(1)
		# v2.style = 'another'
		# v2.save()

		# print(VoiceSchema.load(1))  # ✅ должен быть style: "another"
		####
		# b1 = BeatSchema(timestamp=1, text='a')
		# b2 = BeatSchema(timestamp=2, text='b')

		# t1 = ThreadSchema(voice=None, beats=[b1])
		# t2 = ThreadSchema(voice=None, beats=[b2])
		# b1.text = 't1 uses me'
		# b2.text = 't2 uses me'

		# timeline = TimelineSchema(threads={'t1': t1, 't2': t2})
		# timeline.save()

		# TimelineSchema.load(1)

		#####

		# voice = VoiceSchema(
		# 	name   = 'shared',
		# 	tone   = 'warm',
		# 	style  = 'soft',
		# 	intent = 'greet'
		# )
		# voice.save()

		# t1 = ThreadSchema(voice=voice, beats=[])
		# t2 = ThreadSchema(voice=voice, beats=[])
		# t1.save()
		# t2.save()

		# print('✅ Both threads saved:')
		# print(t1)
		# print(t2)

		# # Удаляем voice
		# voice.delete()

		# print('❌ After deleting voice:')
		# print(t1)
		# print(t2)

		# # Пробуем сохранить снова — не должно быть ошибки
		# t1.save()
		# t2.save()

		# print('✅ Saved successfully after voice deletion:')
		# print(t1)
		# print(t2)
		###
		# 1️⃣ Удаляем Thread — проверяем что edges ушли, voice/beat остались
		v = VoiceSchema(name='v', tone='x', style='x', intent='x')
		b = BeatSchema(timestamp=1, text='b1')
		t = ThreadSchema(voice=v, beats=[b])
		v.save()
		b.save()
		t.save()

		t.delete()
		print('✅ Deleted thread:', t)

		assert VoiceSchema.load(v.id)
		assert BeatSchema.load(b.id)

		# 2️⃣ Добавляем beat повторно в новый thread — дубликаты не создаются
		t2 = ThreadSchema(voice=v, beats=[b])
		t2.save()
		t2_again = ThreadSchema.load(t2.id)
		assert len(t2_again.beats) == 1
		print('✅ Reused beat in second thread:', t2_again)

		# 3️⃣ Удаляем beat → создаём новый → id не reused
		b2 = BeatSchema(timestamp=2, text='b2')
		b2.save()
		id_old = b2.id
		b2.delete()

		b3 = BeatSchema(timestamp=3, text='b3')
		b3.save()
		assert b3.id != id_old, '❌ ID should not be reused!'
		print('✅ New beat has different id:', b3.id)

		# 4️⃣ Проверка кеша: load(x) всегда возвращает ту же ссылку
		b4 = BeatSchema(timestamp=4, text='b4')
		b4.save()
		ref1 = BeatSchema.load(b4.id)
		ref2 = BeatSchema.load(b4.id)
		assert ref1 is ref2
		print('✅ Cached object returned as same ref')



		return 'done'
