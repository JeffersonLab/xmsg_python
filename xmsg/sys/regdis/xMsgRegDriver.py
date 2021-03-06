# coding=utf-8

import zmq

from xmsg.core.xMsgConstants import xMsgConstants
from xmsg.core.xMsgUtil import xMsgUtil
from xmsg.core.xMsgExceptions import TimeoutReached, RegistrationException
from xmsg.sys.regdis.xMsgRegResponse import xMsgRegResponse
from xmsg.sys.regdis.xMsgRegRequest import xMsgRegRequest


class xMsgRegDriver(object):
    """Methods for registration and discovery of xMsg actors, i.e. publishers
    and subscribers.

    This class also contains the base method used by all xMsg extending classes
    to create 0MQ socket for communications. This means that this class owns
    the 0MQ context.
    The sockets use the default registrar port: xMsgConstants#REGISTRAR_PORT.

    Attributes:
        context (zmq.Context): zmq context
        reg_address (RegAddress): registrar address
    """

    def __init__(self, context, reg_address):
        # 0MQ context
        self.context = context

        self._reg_address = reg_address
        # Connection settings
        self._connection = self.zmq_socket(self.context, zmq.REQ,
                                           reg_address.address,
                                           xMsgConstants.CONNECT)

    def get_address(self):
        """Returns the Registration address object

        Returns:
            RegAddress: Registration Address
        """
        return self._reg_address

    def get_context(self):
        """Returns the main zmq socket context

        Returns:
            zmq.Context: zmq context
        """
        return self.context

    def add(self, registration_data, is_publisher):
        """Sends registration request to the server

        Request is wired using xMsg message construct, that have 3 parts:
            topic, sender, and data.
        Data is the object of the xMsgRegistration

        Args:
            registration_data (xMsgRegistration): registration information obj.
            is_publisher (bool): if set to be true then this is a request
                to register a publisher, otherwise this is a subscriber
                registration request
        """
        # Data serialization
        if registration_data.IsInitialized():
            # Send topic, sender, followed by the data
            # Topic of the message is a string = "registerPublisher"
            # or "registerSubscriber"
            if is_publisher:
                topic = xMsgConstants.REGISTER_PUBLISHER

            else:
                topic = xMsgConstants.REGISTER_SUBSCRIBER

            timeout = xMsgConstants.REGISTER_REQUEST_TIMEOUT
            request = xMsgRegRequest(topic, registration_data.name,
                                     registration_data)

            self.request(request, timeout)

    def remove(self, registration_data, is_publisher):
        """Sends remove registration request to the server.

        Request is wired using xMsg message construct, that have 3 parts:
        topic, sender, and data. Data is the object of the xMsgRegistration

        Args:
            registration_data (xMsgRegistration): registration information
                object
            is_publisher (bool): if set to be true then this is a request
                to register a publisher, otherwise this is a subscriber
                registration request
        """

        # Data serialization
        if registration_data.IsInitialized():
            # Send topic, sender, followed by the data
            # Topic of the message is a string = "removePublisher"
            # or "removeSubscriber"
            if is_publisher:
                topic = xMsgConstants.REMOVE_PUBLISHER

            else:
                topic = xMsgConstants.REMOVE_SUBSCRIBER

            timeout = xMsgConstants.REGISTER_REQUEST_TIMEOUT
            request = xMsgRegRequest(topic,
                                     registration_data.name,
                                     registration_data)

            self.request(request, timeout)

    def remove_all(self, s_host):
        pass

    def find(self, registration_data, is_publisher):
        """Searches the FE registration and discovery databases for an actor

        The method will search for xMsg actors that publishes or subscribes
        the topic of the interest (globally). The search criteria i.e. topic is
        defined within the xMsgRegistrationData object.

        Args:
            name (String): the name of the requester/sender
            registration_data (xMsgRegistration): xMsgRegistration object
            is_publisher (bool): if set to be true then this is a request to
                register a publisher, otherwise this is a subscriber
                registration request

        Returns:
            list: list of xMsgRegistration objects
        """
        # Data serialization
        if registration_data.IsInitialized():
            # Send topic, sender, followed by the data
            # Topic of the message is a string = "findPublisher"
            # or "findSubscriber"
            if is_publisher:
                topic = xMsgConstants.FIND_PUBLISHER

            else:
                topic = xMsgConstants.FIND_SUBSCRIBER

            timeout = xMsgConstants.FIND_REQUEST_TIMEOUT
            request_message = xMsgRegRequest(topic,
                                             registration_data.name,
                                             registration_data)

            return self.request(request_message, timeout)

    def request(self, request, timeout):
        """Sends a request to the given registrar server and waits the response.

        Args:
            socket (zmq.Socket): zmq socket for communication
            request (xMsgRegRequest): xMsg request object
            timeout (int): timeout for processing request in seconds

        Returns:
            bytes[]: serialized registration information
        """
        try:
            self._connection.send_multipart(request.msg())
        except:
            raise RegistrationException("Error sending registration message")

        poller = zmq.Poller()
        poller.register(self._connection, zmq.POLLIN)
        try:
            if poller.poll(timeout * 1000):
                # timeout in milliseconds
                request = self._connection.recv_multipart()
                response = xMsgRegResponse.create_from_multipart_request(request)

                if response.get_status() != xMsgConstants.SUCCESS:
                    raise RegistrationException(response.get_status())

                xMsgUtil.log("Info: xMsg actor has been registered in node")

                return response.get_data()

            else:
                raise TimeoutReached("Timeout processing registration request")

        except KeyboardInterrupt:
            raise RegistrationException("Keyboard Interrupt while trying to \
                                        register")

    def zmq_socket(self, context, socket_type, reg_address, boc):
        """Creates and returns zmq socket object

        Args:
            context (zmq.Context): zmq context
            socket_type (int): the type of the socket (integer defined by zmq)
            reg_address (String): the registrar service tcp address
            boc (String): 'bind' or 'connect' host and port to socket
                Note that for xMsg proxies we always connect (boc = 'connect')
                (proxies are XPUB/XSUB sockets).

        Returns:
            zmq.Socket: zmq socket object
        """
        # Create a zmq socket
        sb = context.socket(socket_type)
        sb.set_hwm(0)

        if boc == xMsgConstants.BIND:
            # Bind socket to the host and port
            sb.bind(reg_address)

        elif boc == xMsgConstants.CONNECT:
            # Connect to the host and port
            sb.connect(reg_address)

        return sb
