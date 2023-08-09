import filecmp
import threading
import time
import unittest
# before each test first enter python server.py and then press the green button of the function you want to test
import client


class MyTestCase(unittest.TestCase):


    def test_sending(self):
        client1 = client.Client("shani",False)
        client2 = client.Client("shon",False)
        time.sleep(1)
        message_from_client1 =client1.last_message2
        self.assertEqual(message_from_client1,"** shon joined! **\n")

    # goal ! - to examine the ability to pass a document by udp  .
    #instrctions  : 1 . there is a file on the document name cake.txt  - enter "cake.txt" in the gui next to "Download fille"
    #               2.press Y when you asked if to keep the downloading
    #               3. watch hat there is a new document name data with an identical file inside it .


    def test_cheakUDPtransferFile(self):       ## throw warning -- ignore!! .
        client1 = client.Client("shon",flag=False)
        time.sleep(23)
        self.assertEqual(filecmp.cmp("cake.txt","shon/cake.txt"),True)

    # goal !  CHEAK IF - you client1 can download a file while client2 is downloading it too
    # instructions :   1. there is a file on the document name cake.txt  - enter "cake.txt" in the gui next to "Download fille"
    #                  2. when it will ask you if to keep the downloading - enter "cake.txt" int the other client gui(again next to download file)
    #                  3. press Y at the jumping window at the first client
    #                  4. press Y at the jumping window at the second client

    def test_UDPtransfer_in_parallel(self) : ## throw warning -- ignore .
        client1 = client.Client("shani", False)
        client2 = client.Client("shon", False)
        time.sleep(45)
        self.assertEqual(filecmp.cmp("shani/cake.txt", "shon/cake.txt"), True)




