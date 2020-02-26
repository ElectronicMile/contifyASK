from ask_sdk_core.skill_builder import SkillBuilder

sb = SkillBuilder()

from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.utils import is_request_type, is_intent_name, request_util
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response
from ask_sdk_model.ui import SimpleCard, LinkAccountCard

import contify_utils as utils


class LaunchRequestHandler(AbstractRequestHandler):
	def can_handle(self, handler_input):
		# type: (HandlerInput) -> bool
		return is_request_type("LaunchRequest")(handler_input)

	def handle(self, handler_input):
		# type: (HandlerInput) -> Response
		speech_text = "Welcome to the Alexa Skills Kit, you can say hello!"

		handler_input.response_builder.speak(speech_text).set_card(
			SimpleCard("Hello World", speech_text)).set_should_end_session(False)
		return handler_input.response_builder.response

class GetContifyContextHandler(AbstractRequestHandler):
	def can_handle(self, handler_input):
		# type: (HandlerInput) -> bool
		return is_intent_name("GetContifyContextIntent")(handler_input)

	def handle(self, handler_input):
		# type: (HandlerInput) -> Response

		resp = handler_input.response_builder
		token, speech_text, authproblem, sp = utils.login(handler_input)

		if authproblem:
			resp.set_card(LinkAccountCard())
		else:
			speech_text = utils.get_current_context(sp)

		return resp.speak(speech_text).response

class NextIntentHandler(AbstractRequestHandler):
	def can_handle(self, handler_input):
		# type: (HandlerInput) -> bool
		return is_intent_name("AMAZON.NextIntent")(handler_input)

	def handle(self, handler_input):
		# type: (HandlerInput) -> Response

		resp = handler_input.response_builder
		token, speech_text, authproblem, sp = utils.login(handler_input)

		if authproblem:
			resp.set_card(LinkAccountCard())
		else:
			controlparams = {'country': None, 'album_type': None, 'limit': 20, 'offset': 0}
			controlpayload = None
			controlurl = 'https://api.spotify.com/v1/me/player/%s'
			sp._internal_call('POST', controlurl % "next", controlpayload, controlparams)

		return None

"""class LikeActionHandler(AbstractRequestHandler):
	def can_handle(self, handler_input):
		# type: (HandlerInput) -> bool
		return is_request_type("LikeAction")(handler_input)

	def handle(self, handler_input):
		# type: (HandlerInput) -> Response

		resp = handler_input.response_builder
		token, speech_text, authproblem, sp = utils.login(handler_input)

		if authproblem:
			resp.set_card(LinkAccountCard())"""

class HelpIntentHandler(AbstractRequestHandler):
	def can_handle(self, handler_input):
		# type: (HandlerInput) -> bool
		return is_intent_name("AMAZON.HelpIntent")(handler_input)

	def handle(self, handler_input):
		# type: (HandlerInput) -> Response
		speech_text = "You can say hello to me!"

		handler_input.response_builder.speak(speech_text).ask(speech_text).set_card(
			SimpleCard("Hello World", speech_text))
		return handler_input.response_builder.response

class CancelAndStopIntentHandler(AbstractRequestHandler):
	def can_handle(self, handler_input):
		# type: (HandlerInput) -> bool
		return is_intent_name("AMAZON.CancelIntent")(handler_input) or \
			   is_intent_name("AMAZON.StopIntent")(handler_input)

	def handle(self, handler_input):
		# type: (HandlerInput) -> Response
		speech_text = "Goodbye!"

		handler_input.response_builder.speak(speech_text).set_card(
			SimpleCard("Hello World", speech_text))
		return handler_input.response_builder.response

class SessionEndedRequestHandler(AbstractRequestHandler):
	def can_handle(self, handler_input):
		# type: (HandlerInput) -> bool
		return is_request_type("SessionEndedRequest")(handler_input)

	def handle(self, handler_input):
		# type: (HandlerInput) -> Response
		# any cleanup logic goes here

		return handler_input.response_builder.response

from ask_sdk_core.dispatch_components import AbstractExceptionHandler

class AllExceptionHandler(AbstractExceptionHandler):

	def can_handle(self, handler_input, exception):
		# type: (HandlerInput, Exception) -> bool
		return True

	def handle(self, handler_input, exception):
		# type: (HandlerInput, Exception) -> Response
		# Log the exception in CloudWatch Logs
		print(exception)

		speech = "Sorry, I didn't get it. Can you please say it again!!"
		handler_input.response_builder.speak(speech).ask(speech)
		return handler_input.response_builder.response


sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(GetContifyContextHandler())
sb.add_request_handler(NextIntentHandler())
#sb.add_request_handler(LikeActionHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelAndStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())

sb.add_exception_handler(AllExceptionHandler())

handler = sb.lambda_handler()