import json


class Registration:
	def __init__(self, nick, can_swim, friend):
		self.nick = nick
		self.can_swim = can_swim
		self.friend = friend

	def serialize(self):
		registration_dict = {
			"nick": self.nick,
			"can_swim": self.can_swim,
			"friend": self.friend
		}

		json_string = json.dumps(registration_dict)

		return json_string