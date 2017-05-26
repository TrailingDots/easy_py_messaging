import client_create_class
client = client_create_class.ClientCreateClass({})
client.start()
msg = 'Hello world!'
print 'Sending : "%s"' % msg
response = client.send(msg)
print 'Response: "%s"\n' % response
client.join()

