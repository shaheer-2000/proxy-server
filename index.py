import socket
from multiprocessing import Process, Value
from threading import Thread
# FIFO, LRU, LIFO, LFU implemented, FIFO and LRU used
from cache import FIFO, LRU
from content_filter import ContentFilter
import ssl
import requests

def proxy_handler(shutdown, cf, cache, conn: socket, addr):
	while True:
		if shutdown.value:
			break

		try:
			data = conn.recv(1024)

			try:
				data = data.decode("utf-8")
			except UnicodeDecodeError:
				data = data.decode("iso-8859-1")

			if not data:
				break

			data = data.split(" ")
			if data[2].startswith("HTTP") or data[2].startswith("HTTPS"):
				file = data[1][1:]

			if cf.is_blacklisted(file):
				conn.sendall(b"HTTP/1.1 403 Forbidden\r\n\r\n")
				conn.shutdown(socket.SHUT_WR)
				conn.close()
				continue
			
			t1 = cache[0].get(file)
			t2 = cache[1].get(file)
			if t1:
				conn.sendall(t1)
				conn.shutdown(socket.SHUT_WR)
				conn.close()
			elif t2:
				conn.sendall(t2)
				conn.shutdown(socket.SHUT_WR)
				conn.close()
			else:
				# fetch here as res
				res = requests.get(f"http://{file}", verify=False)
				headers = "\r\n".join([f"{key}={value}" for key, value in res.headers.items()])
				response = (f"HTTP/1.1 {res.status_code} {res.reason}\r\n{headers}\r\n\r\n").encode() + res.content + b"\r\n"
				cache[0].put(file, response)
				cache[1].put(file, response)
				conn.sendall(response)
				conn.shutdown(socket.SHUT_WR)
				conn.close()
		except ConnectionAbortedError:
			break
		except OSError:
			break

	return

def connection_handler(connections, cf, cache, shutdown, serv_socket):
	while True:
		if shutdown.value:
			break

		try:
			conn, addr = serv_socket.accept()

			conn_thread = Thread(target=proxy_handler, args=(shutdown, cf, cache, conn, addr))

			if not shutdown.value:
				# if addr in connections:
				# 	connections["conn"].close()
				# 	# connections["conn_thread"].terminate()
				# 	# while conn["conn_thread"].is_alive():
				# 	# 	pass
				# 	# connections["conn_thread"].close()
				# 	connections["conn_thread"].

				connections[addr] = {
					"conn": conn,
					"conn_thread": conn_thread
				}

			conn_thread.start()
		except socket.timeout:
			pass

if __name__ == "__main__":
	# Throws error
	# context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
	# context.verify_mode = ssl.CERT_REQUIRED
	# context.load_cert_chain("./.ssl/cadb.pem", "./.ssl/cadb.key")

	shutdown = Value("b", 0)

	serv_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	serv_socket.settimeout(1)
	serv_socket.bind(("127.0.0.1", 8000))
	serv_socket.listen(1)

	connections = {}

	# sec_serv_socket = context.wrap_socket(serv_socket, server_hostname="proxy")
	cf = ContentFilter("./database")
	fifo_cache = FIFO()
	lru_cache = LRU()
	cache = [fifo_cache, lru_cache]
	conn_handler = Thread(target=connection_handler, args=(connections, cf, cache, shutdown, serv_socket))

	conn_handler.start()

	while True:
		opt = int(input("""
		Select the option number to proceed:
		1) Stop Server
		2) Blacklist page
		3) Unblacklist page
		4) Save Blacklist
		"""))

		if opt == 1:
			shutdown.value = 1

			for conn in connections.values():
				if conn["conn"]:
					conn["conn"].close()

				if conn["conn_thread"]:
					# conn["proc"].terminate()
					# while conn["proc"].is_alive():
					# 	pass
					# conn["conn_thread"].close()
					conn["conn_thread"].join()

			conn_handler.join()
			serv_socket.close()
			print("Thank you for using")
			break
		elif opt == 2:
			page = input("Enter name of page to blacklist: ")
			cf.blacklist(page)
		elif opt == 3:
			page = input("Enter name of page to unblacklist: ")
			cf.unblacklist(page)
		elif opt == 4:
			cf.save()

	# conn_handler.join()
