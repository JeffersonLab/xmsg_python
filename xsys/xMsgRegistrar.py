'''
 Copyright (C) 2015. Jefferson Lab, xMsg framework (JLAB). All Rights Reserved.
 Permission to use, copy, modify, and distribute this software and its
 documentation for educational, research, and not-for-profit purposes,
 without fee and without a signed licensing agreement.

 Author Vardan Gyurjyan
 Department of Experimental Nuclear Physics, Jefferson Lab.

 IN NO EVENT SHALL JLAB BE LIABLE TO ANY PARTY FOR DIRECT, INDIRECT, SPECIAL,
 INCIDENTAL, OR CONSEQUENTIAL DAMAGES, INCLUDING LOST PROFITS, ARISING OUT OF
 THE USE OF THIS SOFTWARE AND ITS DOCUMENTATION, EVEN IF JLAB HAS BEEN ADVISED
 OF THE POSSIBILITY OF SUCH DAMAGE.

 JLAB SPECIFICALLY DISCLAIMS ANY WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
 THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
 PURPOSE. THE CLARA SOFTWARE AND ACCOMPANYING DOCUMENTATION, IF ANY, PROVIDED
 HEREUNDER IS PROVIDED "AS IS". JLAB HAS NO OBLIGATION TO PROVIDE MAINTENANCE,
 SUPPORT, UPDATES, ENHANCEMENTS, OR MODIFICATIONS.
'''
import signal
import zmq

from core.xMsgConstants import xMsgConstants
from xsys.regdis.xMsgRegistrar import xMsgRegistrar


__author__ = 'gurjyan'


class xMsgFE():
    """
    xMsg Front-End
    """

    context = str(xMsgConstants.UNDEFINED)

    def __init__(self):

        # create a zmq context
        self.context = zmq.Context()

        # Start local registrar service. Constructor starts a thread
        # that periodically updates front-end registrar database with
        # the data from the local databases
        self.t = xMsgRegistrar(self.context)
        self.t.daemon = True
        self.t.start()

    def exit_gracefully(self, signum, frame):
        print "xMsgFE death"
        self.context.close()

    def join(self):
        self.t.join()


def main():
    xn = xMsgFE()
    signal.signal(signal.SIGTERM, xn.exit_gracefully)
    signal.signal(signal.SIGINT, xn.exit_gracefully)

if __name__ == '__main__':
    main()