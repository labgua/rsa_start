import tornado.ioloop
import tornado.web
import tornado.websocket

class ChatSecretWebSocket(tornado.websocket.WebSocketHandler):

	clients = {}
	names = {}

	def check_origin(self, origin):
		return True

	def open(self):
		print("ChatSecretWebSocket opened")

	def on_message(self, message):
		message = str(message)
		if message.startswith("REC####") :
			rec_params = message.split("####")
			name = rec_params[1]
			#pub_key = rec_params[2]
			
			# se stesso client, permetti il rename
			if name in ChatSecretWebSocket.clients.keys() and self not in ChatSecretWebSocket.names[self] :
				self.write_message("SERVER####Nome gia registrato")
				return

			ChatSecretWebSocket.clients[name] = self
			ChatSecretWebSocket.names[self] = name

			wellcome_msg = "Hello {0}!".format(name)
			print(wellcome_msg)
			self.write_message("SERVER####{0}".format(wellcome_msg))

		if message.startswith("SEND####") :
			send_params = message.split("####")
			name_receiver = send_params[1]
			msg = send_params[2]

			sender_name = ChatSecretWebSocket.names[self]
			ref_receiver = ChatSecretWebSocket.clients[name_receiver]


			ref_receiver.write_message( "RECV####{0}####{1}".format(sender_name, msg) )

		if message.startswith("KEYREQUEST####") :
			keyrequest_params = message.split("####")
			name_receiver = keyrequest_params[1]

			sender_name = ChatSecretWebSocket.names[self]
			ref_receiver = ChatSecretWebSocket.clients[name_receiver]

			print("{0} chiede la chiave pubblica di {1} - inoltro a {2}".format(sender_name, name_receiver, sender_name) )

			ref_receiver.write_message( "KEYREQUEST####{0}".format(sender_name) )

		if message.startswith("KEYREPLY####") :
			keyreplay_params = message.split("####")
			name_receiver = keyreplay_params[1]
			key_sender = keyreplay_params[2]

			sender_name = ChatSecretWebSocket.names[self]
			ref_receiver = ChatSecretWebSocket.clients[name_receiver]

			print("{0} invia la chiave a {1} - inoltro a {2}".format(sender_name, name_receiver, name_receiver))

			ref_receiver.write_message( "KEYREPLY####{0}####{1}".format(sender_name, key_sender))


	def on_close(self):
		name_self = ChatSecretWebSocket.names[self]
		print("WebSocket closed by " + name_self )
		del ChatSecretWebSocket.clients[name_self]
		del ChatSecretWebSocket.names[self]
		
		




print("Chat Cifrata Server")

app = tornado.web.Application([
    ('/chat', ChatSecretWebSocket)
])

if __name__ == "__main__":
	app.listen(8888)
	tornado.ioloop.IOLoop.current().start()