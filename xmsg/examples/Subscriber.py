#
# Copyright (C) 2015. Jefferson Lab, xMsg framework (JLAB). All Rights Reserved.
# Permission to use, copy, modify, and distribute this software and its
# documentation for educational, research, and not-for-profit purposes,
# without fee and without a signed licensing agreement.
#
# Author Vardan Gyurjyan
# Department of Experimental Nuclear Physics, Jefferson Lab.
#
# IN NO EVENT SHALL JLAB BE LIABLE TO ANY PARTY FOR DIRECT, INDIRECT, SPECIAL,
# INCIDENTAL, OR CONSEQUENTIAL DAMAGES, INCLUDING LOST PROFITS, ARISING OUT OF
# THE USE OF THIS SOFTWARE AND ITS DOCUMENTATION, EVEN IF JLAB HAS BEEN ADVISED
# OF THE POSSIBILITY OF SUCH DAMAGE.
#
# JLAB SPECIFICALLY DISCLAIMS ANY WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE. THE CLARA SOFTWARE AND ACCOMPANYING DOCUMENTATION, IF ANY, PROVIDED
# HEREUNDER IS PROVIDED "AS IS". JLAB HAS NO OBLIGATION TO PROVIDE MAINTENANCE,
# SUPPORT, UPDATES, ENHANCEMENTS, OR MODIFICATIONS.
#


from xmsg.core.xMsg import xMsg
from xmsg.core.xMsgUtil import xMsgUtil
from xmsg.core.xMsgTopic import xMsgTopic
from xmsg.core.xMsgCallBack import xMsgCallBack
from xmsg.net.xMsgAddress import ProxyAddress
from xmsg.data import xMsgData_pb2


class ExampleSubscriberCallback(xMsgCallBack):

    def callback(self, msg):
        # User takes care of the proper de-serialization
        ds_msg = xMsgData_pb2.xMsgData()
        ds_msg.ParseFromString(msg.get_data())
        print "Subscriber received data : %s" % ds_msg
        return msg


def main(fe_host="localhost"):
    subscriber = xMsg("test_publisher", "localhost", fe_host)

    # Build Topic
    topic = xMsgTopic.build("test_domain", "test_subject", "test_type")
    connection = subscriber.connect(ProxyAddress(fe_host))

    try:
        callback = ExampleSubscriberCallback()
        subscription = subscriber.subscribe(topic, connection, callback)

        xMsgUtil.keep_alive()

    except KeyboardInterrupt:
        subscriber.unsubscribe(subscription)
        subscriber.destroy(10)
        return
